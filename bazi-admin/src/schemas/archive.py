"""
档案相关的 Pydantic Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ArchiveBase(BaseModel):
    """档案基础 Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: int = Field(..., ge=0, le=1, description="性别 (1=男, 0=女)")
    calendar_type: str = Field(default="solar", description="历法类型 (solar/lunar)")
    is_lunar: bool = Field(default=False, description="是否为农历")
    birth_year: int = Field(..., ge=1900, le=2100, description="出生年份")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    birth_day: int = Field(..., ge=1, le=31, description="出生日期")
    birth_hour: int = Field(..., ge=0, le=23, description="出生小时")
    birth_minute: int = Field(default=0, ge=0, le=59, description="出生分钟")
    tags: Optional[str] = Field(None, max_length=200, description="标签 (逗号分隔)")
    is_default: bool = Field(default=False, description="是否为默认档案")


class ArchiveCreate(ArchiveBase):
    """创建档案 Schema"""
    archive_id: str = Field(..., description="档案ID (UUID)")
    local_created_at: int = Field(..., description="本地创建时间戳 (毫秒)")


class ArchiveUpdate(ArchiveBase):
    """更新档案 Schema"""
    local_created_at: int = Field(..., description="本地创建时间戳 (毫秒)")


class ArchiveResponse(ArchiveBase):
    """档案响应 Schema"""
    archive_id: str = Field(..., description="档案ID (UUID)")
    user_id: str = Field(..., description="用户ID (UUID)")
    local_created_at: int = Field(..., description="本地创建时间戳 (毫秒)")
    cloud_uploaded_at: Optional[int] = Field(None, description="云端上传时间戳 (毫秒)")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True  # SQLAlchemy 2.0 新语法


class ArchiveSyncRequest(BaseModel):
    """档案同步请求 Schema"""
    archives: List[ArchiveCreate] = Field(..., description="档案列表")


class ArchiveSyncResponse(BaseModel):
    """档案同步响应 Schema"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    synced_count: int = Field(..., description="同步的档案数量")
    archives: List[ArchiveResponse] = Field(..., description="云端最新档案列表")
