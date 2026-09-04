"""Store an independent target date for each exam type."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_user_exam_targets"
down_revision: Union[str, None] = "0003_content_favorite_ai"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_exam_targets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exam_type", sa.Enum("CSCA", "HKS"), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exam_type", name="uk_user_exam_target"),
        comment="用户各考试目标日期",
    )
    op.create_index("idx_user_exam_target_user", "user_exam_targets", ["user_id"])
    op.create_index("idx_user_exam_target_exam", "user_exam_targets", ["exam_type"])

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO user_exam_targets (user_id, exam_type, target_date)
            SELECT id, target_exam, target_date
            FROM users
            WHERE target_exam IS NOT NULL AND target_date IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_index("idx_user_exam_target_exam", table_name="user_exam_targets")
    op.drop_index("idx_user_exam_target_user", table_name="user_exam_targets")
    op.drop_table("user_exam_targets")
