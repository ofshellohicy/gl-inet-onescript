# 来源：OpenClash Captive Portal 跨平台补充考证

## 摘要

该来源补充考证 iOS、macOS、Windows 与 Linux 的 Captive Portal 探测机制，并记录当时对 GL-MT3000 OpenClash 自定义层的只读检查。Apple 已完成真实 DNS、置顶直连和酒店现场验收；检查时 Windows 相关域名已排除 Fake-IP 但未直连。该 Windows 状态随后已被应用记录更新；Linux 没有统一端点，仍必须按客户端实际 NetworkManager URI 精确补充。

## 已证实事实

- iOS 与 macOS 使用 Apple 管理的 `captive.apple.com` 进行 Captive Portal 网络连通性验证。
- Windows 10 1607 及之后版本主要使用 `www.msftconnecttest.com`、`ipv6.msftconnecttest.com` 和 `dns.msftncsi.com`；旧版本使用 `www.msftncsi.com` 与 `ipv6.msftncsi.com`。
- NetworkManager 的连通性 URI 是可选配置，不存在覆盖全部 Linux 发行版的单一固定域名。
- Debian 可选连接检测包使用 `network-test.debian.org`，该事实只适用于安装并启用相应配置的 Debian 系统。
- Apple、Microsoft 与发行版探测入口不是标准协议本身；IETF CAPPORT 由 RFC 8910 负责通过 DHCP/RA 告知 API URI，由 RFC 8908 定义 API，同时仍要求兼容传统探测方式。
- 本次只读检查时，目标 MT3000 Fake-IP 排除表已含 Microsoft 后缀、Debian 和 Firefox 探测主机，但直连规则只有 Apple 主机。
- 该次考证没有修改在线路由器；Windows 四条直连随后另行授权并应用，见后续来源。Linux 仍属于动态识别和待实测范围。

## 解释

OpenClash Fake-IP 模式要兼容系统自动弹出认证页，需要同时保证探测主机返回真实地址并从酒店上游直连。Apple 与 Windows 可维护少量精确主机；Linux 应先识别实际配置 URI。未知酒店入口仍应使用 GL.iNet Public Hotspot Login Mode 或临时绕过，而不是永久直连整片域名或所有 HTTP/HTTPS 流量。

## 来源

- [跨平台补充考证原始记录](../../raw/openclash-captive-portal-cross-platform-review-2026-08-19.md)
- [Apple 企业网络所需主机](https://support.apple.com/en-euro/101555)
- [Microsoft NCSI FAQ](https://learn.microsoft.com/en-us/windows-server/networking/ncsi/ncsi-frequently-asked-questions)
- [NetworkManager 连通性检测配置](https://www.networkmanager.dev/docs/api/latest/NetworkManager.conf.html)
- [Debian NetworkManager 连通性配置](https://sources.debian.org/src/network-manager/1.52.1-1/debian/20-connectivity-debian.conf/)
- [IETF RFC 8910](https://www.rfc-editor.org/rfc/rfc8910.html)
- [IETF RFC 8908](https://www.rfc-editor.org/rfc/rfc8908.html)
- [GL.iNet Captive Portal 指南](https://docs.gl-inet.com/router/en/4/faq/connect_to_a_hotspot_with_captive_portal/)

## 相关页

- [GL-MT3000](../entities/gl-mt3000.md)
- [OpenClash](../entities/openclash.md)
- [OpenClash Captive Portal 跨平台绕过方法](../analyses/openclash-captive-portal-bypass.md)
- [Windows 规则应用记录](openclash-captive-portal-windows-apply-2026-08-19.md)
