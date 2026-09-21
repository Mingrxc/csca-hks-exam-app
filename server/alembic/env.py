"""Alembic migration environment."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.config.database import Base, sync_url

# Register all tables on Base.metadata before Alembic compares schemas.
from src.modules.content.models import ContentItem  # noqa: F401
from src.modules.favorite.models import Favorite  # noqa: F401
from src.modules.exam.models import AnswerRecord  # noqa: F401
from src.modules.question.models import Paper, Question  # noqa: F401
from src.modules.user.models import StreakRecord, User, UserExamTarget  # noqa: F401
from src.modules.wrongbook.models import KnowledgeStat, WrongBook  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
config.set_main_option(
    "sqlalchemy.url",
    sync_url.render_as_string(hide_password=False).replace("%", "%%"),
)


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
