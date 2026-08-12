# 后端业务模块

每个模块遵循统一结构：

```
module_name/
├── __init__.py      # 导出 router
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

## API 路由规范

- 前缀：`/api/v1/{module}/`
- 聚合入口：`src/api/v1/router.py`
- 请求体/响应体：统一使用 `{ "code": 0, "message": "...", "data": ... }` 格式
- 认证：Header `Authorization: Bearer <token>`
