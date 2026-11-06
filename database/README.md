# 数据库

`schema.sql` 是 `scripts/export_schema.py` 从当前 ORM 导出的结构参考。初始化和升级使用 Alembic，入口是 [env.py](../server/alembic/env.py)。业务模型在各后端模块。原题从工作区同级的 `original_question_bank/` 通过导入脚本进入 MySQL。

升级已有库先核对目标并备份，再从 `server/` 运行 `python -m alembic current` 查看修订，运行 `python -m alembic upgrade head`，然后用 `current`、`check` 与 [完整性脚本](../scripts/check_database_integrity.py)验证。`backups/` 存放数据库备份，由 Git 忽略。
