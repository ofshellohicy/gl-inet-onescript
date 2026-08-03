# OpenClash 安装与固件升级恢复方法

## 问题

如何在 GL-MT3600BE 上按 OpenWrt 标准机制安装 OpenClash，并在重启、固件升级或恢复出厂后判断是否需要恢复？

## 结论

使用仓库内的 [`scripts/install-openclash-gl-mt3600be.sh`](../../../scripts/install-openclash-gl-mt3600be.sh)，先执行 `--dry-run`，确认型号为 GL-MT3600BE、CPU 为 AArch64、OpenWrt 包架构为 `aarch64_cortex-a53`，再执行 `--apply`。普通重启不需重装；固件升级或恢复出厂若清除了第三方包，应重新执行脚本。

## 标准流程

```sh
sh /tmp/install-openclash-gl-mt3600be.sh --dry-run
sh /tmp/install-openclash-gl-mt3600be.sh --apply
```

脚本会创建安装前备份、安装依赖与官方 IPK、部署 Linux ARM64 Mihomo 核心、启用 init 服务，并重载 LuCI ACL 与缓存。

## 状态判断

| 场景 | 结果 | 动作 |
| --- | --- | --- |
| 普通重启 | 软件包、配置和核心保留 | 无需重装 |
| 已有有效配置且已启用 | init 服务按配置启动 | 检查运行状态 |
| 无配置或未启用 | LuCI 存在，代理不运行 | 添加配置后手动启用 |
| 固件升级后菜单消失 | 第三方包可能被清除 | dry run 后重新安装 |
| 恢复出厂 | 包、密钥和配置可能清除 | 恢复 SSH 后重新安装与配置 |
| 包已安装但菜单不显示 | ACL 或会话可能未刷新 | 按 [LuCI ACL 与菜单刷新](../concepts/luci-acl-and-menu-refresh.md) 处理 |

## 安全边界

- 不安装非 `aarch64_cortex-a53` 架构的 OpenWrt 包。
- Mihomo 必须是 Linux ARM64 核心。
- TLS 校验异常时不使用 `curl -k`；改由可验证的电脑下载、核对哈希后通过 SSH 传输。
- 安装脚本不自动添加订阅、不自动开启代理，也不擅自修改 DHCP 或业务网络规则。

## 相关页

- [GL-MT3600BE](../entities/gl-mt3600be.md)
- [OpenClash](../entities/openclash.md)
- [GL-MT3600BE OpenClash 安装材料](../sources/gl-mt3600be-openclash-install.md)
