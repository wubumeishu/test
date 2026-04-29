"""
测试完整的神煞数据提取
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(project_root, "bazi-admin"))

from lunar_python import Solar

# 测试数据：1990年5月15日14时30分
solar = Solar.fromYmdHms(1990, 5, 15, 14, 30, 0)
lunar = solar.getLunar()

print("=" * 80)
print("测试完整的神煞数据提取")
print("=" * 80)
print()

# 日柱神煞（lunar-python 主要提供日柱的神煞）
print("【日柱神煞】")
print(f"吉神: {lunar.getDayJiShen()}")
print(f"凶煞: {lunar.getDayXiongSha()}")
print(f"天神: {lunar.getDayTianShen()}")
print(f"天神吉凶: {lunar.getDayTianShenLuck()}")
print(f"天神类型: {lunar.getDayTianShenType()}")
print()

# 合并所有神煞
day_shensha = []
day_shensha.extend(lunar.getDayJiShen())  # 吉神
day_shensha.extend(lunar.getDayXiongSha())  # 凶煞
day_shensha.append(lunar.getDayTianShen())  # 天神

print(f"日柱合并神煞: {day_shensha}")
print()

# 时柱神煞
print("【时柱神煞】")
print(f"时天神: {lunar.getTimeTianShen()}")
print(f"时天神吉凶: {lunar.getTimeTianShenLuck()}")
print(f"时天神类型: {lunar.getTimeTianShenType()}")
print()

time_shensha = [lunar.getTimeTianShen()]
print(f"时柱神煞: {time_shensha}")
print()

# 检查是否有年柱和月柱的神煞方法
print("【检查年柱和月柱神煞方法】")
year_methods = [m for m in dir(lunar) if 'year' in m.lower() and ('ji' in m.lower() or 'xiong' in m.lower() or 'tianshen' in m.lower())]
month_methods = [m for m in dir(lunar) if 'month' in m.lower() and ('ji' in m.lower() or 'xiong' in m.lower() or 'tianshen' in m.lower())]

print(f"年柱相关方法: {year_methods}")
print(f"月柱相关方法: {month_methods}")
print()

print("=" * 80)
