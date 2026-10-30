"""Add the approved 1.5.3 announcement; keep earlier content and learning data."""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0010_release_1_5_3"
down_revision = "0009_release_1_5_2"
branch_labels = None
depends_on = None


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
        "category": "notice", "title": "1.5.3 更新公告",
        "summary": "撤销AI功能", "body": "撤销AI功能",
        "release_version": "1.5.3", "published_at": now, "is_active": 1,
        "sort_order": 0, "created_at": now, "updated_at": now,
    }
    # Preserve an existing same-version record, including a withdrawn draft.
    exists = sa.exists(sa.select(announcements.c.release_version).where(
        announcements.c.category == "notice", announcements.c.release_version == "1.5.3",
    ))
    source = sa.select(*(sa.literal(value, type_=announcements.c[key].type)
                         for key, value in values.items())).where(~exists)
    op.execute(announcements.insert().from_select(list(values), source))


def downgrade():
    # Code rollback must not delete editorial history.
    pass
