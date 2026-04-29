# 配置脚本

本目录存放数据库配置和测试相关的辅助脚本。

## 脚本列表

### 数据库配置
- `setup_database.py` - 一键配置数据库（推荐）
- `switch_to_postgresql.py` - 切换到 PostgreSQL 配置
- `create_database.py` - 创建数据库

### 连接测试
- `test_pg_connection.py` - 测试 PostgreSQL 连接
- `test_connection_final.py` - 最终连接测试
- `test_db_connection.py` - 数据库连接测试
- `check_postgresql.py` - 检查 PostgreSQL 状态

### 问题修复
- `fix_postgresql_connection.py` - 修复 PostgreSQL 连接问题

## 使用说明

所有脚本需要在 `bazi-admin` 目录下运行，因为它们依赖项目的配置文件和模块。

**示例:**
```bash
cd bazi-admin
python ../kiro/scripts/setup_database.py
```
