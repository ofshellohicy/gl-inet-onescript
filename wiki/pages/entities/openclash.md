# OpenClash

## 摘要

OpenClash 在本项目中以 OpenWrt 标准软件包和 LuCI 应用方式安装，配合 Linux ARM64 Mihomo 核心运行。安装脚本不自动添加订阅或启用代理；双配置脚本只新增经过核心检查的独立 YAML，不自动切换或重启服务。

## 当前事实

- 2026-07-18 实机安装版本：`luci-app-openclash 0.47.116`。
- 核心路径：`/etc/openclash/core/clash_meta`。
- LuCI 入口：`http://192.168.8.1:8080/cgi-bin/luci/admin/services/openclash`。
- init 服务位于 `/etc/init.d/openclash`，实机已创建 `S99openclash`链接。
- 无订阅或配置时保持停用是预期状态。

## 关联

- 设备：[GL-MT3000](gl-mt3000.md)
- 设备：[GL-MT3600BE](gl-mt3600be.md)
- 概念：[LuCI ACL 与菜单刷新](../concepts/luci-acl-and-menu-refresh.md)
- 来源：[GL-MT3600BE OpenClash 安装材料](../sources/gl-mt3600be-openclash-install.md)
- 来源：[OpenClash 双配置导入实机记录](../sources/openclash-dual-config-operation-2026-08-18.md)
- 方法：[OpenClash 双配置与 sing-box 转换](../analyses/openclash-dual-config-and-sing-box-conversion.md)
