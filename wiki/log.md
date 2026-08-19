# GL.iNet OneScript 项目知识库变更日志

## [2026-08-19] apply | Windows NCSI 精确直连

- 在单独授权后，对 GL-MT3000 应用 Windows 新旧 NCSI 四条精确 `DIRECT`，Linux 保持动态识别且未新增域名。
- 写入前备份 OpenClash UCI 与两份自定义文件；只重启 OpenClash 一次。
- 验证四条规则进入持久化自定义层和生成配置，Microsoft 后缀继续排除 Fake-IP，核心单进程运行且活动路径未改变。
- IPv4 客户端获得真实 DNS，新旧 Microsoft 探测页分别返回预期正文；IPv6 链路和 Windows 酒店现场仍待验收。
- 只读确认 MT3000 未发布 RFC 8910 DHCP/RA CAPPORT 选项，也未提供 RFC 8908 API；当前实现是传统探测兼容层，不是 CAPPORT 服务端。

## [2026-08-19] review | Captive Portal 跨平台补充考证

- 按 iOS/macOS、Windows 和 Linux 分开核对系统连通性探测机制，不再把 Apple 地址写成通用入口。
- 只读确认 MT3000 已对 Microsoft、Debian 和 Firefox 探测主机排除 Fake-IP，但直连规则仍只有 Apple 主机。
- 给出 Windows 精确直连 dry run；本次未修改在线路由器，Windows 与 Linux 尚未现场验收。
- 记录 Linux NetworkManager URI 由发行版或管理员配置，必须先读取 `ConnectivityCheckUri`，不能维护虚假的全 Linux 静态列表。
- 补充 Public Hotspot Login Mode 的通用兜底及 DNS/原生 HTTP 暴露边界。

## [2026-08-19] ingest | OpenClash 酒店 Captive Portal 实测

- 入库 GL-MT3000、OpenClash `0.47.088`、Fake-IP 模式的脱敏配置与验证记录。
- 记录 `captive.apple.com` 同时加入 Fake-IP 排除和置顶 `DIRECT` 的最小持久化方法。
- 本地验证生成规则顺序、真实 DNS、`HTTP 200 / Success`、单核心运行和活动配置不变。
- 用户随后在真实酒店 Wi-Fi 环境测试并反馈“很好用”，形成现场验收证据。
- 明确该结论不覆盖酒店后续动态域名、专用 App、客户端证书或所有 Captive Portal 实现。

## [2026-08-18] audit | 原配置地区节点排除

- 脱敏解析原 `config.yaml` 的节点、代理组、协议、旗帜地区和规则策略统计。
- 确认当前香港、澳门、台湾、新加坡节点及代理组引用均为 0。
- 发现订阅排除词缺少澳门，且 `sub_convert=0` 时 OpenClash 不把 `ex_keyword` 用于直接订阅下载。
- 新增地区排除检查文档、来源摘要和分析页；未修改路由器配置。
- 用户确认当前配置验收为 OK，`奈飞` 是有意排除的节点关键词；记录为策略决定，不立即修改。

## [2026-08-18] ingest | OpenClash 双配置与 sing-box 转换

- 入库 GL-MT3000 双配置导入脱敏实机记录和来源摘要。
- 新增 GL-MT3000 实体页以及 MT3000/MT3600BE 共用的双配置分析页。
- 新增默认 dry run 的 sing-box VLESS Reality 转换与无扰导入脚本。
- 记录 MT3600BE 可复用范围、live preflight 要求、LuCI 切换语义和敏感配置边界。
- 追加第二配置切换、美国出口验证及完整 GeoSite 双核心校验触发 OOM 的实机证据。

## [2026-08-03] ingest | GL-MT3600BE OpenClash 安装与恢复

- 将安装脚本迁入 `scripts/`，将配套说明迁入 `docs/`。
- 入库安装说明和 2026-07-18 实机操作记录。
- 新增 GL-MT3600BE、OpenClash、LuCI ACL 与安装恢复页面。
- 记录普通重启、固件升级、恢复出厂的不同影响。

## [2026-08-03] bootstrap | 初始化项目知识库

- 创建 wiki 目录、索引、概览、规范与日志。
