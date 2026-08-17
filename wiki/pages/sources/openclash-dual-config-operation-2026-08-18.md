# 来源：OpenClash 双配置导入实机记录

## 摘要

该来源组合记录了 2026-08-18 在 GL-MT3000 上将 sing-box VLESS Reality outbound 转换为独立 Mihomo YAML、无扰导入 OpenClash，以及后续切换和美国出口验证。记录已脱敏，可用于指导后续 GL-MT3600BE 操作。

## 已证实事实

- GL-MT3000 实机目标为 `mediatek/mt7981`，包架构为 `aarch64_cortex-a53`。
- 新配置在 Mac 和路由器 Mihomo 核心上均通过检查，独立测试取得美国出口。
- 安装前后活动路径仍为原 `config.yaml`，OpenClash PID 未变化。
- LuCI 可以同时显示原配置和第二配置。
- 安装过程可以拆成 dry run、核心检查、备份、原子写入、状态不变验证和清理。
- 活动核心旁运行第二个完整 GeoSite 校验进程会耗尽 MT3000 可用内存；轻量校验副本可通过核心检查。
- 切换并 Apply 后，UCI 原始配置路径与 OpenClash 处理后的运行路径均指向第二配置，活动代理出口为美国。

## 解释

Mihomo 配置的可迁移性来自协议字段一致，而不是设备型号相同。MT3600BE 可以复用转换脚本，但必须重新验证型号、目标平台、包架构、OpenClash 版本和核心能力。

## 来源

- [脱敏实机记录](../../raw/openclash-dual-config-operation-2026-08-18.md)
- [切换验证记录](../../raw/openclash-dual-config-switch-verification-2026-08-18.md)
- [公开操作文档](../../../docs/openclash-dual-config-mt3000-mt3600.md)
- [转换与导入脚本](../../../scripts/import-openclash-dual-config.py)

## 相关页

- [GL-MT3000](../entities/gl-mt3000.md)
- [GL-MT3600BE](../entities/gl-mt3600be.md)
- [OpenClash](../entities/openclash.md)
- [OpenClash 双配置与 sing-box 转换方法](../analyses/openclash-dual-config-and-sing-box-conversion.md)
