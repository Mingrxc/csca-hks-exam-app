# 数据库

更新：2026-10-22。MySQL8.4，当前迁移0007_question_bank_v2，复用现有Conda deng环境。

10张业务表：users、user_exam_targets、streak_records、questions、papers、answer_records、wrong_book、knowledge_stats、favorites、content_items。Alembic另维护版本表。

新版题目按唯一bank_id更新，独立保存版本、等级、模块、材料、作答与评分方式。source_data完整保留原题。题目答案与作答记录使用TEXT，开放题通过可空is_correct及self_score单独管理。

## 初始化与重建

用户确认当前业务数据可清空。项目根目录执行：

```powershell
conda activate deng
python scripts/reset_database.py
python scripts/reset_database.py --apply --expected-database csca_hks_exam
```

默认仅输出计划。--apply先成功生成database/backups/before-bank-v2-*.sql及SHA-256，再重建业务表、执行完整迁移并导入1221题。口语和口译99题不入库，原稿保留。MySQL服务、账号和环境配置继续复用。备份目录已忽略，不提交Git。

全新环境先创建空数据库，再从server目录执行python -m alembic upgrade head，最后执行导入器--apply。真实连接信息来自环境变量及server/.env、server/.env.local，不写入文档。

## 验证

```powershell
python scripts/check_database_integrity.py
cd server
python -m alembic current
python -m alembic check
python -m pytest -q
```

schema.sql为当前ORM生成的结构参考。使用Alembic初始化，不手工猜测stamp版本。python scripts/export_schema.py可重新生成参考文件，无数据库读写。

字段与导入边界见[新版题库契约](../docs/question-bank-import-contract.md)。本地数据库与正式服务器分别核验，本地重建不表示已经更新线上。
