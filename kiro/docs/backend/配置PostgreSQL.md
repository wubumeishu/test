# 🗄️ PostgreSQL 数据库配置指南

## 当前状态

✅ **你已完成：**
- 安装 PostgreSQL
- 启动 PostgreSQL 服务
- 创建 `zen_bazi` 空数据库

🎯 **下一步：**
- 配置数据库连接
- 启动 FastAPI 服务

---

## 🚀 一键配置（推荐）

运行配置向导，自动完成所有配置：

```bash
cd bazi-admin
python setup_database.py
```

**这个脚本会做什么？**
1. 提示你输入 PostgreSQL 密码
2. 测试数据库连接是否正常
3. 自动更新 `.env` 配置文件
4. 验证配置完成

**输入密码时：**
- 密码不会显示在屏幕上（这是安全特性）
- 直接输入密码后按回车即可

---

## 📝 手动配置（备选）

如果你想手动配置，按以下步骤操作：

### 步骤 1：测试连接

```bash
python test_pg_connection.py <你的PostgreSQL密码>
```

**示例：**
```bash
python test_pg_connection.py mypassword123
```

如果看到 `✅ 连接成功！`，继续下一步。

### 步骤 2：更新配置

```bash
python switch_to_postgresql.py <你的PostgreSQL密码>
```

这会自动更新 `.env` 文件。

### 步骤 3：启动服务

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

---

## ✅ 验证配置

服务启动后，你应该看到：

```
🚀 正在启动应用...
✅ 数据库表创建成功
✅ 数据库初始化完成
INFO:     Uvicorn running on http://127.0.0.1:9000
```

访问以下地址验证：

- **健康检查：** http://127.0.0.1:9000/api/health
- **API 文档：** http://127.0.0.1:9000/docs

---

## 🔍 查看数据库

配置完成后，可以使用以下工具查看数据库：

### 方法 1：pgAdmin（推荐）

1. 打开 pgAdmin
2. 连接到 localhost
3. 找到 `zen_bazi` 数据库
4. 查看 `Tables` 目录，应该能看到 `users` 表

### 方法 2：命令行

```bash
psql -U postgres -d zen_bazi
```

查看表：
```sql
\dt
```

查看表结构：
```sql
\d users
```

---

## ❓ 常见问题

### Q1: 忘记 PostgreSQL 密码怎么办？

**Windows:**
1. 找到 `pg_hba.conf` 文件（通常在 `C:\Program Files\PostgreSQL\版本号\data\`）
2. 将 `md5` 改为 `trust`
3. 重启 PostgreSQL 服务
4. 使用 `psql -U postgres` 登录
5. 运行 `ALTER USER postgres PASSWORD '新密码';`
6. 改回 `md5`，重启服务

### Q2: 连接失败 "could not connect to server"

**检查：**
- PostgreSQL 服务是否正在运行
- Windows: 打开"服务"，找到 PostgreSQL，确保状态为"正在运行"

### Q3: 端口被占用

**检查端口：**
```bash
netstat -ano | findstr :5432
```

如果 5432 端口被占用，可以修改 PostgreSQL 配置使用其他端口。

---

## 📚 相关文档

- **详细配置：** `SETUP_POSTGRESQL.md`
- **数据库架构：** `DATABASE_SETUP.md`
- **快速修复：** `QUICK_FIX.md`

---

## 🎉 配置完成后

数据库配置完成后，你可以：

1. **创建更多数据模型**
   - 在 `src/models/` 目录下创建新的模型文件
   - 重启服务，表会自动创建

2. **添加 API 接口**
   - 在 `main.py` 中添加 CRUD 接口
   - 使用 `Depends(get_db)` 注入数据库会话

3. **前后端联调**
   - 前端通过 `http://127.0.0.1:9000/api/` 访问接口
   - 实现档案管理、八字分析等功能

---

## 💡 提示

- **开发环境：** 当前配置适合开发测试
- **生产环境：** 需要额外配置连接池、备份策略等
- **数据安全：** 不要将 `.env` 文件提交到 Git
