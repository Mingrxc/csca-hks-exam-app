"""Add home content, favorites and AI-ready tables.

Revision ID: 0003_content_favorite_ai
Revises: 0002_answer_record_uniqueness
Create Date: 2026-08-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "0003_content_favorite_ai"
down_revision: Union[str, None] = "0002_answer_record_uniqueness"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=256), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "question_id", name="uk_user_favorite_question"),
        comment="收藏题目表",
    )
    op.create_index("idx_favorites_user", "favorites", ["user_id"])
    op.create_index("idx_favorites_question", "favorites", ["question_id"])
    op.create_index("idx_favorites_created", "favorites", ["created_at"])

    op.create_table(
        "content_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.Enum("consulting", "club", "ad", "notice"), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("cover_image", sa.String(length=512), nullable=True),
        sa.Column("link_url", sa.String(length=512), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=True),
        sa.Column("is_active", mysql.TINYINT(display_width=1), server_default="1", nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="首页资讯和广告内容表",
    )
    op.create_index("idx_content_category", "content_items", ["category"])
    op.create_index("idx_content_sort", "content_items", ["sort_order"])
    op.create_index("idx_content_active", "content_items", ["is_active"])


def downgrade() -> None:
    op.drop_index("idx_content_active", table_name="content_items")
    op.drop_index("idx_content_sort", table_name="content_items")
    op.drop_index("idx_content_category", table_name="content_items")
    op.drop_table("content_items")

    op.drop_index("idx_favorites_created", table_name="favorites")
    op.drop_index("idx_favorites_question", table_name="favorites")
    op.drop_index("idx_favorites_user", table_name="favorites")
    op.drop_table("favorites")
