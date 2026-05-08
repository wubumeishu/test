"""
档案相关的路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.database import get_db
from src.models import Archive, User
from src.schemas.archive import (
    ArchiveSyncRequest,
    ArchiveSyncResponse,
    ArchiveResponse,
)
from src.api.deps import get_current_user
import time

router = APIRouter(prefix="/api/archives", tags=["档案管理"])


async def _clear_other_defaults(db: AsyncSession, user_id: str, exclude_archive_id: str) -> None:
    """
    DB 级防脏数据：将指定用户下除 exclude_archive_id 以外的所有档案的
    is_default 强制置为 False，确保每个用户最多只有一条默认档案记录。
    调用方负责在同一事务中 commit。
    """
    stmt = (
        update(Archive)
        .where(
            Archive.user_id == user_id,
            Archive.archive_id != exclude_archive_id,
            Archive.is_default == True,   # noqa: E712  仅更新有脏数据的行，减少写放大
        )
        .values(is_default=False)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)


@router.post("/sync", response_model=ArchiveSyncResponse)
async def sync_archives(
    request: ArchiveSyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    档案同步接口 (归宗算法)
    
    功能说明:
    1. 接收前端传来的本地档案数组
    2. 对于每个档案:
       - 如果数据库中不存在，执行 INSERT
       - 如果数据库中已存在，对比 local_created_at
       - 只有当请求中的时间戳更晚时，才执行 UPDATE
    3. 若某条档案的 is_default=True，先在 DB 层清零该用户其他档案的默认标记
    4. 返回该用户在云端的所有最新档案列表
    
    **数据隔离**: 只能同步当前登录用户的档案
    
    Args:
        request: 档案同步请求，包含档案列表
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        同步结果和云端最新档案列表
    """
    user_id = current_user.user_id
    synced_count = 0
    current_timestamp = int(time.time() * 1000)  # 当前时间戳 (毫秒)
    
    try:
        # 遍历前端传来的档案列表
        for archive_data in request.archives:
            # 查询数据库中是否已存在该档案（强制带上 user_id 条件）
            stmt = select(Archive).where(
                Archive.archive_id == archive_data.archive_id,
                Archive.user_id == user_id  # 数据隔离：只查询当前用户的档案
            )
            result = await db.execute(stmt)
            existing_archive = result.scalar_one_or_none()
            
            if existing_archive is None:
                # ── DB 级防脏数据：新建档案若为默认，先清零其他档案 ──
                if archive_data.is_default:
                    await _clear_other_defaults(db, user_id, archive_data.archive_id)

                # 档案不存在，执行 INSERT（强制写入当前用户的 ID）
                new_archive = Archive(
                    archive_id=archive_data.archive_id,
                    user_id=user_id,  # 数据隔离：强制写入当前用户 ID
                    name=archive_data.name,
                    gender=archive_data.gender,
                    calendar_type=archive_data.calendar_type,
                    is_lunar=archive_data.calendar_type == "lunar",
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
                print(f"✅ [archive] 新建档案: {archive_data.name} (用户: {user_id})")
                
            else:
                # 档案已存在，对比时间戳
                if archive_data.local_created_at > existing_archive.local_created_at:
                    # ── DB 级防脏数据：更新档案若为默认，先清零其他档案 ──
                    if archive_data.is_default:
                        await _clear_other_defaults(db, user_id, archive_data.archive_id)

                    # 请求中的时间戳更晚，执行 UPDATE
                    existing_archive.name = archive_data.name
                    existing_archive.gender = archive_data.gender
                    existing_archive.calendar_type = archive_data.calendar_type
                    existing_archive.is_lunar = archive_data.calendar_type == "lunar"
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
                    print(f"✅ [archive] 更新档案: {archive_data.name} (用户: {user_id})")
                else:
                    # 时间戳未推进，但若该档案携带 is_default=False（清洗写回），
                    # 仍需强制更新 is_default，防止清洗结果被时间戳门槛拦截
                    if not archive_data.is_default and existing_archive.is_default:
                        existing_archive.is_default = False
                        existing_archive.cloud_uploaded_at = current_timestamp
                        synced_count += 1
        
        # 提交事务（_clear_other_defaults 与所有 INSERT/UPDATE 在同一事务内）
        await db.commit()
        
        # 查询该用户在云端的所有最新档案（强制带上 user_id 条件）
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
        
        print(f"✅ [archive] 同步完成，用户 {user_id} 共有 {len(all_archives)} 个档案")
        
        return ArchiveSyncResponse(
            success=True,
            message=f"同步成功，共处理 {len(request.archives)} 个档案，实际同步 {synced_count} 个",
            synced_count=synced_count,
            archives=archive_responses,
        )
        
    except Exception as e:
        await db.rollback()
        print(f"❌ [archive] 同步失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"档案同步失败: {str(e)}"
        )


@router.get("/list", response_model=List[ArchiveResponse])
async def get_archives(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的所有档案列表
    
    **数据隔离**: 只返回当前登录用户的档案
    
    Args:
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        档案列表
    """
    try:
        user_id = current_user.user_id
        
        # 强制带上 user_id 条件，只查询当前用户的档案
        stmt = select(Archive).where(Archive.user_id == user_id).order_by(
            Archive.is_default.desc(),
            Archive.created_at.desc()
        )
        result = await db.execute(stmt)
        archives = result.scalars().all()
        
        print(f"✅ [archive] 查询档案列表，用户 {user_id} 共有 {len(archives)} 个档案")
        
        return [ArchiveResponse.model_validate(archive) for archive in archives]
        
    except Exception as e:
        print(f"❌ [archive] 查询档案列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取档案列表失败: {str(e)}"
        )


@router.delete("/{archive_id}")
async def delete_archive(
    archive_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除指定档案
    
    **数据隔离**: 只能删除当前登录用户的档案
    
    Args:
        archive_id: 档案ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    try:
        user_id = current_user.user_id
        
        # 查询档案（强制带上 user_id 条件）
        stmt = select(Archive).where(
            Archive.archive_id == archive_id,
            Archive.user_id == user_id  # 数据隔离：只能删除自己的档案
        )
        result = await db.execute(stmt)
        archive = result.scalar_one_or_none()
        
        if archive is None:
            raise HTTPException(status_code=404, detail="档案不存在或无权访问")
        
        # 删除档案
        await db.delete(archive)
        await db.commit()
        
        print(f"✅ [archive] 删除档案成功: {archive_id} (用户: {user_id})")
        
        return {
            "success": True,
            "message": "档案删除成功",
            "archive_id": archive_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ [archive] 删除档案失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"删除档案失败: {str(e)}"
        )
