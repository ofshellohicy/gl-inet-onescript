# 来源：GL-MT3600BE OpenClash 安装材料

## 摘要

该来源组合包含 GL-MT3600BE 安装说明和 2026-07-18 实机操作记录，覆盖架构校验、官方 IPK 与 ARM64 Mihomo 核心安装、LuCI ACL 刷新、开机服务和固件升级后恢复。

## 关键要点

- 设备架构是 `aarch64_cortex-a53`，Mihomo 应使用 Linux ARM64 版本。
- 80 端口是 GL.iNet 原厂后台，8080 端口是标准 LuCI。
- 安装新 LuCI 应用后要重启 `rpcd` 以重载 ACL，否则菜单可能被过滤。
- init 服务启用不等于立即启用代理；无配置时保持 `openclash.config.enable=0`。
- 官方下载证书异常时不应使用 `curl -k`。

## 来源

- [安装说明](../../raw/install-openclash-gl-mt3600be.md)
- [实机安装记录](../../raw/openclash-install-operation-2026-07-18.md)
- [当前安装脚本](../../../scripts/install-openclash-gl-mt3600be.sh)
- [当前配套文档](../../../docs/install-openclash-gl-mt3600be.md)

## 相关页

- [GL-MT3600BE](../entities/gl-mt3600be.md)
- [OpenClash](../entities/openclash.md)
- [LuCI ACL 与菜单刷新](../concepts/luci-acl-and-menu-refresh.md)
- [OpenClash 安装与固件升级恢复方法](../analyses/openclash-install-and-recovery.md)
