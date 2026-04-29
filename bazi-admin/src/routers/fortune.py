"""
八字排盘相关的路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import Archive, Record
from src.schemas.bazi import (
    BaziCalculateRequest,
    BaziCalculateByDataRequest,
    BaziCalculateResponse,
    RecordListResponse,
    RecordResponse,
    PillarResponse,
    WuxingStrengthResponse,
)
from src.services.bazi_engine import calculate_full_bazi, BaziResult
from uuid import uuid4

router = APIRouter(prefix="/api/fortune", tags=["八字排盘"])


# 临时模拟用户ID (后续接入登录后替换)
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


async def get_current_user_id() -> str:
    """
    获取当前用户ID
    TODO: 后续接入登录系统后，从 JWT Token 中解析用户ID
    """
    return MOCK_USER_ID


def convert_bazi_result_to_response(
    result: BaziResult,
    record_id: str,
    name: str,
    ai_report: str = None
) -> BaziCalculateResponse:
    """
    将 BaziResult 转换为 API 响应格式
    
    Args:
        result: 八字计算结果
        record_id: 记录ID
        name: 姓名
        ai_report: AI 分析报告 (可选)
        
    Returns:
        API 响应对象
    """
    return BaziCalculateResponse(
        success=True,
        message="八字排盘成功",
        record_id=record_id,
        name=name,
        gender=result.gender,
        solar_date=result.solar_date,
        lunar_date=result.lunar_date,
        shengxiao=result.shengxiao,
        bazi_string=result.bazi_string,
        year_pillar=PillarResponse(
            gan=result.year_pillar.gan,
            zhi=result.year_pillar.zhi,
            nayin=result.year_pillar.nayin,
            canggan=result.year_pillar.canggan,
            shishen=result.year_pillar.shishen,
            changsheng=result.year_pillar.changsheng,
            canggan_shishen=result.year_pillar.canggan_shishen,
            shensha=result.year_pillar.shensha,
        ),
        month_pillar=PillarResponse(
            gan=result.month_pillar.gan,
            zhi=result.month_pillar.zhi,
            nayin=result.month_pillar.nayin,
            canggan=result.month_pillar.canggan,
            shishen=result.month_pillar.shishen,
            changsheng=result.month_pillar.changsheng,
            canggan_shishen=result.month_pillar.canggan_shishen,
            shensha=result.month_pillar.shensha,
        ),
        day_pillar=PillarResponse(
            gan=result.day_pillar.gan,
            zhi=result.day_pillar.zhi,
            nayin=result.day_pillar.nayin,
            canggan=result.day_pillar.canggan,
            shishen=result.day_pillar.shishen,
            changsheng=result.day_pillar.changsheng,
            canggan_shishen=result.day_pillar.canggan_shishen,
            shensha=result.day_pillar.shensha,
        ),
        hour_pillar=PillarResponse(
            gan=result.hour_pillar.gan,
            zhi=result.hour_pillar.zhi,
            nayin=result.hour_pillar.nayin,
            canggan=result.hour_pillar.canggan,
            shishen=result.hour_pillar.shishen,
            changsheng=result.hour_pillar.changsheng,
            canggan_shishen=result.hour_pillar.canggan_shishen,
            shensha=result.hour_pillar.shensha,
        ),
        day_master=result.day_master,
        day_master_wuxing=result.day_master_wuxing,
        wuxing_strength=WuxingStrengthResponse(
            jin=result.wuxing_strength.jin,
            mu=result.wuxing_strength.mu,
            shui=result.wuxing_strength.shui,
            huo=result.wuxing_strength.huo,
            tu=result.wuxing_strength.tu,
        ),
        wuxing_summary=result.wuxing_summary,
        ai_report=ai_report,
    )


@router.post("/calculate", response_model=BaziCalculateResponse)
async def calculate_bazi(
    request: BaziCalculateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    八字排盘接口 (通过档案ID)
    
    功能说明:
    1. 根据档案ID查询档案信息
    2. 调用 bazi_engine.py 进行八字计算
    3. 将计算结果存入 records 表
    4. 返回精简的排盘数据供前端展示
    
    Args:
        request: 排盘请求，包含档案ID
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        八字排盘结果
    """
    try:
        print(f"🔄 [fortune] 开始排盘，档案ID: {request.archive_id}")
        
        # 1. 查询档案信息
        stmt = select(Archive).where(Archive.archive_id == request.archive_id)
        result = await db.execute(stmt)
        archive = result.scalar_one_or_none()
        
        # 判空逻辑：如果查不到档案，返回 404
        if archive is None:
            print(f"❌ [fortune] 档案不存在: {request.archive_id}")
            raise HTTPException(status_code=404, detail="未找到该档案")
        
        print(f"✅ [fortune] 找到档案: {archive.name}, 性别: {archive.gender}")
        print(f"📅 [fortune] 出生日期: {archive.birth_year}-{archive.birth_month}-{archive.birth_day} {archive.birth_hour}:{archive.birth_minute}")
        
        # 2. 检查历法类型
        if archive.calendar_type != "solar":
            print(f"⚠️ [fortune] 不支持的历法类型: {archive.calendar_type}")
            raise HTTPException(
                status_code=400,
                detail="暂不支持农历，请使用公历日期"
            )
        
        # 3. 字段类型转换（确保所有参数都是 int 类型）
        try:
            birth_year = int(archive.birth_year)
            birth_month = int(archive.birth_month)
            birth_day = int(archive.birth_day)
            birth_hour = int(archive.birth_hour)
            birth_minute = int(archive.birth_minute)
            gender = int(archive.gender)
            
            print(f"🔢 [fortune] 类型转换成功: year={birth_year}, month={birth_month}, day={birth_day}, hour={birth_hour}, minute={birth_minute}, gender={gender}")
        except (ValueError, TypeError) as e:
            print(f"❌ [fortune] 日期字段类型转换失败: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"档案数据格式错误: {str(e)}"
            )
        
        # 4. 调用八字计算引擎
        try:
            print(f"🧮 [fortune] 开始调用八字计算引擎...")
            bazi_result = calculate_full_bazi(
                year=birth_year,
                month=birth_month,
                day=birth_day,
                hour=birth_hour,
                minute=birth_minute,
                gender=gender
            )
            print(f"✅ [fortune] 八字计算成功: {bazi_result.bazi_string}")
        except ValueError as e:
            print(f"❌ [fortune] 日期验证失败: {e}")
            raise HTTPException(status_code=400, detail=f"日期验证失败: {str(e)}")
        except Exception as e:
            print(f"❌ [fortune] 八字计算引擎异常: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"八字计算失败: {str(e)}"
            )
        
        # 5. 准备存储到数据库的数据
        record_id = str(uuid4())
        
        # JSONB 序列化：将完整的八字结果转换为可 JSON 序列化的字典
        try:
            five_elements_json = {
                "solar_date": bazi_result.solar_date,
                "lunar_date": bazi_result.lunar_date,
                "shengxiao": bazi_result.shengxiao,
                "year_pillar": {
                    "gan": bazi_result.year_pillar.gan,
                    "zhi": bazi_result.year_pillar.zhi,
                    "nayin": bazi_result.year_pillar.nayin,
                    "canggan": bazi_result.year_pillar.canggan,
                    "shishen": bazi_result.year_pillar.shishen,
                    "changsheng": bazi_result.year_pillar.changsheng,
                    "canggan_shishen": bazi_result.year_pillar.canggan_shishen,
                },
                "month_pillar": {
                    "gan": bazi_result.month_pillar.gan,
                    "zhi": bazi_result.month_pillar.zhi,
                    "nayin": bazi_result.month_pillar.nayin,
                    "canggan": bazi_result.month_pillar.canggan,
                    "shishen": bazi_result.month_pillar.shishen,
                    "changsheng": bazi_result.month_pillar.changsheng,
                    "canggan_shishen": bazi_result.month_pillar.canggan_shishen,
                },
                "day_pillar": {
                    "gan": bazi_result.day_pillar.gan,
                    "zhi": bazi_result.day_pillar.zhi,
                    "nayin": bazi_result.day_pillar.nayin,
                    "canggan": bazi_result.day_pillar.canggan,
                    "shishen": bazi_result.day_pillar.shishen,
                    "changsheng": bazi_result.day_pillar.changsheng,
                    "canggan_shishen": bazi_result.day_pillar.canggan_shishen,
                },
                "hour_pillar": {
                    "gan": bazi_result.hour_pillar.gan,
                    "zhi": bazi_result.hour_pillar.zhi,
                    "nayin": bazi_result.hour_pillar.nayin,
                    "canggan": bazi_result.hour_pillar.canggan,
                    "shishen": bazi_result.hour_pillar.shishen,
                    "changsheng": bazi_result.hour_pillar.changsheng,
                    "canggan_shishen": bazi_result.hour_pillar.canggan_shishen,
                },
                "day_master": bazi_result.day_master,
                "day_master_wuxing": bazi_result.day_master_wuxing,
                "wuxing_strength": {
                    "jin": float(bazi_result.wuxing_strength.jin),
                    "mu": float(bazi_result.wuxing_strength.mu),
                    "shui": float(bazi_result.wuxing_strength.shui),
                    "huo": float(bazi_result.wuxing_strength.huo),
                    "tu": float(bazi_result.wuxing_strength.tu),
                },
                "wuxing_summary": dict(bazi_result.wuxing_summary),
            }
            print(f"✅ [fortune] JSONB 序列化成功")
        except Exception as e:
            print(f"❌ [fortune] JSONB 序列化失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"数据序列化失败: {str(e)}"
            )
        
        # 6. AI 报告（如果需要深度分析）
        ai_report = None
        if request.is_deep_analysis:
            ai_report = "AI 深度分析报告 (待接入大模型)"
            print(f"📝 [fortune] 深度分析已启用")
        
        # 7. 存入数据库
        try:
            print(f"💾 [fortune] 开始存入数据库...")
            new_record = Record(
                record_id=record_id,
                user_id=user_id,
                archive_id=request.archive_id,
                bazi_str=bazi_result.bazi_string,
                five_elements_json=five_elements_json,
                ai_report_markdown=ai_report,
                is_deep_analysis=request.is_deep_analysis,
            )
            db.add(new_record)
            await db.commit()
            await db.refresh(new_record)
            print(f"✅ [fortune] 数据库存储成功，记录ID: {record_id}")
        except Exception as e:
            print(f"❌ [fortune] 数据库存储失败: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"数据库存储失败: {str(e)}"
            )
        
        # 8. 返回精简的排盘数据
        response = convert_bazi_result_to_response(
            result=bazi_result,
            record_id=record_id,
            name=archive.name,
            ai_report=ai_report,
        )
        
        print(f"🎉 [fortune] 排盘完成，返回结果")
        return response
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获所有其他异常
        print(f"❌ [fortune] 未预期的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"排盘失败: {type(e).__name__}: {str(e)}"
        )


