# 老外1点通：CSCA & HSK 备考小程序

面向留学生的 CSCA 与 HSK 微信刷题小程序。当前仓库包含 uni-app 前端、FastAPI 后端、MySQL 数据模型与迁移、题库导入工具，以及数据库完整性检查脚本。为兼容既有数据，HSK 的内部接口标识仍为 `HKS`。

## 项目本体与维护方式

- 项目本体、代码仓库位于 `D:\Projects\Deng\csca-hks-exam-app`，前后端代码维护均以此仓库为准。
- 用户提出需求，Codex 根据需求完成代码维护、功能更新、相应检查及文档同步。
- 小程序已正式发布，后续工作以已上线产品的修复和迭代为基线，保持现有数据与接口兼容。
- 代码修改、Git 提交和正式部署分别按具体任务范围执行；修改代码不会自动提交、推送或上线。
- 本地运行环境和依赖使用现有配置；需要新增或安装时先沟通。

## 当前状态（2026-10-21）

- 发布状态：用户已确认小程序正式发布。
- 当前代码版本：`V1.4.1 完善分享功能`（`985c81be`）；上一版本为 `V1.4.0 正式发布`（`6c2f133a`）。此处记录本地仓库版本，未独立核对线上构建对应的提交。
- 前端：uni-app、Vue 3、Pinia、TypeScript，目标平台为微信小程序。
- 后端：FastAPI、SQLAlchemy 2、Alembic、PyMySQL。
- 数据库：MySQL 8.4 LTS，数据库名 `csca_hks_exam`。
- 正式 API 配置：`https://api.laowaiyidiantong.icu/api/v1`；本地生产配置的请求超时为 60 秒。
- 题库历史验证基线：1,876 题，其中 CSCA 265 题、HKS 1,611 题；不作为线上实时题数。
- 最新迁移源码：`0006_ownership_foreign_keys`；服务器实际迁移状态需在对应环境核验。
- 测试目录包含 40 个后端测试函数，历史验证记录为 40 项通过；文档更新不代表重新执行了测试或线上验收。
- Git 发布版本与各构建元数据分开记录：当前 `package.json`、`manifest.json` 和后端 API 的版本字段仍为 `1.0.0`。

## 已有功能

- 微信登录后按 OpenID 自动创建或复用用户，使用 JWT 访问个人学习数据。
- 首页、刷题页和个人页共享备考选择，支持 HSK、CSCA 单选、双选或“随便看看”；选择 0 或 2 项时，开始练习再选择本次考试。
- 随机练习、模拟考试、专项训练、难度递进，以及答题卡、计时、逐题反馈和成绩分析。
- 错题筛选、掌握标记、错题重做、PDF 导出、收藏和练习历史。
- 未完成答题的本地恢复，有效期七天；AI 会话历史和备考选择也保存在本地。
- AI 学习问答与错题上下文预填，后端对接 Qwen。
- 主要页面支持转发好友，统一分享至首页并使用固定品牌图片；首页支持朋友圈分享和静态预览。
- 首页资讯栏目仍为“筹备中”，真实内容接入按后续需求推进。

## 视觉基线

- 品牌常量和原生导航使用“老外1点通”；当前分享和朋友圈预览文案使用“老外一点通”。名称统一按后续明确需求处理；`DYH` 不是产品品牌。
- 核心定位是留学生的考试备考伙伴，核心闭环保持“刷题 → 组卷 → 答题 → 成绩反馈 → 错题本 → 复习”。
- 已落实用户审核的清新、温暖、简洁视觉：米白背景 `#F7F1E8`、浅色卡片 `#FFFAF3`、陶土主色 `#B86B4B`、深灰正文 `#2F2926`、浅绿辅助色 `#7E9A80`。
- 首页优先展示学习目标、继续答题、今日数据和复习工具；保留原生导航以及首页、刷题、AI问答、我的四个标签。
- 刷题、组卷、答题、成绩、错题、收藏、历史、AI 和个人页共用设计令牌、卡片和状态反馈，后续按具体需求迭代。

## 小程序品牌图标

项目内已有品牌图标：[client/src/static/brand/icon.png](client/src/static/brand/icon.png)。

- 运行图为 PNG 格式，尺寸 `384 × 384`，143,697 字节（约 140 KiB）。
- 高清原稿完整保留在 [design/brand/icon-original.png](design/brand/icon-original.png)，尺寸 `1254 × 1254`；该目录位于前端源码之外，不进入小程序构建包。
- 深蓝底、米白字样和金色圆点，底部为 `HSK · CSCA`。
- `client/src/constants/brand.ts` 的 `APP_ICON_PATH` 是统一图片地址；好友分享、朋友圈分享和朋友圈预览共同引用。
- 底部导航图标另位于 `client/src/static/tabbar/`，由 `client/src/pages.json` 引用。

