"""
档案相关的路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Archive
from src.schemas.archive import (
    ArchiveSyncRequest,
    ArchiveSyncResponse,
    ArchiveResponse,
)
import time

router = APIRouter(prefix="/api/archives", tags=["档案管理"])


# 临时模拟用户ID (后续接入登录后替换)
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_current_user_id() -> str:
    """
    获取当前用户ID
    TODO: 后续接入登录系统后，从 JWT Token 中解析用户ID
    """
    return MOCK_USER_ID


@router.post("/sync", response_model=ArchiveSyncResponse)
async def sync_archives(
    request: ArchiveSyncRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    档案同步接口 (归宗算法)
    
    功能说明:
    1. 接收前端传来的本地档案数组
    2. 对于每个档案:
       - 如果数据库中不存在，执行 INSERT
       - 如果数据库中已存在，对比 local_created_at
       - 只有当请求中的时间戳更晚时，才执行 UPDATE
    3. 返回该用户在云端的所有最新档案列表
    
    Args:
        request: 档案同步请求，包含档案列表
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        同步结果和云端最新档案列表
    """
    synced_count = 0
    current_timestamp = int(time.time() * 1000)  # 当前时间戳 (毫秒)
    
    try:
        # 遍历前端传来的档案列表
        for archive_data in request.archives:
            # 查询数据库中是否已存在该档案
            stmt = select(Archive).where(Archive.archive_id == archive_data.archive_id)
            result = await db.execute(stmt)
            existing_archive = result.scalar_one_or_none()
            
            if existing_archive is None:
                # 档案不存在，执行 INSERT
                new_archive = Archive(
                    archive_id=archive_data.archive_id,
                    user_id=user_id,
                    name=archive_data.name,
                    gender=archive_data.gender,
                    calendar_type=archive_data.calendar_type,
                    birth_year=archive_data.birth_year,
                    birth_month=archive_data.birth_month,
                    birth_day=archive_data.birth_day,
                    birth_hour=archive_data.birth_hour,
                    birth_minute=archive_data.birth_minute,
                    tags=archive_data.tags,
                    is_default=archive_data.is_default,
                    local_created_at=archive_data.local_created_at,
                    cloud_uploaded_at=current_timestamp,
                )
                db.add(new_archive)
                synced_count += 1
                
            else:
                # 档案已存在，对比时间戳
                if archive_data.local_created_at > existing_archive.local_created_at:
                    # 请求中的时间戳更晚，执行 UPDATE
                    existing_archive.name = archive_data.name
                    existing_archive.gender = archive_data.gender
                    existing_archive.calendar_type = archive_data.calendar_type
                    existing_archive.birth_year = archive_data.birth_year
                    existing_archive.birth_month = archive_data.birth_month
                    existing_archive.birth_day = archive_data.birth_day
                    existing_archive.birth_hour = archive_data.birth_hour
                    existing_archive.birth_minute = archive_data.birth_minute
                    existing_archive.tags = archive_data.tags
                    existing_archive.is_default = archive_data.is_default
                    existing_archive.local_created_at = archive_data.local_created_at
                    existing_archive.cloud_uploaded_at = current_timestamp
                    synced_count += 1
                # 如果请求中的时间戳更早或相等，不做任何操作
        
        # 提交事务
        await db.commit()
        
        # 查询该用户在云端的所有最新档案
        stmt = select(Archive).where(Archive.user_id == user_id).order_by(
            Archive.is_default.desc(),  # 默认档案排在前面
            Archive.created_at.desc()   # 按创建时间倒序
        )
        result = await db.execute(stmt)
        all_archives = result.scalars().all()
        
        # 转换为响应格式
        archive_responses = [
            ArchiveResponse.model_validate(archive) for archive in all_archives
        ]
        
        return ArchiveSyncResponse(
            success=True,
            message=f"同步成功，共处理 {len(request.archives)} 个档案，实际同步 {synced_count} 个",
            synced_count=synced_count,
            archives=archive_responses,
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"档案同步失败: {str(e)}"
        )


@router.get("/list", response_model=List[ArchiveResponse])
async def get_archives(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取用户的所有档案列表
    
    Args:
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        档案列表
    """
    try:
        stmt = select(Archive).where(Archive.user_id == user_id).order_by(
            Archive.is_default.desc(),
            Archive.created_at.desc()
        )
        result = await db.execute(stmt)
        archives = result.scalars().all()
        
        return [ArchiveResponse.model_validate(archive) for archive in archives]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取档案列表失败: {str(e)}"
        )


@router.delete("/{archive_id}")
async def delete_archive(
    archive_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    删除指定档案
    
    Args:
        archive_id: 档案ID
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        删除结果
    """
    try:
        # 查询档案
        stmt = select(Archive).where(
            Archive.archive_id == archive_id,
            Archive.user_id == user_id
        )
        result = await db.execute(stmt)
        archive = result.scalar_one_or_none()
        
        if archive is None:
            raise HTTPException(status_code=404, detail="档案不存在")
        
        # 删除档案
        await db.delete(archive)
        await db.commit()
        
        return {
            "success": True,
            "message": "档案删除成功",
            "archive_id": archive_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除档案失败: {str(e)}"
        )
