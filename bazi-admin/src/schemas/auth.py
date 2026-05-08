"""
认证相关的 Pydantic Schema
"""
from pydantic import BaseModel, Field
from typing import Optional


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    msg: str = Field(..., description="响应消息")


class LoginRequest(BaseModel):
    """验证码登录请求（旧版，保留兼容）"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    code: str = Field(..., description="验证码", min_length=6, max_length=6)


class PasswordLoginRequest(BaseModel):
    """密码登录请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    password: str = Field(..., description="密码", min_length=6)


class RegisterRequest(BaseModel):
    """注册请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    code: str = Field(..., description="验证码", min_length=6, max_length=6)
    password: str = Field(..., description="密码", min_length=6)


class UserInfo(BaseModel):
    """用户基本信息"""
    id: str = Field(..., description="用户ID")
    phone: str = Field(..., description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserInfo = Field(..., description="用户信息")


class PhoneLoginRequest(BaseModel):
    """手机号登录请求（旧版，保留兼容）"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user_id: str = Field(..., description="用户ID")
    nickname: Optional[str] = Field(None, description="用户昵称")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    user_id: str = Field(..., description="用户ID")
    phone: Optional[str] = Field(None, description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    created_at: str = Field(..., description="创建时间")
    last_login: Optional[str] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True
