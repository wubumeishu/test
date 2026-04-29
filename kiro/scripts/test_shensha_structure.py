"""
测试 lunar-python 神煞数据结构
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
bazi = lunar.getEightChar()

print("=" * 80)
print("测试 lunar-python 神煞数据结构")
print("=" * 80)
print()

# 检查 Lunar 对象的神煞方法
print("【Lunar 对象的神煞相关方法】")
lunar_methods = [m for m in dir(lunar) if not m.startswith('_')]
shensha_methods = [m for m in lunar_methods if 'shen' in m.lower() or 'sha' in m.lower()]
print(f"包含 'shen' 或 'sha' 的方法: {shensha_methods}")
print()

# 尝试获取神煞
if 'getShenSha' in lunar_methods:
    print("【lunar.getShenSha()】")
    try:
        shensha = lunar.getShenSha()
        print(f"类型: {type(shensha)}")
        print(f"内容: {shensha}")
    except Exception as e:
        print(f"错误: {e}")
    print()

# 尝试其他可能的方法
for method in shensha_methods:
    print(f"【lunar.{method}()】")
    try:
        result = getattr(lunar, method)()
        print(f"类型: {type(result)}")
        print(f"内容: {result}")
    except Exception as e:
        print(f"错误: {e}")
    print()

# 检查 EightChar 对象
print("【EightChar 对象的所有方法】")
bazi_methods = [m for m in dir(bazi) if not m.startswith('_') and callable(getattr(bazi, m))]
print(f"方法总数: {len(bazi_methods)}")
print(f"前20个方法: {bazi_methods[:20]}")
print()

print("=" * 80)
