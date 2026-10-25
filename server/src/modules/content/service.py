"""首页内容业务逻辑."""

from datetime import timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import utc_now_naive
from src.modules.content.models import ContentItem
from src.modules.content.schemas import ContentItemCreate, ContentItemUpdate

def published_query(db: Session):
    return db.query(ContentItem).filter(
        ContentItem.is_active == 1,
        or_(ContentItem.published_at.is_(None), ContentItem.published_at <= utc_now_naive()),
    )


def announcement_query(db: Session):
    return published_query(db).filter(
        ContentItem.category == "notice", ContentItem.release_version.is_not(None),
        ContentItem.published_at.is_not(None),
    )


def list_announcements(db: Session, *, page: int, page_size: int) -> dict:
    query = announcement_query(db)
    total = query.count()
    items = query.order_by(ContentItem.published_at.desc(), ContentItem.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [serialize_content(item) for item in items], "total": total,
            "page": page, "page_size": page_size}


def get_announcement(db: Session, content_id: int) -> dict:
    item = announcement_query(db).filter(ContentItem.id == content_id).first()
    if not item:
        raise AppException(40441, "公告不存在或尚未发布", status_code=404)
    return serialize_content(item)


def list_home_contents(db: Session) -> list[dict]:
    items = (
        published_query(db)
        .filter(ContentItem.release_version.is_(None))
        .order_by(ContentItem.sort_order.desc(), ContentItem.id.desc())
        .all()
    )
    return [serialize_content(item) for item in items]


def list_content_admin(db: Session) -> list[dict]:
    items = db.query(ContentItem).order_by(ContentItem.sort_order.desc(), ContentItem.id.desc()).all()
    return [serialize_content(item) for item in items]


def get_content(db: Session, content_id: int) -> dict:
    item = published_query(db).filter(ContentItem.id == content_id).first()
    if not item:
        raise AppException(40441, "内容不存在", status_code=404)
    return serialize_content(item)


def save_content(db: Session, payload: ContentItemCreate | ContentItemUpdate, content_id: int | None = None) -> dict:
    values = payload.model_dump(exclude_unset=True)
    for field in ("category", "title", "summary", "body", "sort_order", "is_active"):
        if field in values and values[field] is None:
            raise AppException(42241, "内容必填字段不能为空", status_code=422)
    if content_id is None:
        item = ContentItem(**values)
        db.add(item)
    else:
        item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
        if not item:
            raise AppException(40441, "内容不存在", status_code=404)
        for key, value in values.items():
            setattr(item, key, value)
    if item.release_version and item.category != "notice":
        raise AppException(42242, "更新公告请选择通知分类", status_code=422)
    if item.published_at and item.published_at.tzinfo:
        item.published_at = item.published_at.astimezone(timezone.utc).replace(tzinfo=None)
    if item.is_active and not item.published_at:
        item.published_at = utc_now_naive()
    db.commit()
    db.refresh(item)
    return serialize_content(item)


def delete_content(db: Session, content_id: int) -> dict:
    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise AppException(40441, "内容不存在", status_code=404)
    db.delete(item)
    db.commit()
    return {"id": content_id, "deleted": True}


def serialize_content(item: ContentItem) -> dict:
    return {
        "id": item.id,
        "category": item.category,
        "title": item.title,
        "summary": item.summary,
        "body": item.body,
        "cover_image": item.cover_image,
        "link_url": item.link_url,
        "release_version": item.release_version,
        "published_at": item.published_at.replace(tzinfo=timezone.utc) if item.published_at else None,
        "sort_order": item.sort_order,
        "is_active": bool(item.is_active),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }

