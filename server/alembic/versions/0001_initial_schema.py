"""Initial schema baseline.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("openid", sa.String(length=64), nullable=False),
        sa.Column("unionid", sa.String(length=64), nullable=True),
        sa.Column("nickname", sa.String(length=64), server_default="考霸同学", nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("target_exam", sa.Enum("CSCA", "HKS"), server_default="CSCA", nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("total_questions", sa.Integer(), server_default="0", nullable=True),
        sa.Column("total_correct", sa.Integer(), server_default="0", nullable=True),
        sa.Column("streak_days", sa.Integer(), server_default="0", nullable=True),
        sa.Column("last_streak_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openid", name="openid"),
        comment="用户表",
    )
    op.create_index("idx_openid", "users", ["openid"])
    op.create_index("idx_created", "users", ["created_at"])

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exam_type", sa.Enum("CSCA", "HKS"), nullable=False),
        sa.Column("subject", sa.String(length=32), nullable=False),
        sa.Column("knowledge_point", sa.String(length=64), nullable=False),
        sa.Column("difficulty", sa.Enum("easy", "medium", "hard"), nullable=False),
        sa.Column("question_type", sa.Enum("single", "multi", "judge", "fill"), nullable=False),
        sa.Column("stem_text", sa.Text(), nullable=False),
        sa.Column("stem_image", sa.String(length=512), nullable=True),
        sa.Column("stem_audio", sa.String(length=512), nullable=True),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("answer", sa.String(length=256), nullable=False),
        sa.Column("analysis", sa.Text(), nullable=True),
        sa.Column("wrong_options_analysis", sa.JSON(), nullable=True),
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("correct_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("wrong_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("wrong_rate", sa.Float(), server_default="0", nullable=True),
        sa.Column("is_active", mysql.TINYINT(display_width=1), server_default="1", nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="题目表",
    )
    op.create_index("idx_exam_type", "questions", ["exam_type"])
    op.create_index("idx_subject", "questions", ["subject"])
    op.create_index("idx_knowledge", "questions", ["knowledge_point"])
    op.create_index("idx_difficulty", "questions", ["difficulty"])
    op.create_index("idx_type", "questions", ["question_type"])
    op.create_index("idx_wrong_rate", "questions", ["wrong_rate"])

    op.create_table(
        "papers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("exam_type", sa.Enum("CSCA", "HKS"), nullable=False),
        sa.Column("strategy", sa.Enum("random", "knowledge", "progressive", "real"), nullable=False),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Integer(), server_default="0", nullable=True),
        sa.Column("time_limit", sa.Integer(), server_default="0", nullable=True),
        sa.Column("mode", sa.Enum("exam", "practice"), server_default="practice", nullable=True),
        sa.Column("difficulty", sa.Enum("all", "easy", "medium", "hard"), server_default="all", nullable=True),
        sa.Column("is_public", mysql.TINYINT(display_width=1), server_default="0", nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="试卷表",
    )
    op.create_index("idx_user", "papers", ["user_id"])
    op.create_index("idx_exam_type", "papers", ["exam_type"])
    op.create_index("idx_strategy", "papers", ["strategy"])

    op.create_table(
        "answer_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("paper_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_answer", sa.String(length=256), nullable=True),
        sa.Column("is_correct", mysql.TINYINT(display_width=1), nullable=True),
        sa.Column("time_spent", sa.Integer(), server_default="0", nullable=True),
        sa.Column(
            "wrong_reason",
            sa.Enum("知识点不会", "粗心大意", "审题错误", "时间不够", "选项混淆", "其他"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="答题记录表",
    )
    op.create_index("idx_user_paper", "answer_records", ["user_id", "paper_id"])
    op.create_index("idx_question", "answer_records", ["question_id"])
    op.create_index("idx_correct", "answer_records", ["is_correct"])
    op.create_index("idx_wrong_reason", "answer_records", ["wrong_reason"])

    op.create_table(
        "wrong_book",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("wrong_count", sa.Integer(), server_default="1", nullable=True),
        sa.Column("correct_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("is_mastered", mysql.TINYINT(display_width=1), server_default="0", nullable=True),
        sa.Column("first_wrong_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("last_wrong_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("last_review_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "question_id", name="uk_user_question"),
        comment="错题本表",
    )
    op.create_index("idx_user", "wrong_book", ["user_id"])
    op.create_index("idx_mastered", "wrong_book", ["is_mastered"])
    op.create_index("idx_last_wrong", "wrong_book", ["last_wrong_at"])

    op.create_table(
        "knowledge_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exam_type", sa.Enum("CSCA", "HKS"), nullable=False),
        sa.Column("knowledge_point", sa.String(length=64), nullable=False),
        sa.Column("total_answered", sa.Integer(), server_default="0", nullable=True),
        sa.Column("total_correct", sa.Integer(), server_default="0", nullable=True),
        sa.Column("correct_rate", sa.Float(), server_default="0", nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exam_type", "knowledge_point", name="uk_user_exam_knowledge"),
        comment="知识点统计表",
    )
    op.create_index("idx_user_exam", "knowledge_stats", ["user_id", "exam_type"])

    op.create_table(
        "streak_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("streak_date", sa.Date(), nullable=False),
        sa.Column("question_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "streak_date", name="uk_user_date"),
        comment="打卡记录表",
    )
    op.create_index("idx_user", "streak_records", ["user_id"])
    op.create_index("idx_date", "streak_records", ["streak_date"])


def downgrade() -> None:
    op.drop_table("streak_records")
    op.drop_table("knowledge_stats")
    op.drop_table("wrong_book")
    op.drop_table("answer_records")
    op.drop_table("papers")
    op.drop_table("questions")
    op.drop_table("users")
