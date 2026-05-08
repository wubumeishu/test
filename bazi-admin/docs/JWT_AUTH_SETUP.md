# JWT 认证体系配置文档

## 📋 概述

本文档说明如何为 FastAPI 后端配置基于手机号和 JWT 的账号体系。

## 🏗️ 架构设计

### 认证流程

```
1. 用户输入手机号 → 发送验证码（待实现）
2. 用户输入验证码 → 后端验证
3. 验证通过 → 生成 JWT Token
4. 客户端携带 Token 访问受保护接口
5. 后端验证 Token → 返回用户数据
```

### 技术栈

- **JWT 库**: `python-jose[cryptography]`
- **密码加密**: `passlib[bcrypt]`
- **数据库**: PostgreSQL + SQLAlchemy (异步)
- **迁移工具**: Alembic

## 📦 安装依赖

```bash
cd bazi-admin
pip install -r requirements.txt
```

新增的依赖包括：
- `python-jose[cryptography]` - JWT 编码/解码
- `passlib[bcrypt]` - 密码哈希（预留）
- `python-multipart` - 表单数据解析
- `alembic` - 数据库迁移工具

## ⚙️ 环境变量配置

在 `bazi-admin/.env` 文件中添加以下配置：

```bash
# JWT 认证配置
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天
```

**⚠️ 生产环境安全提示**：
```bash
# 生成强随机密钥
openssl rand -hex 32
```

## 🗄️ 数据库迁移

### 1. 初始化 Alembic（已完成）

项目已配置好 Alembic，配置文件：
- `alembic.ini` - Alembic 配置
- `alembic/env.py` - 环境配置（支持异步）
- `alembic/versions/` - 迁移脚本目录

### 2. 生成迁移脚本

```bash
cd bazi-admin

# 自动生成迁移脚本（检测模型变化）
alembic revision --autogenerate -m "add last_login to user"
```

### 3. 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 查看当前版本
alembic current

# 回滚一个版本
alembic downgrade -1
```

### 4. 手动迁移 SQL（如果不使用 Alembic）

```sql
-- 添加 last_login 字段
ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
```

## 📁 项目结构

```
bazi-admin/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── deps.py              # 依赖注入（get_current_user）
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py          # JWT 工具函数
│   ├── models/
│   │   └── user.py              # User 模型（已添加 last_login）
│   ├── routers/
│   │   └── auth.py              # 认证路由
│   └── schemas/
│       └── auth.py              # 认证相关 Schema
├── alembic/
│   ├── versions/                # 迁移脚本目录
│   ├── env.py                   # Alembic 环境配置
│   └── script.py.mako           # 迁移脚本模板
├── alembic.ini                  # Alembic 配置文件
├── .env                         # 环境变量（需手动创建）
└── requirements.txt             # Python 依赖
```

## 🔐 核心模块说明

### 1. User 模型 (`src/models/user.py`)

```python
class User(Base, TimestampMixin):
    user_id: str              # UUID 主键
    phone: str                # 手机号（唯一）
    wechat_unionid: str       # 微信 UnionID（可选）
    nickname: str             # 昵称
    avatar_url: str           # 头像 URL
    last_login: datetime      # 最后登录时间（新增）
    created_at: datetime      # 创建时间（继承自 TimestampMixin）
    updated_at: datetime      # 更新时间（继承自 TimestampMixin）
```

### 2. JWT 工具 (`src/core/security.py`)

```python
# 创建 Token
create_access_token(data: dict, expires_delta: timedelta) -> str

# 解码 Token
decode_access_token(token: str) -> dict | None

# 密码哈希（预留）
get_password_hash(password: str) -> str
verify_password(plain_password: str, hashed_password: str) -> bool
```

### 3. 依赖注入 (`src/api/deps.py`)

```python
# 必须登录（无 Token 返回 401）
async def get_current_user(...) -> User

# 可选登录（无 Token 返回 None）
async def get_current_user_optional(...) -> User | None
```

### 4. 认证路由 (`src/routers/auth.py`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login/phone` | POST | 手机号登录（自动注册） |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/auth/refresh` | POST | 刷新 Token |

## 🚀 使用示例

### 1. 在 `main.py` 中注册路由

```python
from src.routers import auth

