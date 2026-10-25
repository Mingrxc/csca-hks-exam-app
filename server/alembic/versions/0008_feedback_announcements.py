"""Private feedback and versioned update announcements; preserve learning data."""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0008_feedback_announcements"
down_revision = "0007_question_bank_v2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(64), nullable=False, comment="Per-user idempotency key"),
        sa.Column("category", sa.String(24), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("app_version", sa.String(24), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="unread"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_feedback_user", ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "request_id", name="uk_feedback_user_request"),
        comment="Private user feedback for the operator",
    )
    op.create_index("idx_feedback_user_created", "feedback", ["user_id", "created_at"])
    op.create_index("idx_feedback_status_created", "feedback", ["status", "created_at"])
    op.add_column("content_items", sa.Column("release_version", sa.String(24), nullable=True, comment="App version for update announcements"))
    op.add_column("content_items", sa.Column("published_at", sa.DateTime(), nullable=True, comment="Publication time in UTC"))
    # Prepare release notes as an unpublished draft. Publishing is an explicit admin action.
    drafts = sa.table("content_items", sa.column("category", sa.String()), sa.column("title", sa.String()),
                      sa.column("summary", sa.String()), sa.column("body", sa.Text()),
                      sa.column("release_version", sa.String()), sa.column("is_active", sa.Integer()),
                      sa.column("sort_order", sa.Integer()), sa.column("created_at", sa.DateTime()),
                      sa.column("updated_at", sa.DateTime()))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    op.bulk_insert(drafts, [{
        "category": "notice", "title": "1.5.1 更新说明", "release_version": "1.5.1",
        "summary": "学习助手优化，新增用户反馈、关于页面与更新公告。",
        "body": "1. 优化学习 AI 助手的题目讲解和复习建议。\n2. 在“我的”新增用户反馈，可提交题目问题、功能异常和使用建议。\n3. 新增关于页面，展示品牌、版本、更新公告和隐私保护指引。",
        "is_active": 0, "sort_order": 0, "created_at": now, "updated_at": now,
    }])


def downgrade():
    op.drop_column("content_items", "published_at")
    op.drop_column("content_items", "release_version")
    op.drop_table("feedback")
