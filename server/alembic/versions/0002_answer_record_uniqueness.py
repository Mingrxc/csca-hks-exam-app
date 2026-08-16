"""Deduplicate answer records and enforce one answer per paper question.

Revision ID: 0002_answer_record_uniqueness
Revises: 0001_initial_schema
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0002_answer_record_uniqueness"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users RENAME INDEX idx_openid TO idx_users_openid")
    op.execute("ALTER TABLE users RENAME INDEX idx_created TO idx_users_created")
    op.execute("ALTER TABLE questions RENAME INDEX idx_exam_type TO idx_questions_exam_type")
    op.execute("ALTER TABLE questions RENAME INDEX idx_subject TO idx_questions_subject")
    op.execute("ALTER TABLE questions RENAME INDEX idx_knowledge TO idx_questions_knowledge")
    op.execute("ALTER TABLE questions RENAME INDEX idx_difficulty TO idx_questions_difficulty")
    op.execute("ALTER TABLE questions RENAME INDEX idx_type TO idx_questions_type")
    op.execute("ALTER TABLE questions RENAME INDEX idx_wrong_rate TO idx_questions_wrong_rate")
    op.execute("ALTER TABLE papers RENAME INDEX idx_user TO idx_papers_user")
    op.execute("ALTER TABLE papers RENAME INDEX idx_exam_type TO idx_papers_exam_type")
    op.execute("ALTER TABLE papers RENAME INDEX idx_strategy TO idx_papers_strategy")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_user TO idx_wrongbook_user")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_mastered TO idx_wrongbook_mastered")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_last_wrong TO idx_wrongbook_last_wrong")
    op.create_index("idx_wrongbook_question", "wrong_book", ["question_id"])
    op.execute(
        "ALTER TABLE knowledge_stats "
        "RENAME INDEX uk_user_exam_knowledge TO uk_user_exam_point"
    )
    op.execute(
        "ALTER TABLE knowledge_stats RENAME INDEX idx_user_exam TO idx_knowledge_user_exam"
    )
    op.execute("ALTER TABLE streak_records RENAME INDEX idx_user TO idx_streak_user")
    op.execute("ALTER TABLE streak_records RENAME INDEX idx_date TO idx_streak_date")

    # Keep the newest record for each natural key before adding the constraint.
    op.execute(
        """
        DELETE older
        FROM answer_records AS older
        INNER JOIN answer_records AS newer
            ON older.user_id = newer.user_id
            AND older.paper_id = newer.paper_id
            AND older.question_id = newer.question_id
            AND older.id < newer.id
        """
    )
    op.create_unique_constraint(
        "uk_user_paper_question",
        "answer_records",
        ["user_id", "paper_id", "question_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uk_user_paper_question", "answer_records", type_="unique")
    op.execute("ALTER TABLE streak_records RENAME INDEX idx_streak_date TO idx_date")
    op.execute("ALTER TABLE streak_records RENAME INDEX idx_streak_user TO idx_user")
    op.execute(
        "ALTER TABLE knowledge_stats RENAME INDEX idx_knowledge_user_exam TO idx_user_exam"
    )
    op.execute(
        "ALTER TABLE knowledge_stats "
        "RENAME INDEX uk_user_exam_point TO uk_user_exam_knowledge"
    )
    op.drop_index("idx_wrongbook_question", table_name="wrong_book")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_wrongbook_last_wrong TO idx_last_wrong")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_wrongbook_mastered TO idx_mastered")
    op.execute("ALTER TABLE wrong_book RENAME INDEX idx_wrongbook_user TO idx_user")
    op.execute("ALTER TABLE papers RENAME INDEX idx_papers_strategy TO idx_strategy")
    op.execute("ALTER TABLE papers RENAME INDEX idx_papers_exam_type TO idx_exam_type")
    op.execute("ALTER TABLE papers RENAME INDEX idx_papers_user TO idx_user")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_wrong_rate TO idx_wrong_rate")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_type TO idx_type")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_difficulty TO idx_difficulty")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_knowledge TO idx_knowledge")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_subject TO idx_subject")
    op.execute("ALTER TABLE questions RENAME INDEX idx_questions_exam_type TO idx_exam_type")
    op.execute("ALTER TABLE users RENAME INDEX idx_users_created TO idx_created")
    op.execute("ALTER TABLE users RENAME INDEX idx_users_openid TO idx_openid")
