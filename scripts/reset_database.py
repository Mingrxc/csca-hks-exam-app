"""Rebuild the configured development database after a verified SQL backup.

Default is a read-only plan. Production execution requires --allow-remote and an
explicit --expected-database. No database account or server settings are changed.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
SERVER = PROJECT / "server"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-database", default="csca_hks_exam")
    parser.add_argument("--allow-remote", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(SERVER))
    sys.path.insert(0, str(PROJECT / "scripts"))
    os.chdir(SERVER)
    from src.config.settings import settings
    from import_questions import load_questions, upsert_questions, DEFAULT_SOURCE
    questions, report = load_questions(DEFAULT_SOURCE)
    if report.invalid or not questions or not all(q.bank_id for q in questions):
        raise RuntimeError("Source validation failed; database was not changed")
    if settings.MYSQL_DATABASE != args.expected_database:
        raise RuntimeError("Database name does not match --expected-database")
    if settings.MYSQL_HOST not in {"localhost", "127.0.0.1", "::1"} and not args.allow_remote:
        raise RuntimeError("Remote rebuild requires --allow-remote")
    print(json.dumps({"host": settings.MYSQL_HOST, "database": settings.MYSQL_DATABASE,
                      "questions": len(questions), "mode": "backup_and_rebuild" if args.apply else "plan_only"}))
    if not args.apply:
        return
    dump = shutil.which("mysqldump")
    if not dump:
        candidate = Path(r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe")
        if candidate.is_file():
            dump = str(candidate)
    if not dump:
        raise RuntimeError("Existing mysqldump is required for backup; no changes made")
    destination = PROJECT / "database" / "backups"
    destination.mkdir(parents=True, exist_ok=True)
    backup = destination / f"before-bank-v2-{datetime.now():%Y%m%d-%H%M%S}.sql"
    env = dict(os.environ, MYSQL_PWD=settings.MYSQL_PASSWORD)
    result = subprocess.run([dump, "--host", settings.MYSQL_HOST, "--port", str(settings.MYSQL_PORT),
                             "--user", settings.MYSQL_USER, "--single-transaction", "--no-tablespaces",
                             "--set-gtid-purged=OFF", "--default-character-set=utf8mb4",
                             f"--result-file={backup}", settings.MYSQL_DATABASE],
                            env=env, capture_output=True)
    if result.returncode or not backup.is_file() or backup.stat().st_size < 100:
        raise RuntimeError("SQL backup failed; database was not changed")
    checksum = hashlib.sha256(backup.read_bytes()).hexdigest()
    backup.with_suffix(".sha256").write_text(checksum + "  " + backup.name + "\n", encoding="ascii")
    from src.config.database import Base, sync_engine
    from src.app import create_app
    create_app()  # Register all application models before dropping their tables.
    from sqlalchemy import text
    from alembic import command
    from alembic.config import Config
    Base.metadata.drop_all(sync_engine)
    with sync_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    command.upgrade(Config(str(SERVER / "alembic.ini")), "head")
    inserted, updated = upsert_questions(questions)
    print(json.dumps({"backup": str(backup), "sha256": checksum, "inserted": inserted, "updated": updated,
                      "alembic_head": "0007_question_bank_v2"}))


if __name__ == "__main__":
    main()
