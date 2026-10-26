import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations

from src.modules.content import service
from src.modules.content.models import ContentItem


def migration(db_session):
    path = Path(__file__).resolve().parents[1] / "alembic/versions/0009_release_1_5_2_announcement.py"
    spec = importlib.util.spec_from_file_location("release_152_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.op = Operations(MigrationContext.configure(db_session.connection()))
    return module


def test_migration_adds_approved_public_announcement_once_and_keeps_old_draft(db_session):
    old = ContentItem(category="notice", title="旧版草稿", summary="原摘要", body="原正文",
                      release_version="1.5.1", is_active=0)
    db_session.add(old)
    db_session.flush()
    release = migration(db_session)
    release.upgrade()
    release.upgrade()
    page = service.list_announcements(db_session, page=1, page_size=20)
    assert page["total"] == 1
    announcement = service.get_announcement(db_session, page["items"][0]["id"])
    assert announcement["title"] == "1.5.2 更新公告"
    assert announcement["summary"] == "更新了中英双语选择。"
    assert announcement["body"] == (
        "1. 新增语言设置\n"
        "在“我的 → 语言 / Language”中，可切换简体中文与 English，系统会记住你的选择。\n\n"
        "2. 常用界面支持双语\n"
        "首页、刷题、AI问答、我的，以及导航、按钮和操作提示，随语言设置同步切换。\n\n"
        "3. AI 回答跟随界面语言\n"
        "英文界面下，AI 默认使用英语讲解；你也可以直接指定希望使用的语言。"
    )
    assert announcement["release_version"] == "1.5.2"
    assert announcement["is_active"] is True
    assert announcement["published_at"] is not None
    db_session.refresh(old)
    assert (old.body, old.is_active, old.published_at) == ("原正文", 0, None)
    release.downgrade()
    assert db_session.query(ContentItem).count() == 2


def test_existing_release_record_is_not_overwritten_or_republished(db_session):
    existing = ContentItem(category="notice", title="运营者草稿", summary="摘要", body="保留人工编辑",
                           release_version="1.5.2", is_active=0)
    db_session.add(existing)
    db_session.flush()
    migration(db_session).upgrade()
    db_session.refresh(existing)
    assert db_session.query(ContentItem).count() == 1
    assert (existing.title, existing.body, existing.is_active, existing.published_at) == (
        "运营者草稿", "保留人工编辑", 0, None,
    )
    assert service.list_announcements(db_session, page=1, page_size=20)["total"] == 0
