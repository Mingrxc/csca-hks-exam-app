# 老外一点通

面向留学生的 HSK 与 CSCA 微信备考小程序。前端采用 uni-app、Vue 3 和 Pinia，后端采用 FastAPI、SQLAlchemy 和 MySQL。界面写 HSK，数据库和接口继续使用已有的 `HKS` 标识。

## 从哪里找代码

- [前端](client/README.md)由 `client/src/main.js` 创建应用，`App.vue` 恢复会话，`pages.json` 注册页面和组件。页面经领域模块和共享传输层调用 API。
- [后端](server/README.md)从 `server/main.py` 启动，`server/src/api/v1/router.py` 聚合路由。业务模块校验请求、处理事务并通过 ORM 访问 MySQL。
- 改组卷或判分，从[刷题页面](client/src/pages/exam/README.md)和后端[题库](server/src/modules/question/README.md)、[作答](server/src/modules/exam/README.md)入手。题库源文件在工作区同级的 `original_question_bank/`，导入和媒体规则见[题库契约](docs/question-bank-import-contract.md)。
- 改登录、头像或签到，先看[登录页](client/src/pages/login/README.md)、[个人中心](client/src/pages/profile/README.md)、[首页](client/src/pages/index/README.md)及[用户模块](server/src/modules/user/README.md)。
- 改管理员权限、反馈和公告，先看[管理页面](client/src/pages/admin/README.md)、[内容管理](client/src/pages/content-admin/README.md)及后端[管理员模块](server/src/modules/admin/README.md)。
- [数据库](database/README.md)保存结构参考，[脚本](scripts/README.md)负责导入、检查和打包，[设计](design/README.md)保留品牌资源，[文档](docs/README.md)索引架构和发布记录。

## 开发环境

开发需要 Node.js、npm、Python 和 MySQL 8.4。在 `client/` 运行 `npm ci` 安装前端依赖，从仓库根目录运行 `python -m pip install -r server/requirements.txt` 安装后端依赖。

在仓库根目录准备首次配置，已有文件时按模板逐项核对。

```powershell
if (!(Test-Path server/.env.local)) {
    Copy-Item .env.example server/.env.local
}
if (!(Test-Path client/.env.development.local)) {
    Copy-Item client/.env.example client/.env.development.local
}
```

### 后端

从 `server/` 运行。Pydantic 先读工作目录中的 `.env`，再读 `.env.local`，进程环境变量优先级最高。服务和 Alembic 使用同一份数据库配置。

| 变量 | 用途和填写要求 |
| --- | --- |
| `APP_ENV`、`CORS_ORIGINS` | 开发环境用 `development`，生产环境用 `production`。需要限制 API 跨域来源时填逗号分隔的地址。模板的 `*` 供开发联调。 |
| `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE` | 使用目标 MySQL 的地址、端口、账号、密码和库名。首次配置时填写能访问开发数据库的账号和密码。 |
| `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRE_HOURS` | 签发登录令牌。`JWT_SECRET_KEY` 填独立随机密钥，算法和有效期可沿用模板。 |
| `AUTH_ALLOW_DEV_OPENID`、`DEV_OPENID` | 可选，分别设置是否允许开发登录回退和回退身份。生产环境将 `AUTH_ALLOW_DEV_OPENID` 设为 `false`。 |
| `WX_APPID`、`WX_SECRET` | 真实微信登录必填。使用开发模拟登录时可留空。 |
| `QUESTION_BANK_ROOT`、`QUESTION_MEDIA_BASE_URL` | 可选的题库根目录和媒体地址前缀。默认读取仓库同级的 `original_question_bank/`，媒体前缀为空时使用 API 媒体路由。 |
| `USER_AVATAR_ROOT` | 可选的持久化头像目录，默认使用仓库同级的 `user_uploads/avatars/`。 |
| `QWEN_API_KEY`、`QWEN_BASE_URL`、`QWEN_MODEL`、`QWEN_TEMPERATURE`、`QWEN_MAX_TOKENS`、`QWEN_TIMEOUT_SECONDS` | 保留给 AI 问答。当前接口未挂载，接回后调用模型需要对应密钥。 |

配置仍兼容旧环境文件里的 `CONTENT_ADMIN_OPENIDS`、`REDIS_*` 和 `OSS_*`。当前业务使用数据库角色授权、MySQL 存储和持久化头像目录。

### 前端

Vite 从 `client/` 加载对应模式的环境文件。开发用 `client/.env.development.local`，正式构建从 [前端模板](client/.env.example) 另建 `client/.env.production.local`。`VITE_API_BASE_URL` 是包含 `/api/v1` 的 API 根地址，正式构建必填。`VITE_API_TIMEOUT_MS` 可选，默认 15000 毫秒。环境文件修改后重新启动编译。真机联调地址及微信域名配置见[网络说明](docs/network-environments.md)。

## 迁移、启动与验证

首次开发先在 MySQL 创建空库，再核对 `server/.env.local`。已有库先确认目标、备份数据并读取当前修订，从 `server/` 执行以下命令。迁移脚本在 [server/alembic/versions/](server/alembic/versions/README.md)，当前头为 `0014_release_1_5_5`。

```powershell
python -m alembic current
python -m alembic upgrade head
python -m alembic current
python -m alembic check
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

打开 `http://127.0.0.1:8000/api/v1/health` 核对服务。健康接口只检查 API，`alembic current` 和 `alembic check` 分别确认数据库连接及结构。题库导入先按[脚本说明](scripts/README.md)跑校验；空库成功迁移并导入后可在前端验证组卷。

在 `client/` 运行 `npm run dev:mp-weixin`，开发者工具导入 `client/dist/dev/mp-weixin`，查看首页并确认请求发往所配置的后端。

- 前端全量测试在 `client/` 运行 `node --test tests/*.test.cjs`。发布前运行 `npm run build:mp-weixin`，产物在 `client/dist/build/mp-weixin`。
- 后端测试在 `server/` 运行 `python -m pytest -q`，数据库用例使用隔离 SQLite，题库契约测试读取同级原始题库。可用 `python -m alembic upgrade 0006_ownership_foreign_keys:head --sql` 检查增量 SQL。`0006` 本身需要查询孤立记录，完整迁移链使用在线模式。

## 维护约定

每层自有目录的 `README.md` 说明本层入口与维护边界。源码注释只保留设计原因、业务约束和边界条件，保留工具需要的指令及公开契约。移除页面、组件和资源前，核对注册表、导航、模板、资源路径及构建配置。

环境文件、数据库备份、依赖、构建产物及 `CODEX_MEMORY.md` 由根目录 `.gitignore` 管理。代码变化同步相关 README 和仓库记忆。发布和迁移所需的说明与脱敏模板随代码维护。
