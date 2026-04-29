"""
PostgreSQL 连接问题诊断和修复指南
"""
import os
import subprocess
import sys


def find_postgresql_data_dir():
    """查找 PostgreSQL 数据目录"""
    common_paths = [
        r"C:\Program Files\PostgreSQL\16\data",
        r"C:\Program Files\PostgreSQL\15\data",
        r"C:\Program Files\PostgreSQL\14\data",
        r"C:\Program Files\PostgreSQL\13\data",
        r"C:\PostgreSQL\data",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None


def check_postgresql_service():
    """检查 PostgreSQL 服务状态"""
    try:
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-16'],
            capture_output=True,
            text=True
        )
        if 'RUNNING' in result.stdout:
            return True, "PostgreSQL 服务正在运行"
        else:
            return False, "PostgreSQL 服务未运行"
    except Exception as e:
        return False, f"无法检查服务状态: {e}"


def check_port_listening():
    """检查 5432 端口是否在监听"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        if ':5432' in result.stdout:
            return True, "端口 5432 正在监听"
        else:
            return False, "端口 5432 未监听"
    except Exception as e:
        return False, f"无法检查端口: {e}"


def main():
    print("=" * 70)
    print("🔍 PostgreSQL 连接问题诊断")
    print("=" * 70)
    print()
    
    # 检查 1: 服务状态
    print("📋 检查 1: PostgreSQL 服务状态")
    running, msg = check_postgresql_service()
    print(f"   {'✅' if running else '❌'} {msg}")
    print()
    
    # 检查 2: 端口监听
    print("📋 检查 2: 端口 5432 监听状态")
    listening, msg = check_port_listening()
    print(f"   {'✅' if listening else '❌'} {msg}")
    print()
    
    # 检查 3: 数据目录
    print("📋 检查 3: PostgreSQL 数据目录")
    data_dir = find_postgresql_data_dir()
    if data_dir:
        print(f"   ✅ 找到数据目录: {data_dir}")
        pg_hba = os.path.join(data_dir, "pg_hba.conf")
        postgresql_conf = os.path.join(data_dir, "postgresql.conf")
        
        if os.path.exists(pg_hba):
            print(f"   ✅ pg_hba.conf 存在")
        if os.path.exists(postgresql_conf):
            print(f"   ✅ postgresql.conf 存在")
    else:
        print(f"   ❌ 未找到数据目录")
    print()
    
    # 诊断结果
    print("=" * 70)
    print("📊 诊断结果")
    print("=" * 70)
    print()
    
    if not listening:
        print("❌ 问题：PostgreSQL 没有监听 TCP 端口 5432")
        print()
        print("🔧 解决方案：")
        print()
        print("方案 1：使用 SQLite（推荐，最简单）")
        print("-" * 70)
        print("SQLite 是一个轻量级数据库，无需配置即可使用。")
        print("当前项目已经配置好 SQLite，只需保持 .env 文件不变即可。")
        print()
        print("优点：")
        print("  ✓ 无需配置，开箱即用")
        print("  ✓ 适合开发和测试")
        print("  ✓ 数据存储在 zen_bazi.db 文件中")
        print()
        print("启动服务：")
        print("  uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
        print()
        print()
        
        print("方案 2：配置 PostgreSQL TCP 连接（需要管理员权限）")
        print("-" * 70)
        if data_dir:
            print(f"1. 以管理员身份打开记事本")
            print(f"2. 打开文件: {os.path.join(data_dir, 'postgresql.conf')}")
            print(f"3. 找到 #listen_addresses = 'localhost'")
            print(f"4. 改为: listen_addresses = '*'")
            print(f"5. 保存文件")
            print()
            print(f"6. 打开文件: {os.path.join(data_dir, 'pg_hba.conf')}")
            print(f"7. 在文件末尾添加:")
            print(f"   host    all    all    127.0.0.1/32    md5")
            print(f"8. 保存文件")
            print()
            print(f"9. 重启 PostgreSQL 服务:")
            print(f"   - 打开 Windows 服务管理器")
            print(f"   - 找到 PostgreSQL 服务")
            print(f"   - 右键 -> 重新启动")
            print()
            print(f"10. 重新运行: python setup_database.py")
        else:
            print("无法找到 PostgreSQL 配置文件。")
            print("请参考 QUICK_FIX.md 文档手动配置。")
        print()
        print()
        
        print("方案 3：使用 Unix Socket 连接（仅限 Linux/Mac）")
        print("-" * 70)
        print("Windows 不支持此方案。")
        print()
    
    elif not running:
        print("❌ 问题：PostgreSQL 服务未运行")
        print()
        print("🔧 解决方案：")
        print("1. 打开 Windows 服务管理器（services.msc）")
        print("2. 找到 PostgreSQL 服务")
        print("3. 右键 -> 启动")
        print()
    
    else:
        print("✅ PostgreSQL 配置正常")
        print()
        print("如果仍然无法连接，请检查：")
        print("1. 密码是否正确")
        print("2. zen_bazi 数据库是否已创建")
        print("3. 防火墙是否阻止了连接")
        print()
    
    print("=" * 70)
    print("💡 推荐：使用 SQLite 进行开发")
    print("=" * 70)
    print()
    print("SQLite 已经配置好，无需任何额外设置。")
    print("当前 .env 文件已经配置为使用 SQLite。")
    print()
    print("直接运行：")
    print("  uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
