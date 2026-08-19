# GL.iNet OneScript 项目知识库概览

本知识库沉淀 GL.iNet 路由器的软件安装、固件升级恢复、LuCI 集成、架构适配、双配置切换和公共热点认证经验。当前覆盖 GL-MT3600BE 的 OpenClash 安装恢复，以及 GL-MT3000 上已验证的 sing-box VLESS Reality 双配置导入和酒店 Captive Portal 绕过。

## 当前状态

- 已入库 GL-MT3600BE 实机安装记录和安装说明。
- 可 dry run 的安装脚本位于 [`scripts/install-openclash-gl-mt3600be.sh`](../scripts/install-openclash-gl-mt3600be.sh)。
- 已入库 GL-MT3000 双配置导入、切换和美国出口实测，转换脚本位于 [`scripts/import-openclash-dual-config.py`](../scripts/import-openclash-dual-config.py)。
- MT3000 实测为 `mediatek/mt7981`，MT3600BE 历史实测为 `mediatek/mt7987`；两者均观察到 `aarch64_cortex-a53`，但每次操作仍须 live preflight。
- 双配置导入不会覆盖原 `config.yaml`、切换活动路径或重启 OpenClash；切换由用户在 LuCI 中执行。
- 原 `config.yaml` 当前没有香港、澳门、台湾、新加坡节点，用户确认按现状验收为 OK，且奈飞节点为有意排除；订阅更新后仍需复核四地区统计。
- OpenClash 普通重启可保留；固件升级或恢复出厂后可能需重装第三方包。
- GL-MT3000 已实测通过 `captive.apple.com` 的 Fake-IP 排除与置顶直连，在 OpenClash 运行状态下完成真实酒店认证；iOS 与 macOS 共用该 Apple 探测主机。
- Windows NCSI 的 Microsoft 探测域名已完成 Fake-IP 排除和四条精确直连，运行时及 IPv4 DNS/HTTP 技术验证通过；IPv6 链路和酒店现场验收仍待完成。
- Linux 没有统一探测域名，继续按客户端实际 NetworkManager URI 动态补充；本次没有硬编码任何 Linux 直连主机。
- MT3000 当前未发布 RFC 8910 CAPPORT DHCP/RA 选项，也未提供 RFC 8908 API；其职责是兼容传统客户端探测，不代表替酒店实现了 CAPPORT 服务端。

## 核心入口

- [GL-MT3000](pages/entities/gl-mt3000.md)
- [GL-MT3600BE](pages/entities/gl-mt3600be.md)
- [OpenClash](pages/entities/openclash.md)
- [OpenClash 安装与固件升级恢复方法](pages/analyses/openclash-install-and-recovery.md)
- [OpenClash 双配置与 sing-box 转换方法](pages/analyses/openclash-dual-config-and-sing-box-conversion.md)
- [OpenClash 订阅地区节点排除](pages/analyses/openclash-subscription-region-exclusion.md)
- [OpenClash Captive Portal 跨平台绕过方法](pages/analyses/openclash-captive-portal-bypass.md)
- [LuCI ACL 与菜单刷新](pages/concepts/luci-acl-and-menu-refresh.md)
