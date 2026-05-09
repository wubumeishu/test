"""phase1_user_model_v3

将 User 表从 v2 升级到 v3.0：
  - 重命名 wechat_unionid → wechat_openid
  - 新增 is_vip (Boolean, default=False)
  - 新增 vip_expires_at (DateTime, nullable)

Revision ID: a1b2c3d4e5f6
Revises: db64401f3b36
Create Date: 2026-05-09

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "db64401f3b36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 重命名 wechat_unionid → wechat_openid
    #    先删除旧索引，再重命名列，再重建索引
    op.drop_index("ix_users_wechat_unionid", table_name="users", if_exists=True)
    op.alter_column(
        "users",
        "wechat_unionid",
        new_column_name="wechat_openid",
        existing_type=sa.String(100),
        existing_nullable=True,
        comment="微信小程序 OpenID，系统绝对信任的唯一标识",
    )
    op.create_index("ix_users_wechat_openid", "users", ["wechat_openid"], unique=True)

    # 2. 新增 is_vip 字段
    op.add_column(
        "users",
        sa.Column(
            "is_vip",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="是否为 VIP 用户",
        ),
    )

    # 3. 新增 vip_expires_at 字段
    op.add_column(
        "users",
        sa.Column(
            "vip_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="VIP 到期时间，NULL 表示非 VIP 或永久 VIP",
        ),
    )


def downgrade() -> None:
    # 回滚：删除新增字段，重命名回 wechat_unionid
    op.drop_column("users", "vip_expires_at")
    op.drop_column("users", "is_vip")

    op.drop_index("ix_users_wechat_openid", table_name="users", if_exists=True)
    op.alter_column(
        "users",
        "wechat_openid",
        new_column_name="wechat_unionid",
        existing_type=sa.String(100),
        existing_nullable=True,
        comment="微信 UnionID",
    )
    op.create_index("ix_users_wechat_unionid", "users", ["wechat_unionid"], unique=True)
