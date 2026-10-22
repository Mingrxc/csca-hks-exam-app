# 当前服务器配置与本次更新结果

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
