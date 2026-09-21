# 页面目录

| 模块 | 页面 | 说明 |
|------|------|------|
| 首页 | `index/index` | 老外1点通首页，留学咨询、社团广告、学习通知等资讯流 |
| 刷题 | `exam/index` | 组卷策略入口、历史试卷和学习数据（Tab 主页） |
| 刷题 | `exam/paper` | 组卷配置页（考试类型/题量/难度/知识点/模式/限时） |
| 刷题 | `exam/answer` | 答题页（复用 `QuestionItem` / `AnswerCard` / `CountdownBar`） |
| 刷题 | `exam/result` | 成绩报告页（分数、用时统计、错题列表） |
| 补充 | `favorite/index` | 收藏题目列表，可跳转到 AI 问答 |
| 补充 | `content-admin/index` | 首页内容管理（内容维护入口） |
| AI | `ai/index` | 留学与备考 AI 问答 |
| 个人 | `profile/index` | 个人中心（头像、昵称、统计、目标设置） |
| 补充 | `wrongbook/index` | 错题本列表 |
| 补充 | `wrongbook/detail` | 错题详情 |
| 补充 | `wrongbook/redo` | 错题重做页 |

## 页面路由

由 `pages.json` 统一管理，TabBar 包含首页、刷题、AI问答和个人信息四个入口。

## 共享层

- `src/constants/`：题型、难度、组卷策略等共享配置
- `src/features/`：领域 API 和页面级服务端状态
- `src/shared/`：领域无关 composable 与 UI 工具
- `src/types/`：前端共享类型
