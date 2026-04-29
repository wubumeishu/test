# PostgreSQL 数据库配置指南

## 前提条件

✅ 你已经完成：
- 安装了 PostgreSQL
- PostgreSQL 服务正在运行
- 创建了 `zen_bazi` 空数据库

## 配置步骤

### 步骤 1：测试数据库连接

运行测试脚本，验证连接是否正常：

```bash
cd bazi-admin
python test_pg_connection.py <你的PostgreSQL密码>
```

**示例：**
```bash
python test_pg_connection.py mypassword123
```

如果看到 `✅ 连接成功！`，说明配置正确，继续下一步。

---

### 步骤 2：切换到 PostgreSQL 配置

运行切换脚本，自动更新 `.env` 文件：

```bash
python switch_to_postgresql.py <你的PostgreSQL密码>
```

**示例：**
```bash
python switch_to_postgresql.py mypassword123
```

这个脚本会：
- 注释掉 SQLite 配置
- 启用 PostgreSQL 配置
- 自动填入你的密码

---

### 步骤 3：启动 FastAPI 服务

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

如果看到以下输出，说明成功：

```
🚀 正在启动应用...
✅ 数据库表创建成功
✅ 数据库初始化完成
INFO:     Uvicorn running on http://127.0.0.1:9000
```

---

## 手动配置（可选）

如果你想手动修改 `.env` 文件：

1. 打开 `bazi-admin/.env`
2. 注释掉 SQLite 配置：
   ```
   # DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db
   ```
3. 启用 PostgreSQL 配置并填入密码：
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:你的密码@localhost:5432/zen_bazi
   ```

---

## 验证数据库

访问以下地址验证服务：

- 健康检查：http://127.0.0.1:9000/api/health
- API 文档：http://127.0.0.1:9000/docs

---

## 常见问题

### Q1: 连接失败 "could not connect to server"

**解决方案：**
- 确认 PostgreSQL 服务正在运行
- Windows: 打开"服务"，找到 PostgreSQL，确保状态为"正在运行"
- 或运行：`pg_ctl status`

### Q2: 认证失败 "password authentication failed"

**解决方案：**
- 检查密码是否正确
- 确认用户名是 `postgres`
- 如果忘记密码，需要重置 PostgreSQL 密码

### Q3: 数据库不存在 "database does not exist"

**解决方案：**
使用 pgAdmin 或命令行创建数据库：

```sql
CREATE DATABASE zen_bazi
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;
```

---

## 下一步

配置完成后，你可以：

1. 在 `src/models/` 目录下创建更多数据模型
2. 使用 SQLAlchemy ORM 进行数据库操作
3. 在 `main.py` 中添加 CRUD 接口

**示例：创建用户表**

```python
# src/models/user.py
from sqlalchemy import Column, String, Integer
from src.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
```

服务重启后，表会自动创建！
