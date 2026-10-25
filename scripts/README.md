# 工具脚本

更新：2026-10-25。使用现有Conda deng或服务器既有Python环境，不新建环境或安装依赖。

| 脚本 | 用途 |
|---|---|
| import_questions.py | 默认校验原始题库；--apply按稳定题号写入，--verify-db核对。 |
| check_database_integrity.py | 只读检查业务归属、外键、重复键、题量及迁移版本，包含反馈表。 |
| manage_feedback.py | 运营者在服务器读取/导出私密反馈；显式--mark配合--to才更新状态。 |
| export_schema.py | 根据ORM生成database/schema.sql参考，不连接数据库。 |
| build_backend_bundle.py | 打包后端、最新迁移、工具、原题和153份活动媒体，生成SHA与清单，不含真实配置/用户/备份/依赖。 |
| reset_database.py | 默认仅计划；只有明确授权的重建任务才运行--apply，先验证SQL备份再重建到Alembic head。1.5.1不使用。 |

项目根目录的只读检查和反馈维护：

```powershell
conda activate deng
python scripts/check_database_integrity.py
python scripts/manage_feedback.py --status unread
python scripts/manage_feedback.py --mark 12 --to read
```

反馈可通过--page/--page-size分页，--output导出当前页到指定仓库外私有JSON路径。反馈原文与导出不得提交Git。CLI要求运营者拥有服务器及数据库配置访问权限；对外HTTP管理员接口另要求JWT与CONTENT_ADMIN_OPENIDS白名单。

后端打包：

```powershell
python scripts/build_backend_bundle.py
```

题库来源为同级original_question_bank，产物在同级deployment-artifacts。新打包清单标记0008_feedback_announcements，包含manage_feedback和1.5.1发布说明；20261022旧包不含本轮代码。打包不上传服务器或写数据库。

1.5.1部署只增量执行Alembic，保留现有题库/用户/学习数据。详见[发布说明](../docs/release-1.5.1.md)。
