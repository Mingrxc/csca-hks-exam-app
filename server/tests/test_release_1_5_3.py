import importlib.util
from datetime import timedelta
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations

from src.common.time import utc_now_naive
from src.modules.content import service
from src.modules.content.models import ContentItem


def migration(db_session):
    path = Path(__file__).resolve().parents[1] / "alembic/versions/0010_release_1_5_3_announcement.py"
    spec = importlib.util.spec_from_file_location("release_153_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.op = Operations(MigrationContext.configure(db_session.connection()))
    return module


def test_ai_endpoint_is_unavailable_and_other_routes_remain_registered(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert not any(path.startswith("/api/v1/ai") for path in paths)
    assert "/api/v1/exam/submit" in paths
    assert "/api/v1/content/announcements" in paths
    assert client.post("/api/v1/ai/chat", json={"messages": [{"role": "user", "content": "test"}]}).status_code == 404
    assert client.get("/api/v1/health").json()["version"] == "1.5.3"


def test_approved_announcement_is_public_once_and_keeps_previous_release(db_session):
    previous = ContentItem(category="notice", title="1.5.2 更新公告", summary="原摘要", body="历史内容保留",
                           release_version="1.5.2", is_active=1,
                           published_at=utc_now_naive() - timedelta(days=1))
    db_session.add(previous)
    db_session.flush()
    release = migration(db_session)
    release.upgrade()
    release.upgrade()
    page = service.list_announcements(db_session, page=1, page_size=20)
    assert page["total"] == 2
    announcement = service.get_announcement(db_session, page["items"][0]["id"])
    assert announcement["release_version"] == "1.5.3"
    assert announcement["title"] == "1.5.3 更新公告"
    assert announcement["summary"] == announcement["body"] == "撤销AI功能"
    assert announcement["is_active"] is True
    db_session.refresh(previous)
    assert previous.body == "历史内容保留"
    release.downgrade()
    assert db_session.query(ContentItem).count() == 2


def test_existing_same_version_draft_is_not_republished(db_session):
    draft = ContentItem(category="notice", title="运营者编辑", summary="摘要", body="保留内容",
                        release_version="1.5.3", is_active=0)
    db_session.add(draft)
    db_session.flush()
    migration(db_session).upgrade()
    db_session.refresh(draft)
    assert db_session.query(ContentItem).count() == 1
    assert (draft.body, draft.is_active, draft.published_at) == ("保留内容", 0, None)
