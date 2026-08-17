#!/usr/bin/env python3
"""Convert one sing-box VLESS Reality outbound into an inactive OpenClash profile.

The default mode is a dry run. It validates the local source and performs only
read-only checks on the router. --apply validates the generated YAML with the
router's existing Mihomo core, backs up OpenClash, and installs a second config
without changing the active config or restarting OpenClash.
"""

import argparse
import datetime as dt
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Dict, Iterable, List, Optional


SUPPORTED_MODELS = ("GL-MT3000", "GL-MT3600BE")
EXPECTED_ARCH = "aarch64_cortex-a53"
DEFAULT_PROXY_DOMAINS = (
    "openai.com",
    "chatgpt.com",
    "oaistatic.com",
    "oaiusercontent.com",
)


class UserError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely add a sing-box VLESS Reality node as a second OpenClash config."
    )
    parser.add_argument("--source", required=True, type=Path, help="sing-box client JSON")
    parser.add_argument("--router", default="192.168.8.1", help="router address")
    parser.add_argument("--ssh-user", default="root", help="router SSH user")
    parser.add_argument(
        "--profile-name",
        required=True,
        help="new OpenClash config name, with or without .yaml",
    )
    parser.add_argument("--outbound-tag", help="sing-box VLESS outbound tag")
    parser.add_argument("--node-name", default="US-HOME-NODE", help="Mihomo node name")
    parser.add_argument("--group-name", default="US-HOME", help="Mihomo selector name")
    parser.add_argument(
        "--proxy-domain",
        action="append",
        default=[],
        help="additional domain suffix forced through the proxy group; repeatable",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="read-only validation; default")
    mode.add_argument("--apply", action="store_true", help="back up and install the new profile")
    return parser.parse_args()


def fail(message: str) -> None:
    raise UserError(message)


def run(
    argv: List[str],
    *,
    input_text: Optional[str] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            argv,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )
    except FileNotFoundError:
        fail("required command not found: {}".format(argv[0]))
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "command failed").strip()
        fail("{}: {}".format(argv[0], detail))
    raise AssertionError("unreachable")


def ssh_target(args: argparse.Namespace) -> str:
    return "{}@{}".format(args.ssh_user, args.router)


def ssh(args: argparse.Namespace, script: str) -> str:
    result = run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=8",
            ssh_target(args),
            "sh",
            "-s",
        ],
        input_text=script,
    )
    return result.stdout


def normalized_profile_name(raw: str) -> str:
    name = raw if raw.endswith(".yaml") else raw + ".yaml"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.yaml", name):
        fail("profile name may contain only letters, numbers, dot, underscore, and dash")
    if name == "config.yaml":
        fail("refusing to use config.yaml; choose a distinct second-profile name")
    return name


def load_outbound(path: Path, tag: Optional[str]) -> Dict[str, object]:
    try:
        data = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("source file not found: {}".format(path.expanduser()))
    except (OSError, json.JSONDecodeError) as exc:
        fail("cannot read sing-box JSON: {}".format(exc))

    outbounds = data.get("outbounds")
    if not isinstance(outbounds, list):
        fail("source JSON does not contain an outbounds list")

    candidates = [item for item in outbounds if isinstance(item, dict) and item.get("type") == "vless"]
    if tag:
        candidates = [item for item in candidates if item.get("tag") == tag]
    if len(candidates) != 1:
        fail("expected exactly one matching VLESS outbound, found {}".format(len(candidates)))

    outbound = candidates[0]
    tls = outbound.get("tls")
    reality = tls.get("reality") if isinstance(tls, dict) else None
    required = {
        "server": outbound.get("server"),
        "server_port": outbound.get("server_port"),
        "uuid": outbound.get("uuid"),
        "server_name": tls.get("server_name") if isinstance(tls, dict) else None,
        "public_key": reality.get("public_key") if isinstance(reality, dict) else None,
    }
    missing = [key for key, value in required.items() if value is None or value == ""]
    if missing:
        fail("VLESS Reality outbound is missing: {}".format(", ".join(missing)))
    if not isinstance(required["server_port"], int) or not 1 <= required["server_port"] <= 65535:
        fail("server_port must be an integer from 1 to 65535")
    if not isinstance(tls, dict) or tls.get("enabled") is not True:
        fail("the selected VLESS outbound must enable TLS")
    if not isinstance(reality, dict) or reality.get("enabled") is not True:
        fail("the selected VLESS outbound must enable Reality")
    return outbound


