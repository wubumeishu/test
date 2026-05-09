"""
用户模型 (v3.0)

账号体系设计原则：
- wechat_openid 是系统绝对信任的唯一标识（微信小程序内不变）
- phone 是跨端账号合并的基准，由用户在系统内主动绑定并验证
- 系统绝不信任微信 getPhoneNumber 接口返回的动态手机号
"""
from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    用户表 (v3.0)

    登录方式：
      1. 微信静默登录：code → OpenID → 静默注册，无需手机号
      2. 手机号+短信验证码：登录或注册，可与微信账号合并
      3. 手机号+密码：兼容旧版登录方式

    账号合并规则：
      - 若用户先微信登录（phone=NULL），后在设置页绑定手机号 → 直接写入 phone
      - 若用户先短信登录，后点微信一键登录：
          后端检查该 OpenID 对应的手机号是否与已有账号的 phone 一致
          → 一致：merge，将 wechat_openid 写入已有账号，不新建记录
          → 不一致：提示用户确认
    """
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="用户ID (UUID)"
    )

    # ── 登录凭证 ──────────────────────────────────────────────
    wechat_openid: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="微信小程序 OpenID，系统绝对信任的唯一标识"
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
        comment="手机号，用户在系统内主动绑定并验证，跨端账号合并基准"
    )

    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="bcrypt 哈希密码，passlib[bcrypt] 加密，禁止明文存储"
    )

    # ── 用户资料 ──────────────────────────────────────────────
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称，默认随机禅意名称，如「听风客_9527」"
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="头像 URL，默认系统内置东方美学头像"
    )

    # ── VIP 状态 ──────────────────────────────────────────────
    is_vip: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为 VIP 用户"
    )

    vip_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="VIP 到期时间，NULL 表示非 VIP 或永久 VIP"
    )

    # ── 登录记录 ──────────────────────────────────────────────
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )

    # ── 关联关系 ──────────────────────────────────────────────
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
        return f"<User(user_id={self.user_id}, nickname={self.nickname}, phone={self.phone})>"
