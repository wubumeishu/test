"""
认证相关路由
提供手机号登录、Token 刷新等功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import random
import redis.asyncio as redis

from src.database import get_db
from src.models.user import User
from src.schemas.auth import (
    PhoneLoginRequest, TokenResponse, UserInfoResponse,
    SendCodeRequest, SendCodeResponse, 
    LoginRequest, PasswordLoginRequest, RegisterRequest,
    LoginResponse, UserInfo
)
from src.core.security import (
    create_access_token, get_password_hash, verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.core.redis import get_redis
from src.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ==================== 验证码相关接口 ====================

@router.post("/send-code", response_model=SendCodeResponse, summary="发送验证码")
async def send_verification_code(
    request: SendCodeRequest,
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    发送验证码接口
    
    - 生成 6 位随机数字验证码
    - 存入 Redis（Key: login_code:{phone}，过期时间: 5 分钟）
    - 联调阶段：直接在控制台打印验证码，不真实发送短信
    
    **注意**: 生产环境请集成真实的短信服务（如阿里云、腾讯云）
    """
    phone = request.phone
    
    # 生成 6 位随机验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # 存入 Redis，5 分钟过期
    redis_key = f"login_code:{phone}"
    await redis_client.setex(redis_key, 300, code)  # 300 秒 = 5 分钟
    
    # 联调阶段：打印验证码到控制台
    print("=" * 60)
    print(f"📱 验证码发送成功（模拟）")
    print(f"   手机号: {phone}")
    print(f"   验证码: {code}")
    print(f"   有效期: 5 分钟")
    print("=" * 60)
    
    return SendCodeResponse(msg="验证码已发送")


@router.post("/register", response_model=LoginResponse, summary="注册新用户")
async def register_user(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    注册新用户接口
    
    - 验证手机号和验证码
    - 将密码哈希加密后存入数据库
    - 创建新用户并返回 JWT Token
    
    **流程**:
    1. 从 Redis 读取验证码
    2. 验证码比对
    3. 检查手机号是否已注册
    4. 密码哈希加密
    5. 创建新用户
    6. 生成 JWT Token
    7. 返回注册信息
    """
    phone = request.phone
    code = request.code
    password = request.password
    
    # 从 Redis 读取验证码
    redis_key = f"login_code:{phone}"
    stored_code = await redis_client.get(redis_key)
    
    # 验证码不存在或已过期
    if stored_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期或不存在，请重新获取"
        )
    
    # 验证码错误
    if stored_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 验证成功，删除 Redis 中的验证码（防止重复使用）
    await redis_client.delete(redis_key)
    
    # 检查手机号是否已注册
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册，请直接登录"
        )
    
    # 密码哈希加密
    hashed_password = get_password_hash(password)
    
    # 创建新用户
    user = User(
        user_id=str(uuid4()),
        phone=phone,
        nickname=f"用户{phone[-4:]}",  # 默认昵称：用户+手机号后4位
        hashed_password=hashed_password,
        last_login=datetime.utcnow()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    print(f"✅ 新用户注册成功: {user.user_id} ({phone})")
    
    # 生成 JWT Access Token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 返回注册信息
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.user_id,
            phone=user.phone,
            nickname=user.nickname
        )
    )


@router.post("/login", response_model=LoginResponse, summary="密码登录")
async def login_with_password(
    request: PasswordLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    密码登录接口
    
    - 验证手机号和密码
    - 生成 JWT Token 并返回用户信息
    
    **流程**:
    1. 查询用户
    2. 验证密码
    3. 生成 JWT Token
    4. 返回登录信息
    """
    phone = request.phone
    password = request.password
    
    # 查询用户是否存在
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    user = result.scalar_one_or_none()
    
    # 用户不存在
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号或密码错误"
        )
    
    # 用户未设置密码（旧用户）
    if user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该账号未设置密码，请使用验证码登录或重置密码"
        )
    
    # 验证密码
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号或密码错误"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.commit()
    print(f"✅ 用户登录成功: {user.user_id} ({phone})")
    
    # 生成 JWT Access Token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 返回登录信息
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.user_id,
            phone=user.phone,
            nickname=user.nickname
        )
    )


@router.post("/login/code", response_model=LoginResponse, summary="验证码登录（旧版兼容）")
async def login_with_code(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    验证码登录接口
    
    - 验证手机号和验证码
    - 如果手机号不存在，自动注册新用户（静默注册）
    - 生成 JWT Token 并返回用户信息
    
    **流程**:
    1. 从 Redis 读取验证码
    2. 验证码比对
    3. 查询或创建用户
    4. 生成 JWT Token
    5. 返回登录信息
    """
    phone = request.phone
    code = request.code
    
    # 从 Redis 读取验证码
    redis_key = f"login_code:{phone}"
    stored_code = await redis_client.get(redis_key)
    
    # 验证码不存在或已过期
    if stored_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期或不存在，请重新获取"
        )
    
    # 验证码错误
    if stored_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 验证成功，删除 Redis 中的验证码（防止重复使用）
    await redis_client.delete(redis_key)
    
    # 查询用户是否存在
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    user = result.scalar_one_or_none()
    
    # 如果用户不存在，自动注册（静默注册）
    if user is None:
        user = User(
            user_id=str(uuid4()),
            phone=phone,
            nickname=f"用户{phone[-4:]}",  # 默认昵称：用户+手机号后4位
            last_login=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ 新用户注册成功: {user.user_id} ({phone})")
    else:
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        print(f"✅ 用户登录成功: {user.user_id} ({phone})")
    
    # 生成 JWT Access Token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 返回登录信息
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.user_id,
            phone=user.phone,
            nickname=user.nickname
        )
    )


# ==================== 旧版接口（保留兼容） ====================


@router.post("/login/phone", response_model=TokenResponse, summary="手机号登录")
async def login_by_phone(
    request: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号登录接口
    
    - 如果手机号已注册，直接登录并返回 Token
    - 如果手机号未注册，自动创建新用户并返回 Token
    - 更新用户的 last_login 时间
    
    **注意**: 当前版本未实现短信验证码验证，生产环境请务必添加！
    """
    phone = request.phone
    
    # 查询用户是否存在
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    user = result.scalar_one_or_none()
    
    # 如果用户不存在，自动注册
    if user is None:
        user = User(
            user_id=str(uuid4()),
            phone=phone,
            nickname=f"用户{phone[-4:]}",  # 默认昵称：用户+手机号后4位
            last_login=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ 新用户注册成功: {user.user_id} ({phone})")
    else:
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        print(f"✅ 用户登录成功: {user.user_id} ({phone})")
    
    # 创建 Access Token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        nickname=user.nickname
    )


@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户的详细信息
    
    需要在请求头中携带有效的 JWT Token:
    ```
    Authorization: Bearer <your_token>
    ```
    """
    return UserInfoResponse(
        user_id=current_user.user_id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    刷新 Access Token
    
    使用当前有效的 Token 换取新的 Token，延长登录有效期。
    """
    # 创建新的 Access Token
    access_token = create_access_token(
        data={"sub": current_user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=current_user.user_id,
        nickname=current_user.nickname
    )
