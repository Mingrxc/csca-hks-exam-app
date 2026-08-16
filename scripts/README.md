# 工具脚本

| 脚本 | 用途 |
|------|------|
| `import_questions.py` | Validate and import `original_question_bank` JSON into `questions`. Defaults to dry-run; add `--apply` to write. |
| `check_database_integrity.py` | 只读检查答题重复键、业务表孤儿引用、题目量和 Alembic 版本。 |

从项目根目录运行：

```powershell
server/.venv/Scripts/python scripts/check_database_integrity.py
```
