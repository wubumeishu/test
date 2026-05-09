"""
认证路由 (v3.0)

路由列表：
  POST /api/auth/login/wechat    微信静默登录（code → OpenID）
  POST /api/auth/login/phone     手机号 + 短信验证码登录/注册
  POST /api/auth/login/password  手机号 + 密码登录（兼容旧版）
  POST /api/auth/send-sms-code   发送短信验证码（含防刷限流）
  PUT  /api/auth/profile         更新用户资料（昵称/头像/绑定手机号）
  GET  /api/auth/me              获取当前用户信息
  POST /api/auth/refresh         刷新 Token

账号合并规则（防串号核心）：
  - 微信 OpenID 是系统绝对信任的唯一标识
  - 手机号由用户在系统内主动绑定，不信任微信动态手机号接口
  - 先微信登录 + 后绑定手机号 → 直接写入 phone 字段
  - 先短信登录 + 后微信登录 → 检查 OpenID 对应手机号是否与已有账号一致
      一致 → merge（将 openid 写入已有账号）
      不一致 → 提示用户确认
"""
import os
import random
import certifi
import httpx
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import redis.asyncio as redis

from src.database import get_db
from src.models.user import User
from src.schemas.auth import (
    WechatLoginRequest,
    PhoneLoginRequest,
    PasswordLoginRequest,
    RegisterRequest,
    SendCodeRequest,
    SendCodeResponse,
    UpdateProfileRequest,
    LoginResponse,
    LoginRequest,
    TokenResponse,
    UserInfo,
    UserInfoResponse,
)
from src.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    generate_zen_nickname,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.core.redis import get_redis
from src.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 微信小程序配置（从环境变量读取）
WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")

# 默认系统头像（东方美学风格）
DEFAULT_AVATAR_URL = os.getenv(
    "DEFAULT_AVATAR_URL",
    "https://your-cdn.com/avatars/default_zen.png"
)


# ── 工具函数 ──────────────────────────────────────────────────

def _make_login_response(user: User) -> LoginResponse:
    """构造统一的登录响应"""
    token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo(
            id=user.user_id,
            phone=user.phone,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            bio=user.bio,
            is_vip=user.is_vip,
        ),
    )


async def _get_wechat_openid(code: str) -> str:
    """
    用 code 换取微信 OpenID。

    调用微信 jscode2session 接口，后端换取，前端不可伪造。
    开发环境若未配置 WECHAT_APPID，直接用 code 作为 mock openid。
    """
    if not WECHAT_APPID or not WECHAT_SECRET:
        # 开发模式：直接用 code 作为 mock openid，方便联调
        print(f"⚠️  微信 AppID 未配置，使用 mock openid: mock_{code[:8]}")
        return f"mock_{code[:8]}"

    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(verify=certifi.where(), timeout=10.0) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败：{data.get('errmsg', '未知错误')}",
        )
    return data["openid"]


# ── 短信验证码 ────────────────────────────────────────────────

@router.post("/send-sms-code", response_model=SendCodeResponse, summary="发送短信验证码")
async def send_sms_code(
    request: SendCodeRequest,
    redis_client: redis.Redis = Depends(get_redis),
):
    """
    发送短信验证码（含三层防刷限流）

    限流规则（Redis）：
      1. 同一手机号 60 秒冷却：phone_code_lock:{phone}
      2. 同一手机号单日上限 5 次：phone_code_daily:{phone}
      3. 验证码有效期 5 分钟：login_code:{phone}

    生产环境：集成阿里云 alibabacloud_dysmsapi20170525 发送真实短信。
    当前：控制台打印验证码，方便联调。
    """
    phone = request.phone

    # 限流 1：60 秒冷却
    lock_key = f"phone_code_lock:{phone}"
    if await redis_client.exists(lock_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送太频繁，请 60 秒后再试",
        )

    # 限流 2：单日上限 5 次
    daily_key = f"phone_code_daily:{phone}"
    daily_count = await redis_client.get(daily_key)
    if daily_count and int(daily_count) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="今日发送次数已达上限（5次），请明日再试",
        )

    # 生成 6 位验证码
    code = "".join([str(random.randint(0, 9)) for _ in range(6)])

    # 写入 Redis
    await redis_client.setex(f"login_code:{phone}", 300, code)   # 5 分钟有效
    await redis_client.setex(lock_key, 60, 1)                    # 60 秒冷却锁
    # 单日计数（当天 23:59:59 过期）
    pipe = redis_client.pipeline()
    pipe.incr(daily_key)
    pipe.expireat(daily_key, _today_end_timestamp())
    await pipe.execute()

    # TODO: 生产环境替换为阿里云短信 SDK 调用
    print("=" * 60)
    print(f"📱 验证码（开发模式）")
    print(f"   手机号: {phone}  验证码: {code}  有效期: 5 分钟")
    print("=" * 60)

    return SendCodeResponse(msg="验证码已发送")


