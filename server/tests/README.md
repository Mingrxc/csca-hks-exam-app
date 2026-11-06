# 后端回归测试

`conftest.py` 提供隔离 SQLite 和 FastAPI 测试客户端。管理和登录用例验证权限，题库和考试用例验证组卷、答题与自评，公告用例还覆盖历史迁移。

在 `server/` 运行 `python -m pytest -q`。`test_bank_v2.py` 读取仓库同级的 `original_question_bank/`，逐题对照导入范围，并验证暂缓导入的口语及口译记录。
