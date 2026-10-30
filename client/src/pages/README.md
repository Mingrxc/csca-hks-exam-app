# 页面目录

| 模块 | 页面 | 说明 |
|------|------|------|
| 首页 | `index/index` | 学习目标、继续练习、统计与复习入口；资讯仍为筹备状态 |
| 刷题 | `exam/index` | 组卷策略入口、历史试卷和学习数据（Tab 主页） |
| 刷题 | `exam/paper` | 组卷配置页（考试类型/题量/难度/知识点/模式/限时） |
| 刷题 | `exam/answer` | 答题页（复用 `QuestionItem` / `AnswerCard` / `CountdownBar`） |
| 刷题 | `exam/result` | 成绩报告页（分数、用时统计、错题列表） |
| 补充 | `favorite/index` | 收藏题目列表与取消收藏 |
| 补充 | `content-admin/index` | 管理员维护内容和版本公告，支持草稿与发布 |
| 个人 | `profile/index` | 个人中心（头像、昵称、统计、目标设置） |
| 个人 | `feedback/index` | 私密文字反馈，用户隔离草稿、失败重试与回执 |
| 个人 | `about/index` | 品牌图标、名称、实际版本（当前1.5.3）、介绍、更新公告与隐私保护指引 |
| 个人 | `about/announcements` | 已发布更新公告的分页列表 |
| 个人 | `about/announcement` | 纯文本公告详情 |
| 补充 | `wrongbook/index` | 错题本列表 |
| 补充 | `wrongbook/detail` | 错题详情 |
| 补充 | `wrongbook/redo` | 错题重做页 |

## 页面路由

由 `pages.json` 统一管理，TabBar 包含首页、刷题、我的三个入口；中英文标签随语言切换同步更新。1.5.3已移除AI页面及所有前端入口。

## 共享层

- `src/constants/`：题型、难度、组卷策略等共享配置
- `src/features/`：领域 API 和页面级服务端状态
- `src/shared/`：领域无关 composable 与 UI 工具
- `src/types/`：前端共享类型
