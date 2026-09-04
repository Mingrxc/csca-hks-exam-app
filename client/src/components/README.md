# 组件目录

## 组件列表

| 组件 | 路径 | 说明 |
|------|------|------|
| CountdownBar | `components/CountdownBar/` | 考试倒计时组件，剩余 5 分钟黄色警告，1 分钟红色告警 |
| RingChart | `components/RingChart/` | Canvas 环形进度图，用于成绩页分数展示 |
| AnswerCard | `components/AnswerCard/` | 答题卡弹窗，显示已答/未答/当前/标记状态 |
| QuestionItem | `components/QuestionItem/` | 题目卡片，含题干、选项、解析区，支持收藏切换 |

## 使用方式

通过 `easycom` 自动注册，无需手动 import，直接使用 `<c-countdown-bar>`、`<c-question-item>`、`<c-answer-card>`、`<c-ring-chart>` 等标签。

## 设计规范

- 组件统一为单文件 `.vue`，放在各自独立文件夹中
- props 支持必要的数据注入，emit 对外暴露事件
- 颜色和间距沿用全局 CSS 变量（`--color-primary` 等）
