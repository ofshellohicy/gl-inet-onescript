# 来源：OpenClash 酒店 Captive Portal 绕过实机记录

## 摘要

该来源记录 2026-08-19 在 GL-MT3000、OpenClash `0.47.088`、Fake-IP 模式下，为 `captive.apple.com` 同时增加 Fake-IP 排除和置顶直连规则，并完成本地技术验证和真实酒店现场验收。记录已脱敏，不包含酒店身份或认证凭据。

## 已证实事实

- 目标设备经 live preflight 确认为 GL-MT3000，活动配置为原 `config.yaml`。
- 变更通过 OpenClash 持久化自定义层实现，没有直接编辑订阅配置或切换线路。
- 生成配置中直连规则位于第一条，域名不再返回 Fake-IP。
- OpenClash 重启后保持单核心运行，本地 Apple 检测页返回 `HTTP 200 / Success`。
- 用户随后在真实酒店 Wi-Fi 环境测试并确认效果“很好用”。

## 解释

初始 Apple 检测请求必须同时满足“得到真实地址”和“由上游直接访问”。前者避免 Fake-IP 映射，后者允许酒店网关拦截 HTTP 并返回认证流程。该结论已在本次酒店环境成立，但酒店后续可能重定向至未记录的动态域名。

该来源只证明 Apple 探测路径。Windows 使用独立的 NCSI 主机，Linux 的 NetworkManager URI由发行版或管理员配置；跨平台边界见后续补充考证。

## 来源

- [脱敏实机记录](../../raw/openclash-captive-portal-hotel-validation-2026-08-19.md)
- [公开操作文档](../../../docs/openclash-captive-portal-mt3000.md)

## 相关页

- [GL-MT3000](../entities/gl-mt3000.md)
- [OpenClash](../entities/openclash.md)
- [OpenClash Captive Portal 绕过方法](../analyses/openclash-captive-portal-bypass.md)
- [Captive Portal 跨平台补充考证](openclash-captive-portal-cross-platform-review-2026-08-19.md)
