#!/bin/sh
# Install OpenClash on GL.iNet GL-MT3600BE / OpenWrt 21.02 (aarch64_cortex-a53).
# Installer version: 1.1.0
#
# Usage:
#   sh install-openclash-gl-mt3600be.sh --dry-run
#   sh install-openclash-gl-mt3600be.sh --apply
#   sh install-openclash-gl-mt3600be.sh --apply --no-core
#
# The script intentionally does not add a subscription, enable OpenClash, or
# change firewall, DNS, theme, DHCP, or feed settings.

set -eu

MODE="dry-run"
INSTALL_CORE=1

OPENCLASH_API="${OPENCLASH_API:-https://api.github.com/repos/vernesong/OpenClash/releases/latest}"
MIHOMO_ARM64_ARCHIVE="${MIHOMO_ARM64_ARCHIVE:-https://raw.githubusercontent.com/vernesong/OpenClash/core/master/meta/clash-linux-arm64.tar.gz}"
DEPENDENCIES="bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base"

usage() {
  cat <<'EOF'
Usage: sh install-openclash-gl-mt3600be.sh [--dry-run|--apply] [--no-core]

  --dry-run  Validate this router and print the planned work. This is the default.
  --apply    Create a backup, install dependencies and luci-app-openclash,
             then install the official ARM64 Mihomo core.
  --no-core  With --apply, install only OpenClash. Download the core later from
             LuCI: Services -> OpenClash -> Plugin Settings -> Version Update.
EOF
}

log() {
  printf '%s\n' "$*"
}

clear_luci_cache() {
  find /tmp -maxdepth 1 -type f -name 'luci-indexcache.*' -exec rm -f {} \; 2>/dev/null || true
  if [ -d /tmp/luci-modulecache ]; then
    find /tmp/luci-modulecache -type f -exec rm -f {} \; 2>/dev/null || true
  fi
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      MODE="dry-run"
      ;;
    --apply)
      MODE="apply"
      ;;
    --no-core)
      INSTALL_CORE=0
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      die "unknown option: $1"
      ;;
  esac
  shift
done

[ "$(id -u)" = "0" ] || die "run this script as root on the router"
[ -r /etc/openwrt_release ] || die "this does not appear to be an OpenWrt router"

. /etc/openwrt_release

case "$(uname -m)" in
  aarch64) ;;
  *) die "unsupported CPU architecture: $(uname -m) (expected aarch64)" ;;
esac

[ "${DISTRIB_ARCH:-}" = "aarch64_cortex-a53" ] || \
  die "unsupported OpenWrt package architecture: ${DISTRIB_ARCH:-unknown} (expected aarch64_cortex-a53)"

if command -v ubus >/dev/null 2>&1; then
  board_model="$(ubus call system board 2>/dev/null | jsonfilter -e '@.model' 2>/dev/null || true)"
  case "$board_model" in
    *GL-MT3600BE*|"") ;;
    *) die "unsupported router model: $board_model (expected GL-MT3600BE)" ;;
  esac
fi

command -v opkg >/dev/null 2>&1 || die "opkg is required"
command -v jsonfilter >/dev/null 2>&1 || die "jsonfilter is required"
command -v tar >/dev/null 2>&1 || die "tar is required"

log "Router checks passed: ${DISTRIB_DESCRIPTION:-OpenWrt}, ${DISTRIB_ARCH}"
df -h /overlay 2>/dev/null | tail -n 1 || true

if [ "$MODE" = "dry-run" ]; then
  log ""
  log "Dry run only. No package, configuration, or service changes will be made."
  log ""
  log "Planned changes for --apply:"
  log "  1. Back up current network, DHCP, firewall, LuCI, opkg, and release files under /root."
  log "  2. Run opkg update."
  log "  3. Install OpenClash dependencies. dnsmasq-full may be upgraded by your configured GL.iNet feed."
  log "  4. Download the latest official luci-app-openclash IPK from GitHub and install it."
  if [ "$INSTALL_CORE" = "1" ]; then
    log "  5. Install the official linux-arm64 Mihomo core as /etc/openclash/core/clash_meta."
  else
    log "  5. Skip Mihomo core installation; manage it later in LuCI."
  fi
  log "  6. Enable the OpenClash init service without enabling proxy mode."
  log "  7. Reload rpcd ACLs, clear LuCI caches, and restart uhttpd."
  log "  8. Verify the package, controller, init service, and optional core."
  log ""
  log "Run with --apply to make these changes."
  exit 0
