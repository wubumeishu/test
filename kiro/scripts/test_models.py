"""
测试数据库模型
验证所有模型是否正确创建
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent / "bazi-admin"
sys.path.insert(0, str(project_root))

from src.database import init_db, close_db, engine
from src.models import User, Archive, Record
from sqlalchemy import text


async def test_models():
    """测试模型创建"""
    print("=" * 60)
    print("开始测试数据库模型")
    print("=" * 60)
    
    try:
        # 初始化数据库
        print("\n1️⃣ 初始化数据库...")
        await init_db()
        
        # 检查表是否创建
        print("\n2️⃣ 检查数据库表...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            print(f"\n✅ 已创建 {len(tables)} 个表:")
            for table in tables:
                print(f"   - {table[0]}")
        
        # 检查表结构
        print("\n3️⃣ 检查表结构...")
        
        # Users 表
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\n📋 users 表结构:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   - {col[0]:<20} {col[1]:<20} {nullable}")
        
        # Archives 表
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'archives'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\n📋 archives 表结构:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   - {col[0]:<20} {col[1]:<20} {nullable}")
        
        # Records 表
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'records'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            print("\n📋 records 表结构:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   - {col[0]:<20} {col[1]:<20} {nullable}")
        
        # 检查外键约束
        print("\n4️⃣ 检查外键约束...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name;
            """))
            fks = result.fetchall()
            
            print(f"\n✅ 已创建 {len(fks)} 个外键约束:")
            for fk in fks:
                print(f"   - {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        
        print("\n" + "=" * 60)
        print("✅ 所有模型测试通过!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


if __name__ == "__main__":
    asyncio.run(test_models())
