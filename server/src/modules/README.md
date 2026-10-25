# 后端业务模块

每个模块遵循统一结构：

```
module_name/
├── __init__.py      # 模块标记
├── router.py        # 路由定义（FastAPI APIRouter）
├── schemas.py       # Pydantic 请求/响应模型
├── models.py        # SQLAlchemy ORM 模型
└── service.py       # 业务逻辑（后续拆分）
```

## 模块列表

| 模块 | 路径 | 职责 |
|------|------|------|
| user | `modules/user/` | 微信登录、用户信息 CRUD、学习数据 |
| question | `modules/question/` | 题库查询、智能组卷、题目管理 |
| exam | `modules/exam/` | 答题提交、自动批改、成绩报告 |
| wrongbook | `modules/wrongbook/` | 错题收录、分类筛选、掌握标记、举一反三、导出 PDF |
| favorite | `modules/favorite/` | 个人收藏 |
| content | `modules/content/` | 内容维护、已发布版本公告及管理员发布/撤下 |
| ai | `modules/ai/` | 学习助手提示词、文字上下文与Qwen调用 |
| feedback | `modules/feedback/` | 私密反馈提交、幂等重试、管理员读取与处理状态 |

## API 路由规范

- 前缀：`/api/v1/{module}/`
- 聚合入口：`src/api/v1/router.py`
- 请求体/响应体：统一使用 `{ "code": 0, "message": "...", "data": ... }` 格式
- 认证：Header `Authorization: Bearer <token>`
- 反馈和内容管理必须持有有效JWT，管理操作额外核对CONTENT_ADMIN_OPENIDS，不使用匿名开发身份回退。见[1.5.1说明](../../../docs/release-1.5.1.md)。
