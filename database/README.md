# 数据库

## 表结构（6张表）

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

## 迁移

使用 Alembic 管理数据库版本：

```bash
cd server
alembic revision --autogenerate -m "描述"
alembic upgrade head
```
