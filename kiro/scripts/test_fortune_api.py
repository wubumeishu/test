"""
测试 Fortune API 是否正确返回十神和长生数据
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_calculate_by_data():
    """测试通过原始数据计算八字"""
    print("=" * 80)
    print("测试 Fortune API - 十神和长生数据")
    print("=" * 80)
    print()
    
    # 测试数据
    test_data = {
        "name": "测试用户",
        "gender": 1,
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 14,
        "birth_minute": 30,
        "is_deep_analysis": False
    }
    
    print(f"📤 发送请求: POST {BASE_URL}/api/fortune/calculate-by-data")
    print(f"📋 请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/fortune/calculate-by-data",
            json=test_data,
            timeout=10
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API 调用成功！")
            print()
            
            # 打印基础信息
            print("【基础信息】")
            print(f"姓名: {result.get('name')}")
            print(f"八字: {result.get('bazi_string')}")
            print(f"日主: {result.get('day_master')} ({result.get('day_master_wuxing')})")
            print()
            
            # 检查四柱数据
            print("【四柱数据检查】")
            pillars = [
                ("年柱", result.get("year_pillar")),
                ("月柱", result.get("month_pillar")),
                ("日柱", result.get("day_pillar")),
                ("时柱", result.get("hour_pillar"))
            ]
            
            all_valid = True
            for name, pillar in pillars:
                if pillar:
                    gan = pillar.get("gan", "")
                    zhi = pillar.get("zhi", "")
                    shishen = pillar.get("shishen", "")
                    changsheng = pillar.get("changsheng", "")
                    canggan_shishen = pillar.get("canggan_shishen", [])
                    
                    has_shishen = bool(shishen)
                    has_changsheng = bool(changsheng)
                    has_canggan_shishen = bool(canggan_shishen)
                    
                    status = "✓" if (has_shishen and has_changsheng and has_canggan_shishen) else "✗"
                    
                    print(f"{status} {name}: {gan}{zhi}")
                    print(f"   - 十神: {shishen if has_shishen else '❌ 缺失'}")
                    print(f"   - 长生: {changsheng if has_changsheng else '❌ 缺失'}")
                    print(f"   - 藏干十神: {', '.join(canggan_shishen) if has_canggan_shishen else '❌ 缺失'}")
                    
                    if not (has_shishen and has_changsheng and has_canggan_shishen):
                        all_valid = False
                else:
                    print(f"✗ {name}: 数据缺失")
                    all_valid = False
            
            print()
            
            if all_valid:
                print("🎉 所有数据完整！十神和长生数据已正确返回。")
            else:
                print("⚠️ 存在缺失数据！")
            
            print()
            print("【完整响应 JSON】")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return all_valid
            
        else:
            print(f"❌ API 调用失败")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保后端服务已启动:")
        print("   cd bazi-admin")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_calculate_by_data()
    sys.exit(0 if success else 1)
