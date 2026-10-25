from datetime import date, datetime, timedelta, timezone
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy import create_engine, inspect, text

from src.app import create_app
from src.common.auth import create_token
from src.common.exceptions import AppException
from src.common.time import study_day_utc_bounds, utc_now_naive
from src.config.database import get_db
from src.config.settings import settings
from src.modules.content import service as content_service
from src.modules.content.models import ContentItem
from src.modules.content.schemas import ContentItemCreate, ContentItemUpdate
from src.modules.feedback import service
from src.modules.feedback.models import Feedback
from src.modules.feedback.schemas import FeedbackCreate
from src.modules.user.models import User


@pytest.fixture
def support_client(db_session, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(settings, "CONTENT_ADMIN_OPENIDS", "owner,dev-openid")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "offline-tests-only-secret-with-32-characters")
    db_session.add_all([User(openid="learner"), User(openid="other")])
    db_session.commit()
    app = create_app()

    def override_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client


def auth(openid="learner"):
    return {"Authorization": f"Bearer {create_token(openid)}"}


def feedback_payload(**overrides):
    return {"request_id": "feedback-test-001", "category": "bug", "content": "听力播放出现了问题，请帮忙检查。", "app_version": "1.5.1", **overrides}


def test_feedback_is_private_and_admin_access_requires_a_real_token(support_client, db_session):
    client = support_client
    assert client.post("/api/v1/feedback", json=feedback_payload()).status_code == 401
    assert client.get("/api/v1/feedback/admin").status_code == 401
    assert client.get("/api/v1/content/list").status_code == 401
    created = client.post("/api/v1/feedback", json=feedback_payload(), headers=auth())
    assert created.status_code == 200
    receipt = created.json()["data"]
    assert set(receipt) == {"id", "status", "created_at"}
    assert client.get("/api/v1/feedback/admin", headers=auth()).status_code == 403
    assert client.get("/api/v1/feedback/admin", headers=auth("another-user")).status_code == 403
    assert client.put(f"/api/v1/feedback/admin/{receipt['id']}/status", json={"status": "resolved"}, headers=auth()).status_code == 403
    listed = client.get("/api/v1/feedback/admin", headers=auth("owner")).json()["data"]
    assert listed["total"] == 1
    assert listed["items"][0]["content"] == feedback_payload()["content"]
    updated = client.put(f"/api/v1/feedback/admin/{receipt['id']}/status", json={"status": "read"}, headers=auth("owner"))
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "read"
    assert client.get("/api/v1/feedback/admin?status=unread", headers=auth("owner")).json()["data"]["total"] == 0
    assert db_session.query(Feedback).count() == 1


def test_feedback_retries_are_idempotent_and_do_not_consume_frequency_quota(support_client, db_session):
    client = support_client
    first = client.post("/api/v1/feedback", json=feedback_payload(), headers=auth())
    again = client.post("/api/v1/feedback", json=feedback_payload(), headers=auth())
    assert first.json()["data"] == again.json()["data"]
    assert db_session.query(Feedback).count() == 1
    changed = client.post("/api/v1/feedback", json=feedback_payload(content="不同内容"), headers=auth())
    assert changed.status_code == 409
    frequent = client.post("/api/v1/feedback", json=feedback_payload(request_id="feedback-test-002"), headers=auth())
    assert frequent.status_code == 429
    other = client.post("/api/v1/feedback", json=feedback_payload(), headers=auth("other"))
    assert other.status_code == 200


def test_feedback_rejects_stale_tokens_without_creating_an_account(support_client, db_session):
    response = support_client.post("/api/v1/feedback", json=feedback_payload(), headers=auth("deleted-user"))
    assert response.status_code == 401
    assert db_session.query(User).filter_by(openid="deleted-user").count() == 0


@pytest.mark.parametrize("change", [{"content": "  \n "}, {"content": "字" * 1001}, {"category": "invalid"}, {"user_id": 999}, {"request_id": "bad"}])
def test_feedback_validates_text_type_and_owner_cannot_be_spoofed(support_client, change):
    response = support_client.post("/api/v1/feedback", json=feedback_payload(**change), headers=auth())
    assert response.status_code == 422


def test_feedback_daily_limit_uses_the_beijing_day(db_session, monkeypatch):
    now = datetime(2026, 10, 25, 12)
    bounds = study_day_utc_bounds(date(2026, 10, 25))
    monkeypatch.setattr(service, "utc_now_naive", lambda: now)
    monkeypatch.setattr(service, "study_day_utc_bounds", lambda: bounds)
    user = User(openid="daily-feedback-user")
    db_session.add(user)
    db_session.flush()
    for index in range(20):
        db_session.add(Feedback(user_id=user.id, request_id=f"daily-{index:04}", category="other", content="意见", app_version="1.5.1", created_at=now - timedelta(minutes=5)))
    db_session.commit()
    with pytest.raises(AppException) as error:
        service.submit_feedback(db_session, user.id, FeedbackCreate(**feedback_payload()))
    assert error.value.code == 42962


