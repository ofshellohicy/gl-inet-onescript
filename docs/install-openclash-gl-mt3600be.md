# GL-MT3600BE OpenClash 安装说明

配套脚本：[`scripts/install-openclash-gl-mt3600be.sh`](../scripts/install-openclash-gl-mt3600be.sh)

项目知识库：[`wiki/index.md`](../wiki/index.md)

## 适用环境

- 设备：GL.iNet GL-MT3600BE
- CPU：ARMv8 / AArch64
- OpenWrt 软件包架构：`aarch64_cortex-a53`
- 目标平台：`mediatek/mt7987`
- 管理界面：GL.iNet 原厂后台使用 80 端口，标准 LuCI 使用 8080 端口

脚本会严格检查设备型号和架构。检查不匹配时会直接停止，不会尝试安装其他架构的软件包或核心。

## 使用方法

先把脚本上传到路由器，例如 `/tmp/install-openclash-gl-mt3600be.sh`，然后通过 SSH 执行：

```sh
ssh root@192.168.8.1
sh /tmp/install-openclash-gl-mt3600be.sh --dry-run
sh /tmp/install-openclash-gl-mt3600be.sh --apply
```

默认模式是 `--dry-run`，只检查环境并显示计划，不修改路由器。

只安装 LuCI 插件、暂不下载 Mihomo 核心：

```sh
sh /tmp/install-openclash-gl-mt3600be.sh --apply --no-core
```

## 脚本会做什么

1. 检查 root 权限、设备型号、AArch64 CPU 和 `aarch64_cortex-a53` 软件包架构。
2. 备份网络、DHCP、防火墙、LuCI、OpenClash、opkg 和固件版本文件到 `/root/openclash-preinstall-时间.tgz`。
3. 执行 `opkg update` 并安装 OpenClash 依赖。
4. 从 OpenClash 官方 GitHub Release 获取最新 `luci-app-openclash` IPK。
5. 安装官方 Linux ARM64 Mihomo 核心到 `/etc/openclash/core/clash_meta`。
6. 启用 `/etc/init.d/openclash` 开机服务，但不擅自开启代理。
7. 重启 `rpcd` 以加载 LuCI ACL，清理 LuCI 缓存并重启 `uhttpd`。
8. 验证软件包、LuCI 控制器、开机服务和 ARM64 核心。

脚本不会添加订阅，也不会擅自修改代理模式、防火墙规则、DNS、DHCP、主题或软件源。

## 安装后访问

标准 LuCI 地址：

```text
http://192.168.8.1:8080/cgi-bin/luci/admin/services/openclash
```

安装会重启 `rpcd`，已有 LuCI 会话需要重新登录。菜单位置为“服务 -> OpenClash”。

首次安装后显示“未运行”是正常的。先在“配置订阅”中添加订阅，或在“配置管理”中上传配置，然后在 OpenClash 页面启用服务。

## 重启与固件升级

- 普通重启：OpenClash 软件包、LuCI 页面、配置和 Mihomo 核心会保留。
- 已启用有效配置：OpenClash init 服务会在开机时按配置启动。
- 尚未启用或没有配置：LuCI 页面仍会保留，但代理服务不会运行。
- 固件升级或恢复出厂：第三方软件包可能被清除。升级后重新执行本脚本；如配置也被清除，再从备份恢复需要的 OpenClash 配置。

## 下载或证书错误

脚本不会通过 `curl -k` 绕过 TLS 校验。如果路由器访问 GitHub 时出现证书错误，请先确认路由器时间和 CA 包；也可以使用 `--no-core` 完成 LuCI 安装，再从可信电脑下载官方 ARM64 核心并通过 SSH 传输。

不要为了完成下载关闭证书验证，也不要安装来源不明的 IPK 或核心。
