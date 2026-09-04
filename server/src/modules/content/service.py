"""首页内容业务逻辑."""

from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.modules.content.models import ContentItem
from src.modules.content.schemas import ContentItemCreate, ContentItemUpdate

DEFAULT_CONTENTS = [
    {
        "category": "consulting",
        "title": "香港院校申请时间线更新",
        "summary": "本周补录、面试和奖学金节点整理，先看申请截止日期，再确认材料清单。",
        "body": "整理了最近一周的留学申请节点和材料提醒，适合在刷题间隙快速查看。",
        "sort_order": 40,
        "is_active": True,
    },
    {
        "category": "club",
        "title": "留学生学联招新",
        "summary": "新学期社团开始招募志愿者，适合想认识同校同学的你。",
        "body": "社团活动覆盖学习互助、语言交换和升学经验分享，可按兴趣报名。",
        "sort_order": 35,
        "is_active": True,
    },
    {
        "category": "ad",
        "title": "DYH 备考资料包",
        "summary": "题型速记、错题模板和冲刺计划示例，先占位，后续可在线替换内容。",
        "body": "这是一个可在线维护的占位内容，后续可以在内容管理页直接改成正式广告或合作资料。",
        "sort_order": 30,
        "is_active": True,
    },
    {
        "category": "notice",
        "title": "模拟考试周提醒",
        "summary": "建议每周至少完整做一套模拟卷，保留 20 分钟复盘错题。",
        "body": "固定周末进行模拟考试，能更快看出时间分配和薄弱知识点。",
        "sort_order": 20,
        "is_active": True,
    },
]


def ensure_default_contents(db: Session) -> None:
    if db.query(ContentItem).count():
        return
    for item in DEFAULT_CONTENTS:
        db.add(ContentItem(**item))
    db.commit()


def list_home_contents(db: Session) -> list[dict]:
    ensure_default_contents(db)
    items = (
        db.query(ContentItem)
        .filter(ContentItem.is_active == 1)
        .order_by(ContentItem.sort_order.desc(), ContentItem.id.desc())
        .all()
    )
    return [serialize_content(item) for item in items]


def list_content_admin(db: Session) -> list[dict]:
    ensure_default_contents(db)
    items = db.query(ContentItem).order_by(ContentItem.sort_order.desc(), ContentItem.id.desc()).all()
    return [serialize_content(item) for item in items]


def get_content(db: Session, content_id: int) -> dict:
    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise AppException(40441, "内容不存在", status_code=404)
    return serialize_content(item)


def save_content(db: Session, payload: ContentItemCreate | ContentItemUpdate, content_id: int | None = None) -> dict:
    values = payload.model_dump(exclude_unset=True)
    if content_id is None:
        item = ContentItem(**values)
        db.add(item)
        db.commit()
        db.refresh(item)
        return serialize_content(item)

    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise AppException(40441, "内容不存在", status_code=404)
    for key, value in values.items():
        setattr(item, key, value)
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
        "sort_order": item.sort_order,
        "is_active": bool(item.is_active),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }

