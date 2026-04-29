"""
测试神煞功能集成
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(project_root, "bazi-admin"))

from src.services.bazi_engine import calculate_full_bazi, format_bazi_result

print("=" * 80)
print("测试神煞功能集成")
print("=" * 80)
print()

# 测试数据：1990年5月15日14时30分 男
print("【测试案例】1990年5月15日14时30分 男")
print("-" * 80)

result = calculate_full_bazi(1990, 5, 15, 14, 30, 1)

# 打印格式化结果
print(format_bazi_result(result))
print()

# 详细检查神煞数据
print("【神煞数据检查】")
print("-" * 80)

print(f"年柱神煞: {result.year_pillar.shensha}")
print(f"  - 数量: {len(result.year_pillar.shensha)}")
print()

print(f"月柱神煞: {result.month_pillar.shensha}")
print(f"  - 数量: {len(result.month_pillar.shensha)}")
print()

print(f"日柱神煞: {result.day_pillar.shensha}")
print(f"  - 数量: {len(result.day_pillar.shensha)}")
if result.day_pillar.shensha:
    print(f"  - 详细: {', '.join(result.day_pillar.shensha)}")
print()

print(f"时柱神煞: {result.hour_pillar.shensha}")
print(f"  - 数量: {len(result.hour_pillar.shensha)}")
if result.hour_pillar.shensha:
    print(f"  - 详细: {', '.join(result.hour_pillar.shensha)}")
print()

# JSON 输出
print("【JSON 输出】")
print("-" * 80)
import json
result_dict = result.to_dict()
print(json.dumps(result_dict, ensure_ascii=False, indent=2))
print()

print("=" * 80)
print("✅ 神煞功能测试完成")
print("=" * 80)
