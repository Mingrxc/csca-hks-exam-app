# API 接口封装

## 模块

| 模块 | 说明 |
|------|------|
| `userApi` | 微信登录、用户信息、资料修改 |
| `questionApi` | 题库查询、智能组卷、历史试卷 |
| `examApi` | 提交答案、获取成绩报告 |
| `wrongBookApi` | 错题列表、详情、掌握标记、举一反三、导出 PDF |
| `favoriteApi` | 收藏题目列表、状态、切换收藏 |
| `contentApi` | 首页资讯列表、内容管理 CRUD |
| `aiApi` | 留学与备考 AI 问答 |

## 配置

- 基础 URL：`/api/v1`，通过拦截器自动拼接
- 认证：Bearer Token，从 uni.storage 读取
- 错误处理：401 自动清 token，其他弹出 toast 提示
