"""
检查 PostgreSQL 配置和端口
"""
import os
import subprocess
import glob


def find_postgresql_installations():
    """查找所有 PostgreSQL 安装"""
    installations = []
    
    # 常见安装路径
    base_paths = [
        r"C:\Program Files\PostgreSQL",
        r"C:\PostgreSQL",
        r"C:\Program Files (x86)\PostgreSQL",
    ]
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            # 查找版本目录
            for version_dir in os.listdir(base_path):
                full_path = os.path.join(base_path, version_dir)
                if os.path.isdir(full_path):
                    data_dir = os.path.join(full_path, "data")
                    bin_dir = os.path.join(full_path, "bin")
                    if os.path.exists(data_dir):
                        installations.append({
                            'version': version_dir,
                            'base': full_path,
                            'data': data_dir,
                            'bin': bin_dir
                        })
    
    return installations


def check_postgresql_conf(data_dir):
    """检查 postgresql.conf 配置"""
    conf_file = os.path.join(data_dir, "postgresql.conf")
    
    if not os.path.exists(conf_file):
        return None
    
    config = {
        'port': None,
        'listen_addresses': None,
        'max_connections': None
    }
    
    try:
        with open(conf_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                
                if 'port' in line and '=' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        config['port'] = parts[1].strip().split('#')[0].strip()
                
                if 'listen_addresses' in line and '=' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        config['listen_addresses'] = parts[1].strip().split('#')[0].strip().strip("'\"")
                
                if 'max_connections' in line and '=' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        config['max_connections'] = parts[1].strip().split('#')[0].strip()
        
        return config
    except Exception as e:
        return {'error': str(e)}


def check_services():
    """检查 PostgreSQL 服务"""
    try:
        result = subprocess.run(
            ['sc', 'query', 'type=', 'service', 'state=', 'all'],
            capture_output=True,
            text=True
        )
        
        services = []
        lines = result.stdout.split('\n')
        current_service = None
        
        for line in lines:
            if 'SERVICE_NAME:' in line:
                service_name = line.split(':')[1].strip()
                if 'postgres' in service_name.lower():
                    current_service = service_name
            elif 'STATE' in line and current_service:
                if 'RUNNING' in line:
                    services.append((current_service, 'RUNNING'))
                elif 'STOPPED' in line:
                    services.append((current_service, 'STOPPED'))
                current_service = None
        
        return services
    except Exception as e:
        return []


def check_port_usage():
    """检查端口使用情况"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        
        ports = []
        for line in result.stdout.split('\n'):
            if ':5432' in line or ':5433' in line or ':5434' in line:
                ports.append(line.strip())
        
        return ports
    except Exception as e:
        return []


def main():
    print("=" * 80)
    print("🔍 PostgreSQL 配置检查")
    print("=" * 80)
    print()
    
    # 检查安装
    print("📦 检查 PostgreSQL 安装...")
    installations = find_postgresql_installations()
    
    if not installations:
        print("❌ 未找到 PostgreSQL 安装")
        print()
        print("💡 可能的原因：")
        print("   1. PostgreSQL 安装在非标准路径")
        print("   2. PostgreSQL 未正确安装")
        print()
        print("🔧 建议：")
        print("   使用 SQLite 进行开发（已配置好）")
        print("   运行: uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
        return
    
    print(f"✅ 找到 {len(installations)} 个 PostgreSQL 安装\n")
    
    for i, install in enumerate(installations, 1):
        print(f"{'=' * 80}")
        print(f"安装 {i}: PostgreSQL {install['version']}")
        print(f"{'=' * 80}")
        print(f"📁 安装路径: {install['base']}")
        print(f"📁 数据目录: {install['data']}")
        print(f"📁 可执行文件: {install['bin']}")
        print()
        
        # 检查配置
        print("⚙️  配置信息:")
        config = check_postgresql_conf(install['data'])
        
        if config:
            if 'error' in config:
                print(f"   ❌ 读取配置失败: {config['error']}")
            else:
                port = config.get('port', '5432')
                listen = config.get('listen_addresses', 'localhost')
                max_conn = config.get('max_connections', '100')
                
                print(f"   端口 (port): {port if port else '5432 (默认)'}")
                print(f"   监听地址 (listen_addresses): {listen if listen else 'localhost (默认)'}")
                print(f"   最大连接数 (max_connections): {max_conn if max_conn else '100 (默认)'}")
                
                if not listen or listen == 'localhost':
                    print()
                    print("   ⚠️  警告: listen_addresses 设置为 localhost")
                    print("   这意味着 PostgreSQL 只接受本地连接")
                    print("   如果需要 TCP/IP 连接，需要修改为 '*' 或 '127.0.0.1'")
        else:
            print("   ❌ 未找到 postgresql.conf 文件")
        
        print()
    
    # 检查服务
    print(f"{'=' * 80}")
    print("🔧 PostgreSQL 服务状态")
    print(f"{'=' * 80}")
    services = check_services()
    
    if services:
        for service_name, status in services:
            status_icon = "✅" if status == "RUNNING" else "❌"
            print(f"{status_icon} {service_name}: {status}")
    else:
        print("❌ 未找到 PostgreSQL 服务")
    print()
    
    # 检查端口
    print(f"{'=' * 80}")
    print("🌐 端口使用情况")
    print(f"{'=' * 80}")
    ports = check_port_usage()
    
    if ports:
        print("找到以下 PostgreSQL 相关端口:")
        for port in ports:
            print(f"   {port}")
    else:
        print("❌ 未找到 PostgreSQL 监听的端口")
        print()
        print("💡 这意味着 PostgreSQL 可能：")
        print("   1. 未启动")
        print("   2. 未配置 TCP/IP 连接")
        print("   3. 使用了其他端口")
    print()
    
    # 测试连接
    print(f"{'=' * 80}")
    print("🔌 测试数据库连接")
    print(f"{'=' * 80}")
    print()
    print("正在测试连接到 zen_bazi 数据库...")
    print("密码: 123456")
    print()
    
    # 尝试使用 psql 连接
    if installations:
        psql_path = os.path.join(installations[0]['bin'], 'psql.exe')
        if os.path.exists(psql_path):
            try:
                # 设置环境变量
                env = os.environ.copy()
                env['PGPASSWORD'] = '123456'
                
                result = subprocess.run(
                    [psql_path, '-U', 'postgres', '-d', 'zen_bazi', '-c', 'SELECT version();'],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print("✅ 连接成功！")
                    print()
                    print("数据库版本:")
                    print(result.stdout)
                else:
                    print("❌ 连接失败")
                    print()
                    print("错误信息:")
                    print(result.stderr)
            except subprocess.TimeoutExpired:
                print("❌ 连接超时")
            except Exception as e:
                print(f"❌ 连接失败: {e}")
        else:
            print(f"❌ 未找到 psql.exe: {psql_path}")
    
    print()
    print(f"{'=' * 80}")
    print("📝 总结和建议")
    print(f"{'=' * 80}")
    print()
    
    if not services or all(status != 'RUNNING' for _, status in services):
        print("❌ PostgreSQL 服务未运行")
        print()
        print("🔧 解决方案:")
        print("   1. 打开 Windows 服务管理器 (services.msc)")
        print("   2. 找到 PostgreSQL 服务")
        print("   3. 右键 -> 启动")
        print()
    elif not ports:
        print("❌ PostgreSQL 未监听 TCP 端口")
        print()
        print("🔧 解决方案:")
        print("   方案 1: 使用 SQLite（推荐）")
        print("      - 已配置好，无需额外设置")
        print("      - 运行: uvicorn main:app --host 127.0.0.1 --port 9000 --reload")
        print()
        print("   方案 2: 配置 PostgreSQL TCP 连接")
        print("      - 参考 QUICK_FIX.md 文档")
        print("      - 需要修改 postgresql.conf 和 pg_hba.conf")
        print()
    else:
        print("✅ PostgreSQL 配置正常")
        print()
        print("可以尝试使用 Python 连接:")
        print("   python setup_database.py")
        print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
