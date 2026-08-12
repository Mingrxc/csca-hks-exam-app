# 留学考霸 - CSCA & HKS 备考刷题

面向备考 CSCA 与 HKS 的微信小程序项目，目标是把“刷题 - 组卷 - 错题本 - 复习 - 数据反馈”串成一个完整学习闭环。

## 技术栈（按实现顺序）

1. `uni-app + Vue 3`：小程序页面与交互骨架
2. `Pinia`：客户端状态管理
3. `TypeScript`：前端共享类型、常量和 mock 数据
4. `FastAPI`：后端应用入口与 API 组合
5. `SQLAlchemy`：用户、题库、试卷、答题、错题本数据模型
6. `MySQL`：核心业务数据存储
7. `Redis`：会话、缓存、后续题库加速预留
8. `JWT`：登录态与接口鉴权
9. `OSS / 微信云存储`：图片、音频、PDF 等资源预留

## 当前结构

- `client/src/constants/`：题型、难度、组卷策略等共享配置
- `client/src/mock/`：首页、刷题、错题本、个人中心的示例数据
- `client/src/types/`：前后端共享的数据类型
- `client/src/components/`：答题卡、题目卡片、倒计时、环形图
- `client/src/pages/`：首页、刷题、错题本、个人中心
- `server/src/app.py`：FastAPI 应用工厂
- `server/src/api/v1/`：聚合路由入口
- `server/src/modules/`：用户、题库、考试、错题本模块
- `database/`：建表脚本与种子数据

## 现在做到哪一步

- 前端页面骨架已经搭好，首页、组卷页、答题页、结果页、错题本和个人中心都已具备
- 前端的重复数据与标签映射已经收敛到共享类型、常量和接口适配层
- 后端已经整理出应用工厂和统一路由入口
- 后端已补齐最小刷题闭环接口：开发态登录、智能组卷、题目详情、答题提交、成绩汇总、错题本列表/详情/标记、举一反三
- 数据库表结构和 ORM 模型已经定义好
- 前端已接入“组卷 → 答题 → 成绩报告”以及“错题列表 → 错题详情 → 掌握标记 → 举一反三”主链路
- 微信真实登录、错题重做专用组卷、PDF 导出和本地运行验收尚未完成

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
pip install -r requirements.txt
uvicorn main:app --reload
```

## 下一步

- 启动 MySQL 服务，创建数据库并导入 `database/schema.sql` 与 `database/seeds/sample_questions.sql`
- 安装前后端依赖后启动 API 与微信小程序开发服务，完成真机或开发者工具联调
- 实现微信 `code2session` 真实登录、错题重做专用试卷和 PDF 导出
