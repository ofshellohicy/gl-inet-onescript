# OpenClash

## 摘要

OpenClash 在本项目中以 OpenWrt 标准软件包和 LuCI 应用方式安装，配合 Linux ARM64 Mihomo 核心运行。安装脚本不自动添加订阅或启用代理；双配置脚本只新增经过核心检查的独立 YAML，不自动切换或重启服务。

## 当前事实

- 2026-07-18 实机安装版本：`luci-app-openclash 0.47.116`。
- 核心路径：`/etc/openclash/core/clash_meta`。
- LuCI 入口：`http://192.168.8.1:8080/cgi-bin/luci/admin/services/openclash`。
- init 服务位于 `/etc/init.d/openclash`，实机已创建 `S99openclash`链接。
- 无订阅或配置时保持停用是预期状态。
- `ex_keyword` 只在订阅转换链路中形成排除参数；`sub_convert=0` 的直接下载不能仅靠该字段保证节点过滤。
- GL-MT3000 实测可通过持久化自定义层将 `captive.apple.com` 排除 Fake-IP 并置顶 `DIRECT`，在 OpenClash 保持运行时完成酒店认证。
- 跨平台配置不能只维护 Apple 地址：Windows NCSI 的四条 HTTP 探测主机已精确直连，Microsoft 后缀继续排除 Fake-IP；Linux NetworkManager URI 由发行版或管理员配置，本次不硬编码 Linux 直连域名。
- OpenClash 的域名规则属于传统探测兼容层；它不负责发布 RFC 8910 CAPPORT DHCP/RA 选项或提供 RFC 8908 API。

## 关联

- 设备：[GL-MT3000](gl-mt3000.md)
- 设备：[GL-MT3600BE](gl-mt3600be.md)
- 概念：[LuCI ACL 与菜单刷新](../concepts/luci-acl-and-menu-refresh.md)
- 来源：[GL-MT3600BE OpenClash 安装材料](../sources/gl-mt3600be-openclash-install.md)
- 来源：[OpenClash 双配置导入实机记录](../sources/openclash-dual-config-operation-2026-08-18.md)
- 方法：[OpenClash 双配置与 sing-box 转换](../analyses/openclash-dual-config-and-sing-box-conversion.md)
- 方法：[OpenClash 订阅地区节点排除](../analyses/openclash-subscription-region-exclusion.md)
- 来源：[OpenClash 酒店 Captive Portal 绕过实机记录](../sources/openclash-captive-portal-hotel-validation-2026-08-19.md)
- 来源：[OpenClash Captive Portal 跨平台补充考证](../sources/openclash-captive-portal-cross-platform-review-2026-08-19.md)
- 来源：[OpenClash Windows Captive Portal 规则应用记录](../sources/openclash-captive-portal-windows-apply-2026-08-19.md)
- 方法：[OpenClash Captive Portal 跨平台绕过](../analyses/openclash-captive-portal-bypass.md)