def yaml_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def unique(values: Iterable[str]) -> List[str]:
    result = []
    seen = set()
    for value in values:
        normalized = value.strip().lower().lstrip(".")
        if normalized and not re.fullmatch(
            r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",
            normalized,
        ):
            fail("invalid proxy domain: {}".format(value))
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def server_direct_rule(server: str) -> str:
    try:
        address = ipaddress.ip_address(server)
    except ValueError:
        return "DOMAIN,{},DIRECT".format(server)
    prefix = 32 if address.version == 4 else 128
    return "IP-CIDR,{}/{},DIRECT,no-resolve".format(address, prefix)


def build_yaml(
    outbound: Dict[str, object],
    node_name: str,
    group_name: str,
    proxy_domains: Iterable[str],
    include_geodata_rules: bool = True,
) -> str:
    if not node_name.strip() or any(char in node_name for char in "\r\n"):
        fail("node name must be non-empty and stay on one line")
    if not group_name.strip() or any(char in group_name for char in ",\r\n"):
        fail("group name must be non-empty and cannot contain comma or newline")

    tls = outbound["tls"]
    assert isinstance(tls, dict)
    reality = tls["reality"]
    assert isinstance(reality, dict)
    utls = tls.get("utls")
    fingerprint = "chrome"
    if isinstance(utls, dict) and utls.get("fingerprint"):
        fingerprint = str(utls["fingerprint"])

    flow = outbound.get("flow") or "xtls-rprx-vision"
    packet_encoding = outbound.get("packet_encoding") or "xudp"
    server = str(outbound["server"])
    if any(char in server for char in ",\r\n"):
        fail("server contains characters that cannot be used in a Mihomo rule")
    rules = [server_direct_rule(server)]
    rules.extend("DOMAIN-SUFFIX,{},{}".format(domain, group_name) for domain in proxy_domains)
    if include_geodata_rules:
        rules.extend(
            [
                "GEOSITE,cn,DIRECT",
                "GEOIP,private,DIRECT,no-resolve",
                "GEOIP,cn,DIRECT,no-resolve",
            ]
        )
    rules.append("MATCH,{}".format(group_name))

    lines = [
        "mixed-port: 7893",
        "allow-lan: true",
        "mode: rule",
        "log-level: info",
        "ipv6: false",
        "external-controller: 0.0.0.0:9090",
        "unified-delay: true",
        "tcp-concurrent: true",
        "profile:",
        "  store-selected: true",
        "  store-fake-ip: true",
        "dns:",
        "  enable: true",
        "  ipv6: false",
        "  enhanced-mode: fake-ip",
        "  fake-ip-range: 198.18.0.1/16",
        "  nameserver:",
        "    - 223.5.5.5",
        "    - 119.29.29.29",
        "  fallback:",
        "    - https://1.1.1.1/dns-query",
        "    - https://8.8.8.8/dns-query",
        "  fallback-filter:",
        "    geoip: true",
        "    geoip-code: CN",
        "  fake-ip-filter:",
        "    - '*.lan'",
        "    - '*.local'",
        "    - 'time.*.com'",
        "    - 'ntp.*.com'",
        "proxies:",
        "  - name: {}".format(yaml_string(node_name)),
        "    type: vless",
        "    server: {}".format(yaml_string(server)),
        "    port: {}".format(outbound["server_port"]),
        "    uuid: {}".format(yaml_string(outbound["uuid"])),
        "    network: tcp",
        "    udp: true",
        "    tls: true",
        "    servername: {}".format(yaml_string(tls["server_name"])),
        "    flow: {}".format(yaml_string(flow)),
        "    packet-encoding: {}".format(yaml_string(packet_encoding)),
        "    encryption: ''",
        "    client-fingerprint: {}".format(yaml_string(fingerprint)),
        "    skip-cert-verify: false",
        "    reality-opts:",
        "      public-key: {}".format(yaml_string(reality["public_key"])),
    ]
    if reality.get("short_id"):
        lines.append("      short-id: {}".format(yaml_string(reality["short_id"])))
    lines.extend(
        [
            "    smux:",
            "      enabled: false",
            "proxy-groups:",
            "  - name: {}".format(yaml_string(group_name)),
            "    type: select",
            "    proxies:",
            "      - {}".format(yaml_string(node_name)),
            "      - DIRECT",
            "rules:",
        ]
    )
    lines.extend("  - {}".format(yaml_string(rule)) for rule in rules)
    return "\n".join(lines) + "\n"


