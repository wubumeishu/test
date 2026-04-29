"""
数据库配置向导
交互式配置 PostgreSQL 连接
"""
import asyncio
import os
from getpass import getpass
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def test_connection(password: str) -> bool:
    """测试 PostgreSQL 连接"""
    database_url = f"postgresql+asyncpg://postgres:{password}@localhost:5432/zen_bazi"
    
    try:
        engine = create_async_engine(database_url, echo=False)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def update_env_file(password: str):
    """更新 .env 文件"""
    env_path = ".env"
    
    # 新的配置内容
    new_content = f"""# 数据库配置
# 
# PostgreSQL 配置（生产环境推荐）
DATABASE_URL=postgresql+asyncpg://postgres:{password}@localhost:5432/zen_bazi

# SQLite 配置（开发测试备用）
# DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db

# 服务器配置
HOST=127.0.0.1
PORT=9000

# 环境
ENVIRONMENT=development
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


async def main():
    """主函数"""
    print("=" * 60)
    print("🗄️  PostgreSQL 数据库配置向导")
    print("=" * 60)
    print()
    
    print("📋 前提条件检查：")
    print("  ✓ PostgreSQL 已安装")
    print("  ✓ PostgreSQL 服务正在运行")
    print("  ✓ 已创建 zen_bazi 数据库")
    print()
    
    # 获取密码
    print("🔐 请输入 PostgreSQL 的 postgres 用户密码：")
    password = getpass("密码: ")
    
    if not password:
        print("❌ 密码不能为空")
        return
    
    print()
    print("🔍 正在测试数据库连接...")
    
    # 测试连接
    success = await test_connection(password)
    
    if not success:
        print()
        print("❌ 数据库连接失败，请检查：")
        print("  1. PostgreSQL 服务是否正在运行")
        print("  2. 密码是否正确")
        print("  3. zen_bazi 数据库是否已创建")
        print("  4. PostgreSQL 是否监听 5432 端口")
        print()
        print("💡 提示：可以参考 SETUP_POSTGRESQL.md 文档")
        return
    
    print("✅ 数据库连接成功！")
    print()
    
    # 更新配置文件
    print("📝 正在更新 .env 配置文件...")
    update_env_file(password)
    print("✅ 配置文件已更新")
    print()
    
    print("=" * 60)
    print("🎉 配置完成！")
    print("=" * 60)
    print()
    print("📌 下一步：")
    print("  1. 运行服务：uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
    print("  2. 访问文档：http://127.0.0.1:9000/docs")
    print("  3. 健康检查：http://127.0.0.1:9000/api/health")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 配置已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
