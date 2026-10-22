"""Generate the SQL schema reference from application models without DB access."""
from pathlib import Path
import os
import sys
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateIndex, CreateTable

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "server"))
os.chdir(PROJECT / "server")
from src.config.database import Base
from src.app import create_app
create_app()

statements = ["-- Generated from SQLAlchemy models. Initialize using Alembic upgrade head.",
              "-- This reference contains no credentials or business data.",
              "CREATE DATABASE IF NOT EXISTS csca_hks_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
              "USE csca_hks_exam;"]
for table in Base.metadata.sorted_tables:
    statements.append(str(CreateTable(table).compile(dialect=mysql.dialect())).strip() + ";")
    for index in sorted(table.indexes, key=lambda value: value.name):
        statements.append(str(CreateIndex(index).compile(dialect=mysql.dialect())) + ";")
target = PROJECT / "database" / "schema.sql"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(line.rstrip() for line in "\n\n".join(statements).splitlines()) + "\n", encoding="utf-8")
print("Schema reference exported: database/schema.sql")
