from io import BytesIO
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from PIL import Image
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from main import app
from src.common.auth import create_token
from src.config.database import get_db
from src.config.settings import settings
from src.modules.user.models import User, UserCodeCounter
from src.modules.user import router, service


@pytest.fixture
def api(client, db_session, monkeypatch, tmp_path):
    app.dependency_overrides[get_db] = lambda: db_session
    monkeypatch.setattr(router, "SessionLocal", sessionmaker(bind=db_session.get_bind()))
    monkeypatch.setattr(settings, "USER_AVATAR_ROOT", str(tmp_path / "avatars"))
    monkeypatch.setattr(settings, "AUTH_ALLOW_DEV_OPENID", True)
    async def exchange(code):
        return "wx-" + code
    monkeypatch.setattr(router, "exchange_wx_code", exchange)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def headers(openid):
    return {"Authorization": "Bearer " + create_token(openid)}


def test_guest_cannot_use_private_routes_or_create_users(api, db_session):
    for url in ("/user/info", "/user/dashboard", "/question/papers", "/favorite/list"):
        assert api.get("/api/v1" + url).status_code == 401
    assert api.get("/api/v1/content/announcements").status_code == 200
    assert api.post("/api/v1/ai/chat", json={}).status_code == 404
    assert db_session.query(User).count() == 0


def test_explicit_login_reuses_account_and_learning_counters(api, db_session):
    first = api.post("/api/v1/user/wx-login", json={"code": "same", "nickname": "小明"}).json()["data"]
    assert first["user"]["user_code"] == "lw001"
    user = db_session.get(User, first["user"]["id"])
    user.total_questions = 17
    db_session.commit()
    again = api.post("/api/v1/user/wx-login", json={"code": "same"}).json()["data"]
    assert (again["user"]["id"], again["user"]["user_code"], again["user"]["total_questions"]) == (user.id, "lw001", 17)
    assert db_session.query(User).count() == 1
    assert db_session.query(User).filter(User.user_code == "lw000").count() == 0


def test_deleted_account_token_does_not_recreate_user(api, db_session):
    assert api.get("/api/v1/user/info", headers=headers("deleted")).status_code == 401
    assert db_session.query(User).count() == 0


@pytest.mark.asyncio
async def test_production_never_falls_back_to_dev_identity(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "AUTH_ALLOW_DEV_OPENID", True)
    monkeypatch.setattr(settings, "WX_APPID", "")
    monkeypatch.setattr(settings, "WX_SECRET", "")
    with pytest.raises(service.AppException) as error:
        await service.exchange_wx_code("unconfigured")
    assert error.value.status_code == 503


def test_numbers_are_unique_monotonic_and_can_grow_past_999(db_session):
    first = service.get_or_create_user_by_openid(db_session, "a")
    second = service.get_or_create_user_by_openid(db_session, "b")
    assert (first.user_code, second.user_code) == ("lw001", "lw002")
    db_session.delete(second)
    db_session.commit()
    assert service.get_or_create_user_by_openid(db_session, "c").user_code == "lw003"
    db_session.get(UserCodeCounter, 1).next_value = 1000
    db_session.commit()
    assert service.get_or_create_user_by_openid(db_session, "d").user_code == "lw1000"
    db_session.add(User(openid="duplicate", user_code="lw001"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_profile_identity_is_server_controlled_and_nickname_is_saved(api, db_session):
    user = service.get_or_create_user_by_openid(db_session, "profile")
    auth = headers(user.openid)
    for payload in ({"user_code": "lw000"}, {"openid": "someone-else"}, {"nickname": " "}):
        assert api.put("/api/v1/user/profile", json=payload, headers=auth).status_code == 422
    updated = api.put("/api/v1/user/profile", json={"nickname": "新昵称"}, headers=auth)
    assert updated.status_code == 200
    assert api.get("/api/v1/user/info", headers=auth).json()["data"]["nickname"] == "新昵称"
    assert api.put("/api/v1/user/profile", json={"avatar_url": "wxfile://temporary"}, headers=auth).status_code == 422


def test_avatar_is_authenticated_validated_and_persisted_as_safe_jpeg(api, db_session):
    user = service.get_or_create_user_by_openid(db_session, "avatar")
    auth = headers(user.openid)
    image = BytesIO()
    Image.new("RGBA", (700, 400), (255, 0, 0, 128)).save(image, format="PNG")
    file = {"file": ("avatar.png", image.getvalue(), "image/png")}
    assert api.post("/api/v1/user/avatar", files=file).status_code == 401
    assert api.post("/api/v1/user/avatar", files={"file": ("bad.png", b"invalid", "image/png")}, headers=auth).status_code == 422
    assert api.post("/api/v1/user/avatar", files={"file": ("big.jpg", b"x" * (2 * 1024 * 1024 + 1))}, headers=auth).status_code == 413
    response = api.post("/api/v1/user/avatar", files=file, headers=auth)
    assert response.status_code == 200
    url = response.json()["data"]["avatar_url"]
    saved = api.get(url)
    assert saved.status_code == 200 and saved.headers["content-type"] == "image/jpeg"
    with Image.open(BytesIO(saved.content)) as result:
        assert result.format == "JPEG" and max(result.size) <= 512
    assert api.get("/api/v1/user/info", headers=auth).json()["data"]["avatar_url"] == url
    assert api.get("/api/v1/user/avatar/invalid.jpg").status_code == 404


def load_script(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_binding_previews_and_never_overwrites_another_owner(db_session):
    script = load_script(Path(__file__).resolve().parents[2] / "scripts/assign_owner_code.py", "owner_code")
    user = service.get_or_create_user_by_openid(db_session, "owner")
    assert script.assign_owner_code(db_session, user.id)["applied"] is False
    assert user.user_code == "lw001"
    script.assign_owner_code(db_session, user.id, apply=True)
    assert user.user_code == "lw000"
    other = service.get_or_create_user_by_openid(db_session, "other")
    with pytest.raises(ValueError):
        script.assign_owner_code(db_session, other.id, apply=True)
    assert other.user_code == "lw002"


def test_migration_preserves_existing_ids_records_and_publishes_exact_notice():
    # 在独立 SQLite 中模拟 0011 之前的表结构。
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY, nickname TEXT)"))
        connection.execute(sa.text("INSERT INTO users VALUES (1, '甲'), (1000, '乙')"))
        connection.execute(sa.text("CREATE TABLE learning (user_id INTEGER REFERENCES users(id), answer TEXT)"))
        connection.execute(sa.text("INSERT INTO learning VALUES (1000, '中文作答')"))
        from src.modules.content.models import ContentItem
        ContentItem.__table__.create(connection)
        migration = load_script(Path(__file__).resolve().parents[1] / "alembic/versions/0011_login_strategy.py", "login_migration")
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        assert connection.execute(sa.text("SELECT id, user_code FROM users ORDER BY id")).all() == [(1, "lw001"), (1000, "lw1000")]
        assert connection.execute(sa.text("SELECT * FROM learning")).one() == (1000, "中文作答")
        assert connection.execute(sa.text("SELECT next_value FROM user_code_counters")).scalar_one() == 1001
        notice = connection.execute(sa.text("SELECT summary, body, is_active FROM content_items WHERE release_version='1.5.4'")).one()
        assert notice == ("优化登录策略", "优化登录策略", 1)
    engine.dispose()
