# 留学考霸 - CSCA & HKS 备考刷题

面向备考 CSCA 与 HKS 的微信小程序项目，目标是把“刷题 - 组卷 - 错题本 - 复习 - 数据反馈”串成一个完整学习闭环。

## 技术栈（按实现顺序）

1. `uni-app + Vue 3`：小程序页面与交互骨架
2. `Pinia`：客户端状态管理
3. `TypeScript`：前端共享类型、常量和 API 数据契约
4. `FastAPI`：后端应用入口与 API 组合
5. `SQLAlchemy`：用户、题库、试卷、答题、错题本数据模型
6. `MySQL`：核心业务数据存储
7. `Redis`：会话、缓存、后续题库加速预留
8. `JWT`：登录态与接口鉴权
9. `OSS / 微信云存储`：图片、音频、PDF 等资源预留

## 当前结构

- `client/src/constants/`：题型、难度、组卷策略等共享配置
- `client/src/api/`：请求封装、自动登录和前后端数据适配
- `client/src/types/`：前后端共享的数据类型
- `client/src/components/`：答题卡、题目卡片、倒计时、环形图
- `client/src/pages/`：首页、刷题、错题本、个人中心
- `server/src/app.py`：FastAPI 应用工厂
- `server/src/api/v1/`：聚合路由入口
- `server/src/modules/`：用户、题库、考试、错题本模块
- `database/`：建表脚本与种子数据

## 现在做到哪一步

- 首页、组卷、答题、成绩、错题本、错题重做和个人中心已接入真实 API 数据
- 前端的重复数据与标签映射已经收敛到共享类型、常量和接口适配层
- 后端已经整理出应用工厂和统一路由入口
- 后端已补齐刷题闭环接口：微信登录、首页摘要、智能组卷、答题提交、成绩与逐题解析、历史试卷、错题本、举一反三和错题重做
- 数据库表结构和 ORM 模型已经定义好
- 前端已接入“组卷 → 答题 → 成绩报告 → 全部解析”以及“错题列表 → 错题详情 → 掌握标记 → 错题重做”主链路
- 微信 `code2session`、JWT 自动续登、个人考试目标和错题 PDF 导出调用链已经实现
- 后端自动化测试当前为 31 项通过，包含中文错题 PDF 生成测试

## 本地运行

```bash
cd client
npm install
npm run dev:mp-weixin
```

前端 API 地址通过 `client/.env.development` 配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

真机调试时需要改成本机局域网 IP，例如：

```env
VITE_API_BASE_URL=http://192.168.1.7:8000/api/v1
```

```bash
cd server
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.example .env
.venv/Scripts/python -m uvicorn main:app --reload
```

`server/.env` 至少需要配置 MySQL。真实微信登录还需要填写 `WX_APPID`、`WX_SECRET`，并设置：

```env
AUTH_ALLOW_DEV_OPENID=false
JWT_SECRET_KEY=请替换为足够长的随机密钥
```

本地开发未配置微信参数时，可保留 `AUTH_ALLOW_DEV_OPENID=true` 使用固定开发账号。

## 数据初始化

1. 启动 MySQL，创建空的 `csca_hks_exam` 数据库。
2. 在 `server` 目录运行 `.venv/Scripts/python -m alembic upgrade head`。
3. 可导入 `database/seeds/sample_questions.sql` 做最小验证。
4. 完整题库位于工作区同级 `original_question_bank` 时，运行：

```bash
server/.venv/Scripts/python scripts/import_questions.py --apply
server/.venv/Scripts/python scripts/import_questions.py --verify-db
```

## 下一步

- 恢复本机 MySQL 服务后，应用 Alembic 迁移并审计外键前的孤儿记录
- 在微信开发者工具中验证 `code2session`、过期 token 重试、PDF 预览与真机网络配置
- 为首页和历史接口补充分页、限流与发布环境监控

## 验证

```powershell
cd server
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m alembic upgrade head --sql

cd ../client
npm.cmd run build:mp-weixin
```
