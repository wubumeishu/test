"""
测试 PostgreSQL 连接（使用正确的端口 5433）
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def test_connection():
    """测试连接"""
    database_url = "postgresql+asyncpg://postgres:123456@localhost:5433/zen_bazi"
    
    print("=" * 70)
    print("🔌 测试 PostgreSQL 连接")
    print("=" * 70)
    print()
    print(f"📍 连接地址: postgresql://postgres:***@localhost:5433/zen_bazi")
    print()
    
    try:
        print("🔍 正在连接...")
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.connect() as conn:
            # 测试查询
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            print("✅ 连接成功！")
            print()
            print("📊 数据库信息:")
            print(f"   版本: {version}")
            print()
            
            # 检查当前数据库
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"   当前数据库: {db_name}")
            print()
            
            # 检查表
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"   已有表: {len(tables)} 个")
                for table in tables:
                    print(f"      - {table[0]}")
            else:
                print("   已有表: 0 个（数据库为空）")
            print()
        
        await engine.dispose()
        
        print("=" * 70)
        print("🎉 配置成功！")
        print("=" * 70)
        print()
        print("📌 下一步:")
        print("   1. 启动服务: uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
        print("   2. 访问文档: http://127.0.0.1:9000/docs")
        print("   3. 健康检查: http://127.0.0.1:9000/api/health")
        print()
        
        return True
        
    except Exception as e:
        print("❌ 连接失败")
        print()
        print(f"错误信息: {e}")
        print()
        print("=" * 70)
        print("🔧 故障排查")
        print("=" * 70)
        print()
        print("请检查:")
        print("   1. PostgreSQL 服务是否正在运行")
        print("   2. 密码是否正确 (当前使用: 123456)")
        print("   3. zen_bazi 数据库是否已创建")
        print("   4. 端口是否正确 (当前使用: 5433)")
        print()
        
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