这里记录仓库内资源及代码引用；微信后台实际使用的头像图片未在本次文档更新中核验。

## 目录结构

```text
client/                 uni-app + Vue 3 前端
server/                 FastAPI 后端、ORM、迁移和测试
database/               数据库说明与示例数据
scripts/                题库导入、完整性检查和开发辅助脚本
docs/                   设计与接口文档
design/                 品牌原稿及设计资源，不进入小程序运行包
CODEX_MEMORY.md         本地工作记忆，已取消 Git 跟踪并忽略
```

原始题库默认位于仓库同级的 `original_question_bank`，不纳入 Git。导入脚本也可通过 `--source` 指定其他位置。

前端分层、状态归属和答题恢复规则见 [docs/frontend-architecture.md](docs/frontend-architecture.md)；后端执行模型、事务、响应和数据库关系规则见 [docs/backend-architecture.md](docs/backend-architecture.md)；环境与请求策略见 [docs/network-environments.md](docs/network-environments.md)。

[docs/deployment-status.md](docs/deployment-status.md) 保存首次部署准备期间的历史记录，其中“尚未发布”等描述不代表当前状态。`database/README.md` 中的旧表结构说明也应以现有模型和 Alembic 迁移为准。

`CODEX_MEMORY.md` 通过仓库本地 `.git/info/exclude` 忽略，不会随正常提交上传；本地私有规则不写入共享 `.gitignore`。

## 已确认的本地环境

- Windows PowerShell
- Conda 环境：`deng`（Python 3.11+）
- MySQL Community Server 8.4 LTS（Windows 服务通常为 `MySQL84`）
- Node.js 18+ 与 npm
- 微信开发者工具（仅小程序调试需要）
- Redis 当前为可选项

本项目不要求使用 `.venv`。所有 Python 命令先执行：

```powershell
conda activate deng
```

## 首次配置

以下用于新开发环境。已有环境直接复用；依赖尚未安装时，由开发者在确认后手动执行：

```powershell
conda activate deng
python -m pip install -r .\server\requirements.txt

cd .\client
npm ci
cd ..
```

仓库不保存真实密码、令牌或本机配置。复制模板后只编辑本地文件：

```powershell
Copy-Item .\server\.env.example .\server\.env.local
Copy-Item .\client\.env.example .\client\.env.development.local
```

`server/.env.local` 至少需要填写：

```env
APP_ENV=development
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=deng
MYSQL_PASSWORD=填写本机密码
MYSQL_DATABASE=csca_hks_exam
JWT_SECRET_KEY=填写足够长的随机字符串
```

本地没有微信凭据时可显式使用 `AUTH_ALLOW_DEV_OPENID=true`。生产环境必须将其设为 `false`，并配置 `WX_APPID`、`WX_SECRET`、独立的 JWT 密钥和正式管理员白名单。当前源码仅设置 `APP_ENV=production` 不会自动关闭开发身份，也没有对应启动校验；此项属于后续代码维护关注点，不代表已经核验线上实际配置。

前端本地开发配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_API_TIMEOUT_MS=15000
```

不要把 `.env`、`.env.local`、`.env.*.local` 或任何真实密钥提交到仓库。

前端环境按以下规则配置，不在同一构建中混用多个地址：

| 场景 | 本地文件 | `VITE_API_BASE_URL` |
|---|---|---|
| 微信开发者工具 / H5 | `.env.development.local` | `http://127.0.0.1:8000/api/v1` |
| 同一局域网真机 | `.env.development.local` | `http://<电脑局域网IP>:8000/api/v1` |
| 临时 HTTPS 联调 | `.env.development.local` | 当前有效的临时 HTTPS 地址 |
| 正式发布 | `.env.production.local` 或部署环境变量 | 固定且已在微信后台登记的 HTTPS 地址 |

当前本地生产文件 `client/.env.production.local` 的非敏感配置为：

```env
VITE_API_BASE_URL=https://api.laowaiyidiantong.icu/api/v1
VITE_API_TIMEOUT_MS=60000
```

临时隧道地址失效后应直接替换，不保留为回退地址。生产模式加载请求模块时要求存在 `VITE_API_BASE_URL`；代码当前只校验地址以 `http://` 或 `https://` 开头，发布配置仍需明确使用正式 HTTPS 地址。

## 数据库初始化与迁移

以下初始化命令用于新建开发库或明确安排的环境初始化。已发布数据库的结构变更需在对应维护任务中备份、验证并实施。

先确认 MySQL 8.4 已运行，创建空数据库 `csca_hks_exam` 并为应用账号配置相应权限，再执行：

```powershell
conda activate deng
cd .\server
python -m alembic upgrade head
cd ..
```

当前 Alembic 最新迁移为 `0006_ownership_foreign_keys`，已经为用户所有权和题目引用建立外键。已有数据库先备份，再检查版本；不要在不清楚数据库来源时直接执行 `stamp`。

