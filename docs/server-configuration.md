# 服务器配置与部署记录

## 当前版本：V1.5.5（2026-11-01）

正式API仍为 `https://api.laowaiyidiantong.icu/api/v1`，HTTPS健康返回1.5.5；数据库仍为csca_hks_exam，最新迁移 `0013_trial_admin_owner`。本次从1.5.4/0011增量升级0012、0013，来源为本机已审阅的1.5.5工作树（基础提交7a4ed5f55ee4589b82549bade3756bd2b59488bd，含未提交文件），没有Git提交/推送或微信小程序发布。

维护时原73用户、52试卷、189答题、80错题、79知识统计、21打卡、2目标日期、1221题及0收藏/反馈保留。用户id、编号、身份和学习记录不变；新增admin_owner、admin_members、admin_audit_logs三表，内容4→5，1.5.5公告仅草稿。以上为维护时点，不代表以后实时数量。

| 项目 | 当前配置或位置 |
|---|---|
| 发布标识 | v1.5.5-20261101-141218 |
| 后端包 | laowai-backend-v1.5.5-20261101-141218.tar.gz，90594字节，108文件 |
| SHA-256 | 3338cc0b5152f82e932af438e612353468339c9e2286d7bc61e482eeff68d3c8 |
| 更新前备份 | /var/backups/laowai/before-v1.5.5-20261101-141218 |
| SQL | laowai-20261101T061239Z.sql.gz，配套配置、上传目录、SHA/metadata及code.before.tar.gz |
| 旧代码 | /opt/laowai/rollback/v1.5.5-20261101-141218/csca-hks-exam-app |
| 临时主管理员 | lw005，内部用户ID=5，admin_owner主键1，is_temporary=true |
| 正式本人编号 | lw000继续预留，当前未绑定 |
| 当前状态 | /opt/laowai/deployment/current-release.json |
| 部署报告 | /opt/laowai/deployment/deploy-v1.5.5-20261101-141218.json |
| HTTPS验收 | /opt/laowai/deployment/verification-v1.5.5-20261101-141218.json |

用户在本次部署会话明确确认同时启用lw005临时主管理员，已按bootstrap_admin_owner.py预览核实ID=5，再显式--temporary --expected-user-id 5 --apply绑定。保留lw005，不改主键和学习记录、不占lw000。该标记不设自动到期，不自动转为正式本人；以后转交须独立授权和核实，不能从小程序直接覆盖唯一owner。

管理角色每次请求从数据库读取：普通用户/游客不可读写管理数据，viewer只能读取总览/用户统计/反馈全文/内容草稿，唯一owner才可维护内容、反馈状态和只读管理员。旧CONTENT_ADMIN_OPENIDS不再授予HTTP管理权限，已核实线上配置为空；编号lw000本身也不授予权限。普通资料接口不能更改admin_role。1.5.5草稿由主管理员试用后决定是否公开，本次未发布。

服务器隔离38项相关检查通过，Alembic check无待更新结构、绑定前后完整性clean。HTTPS验证普通/游客拒绝、lw005角色和管理读取、viewer能读不能发布/授权、owner授权及撤销后同一JWT立即失权。验收合成用户和临时授权已删除、所发编号永久退役；保留真实审计3条（首次临时绑定1条、验收grant/revoke各1条），合成目标删除后target_user_id按外键置空。admin_members未留下正式成员，lw005真实绑定保留。

复用服务器Python环境，依赖未变；无清库、重导题、媒体或头像配置调整。数据库/配置/上传目录已备份并校验，健康与备份定时器恢复。Nginx、TLS、凭据、API端口、媒体与头像持久目录及每日03:20/14天本机备份规则沿用下方1.5.4配置，无异地备份。本轮未重新前端构建或手机验收，用户使用1.5.5前端并在lw005“我的”刷新资料可见管理中心。

回退应用时保留永久编号、角色/审计表及上传文件，不删除式downgrade或覆盖旧SQL而丢失后来记录。不要通过恢复旧白名单权限绕过只读策略；需要回退应先核查权限实现和白名单仍为空。1.5.4旧代码不会展示新管理中心，但应保留数据库中的lw005绑定供后续恢复。

README、memory、版本说明及配置文档同步，本机配置副本 `.deployment-access/server-configuration.md`，服务器副本在 `/opt/laowai/deployment/server-configuration.md` 与 `/home/deploy/laowai-deployment-docs/server-configuration.md`。以下1.5.4及更早版本均为历史记录。

## 历史版本：V1.5.4（2026-11-01）

