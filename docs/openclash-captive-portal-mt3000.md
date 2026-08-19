# GL-MT3000 OpenClash 跨平台酒店认证页直连

本文记录 GL-MT3000 在 OpenClash Fake-IP 模式下兼容酒店 Captive Portal 的方法，并区分 iOS/macOS、Windows 与 Linux 的不同探测机制。2026-08-19 已完成 Apple 路径的本地验证和真实酒店测试，也已应用并技术验证 Windows 新旧 NCSI 规则；Windows 酒店现场验收和 Linux 动态端点验证仍待后续测试。

## 先说结论

客户端连上 MT3000 后，系统通常会访问一个普通 HTTP 探测页。酒店网关在认证前拦截这个请求并返回登录页；认证后，原探测页恢复预期响应，系统就把网络标记为可上网。

OpenClash Fake-IP 模式要让这条链路成立，探测主机通常需要同时满足：

1. 加入 Fake-IP 排除，客户端获得真实 DNS 结果；
2. 使用置顶 `DIRECT` 规则，让请求从酒店上游直接发出。

只加 `DIRECT` 仍可能停在 `198.18.0.0/15` 假地址；只排除 Fake-IP，流量仍可能被后续代理规则接管。

## 各平台并不共用一个入口

| 客户端 | 探测机制 | 应考虑的主机 | 当前 MT3000 状态 |
| --- | --- | --- | --- |
| iOS、macOS | Apple Captive Portal 连通性验证 | `captive.apple.com` | 两层已应用，酒店实测通过 |
| Windows 10 1607 及之后 | NCSI HTTP + DNS 探测 | `www.msftconnecttest.com`、`ipv6.msftconnecttest.com`、`dns.msftncsi.com` | 两层已应用；IPv4 DNS/HTTP 通过，IPv6 与酒店待实测 |
| 较旧 Windows | 旧 NCSI 探测 | `www.msftncsi.com`、`ipv6.msftncsi.com`、`dns.msftncsi.com` | 两层已应用；IPv4 DNS/HTTP 通过，IPv6 与酒店待实测 |
| Linux | NetworkManager 等组件的可配置 URI | 没有统一主机；按本机 `ConnectivityCheckUri` 确认 | `network-test.debian.org` 已排除 Fake-IP，但只覆盖使用该配置的 Debian 客户端，且尚未直连 |

Apple 官方把 `captive.apple.com` 列为 iOS 与 macOS 等系统的 Captive Portal 连通性验证主机。Windows 官方说明，Windows 10 1607 及之后访问 `http://www.msftconnecttest.com/connecttest.txt`，并查询 `dns.msftncsi.com`；更早版本使用 `www.msftncsi.com/ncsi.txt`。

Linux 不同：NetworkManager 只规定可配置的 `[connectivity] uri` 和响应判定方式，上游默认不提供统一 URI。发行版或管理员可以更换地址；例如 Debian 的可选配置使用 `http://network-test.debian.org/nm`。因此不能宣称一个静态域名表覆盖所有 Linux。

这些厂商探测地址也不是 Captive Portal 协议本身。IETF 的标准化 CAPPORT 机制由 RFC 8910 通过 DHCP/IPv6 RA 告知客户端 API URI，再由 RFC 8908 定义 Captive Portal API；RFC 8910 同时指出，传统网络在相当长时间内仍需保留 HTTP 拦截和客户端主动探测。此次酒店现场观察到的是后一种兼容路径。

当前 MT3000 并没有作为酒店运营方实现这两份 RFC：实机未发现 DHCPv4 Option 114、DHCPv6 Option 103、IPv6 RA Option 37 或 RFC 8908 API 服务。它现在完成的是“不阻断已知系统探测并兼容传统认证”，酒店上游是否提供 CAPPORT 仍由酒店决定。

## 已验证环境

- 设备：GL.iNet GL-MT3000
- OpenClash：`0.47.088`
- 模式：Fake-IP
- 活动配置：`/etc/openclash/config/config.yaml`
- OpenClash 生成配置：`/etc/openclash/config.yaml`
- 本次未修改订阅节点、代理组、活动配置路径或 DNS 重定向模式

这些版本和路径是一次实机快照。换设备、升级固件或更换 OpenClash 版本后，应先重新检查。

## 当前已应用的 Apple 配置

`/etc/openclash/custom/openclash_custom_rules.list`：

```yaml
rules:
- DOMAIN,captive.apple.com,DIRECT
```

`/etc/openclash/custom/openclash_custom_fake_filter.list`：