@router.post("/calculate-by-data", response_model=BaziCalculateResponse)
async def calculate_bazi_by_data(
    request: BaziCalculateByDataRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    八字排盘接口 (通过原始数据)
    
    功能说明:
    1. 直接接收生辰数据
    2. 调用 bazi_engine.py 进行八字计算
    3. 不存入档案表，但存入 records 表 (archive_id 为空)
    4. 返回精简的排盘数据供前端展示
    
    注意: 此接口用于临时计算，不会创建档案
    
    Args:
        request: 排盘请求，包含生辰数据
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        八字排盘结果
    """
    try:
        print(f"🔄 [fortune] 开始快速排盘，姓名: {request.name}")
        print(f"📅 [fortune] 出生日期: {request.birth_year}-{request.birth_month}-{request.birth_day} {request.birth_hour}:{request.birth_minute}")
        
        # 1. 字段类型转换（确保所有参数都是 int 类型）
        try:
            birth_year = int(request.birth_year)
            birth_month = int(request.birth_month)
            birth_day = int(request.birth_day)
            birth_hour = int(request.birth_hour)
            birth_minute = int(request.birth_minute)
            gender = int(request.gender)
            
            print(f"🔢 [fortune] 类型转换成功: year={birth_year}, month={birth_month}, day={birth_day}, hour={birth_hour}, minute={birth_minute}, gender={gender}")
        except (ValueError, TypeError) as e:
            print(f"❌ [fortune] 日期字段类型转换失败: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"数据格式错误: {str(e)}"
            )
        
        # 2. 调用八字计算引擎
        try:
            print(f"🧮 [fortune] 开始调用八字计算引擎...")
            bazi_result = calculate_full_bazi(
                year=birth_year,
                month=birth_month,
                day=birth_day,
                hour=birth_hour,
                minute=birth_minute,
                gender=gender
            )
            print(f"✅ [fortune] 八字计算成功: {bazi_result.bazi_string}")
        except ValueError as e:
            print(f"❌ [fortune] 日期验证失败: {e}")
            raise HTTPException(status_code=400, detail=f"日期验证失败: {str(e)}")
        except Exception as e:
            print(f"❌ [fortune] 八字计算引擎异常: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"八字计算失败: {str(e)}"
            )
        
        # 3. 准备存储到数据库的数据
        record_id = str(uuid4())
        
        # JSONB 序列化：将完整的八字结果转换为可 JSON 序列化的字典
        try:
            five_elements_json = {
                "solar_date": bazi_result.solar_date,
                "lunar_date": bazi_result.lunar_date,
                "shengxiao": bazi_result.shengxiao,
                "year_pillar": {
                    "gan": bazi_result.year_pillar.gan,
                    "zhi": bazi_result.year_pillar.zhi,
                    "nayin": bazi_result.year_pillar.nayin,
                    "canggan": bazi_result.year_pillar.canggan,
                    "shishen": bazi_result.year_pillar.shishen,
                    "changsheng": bazi_result.year_pillar.changsheng,
                    "canggan_shishen": bazi_result.year_pillar.canggan_shishen,
                },
                "month_pillar": {
                    "gan": bazi_result.month_pillar.gan,
                    "zhi": bazi_result.month_pillar.zhi,
                    "nayin": bazi_result.month_pillar.nayin,
                    "canggan": bazi_result.month_pillar.canggan,
                    "shishen": bazi_result.month_pillar.shishen,
                    "changsheng": bazi_result.month_pillar.changsheng,
                    "canggan_shishen": bazi_result.month_pillar.canggan_shishen,
                },
                "day_pillar": {
                    "gan": bazi_result.day_pillar.gan,
                    "zhi": bazi_result.day_pillar.zhi,
                    "nayin": bazi_result.day_pillar.nayin,
                    "canggan": bazi_result.day_pillar.canggan,
                    "shishen": bazi_result.day_pillar.shishen,
                    "changsheng": bazi_result.day_pillar.changsheng,
                    "canggan_shishen": bazi_result.day_pillar.canggan_shishen,
                },
                "hour_pillar": {
                    "gan": bazi_result.hour_pillar.gan,
                    "zhi": bazi_result.hour_pillar.zhi,
                    "nayin": bazi_result.hour_pillar.nayin,
                    "canggan": bazi_result.hour_pillar.canggan,
                    "shishen": bazi_result.hour_pillar.shishen,
                    "changsheng": bazi_result.hour_pillar.changsheng,
                    "canggan_shishen": bazi_result.hour_pillar.canggan_shishen,
                },
                "day_master": bazi_result.day_master,
                "day_master_wuxing": bazi_result.day_master_wuxing,
                "wuxing_strength": {
                    "jin": float(bazi_result.wuxing_strength.jin),
                    "mu": float(bazi_result.wuxing_strength.mu),
                    "shui": float(bazi_result.wuxing_strength.shui),
                    "huo": float(bazi_result.wuxing_strength.huo),
                    "tu": float(bazi_result.wuxing_strength.tu),
                },
                "wuxing_summary": dict(bazi_result.wuxing_summary),
            }
            print(f"✅ [fortune] JSONB 序列化成功")
        except Exception as e:
            print(f"❌ [fortune] JSONB 序列化失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"数据序列化失败: {str(e)}"
            )
        
        # 4. AI 报告（如果需要深度分析）
        ai_report = None
        if request.is_deep_analysis:
            ai_report = "AI 深度分析报告 (待接入大模型)"
            print(f"📝 [fortune] 深度分析已启用")
        
        # 5. 返回精简的排盘数据（快速排盘不存入数据库）
        response = convert_bazi_result_to_response(
            result=bazi_result,
            record_id=record_id,
            name=request.name,
            ai_report=ai_report,
        )
        
        print(f"🎉 [fortune] 快速排盘完成，返回结果")
        return response
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获所有其他异常
        print(f"❌ [fortune] 未预期的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"排盘失败: {type(e).__name__}: {str(e)}"
        )


@router.get("/records", response_model=RecordListResponse)
async def get_records(
    archive_id: str = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取测算记录列表
    
    Args:
        archive_id: 档案ID (可选，用于筛选)
        limit: 每页数量
        offset: 偏移量
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        测算记录列表
    """
    try:
        # 构建查询
        stmt = select(Record).where(Record.user_id == user_id)
        
        if archive_id:
            stmt = stmt.where(Record.archive_id == archive_id)
        
        stmt = stmt.order_by(Record.created_at.desc()).limit(limit).offset(offset)
        
        # 执行查询
        result = await db.execute(stmt)
        records = result.scalars().all()
        
        # 统计总数
        count_stmt = select(Record).where(Record.user_id == user_id)
        if archive_id:
            count_stmt = count_stmt.where(Record.archive_id == archive_id)
        
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        return RecordListResponse(
            success=True,
            message="获取记录成功",
            total=total,
            records=[RecordResponse.model_validate(record) for record in records],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取记录失败: {str(e)}"
        )


@router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取单个测算记录详情
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        测算记录详情
    """
    try:
        stmt = select(Record).where(
            Record.record_id == record_id,
            Record.user_id == user_id
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if record is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        return RecordResponse.model_validate(record)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取记录失败: {str(e)}"
        )


@router.delete("/records/{record_id}")
async def delete_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    删除测算记录
    
    Args:
        record_id: 记录ID
        db: 数据库会话
        user_id: 当前用户ID
        
    Returns:
        删除结果
    """
    try:
        stmt = select(Record).where(
            Record.record_id == record_id,
            Record.user_id == user_id
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if record is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        await db.delete(record)
        await db.commit()
        
        return {
            "success": True,
            "message": "记录删除成功",
            "record_id": record_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除记录失败: {str(e)}"
        )