正式API仍为 `https://api.laowaiyidiantong.icu/api/v1`，HTTPS健康返回1.5.4；MySQL数据库仍为csca_hks_exam，最新迁移 `0011_login_strategy`。本次直接从1.5.2升级，来源为已审阅的本机1.5.4工作树，基础提交984830324e4a357c6928293133a18df5e8400155，包含未提交文件；没有替用户提交、推送或发布微信小程序。

维护时保留73用户、52份试卷、189条答题、80条错题、79条知识统计、21条打卡、2条目标日期、1221题及0收藏/反馈。新增user_code_counters表1行，用户回填唯一lw编号；内容2→4，两份公告1.5.3“撤销AI功能”和1.5.4“优化登录策略”公开。原身份、主键、学习记录与题库保留；数量只代表维护时点。lw000未绑定，管理白名单不扩大。

| 项目 | 本次配置或位置 |
|---|---|
| 发布标识 | v1.5.4-20261101-130000-r2 |
| 后端代码包 | laowai-backend-v1.5.4-20261101-130000-r2.tar.gz，83702字节，100文件 |
| SHA-256 | 6c0f57cb94940d3840ef04b244a1c407462cc3c48c0f1a7bf2b77218dec335a4 |
| 原始迁移前备份 | /var/backups/laowai/before-v1.5.4-20261101-125500 |
| 原始SQL | laowai-20261101T045508Z.sql.gz，配套配置与code.before.tar.gz |
| 最终切换前备份 | /var/backups/laowai/before-v1.5.4-20261101-130000-r2 |
| 最终切换前SQL | laowai-20261101T045641Z.sql.gz，配套配置与code.before.tar.gz |
| 前版兼容代码 | /opt/laowai/rollback/v1.5.4-20261101-130000-r2/csca-hks-exam-app |
| 当前状态 | /opt/laowai/deployment/current-release.json |
| 部署记录 | /opt/laowai/deployment/deploy-v1.5.4-20261101-130000-r2.json |
| HTTPS验收记录 | /opt/laowai/deployment/verification-v1.5.4-20261101-130000-r2.json |
| 头像目录 | /opt/laowai/user_uploads/avatars，laowai:deploy、0750，服务UMask0077 |
| 服务覆盖配置 | /etc/systemd/system/laowai-api.service.d/avatars.conf |

基础系统、数据库账号、生产凭据、证书、题库和媒体目录沿用既有配置。Pillow13.0.0和python-multipart0.0.12原已存在，未安装依赖。后端只在127.0.0.1:8000监听，Nginx继续代理正式API。AI公开接口已停用，返回404；私有业务接口要求JWT，微信登录不能在生产环境回退开发身份。

头像为新增持久数据。systemd覆盖配置明确设置 `USER_AVATAR_ROOT=/opt/laowai/user_uploads/avatars` 与 `ReadWritePaths=/opt/laowai/user_uploads/avatars`，代码替换不会删除头像。应用只接收不超过2MiB的PNG/JPEG/WebP，重新编码为最大512像素JPEG；Nginx的client_max_body_size由2m调整至3m，为multipart边界留空间。

`laowai-backup`每日约03:20的数据库/配置备份新增 `.uploads.tar.gz`、metadata与SHA，包含整个 `/opt/laowai/user_uploads`；配置归档同时包含新systemd覆盖目录。扩展后的首份备份 `laowai-20261101T045646Z.uploads.tar.gz` 已生成并确认含头像目录，当时尚无真实头像。备份与健康检查timer均已恢复。仍为本服务器14天保留，无异地副本；原始及r2发布前备份在各自子目录单独保留。

迁移经过0009→0010→0011，首次部署在数据迁移完成后发现ORM与字段注释不一致，自动回退代码且保留新编号。修正0011的add/alter字段注释后，r2先再次备份，再补齐已应用字段的注释，最终Alembic check无新结构操作、完整性clean。后续勿重复清库、重新发号或执行downgrade。原始1.5.2模型不能给新用户填写非空user_code；回退应用必须保留编号模型/事务分配器和迁移历史，不能直接覆盖旧代码或恢复旧SQL而丢失后续记录。r2旧代码目录已经带有该兼容支持，并保留AI停用状态。

21项服务器隔离专项测试通过；迁移注释修复后仅追加1项相关验证。HTTPS验收确认版本、AI404、游客401、两份公告原文、新编号、昵称保存、禁止修改编号、2MiB头像上传、安全JPEG缩放与读取及无效图片拒绝。唯一合成账号和头像已删除，其编号永久退役，不应调低计数器回收。没有重新安装环境、导题、全盘回归或重复媒体哈希。

