"""
JWT 认证和安全工具
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 默认 7 天

# 密码加密上下文（虽然当前使用手机号登录，但保留以备后续扩展）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT Access Token
    
    Args:
        data: 要编码到 token 中的数据（通常包含 sub: user_id）
        expires_delta: 过期时间增量，如果为 None 则使用默认值
    
    Returns:
        编码后的 JWT token 字符串
    
    示例:
        token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(days=7)
        )
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 编码 JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码并验证 JWT Access Token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        解码后的 payload 字典，如果验证失败则返回 None
    
    示例:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
    
    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
    
    Returns:
        哈希后的密码
    
    注意:
        bcrypt 限制密码最大 72 字节，函数内部会自动截断
    """
    # bcrypt 限制 72 字节，需要按字节截断而非字符截断
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)
