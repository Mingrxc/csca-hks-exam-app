# 组件目录

## 组件列表

| 组件 | 路径 | 说明 |
|------|------|------|
| CountdownBar | `components/CountdownBar/` | 考试倒计时组件，剩余 5 分钟黄色警告，1 分钟红色告警 |
| RingChart | `components/RingChart/` | Canvas 环形进度图，用于成绩页分数展示 |
| AnswerCard | `components/AnswerCard/` | 答题卡弹窗，显示已答/未答/当前/标记状态 |
| QuestionItem | `components/QuestionItem/` | 题目卡片，含题干、选项、解析区，支持收藏切换 |
| AppState | `components/AppState/` | 统一的加载、空内容和可重试错误状态 |
| ExamSelection | `components/ExamSelection/` | HSK / CSCA 独立勾选，支持 0、1、2 项；支持首页紧凑布局 |

## 使用方式

通过 `easycom` 自动注册，无需手动 import，直接使用 `<c-app-state>`、`<c-exam-selection>`、`<c-countdown-bar>`、`<c-question-item>`、`<c-answer-card>`、`<c-ring-chart>` 等标签。

## 设计规范

- 组件统一为单文件 `.vue`，放在各自独立文件夹中
- props 支持必要的数据注入，emit 对外暴露事件
- 颜色、字号、间距、圆角和阴影使用全局 `--app-*` 设计令牌

`AppState` 的 `compact` 属性用于卡片内的状态提示，保持与首页和学习指标一致的间距；加载失败时通过 `retry` 事件重新请求。

`ExamSelection` 接收 `selectedExams`，通过 `toggle` 事件返回被点击的考试类型。页面调用用户 store 更新和保存选择；组件本身不持有业务状态。