微信端由用户自行上传/发布1.5.4，并检查uploadFile合法域名包含 `https://api.laowaiyidiantong.icu`，真机验收登录、头像、昵称和退出。服务端部署完成不代表微信后台配置或小程序发布已完成。当前配置副本同步至本机 `.deployment-access/server-configuration.md` 与服务器交付目录。以下各版本为历史，不代表当前版本。

## 历史版本：V1.5.2（2026-10-26）

正式后端已部署提交d58e85f7，健康接口返回1.5.2。发布标识 `v1.5.2-20261026-193000`；数据库名仍为csca_hks_exam，已备份后从0008升级至 `0009_release_1_5_2`。本次迁移只新增定稿公告，不改表结构或学习数据，没有清库、重建或导入题库。

维护前后原记录数量保持一致：42用户、22份试卷、71条答题、26条错题、30条知识统计、10条打卡、1221题，收藏/目标日期/反馈均为0。内容从1条增至2条，新增公开的1.5.2公告，旧1.5.1草稿保留。上述数量为本次维护时点，后续真实使用会生成新数据。

| 项目 | 本次配置或位置 |
|---|---|
| 后端代码包 | laowai-backend-v1.5.2-20261026-193000.tar.gz，73789字节，92文件 |
| SHA-256 | efe1834689fc469cc2d9be6770a6186a69b38b3a625c00573e99f20efb165af1 |
| 更新前备份 | /var/backups/laowai/before-v1.5.2-20261026-193000 |
| SQL备份 | laowai-20261026T114512Z.sql.gz，配套配置、校验及旧代码归档 |
| 回退代码 | /opt/laowai/rollback/v1.5.2-20261026-193000/csca-hks-exam-app |
| 当前记录 | /opt/laowai/deployment/current-release.json |
| 部署详情 | /opt/laowai/deployment/deploy-v1.5.2-20261026-193000.json |
| 验收记录 | /opt/laowai/deployment/verification-v1.5.2-20261026-193000.json |

AI支持可选 `language: zh/en`，省略时默认中文；英语界面默认英语，用户明确指定语言优先，模型仍为qwen3.8-27b。复用已有Python环境，无新依赖和环境变量。Nginx、证书、凭据、题库和媒体均未改动；定时备份和健康检查恢复。

本地和服务器各通过7项AI/公告专项测试，没有全量回归或重复媒体检查。正式HTTPS已验证版本、实际英语回复、非法语言拒绝，以及公告标题/摘要/三项正文准确公开；合成验收账号已清理。微信前端上传、审核、发布及真机人工检查仍由用户完成。

本节为当前状态，以下1.5.1及1.5.0内容为历史部署记录；不要据旧章节重复清库、迁移或发布旧公告。

## 历史版本：V1.5.1（2026-10-25）

正式API仍为 https://api.laowaiyidiantong.icu/api/v1 ，健康接口现在返回版本1.5.1。部署提交f5ae203b，发布标识 `v1.5.1-20261025-220540`，数据库已从0007增量升级至 `0008_feedback_announcements`；未清库、未重新导入题库，也未改动现有生产凭据和媒体服务。

迁移前备份后，对10张原业务表的原字段及原记录范围逐表计算SHA并比对，确认全部保留：34用户、18份试卷、44条答题、21条错题、28条知识统计、8条打卡、1221道题，收藏与目标日期记录均为0。内容库原有0条，迁移仅新增1份未发布的1.5.1公告草稿；新feedback表初始为空。验收合成账号和反馈已清理，不保证后续真实使用的数据量仍相同。

| 项目 | 本次配置或位置 |
|---|---|
| 部署包 | laowai-backend-20261025-220659.tar.gz，52,776,431字节 |
| SHA-256 | d31080a25c3d203f3ea9ae0e74db59198f14124c5746a40b6e8dd6a7e8ddc16b |
| 备份目录 | /var/backups/laowai/before-v1.5.1-20261025-220540，root专用 |
| SQL备份 | laowai-20261025T141353Z.sql.gz，配套SHA和配置备份已验证 |
| 旧代码归档 | 备份目录内code.before.tar.gz |
| 回退代码 | /opt/laowai/rollback/v1.5.1-20261025-220540/csca-hks-exam-app |
| 当前记录 | /opt/laowai/deployment/current-release.json |
| 部署详情 | /opt/laowai/deployment/deploy-v1.5.1-20261025-220540.json |
| 验收记录 | /opt/laowai/deployment/verification-v1.5.1-20261025-220540.json |

既有Python虚拟环境继续使用当前server/.venv路径，没有重装依赖；原健康检查和数据库/配置备份定时器已恢复。新增反馈自动纳入完整数据库备份。源码及用户数据的更新前备份另存于上表目录，本次没有下载含密钥的配置备份到本机。

