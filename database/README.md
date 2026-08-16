# 数据库

## 表结构（7张表）

| 表名 | 说明 |
|------|------|
| `users` | 用户表（微信授权、学习数据、打卡） |
| `questions` | 题目表（题干、选项、答案、解析、难度/知识点标签） |
| `papers` | 试卷表（组卷策略、题目列表、限时） |
| `answer_records` | 答题记录表（每题作答、对错、用时、错因） |
| `wrong_book` | 错题本表（累计错误次数、掌握标记、复习时间） |
| `knowledge_stats` | 知识点统计表（各知识点的正确率） |
| `streak_records` | 打卡记录表（每日刷题数） |

## 索引设计

- 高频查询字段均已建索引（exam_type、knowledge_point、difficulty、user_id 等）
- 错题本使用 `UNIQUE(user_id, question_id)` 保证不重复
- 答题记录使用 `UNIQUE(user_id, paper_id, question_id)` 保证重复提交不会产生重复行

## 迁移

使用 Alembic 管理数据库版本。连接参数从 `server/.env` 读取。

### 全新数据库

先创建空数据库 `csca_hks_exam`，然后执行：

```powershell
cd server
.venv/Scripts/python -m alembic upgrade head
```

### 已有数据库首次接入 Alembic

当前线上/本地库已经由旧版 `database/schema.sql` 创建时，先备份数据库，再执行：

```powershell
cd server
.venv/Scripts/python -m alembic stamp 0001_initial_schema
.venv/Scripts/python -m alembic upgrade head
```

`0002_answer_record_uniqueness` 会保留每组答题自然键中 ID 最大的记录、添加唯一约束，并统一旧索引名称。

### 继续使用 schema.sql

当前 `database/schema.sql` 已对应最新结构。导入后要标记版本，避免 Alembic 重复建表：

```powershell
cd server
.venv/Scripts/python -m alembic stamp head
```

后续生成迁移：

```powershell
cd server
.venv/Scripts/python -m alembic revision --autogenerate -m "描述"
.venv/Scripts/python -m alembic upgrade head
```

当前暂不添加数据库外键：历史库需要先在真实 MySQL 上完成孤儿记录审计。用户/试卷所有权和题目归属目前由服务层校验，唯一约束负责阻止重复业务记录。
