# OpenClash 订阅地区节点排除

## 问题

如何确认 OpenClash 原配置持续排除香港、澳门、台湾和新加坡节点，而不是当前订阅恰好没有这些节点？

## 结论

必须同时验证生成后的节点清单和订阅更新链路。2026-08-18 的原 `config.yaml` 当前确实没有四地区节点，用户已确认配置按现状验收为 OK，`奈飞` 是有意排除的节点关键词。现有 `sub_convert=0` 和澳门关键词边界只作为未来订阅更新后的复核依据，不要求现在修改。

## 三层检查

### 1. 结果层

解析 `proxies` 和 `proxy-groups[*].proxies`，使用中英文名称、边界化地区代码和旗帜识别节点。当前实测四地区计数全部为 0。

### 2. 配置层

检查 `proxy-providers`、代理组 `filter/exclude-filter`、OpenClash `ex_keyword` 和 `de_ex_keyword`。当前 YAML 是静态节点，没有 provider 过滤；UCI 排除词缺少澳门。

### 3. 更新链路

检查 `sub_convert` 和订阅地址参数。当前 `sub_convert=0`，OpenClash 直接下载无排除参数的订阅地址。若上游未来增加澳门或其他被排除地区节点，本机设置没有可靠阻止机制。

## 安全做法

- 不把订阅 URL、令牌或节点凭据写入仓库。
- 不直接修改生成后的 `config.yaml`，订阅更新会覆盖手工修改。
- 若启用订阅转换，先在新文件名下 dry run，确认节点计数、协议、代理组和核心检查，再替换旧配置。
- 每次订阅更新后重新运行结果层检查。
- 明确区分“排除代理节点”和“限制目标地区流量”。

## 当前状态

- 当前原配置：四地区节点为 0。
- 当前验收决定：OK，保持原配置不变。
- 奈飞节点排除：有意设置。
- 澳门持久排除：缺失。
- 现有排除词实际参与更新：否，原因是 `sub_convert=0`。
- 后续动作：订阅更新后重新审计，不立即修改。
- 路由器修改：本次未执行。

## 相关页

- [完整检查文档](../../../docs/openclash-region-node-exclusion.md)
- [审计来源摘要](../sources/openclash-original-config-region-audit-2026-08-18.md)
- [OpenClash](../entities/openclash.md)
- [OpenClash 双配置与 sing-box 转换](openclash-dual-config-and-sing-box-conversion.md)
