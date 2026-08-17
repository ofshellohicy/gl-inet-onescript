# OpenClash 双配置导入：MT3000 与 MT3600BE

本文说明如何把 sing-box 中的 VLESS Reality 节点转换成独立的 Mihomo YAML，并作为 OpenClash 的第二套配置导入。流程默认 dry run，不覆盖 `config.yaml`，不切换活动配置，也不重启 OpenClash。

## 适用边界

配置文件本身不绑定 CPU 型号。MT3000 与 MT3600BE 都使用 `aarch64_cortex-a53` 软件包架构时，可以共用转换规则；Mihomo 核心仍必须按路由器实机架构检查。

| 项目 | GL-MT3000 | GL-MT3600BE |
| --- | --- | --- |
| 已观察目标平台 | `mediatek/mt7981` | `mediatek/mt7987` |
| 已观察包架构 | `aarch64_cortex-a53` | `aarch64_cortex-a53` |
| Mihomo 核心 | Linux ARM64 | Linux ARM64 |
| 双配置导入与切换 | 2026-08-18 实机验证，美国出口 | 执行前必须重新 dry run |

不要仅凭产品名跳过预检。固件升级可能改变 OpenWrt 版本、软件源、OpenClash 版本或核心路径。

## 前提

1. OpenClash 已按标准 OpenWrt 机制安装，LuCI 能打开“服务 -> OpenClash”。
2. `/etc/openclash/core/clash_meta` 存在且可执行。
3. Mac 可以使用密钥登录路由器：`ssh root@192.168.8.1`。
4. sing-box JSON 中恰好有一个待转换的 VLESS + TLS + Reality outbound，或可用 `--outbound-tag` 唯一选中。

路由器恢复出厂后若出现主机键变化，先从可信界面或现场信息确认新指纹，再执行 `ssh-keygen -R 192.168.8.1` 并重新连接。不要在未核验指纹时自动接受新主机键。

## Dry Run

在 Mac 的仓库目录执行：

```sh
python3 scripts/import-openclash-dual-config.py \
  --source ~/.config/sing-box-client/client.json \
  --router 192.168.8.1 \
  --profile-name frank-us-home \
  --dry-run
```

dry run 只会：

- 解析本地 JSON，并检查 VLESS、TLS、Reality 必填字段；
- 通过 SSH 只读检查型号、目标平台、包架构、OpenClash、Mihomo、活动配置和进程；
- 报告目标文件是否已存在；
- 打印计划，不上传文件、不修改 UCI、不重启服务。

MT3600BE 使用同一命令，只需将 `--router` 改成它的地址。若两台路由器都使用 `192.168.8.1`，每次换设备都必须重新核验 SSH 主机指纹。

## 导入第二套配置

确认 dry run 后，把最后一个参数改为 `--apply`：

```sh
python3 scripts/import-openclash-dual-config.py \
  --source ~/.config/sing-box-client/client.json \
  --router 192.168.8.1 \
  --profile-name frank-us-home \
  --apply
```

`--apply` 的顺序是：

1. 将生成的 YAML 写入本机权限为 `0600` 的临时文件。
2. 上传到路由器 `/tmp`；另生成一份仅去除 GeoSite/GeoIP 规则的校验副本，用现有 Mihomo 核心检查协议、DNS 和代理组字段。
3. 备份 `/etc/config/openclash` 和 `/etc/openclash/config` 到 `/root/openclash-dual-config-backup-时间.tgz`。
4. 原子写入 `/etc/openclash/config/<profile-name>.yaml`。
5. 比对上传文件与目标文件，并确认 UCI 活动路径和 OpenClash PID 未变化。
6. 删除本机和路由器上的临时文件。

脚本会只读确认 OpenClash 的 GeoSite/GeoIP 文件存在。校验副本仍使用 `-d /etc/openclash`；直接在活动核心旁启动第二个完整 GeoSite 校验进程，可能在小内存路由器上被系统杀掉。完整配置的实际出口验收应在 LuCI 切换后执行。

脚本拒绝把目标命名为 `config.yaml`，也拒绝覆盖同名配置。需要更新已有第二配置时，先在 LuCI 中重命名旧文件，再导入新文件。

## 字段转换

| sing-box | Mihomo |
| --- | --- |
| `server` | `server` |
| `server_port` | `port` |
| `uuid` | `uuid` |
| `flow` | `flow` |
| `packet_encoding` | `packet-encoding` |
| `tls.server_name` | `servername` |
| `tls.utls.fingerprint` | `client-fingerprint` |
| `tls.reality.public_key` | `reality-opts.public-key` |
| `tls.reality.short_id` | `reality-opts.short-id`（非空时写入） |

脚本生成完整独立配置，不把节点拼进原 `config.yaml`。默认策略是私网和中国大陆直连、OpenAI 相关域名明确走代理、其余流量最终走第二配置的代理组。可重复传入 `--proxy-domain example.com` 添加域名后缀规则。

Mihomo 的 VLESS Reality 字段定义以[官方 VLESS 文档](https://wiki.metacubex.one/config/proxies/vless/)为准。

## 在 LuCI 中切换

打开：

```text
http://路由器地址:8080/cgi-bin/luci/admin/services/openclash/config
```

1. 在新配置行点击 `SwiTch`，确认当前配置名变为新文件。
2. 点击 `Apply Settings`，让 OpenClash 按新配置重启。
3. 检查运行状态、DNS 和出口国家。

切换会导致短暂网络中断。OpenClash 当前实现中，`SwiTch` 写入 `openclash.config.config_path`，`Apply Settings` 才启用并重启服务；可在[官方配置管理源码](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/luasrc/model/cbi/openclash/config.lua)核对。

切回原配置时，对 `config.yaml` 重复相同步骤。SSH 回退命令为：

```sh
uci set openclash.config.config_path='/etc/openclash/config/config.yaml'
uci commit openclash
/etc/init.d/openclash restart
```

## 不泄露密钥的验收

```sh
uci -q get openclash.config.config_path
/etc/init.d/openclash status
pidof clash
ls -l /etc/openclash/config/*.yaml
/etc/openclash/core/clash_meta -v
```

不要把生成的 YAML、sing-box 源文件、UUID、Reality 公钥/短 ID 或节点地址提交到 Git、Wiki、聊天记录或公开工单。仓库只保留转换脚本和脱敏操作记录。

## 重启与升级

- 普通重启：OpenClash init 已启用且活动配置有效时，会按 UCI 中保存的配置路径启动。
- 固件升级：第三方软件包或核心可能被清除，先按[安装与恢复文档](install-openclash-gl-mt3600be.md)重新检查 OpenClash，再导入第二配置。
- 恢复出厂：SSH 主机键、公钥、OpenClash 和配置都可能丢失，应从指纹核验和 dry run 重新开始。
