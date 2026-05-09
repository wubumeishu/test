"""
安全工具模块 (v3.0)

包含：
  - JWT Token 签发与解码
  - bcrypt 密码哈希与验证
  - 随机禅意昵称生成器
"""
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# ── JWT 配置 ──────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 默认 7 天

# ── 密码加密上下文（bcrypt）────────────────────────────────────
# deprecated="auto" 表示旧哈希算法会在验证时自动升级
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── 禅意昵称素材库 ────────────────────────────────────────────
_ZEN_PREFIXES = [
    "听风客", "观星人", "问月者", "寻道人", "悟禅客",
    "踏云者", "抚琴人", "望山客", "归隐者", "逐浪人",
    "拈花客", "问心者", "守静人", "随缘客", "知命者",
]

_ZEN_SUFFIXES = [str(i).zfill(4) for i in random.sample(range(1000, 9999), 100)]


def generate_zen_nickname() -> str:
    """
    生成随机禅意昵称，格式：「听风客_9527」

    每次调用返回不同结果，用于新用户注册时的默认昵称。
    """
    prefix = random.choice(_ZEN_PREFIXES)
    suffix = random.randint(1000, 9999)
    return f"{prefix}_{suffix}"


# ── 密码工具 ──────────────────────────────────────────────────

def get_password_hash(password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希加密。

    注意：bcrypt 最大处理 72 字节，超出部分会被截断。
    此处按字节截断，避免多字节字符（中文）被错误截断。

    Args:
        password: 用户输入的明文密码

    Returns:
        bcrypt 哈希字符串，可安全存入数据库
    """
    # 按字节截断，避免 bcrypt 72 字节限制导致的安全问题
    password_bytes = password.encode("utf-8")[:72]
    truncated = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希值是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的哈希值

    Returns:
        True 表示密码正确，False 表示不匹配
    """
    password_bytes = plain_password.encode("utf-8")[:72]
    truncated = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(truncated, hashed_password)


# ── JWT 工具 ──────────────────────────────────────────────────

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    签发 JWT Access Token。

    Args:
        data: 写入 payload 的数据，通常为 {"sub": user_id}
        expires_delta: 自定义过期时长，None 则使用环境变量默认值

    Returns:
        编码后的 JWT 字符串

    示例：
        token = create_access_token({"sub": user.user_id})
        token = create_access_token({"sub": user.user_id}, timedelta(days=30))
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码并验证 JWT Access Token。

    Args:
        token: 前端传入的 JWT 字符串

    Returns:
        解码后的 payload 字典；签名无效或已过期则返回 None

    示例：
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
