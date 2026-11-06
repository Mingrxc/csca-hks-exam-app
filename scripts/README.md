# 项目维护脚本

在仓库根目录使用项目 Python 环境执行。涉及数据库的脚本沿用后端配置，变更前核对目标库。

- `import_questions.py` 从同级 `original_question_bank/` 校验题库，`--apply` 写入，`--verify-db` 读取题库计数。源格式见[题库契约](../docs/question-bank-import-contract.md)。
- `check_database_integrity.py` 只读检查题目、业务归属、重复键和外键。`export_schema.py` 离线生成 `database/schema.sql`。
- `build_backend_bundle.py` 将后端、迁移、测试、题库和引用的素材打包到同级 `deployment-artifacts/`。仓库根 `.env.example` 随包放到 `server/`，真实配置不入包。
- `bootstrap_admin_owner.py` 预览或绑定唯一主管理员，`assign_owner_code.py` 独立维护保留编号。`manage_feedback.py` 支持私密反馈查询，显式指定 `--mark` 与 `--to` 才更新状态。
- `reset_database.py` 默认只预览重建步骤，仅在明确要重建时使用 `--apply`，并先完成备份。
- `start_public_dev.ps1` 和 `start_public_dev.cmd` 使用已安装的 cloudflared 启动联调。参数与进程环境变量见[网络说明](../docs/network-environments.md)。
