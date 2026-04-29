"""
删除所有数据库表
用于重新创建表结构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent / "bazi-admin"
sys.path.insert(0, str(project_root))

from src.database import engine, close_db
from sqlalchemy import text


async def drop_all_tables():
    """删除所有表"""
    print("=" * 60)
    print("⚠️  警告: 即将删除所有数据库表!")
    print("=" * 60)
    
    try:
        async with engine.connect() as conn:
            # 删除表 (按依赖顺序)
            print("\n🗑️  删除表...")
            
            await conn.execute(text("DROP TABLE IF EXISTS records CASCADE;"))
            print("   ✅ 已删除 records 表")
            
            await conn.execute(text("DROP TABLE IF EXISTS archives CASCADE;"))
            print("   ✅ 已删除 archives 表")
            
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            print("   ✅ 已删除 users 表")
            
            await conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ 所有表已删除!")
        print("=" * 60)
        print("\n💡 提示: 现在可以运行 test_models.py 重新创建表")
        
    except Exception as e:
        print(f"\n❌ 删除失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(drop_all_tables())
