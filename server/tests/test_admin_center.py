"""Targeted authorization, metrics, bootstrap and migration checks in isolated SQLite."""
from datetime import timedelta
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from main import app
from src.common.auth import create_token
from src.common.time import study_day_utc_bounds, utc_now_naive
from src.config.database import get_db
from src.config.settings import settings
from src.modules.admin.models import AdminAudit, AdminMember, AdminOwner
from src.modules.admin.service import bootstrap_owner
from src.modules.content.models import ContentItem
from src.modules.exam.models import AnswerRecord
from src.modules.feedback.models import Feedback
from src.modules.question.models import Paper, Question
from src.modules.user.models import User


@pytest.fixture
def admin_env(db_session, client, monkeypatch):
    people = {role: User(openid=role, nickname=role) for role in ("owner", "viewer", "learner", "outsider")}
    db_session.add_all(people.values())
    db_session.flush()
    db_session.add(AdminOwner(id=1, user_id=people["owner"].id))
    db_session.add(AdminMember(user_id=people["viewer"].id, granted_by=people["owner"].id))
    feedback = Feedback(user_id=people["learner"].id, request_id="admin-test-feedback", category="bug", content="保留原文的反馈", app_version="1.5.4")
    content = ContentItem(category="notice", title="草稿", summary="摘要", body="未发布全文", is_active=0)
    db_session.add_all([feedback, content])
    db_session.commit()
    # Legacy allowlist must grant no access, even to a real logged-in user.
    monkeypatch.setattr(settings, "CONTENT_ADMIN_OPENIDS", "outsider")
    def database():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise
    app.dependency_overrides[get_db] = database
    try:
        yield client, db_session, people, feedback, content
    finally:
        app.dependency_overrides.clear()


def auth(role):
    return {"Authorization": "Bearer " + create_token(role)}


def test_guest_ordinary_and_legacy_allowlisted_users_cannot_read_management_data(admin_env):
    client, db, people, feedback, content = admin_env
    for url in ("/admin/overview", "/admin/users", "/feedback/admin", "/content/list", "/admin/members"):
        assert client.get("/api/v1" + url).status_code == 401
        for role in ("learner", "outsider"):
            assert client.get("/api/v1" + url, headers=auth(role)).status_code == 403
    assert client.get(f"/api/v1/content/{content.id}").status_code == 404
    assert client.get("/api/v1/user/info", headers=auth("outsider")).json()["data"]["admin_role"] == "user"


def test_viewer_reads_feedback_full_text_without_marking_it_read(admin_env):
    client, db, people, feedback, content = admin_env
    for url in ("/admin/overview", "/admin/users", "/content/list"):
        assert client.get("/api/v1" + url, headers=auth("viewer")).status_code == 200
    listing = client.get("/api/v1/feedback/admin", headers=auth("viewer")).json()["data"]
    assert listing["items"][0]["content"] == "保留原文的反馈"
    assert listing["items"][0]["user_code"] == people["learner"].user_code
    assert listing["items"][0]["status"] == "unread"
    assert "openid" not in listing["items"][0]
    assert db.query(AdminAudit).count() == 0


def test_viewer_is_denied_every_management_write_and_member_lookup(admin_env):
    client, db, people, feedback, content = admin_env
    writes = [("POST", "/admin/members", {"user_code": people["learner"].user_code}),
              ("DELETE", f"/admin/members/{people['viewer'].id}", None),
              ("POST", "/content", {"category": "notice", "title": "test", "summary": "test", "body": "test"}),
              ("PUT", f"/content/{content.id}", {"is_active": True}),
              ("DELETE", f"/content/{content.id}", None),
              ("PUT", f"/feedback/admin/{feedback.id}/status", {"status": "read"})]
    for method, url, payload in writes:
        assert client.request(method, "/api/v1" + url, json=payload, headers=auth("viewer")).status_code == 403
    assert client.get("/api/v1/admin/members", headers=auth("viewer")).status_code == 403
    assert client.get("/api/v1/admin/members/lookup", params={"user_code": people["learner"].user_code}, headers=auth("viewer")).status_code == 403
    db.refresh(content)
    db.refresh(feedback)
    assert content.is_active == 0 and feedback.status == "unread"
    assert db.query(AdminAudit).count() == 0


