# OpenClash 双配置导入实机记录（脱敏）

## 范围

- 日期：2026-08-18
- 当前实机：GL.iNet GL-MT3000
- 目标平台：`mediatek/mt7981`
- 包架构：`aarch64_cortex-a53`
- OpenClash：`0.47.088`
- 配置来源：本机 sing-box JSON 中的 VLESS + TLS + Reality outbound
- 密钥处理：节点地址、UUID、Reality 参数和密码均未写入本记录

## 操作前状态

- 原活动配置：`/etc/openclash/config/config.yaml`
- OpenClash 已启用并处于 `running`
- Mihomo 为 Linux ARM64 核心，支持 VLESS Reality、Vision 和 XUDP
- LuCI 位于 `8080` 端口

## 已执行流程

1. 只读核对设备型号、CPU、OpenWrt 包架构、剩余空间、OpenClash 和 Mihomo。
2. 从 sing-box JSON 结构化读取 VLESS outbound，转换为独立 Mihomo YAML；未打印敏感字段。
3. 在 Mac 的 Mihomo 临时进程中完成配置检查和代理出口测试。
4. 将配置上传到路由器 `/tmp`，使用路由器现有 Mihomo 核心检查，并以独立临时进程验证美国出口。
5. 备份 OpenClash UCI 和配置目录。
6. 将第二配置原子写入 `/etc/openclash/config/frank-us-home.yaml`，未修改 `openclash.config.config_path`，未重启 OpenClash。
7. 在 LuCI 配置管理页确认原配置为 `Enabled`、第二配置为 `Disabled`。
8. 修复重置后的 SSH 主机键记录并重新安装 Mac 公钥。
9. 删除 Mac 与路由器上的测试临时文件。

## 验证结果

- 新配置通过 Mac 和路由器两侧 Mihomo 检查。
- 独立代理测试出口国家为美国。
- 原活动配置路径保持不变。
- OpenClash PID 在安装第二配置前后保持不变。
- OpenClash 服务保持 `running`，init 服务保持启用。
- 两套 YAML 均在 LuCI 配置管理页可见。
- 备份包存在且可由 `tar -tzf` 正常读取。

## 可迁移结论

- VLESS Reality 的 Mihomo YAML 不绑定 MT3000；只要 MT3600BE 实机仍为 AArch64、OpenClash 与 Mihomo 支持对应字段，同一转换方法可复用。
- 复用的是转换和无扰导入流程，不是跳过硬件、固件和核心预检。
- 第二配置应作为完整独立 YAML 存放，通过 LuCI 的配置管理切换；不要直接改写原配置。

## 未验证项

- 本次未在 MT3600BE 上实际导入第二配置。
- 本次未切换路由器的活动配置，也未重启 OpenClash。
- MT3600BE 执行前必须重新 dry run，并独立验证出口。
