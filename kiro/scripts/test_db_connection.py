"""
测试数据库连接
帮助诊断连接问题
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def test_connection():
    """测试数据库连接"""
    
    # 从环境变量读取
    db_url = os.getenv("DATABASE_URL", "")
    print(f"📝 数据库 URL: {db_url}")
    
    # 尝试不同的连接方式
    test_configs = [
        {
            "user": "postgres",
            "password": "password",
            "database": "zen_bazi",
            "host": "localhost",
            "port": 5432
        },
        {
            "user": "postgres",
            "password": "",  # 空密码
            "database": "zen_bazi",
            "host": "localhost",
            "port": 5432
        },
        {
            "user": "postgres",
            "password": "postgres",  # 默认密码
            "database": "zen_bazi",
            "host": "localhost",
            "port": 5432
        },
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n🔍 测试配置 {i}:")
        print(f"   用户: {config['user']}")
        print(f"   密码: {'(空)' if not config['password'] else '***'}")
        print(f"   数据库: {config['database']}")
        print(f"   主机: {config['host']}")
        print(f"   端口: {config['port']}")
        
        try:
            conn = await asyncpg.connect(**config)
            print(f"   ✅ 连接成功！")
            
            # 测试查询
            version = await conn.fetchval('SELECT version()')
            print(f"   📊 PostgreSQL 版本: {version[:50]}...")
            
            # 列出所有数据库
            databases = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false")
            print(f"   📁 可用数据库:")
            for db in databases:
                print(f"      - {db['datname']}")
            
            await conn.close()
            
            # 生成正确的连接字符串
            password_part = f":{config['password']}" if config['password'] else ""
            correct_url = f"postgresql+asyncpg://{config['user']}{password_part}@{config['host']}:{config['port']}/{config['database']}"
            print(f"\n   ✨ 请将以下内容复制到 .env 文件:")
            print(f"   DATABASE_URL={correct_url}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
    
    print("\n\n💡 建议:")
    print("1. 确认 PostgreSQL 服务正在运行")
    print("2. 检查 PostgreSQL 的 pg_hba.conf 配置")
    print("3. 确认数据库 'zen_bazi' 已创建")
    print("4. 尝试使用 psql 命令行工具连接:")
    print("   psql -U postgres -d zen_bazi")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_connection())
