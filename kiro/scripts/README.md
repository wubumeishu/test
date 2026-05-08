# 测试脚本目录

本目录存放各种测试、诊断和工具脚本。

## 📁 脚本分类

### 🔧 服务器诊断
- `check_server_config.sh` - **服务器配置检查脚本**
  - 检查 `.env` 文件和 DeepSeek API Key
  - 检查后端服务运行状态
  - 检查端口占用和依赖库
  - 查看最近日志

### 🧪 API 测试
- `test_deepseek.py` - **DeepSeek API 连接测试**
  - 测试 API Key 是否有效
  - 测试 API 调用是否正常
  - 显示配额和响应内容
- `test_auth.py` - **认证系统测试**
  - 测试 JWT 认证流程
- `test_verification_code.py` - **验证码功能测试**
  - 测试验证码发送和验证

### 🗄️ 数据库相关
- `setup_database.py` - 数据库初始化脚本
- `switch_to_postgresql.py` - 切换到 PostgreSQL
- `create_database.py` - 创建数据库
- `drop_tables.py` - 删除所有表
- `fix_postgresql_connection.py` - 修复 PostgreSQL 连接
- `check_postgresql.py` - 检查 PostgreSQL 状态
- `check_archives.py` - 检查档案数据

### 🧮 功能测试
- `test_bazi_engine.py` - 测试八字引擎
- `test_fortune_api.py` - 测试排盘 API
- `test_archive_sync.py` - 测试档案同步
- `test_shishen_changsheng.py` - 测试十神和长生
- `test_shensha_structure.py` - 测试神煞结构
- `test_shensha_integration.py` - 测试神煞集成
- `test_shensha_complete.py` - 测试神煞完整功能
- `test_static_files.py` - 测试静态文件

### 🔍 连接测试
- `test_db_connection.py` - 测试数据库连接
- `test_pg_connection.py` - 测试 PostgreSQL 连接
- `test_connection_final.py` - 最终连接测试
- `test_models.py` - 测试数据模型
- `diagnose_network.py` - 诊断网络问题

## 📋 使用说明

### Python 脚本
所有 Python 脚本需要在 `bazi-admin` 目录下运行：

```bash
cd bazi-admin
python ../kiro/scripts/test_deepseek.py
python ../kiro/scripts/test_auth.py
```

### Shell 脚本
Shell 脚本需要在服务器上的项目目录下运行：

```bash
# 在服务器上
cd /www/wwwroot/api.aiyuechuan.cn
bash ../kiro/scripts/check_server_config.sh
```

或者直接在 `bazi-admin` 目录运行：

```bash
cd bazi-admin
bash ../kiro/scripts/check_server_config.sh
```

## 🎯 常用场景

### AI 精批功能排查
```bash
# 1. 检查服务器配置
bash ../kiro/scripts/check_server_config.sh

# 2. 测试 DeepSeek API
python ../kiro/scripts/test_deepseek.py
```

### 认证功能测试
```bash
# 测试 JWT 认证
python ../kiro/scripts/test_auth.py

# 测试验证码
python ../kiro/scripts/test_verification_code.py
```

### 数据库问题排查
```bash
# 检查 PostgreSQL
python ../kiro/scripts/check_postgresql.py

# 测试数据库连接
python ../kiro/scripts/test_db_connection.py
```

---

最后更新：2026-05-08
