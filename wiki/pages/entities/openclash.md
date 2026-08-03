# OpenClash

## 摘要

OpenClash 在本项目中以 OpenWrt 标准软件包和 LuCI 应用方式安装，配合 Linux ARM64 Mihomo 核心运行。脚本负责安装和集成，不自动添加订阅或启用代理。

## 当前事实

- 2026-07-18 实机安装版本：`luci-app-openclash 0.47.116`。
- 核心路径：`/etc/openclash/core/clash_meta`。
- LuCI 入口：`http://192.168.8.1:8080/cgi-bin/luci/admin/services/openclash`。
- init 服务位于 `/etc/init.d/openclash`，实机已创建 `S99openclash`链接。
- 无订阅或配置时保持停用是预期状态。

## 关联

- 设备：[GL-MT3600BE](gl-mt3600be.md)
- 概念：[LuCI ACL 与菜单刷新](../concepts/luci-acl-and-menu-refresh.md)
- 来源：[GL-MT3600BE OpenClash 安装材料](../sources/gl-mt3600be-openclash-install.md)
