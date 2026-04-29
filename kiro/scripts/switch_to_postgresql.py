"""
切换到 PostgreSQL 数据库配置
"""
import os
import sys


def update_env_file(password: str):
    """更新 .env 文件，切换到 PostgreSQL"""
    env_path = ".env"
    
    # 读取当前配置
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    new_lines = []
    for line in lines:
        if line.strip().startswith("DATABASE_URL=sqlite"):
            # 注释掉 SQLite 配置
            new_lines.append(f"# {line}")
        elif line.strip().startswith("# DATABASE_URL=postgresql"):
            # 启用 PostgreSQL 配置
            new_lines.append(f"DATABASE_URL=postgresql+asyncpg://postgres:{password}@localhost:5432/zen_bazi\n")
        else:
            new_lines.append(line)
    
    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ .env 文件已更新")
    print(f"📝 DATABASE_URL=postgresql+asyncpg://postgres:***@localhost:5432/zen_bazi")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python switch_to_postgresql.py <你的PostgreSQL密码>")
        print("例如: python switch_to_postgresql.py mypassword")
        sys.exit(1)
    
    password = sys.argv[1]
    
    print("🔄 正在切换到 PostgreSQL 配置...")
    update_env_file(password)
    print("\n✅ 配置切换完成！")
    print("📌 下一步：运行 'python main.py' 启动服务")