app = FastAPI()

# 注册认证路由
app.include_router(auth.router)
```

### 2. 手机号登录

**请求**:
```bash
curl -X POST http://localhost:9000/api/auth/login/phone \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "用户8000"
}
```

### 3. 访问受保护接口

**请求**:
```bash
curl -X GET http://localhost:9000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "13800138000",
  "nickname": "用户8000",
  "avatar_url": null,
  "created_at": "2026-05-07T10:30:00",
  "last_login": "2026-05-07T12:45:00"
}
```

### 4. 在其他路由中使用认证

```python
from fastapi import APIRouter, Depends
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter()

@router.get("/api/my-archives")
async def get_my_archives(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的档案列表（需要登录）"""
    return {"user_id": current_user.user_id, "archives": [...]}


@router.get("/api/public-data")
async def get_public_data(
    current_user: User | None = Depends(get_current_user_optional)
):
    """公开接口（可选登录）"""
    if current_user:
        return {"message": f"欢迎, {current_user.nickname}"}
    else:
        return {"message": "欢迎访客"}
```

## 🔒 安全建议

### 生产环境必做

1. **强随机密钥**
   ```bash
   # 生成并设置到 .env
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **短信验证码**
   - 集成阿里云、腾讯云等短信服务
   - 验证码 6 位数字，5 分钟有效
   - 同一手机号 1 分钟内只能发送 1 次

3. **Token 过期时间**
   - 建议 7-30 天
   - 提供刷新 Token 机制

4. **HTTPS**
   - 生产环境必须使用 HTTPS
   - 防止 Token 被中间人截获

5. **速率限制**
   - 使用 `slowapi` 或 `fastapi-limiter`
   - 限制登录接口频率（如 5 次/分钟）

### 可选增强

- **Refresh Token**: 长期有效的刷新令牌
- **设备管理**: 记录登录设备，支持踢出
- **登录日志**: 记录登录 IP、时间、设备
- **多因素认证**: 支持邮箱、微信等多种登录方式

## 🧪 测试

### 1. 测试 JWT 工具

```python
from src.core.security import create_access_token, decode_access_token

# 创建 Token
token = create_access_token(data={"sub": "user_id_123"})
print(f"Token: {token}")

# 解码 Token
payload = decode_access_token(token)
print(f"Payload: {payload}")
# 输出: {'sub': 'user_id_123', 'exp': 1715097600}
```

### 2. 测试依赖注入

```python
# 在 FastAPI 路由中自动测试
# 访问 http://localhost:9000/docs 查看 Swagger UI
# 点击 "Authorize" 按钮输入 Token 进行测试
```

## 📝 待实现功能

- [ ] 短信验证码发送和验证
- [ ] 微信登录集成
- [ ] Token 刷新机制优化
- [ ] 登录日志记录
- [ ] 设备管理
- [ ] 速率限制

## 🐛 常见问题

### Q1: Token 验证失败（401 错误）

**原因**:
- Token 已过期
- Token 格式错误
- SECRET_KEY 不匹配

**解决**:
```bash
# 检查 .env 中的 SECRET_KEY 是否正确
# 重新登录获取新 Token
```

### Q2: 数据库迁移失败

**原因**:
- 数据库连接失败
- 模型定义错误

**解决**:
```bash
# 检查 DATABASE_URL
echo $DATABASE_URL

# 测试数据库连接
psql $DATABASE_URL -c "SELECT 1"

# 查看 Alembic 日志
alembic upgrade head --sql  # 只输出 SQL 不执行
```

### Q3: 手机号已存在

**原因**:
- 数据库中已有该手机号

**解决**:
- 直接登录（不会重复注册）
- 或删除旧记录后重新注册

## 📚 参考资料

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [python-jose 文档](https://python-jose.readthedocs.io/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [JWT 标准](https://jwt.io/)

---

**最后更新**: 2026-05-07
