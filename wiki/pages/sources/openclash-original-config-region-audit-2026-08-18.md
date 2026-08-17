# 来源：OpenClash 原配置地区节点审计

## 摘要

该来源是 2026-08-18 对 GL-MT3000 原 `config.yaml` 的脱敏只读检查。当前 48 个节点和两个代理组均没有香港、澳门、台湾或新加坡节点，但订阅更新设置不能保证未来继续排除。

## 已证实事实

- 当前节点地区仅包括 US、JP、GB、DE、AU、CA、ID、IN、FR。
- HK、MO、TW、SG 节点数均为 0，代理组也没有四地区引用。
- 当前 `ex_keyword` 是香港、台湾、奈飞、新加坡，不包含澳门。
- `sub_convert=0`，订阅地址无查询参数。
- OpenClash 当前脚本只在订阅转换路径中使用 `ex_keyword` 生成 `exclude` 参数。
- 用户确认当前配置验收为 OK，`奈飞` 是有意排除的节点关键词。

## 判断

应把“当前快照没有四地区节点”和“订阅更新机制保证四地区排除”分开。当前配置按用户决定继续使用，不做修改；后续 MT3000 或 MT3600BE 更新订阅时重新审计即可。

## 来源

- [脱敏审计记录](../../raw/openclash-original-config-region-audit-2026-08-18.md)
- [用户策略确认](../../raw/openclash-original-config-policy-confirmation-2026-08-18.md)
- [地区节点排除检查文档](../../../docs/openclash-region-node-exclusion.md)

## 相关页

- [OpenClash](../entities/openclash.md)
- [OpenClash 订阅地区节点排除](../analyses/openclash-subscription-region-exclusion.md)
- [OpenClash 双配置与 sing-box 转换](../analyses/openclash-dual-config-and-sing-box-conversion.md)
