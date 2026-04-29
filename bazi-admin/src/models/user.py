"""
用户模型
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    用户表
    存储用户基本信息和第三方登录凭证
    """
    __tablename__ = "users"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="用户ID (UUID)"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
        comment="手机号"
    )
    
    wechat_unionid: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="微信 UnionID"
    )
    
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称"
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="头像 URL"
    )
    
    # 关联关系
    archives: Mapped[list["Archive"]] = relationship(
        "Archive",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    records: Mapped[list["Record"]] = relationship(
        "Record",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, nickname={self.nickname})>"
