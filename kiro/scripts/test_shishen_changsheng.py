"""
测试十神和十二长生数据提取
验证 bazi_engine.py 是否正确使用 lunar-python 原生方法
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(project_root, "bazi-admin"))

from src.services.bazi_engine import calculate_full_bazi, format_bazi_result


def test_shishen_changsheng():
    """测试十神和十二长生数据"""
    print("=" * 80)
    print("测试十神和十二长生数据提取")
    print("=" * 80)
    print()
    
    # 测试案例 1: 1990年5月15日14时30分 男
    print("【测试案例 1】1990年5月15日14时30分 男")
    print("-" * 80)
    result1 = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    
    # 打印格式化结果
    print(format_bazi_result(result1))
    print()
    
    # 详细检查十神和长生数据
    print("【详细数据检查】")
    print("-" * 80)
    
    print(f"年柱: {result1.year_pillar.gan}{result1.year_pillar.zhi}")
    print(f"  - 天干十神: {result1.year_pillar.shishen}")
    print(f"  - 地支长生: {result1.year_pillar.changsheng}")
    print(f"  - 藏干: {result1.year_pillar.canggan}")
    print(f"  - 藏干十神: {result1.year_pillar.canggan_shishen}")
    print()
    
    print(f"月柱: {result1.month_pillar.gan}{result1.month_pillar.zhi}")
    print(f"  - 天干十神: {result1.month_pillar.shishen}")
    print(f"  - 地支长生: {result1.month_pillar.changsheng}")
    print(f"  - 藏干: {result1.month_pillar.canggan}")
    print(f"  - 藏干十神: {result1.month_pillar.canggan_shishen}")
    print()
    
    print(f"日柱: {result1.day_pillar.gan}{result1.day_pillar.zhi}")
    print(f"  - 天干十神: {result1.day_pillar.shishen} (应该固定为'日主')")
    print(f"  - 地支长生: {result1.day_pillar.changsheng}")
    print(f"  - 藏干: {result1.day_pillar.canggan}")
    print(f"  - 藏干十神: {result1.day_pillar.canggan_shishen}")
    print()
    
    print(f"时柱: {result1.hour_pillar.gan}{result1.hour_pillar.zhi}")
    print(f"  - 天干十神: {result1.hour_pillar.shishen}")
    print(f"  - 地支长生: {result1.hour_pillar.changsheng}")
    print(f"  - 藏干: {result1.hour_pillar.canggan}")
    print(f"  - 藏干十神: {result1.hour_pillar.canggan_shishen}")
    print()
    
    # 验证数据完整性
    print("【数据完整性验证】")
    print("-" * 80)
    
    pillars = [
        ("年柱", result1.year_pillar),
        ("月柱", result1.month_pillar),
        ("日柱", result1.day_pillar),
        ("时柱", result1.hour_pillar)
    ]
    
    all_valid = True
    for name, pillar in pillars:
        has_shishen = bool(pillar.shishen)
        has_changsheng = bool(pillar.changsheng)
        has_canggan_shishen = bool(pillar.canggan_shishen)
        
        status = "✓" if (has_shishen and has_changsheng and has_canggan_shishen) else "✗"
        print(f"{status} {name}: 十神={has_shishen}, 长生={has_changsheng}, 藏干十神={has_canggan_shishen}")
        
        if not (has_shishen and has_changsheng and has_canggan_shishen):
            all_valid = False
    
    print()
    if all_valid:
        print("✓ 所有数据完整！")
    else:
        print("✗ 存在缺失数据！")
    
    print()
    print("=" * 80)
    
    # 测试案例 2: 1992年8月20日10时0分 女
    print()
    print("【测试案例 2】1992年8月20日10时0分 女")
    print("-" * 80)
    result2 = calculate_full_bazi(1992, 8, 20, 10, 0, 0)
    print(format_bazi_result(result2))
    print()
    
    # JSON 输出测试
    print("【JSON 输出测试】")
    print("-" * 80)
    import json
    result_dict = result1.to_dict()
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))
    print()
    
    return all_valid


if __name__ == "__main__":
    try:
        success = test_shishen_changsheng()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