def parse_key_values(output: str) -> Dict[str, str]:
    values = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def router_preflight(args: argparse.Namespace, profile_name: str) -> Dict[str, str]:
    quoted_profile = shlex.quote("/etc/openclash/config/" + profile_name)
    script = """set -eu
. /etc/openwrt_release
model="$(ubus call system board 2>/dev/null | jsonfilter -e '@.model' 2>/dev/null || true)"
active="$(uci -q get openclash.config.config_path || true)"
printf 'model=%%s\n' "$model"
printf 'machine=%%s\n' "$(uname -m)"
printf 'arch=%%s\n' "${DISTRIB_ARCH:-}"
printf 'target=%%s\n' "${DISTRIB_TARGET:-}"
printf 'openclash=%%s\n' "$(opkg status luci-app-openclash 2>/dev/null | awk '/^Version:/{print $2; exit}')"
printf 'core=%%s\n' "$([ -x /etc/openclash/core/clash_meta ] && echo yes || echo no)"
printf 'geodata=%%s\n' "$([ -s /etc/openclash/GeoSite.dat ] && [ -s /etc/openclash/GeoIP.dat ] && echo yes || echo no)"
printf 'active=%%s\n' "$active"
printf 'service=%%s\n' "$(/etc/init.d/openclash status 2>/dev/null || true)"
printf 'pid=%%s\n' "$(pidof clash 2>/dev/null || true)"
printf 'target_exists=%%s\n' "$([ -e %s ] && echo yes || echo no)"
""" % quoted_profile
    values = parse_key_values(ssh(args, script))
    model = values.get("model", "")
    if not any(item in model for item in SUPPORTED_MODELS):
        fail("unsupported router model: {}".format(model or "unknown"))
    if values.get("machine") != "aarch64" or values.get("arch") != EXPECTED_ARCH:
        fail(
            "unsupported architecture: machine={}, package={}".format(
                values.get("machine", "unknown"), values.get("arch", "unknown")
            )
        )
    if not values.get("openclash"):
        fail("luci-app-openclash is not installed")
    if values.get("core") != "yes":
        fail("Mihomo core is missing or not executable")
    if values.get("geodata") != "yes":
        fail("OpenClash GeoSite.dat or GeoIP.dat is missing")
    return values


