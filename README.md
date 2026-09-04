# DYH：CSCA & HKS 备考小程序

当前项目名使用 `DYH` 占位。它是一个面向 CSCA 与 HKS 备考的微信小程序，包含首页资讯、刷题、AI 问答和个人信息四个导航入口，并保留错题本、收藏题目、历史试卷和在线内容管理。

## 当前状态

- 前端已接入真实 API：首页资讯、组卷、答题、成绩报告、历史试卷、错题本、收藏题目、AI 问答和个人中心。
- 后端使用 FastAPI、SQLAlchemy、Alembic 和 MySQL；已完成微信登录、JWT 自动续登、内容管理、收藏、AI 代理和错题 PDF 导出等接口。
- 数据库已完成 Alembic 初始迁移和答题记录唯一约束迁移；`scripts/check_database_integrity.py` 可执行只读完整性检查。
- 已在本地 MySQL 和微信开发者工具完成主要流程回归。真实生产微信登录、真机网络配置和发布环境验证仍需有效的微信凭据及服务器地址。
- 最近一次后端验证为 32 项通过；前端微信小程序生产构建成功。

## 目录

```text
client/                 uni-app + Vue 3 前端
server/                 FastAPI 后端、ORM、迁移和测试
database/               schema、迁移说明和示例种子
scripts/                题库导入与数据库完整性检查
docs/                   设计与接口文档
```

完整题库源文件默认位于项目同级的 `original_question_bank` 目录。该目录是外部数据源，不属于本仓库；导入脚本也支持通过参数指定其他题库目录。

## 环境要求

- Windows PowerShell（下文命令按 Windows 路径书写）
- Node.js 18+ 和 npm
- Python 3.11+
- MySQL 8（数据库名默认为 `csca_hks_exam`）
- Redis 为可选依赖，当前主要用于后续缓存扩展
- 微信开发者工具（仅调试小程序时需要）

## 首次安装

```powershell
cd client
npm install

cd ..\server
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

不要提交 `.env`、密钥或本地依赖目录。仓库中的 `.env.example` 是可提交的配置模板。

## 配置

后端配置写入 `server/.env`，至少确认以下项目：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=请填写本机密码
MYSQL_DATABASE=csca_hks_exam
JWT_SECRET_KEY=请替换为足够长的随机密钥
```

本地没有微信凭据时，可保留 `AUTH_ALLOW_DEV_OPENID=true` 进行开发调试；生产环境必须设置为 `false`，并填写 `WX_APPID` 与 `WX_SECRET`。