```text
captive.apple.com
```

启用持久化自定义层：

```sh
uci set openclash.config.enable_custom_clash_rules='1'
uci set openclash.config.custom_fakeip_filter='1'
uci commit openclash
/etc/init.d/openclash restart
```

不要用示例覆盖整份自定义文件。应保留现有内容，并在写入前备份 `/etc/config/openclash` 和两份自定义文件。

## 当前已应用的 Windows 配置

当前 Fake-IP 排除表已经包含：

```text
+.msftconnecttest.com
+.msftncsi.com
```

因此只给 HTTP 探测主机增加了精确直连，没有重复添加相同的 Fake-IP 排除项：

```yaml
- DOMAIN,www.msftconnecttest.com,DIRECT
- DOMAIN,ipv6.msftconnecttest.com,DIRECT
- DOMAIN,www.msftncsi.com,DIRECT
- DOMAIN,ipv6.msftncsi.com,DIRECT
```

`dns.msftncsi.com` 是 DNS 探测主机，现有 `+.msftncsi.com` 已使它返回真实 DNS 结果；它不是浏览器 HTTP 入口，因此不为了凑齐列表而添加无意义的 HTTP 直连规则。

2026-08-19 应用后已确认：四条规则在自定义层与生成配置中连续装载，OpenClash 单核心运行，活动路径不变；IPv4 客户端 DNS 返回真实公网结果，新版与旧版 HTTP 探测页分别返回 `Microsoft Connect Test` 和 `Microsoft NCSI`。当前网络没有完成 IPv6 探测链路验证，Windows 也仍需在真实酒店完成现场验收。

## Linux 的正确处理方式

先在目标 Linux 客户端读取实际 URI：

```sh
busctl get-property \
  org.freedesktop.NetworkManager \
  /org/freedesktop/NetworkManager \
  org.freedesktop.NetworkManager \
  ConnectivityCheckUri
```

同时可检查发行版和管理员配置：

```sh
grep -RniE '^[[:space:]]*uri[[:space:]]*=' \
  /etc/NetworkManager/NetworkManager.conf \
  /etc/NetworkManager/conf.d \
  /usr/lib/NetworkManager/conf.d 2>/dev/null
```

处理规则如下：

- 返回空值：该客户端没有启用 NetworkManager 连通性 URI，不能靠添加某个“Linux 通用域名”让系统自动弹窗；可直接在浏览器访问普通 HTTP 页面，或使用 GL.iNet Public Hotspot Login Mode。
- 返回具体 URI：只提取其中主机名，为它增加精确 `DOMAIN,<host>,DIRECT` 和 Fake-IP 排除。
- Debian 客户端若实际返回 `network-test.debian.org`，当前路由器已完成 Fake-IP 排除，但仍应在确认后补一条精确直连并实测。
- Firefox 的 `detectportal.firefox.com` 是浏览器级探测，不等于 Linux 系统级统一入口；当前路由器已排除其 Fake-IP，但不把它写成“所有 Linux 必需”。

## 分平台验证

配置应用后先检查路由器：

```sh
/etc/init.d/openclash status
uci -q get openclash.config.config_path
grep -nE 'captive\.apple|msftconnect|msftncsi|network-test\.debian' /etc/openclash/config.yaml
pidof clash
```

然后使用相应客户端：

- iOS/macOS：重新连接 MT3000，等待系统登录助手；未弹出时访问 `http://captive.apple.com/hotspot-detect.html`。
- Windows 10/11：重新连接后观察“需要操作”提示；未弹出时访问 `http://www.msftconnecttest.com/connecttest.txt`。
- 旧 Windows：测试 `http://www.msftncsi.com/ncsi.txt`。
- Linux：先运行 `nmcli networking connectivity check`；结果为 `portal` 时由桌面组件打开登录助手，或手动打开刚查到的 HTTP URI。

认证前，酒店应把探测请求带到登录页；认证后，Apple 页应返回 `Success`，Windows 新版页应返回 `Microsoft Connect Test`。最终验收仍需确认普通网页和代理出口均恢复。

## 通用兜底与隐私边界

GL.iNet 官方推荐在中继公共热点时启用 Public Hotspot Login Mode；固件检测到“已连热点但未联网”后，会临时挂起部分服务并把 DNS 切到自动。该模式对未知酒店入口更通用，但官方也明确提示，这会让部分网络活动暴露给酒店或商场热点提供方。

因此推荐顺序是：

