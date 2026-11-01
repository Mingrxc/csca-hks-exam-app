"""Permanent public user codes and the approved 1.5.4 announcement."""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0011_login_strategy"
down_revision = "0010_release_1_5_3"
branch_labels = None
depends_on = None
USER_CODE_COMMENT = "Permanent public user number; lw000 is reserved"


def upgrade():
    op.add_column("users", sa.Column("user_code", sa.String(32), nullable=True, comment=USER_CODE_COMMENT))
    if op.get_context().dialect.name == "sqlite":
        op.execute("UPDATE users SET user_code = printf('lw%03d', id)")
        with op.batch_alter_table("users") as batch:
            batch.alter_column("user_code", existing_type=sa.String(32), nullable=False)
    else:
        op.execute("UPDATE users SET user_code = CONCAT('lw', CASE WHEN id < 1000 THEN LPAD(CAST(id AS CHAR), 3, '0') ELSE CAST(id AS CHAR) END)")
        op.alter_column("users", "user_code", existing_type=sa.String(32), nullable=False,
                        comment=USER_CODE_COMMENT, existing_comment=USER_CODE_COMMENT)
    op.create_index("uk_users_user_code", "users", ["user_code"], unique=True)
    op.create_table("user_code_counters", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("next_value", sa.Integer(), nullable=False))
    op.execute("INSERT INTO user_code_counters (id, next_value) SELECT 1, COALESCE(MAX(id), 0) + 1 FROM users")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    entries = sa.table("content_items", sa.column("category", sa.String()), sa.column("title", sa.String()),
                       sa.column("summary", sa.String()), sa.column("body", sa.Text()),
                       sa.column("release_version", sa.String()), sa.column("published_at", sa.DateTime()),
                       sa.column("is_active", sa.Integer()), sa.column("sort_order", sa.Integer()),
                       sa.column("created_at", sa.DateTime()), sa.column("updated_at", sa.DateTime()))
    values = {"category": "notice", "title": "1.5.4 更新公告", "summary": "优化登录策略", "body": "优化登录策略",
              "release_version": "1.5.4", "published_at": now, "is_active": 1, "sort_order": 0,
              "created_at": now, "updated_at": now}
    exists = sa.exists(sa.select(entries.c.release_version).where(entries.c.category == "notice", entries.c.release_version == "1.5.4"))
    source = sa.select(*(sa.literal(value, type_=entries.c[key].type) for key, value in values.items())).where(~exists)
    op.execute(entries.insert().from_select(list(values), source))


def downgrade():
    raise RuntimeError("Public user numbers are permanent. Retain this schema when rolling back application code.")
