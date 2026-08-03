# GL-MT3600BE OpenClash 实机安装记录

- 操作日期：2026-07-18
- 设备：GL.iNet GL-MT3600BE
- 主机名：`GL-MT3600BE`
- CPU：ARMv8 Processor rev 4
- 目标平台：`mediatek/mt7987`
- OpenWrt 包架构：`aarch64_cortex-a53`
- 固件：OpenWrt 21.02-SNAPSHOT
- 内核：5.4.281
- 原厂后台：HTTP 80 端口
- LuCI：HTTP 8080 端口

## 安装结果

- `luci-app-openclash 0.47.116` 安装成功。
- Mihomo Linux ARM64 核心安装至 `/etc/openclash/core/clash_meta`。
- `dnsmasq-full` 由 `2.92-4` 更新至 `2.92-16`。
- 安装前备份位于 `/root/openclash-preinstall-20260718-112932.tgz`。
- `/etc/rc.d/S99openclash` 存在，OpenClash init 服务已启用。
- `openclash.config.enable=0`，因尚无订阅或配置文件，代理服务未启动。

## 故障与处理

1. 路由器访问 `raw.githubusercontent.com` 时 TLS 证书异常，未使用 `curl -k`。在 Mac 上通过有效 TLS 下载官方 ARM64 核心，核对 SHA-256 后经 SSH 传输。
2. 安装后 LuCI 最初不显示“服务 -> OpenClash”。控制器和菜单缓存已存在，原因是 `rpcd` 未重载新增 ACL。
3. 重启 `rpcd`、清理 LuCI 缓存、重启 `uhttpd` 并重新登录后，OpenClash 菜单和管理页显示正常。

## 验证结论

- 普通重启不会删除已安装的包、LuCI 页面、配置或核心。
- OpenClash 是否开机运行由有效配置和 `openclash.config.enable` 决定。
- 固件升级或恢复出厂可能删除第三方包，需重新执行安装脚本。
