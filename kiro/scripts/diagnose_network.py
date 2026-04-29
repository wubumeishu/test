#!/usr/bin/env python3
"""
网络连接诊断脚本
用于检查前后端服务状态和网络连接
"""

import socket
import requests
import json
from datetime import datetime


def check_port(host: str, port: int, service_name: str) -> bool:
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {service_name} 正在运行 ({host}:{port})")
            return True
        else:
            print(f"❌ {service_name} 未运行 ({host}:{port})")
            return False
    except Exception as e:
        print(f"❌ {service_name} 检查失败: {e}")
        return False


def test_backend_api() -> bool:
    """测试后端 API"""
    try:
        url = "http://127.0.0.1:9000/api/health"
        print(f"\n📡 测试后端健康检查接口: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端 API 响应正常")
            print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 后端 API 响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端 API（连接被拒绝）")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 后端 API 请求超时")
        return False
    except Exception as e:
        print(f"❌ 后端 API 测试失败: {e}")
        return False


def test_fortune_api() -> bool:
    """测试排盘 API"""
    try:
        url = "http://127.0.0.1:9000/api/fortune/calculate-by-data"
        print(f"\n📡 测试排盘接口: {url}")
        
        # 构造测试数据
        test_data = {
            "name": "测试",
            "gender": 1,
            "birth_year": 2026,
            "birth_month": 4,
            "birth_day": 29,
            "birth_hour": 19,
            "birth_minute": 54,
            "is_deep_analysis": False
        }
        
        print(f"   请求数据: {json.dumps(test_data, ensure_ascii=False)}")
        
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 排盘 API 响应正常")
            print(f"   成功状态: {data.get('success')}")
            print(f"   消息: {data.get('message')}")
            print(f"   八字: {data.get('bazi_string')}")
            print(f"   日主: {data.get('day_master')} ({data.get('day_master_wuxing')})")
            return True
        else:
            print(f"❌ 排盘 API 响应异常: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到排盘 API（连接被拒绝）")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 排盘 API 请求超时")
        return False
    except Exception as e:
        print(f"❌ 排盘 API 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 网络连接诊断工具")
    print("=" * 60)
    print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查端口
    print("📋 检查服务端口...")
    print("-" * 60)
    backend_running = check_port("127.0.0.1", 9000, "后端服务")
    frontend_running = check_port("127.0.0.1", 5173, "前端服务")
    print()
    
    # 测试后端 API
    if backend_running:
        print("📋 测试后端 API...")
        print("-" * 60)
        health_ok = test_backend_api()
        fortune_ok = test_fortune_api()
        print()
    else:
        health_ok = False
        fortune_ok = False
    
    # 总结
    print("=" * 60)
    print("📊 诊断结果总结")
    print("=" * 60)
    print(f"{'✅' if backend_running else '❌'} 后端服务 (端口 9000)")
    print(f"{'✅' if frontend_running else '❌'} 前端服务 (端口 5173)")
    print(f"{'✅' if health_ok else '❌'} 后端健康检查")
    print(f"{'✅' if fortune_ok else '❌'} 排盘接口")
    print()
    
    # 建议
    if not backend_running:
        print("💡 建议:")
        print("   后端服务未运行，请执行:")
        print("   cd bazi-admin")
        print("   python main.py")
        print()
    
    if not frontend_running:
        print("💡 建议:")
        print("   前端服务未运行，请执行:")
        print("   cd my-bazi-app")
        print("   npm run dev:h5")
        print()
    
    if backend_running and frontend_running and health_ok and fortune_ok:
        print("✅ 所有服务运行正常！")
        print()
        print("💡 如果前端仍然无法访问后端，请确保:")
        print("   1. 在浏览器中访问 http://localhost:5173（不要在微信开发者工具中）")
        print("   2. 打开浏览器控制台（F12）查看网络请求")
        print("   3. 检查 Network 标签中的请求状态")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    main()
