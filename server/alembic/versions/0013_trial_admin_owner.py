"""Mark an explicitly bound trial owner without consuming lw000."""
from alembic import op
import sqlalchemy as sa

revision = "0013_trial_admin_owner"
down_revision = "0012_admin_center"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("admin_owner", sa.Column("is_temporary", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    raise RuntimeError("Retain the trial-owner marker to avoid changing the meaning of an existing owner binding.")
