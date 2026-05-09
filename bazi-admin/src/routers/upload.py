"""
文件上传路由

POST /api/upload/avatar  上传用户头像，返回可访问的静态 URL
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

# 头像存储目录（相对于项目根目录）
AVATAR_DIR = "static/avatars"
# 允许的图片格式
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
# 最大文件大小：5MB
MAX_SIZE = 5 * 1024 * 1024

# 确保目录存在
os.makedirs(AVATAR_DIR, exist_ok=True)


class UploadResponse(BaseModel):
    url: str = ""
    message: str = ""


@router.post("/avatar", response_model=UploadResponse, summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(..., description="头像图片文件"),
    current_user: User = Depends(get_current_user),
):
    """
    上传用户头像

    - 接受 JPEG / PNG / WebP / GIF 格式
    - 最大 5MB
    - 返回可直接访问的静态文件 URL

    前端流程：
      1. 用户选择头像（微信 chooseAvatar 或 uni.chooseImage）
      2. 调用此接口上传临时文件
      3. 拿到返回的 url 后存入 profile 表单
      4. 点击保存时将 url 通过 PUT /api/auth/profile 写入数据库
    """
    # 校验文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式：{file.content_type}，请上传 JPG/PNG/WebP 图片",
        )

    # 读取文件内容
    content = await file.read()

    # 校验文件大小
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件过大，头像图片不能超过 5MB",
        )

    # 生成唯一文件名（用户ID前缀 + UUID，避免覆盖其他用户头像）
    ext = _get_extension(file.content_type)
    filename = f"{current_user.user_id[:8]}_{uuid.uuid4().hex[:12]}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    # 写入磁盘
    with open(filepath, "wb") as f:
        f.write(content)

    # 构造可访问的 URL
    # 生产环境：替换为 CDN 域名，如 https://cdn.aiyuechuan.cn/avatars/xxx.jpg
    base_url = os.getenv("BASE_URL", "https://api.aiyuechuan.cn")
    url = f"{base_url}/static/avatars/{filename}"

    print(f"✅ [upload] 头像上传成功: {url}")
    return UploadResponse(url=url, message="上传成功")


def _get_extension(content_type: str) -> str:
    """根据 MIME 类型返回文件扩展名"""
    mapping = {
        "image/jpeg": ".jpg",
        "image/png":  ".png",
        "image/webp": ".webp",
        "image/gif":  ".gif",
    }
    return mapping.get(content_type, ".jpg")
