# 数据库

当前本地1.5.5最新迁移0014_release_1_5_5（0012新增权限表，0013追加临时主管理员标记，0014仅更新定稿公告），共15张应用表（含user_code_counters）及alembic_version，schema.sql结构无需变化。正式部署记录为1.5.5/0013，lw005已绑定临时主管理员；本轮0014未执行真实迁移。0014将1.5.5公告摘要/正文改为“新增了一些功能”，设为北京时间2026-11-02起公开，保留其他公告、用户/编号/权限/学习数据。首次绑定和权限约束见docs/release-1.5.5.md，下方1.5.4说明为开发阶段历史。

更新：2026-10-30。MySQL8.4，源码最新迁移0011_login_strategy，复用现有Conda deng环境。本轮1.5.4未在现有MySQL或正式库执行迁移。

目标11张业务表及1张发号计数表：user_code_counters、users、user_exam_targets、streak_records、questions、papers、answer_records、wrong_book、knowledge_stats、favorites、content_items、feedback；Alembic另维护版本表。

0007保存稳定bank_id、完整原题、材料与作答/评分方式，答案和作答为TEXT，开放题通过is_correct空值及self_score单独管理。0008新增私密反馈表和版本公告字段，不更改题库与学习记录，并准备一份未公开的1.5.1公告草稿。

## 1.5.4增量升级

0011新增users.user_code（唯一非空）与user_code_counters，回填原用户编号并添加已定稿1.5.4公告。用户主键/外键和学习记录保留，lw000暂未绑定。永久编号不提供删字段downgrade，应用回退保留结构。参见docs/release-1.5.4.md。

先核对目标环境并按现有流程备份，再从server目录使用既有Python环境执行：

```text
python -m alembic current
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

本轮不清库、不使用reset_database、不重新导入题库。2026-10-22的题库替换清库授权只针对当次任务，不能沿用到后续维护。

全新空库同样使用Alembic初始化，再按明确安排导入题库。真实连接配置来自环境变量和server/.env、.env.local，不进入文档或Git。

## 验证与结构参考

```text
python scripts/check_database_integrity.py
python scripts/export_schema.py
```

完整性检查包含反馈归属外键，升级前的旧数据库会报告缺少feedback表，不应为此重建原库。schema.sql是当前ORM生成的参考，不代替迁移，也不对未知旧库猜测stamp。

见[1.5.1发布说明](../docs/release-1.5.1.md)与[题库契约](../docs/question-bank-import-contract.md)。测试使用独立SQLite，不代表正式数据库已升级。
