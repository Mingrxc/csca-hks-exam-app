"""Versioned question bank, complete source metadata and self assessment."""
from alembic import op
import sqlalchemy as sa

revision = "0007_question_bank_v2"
down_revision = "0006_ownership_foreign_keys"
branch_labels = None
depends_on = None


def upgrade():
    for column in [
        sa.Column("bank_id", sa.String(96), nullable=True, comment="Stable source question ID"),
        sa.Column("exam_version", sa.String(24), nullable=True),
        sa.Column("level", sa.String(8), nullable=True),
        sa.Column("knowledge_module", sa.String(96), nullable=True),
        sa.Column("material_id", sa.String(96), nullable=True),
        sa.Column("response_mode", sa.String(32), nullable=False, server_default="choice"),
        sa.Column("scoring_mode", sa.String(40), nullable=False, server_default="objective"),
        sa.Column("max_score", sa.Float(), nullable=False, server_default="1"),
        sa.Column("source_data", sa.JSON(), nullable=True, comment="Lossless private source metadata"),
    ]:
        op.add_column("questions", column)
    op.create_unique_constraint("bank_id", "questions", ["bank_id"])
    op.create_index("ix_questions_material_id", "questions", ["material_id"])
    op.create_index("idx_questions_version_level", "questions", ["exam_version", "level"])
    op.alter_column("questions", "answer", existing_type=sa.String(256), type_=sa.Text(), existing_nullable=False, comment="Correct or reference answer")
    op.add_column("papers", sa.Column("selection", sa.JSON(), nullable=True, comment="Version, level and category selection"))
    op.alter_column("answer_records", "user_answer", existing_type=sa.String(256), type_=sa.Text(), existing_nullable=True, comment="Submitted answer")
    op.add_column("answer_records", sa.Column("evaluation_status", sa.String(32), nullable=False, server_default="objective"))
    op.add_column("answer_records", sa.Column("self_score", sa.Float(), nullable=True, comment="Self-assessed practice score"))
    op.add_column("users", sa.Column("total_objective", sa.Integer(), nullable=True, server_default="0", comment="Automatically graded questions answered"))
    op.execute("UPDATE users SET total_objective = total_questions")


def downgrade():
    op.drop_column("users", "total_objective")
    op.drop_column("answer_records", "self_score")
    op.drop_column("answer_records", "evaluation_status")
    op.drop_column("papers", "selection")
    op.drop_index("idx_questions_version_level", table_name="questions")
    op.drop_index("ix_questions_material_id", table_name="questions")
    op.drop_constraint("bank_id", "questions", type_="unique")
    for name in ["source_data", "max_score", "scoring_mode", "response_mode", "material_id", "knowledge_module", "level", "exam_version", "bank_id"]:
        op.drop_column("questions", name)
    # Keep TEXT answers on downgrade to avoid truncating existing long responses.
