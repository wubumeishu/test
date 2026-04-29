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
    创建所有表
    """
    from src.models.base import Base
    # 导入所有模型以确保它们被注册
    from src.models import User, Archive, Record
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功")


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
    print("✅ 数据库连接已关闭")
