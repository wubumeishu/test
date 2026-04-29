"""
PostgreSQL 连接测试脚本
用于验证数据库连接是否正常
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def test_connection(password: str):
    """测试 PostgreSQL 连接"""
    database_url = f"postgresql+asyncpg://postgres:{password}@localhost:5432/zen_bazi"
    
    print(f"🔍 正在测试连接: {database_url.replace(password, '***')}")
    
    try:
        # 创建引擎
        engine = create_async_engine(database_url, echo=False)
        
        # 测试连接
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ 连接成功！")
            print(f"📊 PostgreSQL 版本: {version}")
            
            # 检查数据库是否存在
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"📁 当前数据库: {db_name}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python test_pg_connection.py <你的PostgreSQL密码>")
        print("例如: python test_pg_connection.py mypassword")
        sys.exit(1)
    
    password = sys.argv[1]
    success = asyncio.run(test_connection(password))
    
    if success:
        print("\n✅ 数据库连接测试通过！")
        print("📝 请更新 .env 文件中的 DATABASE_URL")
    else:
        print("\n❌ 数据库连接测试失败，请检查：")
        print("1. PostgreSQL 服务是否正在运行")
        print("2. 密码是否正确")
        print("3. zen_bazi 数据库是否已创建")
        print("4. PostgreSQL 是否监听 5432 端口")
