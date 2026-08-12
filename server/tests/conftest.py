"""pytest 配置和 fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from main import app
from src.config.database import Base

# Import models so SQLAlchemy registers every table used by service tests.
from src.modules.exam.models import AnswerRecord  # noqa: F401
from src.modules.question.models import Paper, Question  # noqa: F401
from src.modules.user.models import StreakRecord, User  # noqa: F401
from src.modules.wrongbook.models import KnowledgeStat, WrongBook  # noqa: F401


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def register_sqlite_rand(dbapi_connection, connection_record):
        dbapi_connection.create_function("rand", 0, lambda: 0.5)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
