# 数据库配置说明

## 🎯 快速配置（推荐）

你已经创建了 `zen_bazi` 数据库，现在只需运行配置向导：

```bash
cd bazi-admin
python setup_database.py
```

这个脚本会：
1. ✅ 测试 PostgreSQL 连接
2. ✅ 自动更新 `.env` 配置
3. ✅ 验证配置是否正确

配置完成后，启动服务：

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

---

## 📋 当前状态

✅ **已完成：**
- SQLAlchemy 异步引擎配置
- 数据库模型基类
- 用户模型示例
- FastAPI 生命周期集成
- PostgreSQL 数据库已创建

⚠️ **待完成：**
- 更新 `.env` 文件中的数据库密码

---

## 🔧 手动配置（可选）

如果你想手动配置，可以：

### 方法 1：使用测试脚本

```bash
python test_pg_connection.py <你的密码>
python switch_to_postgresql.py <你的密码>
```

### 方法 2：直接编辑 .env

打开 `bazi-admin/.env`，修改：

```env
# 注释掉 SQLite
# DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db

# 启用 PostgreSQL（替换为你的密码）
DATABASE_URL=postgresql+asyncpg://postgres:你的密码@localhost:5432/zen_bazi
```

---

## 📚 详细文档

- **完整配置指南：** `SETUP_POSTGRESQL.md`
- **PostgreSQL 安装：** `POSTGRESQL_SETUP.md`
- **快速修复：** `QUICK_FIX.md`

---

## 数据库架构

### 已创建的模型

#### User 模型 (`src/models/user.py`)

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
```

### 添加新模型

1. 在 `src/models/` 目录下创建新的模型文件
2. 继承 `Base` 和 `TimestampMixin`
3. 重启服务，表会自动创建

**示例：创建档案模型**

```python
# src/models/archive.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from src.models.base import Base, TimestampMixin

class Archive(Base, TimestampMixin):
    __tablename__ = "archives"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    gender = Column(Integer, nullable=False)  # 1=男, 0=女
    birth_date = Column(String(20), nullable=False)
    birth_time = Column(String(20), nullable=False)
    relation = Column(String(20))
    is_default = Column(Boolean, default=False)
```

---

## 数据库操作示例

### 查询用户

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.user import User

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

### 创建用户

```python
@app.post("/users")
async def create_user(username: str, email: str, db: AsyncSession = Depends(get_db)):
    user = User(username=username, email=email, password_hash="hashed_password")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

---

## 故障排查

### 连接失败

- **检查服务：** PostgreSQL 服务是否正在运行
- **检查密码：** 确认密码正确
- **检查端口：** PostgreSQL 是否监听 5432 端口

### 认证失败

- 确认用户名是 `postgres`
- 确认密码正确
- 如果忘记密码，需要重置

### 数据库不存在

虽然你已经创建了，但如果遇到问题，可以重新创建：

```sql
CREATE DATABASE zen_bazi
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;
```

---

## 下一步

1. ✅ 运行 `python setup_database.py` 完成配置
2. ✅ 启动服务验证连接
3. 📝 根据业务需求创建更多模型
4. 🔌 在 `main.py` 中添加 CRUD 接口
5. 🔐 实现用户认证和授权
