# 后端共享基础

`auth.py` 签发和解析 JWT，`deps.py` 为业务路由校验账号及数据库管理员角色。`response.py`、`exceptions.py` 和 `request_context.py` 统一 JSON 响应、错误与请求 ID。`time.py` 按 UTC 存储时间，按北京时间划分学习日。
