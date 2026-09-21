"""Read-only database integrity and schema-constraint checks."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = PROJECT_ROOT / "server"

CHECKS = {
    "duplicate_answer_keys": """
        SELECT COUNT(*) FROM (
            SELECT 1 FROM answer_records
            GROUP BY user_id, paper_id, question_id
            HAVING COUNT(*) > 1
        ) AS duplicates
    """,
    "orphan_papers_user": """
        SELECT COUNT(*) FROM papers p
        LEFT JOIN users u ON u.id = p.user_id
        WHERE u.id IS NULL
    """,
    "orphan_answers_user": """
        SELECT COUNT(*) FROM answer_records a
        LEFT JOIN users u ON u.id = a.user_id
        WHERE u.id IS NULL
    """,
    "orphan_answers_paper": """
        SELECT COUNT(*) FROM answer_records a
        LEFT JOIN papers p ON p.id = a.paper_id
        WHERE p.id IS NULL
    """,
    "orphan_answers_question": """
        SELECT COUNT(*) FROM answer_records a
        LEFT JOIN questions q ON q.id = a.question_id
        WHERE q.id IS NULL
    """,
    "orphan_wrongbook_user": """
        SELECT COUNT(*) FROM wrong_book w
        LEFT JOIN users u ON u.id = w.user_id
        WHERE u.id IS NULL
    """,
    "orphan_wrongbook_question": """
        SELECT COUNT(*) FROM wrong_book w
        LEFT JOIN questions q ON q.id = w.question_id
        WHERE q.id IS NULL
    """,
    "orphan_knowledge_user": """
        SELECT COUNT(*) FROM knowledge_stats k
        LEFT JOIN users u ON u.id = k.user_id
        WHERE u.id IS NULL
    """,
    "orphan_streak_user": """
        SELECT COUNT(*) FROM streak_records s
        LEFT JOIN users u ON u.id = s.user_id
        WHERE u.id IS NULL
    """,
    "orphan_favorites_user": """
        SELECT COUNT(*) FROM favorites f
        LEFT JOIN users u ON u.id = f.user_id
        WHERE u.id IS NULL
    """,
    "orphan_favorites_question": """
        SELECT COUNT(*) FROM favorites f
        LEFT JOIN questions q ON q.id = f.question_id
        WHERE q.id IS NULL
    """,
    "orphan_user_targets_user": """
        SELECT COUNT(*) FROM user_exam_targets t
        LEFT JOIN users u ON u.id = t.user_id
        WHERE u.id IS NULL
    """,
    "answer_paper_owner_mismatch": """
        SELECT COUNT(*) FROM answer_records a
        INNER JOIN papers p ON p.id = a.paper_id
        WHERE a.user_id <> p.user_id
    """,
    "orphan_paper_question_json": """
        SELECT COUNT(*)
        FROM papers p
        JOIN JSON_TABLE(
            p.question_ids,
            '$[*]' COLUMNS(question_id INT PATH '$')
        ) AS paper_question
        LEFT JOIN questions q ON q.id = paper_question.question_id
        WHERE q.id IS NULL
    """,
}

EXPECTED_FOREIGN_KEYS = {
    "fk_papers_user",
    "fk_answer_records_user",
    "fk_answer_records_paper",
    "fk_answer_records_question",
    "fk_wrong_book_user",
    "fk_wrong_book_question",
    "fk_knowledge_stats_user",
    "fk_streak_records_user",
    "fk_favorites_user",
    "fk_favorites_question",
    "fk_user_exam_targets_user",
}


def main() -> int:
    original_cwd = Path.cwd()
    sys.path.insert(0, str(SERVER_ROOT))
    os.chdir(SERVER_ROOT)
    try:
        from src.config.settings import settings

        url = (
            "mysql+pymysql://"
            f"{quote_plus(settings.MYSQL_USER)}:{quote_plus(settings.MYSQL_PASSWORD)}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as connection:
            tables = set(inspect(connection).get_table_names())
            required = {
                "users",
                "questions",
                "papers",
                "answer_records",
                "wrong_book",
                "knowledge_stats",
                "streak_records",
                "favorites",
                "user_exam_targets",
                "content_items",
            }
            missing = sorted(required - tables)
            if missing:
                print(f"missing_tables={','.join(missing)}")
                return 1

            question_count = connection.execute(text("SELECT COUNT(*) FROM questions")).scalar_one()
            print(f"questions={question_count}")
            if "alembic_version" in tables:
                version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                print(f"alembic_version={version}")
            else:
                print("alembic_version=unversioned")

            issues = 0
            for name, statement in CHECKS.items():
                count = connection.execute(text(statement)).scalar_one()
                print(f"{name}={count}")
                issues += count

            inspector = inspect(connection)
            actual_foreign_keys = {
                foreign_key["name"]
                for table_name in required
                for foreign_key in inspector.get_foreign_keys(table_name)
                if foreign_key.get("name")
            }
            missing_foreign_keys = sorted(EXPECTED_FOREIGN_KEYS - actual_foreign_keys)
            print(
                "missing_foreign_keys="
                + (",".join(missing_foreign_keys) if missing_foreign_keys else "0")
            )
            issues += len(missing_foreign_keys)
            print("integrity=clean" if issues == 0 else f"integrity=failed issues={issues}")
            return 0 if issues == 0 else 1
    except SQLAlchemyError as exc:
        print(f"database_check_failed={exc.__class__.__name__}")
        return 2
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    raise SystemExit(main())
