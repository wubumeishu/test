"""
八字排盘核心算法服务
基于 lunar-python 库实现完整的八字计算功能
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from lunar_python import Solar, Lunar


# ==================== 常量定义 ====================

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 生肖
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 五行属性映射 (天干)
TIANGAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# 五行属性映射 (地支)
DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支藏干
DIZHI_CANGGAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# 十神关系映射 (以日主为中心)
# 格式: {日主五行: {目标五行: 十神名称}}
SHISHEN_MAP = {
    "木": {
        "木": "比肩",  # 同我
        "火": "食神",  # 我生
        "土": "偏财",  # 我克
        "金": "七杀",  # 克我
        "水": "偏印"   # 生我
    },
    "火": {
        "火": "比肩",
        "土": "食神",
        "金": "偏财",
        "水": "七杀",
        "木": "偏印"
    },
    "土": {
        "土": "比肩",
        "金": "食神",
        "水": "偏财",
        "木": "七杀",
        "火": "偏印"
    },
    "金": {
        "金": "比肩",
        "水": "食神",
        "木": "偏财",
        "火": "七杀",
        "土": "偏印"
    },
    "水": {
        "水": "比肩",
        "木": "食神",
        "火": "偏财",
        "土": "七杀",
        "金": "偏印"
    }
}

# 阴阳属性
TIANGAN_YINYANG = {
    "甲": "阳", "乙": "阴",
    "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴",
    "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴"
}

# 十神完整映射 (考虑阴阳)
# 同性为偏，异性为正
SHISHEN_FULL_MAP = {
    "比肩": {"同性": "比肩", "异性": "劫财"},
    "食神": {"同性": "食神", "异性": "伤官"},
    "偏财": {"同性": "偏财", "异性": "正财"},
    "七杀": {"同性": "七杀", "异性": "正官"},
    "偏印": {"同性": "偏印", "异性": "正印"}
}

# 十二长生 (地势)
# 格式: {日主天干: {地支: 长生状态}}
CHANGSHENG_MAP = {
    "甲": {"亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死", "未": "墓", "申": "绝", "酉": "胎", "戌": "养"},
    "乙": {"午": "长生", "巳": "沐浴", "辰": "冠带", "卯": "临官", "寅": "帝旺", "丑": "衰", "子": "病", "亥": "死", "戌": "墓", "酉": "绝", "申": "胎", "未": "养"},
    "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "丁": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "戊": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "己": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "庚": {"巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官", "酉": "帝旺", "戌": "衰", "亥": "病", "子": "死", "丑": "墓", "寅": "绝", "卯": "胎", "辰": "养"},
    "辛": {"子": "长生", "亥": "沐浴", "戌": "冠带", "酉": "临官", "申": "帝旺", "未": "衰", "午": "病", "巳": "死", "辰": "墓", "卯": "绝", "寅": "胎", "丑": "养"},
    "壬": {"申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官", "子": "帝旺", "丑": "衰", "寅": "病", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎", "未": "养"},
    "癸": {"卯": "长生", "寅": "沐浴", "丑": "冠带", "子": "临官", "亥": "帝旺", "戌": "衰", "酉": "病", "申": "死", "未": "墓", "午": "绝", "巳": "胎", "辰": "养"}
}

# 纳音五行 (六十甲子纳音)
NAYIN_MAP = {
    "甲子": "海中金", "乙丑": "海中金",
    "丙寅": "炉中火", "丁卯": "炉中火",
    "戊辰": "大林木", "己巳": "大林木",
    "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "剑锋金", "癸酉": "剑锋金",
    "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水",
    "戊寅": "城头土", "己卯": "城头土",
    "庚辰": "白蜡金", "辛巳": "白蜡金",
    "壬午": "杨柳木", "癸未": "杨柳木",
    "甲申": "泉中水", "乙酉": "泉中水",
    "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火",
    "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "长流水", "癸巳": "长流水",
    "甲午": "砂石金", "乙未": "砂石金",
    "丙申": "山下火", "丁酉": "山下火",
    "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土",
    "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "覆灯火", "乙巳": "覆灯火",
    "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驿土", "己酉": "大驿土",
    "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木",
    "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土",
    "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木",
    "壬戌": "大海水", "癸亥": "大海水"
}


# ==================== 数据类定义 ====================

@dataclass
class Pillar:
    """四柱（年月日时）"""
    gan: str        # 天干
    zhi: str        # 地支
    nayin: str      # 纳音
    canggan: List[str]  # 藏干
    shishen: str = ""  # 十神
    changsheng: str = ""  # 十二长生
    canggan_shishen: List[str] = None  # 藏干十神
    shensha: List[str] = None  # 神煞
    
    def __post_init__(self):
        """初始化后处理"""
        if self.canggan_shishen is None:
            self.canggan_shishen = []
        if self.shensha is None:
            self.shensha = []


@dataclass
class WuxingStrength:
    """五行强度"""
    jin: float      # 金
    mu: float       # 木
    shui: float     # 水
    huo: float      # 火
    tu: float       # 土


@dataclass
class BaziResult:
    """八字排盘结果"""
    # 基础信息
    solar_date: str             # 公历日期 YYYY-MM-DD HH:mm
    lunar_date: str             # 农历日期
    gender: int                 # 性别 (1=男, 0=女)
    shengxiao: str              # 生肖
    
    # 四柱
    year_pillar: Pillar         # 年柱
    month_pillar: Pillar        # 月柱
    day_pillar: Pillar          # 日柱
    hour_pillar: Pillar         # 时柱
    
    # 八字字符串
    bazi_string: str            # 完整八字字符串 (如: 甲子 乙丑 丙寅 丁卯)
    
    # 五行分析
    wuxing_strength: WuxingStrength  # 五行强度百分比
    wuxing_summary: Dict[str, int]   # 五行统计 (个数)
    
    # 其他信息
    day_master: str             # 日主 (日干)
    day_master_wuxing: str      # 日主五行
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


# ==================== 核心计算函数 ====================

def get_nayin(gan: str, zhi: str) -> str:
    """
    获取纳音五行
    
    Args:
        gan: 天干
        zhi: 地支
        
    Returns:
        纳音五行名称
    """
    ganzhi = f"{gan}{zhi}"
    return NAYIN_MAP.get(ganzhi, "未知")


def get_shishen(day_gan: str, target_gan: str) -> str:
    """
    计算十神
    
    Args:
        day_gan: 日主天干
        target_gan: 目标天干
        
    Returns:
        十神名称
    """
    # 获取日主和目标的五行
    day_wuxing = TIANGAN_WUXING.get(day_gan, "")
    target_wuxing = TIANGAN_WUXING.get(target_gan, "")
    
    if not day_wuxing or not target_wuxing:
        return ""
    
    # 获取基础十神
    base_shishen = SHISHEN_MAP.get(day_wuxing, {}).get(target_wuxing, "")
    
    if not base_shishen:
        return ""
    
    # 判断阴阳
    day_yinyang = TIANGAN_YINYANG.get(day_gan, "")
    target_yinyang = TIANGAN_YINYANG.get(target_gan, "")
    
    # 同性为偏，异性为正
    if day_yinyang == target_yinyang:
        return SHISHEN_FULL_MAP.get(base_shishen, {}).get("同性", base_shishen)
    else:
        return SHISHEN_FULL_MAP.get(base_shishen, {}).get("异性", base_shishen)


def get_changsheng(day_gan: str, zhi: str) -> str:
    """
    计算十二长生（地势）
    
    Args:
        day_gan: 日主天干
        zhi: 地支
        
    Returns:
        十二长生状态
    """
    return CHANGSHENG_MAP.get(day_gan, {}).get(zhi, "")


def extract_shensha(lunar_obj, pillar_type: str) -> List[str]:
    """
    提取神煞列表
    
    Args:
        lunar_obj: Lunar 对象
        pillar_type: 柱类型 ('year', 'month', 'day', 'time')
        
    Returns:
        神煞名称列表
    """
    shensha_list = []
    
    try:
        if pillar_type == 'day':
            # 日柱神煞：吉神 + 凶煞 + 天神
            ji_shen = lunar_obj.getDayJiShen()  # 吉神列表
            xiong_sha = lunar_obj.getDayXiongSha()  # 凶煞列表
            tian_shen = lunar_obj.getDayTianShen()  # 天神
            
            if ji_shen:
                shensha_list.extend(ji_shen)
            if xiong_sha:
                shensha_list.extend(xiong_sha)
            if tian_shen and tian_shen not in shensha_list:
                shensha_list.append(tian_shen)
                
        elif pillar_type == 'time':
            # 时柱神煞：天神
            tian_shen = lunar_obj.getTimeTianShen()
            if tian_shen:
                shensha_list.append(tian_shen)
        
        # 年柱和月柱：lunar-python 未提供专门的神煞方法，返回空列表
        # 注：可以根据需要扩展自定义神煞计算逻辑
        
    except Exception as e:
        print(f"⚠️ [神煞提取] {pillar_type}柱神煞提取失败: {e}")
    
    return shensha_list


def calculate_wuxing_strength(
    year_pillar: Pillar,
    month_pillar: Pillar,
    day_pillar: Pillar,
    hour_pillar: Pillar
) -> Tuple[WuxingStrength, Dict[str, int]]:
    """
    计算五行强度
    
    算法说明:
    1. 天干权重: 30%
    2. 地支权重: 20%
    3. 藏干权重: 10% (平均分配)
    
    Args:
        year_pillar: 年柱
        month_pillar: 月柱
        day_pillar: 日柱
        hour_pillar: 时柱
        
    Returns:
        (五行强度百分比, 五行统计个数)
    """
    # 初始化五行计数
    wuxing_count = {"金": 0.0, "木": 0.0, "水": 0.0, "火": 0.0, "土": 0.0}
    wuxing_summary = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    
    pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
    
    for pillar in pillars:
        # 天干 (权重 30)
        gan_wuxing = TIANGAN_WUXING.get(pillar.gan, "")
        if gan_wuxing:
            wuxing_count[gan_wuxing] += 30
            wuxing_summary[gan_wuxing] += 1
        
        # 地支 (权重 20)
        zhi_wuxing = DIZHI_WUXING.get(pillar.zhi, "")
        if zhi_wuxing:
            wuxing_count[zhi_wuxing] += 20
            wuxing_summary[zhi_wuxing] += 1
        
        # 藏干 (权重 10, 平均分配)
        if pillar.canggan:
            canggan_weight = 10 / len(pillar.canggan)
            for canggan in pillar.canggan:
                canggan_wuxing = TIANGAN_WUXING.get(canggan, "")
                if canggan_wuxing:
                    wuxing_count[canggan_wuxing] += canggan_weight
    
    # 计算总分
    total = sum(wuxing_count.values())
    
    # 转换为百分比
    wuxing_strength = WuxingStrength(
        jin=round((wuxing_count["金"] / total * 100), 2) if total > 0 else 0.0,
        mu=round((wuxing_count["木"] / total * 100), 2) if total > 0 else 0.0,
        shui=round((wuxing_count["水"] / total * 100), 2) if total > 0 else 0.0,
        huo=round((wuxing_count["火"] / total * 100), 2) if total > 0 else 0.0,
        tu=round((wuxing_count["土"] / total * 100), 2) if total > 0 else 0.0
    )
    
    return wuxing_strength, wuxing_summary


def validate_date(year: int, month: int, day: int, hour: int, minute: int) -> bool:
    """
    验证日期有效性
    
    支持范围:
    - lunar-python 理论上支持公元元年至今的日期
    - 但考虑到历史准确性,建议使用 1000 年之后的日期
    - 本函数支持 1000-2100 年范围
    
    Args:
        year: 年份
        month: 月份
        day: 日期
        hour: 小时
        minute: 分钟
        
    Returns:
        是否有效
    """
    try:
        # 检查基本范围
        # 扩展支持到 1000 年 (lunar-python 支持更早,但历史准确性存疑)
        if not (1000 <= year <= 2100):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        if not (0 <= hour <= 23):
            return False
        if not (0 <= minute <= 59):
            return False
        
        # 使用 datetime 验证日期有效性
        # datetime 支持 1-9999 年
        datetime(year, month, day, hour, minute)
        return True
    except (ValueError, OverflowError):
        return False


def calculate_full_bazi(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    gender: int = 1
) -> BaziResult:
    """
    计算完整八字
    
    支持范围:
    - 1000-2100 年 (推荐)
    - lunar-python 理论上支持更早的日期,但历史准确性存疑
    - 1000 年之前的日期可能存在历法差异
    
    Args:
        year: 出生年份 (公历, 1000-2100)
        month: 出生月份 (公历, 1-12)
        day: 出生日期 (公历, 1-31)
        hour: 出生小时 (公历, 0-23)
        minute: 出生分钟 (公历, 0-59)
        gender: 性别 (1=男, 0=女)
        
    Returns:
        BaziResult: 完整的八字排盘结果
        
    Raises:
        ValueError: 日期参数无效
    """
    # 验证日期
    if not validate_date(year, month, day, hour, minute):
        raise ValueError(f"无效的日期: {year}-{month}-{day} {hour}:{minute}")
    
    try:
        # 创建公历对象
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        
        # 转换为农历
        lunar = solar.getLunar()
        
        # 获取八字
        bazi = lunar.getEightChar()
        
        # 年柱（使用 lunar-python 原生方法）
        year_gan = bazi.getYearGan()
        year_zhi = bazi.getYearZhi()
        year_pillar = Pillar(
            gan=year_gan,
            zhi=year_zhi,
            nayin=get_nayin(year_gan, year_zhi),
            canggan=bazi.getYearHideGan(),  # 使用原生方法获取藏干
            shishen=bazi.getYearShiShenGan(),  # 使用原生方法获取年干十神
            changsheng=bazi.getYearDiShi(),  # 使用原生方法获取年支地势（十二长生）
            canggan_shishen=bazi.getYearShiShenZhi(),  # 使用原生方法获取年支藏干十神
            shensha=extract_shensha(lunar, 'year')  # 提取年柱神煞
        )
        
        # 月柱（使用 lunar-python 原生方法）
        month_gan = bazi.getMonthGan()
        month_zhi = bazi.getMonthZhi()
        month_pillar = Pillar(
            gan=month_gan,
            zhi=month_zhi,
            nayin=get_nayin(month_gan, month_zhi),
            canggan=bazi.getMonthHideGan(),  # 使用原生方法获取藏干
            shishen=bazi.getMonthShiShenGan(),  # 使用原生方法获取月干十神
            changsheng=bazi.getMonthDiShi(),  # 使用原生方法获取月支地势（十二长生）
            canggan_shishen=bazi.getMonthShiShenZhi(),  # 使用原生方法获取月支藏干十神
            shensha=extract_shensha(lunar, 'month')  # 提取月柱神煞
        )
        
        # 日柱（使用 lunar-python 原生方法）
        day_gan = bazi.getDayGan()
        day_zhi = bazi.getDayZhi()
        day_pillar = Pillar(
            gan=day_gan,
            zhi=day_zhi,
            nayin=get_nayin(day_gan, day_zhi),
            canggan=bazi.getDayHideGan(),  # 使用原生方法获取藏干
            shishen="日主",  # 日干固定为日主
            changsheng=bazi.getDayDiShi(),  # 使用原生方法获取日支地势（十二长生）
            canggan_shishen=bazi.getDayShiShenZhi(),  # 使用原生方法获取日支藏干十神
            shensha=extract_shensha(lunar, 'day')  # 提取日柱神煞
        )
        
        # 时柱（使用 lunar-python 原生方法）
        hour_gan = bazi.getTimeGan()
        hour_zhi = bazi.getTimeZhi()
        hour_pillar = Pillar(
            gan=hour_gan,
            zhi=hour_zhi,
            nayin=get_nayin(hour_gan, hour_zhi),
            canggan=bazi.getTimeHideGan(),  # 使用原生方法获取藏干
            shishen=bazi.getTimeShiShenGan(),  # 使用原生方法获取时干十神
            changsheng=bazi.getTimeDiShi(),  # 使用原生方法获取时支地势（十二长生）
            canggan_shishen=bazi.getTimeShiShenZhi(),  # 使用原生方法获取时支藏干十神
            shensha=extract_shensha(lunar, 'time')  # 提取时柱神煞
        )
        
        # 八字字符串
        bazi_string = f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
        
        # 计算五行强度
        wuxing_strength, wuxing_summary = calculate_wuxing_strength(
            year_pillar, month_pillar, day_pillar, hour_pillar
        )
        
        # 生肖
        shengxiao_index = lunar.getYearZhiIndex()
        shengxiao = SHENGXIAO[shengxiao_index]
        
        # 日主
        day_master = day_gan
        day_master_wuxing = TIANGAN_WUXING.get(day_master, "未知")
        
        # 格式化日期
        solar_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
        lunar_date = f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
        
        # 构建结果
        result = BaziResult(
            solar_date=solar_date,
            lunar_date=lunar_date,
            gender=gender,
            shengxiao=shengxiao,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            bazi_string=bazi_string,
            wuxing_strength=wuxing_strength,
            wuxing_summary=wuxing_summary,
            day_master=day_master,
            day_master_wuxing=day_master_wuxing
        )
        
        return result
        
    except Exception as e:
        raise ValueError(f"八字计算失败: {str(e)}")


# ==================== 辅助函数 ====================

def format_bazi_result(result: BaziResult) -> str:
    """
    格式化八字结果为可读字符串
    
    Args:
        result: 八字结果
        
    Returns:
        格式化的字符串
    """
    lines = [
        "=" * 60,
        "八字排盘结果",
        "=" * 60,
        f"公历: {result.solar_date}",
        f"农历: {result.lunar_date}",
        f"性别: {'男' if result.gender == 1 else '女'}",
        f"生肖: {result.shengxiao}",
        "",
        "四柱八字:",
        f"  年柱: {result.year_pillar.gan}{result.year_pillar.zhi} ({result.year_pillar.nayin})",
        f"        十神: {result.year_pillar.shishen}  长生: {result.year_pillar.changsheng}",
        f"        藏干: {', '.join(result.year_pillar.canggan)}",
        f"        藏干十神: {', '.join(result.year_pillar.canggan_shishen)}",
        f"  月柱: {result.month_pillar.gan}{result.month_pillar.zhi} ({result.month_pillar.nayin})",
        f"        十神: {result.month_pillar.shishen}  长生: {result.month_pillar.changsheng}",
        f"        藏干: {', '.join(result.month_pillar.canggan)}",
        f"        藏干十神: {', '.join(result.month_pillar.canggan_shishen)}",
        f"  日柱: {result.day_pillar.gan}{result.day_pillar.zhi} ({result.day_pillar.nayin})",
        f"        十神: {result.day_pillar.shishen}  长生: {result.day_pillar.changsheng}",
        f"        藏干: {', '.join(result.day_pillar.canggan)}",
        f"        藏干十神: {', '.join(result.day_pillar.canggan_shishen)}",
        f"  时柱: {result.hour_pillar.gan}{result.hour_pillar.zhi} ({result.hour_pillar.nayin})",
        f"        十神: {result.hour_pillar.shishen}  长生: {result.hour_pillar.changsheng}",
        f"        藏干: {', '.join(result.hour_pillar.canggan)}",
        f"        藏干十神: {', '.join(result.hour_pillar.canggan_shishen)}",
        "",
        f"八字: {result.bazi_string}",
        f"日主: {result.day_master} ({result.day_master_wuxing})",
        "",
        "五行强度:",
        f"  金: {result.wuxing_strength.jin}% ({result.wuxing_summary['金']}个)",
        f"  木: {result.wuxing_strength.mu}% ({result.wuxing_summary['木']}个)",
        f"  水: {result.wuxing_strength.shui}% ({result.wuxing_summary['水']}个)",
        f"  火: {result.wuxing_strength.huo}% ({result.wuxing_summary['火']}个)",
        f"  土: {result.wuxing_strength.tu}% ({result.wuxing_summary['土']}个)",
        "=" * 60
    ]
    return "\n".join(lines)


# ==================== 测试函数 ====================

if __name__ == "__main__":
    # 测试示例
    print("测试八字排盘引擎\n")
    
    # 示例 1: 1990年5月15日14时30分 男
    print("示例 1: 1990年5月15日14时30分 男")
    result1 = calculate_full_bazi(1990, 5, 15, 14, 30, 1)
    print(format_bazi_result(result1))
    print()
    
    # 示例 2: 1992年8月20日10时0分 女
    print("示例 2: 1992年8月20日10时0分 女")
    result2 = calculate_full_bazi(1992, 8, 20, 10, 0, 0)
    print(format_bazi_result(result2))
    print()
    
    # 示例 3: JSON 输出
    print("示例 3: JSON 输出")
    import json
    result_dict = result1.to_dict()
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))
