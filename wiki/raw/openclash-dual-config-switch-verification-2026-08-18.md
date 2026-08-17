# OpenClash 第二配置切换验证记录（脱敏）

## 范围

- 日期：2026-08-18
- 设备：GL.iNet GL-MT3000
- 目标配置：先前导入的第二套 VLESS Reality 配置
- 密钥处理：未记录节点地址、UUID、Reality 参数或密码

## 内存校验发现

在原 OpenClash 核心仍运行时，先后启动了两次包含完整 GeoSite 规则的第二 Mihomo 检查进程。两个检查进程分别占用约 164 MB 和 143 MB 常驻内存，均被内核 OOM 机制终止；内核日志明确显示被杀进程是临时 `clash_meta`，原 PID 11452 的 `clash` 在两次事件中均仍存在。

随后使用去掉 GeoSite/GeoIP 规则的校验副本检查相同的协议、DNS 和代理组字段，路由器核心检查成功。由此确定通用脚本不应在活动核心旁运行第二个完整 GeoSite 校验进程。

## 切换结果

- 02:37 的 OpenClash 日志显示 `/etc/config/openclash` 修改后触发正常重启。
- UCI 选中路径为 `/etc/openclash/config/frank-us-home.yaml`。
- 实际运行路径为 OpenClash 处理后的 `/etc/openclash/frank-us-home.yaml`。
- OpenClash 状态为 `running`，init 服务保持启用。
- 通过活动核心 HTTP 代理端口访问 Cloudflare trace，出口国家为 `US`。
- 重启后可用内存约 181 MB，无 Swap。

## 可迁移结论

- 导入阶段使用轻量校验副本，避免与活动核心同时加载完整 GeoSite/GeoIP。
- GeoSite/GeoIP 文件存在性在 dry run 中单独检查。
- 完整配置的最终验收放在用户执行 `SwiTch` 和 `Apply Settings` 后，通过实际代理出口完成。
- “原始 YAML 路径”和“OpenClash 处理后的运行路径”不同是正常现象，应同时检查 UCI 与进程命令行。