def apply_profile(
    args: argparse.Namespace,
    profile_name: str,
    yaml_text: str,
    validation_yaml_text: str,
    before: Dict[str, str],
) -> Dict[str, str]:
    if before.get("target_exists") == "yes":
        fail("target profile already exists; rename it in LuCI or choose another --profile-name")

    remote_temp = "/tmp/openclash-profile-{}-{}.yaml".format(os.getpid(), profile_name[:-5])
    remote_check = "/tmp/openclash-profile-{}-check.yaml".format(os.getpid())
    local_temps = []
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="openclash-profile-", suffix=".yaml", delete=False
        ) as handle:
            handle.write(yaml_text)
            local_temps.append(handle.name)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="openclash-profile-check-", suffix=".yaml", delete=False
        ) as handle:
            handle.write(validation_yaml_text)
            local_temps.append(handle.name)
        for local_temp in local_temps:
            os.chmod(local_temp, 0o600)
        for local_temp, remote_path in zip(local_temps, (remote_temp, remote_check)):
            run(
                [
                    "scp",
                    "-O",
                    "-q",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=8",
                    local_temp,
                    "{}:{}".format(ssh_target(args), remote_path),
                ]
            )

        target = "/etc/openclash/config/" + profile_name
        stage = "/etc/openclash/config/.{}.tmp".format(profile_name)
        q_temp = shlex.quote(remote_temp)
        q_check = shlex.quote(remote_check)
        q_target = shlex.quote(target)
        q_stage = shlex.quote(stage)
        q_active = shlex.quote(before.get("active", ""))
        q_pid = shlex.quote(before.get("pid", ""))
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = "/root/openclash-dual-config-backup-{}.tgz".format(stamp)
        q_backup = shlex.quote(backup)
        script = """set -eu
upload=%s
check_config=%s
target=%s
stage=%s
backup=%s
trap 'rm -f "$upload" "$check_config" "$stage"' EXIT INT TERM
[ ! -e "$target" ] || { echo 'target profile already exists' >&2; exit 1; }
/etc/openclash/core/clash_meta -d /etc/openclash -t -f "$check_config" >/tmp/openclash-profile-check.log 2>&1 || {
  sed -n '1,80p' /tmp/openclash-profile-check.log >&2
  rm -f /tmp/openclash-profile-check.log
  exit 1
}
rm -f /tmp/openclash-profile-check.log
tar czf "$backup" /etc/config/openclash /etc/openclash/config
tar tzf "$backup" >/dev/null
cp "$upload" "$stage"
chmod 0600 "$stage"
mv "$stage" "$target"
cmp "$upload" "$target"
active_after="$(uci -q get openclash.config.config_path || true)"
pid_after="$(pidof clash 2>/dev/null || true)"
[ "$active_after" = %s ] || { echo 'active config changed unexpectedly' >&2; exit 1; }
[ "$pid_after" = %s ] || { echo 'OpenClash process changed unexpectedly' >&2; exit 1; }
printf 'installed=%%s\n' "$target"
printf 'backup=%%s\n' "$backup"
printf 'active=%%s\n' "$active_after"
printf 'service=%%s\n' "$(/etc/init.d/openclash status 2>/dev/null || true)"
printf 'pid=%%s\n' "$pid_after"
""" % (q_temp, q_check, q_target, q_stage, q_backup, q_active, q_pid)
        return parse_key_values(ssh(args, script))
    finally:
        for local_temp in local_temps:
            try:
                os.unlink(local_temp)
            except FileNotFoundError:
                pass
        cleanup = """[ ! -e {0} ] || rm -f {0}
[ ! -e {1} ] || rm -f {1}
""".format(shlex.quote(remote_temp), shlex.quote(remote_check))
        try:
            ssh(args, cleanup)
        except UserError:
            pass


def main() -> int:
    args = parse_args()
    profile_name = normalized_profile_name(args.profile_name)
    outbound = load_outbound(args.source, args.outbound_tag)
    domains = unique(DEFAULT_PROXY_DOMAINS + tuple(args.proxy_domain))
    yaml_text = build_yaml(outbound, args.node_name, args.group_name, domains)
    validation_yaml_text = build_yaml(
        outbound,
        args.node_name,
        args.group_name,
        domains,
        include_geodata_rules=False,
    )
    before = router_preflight(args, profile_name)

    print("Local source: valid sing-box VLESS + TLS + Reality")
    print("Router: {} ({}, {})".format(before.get("model"), before.get("target"), before.get("arch")))
    print("OpenClash: {} | Mihomo core: available".format(before.get("openclash")))
    print("Current config: {} | service: {} | pid: {}".format(
        before.get("active"), before.get("service"), before.get("pid") or "stopped"
    ))
    print("Planned second config: /etc/openclash/config/{}".format(profile_name))
    print("Target already exists: {}".format(before.get("target_exists")))
    print("Proxy-domain rules: {} plus CN/private direct and final proxy".format(len(domains)))

    if not args.apply:
        print("Dry run only: no router files, UCI settings, or services were changed.")
        print("Run the same command with --apply after reviewing this output.")
        return 0

    result = apply_profile(args, profile_name, yaml_text, validation_yaml_text, before)
    print("Installed: {}".format(result.get("installed")))
    print("Backup: {}".format(result.get("backup")))
    print("Router validation: protocol, DNS, and group fields passed; GeoSite/GeoIP files present")
    print("Unchanged active config: {}".format(result.get("active")))
    print("Unchanged OpenClash process: {} ({})".format(result.get("pid"), result.get("service")))
    print("Switch later in LuCI: Services -> OpenClash -> Config Manage -> SwiTch -> Apply Settings")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except UserError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)
