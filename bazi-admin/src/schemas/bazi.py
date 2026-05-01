"""
八字排盘相关的 Pydantic Schema
"""
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求 Schema ====================

class BaziCalculateRequest(BaseModel):
    """八字排盘请求 Schema"""
    archive_id: str = Field(..., description="档案ID (UUID)")
    is_deep_analysis: bool = Field(default=False, description="是否为深度分析")
    name: Optional[str] = Field(default=None, description="命主姓名（可选，优先取档案中的姓名）")


class BaziCalculateByDataRequest(BaseModel):
    """通过原始数据计算八字请求 Schema"""
    name: Optional[str] = Field(default=None, max_length=50, description="姓名（可选）")
    gender: int = Field(..., ge=0, le=1, description="性别 (1=男, 0=女)")
    birth_year: int = Field(..., ge=1000, le=2100, description="出生年份 (公历)")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份 (公历)")
    birth_day: int = Field(..., ge=1, le=31, description="出生日期 (公历)")
    birth_hour: int = Field(..., ge=0, le=23, description="出生小时 (公历)")
    birth_minute: int = Field(default=0, ge=0, le=59, description="出生分钟 (公历)")
    is_deep_analysis: bool = Field(default=False, description="是否为深度分析")


# ==================== 响应 Schema ====================

class PillarResponse(BaseModel):
    """四柱响应 Schema"""
    gan: str = Field(..., description="天干")
    zhi: str = Field(..., description="地支")
    nayin: str = Field(..., description="纳音")
    canggan: List[str] = Field(..., description="藏干")
    
    # 新增字段（可选，兼容历史数据）
    shishen: Optional[str] = Field(default="", description="天干对应的十神（如：偏印、伤官、比肩）")
    changsheng: Optional[str] = Field(default="", description="地支对应的十二长生/地势（如：沐浴、建禄、帝旺）")
    canggan_shishen: Optional[List[str]] = Field(default_factory=list, description="藏干分别对应的十神列表")
    shensha: Optional[List[str]] = Field(default_factory=list, description="神煞列表（如：天乙贵人、文昌贵人、桃花等）")


class WuxingStrengthResponse(BaseModel):
    """五行强度响应 Schema"""
    jin: float = Field(..., description="金 (%)")
    mu: float = Field(..., description="木 (%)")
    shui: float = Field(..., description="水 (%)")
    huo: float = Field(..., description="火 (%)")
    tu: float = Field(..., description="土 (%)")


class BaziCalculateResponse(BaseModel):
    """八字排盘响应 Schema (精简版)"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    record_id: str = Field(..., description="记录ID (UUID)")
    
    # 基础信息
    name: str = Field(..., description="姓名")
    gender: int = Field(..., description="性别 (1=男, 0=女)")
    solar_date: str = Field(..., description="公历日期")
    lunar_date: str = Field(..., description="农历日期")
    shengxiao: str = Field(..., description="生肖")
    
    # 八字信息
    bazi_string: str = Field(..., description="八字字符串")
    year_pillar: PillarResponse = Field(..., description="年柱")
    month_pillar: PillarResponse = Field(..., description="月柱")
    day_pillar: PillarResponse = Field(..., description="日柱")
    hour_pillar: PillarResponse = Field(..., description="时柱")
    
    # 日主
    day_master: str = Field(..., description="日主")
    day_master_wuxing: str = Field(..., description="日主五行")
    
    # 五行分析
    wuxing_strength: WuxingStrengthResponse = Field(..., description="五行强度")
    wuxing_summary: Dict[str, int] = Field(..., description="五行统计")
    
    # AI 报告 (可选)
    ai_report: Optional[str] = Field(None, description="AI 分析报告 (Markdown)")


class RecordResponse(BaseModel):
    """测算记录响应 Schema"""
    record_id: str = Field(..., description="记录ID (UUID)")
    user_id: str = Field(..., description="用户ID (UUID)")
    archive_id: str = Field(..., description="档案ID (UUID)")
    name: Optional[str] = Field(None, description="命主姓名（从档案或 five_elements_json 中取）")
    bazi_str: str = Field(..., description="八字字符串")
    five_elements_json: Optional[Dict] = Field(None, description="五行分析 JSON")
    ai_report_markdown: Optional[str] = Field(None, description="AI 分析报告")
    is_deep_analysis: bool = Field(..., description="是否为深度分析")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True  # SQLAlchemy 2.0 新语法


class RecordListResponse(BaseModel):
    """测算记录列表响应 Schema"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    total: int = Field(..., description="总记录数")
    records: List[RecordResponse] = Field(..., description="记录列表")
