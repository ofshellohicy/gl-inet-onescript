# OpenClash 酒店 Captive Portal 绕过实机记录（脱敏）

## 范围

- 日期：2026-08-19
- 设备：GL.iNet GL-MT3000
- OpenClash：`0.47.088`
- 目标：OpenClash 保持运行时，允许酒店认证入口 `http://captive.apple.com/hotspot-detect.html` 走上游直连
- 隐私边界：未记录酒店名称、SSID、账号、密码、房号、验证码、节点地址或代理密钥

## 操作前状态

- 活动配置：`/etc/openclash/config/config.yaml`
- 运行模式：Fake-IP
- `enable_custom_clash_rules=0`
- `custom_fakeip_filter=0`
- `enable_redirect_dns=1`
- `captive.apple.com` 不在活动配置、生成配置或自定义 Fake-IP 排除表中
- OpenClash 服务处于 `running`

## Dry Run 结论

计划只修改全局持久化自定义规则，不直接编辑订阅配置：

```diff
 rules:
+- DOMAIN,captive.apple.com,DIRECT
```

```diff
 detectportal.firefox.com
+captive.apple.com
 resolver1.opendns.com
```

同时启用 `enable_custom_clash_rules` 和 `custom_fakeip_filter`。不修改节点、代理组、活动配置路径、DNS 重定向模式或另一套独立配置。

## 已执行变更

1. 确认 `192.168.8.1` 实机型号为 GL-MT3000，而非 MT3600BE。
2. 备份 `/etc/config/openclash`、自定义规则和 Fake-IP 排除表。
3. 原子替换两份已校验的自定义文件。
4. 启用两项 UCI 开关并提交。
5. 受控重启 OpenClash 一次；若规则或服务验证失败，执行备份回滚。

备份路径：

```text
/root/openclash-captive-apple-backup-20260819-104127.tgz
```

## 本地验证结果

- OpenClash 恢复 `running`。
- 活动配置仍为 `/etc/openclash/config/config.yaml`。
- 核心实际读取 `/etc/openclash/config.yaml`。
- 只有一个 Clash 核心进程。
- `DOMAIN,captive.apple.com,DIRECT` 位于生成配置 `rules:` 后第一条。
- `captive.apple.com` 已进入生成配置的 Fake-IP 排除表。
- 客户端 DNS 查询取得 8 个真实 IPv4 地址，`198.18.0.0/15` Fake-IP 为 0 个。
- 客户端访问检测页得到 `HTTP 200`，正文为 `Success`。
- 最近启动日志存在成功标记，未发现配置解析、Fatal 或 Panic 错误。

## 酒店现场验证

应用配置后，用户携带该 MT3000 在真实酒店 Wi-Fi 环境完成测试，并于 2026-08-19 反馈“很好用”。这构成实际 Captive Portal 链路可用的验收证据。

现场反馈没有包含酒店侧重定向链、认证域名、认证时长或重新认证行为，因此不能外推为所有酒店网络均兼容。

## 可复用结论

- 对已确认从 Apple Captive Portal 检测页进入的网络，同时配置 Fake-IP 排除和置顶 `DIRECT` 比单独添加域名规则更完整。
- OpenClash 自定义规则 1 会被合并到生成规则顶部，适合持久化该例外，而不应直接编辑可被订阅更新覆盖的 `config.yaml`。
- 现场验收必须区分无线关联、认证页完成和 OpenClash 代理出口；仅看到服务运行不等于认证成功。
- 后续若酒店重定向至其他域名后失败，应只补充必要域名，不扩大为全部 HTTP/HTTPS 直连。
