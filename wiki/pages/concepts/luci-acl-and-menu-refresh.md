# LuCI ACL 与菜单刷新

## 摘要

LuCI 菜单不显示不一定表示软件包未安装。新安装的 LuCI 应用可能已提供控制器和菜单索引，但当前 `rpcd` 进程和登录会话尚未加载新 ACL，导致菜单按权限被过滤。

## 已验证处理

1. 确认 `/usr/lib/lua/luci/controller/openclash.lua` 存在且 Lua 语法正常。
2. 确认 `/usr/share/rpcd/acl.d/luci-app-openclash.json` 存在。
3. 重启 `/etc/init.d/rpcd`。
4. 删除 `/tmp/luci-indexcache.*` 和 `/tmp/luci-modulecache/` 中的缓存文件。
5. 重启 `/etc/init.d/uhttpd`。
6. 注销或重新登录 LuCI，让新会话获得 ACL。

## 相关页

- [OpenClash](../entities/openclash.md)
- [GL-MT3600BE OpenClash 安装材料](../sources/gl-mt3600be-openclash-install.md)
- [OpenClash 安装与固件升级恢复](../analyses/openclash-install-and-recovery.md)
