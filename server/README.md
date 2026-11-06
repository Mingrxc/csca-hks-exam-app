# FastAPI 服务

`main.py` 是 Uvicorn 入口，`requirements.txt` 声明运行和测试依赖。`alembic.ini` 定位 [数据库迁移](alembic/README.md)，`pytest.ini` 设置 [测试](tests/README.md)的隔离产物目录。

在本层启动服务或执行 Alembic。环境文件取自当前工作目录，填写方法和验证命令见[根目录说明](../README.md)。应用内部入口见 [src](src/README.md)。
