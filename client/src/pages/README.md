# 页面目录

| 模块 | 页面 | 说明 |
|------|------|------|
| 首页 | `index/index` | 考试倒计时、今日数据卡片、四种组卷策略快捷入口、错题提醒 |
| 刷题 | `exam/index` | 组卷策略选择页（Tab 主页） |
| 刷题 | `exam/paper` | 组卷配置页（考试类型/题量/难度/知识点/模式/限时） |
| 刷题 | `exam/answer` | 答题页（复用 `QuestionItem` / `AnswerCard` / `CountdownBar`） |
| 刷题 | `exam/result` | 成绩报告页（分数、用时统计、错题列表） |
| 错题本 | `wrongbook/index` | 错题列表（Tab 主页），支持按考试类型/知识点/错误次数筛选 |
| 错题本 | `wrongbook/detail` | 错题详情（正确答案+解析+易混选项辨析+举一反三推荐） |
| 错题本 | `wrongbook/redo` | 错题重做页（复用题目组件，只保留错题） |
| 我的 | `profile/index` | 个人中心（用户信息、学习数据、成就、设置） |

## 页面路由

由 `pages.json` 统一管理，TabBar 包含首页/刷题/错题本/我的四个入口。

## 共享层

- `src/constants/`：题型、难度、组卷策略等共享配置
- `src/mock/`：页面示例数据
- `src/types/`：前端共享类型
