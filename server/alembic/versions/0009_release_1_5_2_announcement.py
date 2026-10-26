"""Add the approved 1.5.2 announcement without changing existing content."""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0009_release_1_5_2"
down_revision = "0008_feedback_announcements"
branch_labels = None
depends_on = None

TITLE = "1.5.2 更新公告"
SUMMARY = "更新了中英双语选择。"
BODY = (
    "1. 新增语言设置\n"
    "在“我的 → 语言 / Language”中，可切换简体中文与 English，系统会记住你的选择。\n\n"
    "2. 常用界面支持双语\n"
    "首页、刷题、AI问答、我的，以及导航、按钮和操作提示，随语言设置同步切换。\n\n"
    "3. AI 回答跟随界面语言\n"
    "英文界面下，AI 默认使用英语讲解；你也可以直接指定希望使用的语言。"
)


def upgrade():
    announcements = sa.table(
        "content_items",
        sa.column("category", sa.String(20)),
        sa.column("title", sa.String(128)),
        sa.column("summary", sa.String(255)),
        sa.column("body", sa.Text()),
        sa.column("release_version", sa.String(24)),
        sa.column("published_at", sa.DateTime()),
        sa.column("is_active", sa.Integer()),
        sa.column("sort_order", sa.Integer()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    values = {
        "category": "notice", "title": TITLE, "summary": SUMMARY, "body": BODY,
        "release_version": "1.5.2", "published_at": now, "is_active": 1,
        "sort_order": 0, "created_at": now, "updated_at": now,
    }
    # Also works for offline SQL generation. Keep any pre-existing 1.5.2 record,
    # including an intentionally unpublished or operator-edited announcement.
    exists = sa.exists(sa.select(announcements.c.release_version).where(
        announcements.c.category == "notice", announcements.c.release_version == "1.5.2",
    ))
    source = sa.select(*(sa.literal(value, type_=announcements.c[key].type)
                         for key, value in values.items())).where(~exists)
    op.execute(announcements.insert().from_select(list(values), source))


def downgrade():
    # Announcements are editorial history. A code rollback must not erase them.
    pass
