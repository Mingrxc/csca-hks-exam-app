"""Owner, read-only members and audit trail; no automatic privilege grants."""
from alembic import op
import sqlalchemy as sa

revision = "0012_admin_center"
down_revision = "0011_login_strategy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("admin_owner",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_admin_owner_singleton"),
        sa.UniqueConstraint("user_id", name="uk_admin_owner_user"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_admin_owner_user", ondelete="RESTRICT"))
    op.create_table("admin_members",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_admin_member_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"], name="fk_admin_member_grantor", ondelete="RESTRICT"))
    op.create_table("admin_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_code", sa.String(32), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name="fk_admin_audit_actor", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], name="fk_admin_audit_target", ondelete="SET NULL"))
    op.create_index("idx_admin_audit_created", "admin_audit_logs", ["created_at"])
    # Trial release: prepare a draft only; the owner decides when to publish it.
    entries = sa.table("content_items", sa.column("category", sa.String()), sa.column("title", sa.String()),
        sa.column("summary", sa.String()), sa.column("body", sa.Text()), sa.column("release_version", sa.String()),
        sa.column("is_active", sa.Integer()), sa.column("sort_order", sa.Integer()),
        sa.column("created_at", sa.DateTime()), sa.column("updated_at", sa.DateTime()))
    values = {"category": "notice", "title": "1.5.5 更新公告", "summary": "新增管理员功能",
        "body": "新增管理中心，支持后台数据查看、用户反馈查看与管理员权限管理。", "release_version": "1.5.5",
        "is_active": 0, "sort_order": 0, "created_at": sa.func.now(), "updated_at": sa.func.now()}
    exists = sa.exists(sa.select(entries.c.release_version).where(entries.c.category == "notice", entries.c.release_version == "1.5.5"))
    source = sa.select(*(value if isinstance(value, sa.sql.ClauseElement) else sa.literal(value, type_=entries.c[key].type)
                         for key, value in values.items())).where(~exists)
    op.execute(entries.insert().from_select(list(values), source))


def downgrade():
    raise RuntimeError("Retain owner grants and audit history when rolling back application code.")
