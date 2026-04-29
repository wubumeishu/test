# 八字后端服务 (bazi-admin)

基于 FastAPI 的八字应用后端 API 服务

## 技术栈

- **FastAPI**: 现代化的 Python Web 框架
- **SQLAlchemy**: 异步 ORM
- **PostgreSQL**: 数据库
- **Uvicorn**: ASGI 服务器
- **lunar-python**: 农历和八字计算库

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库配置

### 1. 安装 PostgreSQL

确保已安装 PostgreSQL 数据库。

### 2. 创建数据库

```sql
CREATE DATABASE bazi_db;
```

### 3. 配置环境变量

修改 `.env` 文件中的数据库连接信息：

```env
DATABASE_URL=postgresql+asyncpg://用户名:密码@localhost:5432/bazi_db
```

### 4. 初始化数据库

启动服务时会自动创建表结构。

## 启动服务

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

## API 文档

启动服务后访问：

- Swagger UI: http://127.0.0.1:9000/docs
- ReDoc: http://127.0.0.1:9000/redoc

## 项目结构

```
bazi-admin/
├── main.py                 # 主应用入口
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── src/
│   ├── __init__.py
│   ├── database.py         # 数据库连接配置
│   └── models/
│       ├── __init__.py
│       ├── base.py         # Base 模型类
│       └── user.py         # 用户模型示例
└── README.md
```

## API 接口

### 健康检查

```
GET /api/health
```

### 八字分析

```
POST /api/analyze
Content-Type: application/json

{
  "bazi_string": "甲子 乙丑 丙寅 丁卯"
}
```

## 数据库使用示例

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

## 开发说明

1. 所有模型都应继承 `src.models.base.Base`
2. 使用 `TimestampMixin` 自动添加时间戳字段
3. 使用 `get_db()` 进行依赖注入获取数据库会话
4. 数据库操作使用异步方式

## 注意事项

- 开发环境下 CORS 允许所有来源
- 生产环境需要配置具体的允许来源
- 数据库连接使用异步引擎
- 确保 PostgreSQL 服务正在运行
