# 工具脚本

| 脚本 | 用途 |
|------|------|
| `import_questions.py` | Validate and import `original_question_bank` JSON into `questions`. Defaults to dry-run; add `--apply` to write. |
| `check_database_integrity.py` | 只读检查答题重复键、业务表孤儿引用、题目量和 Alembic 版本。 |
| `build_backend_bundle.py` | 将后端、迁移脚本和原始题库打包，生成 SHA-256 校验和文件清单；不包含真实凭据、用户数据或本地依赖。 |

从项目根目录运行：

```powershell
server/.venv/Scripts/python scripts/check_database_integrity.py
```

使用已有的 Conda `deng` 环境打包后端：

```powershell
conda run -n deng python scripts/build_backend_bundle.py
```

题库来源仍为项目同级的 `../original_question_bank`，输出到同级的 `../deployment-artifacts`，文件名包含打包日期和时间。验证用的临时解压目录会自动删除。打包本身不会上传服务器或写入数据库。

## 新版题库适配（2026-10-22）

- reset_database.py：默认仅计划；--apply先SQL备份，再重建到0007_question_bank_v2并导入1221题。--expected-database核对库名，远程另需--allow-remote。
- export_schema.py：从ORM生成database/schema.sql参考，不访问数据库。
- import_questions.py：稳定题号更新、保留新字段与图片选项；排除99道口语／口译，有无效记录时阻止写入。
- build_backend_bundle.py：新增重建工具、新迁移及实际引用的音频图片；包内不含真实配置、数据库备份或本地用户数据。

详细说明见docs/question-bank-import-contract.md。运行现有环境即可，不需要新增依赖。
