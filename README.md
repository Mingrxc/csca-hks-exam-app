# 老外1点通：CSCA & HKS 备考小程序

面向留学生的 CSCA 与 HKS 微信刷题小程序。当前仓库包含 uni-app 前端、FastAPI 后端、MySQL 数据模型与迁移、题库导入工具，以及数据库完整性检查脚本。

## 当前基线

- 前端：uni-app、Vue 3、Pinia、TypeScript，目标平台为微信小程序。
- 后端：FastAPI、SQLAlchemy 2、Alembic、PyMySQL。
- 数据库：MySQL 8.4 LTS，数据库名 `csca_hks_exam`。
- 题库：1,876 题，其中 CSCA 265 题、HKS 1,611 题。
- 验证状态：后端测试 40 项通过；Alembic 位于最新版本；本地 MySQL 完整性检查与核心 API 冒烟检查通过。
- 生产微信登录、固定 HTTPS API、真机弱网和发布流程仍需后续验证。

## 产品与视觉方向

- 当前品牌名称暂定为“老外1点通”；`DYH` 不是产品品牌。
- 核心定位是留学生的考试备考伙伴，核心闭环保持“刷题 → 组卷 → 答题 → 成绩反馈 → 错题本 → 复习”。
- Phase 5 采用“暖色学术陪伴感”：温暖、克制、学术、年轻，不做传统题库蓝、低龄卡通或教务系统风格。
- 首页信息占比确定为学习仪表盘约 70%、留学资讯约 30%。学习目标、继续答题、今日数据和复习入口优先于内容资讯。
- 当前资讯和社团广告属于占位内容。视觉改造时移除虚构广告，以正式空状态预留真实资讯；后续再接入真实内容源。
- Phase 5 按 App Shell/导航/首页、组卷/答题、结果/错题闭环、AI/个人/内容的顺序逐段验收，不进行一次性全页面重画。

Phase 5 编码暂缓，先完成生产服务器与部署形态的选型讨论。

## 目录结构

```text
client/                 uni-app + Vue 3 前端
server/                 FastAPI 后端、ORM、迁移和测试
database/               数据库说明与示例数据
scripts/                题库导入、完整性检查和开发辅助脚本
docs/                   设计与接口文档
CODEX_MEMORY.md         项目现状、决策和重构路线
```

原始题库默认位于仓库同级的 `original_question_bank`，不纳入 Git。导入脚本也可通过 `--source` 指定其他位置。

前端分层、状态归属和答题恢复规则见 [docs/frontend-architecture.md](docs/frontend-architecture.md)；后端执行模型、事务、响应和数据库关系规则见 [docs/backend-architecture.md](docs/backend-architecture.md)；环境与请求策略见 [docs/network-environments.md](docs/network-environments.md)。

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

依赖尚未安装时，由开发者在确认环境后手动执行：

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

本地没有微信凭据时可使用 `AUTH_ALLOW_DEV_OPENID=true`。生产环境必须将其设为 `false`，并配置 `WX_APPID`、`WX_SECRET` 和安全的 JWT 密钥。

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

临时隧道地址失效后应直接替换，不保留为回退地址。生产构建缺少 `VITE_API_BASE_URL` 时会直接失败；正式构建前必须检查 `.env.production.local`，禁止将 `127.0.0.1` 当作线上地址发布。

## 数据库初始化与迁移

先确认 MySQL 8.4 已运行，并使用具备 `csca_hks_exam` 权限的本地用户。新数据库直接执行：

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

先 dry-run，再写入，最后核对数据库统计：

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

请求层按环境只读取一个明确的 `VITE_API_BASE_URL`，不会在多个后端之间隐式切换。默认超时为 15 秒；网络失败只会对 GET 请求重试一次，POST、PUT 和 DELETE 不自动重试，以避免重复写入。401 响应只触发一次重新登录，最终错误会被统一转换并提示。每个请求都会携带 `X-Request-ID`，排错时可用客户端日志中的 ID 对应后端日志。

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

## 发布前仍需完成

1. 使用正式微信凭据验证登录、token 续期和退出登录。
2. 使用固定 HTTPS API 在真机验证组卷、答题、音频/图片题和错题 PDF。
3. 完成密钥轮换、CORS、限流、日志、数据库备份恢复和回滚演练。
4. 单独决定是否清理 Git 历史中曾出现的旧凭据；未经明确确认不重写历史。
