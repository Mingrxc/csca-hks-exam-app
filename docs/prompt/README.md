# 留学考霸 — CSCA & HKS 备考刷题

一款面向备考 CSCA 与 HKS 的留学生的**微信小程序**，围绕刷题、错题本、举一反三打造高效的学习闭环。

## 核心功能

- **智能组卷** — 随机组卷、知识点专项、难度递进、真题比例模拟，四种策略灵活出卷
- **双模式答题** — 考试模式（限时沉浸） / 练习模式（即时反馈），支持单选、多选、判断、填空
- **错题本** — 自动收录错题，记录错误次数与错因，支持分类筛选、重做、掌握标记、导出 PDF
- **举一反三** — 基于知识点 + 难度 + 历史数据的协同过滤，错题页推荐相似题目
- **成绩报告** — 分数环形图、知识点雷达图、用时统计

## 技术栈

| 层级 | 方案 |
|------|------|
| 小程序框架 | uni-app (Vue3) + Pinia |
| UI 组件 | uView Plus / uni-ui |
| 后端 | Python FastAPI 或 Node.js + Express |
| 数据库 | MySQL（主库） + Redis（缓存/排行） |
| ORM | Prisma (Node.js) / SQLAlchemy (Python) |
| 存储 | 阿里云 OSS / 微信云存储 |

## 项目结构

```
exam-miniapp/
├── miniapp/                 # uni-app 前端
│   ├── pages/
│   │   ├── index/           # 首页
│   │   ├── exam/            # 刷题模块
│   │   ├── wrongbook/       # 错题本
│   │   ├── forum/           # 论坛（可选）
│   │   ├── friend/          # 好友（可选）
│   │   ├── team/            # 组队（可选）
│   │   └── profile/         # 个人中心
│   ├── components/          # 公共组件
│   ├── stores/              # Pinia 状态管理
│   ├── api/                 # 接口封装
│   └── utils/               # 工具函数
├── server/                  # 后端服务
│   └── src/modules/
│       ├── user/            # 用户模块
│       ├── question/        # 题库模块
│       ├── exam/            # 考试模块
│       ├── wrongbook/       # 错题本模块
│       └── ...
└── docs/                    # 项目文档
```

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url>
cd exam-miniapp

# 2. 安装前端依赖
cd miniapp
npm install

# 3. 启动微信小程序开发
npm run dev:mp-weixin
# 打开微信开发者工具，导入 miniapp/dist/dev/mp-weixin 目录

# 4. 安装后端依赖
cd ../server
pip install -r requirements.txt

# 5. 启动后端
uvicorn main:app --reload
```

## 开发阶段

| 阶段 | 内容 | 周期 |
|------|------|------|
| Phase 1 MVP | 刷题 + 错题本 + 举一反三 | 4-6 周 |
| Phase 2 增强 | 错题导出、错因统计、听力题、推送 | 3-4 周 |
| Phase 3 社交 | 论坛、好友、组队打卡、勋章 | 4-6 周 |
| Phase 4 AI | AI 错题讲解、智能组卷、冲刺计划 | 后续 |

## 设计规范

- 主色调：蓝紫（学术感） + 暖橙（激励感）
- 刷题页极简，仅保留题干与选项
- 即时反馈，正向激励文案
- 支持离线答题，联网后同步

## License

MIT