def test_owner_grants_unilaterally_and_revocation_invalidates_the_same_token(admin_env):
    client, db, people, feedback, content = admin_env
    code = people["learner"].user_code
    preview = client.get("/api/v1/admin/members/lookup", params={"user_code": code}, headers=auth("owner"))
    assert preview.json()["data"]["nickname"] == "learner"
    for _ in range(2):
        assert client.post("/api/v1/admin/members", json={"user_code": code}, headers=auth("owner")).status_code == 200
    assert db.query(AdminAudit).filter_by(action="admin.grant").count() == 1
    token = auth("learner")
    assert client.get("/api/v1/user/info", headers=token).json()["data"]["admin_role"] == "viewer"
    assert client.get("/api/v1/feedback/admin", headers=token).status_code == 200
    assert client.delete(f"/api/v1/admin/members/{people['learner'].id}", headers=auth("owner")).status_code == 200
    assert client.get("/api/v1/admin/overview", headers=token).status_code == 403
    assert client.get("/api/v1/user/info", headers=token).json()["data"]["admin_role"] == "user"
    assert client.delete(f"/api/v1/admin/members/{people['owner'].id}", headers=auth("owner")).status_code == 409
    assert client.post("/api/v1/admin/members", json={"user_code": code, "role": "owner"}, headers=auth("owner")).status_code == 422
    assert client.put("/api/v1/user/profile", json={"admin_role": "owner"}, headers=token).status_code == 422


def test_owner_content_and_feedback_changes_are_audited_atomically(admin_env):
    client, db, people, feedback, content = admin_env
    assert client.put(f"/api/v1/content/{content.id}", json={"is_active": True}, headers=auth("owner")).status_code == 200
    assert client.put(f"/api/v1/feedback/admin/{feedback.id}/status", json={"status": "resolved"}, headers=auth("owner")).status_code == 200
    assert client.delete(f"/api/v1/content/{content.id}", headers=auth("owner")).status_code == 200
    actions = {item.action for item in db.query(AdminAudit).all()}
    assert actions == {"content.update", "feedback.status", "content.delete"}
    assert all(item.actor_user_id == people["owner"].id for item in db.query(AdminAudit).all())


def test_overview_counts_distinct_learners_in_beijing_day_and_user_search_is_bounded(admin_env):
    client, db, people, feedback, content = admin_env
    start, end = study_day_utc_bounds()
    for user in people.values():
        user.created_at = start - timedelta(seconds=1)
    people["learner"].created_at = start
    question = Question(exam_type="CSCA", subject="数学", knowledge_point="函数", difficulty="easy", question_type="single", stem_text="test", answer="A", options=[{"key": "A", "text": "test"}])
    db.add(question)
    db.flush()
    for index, created in enumerate((start, start + timedelta(seconds=1), end)):
        paper = Paper(user_id=people["learner"].id, title="test", exam_type="CSCA", strategy="random", question_ids=[question.id])
        db.add(paper)
        db.flush()
        db.add(AnswerRecord(user_id=people["learner"].id, paper_id=paper.id, question_id=question.id, created_at=created))
    db.commit()
    values = client.get("/api/v1/admin/overview", headers=auth("viewer")).json()["data"]
    assert (values["new_users_today"], values["answering_users_today"], values["total_answers"]) == (1, 1, 3)
    page = client.get("/api/v1/admin/users", params={"search": people["learner"].user_code}, headers=auth("viewer")).json()["data"]
    assert page["total"] == 1 and page["items"][0]["last_study_at"]
    assert "openid" not in page["items"][0]
    assert client.get("/api/v1/admin/users?page_size=101", headers=auth("viewer")).status_code == 422