fi

stamp="$(date +%Y%m%d-%H%M%S)"
backup="/root/openclash-preinstall-${stamp}.tgz"
workdir="/tmp/openclash-install-${stamp}"
release_json="${workdir}/release.json"
ipk_path="${workdir}/luci-app-openclash.ipk"
core_archive="${workdir}/mihomo-arm64.tar.gz"
core_stage="${workdir}/core"

cleanup() {
  rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

backup_items=""
for item in /etc/config/network /etc/config/dhcp /etc/config/firewall /etc/config/system /etc/config/luci /etc/config/openclash /etc/openclash /etc/opkg /etc/opkg.conf /etc/openwrt_release; do
  [ -e "$item" ] && backup_items="$backup_items $item"
done
[ -n "$backup_items" ] || die "no configuration files were available for backup"

log "Creating backup: $backup"
# OpenWrt paths do not contain whitespace, so this intentionally expands the list.
# shellcheck disable=SC2086
tar czf "$backup" $backup_items

mkdir -p "$workdir" "$core_stage"

log "Updating package lists"
opkg update

log "Installing OpenClash dependencies"
# shellcheck disable=SC2086
opkg install $DEPENDENCIES

log "Resolving the latest official OpenClash IPK"
curl -fsSL --retry 2 --connect-timeout 20 -A "openclash-installer/1.0" "$OPENCLASH_API" -o "$release_json"
openclash_ipk_url="$(jsonfilter -i "$release_json" -e '@.assets[*].browser_download_url' | grep -E '/luci-app-openclash_[^/]+\.ipk$' | head -n 1)"
[ -n "$openclash_ipk_url" ] || die "the latest OpenClash release does not expose a luci-app-openclash IPK"

log "Installing OpenClash from: $openclash_ipk_url"
curl -fL --retry 2 --connect-timeout 20 "$openclash_ipk_url" -o "$ipk_path"
opkg install "$ipk_path"

if [ "$INSTALL_CORE" = "1" ]; then
  log "Installing the official ARM64 Mihomo core"
  curl -fL --retry 2 --connect-timeout 20 "$MIHOMO_ARM64_ARCHIVE" -o "$core_archive"
  tar -xzf "$core_archive" -C "$core_stage"
  [ -f "$core_stage/clash" ] || die "the downloaded Mihomo archive did not contain the expected clash binary"
  [ "$(find "$core_stage" -type f | wc -l)" = "1" ] || die "the Mihomo archive contained unexpected extra files"
  mkdir -p /etc/openclash/core
  cp "$core_stage/clash" /etc/openclash/core/clash_meta
  chmod 0755 /etc/openclash/core/clash_meta
fi

[ -x /etc/init.d/openclash ] || die "OpenClash init script is missing after package installation"
/etc/init.d/openclash enable

# rpcd loads LuCI ACL definitions when it starts. Without this restart, an
# existing login can hide the entire Services -> OpenClash menu.
/etc/init.d/rpcd restart
clear_luci_cache
/etc/init.d/uhttpd restart

opkg status luci-app-openclash | grep -q '^Status: .* installed$' || \
  die "luci-app-openclash is not registered as installed"
[ -s /usr/lib/lua/luci/controller/openclash.lua ] || \
  die "the OpenClash LuCI controller is missing"
/etc/init.d/openclash enabled || die "the OpenClash init service is not enabled"
if [ "$INSTALL_CORE" = "1" ]; then
  [ -x /etc/openclash/core/clash_meta ] || die "the Mihomo core is not executable"
  /etc/openclash/core/clash_meta -v 2>/dev/null | grep -qi 'arm64' || \
    die "the installed Mihomo core did not report an ARM64 build"
fi

log ""
log "OpenClash installation completed."
log "Backup: $backup"
opkg list-installed luci-app-openclash || true
if [ "$INSTALL_CORE" = "1" ]; then
  /etc/openclash/core/clash_meta -v 2>/dev/null || true
fi
log "Open LuCI at: http://192.168.8.1:8080/cgi-bin/luci/admin/services/openclash"
log "If LuCI was already open, sign in again so the refreshed ACL is applied."
log "OpenClash remains disabled until you add a subscription/configuration and enable it in LuCI."