只读验证命令：

```powershell
conda activate deng
python .\scripts\check_database_integrity.py
cd .\server
python -m alembic current
python -m alembic check
cd ..
```

## 导入题库

以下命令默认使用当前环境的数据库连接；先确认目标环境。题库更新按需求执行，先 dry-run，再写入，最后核对数据库统计：

```powershell
conda activate deng
python .\scripts\import_questions.py
python .\scripts\import_questions.py --apply
python .\scripts\import_questions.py --verify-db
```

指定其他题库目录：

```powershell
python .\scripts\import_questions.py --source "D:\path\to\question_bank"
```

## 启动开发环境

终端一，启动后端：

```powershell
conda activate deng
cd .\server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

终端二，启动前端开发构建：

```powershell
cd .\client
npm run dev:mp-weixin
```

然后在微信开发者工具中导入 `client/dist/dev/mp-weixin`。本机开发不需要部署服务器；后端运行在本机即可。

## `request fail` 排查

本地小程序构建不会自动启动 FastAPI。每次重新打开开发环境，都需要保持“终端一”的 Uvicorn 进程运行；只启动微信开发者工具时，页面会显示加载失败且无法组卷，但这不代表数据库损坏。

1. 浏览器或微信开发者工具先访问 `http://127.0.0.1:8000/api/v1/health`，确认后端正在运行。
2. 检查 `client/.env.development.local`，删除已经失效的临时隧道地址并使用当前 API 地址。
3. 修改环境文件后重启前端构建，避免继续使用旧构建产物。
4. 微信开发者工具可在开发阶段关闭合法域名校验；手机不能把 `127.0.0.1` 当作电脑。
5. 真机联调可使用同一局域网内的电脑 IP（并检查防火墙），或临时 HTTPS 隧道。
6. 正式发布必须使用可长期访问、已配置到微信后台的 HTTPS API 域名，但不限定必须是传统云服务器。

请求层按环境只读取一个明确的 `VITE_API_BASE_URL`，不会在多个后端之间隐式切换。默认超时为 15 秒，当前本地生产配置覆盖为 60 秒；网络失败只会对 GET 请求重试一次，POST、PUT 和 DELETE 不自动做网络重试。401 响应最多触发一次重新登录和重发，最终错误会被统一转换并提示。每个请求都会携带 `X-Request-ID`，排错时可用客户端日志中的 ID 对应后端日志。

需要临时公网联调时可使用 `scripts/start_public_dev.ps1`。该脚本要求使用现有 Conda `deng` 环境，并要求 `cloudflared` 已由开发者手动安装；脚本不会下载任何工具。

## 测试与构建

后端：

```powershell
conda activate deng
cd .\server
python -m pytest -q
python -m alembic check
```

前端：

```powershell
cd .\client
npm run build:mp-weixin
```

`client/node_modules`、`client/dist`、Python 缓存、测试缓存和真实环境文件均为本地内容，不应被 Git 跟踪。前端依赖版本由 `package-lock.json` 固定。

### 分享图片与构建包体积

微信开发者工具截图中的主包 1.5MB、单个图片/音频 200KB 是本次处理的代码质量检查阈值。原始图标约 988 KiB，曾同时导致资源大小与主包体积检查未通过；现在运行图缩小为同一设计的 384 像素 PNG，高清原稿独立保存。

2026-10-21 本地 `build:mp-weixin` 构建成功，构建目录文件合计 723,831 字节（约 0.69 MiB），不存在超过 200,000 字节的图片或音频。分享返回值检查确认好友和朋友圈使用同一图标，高清原稿未进入构建包。这些结果对应本次本地构建；微信工具重新扫描和真机分享结果另行确认。

资源修改后重新构建，微信开发者工具导入 `client/dist/build/mp-weixin` 并重新扫描。正式用户需在新版本发布后才能使用更新后的分享资源。

## 后续代码维护关注点

以下来自当前源码阅读，按具体需求逐项处理，不是本次已完成的修复，也不直接代表线上故障：

1. 生产配置启动校验，以及开发身份、管理员白名单的安全默认值。
2. 头像上传后的持久化链路，当前资料更新直接保存选择头像事件提供的路径。
3. 备考选择、答题快照、AI 会话等本地缓存的用户归属与退出登录清理。
4. 并发答题统计的原子更新，以及 AI 接口的调用额度和限流。
5. 图片、音频题和 PDF 的真机展示与资源可访问性；分享和朋友圈预览的持续回归。
6. 品牌文字与版本元数据的一致性，以及历史文档的逐步更新。

每次涉及相关代码时运行适当的测试或构建，并按需要做真机回归。服务器配置、备份恢复与部署记录以对应运维任务的最新核验结果为准。
