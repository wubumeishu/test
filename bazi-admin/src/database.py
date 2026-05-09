"""
数据库连接配置
使用 SQLAlchemy 异步引擎连接 PostgreSQL
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/bazi_db"
)

# 创建异步引擎
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发环境下打印 SQL 语句
    future=True,
    poolclass=NullPool,  # 使用 NullPool 避免连接池问题
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖注入
    用于 FastAPI 的 Depends
    
    使用示例：
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表，并确保 Mock 用户存在
    """
    from src.models.base import Base
    # 导入所有模型以确保它们被注册
    from src.models import User, Archive, Record
    from sqlalchemy import select, text
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功")

    # 确保 Mock 用户存在（外键约束要求 users 表中必须有此记录）
    MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.user_id == MOCK_USER_ID)
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                mock_user = User(
                    user_id=MOCK_USER_ID,
                    nickname="默认用户",
                    phone=None,
                    wechat_openid=None,
                    avatar_url=None,
                )
                session.add(mock_user)
                await session.commit()
                print(f"✅ Mock 用户已创建: {MOCK_USER_ID}")
            else:
                print(f"ℹ️ Mock 用户已存在: {MOCK_USER_ID}")
        except Exception as e:
            await session.rollback()
            print(f"⚠️ Mock 用户创建失败（可能已存在）: {e}")


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
    print("✅ 数据库连接已关闭")
