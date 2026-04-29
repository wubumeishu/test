"""
测算记录模型
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base, TimestampMixin


class Record(Base, TimestampMixin):
    """
    测算记录表
    存储用户的八字测算结果和 AI 分析报告
    """
    __tablename__ = "records"
    
    record_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="记录ID (UUID)"
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID (外键)"
    )
    
    archive_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("archives.archive_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="档案ID (外键)"
    )
    
    bazi_str: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="八字字符串 (例: 甲子 乙丑 丙寅 丁卯)"
    )
    
    five_elements_json: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="五行分析 JSON 数据"
    )
    
    ai_report_markdown: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="AI 分析报告 (Markdown 格式)"
    )
    
    is_deep_analysis: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为深度分析"
    )
    
    # 关联关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="records"
    )
    
    archive: Mapped["Archive"] = relationship(
        "Archive",
        back_populates="records"
    )
    
    def __repr__(self) -> str:
        return f"<Record(record_id={self.record_id}, bazi_str={self.bazi_str}, is_deep={self.is_deep_analysis})>"
