# 后端文档

本目录存放 bazi-admin 后端项目的配置文档和说明。

## 📚 文档列表

### 数据库相关

#### 模型设计
- **[数据库模型设计.md](./数据库模型设计.md)** - 完整的数据库模型设计文档 ⭐
  - User (用户模型)
  - Archive (档案模型)
  - Record (测算记录模型)
  - 关系图和使用示例

#### 快速启动
- **[快速启动指南.md](./快速启动指南.md)** - 从零开始启动项目 ⭐
  - 安装依赖
  - 配置数据库
  - 测试模型
  - 启动服务

#### PostgreSQL 配置
- `配置PostgreSQL.md` - PostgreSQL 数据库配置指南（中文）
- `配置成功.md` - 配置成功后的说明文档
- `SETUP_POSTGRESQL.md` - PostgreSQL 设置步骤
- `POSTGRESQL_SETUP.md` - PostgreSQL 连接问题解决方案
- `DATABASE_SETUP.md` - 数据库架构和模型说明
- `QUICK_FIX.md` - 快速修复 TCP 连接问题
- `开始配置.txt` - 快速开始配置指南

## 🚀 快速开始

### 1. 配置数据库

如果是第一次配置 PostgreSQL，请按顺序阅读:

1. [配置PostgreSQL.md](./配置PostgreSQL.md) - 了解配置流程
2. [快速启动指南.md](./快速启动指南.md) - 启动项目

### 2. 了解数据库模型

阅读 [数据库模型设计.md](./数据库模型设计.md) 了解:
- 表结构设计
- 字段说明
- 关联关系
- 使用示例

### 3. 测试模型

```bash
cd bazi-admin
python ../kiro/scripts/test_models.py
```

### 4. 启动服务

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

## 📊 数据库架构

```
┌─────────────┐
│    User     │  用户表
│  (用户表)   │  - user_id (UUID)
└──────┬──────┘  - phone
       │         - wechat_unionid
       │ 1:N     - nickname
       │         - avatar_url
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│   Archive   │    │   Record    │  测算记录表
│  (档案表)   │    │ (测算记录)  │  - record_id (UUID)
└──────┬──────┘    └─────────────┘  - bazi_str
       │                             - five_elements_json (JSONB)
       │ 1:N                         - ai_report_markdown
       │                             - is_deep_analysis
       ▼
┌─────────────┐
│   Record    │
│ (测算记录)  │
└─────────────┘

档案表 (Archive)
- archive_id (UUID)
- name (姓名)
- gender (性别)
- birth_* (生辰)
- local_created_at (本地时间戳)
- cloud_uploaded_at (云端时间戳)
```

## 🛠️ 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: PostgreSQL
- **驱动**: asyncpg
- **Python**: 3.10+

## 📝 相关脚本

配置脚本已移至 `kiro/scripts/` 目录:

- `setup_database.py` - 一键配置数据库
- `test_models.py` - 测试数据库模型 ⭐
- `test_pg_connection.py` - 测试 PostgreSQL 连接
- 更多脚本请查看 `kiro/scripts/README.md`

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

## ⚠️ 注意事项

1. **环境变量**: 不要将 `.env` 文件提交到 Git
2. **数据库密码**: 使用强密码
3. **端口配置**: 确保端口未被占用
4. **级联删除**: 删除用户会自动删除其档案和记录

---

最后更新: 2026-04-27
