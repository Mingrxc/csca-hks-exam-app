# Pinia 状态管理

## Store 列表

| 文件 | Store | 说明 |
|------|-------|------|
| `user.ts` | `useUserStore` | 用户状态：登录 token、用户信息、累计刷题/正确率/打卡/收藏数 |
| `exam.ts` | `useExamStore` | 考试状态：组卷配置、题目列表、答题记录、计时、得分计算 |

## 使用规范

- 所有与后端 API 交互的状态变更都在 store 中完成
- 页面组件只读 state，通过 store 的 action 修改数据
- 不在页面内直接调用 API
