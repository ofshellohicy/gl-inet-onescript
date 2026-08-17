# OpenClash 双配置与 sing-box 转换方法

## 问题

如何把 Mac 上可用的 sing-box VLESS Reality 节点迁移到 GL-MT3000 或 GL-MT3600BE，同时保留路由器原有 OpenClash 配置并允许后续切换？

## 结论

把节点转换为一份完整、独立的 Mihomo YAML，并以新的文件名安装到 `/etc/openclash/config`。导入阶段不修改 `openclash.config.config_path`，不重启服务；验证通过后再由用户在 LuCI 中执行 `SwiTch` 和 `Apply Settings`。不要把新节点合并进原 `config.yaml`。

使用仓库内的 [`scripts/import-openclash-dual-config.py`](../../../scripts/import-openclash-dual-config.py)：

```sh
python3 scripts/import-openclash-dual-config.py \
  --source ~/.config/sing-box-client/client.json \
  --router 192.168.8.1 \
  --profile-name frank-us-home \
  --dry-run
```

确认型号、架构、核心、活动配置和目标文件后，才将 `--dry-run` 改为 `--apply`。

## 为什么可以跨 MT3000 与 MT3600BE

- VLESS、TLS、Reality、Vision、XUDP 是 Mihomo 配置语义，不依赖 MT7981 或 MT7987。
- 两台已观察设备都使用 AArch64 与 `aarch64_cortex-a53` 包架构。
- 真正依赖架构的是 Mihomo 可执行文件和 OpenWrt 软件包，不是节点 YAML。

因此可以复用转换脚本，但不能复用旧的实机结论。每台设备、每次固件升级后都要重新 dry run。

## 安全不变量

1. `config.yaml` 不被覆盖。
2. 同名第二配置不被覆盖。
3. 协议、DNS 和代理组字段先经路由器现有 Mihomo 核心检查；GeoSite/GeoIP 数据文件单独检查存在性。
4. 写入前创建可读取的备份包。
5. 导入后 UCI 活动路径与 OpenClash PID 必须和导入前一致。
6. 密钥配置只存在于 sing-box 源文件、本机临时文件和路由器配置目录，不进入仓库。

核心检查使用一份去掉 GeoSite/GeoIP 规则的校验副本，并带 `-d /etc/openclash`。GL-MT3000 实测表明，活动核心旁再启动完整 GeoSite 校验进程会触发 OOM；完整配置的出口验收应在用户切换后完成。本次切换后 OpenClash 启动成功，活动代理出口验证为美国。

## 切换语义

OpenClash 配置管理中的 `SwiTch` 保存新的 `config_path`；`Apply Settings` 才触发 OpenClash 按选中配置启动。切换时预计出现短暂断网。失败时通过 LuCI 或 SSH 将路径恢复到原 `config.yaml` 并重启 OpenClash。

## 规则策略

脚本生成的独立配置默认：

- 代理服务器地址直连，避免连接自身时形成路由循环；
- 私网与中国大陆目标直连；
- OpenAI 相关域名明确进入家庭宽带代理组；
- 其余流量最终进入同一代理组；
- DNS 使用 Fake-IP，并保留局域网和时间同步域名过滤。

这是一套面向美国家庭宽带出口的默认策略。其他用途应通过 `--proxy-domain` 增补域名，或在导入后复制配置再审查规则，不应直接修改仍在运行的原配置。

## 相关页

- [完整操作文档](../../../docs/openclash-dual-config-mt3000-mt3600.md)
- [GL-MT3000](../entities/gl-mt3000.md)
- [GL-MT3600BE](../entities/gl-mt3600be.md)
- [OpenClash](../entities/openclash.md)
- [双配置导入实机记录](../sources/openclash-dual-config-operation-2026-08-18.md)