反馈可以在服务器直接读取或显式标记：

```bash
sudo laowai-feedback --status unread
sudo laowai-feedback --mark 12 --to read
sudo laowai-feedback --mark 12 --to resolved
```

反馈内容和导出文件须保存在私有位置。`CONTENT_ADMIN_OPENIDS`目前仍为空，管理员页面/API不会对普通用户开放；需要使用时由运营者在 `/etc/laowai/config.json` 中设置实际运营OpenID并执行 `sudo laowai-config check`、`sudo laowai-config apply`。不能猜测管理员身份。公告草稿在微信新版正式发布并核对内容后再由运营者启用，本次没有公开发布。

本地及服务器隔离测试各71项通过；正式HTTPS验证了私密反馈、幂等、冲突和限额、运营读取和标记、公告隐藏、AI拒绝客户端system角色及真实回复。原题库和153份媒体与包内源文件一致，未覆盖其目录；现有题库接口和音频Range访问正常。

本次只新增表和字段。代码回退可保留0008结构，避免删除已产生的反馈；不要直接降级或覆盖现有用户数据。下方是2026-10-22首次题库替换时的历史配置，版本、数据量及当次清库说明以本节为准。

## 2026-10-22题库替换与基础配置（历史）

更新：2026-10-22，Asia/Shanghai。本文件为新版题库上线后的实际状态，不包含密码、AppSecret、API Key、JWT 密钥或证书私钥。

## 当前运行状态

| 项目 | 配置与结果 |
|---|---|
| 服务器 | 腾讯云上海轻量服务器，43.142.125.251，Debian 13.7，2核/约2GB内存/40GB系统盘/2GB Swap |
| API | https://api.laowaiyidiantong.icu/api/v1 |
| 健康检查 | https://api.laowaiyidiantong.icu/api/v1/health |
| 题库目录接口 | https://api.laowaiyidiantong.icu/api/v1/question/catalog |
| 发布标识 | bank-v2-20261022-173312 |
| 后端包 | laowai-backend-20261022-055704.tar.gz，52,755,022字节 |
| SHA-256 | efc7eb5950584025086661b2ae7e46f6c0ea8886fc1f8befa3bc98b99b9b6fc0 |
| 数据库 | MySQL 8.4.11，csca_hks_exam，迁移0007_question_bank_v2 |
| 题目 | 1,221：CSCA550、内部HKS671；暂缓99道口语/口译 |
| 媒体 | 94份音频、59张图片，共153文件，均已安装到本机服务器 |
| AI | qwen3.8-27b，已通过正式AI接口验证非空回复 |
| 进程 | systemd管理laowai-api；Nginx与MySQL持续运行 |

用户明确授权清空旧正式业务数据并直接切换新版。清库前实际数据为1,876题、20用户、22份试卷、39条答题记录、9条错题、10条收藏；已备份并做隔离恢复验证。新版初始化及验收清理后，用户、试卷和答题记录均为0。后续真实使用会生成新数据。

小程序仍需由用户完成微信审核与正式发布。此次不实现旧客户端兼容；手机仍运行旧客户端时，HSK组卷可能因缺少考试版本/等级而失败。源码、manifest及健康响应中的通用版本字段仍为1.0.0，不能据此判断本次发布包，使用上表发布标识及哈希。

## 目录和配置

| 路径 | 用途 |
|---|---|
| /opt/laowai/csca-hks-exam-app/server | 当前后端源码 |
| /opt/laowai/csca-hks-exam-app/server/.venv | 复用的Python 3.13.5环境，未重新安装依赖 |
| /opt/laowai/csca-hks-exam-app/scripts | 新版题库导入、重建和检查工具 |
| /opt/laowai/original_question_bank | 新版31份原题JSON及153份活动媒体；完整替换旧题库目录 |
| /var/lib/laowai-media/bank-v2/HSK/_assets | Nginx对外提供的媒体文件副本 |
| /etc/laowai/config.json | root维护的生产配置，0600 |
| /etc/laowai/backend.env | systemd使用的环境文件，0600 |
| /etc/laowai/migration.json | 独立迁移账号凭据，0600 |
| /etc/systemd/system/laowai-api.service | 以laowai账号、deploy组运行，监听127.0.0.1:8000 |
| /etc/nginx/sites-available/laowai-api | HTTPS代理和新版媒体白名单 |

生产关键参数：