def test_owner_bootstrap_is_preview_only_until_verified_and_cannot_create_two_owners(db_session):
    user, other = User(openid="real-owner"), User(openid="other")
    db_session.add_all([user, other])
    db_session.commit()
    original = user.user_code
    result = bootstrap_owner(db_session, original)
    assert result["applied"] is False and user.user_code == original
    assert db_session.query(AdminOwner).count() == 0
    with pytest.raises(ValueError):
        bootstrap_owner(db_session, original, apply=True, expected_user_id=999)
    bootstrap_owner(db_session, original, apply=True, expected_user_id=user.id)
    assert user.user_code == "lw000"
    assert db_session.get(AdminOwner, 1).user_id == user.id
    assert db_session.query(AdminAudit).filter_by(action="owner.bootstrap").count() == 1
    with pytest.raises(ValueError):
        bootstrap_owner(db_session, other.user_code, apply=True, expected_user_id=other.id)
    db_session.add(AdminOwner(id=2, user_id=other.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_reserved_display_code_alone_does_not_grant_management_access(client, db_session):
    user = User(openid="number-only", user_code="lw000")
    db_session.add(user)
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        response = client.get("/api/v1/user/info", headers=auth("number-only"))
        assert response.json()["data"]["admin_role"] == "user"
        assert client.get("/api/v1/admin/overview", headers=auth("number-only")).status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_temporary_owner_lw005_keeps_code_and_requires_explicit_apply(client, db_session):
    user = User(id=5, openid="dev-owner", user_code="lw005")
    db_session.add(user)
    db_session.commit()
    preview = bootstrap_owner(db_session, "lw005", temporary=True)
    assert preview["new_code"] == "lw005" and preview["temporary"] is True
    assert db_session.query(AdminOwner).count() == 0
    bootstrap_owner(db_session, "lw005", temporary=True, apply=True, expected_user_id=user.id)
    assert user.user_code == "lw005"
    assert db_session.get(AdminOwner, 1).is_temporary is True
    assert db_session.query(User).filter_by(user_code="lw000").count() == 0
    assert db_session.query(AdminAudit).filter_by(action="owner.bootstrap_trial").count() == 1
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        assert client.get("/api/v1/user/info", headers=auth("dev-owner")).json()["data"]["admin_role"] == "owner"
        assert client.get("/api/v1/admin/overview", headers=auth("dev-owner")).status_code == 200
    finally:
        app.dependency_overrides.clear()
    with pytest.raises(ValueError):
        bootstrap_owner(db_session, "lw005", apply=True, expected_user_id=user.id)


def test_temporary_owner_does_not_claim_or_overwrite_reserved_lw000(db_session):
    reserved = User(openid="reserved-real-owner", user_code="lw000")
    trial = User(openid="trial", user_code="lw005")
    db_session.add_all([reserved, trial])
    db_session.commit()
    bootstrap_owner(db_session, "lw005", temporary=True, apply=True, expected_user_id=trial.id)
    assert reserved.user_code == "lw000" and trial.user_code == "lw005"
    assert db_session.get(AdminOwner, 1).user_id == trial.id
    with pytest.raises(ValueError):
        bootstrap_owner(db_session, "lw000", apply=True, expected_user_id=reserved.id)


def test_migration_retains_users_assigns_no_permissions_and_leaves_notice_unpublished():
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        User.__table__.create(connection)
        ContentItem.__table__.create(connection)
        connection.execute(sa.text("INSERT INTO users (id, openid, user_code) VALUES (7, 'existing', 'lw007')"))
        path = Path(__file__).resolve().parents[1] / "alembic/versions/0012_admin_center.py"
        spec = importlib.util.spec_from_file_location("admin_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        assert connection.execute(sa.text("SELECT user_code FROM users WHERE id=7")).scalar_one() == "lw007"
        for table in ("admin_owner", "admin_members", "admin_audit_logs"):
            assert connection.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar_one() == 0
        assert connection.execute(sa.text("SELECT is_active, published_at FROM content_items WHERE release_version='1.5.5'")).one() == (0, None)
    engine.dispose()


def test_trial_owner_marker_migration_preserves_an_existing_owner():
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE admin_owner (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL)"))
        connection.execute(sa.text("INSERT INTO admin_owner VALUES (1, 5)"))
        path = Path(__file__).resolve().parents[1] / "alembic/versions/0013_trial_admin_owner.py"
        spec = importlib.util.spec_from_file_location("trial_owner_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        assert connection.execute(sa.text("SELECT id, user_id, is_temporary FROM admin_owner")).one() == (1, 5, 0)
    engine.dispose()
