from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, false
from sqlalchemy.sql import func
from src.config.database import Base


class AdminOwner(Base):
    __tablename__ = "admin_owner"
    __table_args__ = (CheckConstraint("id = 1", name="ck_admin_owner_singleton"),
                      UniqueConstraint("user_id", name="uk_admin_owner_user"))
    id = Column(Integer, primary_key=True, autoincrement=False)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_admin_owner_user", ondelete="RESTRICT"), nullable=False)
    is_temporary = Column(Boolean, nullable=False, default=False, server_default=false())
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class AdminMember(Base):
    __tablename__ = "admin_members"
    user_id = Column(Integer, ForeignKey("users.id", name="fk_admin_member_user", ondelete="CASCADE"), primary_key=True, autoincrement=False)
    granted_by = Column(Integer, ForeignKey("users.id", name="fk_admin_member_grantor", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class AdminAudit(Base):
    __tablename__ = "admin_audit_logs"
    __table_args__ = (Index("idx_admin_audit_created", "created_at"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", name="fk_admin_audit_actor", ondelete="SET NULL"), nullable=True)
    actor_code = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id", name="fk_admin_audit_target", ondelete="SET NULL"), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
