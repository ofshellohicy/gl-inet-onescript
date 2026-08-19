# OpenClash Windows Captive Portal 规则应用记录（2026-08-19）

## 授权与范围

- 目标设备：GL.iNet GL-MT3000
- 用户确认：应用 Windows 四条精确直连；Linux 保持动态识别，不硬编码全发行版列表
- 变更范围：只修改 `/etc/openclash/custom/openclash_custom_rules.list`
- 未修改：活动 YAML、订阅节点、代理组、DNS 模式、Fake-IP 排除表和 Linux 探测域名

## 写入前预检

- 设备型号：`GL.iNet GL-MT3000`
- OpenWrt target：`mediatek/mt7981`
- OpenClash：`0.47.088`，状态 `running`
- 活动配置：`/etc/openclash/config/config.yaml`
- 持久化自定义规则：已启用
- 自定义 Fake-IP 排除：已启用
- 核心 PID：单进程
- overlay 可用空间：约 `113.7M`
- 四条目标规则写入前均为 0 条
- Fake-IP 排除表已存在 `+.msftconnecttest.com` 与 `+.msftncsi.com`

## 备份

写入前创建：

```text
/root/openclash-captive-windows-backup-20260819-110921.tgz
```

SHA-256：

```text
f1e4d60acbe43cc3a25185445caf65f50416d0ae60fc15e1acd82786a6caa1e2
```

备份包含：

- `/etc/config/openclash`
- `/etc/openclash/custom/openclash_custom_rules.list`
- `/etc/openclash/custom/openclash_custom_fake_filter.list`

## 应用内容

在已验证的 Apple 规则后增加：

```yaml
- DOMAIN,www.msftconnecttest.com,DIRECT
- DOMAIN,ipv6.msftconnecttest.com,DIRECT
- DOMAIN,www.msftncsi.com,DIRECT
- DOMAIN,ipv6.msftncsi.com,DIRECT
```

`dns.msftncsi.com` 已被现有 `+.msftncsi.com` 排除 Fake-IP；它是 DNS 探测主机，不另加 HTTP 直连规则。

## 重启后验证

- OpenClash 状态：`running`
- 活动配置仍为 `/etc/openclash/config/config.yaml`
- 自定义规则和自定义 Fake-IP 排除开关仍为 `1`
- 核心 PID：1 个
- 自定义规则文件中 Apple + Windows 五条规则连续排列，四条新规则各出现一次
- 生成配置 `/etc/openclash/config.yaml` 中五条规则连续加载
- 生成 Fake-IP 排除包含 `captive.apple.com`、`+.msftconnecttest.com`、`+.msftncsi.com`
- 最近系统日志未发现 OpenClash fatal、panic、语法错误或启动失败

客户端验证：

- `www.msftconnecttest.com`、`www.msftncsi.com` 和 `dns.msftncsi.com` 返回真实公网 DNS，不是 `198.18.0.0/15`
- `http://www.msftconnecttest.com/connecttest.txt` 返回 `Microsoft Connect Test`
- `http://www.msftncsi.com/ncsi.txt` 返回 `Microsoft NCSI`
- IPv6 探测主机可解析别名；当前验证没有证明酒店 IPv6 Captive Portal 链路

正常互联网下的响应只证明规则装载、DNS 与 HTTP 路径正确，不等于 Windows 已在真实酒店完成认证。Windows 现场验收仍待后续测试。

## RFC 8910 / RFC 8908 审计

本次同时只读检查了 MT3000 的 DHCP、RA、dnsmasq 和本地服务：

- 未发现 DHCPv4 Option 114 Captive-Portal 配置
- 未发现 DHCPv6 Option 103 或 IPv6 RA Option 37 配置
- 未发现 CAPPORT API URI 发布配置
- 未发现本机 RFC 8908 Captive Portal API 服务

因此，MT3000 当前没有作为 CAPPORT 网络运营方实现 RFC 8910/8908。现有 OpenClash 规则的作用是兼容 Apple 与 Windows 的传统 HTTP/DNS 主动探测，并避免代理/Fake-IP 阻断；酒店是否提供标准 CAPPORT 仍由酒店上游决定。

## Linux 决定

保持动态识别：先读取客户端 NetworkManager `ConnectivityCheckUri`，再按实际主机精确增加 Fake-IP 排除和 `DIRECT`。本次未给 `network-test.debian.org`、`detectportal.firefox.com` 或其他发行版域名增加直连。

## 回滚

确认目标设备和备份文件后执行：

```sh
tar xzf /root/openclash-captive-windows-backup-20260819-110921.tgz -C /
/etc/init.d/openclash restart
```

该备份是在 Windows 四条规则写入前、Apple 规则已存在时创建；回滚会保留此前 Apple 配置，只撤销本次 Windows 扩展及同期配置状态。
