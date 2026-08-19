# OpenClash Captive Portal 跨平台绕过方法

## 问题

GL.iNet 路由器使用 OpenClash Fake-IP 模式中继酒店 Wi-Fi 时，怎样让 Windows、iOS、macOS 和 Linux 打开认证页，同时避免把无关流量永久直连？

## 结论

Captive Portal 没有一个覆盖全部操作系统的固定探测地址。正确做法是对客户端实际使用的 HTTP 探测主机同时配置“Fake-IP 排除 + 置顶 `DIRECT`”，并把规则限制在精确主机：

- iOS/macOS：`captive.apple.com`。
- Windows 10 1607 及之后：`www.msftconnecttest.com`、`ipv6.msftconnecttest.com`；DNS 探测还使用 `dns.msftncsi.com`。
- 旧 Windows：`www.msftncsi.com`、`ipv6.msftncsi.com`。
- Linux：先读取 NetworkManager 的 `ConnectivityCheckUri`；上游没有统一默认地址，发行版与管理员均可修改。

Apple 路径已于 2026-08-19 在 GL-MT3000 完成真实酒店验收。Windows 四条精确直连已应用并完成运行时及 IPv4 DNS/HTTP 技术验证，但 IPv6 链路和酒店现场仍待验收；Linux 仍为动态识别策略，没有新增直连域名。

这些平台域名是兼容性探测入口，不是 Captive Portal 协议本身。标准化 CAPPORT 由 RFC 8910 通过 DHCP/RA 发布 API URI，再由 RFC 8908 定义 API；传统酒店仍可能依赖 HTTP 拦截，所以当前仍需维护少量平台探测规则。实机审计未发现 MT3000 LAN 发布 CAPPORT DHCP/RA 选项或提供 RFC 8908 API，因此当前结论是“兼容传统探测”，不是“MT3000 已实现完整 CAPPORT 服务端”。

## 为什么需要两层

- `DIRECT` 决定请求不进入代理节点，让酒店上游可以拦截初始 HTTP 请求。
- Fake-IP 排除使客户端获得真实地址，而不是 `198.18.0.0/15` 映射。
- 单独配置其中一项，仍可能在 DNS 或转发层被 OpenClash 截断。

自定义规则应进入 `/etc/openclash/custom/openclash_custom_rules.list`，Fake-IP 排除进入 `/etc/openclash/custom/openclash_custom_fake_filter.list`。这样 OpenClash 重新生成活动配置或更新订阅时仍可合并，不必直接改写 `config.yaml`。

## 平台策略

### iOS 与 macOS

Apple 官方列明 `captive.apple.com` 是 iOS、macOS 等系统的 Captive Portal 连通性验证主机。目标 MT3000 已配置：

```yaml
- DOMAIN,captive.apple.com,DIRECT
```

```text
captive.apple.com
```

### Windows

目标 MT3000 的 Fake-IP 排除表包含 `+.msftconnecttest.com` 与 `+.msftncsi.com`，并已应用以下精确直连：

```yaml
- DOMAIN,www.msftconnecttest.com,DIRECT
- DOMAIN,ipv6.msftconnecttest.com,DIRECT
- DOMAIN,www.msftncsi.com,DIRECT
- DOMAIN,ipv6.msftncsi.com,DIRECT
```

`dns.msftncsi.com` 已被现有后缀规则排除 Fake-IP；它是 DNS 探测主机，不是需要打开的 HTTP 登录入口。

应用后 OpenClash 保持单核心运行，活动路径未改变；IPv4 客户端 DNS 结果不在 `198.18.0.0/15`，新版和旧版 HTTP 探测页分别返回预期正文。IPv6 探测链路和 Windows 酒店认证仍待现场验证。

### Linux

NetworkManager 连通性检测 URI 是可选配置。先查询：

```sh
busctl get-property org.freedesktop.NetworkManager \
  /org/freedesktop/NetworkManager \
  org.freedesktop.NetworkManager ConnectivityCheckUri
```

只为返回 URI 中的主机增加两层规则。Debian 的可选配置以 `network-test.debian.org` 为例，但该地址不能代表 Ubuntu、Fedora、Arch 或其他 Linux 系统。若 URI 为空，系统不会因为路由器增加一个猜测域名就自动弹窗，应使用普通 HTTP 页面或 GL.iNet Public Hotspot Login Mode。

## 验收链路

1. live preflight 确认设备型号、OpenClash 版本、活动路径和运行模式。
2. dry run 明确只改变自定义层，且列出精确主机。
3. 写入前备份 UCI 与两份自定义文件。
4. 重启后确认单核心运行、活动路径不变、规则置顶、Fake-IP 排除生效。
5. 分别用目标操作系统检查系统提示、DNS 结果和 HTTP 探测响应。
6. 最终必须在真实 Captive Portal 完成认证，不能用正常互联网下的 `200` 代替现场验收。

## 适用边界

- 该方法只保证已确认探测入口；酒店重定向的后续动态主机仍可能需要精确补充。
- 不应把全部 `80/443`、整片大域名或整台日常客户端永久直连，这会扩大泄漏面。
- 永久直连探测主机会产生少量原生 DNS/HTTP 流量，这是自动弹出认证页的明确取舍。
- 专用 App、客户端证书、终端合规检查、802.1X/EAP 或 MAC 白名单不由域名绕过解决。
- GL.iNet Public Hotspot Login Mode 是未知入口的通用兜底；官方说明该模式可能临时挂起服务、切换 DNS，并向热点提供方暴露部分网络活动。
- 本次现场证据来自 GL-MT3000 的 Apple 路径；MT3600BE、Windows 与 Linux 只能复用机制，不能复用实机结论。

## 相关页

- [完整操作文档](../../../docs/openclash-captive-portal-mt3000.md)
- [Apple 路径酒店实机来源摘要](../sources/openclash-captive-portal-hotel-validation-2026-08-19.md)
- [跨平台补充考证来源摘要](../sources/openclash-captive-portal-cross-platform-review-2026-08-19.md)
- [Windows 规则应用来源摘要](../sources/openclash-captive-portal-windows-apply-2026-08-19.md)
- [GL-MT3000](../entities/gl-mt3000.md)
- [OpenClash](../entities/openclash.md)