def make_content(db_session, **overrides):
    item = ContentItem(category="notice", title="版本更新", summary="更新摘要", body="第一项\n第二项",
                       release_version="1.5.1", is_active=1,
                       published_at=utc_now_naive() - timedelta(days=1))
    for name, value in overrides.items():
        setattr(item, name, value)
    db_session.add(item)
    db_session.commit()
    return item


def test_only_published_updates_are_visible_from_list_or_detail_routes(support_client, db_session):
    published = make_content(db_session)
    draft = make_content(db_session, is_active=0)
    future = make_content(db_session, published_at=utc_now_naive() + timedelta(days=1))
    regular = make_content(db_session, release_version=None, category="consulting")
    result = support_client.get("/api/v1/content/announcements").json()["data"]
    assert result["total"] == 1
    assert result["items"][0]["id"] == published.id
    assert result["items"][0]["published_at"].endswith("Z")
    assert support_client.get(f"/api/v1/content/announcements/{published.id}").status_code == 200
    for hidden in (draft, future):
        assert support_client.get(f"/api/v1/content/announcements/{hidden.id}").status_code == 404
        assert support_client.get(f"/api/v1/content/{hidden.id}").status_code == 404
    assert support_client.get(f"/api/v1/content/announcements/{regular.id}").status_code == 404
    home = support_client.get("/api/v1/content/home").json()["data"]
    assert [item["id"] for item in home] == [regular.id]
    assert support_client.get("/api/v1/content/announcements?page_size=101").status_code == 422


def test_empty_content_reads_do_not_create_demo_data(support_client, db_session):
    assert support_client.get("/api/v1/content/home").json()["data"] == []
    assert support_client.get("/api/v1/content/list", headers=auth("owner")).json()["data"] == []
    assert db_session.query(ContentItem).count() == 0


def test_admin_can_publish_and_withdraw_an_update_without_exposing_drafts(support_client, db_session):
    draft = make_content(db_session, is_active=0, published_at=None)
    url = f"/api/v1/content/{draft.id}"
    assert support_client.put(url, json={"is_active": True}, headers=auth()).status_code == 403
    published = support_client.put(url, json={"is_active": True}, headers=auth("owner"))
    assert published.status_code == 200
    assert published.json()["data"]["published_at"]
    assert support_client.get("/api/v1/content/announcements").json()["data"]["total"] == 1
    assert support_client.put(url, json={"is_active": False}, headers=auth("owner")).status_code == 200
    assert support_client.get(f"/api/v1/content/announcements/{draft.id}").status_code == 404


def test_publication_timezone_is_normalized_and_invalid_updates_are_rejected(db_session):
    created = content_service.save_content(db_session, ContentItemCreate(
        category="notice", title="更新", summary="摘要", body="正文", release_version="1.5.1",
        published_at=datetime(2026, 10, 25, 20, tzinfo=timezone(timedelta(hours=8))),
    ))
    assert created["published_at"] == datetime(2026, 10, 25, 12, tzinfo=timezone.utc)
    with pytest.raises(AppException):
        content_service.save_content(db_session, ContentItemUpdate(title=None), created["id"])
    with pytest.raises(ValidationError):
        ContentItemCreate(category="notice", title="  ", summary="摘要", body="正文")


def test_incremental_migration_preserves_existing_users_and_content():
    path = Path(__file__).resolve().parents[1] / "alembic/versions/0008_feedback_announcements.py"
    spec = importlib.util.spec_from_file_location("feedback_migration_test", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users VALUES (7)"))
        connection.execute(text("CREATE TABLE content_items (id INTEGER PRIMARY KEY, category VARCHAR(20), title VARCHAR(128), summary VARCHAR(255), body TEXT, is_active INTEGER, sort_order INTEGER, created_at DATETIME, updated_at DATETIME)"))
        connection.execute(text("INSERT INTO content_items (id, title, body, is_active) VALUES (5, '原有内容', '保留正文', 1)"))
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        assert connection.execute(text("SELECT id FROM users")).scalar_one() == 7
        assert connection.execute(text("SELECT body FROM content_items WHERE id=5")).scalar_one() == "保留正文"
        draft = connection.execute(text("SELECT is_active, published_at FROM content_items WHERE release_version='1.5.1'")).one()
        assert tuple(draft) == (0, None)
        assert "feedback" in inspect(connection).get_table_names()
        assert inspect(connection).get_foreign_keys("feedback")[0]["name"] == "fk_feedback_user"
