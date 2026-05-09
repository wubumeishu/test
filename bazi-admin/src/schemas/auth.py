"""
认证相关 Pydantic Schema (v3.0)

覆盖三种登录方式：
  1. 微信静默登录（code → OpenID）
  2. 手机号 + 短信验证码
  3. 手机号 + 密码（兼容旧版）
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


# ── 通用响应 ──────────────────────────────────────────────────

class UserInfo(BaseModel):
    """嵌入登录响应中的用户摘要信息"""
    id: str = Field(..., description="用户ID (UUID)")
    phone: Optional[str] = Field(None, description="手机号，未绑定时为 null")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像 URL")
    bio: Optional[str] = Field(None, description="个性签名")
    is_vip: bool = Field(False, description="是否 VIP")


class LoginResponse(BaseModel):
    """所有登录方式的统一响应格式"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserInfo = Field(..., description="用户基本信息")


class TokenResponse(BaseModel):
    """旧版 Token 响应（保留兼容）"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nickname: Optional[str] = None


# ── 微信登录 ──────────────────────────────────────────────────

class WechatLoginRequest(BaseModel):
    """
    微信静默登录请求

    前端调用 uni.login() 获取 code，传给后端换取 OpenID。
    后端绝不信任前端直接传来的 openid，必须用 code 换取。
    """
    code: str = Field(..., description="微信 uni.login() 返回的临时 code", min_length=1)


# ── 短信验证码 ────────────────────────────────────────────────

class SendCodeRequest(BaseModel):
    """发送短信验证码请求"""
    phone: str = Field(..., description="手机号（11位）", min_length=11, max_length=11)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class SendCodeResponse(BaseModel):
    """发送短信验证码响应"""
    msg: str = Field(..., description="响应消息")


class PhoneLoginRequest(BaseModel):
    """手机号 + 短信验证码登录/注册"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    code: str = Field(..., description="6位短信验证码", min_length=6, max_length=6)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


# ── 密码登录（兼容旧版）──────────────────────────────────────

class PasswordLoginRequest(BaseModel):
    """手机号 + 密码登录"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    password: str = Field(..., description="密码", min_length=6)


class RegisterRequest(BaseModel):
    """手机号 + 验证码 + 密码注册"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    code: str = Field(..., description="6位短信验证码", min_length=6, max_length=6)
    password: str = Field(..., description="密码", min_length=6)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


# ── 资料更新 ──────────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    """
    更新用户资料请求（PUT /api/auth/profile）

    所有字段均为可选，只传需要修改的字段。
    手机号绑定需要同时传 phone + sms_code 进行验证。
    """
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    avatar_url: Optional[str] = Field(None, description="头像 URL", max_length=500)
    bio: Optional[str] = Field(None, description="个性签名", max_length=100)
    # 绑定/更换手机号时需要同时提供验证码
    phone: Optional[str] = Field(None, description="新手机号（需同时提供 sms_code）")
    sms_code: Optional[str] = Field(None, description="短信验证码（绑定手机号时必填）")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


# ── 用户详情响应 ──────────────────────────────────────────────

class UserInfoResponse(BaseModel):
    """GET /api/auth/me 返回的完整用户信息"""
    user_id: str
    phone: Optional[str] = None
    wechat_openid: Optional[str] = Field(None, description="已绑定微信则返回，否则 null")
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, description="个性签名")
    is_vip: bool = False
    vip_expires_at: Optional[str] = Field(None, description="VIP 到期时间 ISO8601，非 VIP 为 null")
    created_at: str
    last_login: Optional[str] = None

    class Config:
        from_attributes = True


# ── 旧版兼容（保留，勿删）────────────────────────────────────

class LoginRequest(BaseModel):
    """旧版验证码登录请求（保留兼容）"""
    phone: str = Field(..., min_length=11, max_length=11)
    code: str = Field(..., min_length=6, max_length=6)
