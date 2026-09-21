"""Add ownership and question-reference foreign keys.

Revision ID: 0006_ownership_foreign_keys
Revises: 0005_english_column_comments
Create Date: 2026-09-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_ownership_foreign_keys"
down_revision: Union[str, None] = "0005_english_column_comments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ORPHAN_CHECKS = {
    "papers.user_id": "SELECT COUNT(*) FROM papers p LEFT JOIN users u ON u.id = p.user_id WHERE u.id IS NULL",
    "answer_records.user_id": "SELECT COUNT(*) FROM answer_records a LEFT JOIN users u ON u.id = a.user_id WHERE u.id IS NULL",
    "answer_records.paper_id": "SELECT COUNT(*) FROM answer_records a LEFT JOIN papers p ON p.id = a.paper_id WHERE p.id IS NULL",
    "answer_records.question_id": "SELECT COUNT(*) FROM answer_records a LEFT JOIN questions q ON q.id = a.question_id WHERE q.id IS NULL",
    "wrong_book.user_id": "SELECT COUNT(*) FROM wrong_book w LEFT JOIN users u ON u.id = w.user_id WHERE u.id IS NULL",
    "wrong_book.question_id": "SELECT COUNT(*) FROM wrong_book w LEFT JOIN questions q ON q.id = w.question_id WHERE q.id IS NULL",
    "knowledge_stats.user_id": "SELECT COUNT(*) FROM knowledge_stats k LEFT JOIN users u ON u.id = k.user_id WHERE u.id IS NULL",
    "streak_records.user_id": "SELECT COUNT(*) FROM streak_records s LEFT JOIN users u ON u.id = s.user_id WHERE u.id IS NULL",
    "favorites.user_id": "SELECT COUNT(*) FROM favorites f LEFT JOIN users u ON u.id = f.user_id WHERE u.id IS NULL",
    "favorites.question_id": "SELECT COUNT(*) FROM favorites f LEFT JOIN questions q ON q.id = f.question_id WHERE q.id IS NULL",
    "user_exam_targets.user_id": "SELECT COUNT(*) FROM user_exam_targets t LEFT JOIN users u ON u.id = t.user_id WHERE u.id IS NULL",
}


FOREIGN_KEYS = (
    ("fk_papers_user", "papers", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_answer_records_user", "answer_records", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_answer_records_paper", "answer_records", "papers", ["paper_id"], ["id"], "CASCADE"),
    ("fk_answer_records_question", "answer_records", "questions", ["question_id"], ["id"], "RESTRICT"),
    ("fk_wrong_book_user", "wrong_book", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_wrong_book_question", "wrong_book", "questions", ["question_id"], ["id"], "RESTRICT"),
    ("fk_knowledge_stats_user", "knowledge_stats", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_streak_records_user", "streak_records", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_favorites_user", "favorites", "users", ["user_id"], ["id"], "CASCADE"),
    ("fk_favorites_question", "favorites", "questions", ["question_id"], ["id"], "RESTRICT"),
    ("fk_user_exam_targets_user", "user_exam_targets", "users", ["user_id"], ["id"], "CASCADE"),
)


def upgrade() -> None:
    bind = op.get_bind()
    for label, statement in ORPHAN_CHECKS.items():
        count = bind.execute(sa.text(statement)).scalar_one()
        if count:
            raise RuntimeError(f"Cannot add foreign key for {label}: {count} orphan rows found")

    for name, source, target, local_columns, remote_columns, ondelete in FOREIGN_KEYS:
        op.create_foreign_key(
            name,
            source,
            target,
            local_columns,
            remote_columns,
            ondelete=ondelete,
        )


def downgrade() -> None:
    for name, source, *_ in reversed(FOREIGN_KEYS):
        op.drop_constraint(name, source, type_="foreignkey")
