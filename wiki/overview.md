# GL.iNet OneScript 项目知识库概览

本知识库沉淀 GL.iNet 路由器的软件安装、固件升级恢复、LuCI 集成与架构适配经验。当前首个已验证流程是 GL-MT3600BE 上的 OpenClash 安装与恢复。

## 当前状态

- 已入库 GL-MT3600BE 实机安装记录和安装说明。
- 可 dry run 的安装脚本位于 [`scripts/install-openclash-gl-mt3600be.sh`](../scripts/install-openclash-gl-mt3600be.sh)。
- 当前实机为 `mediatek/mt7987` / `aarch64_cortex-a53`，LuCI 使用 `8080` 端口。
- OpenClash 普通重启可保留；固件升级或恢复出厂后可能需重装第三方包。

## 核心入口

- [GL-MT3600BE](pages/entities/gl-mt3600be.md)
- [OpenClash](pages/entities/openclash.md)
- [OpenClash 安装与固件升级恢复方法](pages/analyses/openclash-install-and-recovery.md)
- [LuCI ACL 与菜单刷新](pages/concepts/luci-acl-and-menu-refresh.md)
