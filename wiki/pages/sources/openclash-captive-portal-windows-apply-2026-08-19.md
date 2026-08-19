# 来源：OpenClash Windows Captive Portal 规则应用记录

## 摘要

该来源记录 2026-08-19 在 GL-MT3000、OpenClash `0.47.088`、Fake-IP 模式下应用 Windows 新旧 NCSI 四条精确直连规则。写入前完成设备、空间、活动路径、开关和重复项预检；写入后只重启 OpenClash 一次，并验证单核心运行、运行时规则、真实 DNS 与 Microsoft 探测页正文。Linux 继续动态识别，未增加任何猜测域名。

## 已证实事实

- 四条 Windows HTTP 探测主机已进入持久化自定义层和生成配置，且各出现一次。
- 现有 `+.msftconnecttest.com`、`+.msftncsi.com` 继续负责 Fake-IP 排除，无需重复写入。
- OpenClash 重启后运行正常，活动配置路径和两个自定义开关未改变。
- IPv4 新旧 Windows HTTP 探测页分别返回预期正文，DNS 结果不是 Fake-IP；IPv6 规则已装载，但当前网络没有完成 IPv6 探测链路验证。
- 这些技术验证不等于 Windows 已完成真实酒店认证，现场验收仍待测试。
- MT3000 当前未发布 RFC 8910 CAPPORT DHCP/RA 选项，也未提供 RFC 8908 API；现有规则属于传统探测兼容层，不是 CAPPORT 服务端实现。
- Linux 保持按 NetworkManager `ConnectivityCheckUri` 动态识别，本次未新增直连域名。

## 来源

- [脱敏应用记录](../../raw/openclash-captive-portal-windows-apply-2026-08-19.md)
- [完整跨平台操作文档](../../../docs/openclash-captive-portal-mt3000.md)

## 相关页

- [GL-MT3000](../entities/gl-mt3000.md)
- [OpenClash](../entities/openclash.md)
- [OpenClash Captive Portal 跨平台绕过方法](../analyses/openclash-captive-portal-bypass.md)