def _today_end_timestamp() -> int:
    """返回今天 23:59:59 的 Unix 时间戳"""
    now = datetime.now()
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return int(end.timestamp())


# ── 微信静默登录 ──────────────────────────────────────────────

@router.post("/login/wechat", response_model=LoginResponse, summary="微信静默登录")
async def login_wechat(
    request: WechatLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    微信静默登录（code → OpenID → 静默注册）

    流程：
      1. 用 code 换取 OpenID（后端调微信接口，前端不可伪造）
      2. 查询 OpenID 是否已存在
         - 存在 → 直接登录，更新 last_login
         - 不存在 → 静默注册（无需手机号），生成禅意昵称
      3. 签发 JWT Token

    账号合并场景（OpenID 不存在但手机号已存在）：
      此处不自动合并，合并逻辑在 PUT /profile 绑定手机号时处理。
    """
    openid = await _get_wechat_openid(request.code)

    # 查询是否已有该 OpenID 的账号
    result = await db.execute(select(User).where(User.wechat_openid == openid))
    user = result.scalar_one_or_none()

    if user is None:
        # 静默注册：不强制要手机号
        user = User(
            user_id=str(uuid4()),
            wechat_openid=openid,
            nickname=generate_zen_nickname(),
            avatar_url=DEFAULT_AVATAR_URL,
            last_login=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ 微信新用户注册: {user.user_id} (openid={openid[:8]}...)")
    else:
        user.last_login = datetime.utcnow()
        await db.commit()
        print(f"✅ 微信用户登录: {user.user_id}")

    return _make_login_response(user)


# ── 手机号 + 短信验证码登录 ───────────────────────────────────

@router.post("/login/phone", response_model=LoginResponse, summary="手机号验证码登录/注册")
async def login_phone(
    request: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """
    手机号 + 短信验证码登录（不存在则自动注册）

    流程：
      1. 校验验证码（Redis）
      2. 查询手机号是否已存在
         - 存在 → 直接登录
         - 不存在 → 注册新用户，生成禅意昵称
      3. 签发 JWT Token
    """
    phone, code = request.phone, request.code

    # 校验验证码
    stored = await redis_client.get(f"login_code:{phone}")
    if stored is None:
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")
    if stored != code:
        raise HTTPException(status_code=400, detail="验证码错误")
    await redis_client.delete(f"login_code:{phone}")  # 用完即删，防重放

    # 查询用户
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            user_id=str(uuid4()),
            phone=phone,
            nickname=generate_zen_nickname(),
            avatar_url=DEFAULT_AVATAR_URL,
            last_login=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ 手机号新用户注册: {user.user_id} ({phone})")
    else:
        user.last_login = datetime.utcnow()
        await db.commit()
        print(f"✅ 手机号用户登录: {user.user_id} ({phone})")

    return _make_login_response(user)


# ── 手机号 + 密码登录（兼容旧版）────────────────────────────

@router.post("/login/password", response_model=LoginResponse, summary="密码登录")
async def login_password(
    request: PasswordLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """手机号 + 密码登录（兼容旧版账号）"""
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()

    if user is None or user.hashed_password is None:
        raise HTTPException(status_code=400, detail="手机号或密码错误")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="手机号或密码错误")

    user.last_login = datetime.utcnow()
    await db.commit()
    print(f"✅ 密码登录: {user.user_id} ({request.phone})")
    return _make_login_response(user)


# ── 资料更新（含手机号绑定与账号合并）───────────────────────

@router.put("/profile", response_model=LoginResponse, summary="更新用户资料")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """
    更新用户资料（昵称、头像、绑定手机号）

    绑定手机号时的账号合并逻辑：
      - 若该手机号已存在于另一个账号（先短信登录的用户）：
          将当前微信账号的 wechat_openid 写入那个账号，
          并将当前账号标记为废弃（或直接删除，视业务决定）
      - 若该手机号不存在：直接写入当前账号的 phone 字段
    """
    # ── 绑定手机号（含账号合并）──────────────────────────────
    if request.phone:
        if not request.sms_code:
            raise HTTPException(status_code=400, detail="绑定手机号需要提供短信验证码")

        # 校验验证码
        stored = await redis_client.get(f"login_code:{request.phone}")
        if stored is None:
            raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")
        if stored != request.sms_code:
            raise HTTPException(status_code=400, detail="验证码错误")
        await redis_client.delete(f"login_code:{request.phone}")

        # 检查该手机号是否已绑定其他账号
        result = await db.execute(
            select(User).where(
                User.phone == request.phone,
                User.user_id != current_user.user_id,
            )
        )
        existing_phone_user = result.scalar_one_or_none()

        if existing_phone_user is not None:
            # 账号合并：将当前微信 OpenID 写入已有手机号账号
            if current_user.wechat_openid:
                if existing_phone_user.wechat_openid:
                    # 两个账号都有 OpenID，无法自动合并，需要用户确认
                    raise HTTPException(
                        status_code=409,
                        detail="该手机号已绑定其他微信账号，请联系客服处理",
                    )
                existing_phone_user.wechat_openid = current_user.wechat_openid
                await db.commit()
                print(f"✅ 账号合并完成: openid={current_user.wechat_openid[:8]}... → user={existing_phone_user.user_id}")
                # 返回合并后账号的 Token
                return _make_login_response(existing_phone_user)
            else:
                raise HTTPException(
                    status_code=409,
                    detail="该手机号已被注册，请直接使用手机号登录",
                )
        else:
            # 手机号未被占用，直接绑定
            current_user.phone = request.phone

    # ── 更新昵称和头像 ────────────────────────────────────────
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    if request.bio is not None:
        current_user.bio = request.bio

    await db.commit()
    await db.refresh(current_user)
    print(f"✅ 用户资料更新: {current_user.user_id}")
    return _make_login_response(current_user)


# ── 获取当前用户信息 ──────────────────────────────────────────

@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的完整信息（需要 Bearer Token）"""
    return UserInfoResponse(
        user_id=current_user.user_id,
        phone=current_user.phone,
        wechat_openid=current_user.wechat_openid,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        is_vip=current_user.is_vip,
        vip_expires_at=(
            current_user.vip_expires_at.isoformat()
            if current_user.vip_expires_at else None
        ),
        created_at=current_user.created_at.isoformat(),
        last_login=(
            current_user.last_login.isoformat()
            if current_user.last_login else None
        ),
    )


# ── Token 刷新 ────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """用当前有效 Token 换取新 Token，延长登录有效期"""
    token = create_access_token(
        data={"sub": current_user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=current_user.user_id,
        nickname=current_user.nickname,
    )


# ── 旧版兼容接口（保留，勿删）────────────────────────────────

@router.post("/send-code", response_model=SendCodeResponse, summary="发送验证码（旧版）")
async def send_code_legacy(
    request: SendCodeRequest,
    redis_client: redis.Redis = Depends(get_redis),
):
    """旧版发送验证码接口，内部转发到新版，保持向后兼容"""
    return await send_sms_code(request, redis_client)


@router.post("/login/code", response_model=LoginResponse, summary="验证码登录（旧版兼容）")
async def login_code_legacy(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """旧版验证码登录接口，内部转发到新版"""
    return await login_phone(
        PhoneLoginRequest(phone=request.phone, code=request.code),
        db,
        redis_client,
    )
