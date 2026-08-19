# OpenClash Captive Portal 跨平台补充考证（2026-08-19）

## 背景

此前实机配置和酒店验收只确认了 Apple 探测入口 `http://captive.apple.com/hotspot-detect.html`。用户随后指出，长期方案还必须考虑 Windows、iOS、macOS 和 Linux。

## 官方机制核对

### iOS 与 macOS

- Apple 将 `captive.apple.com` 列为 iOS、iPadOS、tvOS、macOS 和 visionOS 的 Captive Portal 网络连通性验证主机。
- 端口为 TCP 80 和 443。
- 这是 Apple 平台的厂商探测入口，不是酒店路由器规定的通用协议地址。

### Windows

- Windows 10 1607 及之后版本的 NCSI HTTP 探测为 `http://www.msftconnecttest.com/connecttest.txt`，正常响应内容为 `Microsoft Connect Test`。
- 对应 IPv6 主机为 `ipv6.msftconnecttest.com`。
- NCSI 还查询 `dns.msftncsi.com`。
- Windows 10 1607 之前的兼容入口为 `http://www.msftncsi.com/ncsi.txt`，IPv6 主机为 `ipv6.msftncsi.com`。
- Captive Portal 返回重定向或不匹配的正文时，Windows 可将网络识别为需要登录并打开浏览器。

### Linux

- Linux 没有一个由“Linux”统一规定的探测域名。
- NetworkManager 提供可选的 `[connectivity]` 检测机制；`uri` 由发行版或管理员设置，上游默认没有配置 URI。
- GNOME Portal Helper 等组件可利用 NetworkManager 的 `portal` 状态打开登录页。
- Debian 的可选 `network-manager-config-connectivity-debian` 配置使用 `http://network-test.debian.org/nm`，但不能据此外推所有 Linux 发行版。
- 当前 URI 可从 NetworkManager 的 `ConnectivityCheckUri` 属性或本机配置文件读取。

### 标准化 CAPPORT

- `captive.apple.com`、Microsoft NCSI 和发行版连通性 URI 都是客户端探测入口，不是 Captive Portal 协议本身。
- RFC 8910 定义 DHCPv4、DHCPv6 与 IPv6 RA 选项，用来向客户端提供 Captive Portal API URI。
- RFC 8908 定义 HTTPS Captive Portal API。
- RFC 8910 明确说明传统 HTTP 拦截和客户端探测仍需长期兼容，因此标准机制不能让现有厂商探测规则立即消失。

## 路由器只读检查

目标设备仍为 GL-MT3000，OpenClash 状态为 `running`，活动路径仍为 `/etc/openclash/config/config.yaml`。本次未修改路由器。

`/etc/openclash/custom/openclash_custom_rules.list` 当前只包含一个已启用的 Captive Portal 直连规则：

```yaml
- DOMAIN,captive.apple.com,DIRECT
```

`/etc/openclash/custom/openclash_custom_fake_filter.list` 已包含：

```text
network-test.debian.org
detectportal.firefox.com
captive.apple.com
+.msftconnecttest.com
+.msftncsi.com
```

因此 Apple 已形成“真实 DNS + 直连”的完整闭环；Microsoft、Debian 和 Firefox 相关地址目前只排除了 Fake-IP，尚未保证流量不进入代理。

## 配置原则

1. 只对已确认的探测主机使用精确 `DOMAIN` 直连，不把整个 `apple.com`、`microsoft.com` 或所有 TCP 80/443 设为直连。
2. HTTP 探测主机同时需要 Fake-IP 排除和置顶 `DIRECT`。
3. Windows 的 DNS 探测主机需要返回真实 DNS 结果；它不是浏览器入口，不必仅为此添加 HTTP 直连规则。
4. Linux 先读取实际 `ConnectivityCheckUri`，再把其中主机精确加入两层规则；不能维护一个自称覆盖所有 Linux 的静态域名表。
5. GL.iNet 的 Public Hotspot Login Mode 仍是未知入口的通用兜底；官方说明该模式会临时挂起部分服务并把 DNS 切到自动，可能向热点提供方泄露网络活动。
6. 永久直连探测地址会产生少量原生 DNS/HTTP 流量，应把规则限制在探测专用主机，并在文档中说明隐私取舍。

## 验证边界

- Apple 规则已于 2026-08-19 在真实酒店完成验收。
- Windows 和 Linux 本次只完成官方机制考证与当前路由配置审计，尚未写入新的直连规则，也未完成相应客户端的酒店实测。
- Android 不在本次用户指定的平台范围内；不得用 Apple、Windows 或某个 Linux 发行版的地址代替 Android 结论。

## 官方来源

- Apple Support: https://support.apple.com/en-euro/101555
- Microsoft NCSI FAQ: https://learn.microsoft.com/en-us/windows-server/networking/ncsi/ncsi-frequently-asked-questions
- Microsoft NCSI troubleshooting: https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/troubleshoot-ncsi-guidance
- NetworkManager configuration reference: https://www.networkmanager.dev/docs/api/latest/NetworkManager.conf.html
- NetworkManager `connectivity-check-uri` property: https://networkmanager.dev/docs/libnm/latest/NMClient.html
- Debian NetworkManager connectivity configuration: https://sources.debian.org/src/network-manager/1.52.1-1/debian/20-connectivity-debian.conf/
- IETF RFC 8910: https://www.rfc-editor.org/rfc/rfc8910.html
- IETF RFC 8908: https://www.rfc-editor.org/rfc/rfc8908.html
- GL.iNet Captive Portal guide: https://docs.gl-inet.com/router/en/4/faq/connect_to_a_hotspot_with_captive_portal/
