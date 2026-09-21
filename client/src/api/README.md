# API 接口封装

## 边界

`client.ts` 是唯一的请求与下载传输层，负责环境地址、认证、超时、安全重试、统一错误和请求 ID。业务接口按领域放在 `src/features/*/api.ts`；`index.ts` 只保留兼容导出，新代码应直接依赖所属 feature。

## 领域模块

| 模块 | 说明 |
|------|------|
| `userApi` | 微信登录、用户信息、资料修改 |
| `questionApi` | 题库查询、智能组卷、历史试卷 |
| `examApi` | 提交答案、获取成绩报告 |
| `wrongBookApi` | 错题列表、详情、掌握标记、举一反三、导出 PDF |
| `favoriteApi` | 收藏题目列表、状态、切换收藏 |
| `contentApi` | 首页资讯列表、内容管理 CRUD |
| `aiApi` | 留学与备考 AI 问答 |

## 约束

- 页面不得直接调用 `uni.request`、`uni.downloadFile` 或拼接 API 根地址。
- GET 网络失败最多重试一次；写请求不自动重试。
- 认证恢复、错误提示和 `X-Request-ID` 由传输层统一处理。
