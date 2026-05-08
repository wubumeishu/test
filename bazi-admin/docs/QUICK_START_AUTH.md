# JWT 认证快速启动指南

## 🚀 快速开始（5 分钟）

### 1. 安装依赖

```bash
cd bazi-admin
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并生成安全的密钥：

```bash
# 复制配置文件
cp .env.example .env

# 生成随机密钥（Linux/Mac）
openssl rand -hex 32

# 或使用 Python 生成（Windows/跨平台）
python -c "import secrets; print(secrets.token_hex(32))"
```

将生成的密钥填入 `.env` 文件：

```bash
SECRET_KEY=你生成的随机密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. 数据库迁移

```bash
# 方式一：使用 Alembic（推荐）
alembic revision --autogenerate -m "add last_login to user"
alembic upgrade head

# 方式二：手动 SQL
psql $DATABASE_URL -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;"
```

### 4. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 5. 测试接口

访问 Swagger 文档：http://localhost:9000/docs

#### 测试登录

```bash
curl -X POST http://localhost:9000/api/auth/login/phone \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "用户8000"
}
```

#### 测试获取用户信息

```bash
# 替换 YOUR_TOKEN 为上一步获取的 access_token
curl -X GET http://localhost:9000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📝 API 接口列表

| 接口 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/login/phone` | POST | ❌ | 手机号登录 |
| `/api/auth/me` | GET | ✅ | 获取当前用户信息 |
| `/api/auth/refresh` | POST | ✅ | 刷新 Token |

## 🔐 在其他接口中使用认证

### 必须登录的接口

```python
from fastapi import APIRouter, Depends
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter()

@router.get("/api/my-data")
async def get_my_data(current_user: User = Depends(get_current_user)):
    """需要登录才能访问"""
    return {
        "user_id": current_user.user_id,
        "nickname": current_user.nickname,
        "data": "..."
    }
```

### 可选登录的接口

```python
from src.api.deps import get_current_user_optional

@router.get("/api/public-data")
async def get_public_data(
    current_user: User | None = Depends(get_current_user_optional)
):
    """可选登录，登录后显示个性化内容"""
    if current_user:
        return {"message": f"欢迎回来, {current_user.nickname}"}
    else:
        return {"message": "欢迎访客"}
```

## ⚠️ 注意事项

1. **生产环境必须修改 SECRET_KEY**
   - 使用强随机字符串
   - 不要提交到 Git

2. **当前版本未实现短信验证码**
   - 任何手机号都可以直接登录
   - 生产环境请务必添加验证码验证

3. **Token 过期时间**
   - 默认 7 天（10080 分钟）
   - 可通过环境变量调整

4. **HTTPS**
   - 生产环境必须使用 HTTPS
   - 防止 Token 被截获

## 🐛 常见问题

### Q: 401 Unauthorized

**原因**: Token 无效或已过期

**解决**: 重新登录获取新 Token

### Q: 数据库迁移失败

**原因**: 数据库连接失败或字段已存在

**解决**:
```bash
# 检查数据库连接
psql $DATABASE_URL -c "SELECT 1"

# 手动添加字段（如果 Alembic 失败）
psql $DATABASE_URL -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;"
```

## 📚 完整文档

详细文档请参考：[JWT_AUTH_SETUP.md](./JWT_AUTH_SETUP.md)

---

**最后更新**: 2026-05-07