1. 已知系统探测主机使用精确的 Fake-IP 排除和 `DIRECT`；
2. Linux 按客户端实际 URI 补充，不维护虚假的“全 Linux 列表”；
3. 未知入口使用 Public Hotspot Login Mode 临时认证；
4. 不把整个 `apple.com`、`microsoft.com`、所有 TCP 80/443 或整台常用客户端永久直连。

即使只直连探测主机，也会产生少量原生 DNS/HTTP 请求。这是换取自动弹出认证页的隐私取舍，规则应保持精确。

## 酒店现场步骤

1. 用 GL.iNet 中继连接酒店 Wi-Fi，并开启 Public Hotspot Login Mode；需要时开启 Camouflage。
2. 保持 OpenClash 运行，使用准备认证的操作系统重新连接 MT3000。
3. 等待系统自动打开认证页；未弹出时，打开该系统对应的 HTTP 探测地址。
4. 在酒店页面完成认证，再检查普通网页和代理出口。
5. 若初始探测页已成功跳转但后续页面变空，只记录新的主机名并做精确补充；不要记录账号、密码、房号或验证码。

2026-08-19，用户使用当前 Apple 配置的 MT3000 在真实酒店网络完成测试并反馈“很好用”。该证据证明本次 iOS/macOS 探测链路可用，不等于 Windows、全部 Linux 发行版或所有酒店实现已经验收。

## 不能解决的情况

- 酒店要求专用 App、客户端证书、终端合规代理或非 Captive Portal 的 802.1X/EAP 认证；
- 酒店把后续认证站点放在动态域名，而该域名仍被 Fake-IP 或代理接管；
- 酒店按 MAC 限制设备，且路由器中继 MAC 与已登记设备不一致；
- 认证会话过期、SSID 改变或中继 MAC 改变，需要重新登录；
- Linux 客户端没有启用任何连通性检测，系统自然不会自动弹窗；
- OpenClash 开启了阻止非代理流量的策略，覆盖了置顶 `DIRECT` 的预期行为。

## 备份与回滚

Apple 配置应用前的备份为：

```text
/root/openclash-captive-apple-backup-20260819-104127.tgz
```

如需回滚到 Apple 规则写入前的状态：

```sh
tar xzf /root/openclash-captive-apple-backup-20260819-104127.tgz -C /
/etc/init.d/openclash restart
```

该早期备份会同时移除后来加入的 Apple 与 Windows 规则。回滚前仍应确认当前设备是目标 MT3000，并确认备份存在且可读取。

Windows 扩展应用前的备份为：

```text
/root/openclash-captive-windows-backup-20260819-110921.tgz
```

SHA-256：

```text
f1e4d60acbe43cc3a25185445caf65f50416d0ae60fc15e1acd82786a6caa1e2
```

只回滚 Windows 扩展及同期配置状态：

```sh
tar xzf /root/openclash-captive-windows-backup-20260819-110921.tgz -C /
/etc/init.d/openclash restart
```

该备份创建时 Apple 规则已经存在，因此恢复它会保留 Apple 配置。Linux 动态策略本次没有写入，不存在 Linux 回滚项。

## 参考

- [Apple：企业网络所需主机](https://support.apple.com/en-euro/101555)
- [Microsoft：NCSI 常见问题](https://learn.microsoft.com/en-us/windows-server/networking/ncsi/ncsi-frequently-asked-questions)
- [Microsoft：NCSI 排障指南](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/troubleshoot-ncsi-guidance)
- [NetworkManager：连通性检测配置](https://www.networkmanager.dev/docs/api/latest/NetworkManager.conf.html)
- [NetworkManager：当前 connectivity-check URI 属性](https://networkmanager.dev/docs/libnm/latest/NMClient.html)
- [Debian：NetworkManager 连通性 URI](https://sources.debian.org/src/network-manager/1.52.1-1/debian/20-connectivity-debian.conf/)
- [IETF RFC 8910：通过 DHCP/RA 标识 Captive Portal](https://www.rfc-editor.org/rfc/rfc8910.html)
- [IETF RFC 8908：Captive Portal API](https://www.rfc-editor.org/rfc/rfc8908.html)
- [GL.iNet：连接 Captive Portal 公共热点](https://docs.gl-inet.com/router/en/4/faq/connect_to_a_hotspot_with_captive_portal/)
- [OpenClash 当前访问控制与自定义设置源码](https://github.com/vernesong/OpenClash/blob/master/luci-app-openclash/luasrc/model/cbi/openclash/settings.lua)
