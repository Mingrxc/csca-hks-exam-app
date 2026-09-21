# Pinia 状态管理

## Store 列表

| 文件 | Store | 说明 |
|------|-------|------|
| `user.ts` | `useUserStore` | 用户状态：登录 token、用户信息、累计刷题/正确率/打卡/收藏数 |
| `exam.ts` | `useExamStore` | 跨页考试状态：组卷、答案、提交状态、错因、计时与本机进度恢复 |

## 使用规范

- Store 只承载跨页面或需要生命周期持久化的状态。
- 页面级服务端数据由 `features/*` composable 管理，不为每个列表创建全局 Store。
- 页面通过 Store action 修改持久状态，不直接写本地缓存。
- API 调用通过领域 feature 发起，Store 不承担通用请求状态。
