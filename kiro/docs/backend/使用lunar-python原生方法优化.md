# 使用 lunar-python 原生方法优化八字计算

## 📅 更新时间
2026-04-29 20:30

## ✅ 优化内容

### 问题背景

之前我们自己实现了十神和十二长生的计算逻辑，但实际上 **lunar-python 库本身就提供了这些功能的原生方法**，使用原生方法有以下优势：

1. **更准确**：库的实现经过充分测试和验证
2. **更完整**：包含了更多细节和边界情况的处理
3. **更简洁**：减少自定义代码，降低维护成本
4. **更权威**：遵循传统命理学的标准算法

### 修改内容

**文件**：`bazi-admin/src/services/bazi_engine.py`

#### 修改前（自定义实现）

```python
# 年柱
year_gan = bazi.getYearGan()
year_zhi = bazi.getYearZhi()
year_canggan = DIZHI_CANGGAN.get(year_zhi, [])
year_pillar = Pillar(
    gan=year_gan,
    zhi=year_zhi,
    nayin=get_nayin(year_gan, year_zhi),
    canggan=year_canggan,
    shishen=get_shishen(day_gan, year_gan),  # 自定义函数
    changsheng=get_changsheng(day_gan, year_zhi),  # 自定义函数
    canggan_shishen=[get_shishen(day_gan, cg) for cg in year_canggan]  # 自定义函数
)
```

#### 修改后（使用原生方法）

```python
# 年柱（使用 lunar-python 原生方法）
year_gan = bazi.getYearGan()
year_zhi = bazi.getYearZhi()
year_pillar = Pillar(
    gan=year_gan,
    zhi=year_zhi,
    nayin=get_nayin(year_gan, year_zhi),
    canggan=bazi.getYearHideGan(),  # 原生方法：获取年支藏干
    shishen=bazi.getYearShiShenGan(),  # 原生方法：获取年干十神
    changsheng=bazi.getYearDiShi(),  # 原生方法：获取年支地势（十二长生）
    canggan_shishen=bazi.getYearShiShenZhi()  # 原生方法：获取年支藏干十神
)
```

### lunar-python 原生方法清单

#### 年柱相关方法

| 方法名 | 返回类型 | 说明 |
|--------|----------|------|
| `getYearGan()` | str | 年干 |
| `getYearZhi()` | str | 年支 |
| `getYearHideGan()` | List[str] | 年支藏干（数组） |
| `getYearShiShenGan()` | str | 年干十神 |
| `getYearShiShenZhi()` | List[str] | 年支藏干十神（数组） |
| `getYearDiShi()` | str | 年支地势（十二长生） |

#### 月柱相关方法

| 方法名 | 返回类型 | 说明 |
|--------|----------|------|
| `getMonthGan()` | str | 月干 |
| `getMonthZhi()` | str | 月支 |
| `getMonthHideGan()` | List[str] | 月支藏干（数组） |
| `getMonthShiShenGan()` | str | 月干十神 |
| `getMonthShiShenZhi()` | List[str] | 月支藏干十神（数组） |
| `getMonthDiShi()` | str | 月支地势（十二长生） |

#### 日柱相关方法

| 方法名 | 返回类型 | 说明 |
|--------|----------|------|
| `getDayGan()` | str | 日干 |
| `getDayZhi()` | str | 日支 |
| `getDayHideGan()` | List[str] | 日支藏干（数组） |
| `getDayShiShenGan()` | str | 日干十神（通常返回"日主"） |
| `getDayShiShenZhi()` | List[str] | 日支藏干十神（数组） |
| `getDayDiShi()` | str | 日支地势（十二长生） |

#### 时柱相关方法

| 方法名 | 返回类型 | 说明 |
|--------|----------|------|
| `getTimeGan()` | str | 时干 |
| `getTimeZhi()` | str | 时支 |
| `getTimeHideGan()` | List[str] | 时支藏干（数组） |
| `getTimeShiShenGan()` | str | 时干十神 |
| `getTimeShiShenZhi()` | List[str] | 时支藏干十神（数组） |
| `getTimeDiShi()` | str | 时支地势（十二长生） |

### 完整代码示例

