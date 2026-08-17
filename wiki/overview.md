# GL.iNet OneScript 项目知识库概览

本知识库沉淀 GL.iNet 路由器的软件安装、固件升级恢复、LuCI 集成、架构适配与双配置切换经验。当前覆盖 GL-MT3600BE 的 OpenClash 安装恢复，以及 GL-MT3000 上已验证的 sing-box VLESS Reality 双配置导入。

## 当前状态

- 已入库 GL-MT3600BE 实机安装记录和安装说明。
- 可 dry run 的安装脚本位于 [`scripts/install-openclash-gl-mt3600be.sh`](../scripts/install-openclash-gl-mt3600be.sh)。
- 已入库 GL-MT3000 双配置导入、切换和美国出口实测，转换脚本位于 [`scripts/import-openclash-dual-config.py`](../scripts/import-openclash-dual-config.py)。
- MT3000 实测为 `mediatek/mt7981`，MT3600BE 历史实测为 `mediatek/mt7987`；两者均观察到 `aarch64_cortex-a53`，但每次操作仍须 live preflight。
- 双配置导入不会覆盖原 `config.yaml`、切换活动路径或重启 OpenClash；切换由用户在 LuCI 中执行。
- 原 `config.yaml` 当前没有香港、澳门、台湾、新加坡节点，用户确认按现状验收为 OK，且奈飞节点为有意排除；订阅更新后仍需复核四地区统计。
- OpenClash 普通重启可保留；固件升级或恢复出厂后可能需重装第三方包。

## 核心入口

- [GL-MT3000](pages/entities/gl-mt3000.md)
- [GL-MT3600BE](pages/entities/gl-mt3600be.md)
- [OpenClash](pages/entities/openclash.md)
- [OpenClash 安装与固件升级恢复方法](pages/analyses/openclash-install-and-recovery.md)
- [OpenClash 双配置与 sing-box 转换方法](pages/analyses/openclash-dual-config-and-sing-box-conversion.md)
- [OpenClash 订阅地区节点排除](pages/analyses/openclash-subscription-region-exclusion.md)
- [LuCI ACL 与菜单刷新](pages/concepts/luci-acl-and-menu-refresh.md)
