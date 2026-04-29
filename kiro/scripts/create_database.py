"""
创建 zen_bazi 数据库
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """创建数据库"""
    
    # 连接配置（尝试不同的密码）
    configs = [
        {"user": "postgres", "password": "password", "host": "localhost", "port": 5432},
        {"user": "postgres", "password": "", "host": "localhost", "port": 5432},
        {"user": "postgres", "password": "postgres", "host": "localhost", "port": 5432},
        {"user": "postgres", "password": "admin", "host": "localhost", "port": 5432},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n🔍 尝试配置 {i}:")
        print(f"   用户: {config['user']}")
        print(f"   密码: {'(空)' if not config['password'] else '***'}")
        
        try:
            # 连接到默认的 postgres 数据库
            conn = psycopg2.connect(
                dbname="postgres",
                **config
            )
            
            # 设置自动提交模式
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            print(f"   ✅ 连接成功！")
            
            # 创建游标
            cursor = conn.cursor()
            
            # 检查数据库是否已存在
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'zen_bazi'")
            exists = cursor.fetchone()
            
            if exists:
                print(f"   ℹ️  数据库 'zen_bazi' 已存在")
            else:
                # 创建数据库
                cursor.execute("CREATE DATABASE zen_bazi")
                print(f"   ✅ 数据库 'zen_bazi' 创建成功！")
            
            # 列出所有数据库
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
            databases = cursor.fetchall()
            print(f"\n   📁 当前所有数据库:")
            for db in databases:
                marker = " ✨" if db[0] == "zen_bazi" else ""
                print(f"      - {db[0]}{marker}")
            
            # 关闭连接
            cursor.close()
            conn.close()
            
            # 生成正确的连接字符串
            password_part = f":{config['password']}" if config['password'] else ""
            correct_url = f"postgresql+asyncpg://{config['user']}{password_part}@{config['host']}:{config['port']}/zen_bazi"
            
            print(f"\n   ✨ 请将以下内容更新到 .env 文件:")
            print(f"   DATABASE_URL={correct_url}")
            
            return True
            
        except psycopg2.OperationalError as e:
            print(f"   ❌ 连接失败: {e}")
            continue
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            continue
    
    print("\n\n❌ 所有配置都失败了")
    print("\n💡 请手动创建数据库:")
    print("1. 打开 pgAdmin 或 SQL Shell (psql)")
    print("2. 连接到 PostgreSQL")
    print("3. 执行命令: CREATE DATABASE zen_bazi;")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 创建 zen_bazi 数据库")
    print("=" * 60)
    
    success = create_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 数据库创建完成！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 更新 .env 文件中的 DATABASE_URL")
        print("2. 启动服务: uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
    else:
        print("\n" + "=" * 60)
        print("❌ 数据库创建失败")
        print("=" * 60)