```python
# 获取八字对象
bazi = lunar.getEightChar()

# 年柱
year_pillar = Pillar(
    gan=bazi.getYearGan(),
    zhi=bazi.getYearZhi(),
    nayin=get_nayin(bazi.getYearGan(), bazi.getYearZhi()),
    canggan=bazi.getYearHideGan(),
    shishen=bazi.getYearShiShenGan(),
    changsheng=bazi.getYearDiShi(),
    canggan_shishen=bazi.getYearShiShenZhi()
)

# 月柱
month_pillar = Pillar(
    gan=bazi.getMonthGan(),
    zhi=bazi.getMonthZhi(),
    nayin=get_nayin(bazi.getMonthGan(), bazi.getMonthZhi()),
    canggan=bazi.getMonthHideGan(),
    shishen=bazi.getMonthShiShenGan(),
    changsheng=bazi.getMonthDiShi(),
    canggan_shishen=bazi.getMonthShiShenZhi()
)

# 日柱
day_pillar = Pillar(
    gan=bazi.getDayGan(),
    zhi=bazi.getDayZhi(),
    nayin=get_nayin(bazi.getDayGan(), bazi.getDayZhi()),
    canggan=bazi.getDayHideGan(),
    shishen=bazi.getDayShiShenGan(),
    changsheng=bazi.getDayDiShi(),
    canggan_shishen=bazi.getDayShiShenZhi()
)

# 时柱
hour_pillar = Pillar(
    gan=bazi.getTimeGan(),
    zhi=bazi.getTimeZhi(),
    nayin=get_nayin(bazi.getTimeGan(), bazi.getTimeZhi()),
    canggan=bazi.getTimeHideGan(),
    shishen=bazi.getTimeShiShenGan(),
    changsheng=bazi.getTimeDiShi(),
    canggan_shishen=bazi.getTimeShiShenZhi()
)
```

### 测试结果

#### 测试用例
```
出生日期：1990年5月15日14时30分
性别：男
```

#### 输出结果
```
============================================================
八字排盘结果
============================================================
公历: 1990-05-15 14:30
农历: 一九九〇年四月廿一
性别: 男
生肖: 马

四柱八字:
  年柱: 庚午 (路旁土)
        十神: 比肩  长生: 沐浴
        藏干: 丁, 己
        藏干十神: 正官, 正印
  月柱: 辛巳 (白蜡金)
        十神: 劫财  长生: 长生
        藏干: 丙, 庚, 戊
        藏干十神: 七杀, 比肩, 偏印
  日柱: 庚辰 (白蜡金)
        十神: 日主  长生: 养
        藏干: 戊, 乙, 癸
        藏干十神: 偏印, 正财, 伤官
  时柱: 癸未 (杨柳木)
        十神: 伤官  长生: 冠带
        藏干: 己, 丁, 乙
        藏干十神: 正印, 正官, 正财

八字: 庚午 辛巳 庚辰 癸未
日主: 庚 (金)

五行强度:
  金: 38.89% (3个)
  木: 2.78% (0个)
  水: 13.89% (1个)
  火: 21.53% (2个)
  土: 22.92% (2个)
============================================================
```

✅ 所有数据计算正确！

### 优化效果

#### 1. 代码简化
- **删除**：自定义的十神和十二长生映射常量（约 100 行）
- **删除**：`get_shishen()` 和 `get_changsheng()` 函数（约 50 行）
- **简化**：四柱创建逻辑更加清晰

#### 2. 准确性提升
- 使用库的标准实现，避免自定义逻辑的潜在错误
- 藏干顺序遵循传统命理学标准

#### 3. 维护性提升
- 减少自定义代码，降低维护成本
- 库更新时自动获得改进

### 保留的自定义功能

以下功能仍然保留自定义实现：

1. **纳音计算**：`get_nayin()` 函数
   - lunar-python 也有纳音方法，但我们的实现已经很完善
   
2. **五行强度计算**：`calculate_wuxing_strength()` 函数
   - 这是我们的特色功能，使用权重算法计算五行百分比

3. **数据封装**：`Pillar` 和 `BaziResult` 数据类
   - 提供更好的类型提示和数据结构

### 可用的其他 lunar-python 方法

lunar-python 还提供了更多高级功能，可以在未来扩展：

#### 大运相关
```python
bazi.getYun(gender)  # 获取大运
```

#### 流年相关
```python
bazi.getLiuNian(age)  # 获取流年
```

#### 神煞相关
```python
bazi.getYearShenSha()  # 年柱神煞
bazi.getMonthShenSha()  # 月柱神煞
bazi.getDayShenSha()  # 日柱神煞
bazi.getTimeShenSha()  # 时柱神煞
```

#### 纳音相关
```python
bazi.getYearNaYin()  # 年柱纳音
bazi.getMonthNaYin()  # 月柱纳音
bazi.getDayNaYin()  # 日柱纳音
bazi.getTimeNaYin()  # 时柱纳音
```

### 注意事项

1. **日干十神**：`getDayShiShenGan()` 通常返回 `"日主"` 或 `"我"`，这是正确的
2. **藏干顺序**：lunar-python 的藏干顺序可能与某些资料不同，但都是有依据的
3. **空值处理**：原生方法返回的列表可能为空，前端需要做好判空处理

### 后续优化建议

1. **大运流年**：添加大运和流年的计算和展示
2. **神煞系统**：添加神煞的计算（如桃花、天乙贵人等）
3. **格局判断**：使用 lunar-python 的格局判断功能
4. **旺衰分析**：添加日主旺衰的详细分析

---

**优化完成！** 🎉

现在我们的八字计算引擎使用了 lunar-python 的原生方法，更加准确和可靠！
