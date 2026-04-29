"""
测试八字排盘引擎
"""
import sys
from pathlib import Path
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent / "bazi-admin"
sys.path.insert(0, str(project_root))

from src.services.bazi_engine import calculate_full_bazi, format_bazi_result


def test_basic_calculation():
    """测试基础计算功能"""
    print("=" * 60)
    print("测试 1: 基础八字计算")
    print("=" * 60)
    
    # 测试数据: 1990年5月15日14时30分 男
    result = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    
    print(format_bazi_result(result))
    
    # 验证关键字段
    assert result.bazi_string is not None
    assert len(result.bazi_string.split()) == 4
    assert result.shengxiao in ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    assert result.day_master in ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    
    print("✅ 基础计算测试通过\n")


def test_wuxing_calculation():
    """测试五行计算"""
    print("=" * 60)
    print("测试 2: 五行强度计算")
    print("=" * 60)
    
    result = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    
    # 验证五行百分比总和接近 100%
    total = (
        result.wuxing_strength.jin +
        result.wuxing_strength.mu +
        result.wuxing_strength.shui +
        result.wuxing_strength.huo +
        result.wuxing_strength.tu
    )
    
    print(f"五行百分比总和: {total}%")
    assert 99.0 <= total <= 101.0, f"五行百分比总和应接近100%, 实际: {total}%"
    
    # 验证五行统计
    total_count = sum(result.wuxing_summary.values())
    print(f"五行总个数: {total_count}")
    assert total_count > 0, "五行统计不能为空"
    
    print("✅ 五行计算测试通过\n")


def test_multiple_dates():
    """测试多个日期"""
    print("=" * 60)
    print("测试 3: 多个日期测试")
    print("=" * 60)
    
    test_cases = [
        (1990, 5, 15, 14, 30, 1, "1990年5月15日14时30分 男"),
        (1992, 8, 20, 10, 0, 0, "1992年8月20日10时0分 女"),
        (2000, 1, 1, 0, 0, 1, "2000年1月1日0时0分 男"),
        (1988, 12, 31, 23, 59, 0, "1988年12月31日23时59分 女"),
    ]
    
    for year, month, day, hour, minute, gender, desc in test_cases:
        print(f"\n测试: {desc}")
        result = calculate_full_bazi(year, month, day, hour, minute, gender)
        print(f"  八字: {result.bazi_string}")
        print(f"  生肖: {result.shengxiao}")
        print(f"  日主: {result.day_master} ({result.day_master_wuxing})")
        print(f"  五行: 金{result.wuxing_strength.jin}% 木{result.wuxing_strength.mu}% 水{result.wuxing_strength.shui}% 火{result.wuxing_strength.huo}% 土{result.wuxing_strength.tu}%")
    
    print("\n✅ 多日期测试通过\n")


def test_edge_cases():
    """测试边界情况"""
    print("=" * 60)
    print("测试 4: 边界情况测试")
    print("=" * 60)
    
    # 测试最早日期
    print("\n测试: 1900年1月1日0时0分")
    result = calculate_full_bazi(1900, 1, 1, 0, 0, 1)
    print(f"  八字: {result.bazi_string}")
    print(f"  ✅ 1900年日期测试通过")
    
    # 测试最晚日期
    print("\n测试: 2100年12月31日23时59分")
    result = calculate_full_bazi(2100, 12, 31, 23, 59, 1)
    print(f"  八字: {result.bazi_string}")
    print(f"  ✅ 2100年日期测试通过")
    
    # 测试闰年
    print("\n测试: 2020年2月29日12时0分 (闰年)")
    result = calculate_full_bazi(2020, 2, 29, 12, 0, 1)
    print(f"  八字: {result.bazi_string}")
    print(f"  ✅ 闰年日期测试通过")
    
    print("\n✅ 边界情况测试通过\n")


def test_invalid_dates():
    """测试无效日期"""
    print("=" * 60)
    print("测试 5: 无效日期测试")
    print("=" * 60)
    
    invalid_cases = [
        (1899, 1, 1, 0, 0, 1, "1899年 (太早)"),
        (2101, 1, 1, 0, 0, 1, "2101年 (太晚)"),
        (2020, 13, 1, 0, 0, 1, "13月 (无效月份)"),
        (2020, 2, 30, 0, 0, 1, "2月30日 (无效日期)"),
        (2020, 1, 1, 25, 0, 1, "25时 (无效小时)"),
        (2020, 1, 1, 0, 60, 1, "60分 (无效分钟)"),
    ]
    
    for year, month, day, hour, minute, gender, desc in invalid_cases:
        print(f"\n测试: {desc}")
        try:
            result = calculate_full_bazi(year, month, day, hour, minute, gender)
            print(f"  ❌ 应该抛出异常但没有")
            assert False, f"无效日期应该抛出异常: {desc}"
        except ValueError as e:
            print(f"  ✅ 正确抛出异常: {e}")
    
    print("\n✅ 无效日期测试通过\n")


def test_json_output():
    """测试 JSON 输出"""
    print("=" * 60)
    print("测试 6: JSON 输出测试")
    print("=" * 60)
    
    result = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    result_dict = result.to_dict()
    
    # 转换为 JSON
    json_str = json.dumps(result_dict, ensure_ascii=False, indent=2)
    print("\nJSON 输出:")
    print(json_str)
    
    # 验证 JSON 可以解析
    parsed = json.loads(json_str)
    assert parsed["bazi_string"] == result.bazi_string
    assert parsed["shengxiao"] == result.shengxiao
    
    print("\n✅ JSON 输出测试通过\n")


def test_pillar_details():
    """测试四柱详细信息"""
    print("=" * 60)
    print("测试 7: 四柱详细信息测试")
    print("=" * 60)
    
    result = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    
    print("\n年柱:")
    print(f"  干支: {result.year_pillar.gan}{result.year_pillar.zhi}")
    print(f"  纳音: {result.year_pillar.nayin}")
    print(f"  藏干: {', '.join(result.year_pillar.canggan)}")
    
    print("\n月柱:")
    print(f"  干支: {result.month_pillar.gan}{result.month_pillar.zhi}")
    print(f"  纳音: {result.month_pillar.nayin}")
    print(f"  藏干: {', '.join(result.month_pillar.canggan)}")
    
    print("\n日柱:")
    print(f"  干支: {result.day_pillar.gan}{result.day_pillar.zhi}")
    print(f"  纳音: {result.day_pillar.nayin}")
    print(f"  藏干: {', '.join(result.day_pillar.canggan)}")
    
    print("\n时柱:")
    print(f"  干支: {result.hour_pillar.gan}{result.hour_pillar.zhi}")
    print(f"  纳音: {result.hour_pillar.nayin}")
    print(f"  藏干: {', '.join(result.hour_pillar.canggan)}")
    
    # 验证纳音不为空
    assert result.year_pillar.nayin != "未知"
    assert result.month_pillar.nayin != "未知"
    assert result.day_pillar.nayin != "未知"
    assert result.hour_pillar.nayin != "未知"
    
    # 验证藏干不为空
    assert len(result.year_pillar.canggan) > 0
    assert len(result.month_pillar.canggan) > 0
    assert len(result.day_pillar.canggan) > 0
    assert len(result.hour_pillar.canggan) > 0
    
    print("\n✅ 四柱详细信息测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试八字排盘引擎")
    print("=" * 60 + "\n")
    
    try:
        test_basic_calculation()
        test_wuxing_calculation()
        test_multiple_dates()
        test_edge_cases()
        test_invalid_dates()
        test_json_output()
        test_pillar_details()
        
        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