前端 API 地址写入 `client/.env.local` 或 `client/.env.development`，例如：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_API_FALLBACK_URL=http://127.0.0.1:8000/api/v1
```

小程序请求会优先使用 `VITE_API_BASE_URL`，网络失败时回退到 `VITE_API_FALLBACK_URL`。因此电脑模拟器可以回退到本机地址，真机则使用公网 HTTPS 地址。

### 真机调试

微信官方网络文档要求小程序只能和指定域名通信，`localhost` 和本机 IP 都不适合手机真机访问；局域网 IP 只适合开发阶段联调，正式发布要换成已配置的 HTTPS 域名。见官方文档：[网络](https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html)

本地真机联调建议使用项目根目录的一键脚本：

1. 在项目根目录执行 `powershell -ExecutionPolicy Bypass -File .\scripts\start_public_dev.ps1`，也可以双击 `scripts/start_public_dev.cmd`。
2. 脚本会启动后端，创建 Cloudflare HTTPS Quick Tunnel，自动更新前端地址并构建。
3. 在微信开发者工具中重新编译 `client/dist/build/mp-weixin`。
4. 在微信开发者工具里开启「开发环境不校验请求域名、TLS 版本及 HTTPS 证书」。

脚本会先检查 MySQL80。首次运行如果服务权限不足，会弹出管理员授权，并将 MySQL80 设置为开机自动启动；如果授权被取消，需要手动以管理员身份执行 `Set-Service -Name MySQL80 -StartupType Automatic; Start-Service -Name MySQL80`。

Quick Tunnel 每次启动都会生成新的临时域名，适合开发联调但不能保证跨重启地址不变。需要固定地址时，先在 Cloudflare 账户中创建 Named Tunnel 和一个 Cloudflare DNS 域名，然后执行：

```powershell
$env:CLOUDFLARE_TUNNEL_NAME = 'your-tunnel-name'
$env:CLOUDFLARE_PUBLIC_URL = 'https://api.example.com'
powershell -ExecutionPolicy Bypass -File .\scripts\start_public_dev.ps1 -Mode named
```

Named Tunnel 的固定 HTTPS 地址不会因电脑重启改变；电脑端仍会在公网地址不可用时回退到 `127.0.0.1`。

如果 Cloudflare 控制台提供的是 Tunnel Token，推荐使用 Token 模式：

```powershell
$env:CLOUDFLARE_TUNNEL_TOKEN = 'your-tunnel-token'
$env:CLOUDFLARE_PUBLIC_URL = 'https://api.example.com'
powershell -ExecutionPolicy Bypass -File .\scripts\start_public_dev.ps1 -Mode token
```

Token 只保存在当前终端环境中，不写入仓库；固定域名由 Cloudflare 控制台配置，不能使用 `trycloudflare.com` 临时域名代替。

页面路由里的 `/pages/index/index` 这类写法是对的，这是小程序内部绝对路由，不是问题根源。真正要避免的是把后端接口写成 `127.0.0.1` 这种本机地址。

## 数据库初始化

先启动 MySQL 并创建空数据库 `csca_hks_exam`，再在 `server` 目录执行：

```powershell
cd server
.venv\Scripts\python.exe -m alembic upgrade head
cd ..
```

如果数据库已经由旧版 `database/schema.sql` 创建，先备份，再标记初始版本并升级：

```powershell
cd server
.venv\Scripts\python.exe -m alembic stamp 0001_initial_schema
.venv\Scripts\python.exe -m alembic upgrade head
cd ..
```

验证数据库状态（只读）：

```powershell
server\.venv\Scripts\python.exe scripts\check_database_integrity.py
```

## 导入题库

默认先执行 dry-run，确认题库文件和数量；确认无误后再写入数据库：

```powershell
server\.venv\Scripts\python.exe scripts\import_questions.py
server\.venv\Scripts\python.exe scripts\import_questions.py --apply
server\.venv\Scripts\python.exe scripts\import_questions.py --verify-db
```

题库不在默认的项目同级目录时，使用 `--source <目录>` 指定来源。

## 启动开发环境

后端：

```powershell
cd server
.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

前端（另开终端）：

```powershell
cd client
npm run dev:mp-weixin
```

在微信开发者工具中导入 `client/dist/build/mp-weixin`（构建后生成）或按 uni-app 开发模式运行，并使用实际 API 地址进行联调。

如果你要把整个工程交给别人审查，至少要同时带上：

- `client/dist/build/mp-weixin`
- 可访问的后端地址
- `server/.env` 或等价的环境变量配置
- 微信小程序 `appid`
- 不要把你本机真实的 `server/.env.local` 密钥文件一起发出去

对方在微信开发者工具里应当直接导入 `client/dist/build/mp-weixin`，这才是可审查的小程序包。只打包仓库根目录还不够，后端接口也需要能连通，AI 和数据功能才会完整。

## 验证与构建

```powershell
cd server
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m alembic check
cd ..\client
npm run build:mp-weixin
```

`client/node_modules`、`client/dist`、Python 虚拟环境和测试缓存都是可再生中间产物，已加入 `.gitignore`，不会随源码提交。删除后重新执行安装和构建命令即可恢复。

## 仍需完成的发布验证

1. 使用正式 `WX_APPID`/`WX_SECRET` 在真机验证登录、过期 token 重试和退出登录。
2. 使用可从手机访问的 HTTPS API 地址验证组卷、答题和错题 PDF 预览。
3. 在发布环境完成 CORS、JWT 密钥、数据库备份、日志和限流配置审查。
