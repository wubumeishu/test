"""
档案模型
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Integer, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, TimestampMixin


class Archive(Base, TimestampMixin):
    """
    档案表
    存储用户创建的八字档案信息
    """
    __tablename__ = "archives"
    
    archive_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="档案ID (UUID)"
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID (外键)"
    )
    
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="姓名"
    )
    
    gender: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="性别 (1=男, 0=女)"
    )
    
    calendar_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="solar",
        comment="历法类型 (solar=公历, lunar=农历)"
    )
    
    birth_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="出生年份"
    )
    
    birth_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="出生月份"
    )
    
    birth_day: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="出生日期"
    )
    
    birth_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="出生小时"
    )
    
    birth_minute: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="出生分钟"
    )
    
    tags: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="标签 (逗号分隔)"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为默认档案"
    )
    
    # 核心同步字段
    local_created_at: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="本地创建时间戳 (毫秒)"
    )
    
    cloud_uploaded_at: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="云端上传时间戳 (毫秒)"
    )
    
    # 关联关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="archives"
    )
    
    records: Mapped[list["Record"]] = relationship(
        "Record",
        back_populates="archive",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Archive(archive_id={self.archive_id}, name={self.name}, gender={self.gender})>"
