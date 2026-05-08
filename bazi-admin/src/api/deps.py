"""
API 依赖注入
提供通用的依赖项，如当前用户认证
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.user import User
from src.core.security import decode_access_token

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户（依赖注入）
    
    从请求头的 Authorization: Bearer <token> 中解析 JWT，
    验证有效性，并返回当前数据库中的 User 对象。
    
    Args:
        credentials: HTTP Bearer 认证凭证
        db: 数据库会话
    
    Returns:
        当前登录的 User 对象
    
    Raises:
        HTTPException: 401 - Token 无效、过期或用户不存在
    
    使用示例:
        @app.get("/api/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.user_id, "nickname": current_user.nickname}
    """
    # 提取 token
    token = credentials.credentials
    
    # 解码 token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从 payload 中提取 user_id
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库查询用户
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取当前登录用户（可选）
    
    如果请求头中没有 token 或 token 无效，返回 None 而不是抛出异常。
    适用于可选认证的接口。
    
    Args:
        credentials: HTTP Bearer 认证凭证（可选）
        db: 数据库会话
    
    Returns:
        当前登录的 User 对象，如果未登录则返回 None
    
    使用示例:
        @app.get("/api/public")
        async def public_endpoint(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"欢迎, {current_user.nickname}"}
            else:
                return {"message": "欢迎访客"}
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None
        
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        return user
    except Exception:
        return None
