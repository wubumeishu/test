"""
Redis 连接配置
用于存储验证码等临时数据
"""
import os
from typing import Optional
import redis.asyncio as redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Redis 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis 客户端实例
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    获取 Redis 客户端实例（依赖注入）
    
    使用示例:
        @app.get("/test")
        async def test(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")
            value = await redis.get("key")
            return {"value": value}
    """
    global redis_client
    
    if redis_client is None:
        redis_client = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return redis_client


async def init_redis():
    """
    初始化 Redis 连接
    在应用启动时调用
    """
    global redis_client
    
    try:
        redis_client = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # 测试连接
        await redis_client.ping()
        print("✅ Redis 连接成功")
    except Exception as e:
        print(f"⚠️ Redis 连接失败: {e}")
        print("   验证码功能将不可用")
        redis_client = None


async def close_redis():
    """
    关闭 Redis 连接
    在应用关闭时调用
    """
    global redis_client
    
    if redis_client:
        await redis_client.close()
        print("✅ Redis 连接已关闭")