```dotenv
APP_ENV=production
AUTH_ALLOW_DEV_OPENID=false
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=laowai_app
MYSQL_DATABASE=csca_hks_exam
QUESTION_BANK_ROOT=/opt/laowai/original_question_bank
QUESTION_MEDIA_BASE_URL=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.8-27b
QWEN_TIMEOUT_SECONDS=45
QWEN_MAX_TOKENS=1024
```

微信凭据、数据库密码、AI Key及JWT签名密钥沿用服务器私有配置，未写入源码。JWT主体是OpenID。日常应用账号仍仅有DML权限；DDL迁移由root维护工具加载独立账号执行。

配置维护：

```bash
sudoedit /etc/laowai/config.json
sudo laowai-config check
sudo laowai-config apply
```

`apply`会重启后端。不要以本机.env覆盖生产配置。

## 媒体、HTTPS和网络

媒体地址为同一正式API域名下的 `/api/v1/question/media/HSK/_assets/...`。Nginx只允许音频和图片格式，拒绝目录列出、符号链接及非GET/HEAD方法，不公开题库JSON或.meta.json。94份音频全部验证字节范围请求返回206；153份文件均验证HTTPS访问及大小一致。

原运行依赖的Starlette 0.38.6不直接提供本次需要的Range响应，因此由现有Nginx提供静态媒体，未升级或安装依赖。旧第三方媒体代理规则保留在配置中，但新版题目使用本地媒体。

证书、自动续期、防火墙、SSH与Fail2ban配置沿用原部署。80转HTTPS，443提供服务；MySQL3306/33060与应用8000仅监听回环。生产开发身份关闭，公网API文档保持关闭。

微信的request/downloadFile合法域名仍为 `https://api.laowaiyidiantong.icu`，不带API路径。前端正式配置仍为该域名的 `/api/v1`，超时60000ms，正式AppID不变。

## 备份和回滚

- 清库前备份：`/var/backups/laowai/refresh-bank-v2-20261022-173312`，root专用，包含SQL、配置备份、旧源码和原题库归档、依赖快照。
- 清库前SQL：`laowai-20261022T094915Z.sql.gz`，配套SHA-256已验证；已恢复到隔离库并核对六项数据量和0006迁移版本，验证后仅删除隔离库。
- 旧代码和题库目录：`/opt/laowai/rollback/bank-v2-20261022-173312`，用于配套回滚；虚拟环境已移回当前代码的固定运行路径。
- 重建脚本另生成SQL备份：`/opt/laowai/csca-hks-exam-app/database/backups/before-bank-v2-20261022-174918.sql`。
- 原有每天03:20左右的数据库/配置备份和14天保留策略继续运行，备份位置仍为 `/var/backups/laowai`。

本次用户要求停止额外检查后，未执行新增日常媒体/源码备份的收尾脚本，也未把本次旧环境备份下载到本机。不要将上述服务器备份误称为已有异地副本。新版安装包仍保留在服务器 `/home/deploy` 与本机部署产物目录。

实际回滚需要在停止后端后，配套恢复旧代码、题库、SQL、生产配置和Nginx配置；不要只回滚代码或只执行Alembic降级。若新版已产生业务数据，应先另外保存当前数据。此处仅记录恢复位置，不自动执行回滚。

## 验收与操作记录

- 独立服务器目录53项后端测试通过；真实MySQL结构检查无漂移，完整性检查clean。
- 正式HTTPS通过24组HSK各等级和CSCA五科组卷，组卷时不提前下发解答。
- 自动判分、重复提交、长文本、自评、考试交卷时机、跨用户权限、正确率分母检查通过。
- 错题、收藏、重做、PDF文件签名、首页统计和历史接口通过。
- 全部153份媒体和94份音频Range检查通过，题库JSON无法公开读取。
- `/api/v1/ai/chat`实际返回qwen3.8-27b非空回复。
- 临时测试账号、业务记录及其题目统计贡献已清理；没有发布微信小程序或提交/推送Git。

服务器记录：

```text
/opt/laowai/deployment/refresh-bank-v2-20261022-173312.json
/opt/laowai/deployment/verification-bank-v2-20261022-173312.json
```

以上记录和本文件优先于旧版首次部署进度、state.json及final-status.json；后两个旧汇总文件未执行本轮额外收尾更新。

常用命令：

```bash
sudo systemctl status laowai-api mysql nginx --no-pager
sudo systemctl restart laowai-api
sudo journalctl -u laowai-api -n 100 --no-pager
sudo nginx -t
sudo laowai-manage current
sudo laowai-manage verify
sudo laowai-manage integrity
```

本次交付后不要重复执行清库。后续正常题目修订按稳定题号导入，执行写入前先保留备份。
