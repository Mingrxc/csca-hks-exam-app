"""Apply the approved 1.5.5 announcement, scheduled for November 2 in Beijing."""
from datetime import datetime, timedelta, timezone

from alembic import op
import sqlalchemy as sa

revision = "0014_release_1_5_5"
down_revision = "0013_trial_admin_owner"
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
    published_at = datetime(2026, 11, 2, tzinfo=timezone(timedelta(hours=8)))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    values = {
        "category": "notice",
        "title": "1.5.5 更新公告",
        "summary": "新增了一些功能",
        "body": "新增了一些功能",
        "release_version": "1.5.5",
        "published_at": published_at.astimezone(timezone.utc).replace(tzinfo=None),
        "is_active": 1,
        "updated_at": now,
    }
    target = sa.and_(announcements.c.category == "notice", announcements.c.release_version == "1.5.5")
    # 更新 0012 创建的草稿，保留公告编号和创建时间。
    op.execute(announcements.update().where(target).values(**values))
    values.update(sort_order=0, created_at=now)
    exists = sa.exists(sa.select(announcements.c.release_version).where(target))
    source = sa.select(*(sa.literal(value, type_=announcements.c[key].type)
                         for key, value in values.items())).where(~exists)
    op.execute(announcements.insert().from_select(list(values), source))


def downgrade():
    # 应用回退时保留已经定稿的公告。
    pass
