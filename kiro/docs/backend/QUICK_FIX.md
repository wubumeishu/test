# 🚀 快速修复：PostgreSQL TCP 连接问题

## 问题

PostgreSQL 服务正在运行，但没有监听 TCP/IP 连接（端口 5432）。

## ✅ 解决方案（3 种方法）

---

### 方法 1: 使用 pgAdmin 创建数据库（最简单）⭐

1. **打开 pgAdmin 4**
   - 在开始菜单搜索 "pgAdmin"
   - 或访问：http://localhost:5050

2. **连接到 PostgreSQL**
   - 展开左侧的 "Servers"
   - 点击 "PostgreSQL 18"
   - 输入密码（安装时设置的密码）

3. **创建数据库**
   - 右键点击 "Databases"
   - 选择 "Create" → "Database..."
   - 在 "Database" 字段输入：`zen_bazi`
   - 点击 "Save"

4. **完成！** 数据库已创建

---

### 方法 2: 使用 SQL Shell (psql)

1. **打开 SQL Shell (psql)**
   - 在开始菜单搜索 "SQL Shell" 或 "psql"

2. **连接到 PostgreSQL**
   ```
   Server [localhost]: (直接按回车)
   Database [postgres]: (直接按回车)
   Port [5432]: (直接按回车)
   Username [postgres]: (直接按回车)
   Password: (输入你的密码)
   ```

3. **创建数据库**
   ```sql
   CREATE DATABASE zen_bazi;
   ```

4. **验证**
   ```sql
   \l
   ```
   应该能看到 `zen_bazi` 在列表中

5. **退出**
   ```sql
   \q
   ```

---

### 方法 3: 配置 PostgreSQL 监听 TCP 连接（高级）

#### 步骤 1: 找到配置文件

PostgreSQL 18 配置文件位置：
```
C:\Program Files\PostgreSQL\18\data\postgresql.conf
C:\Program Files\PostgreSQL\18\data\pg_hba.conf
```

#### 步骤 2: 编辑 postgresql.conf

1. 以**管理员身份**打开记事本
2. 打开 `postgresql.conf`
3. 找到这一行（约在第 59 行）：
   ```
   #listen_addresses = 'localhost'
   ```
4. 修改为（删除 # 号）：
   ```
   listen_addresses = 'localhost'
   ```
5. 保存文件

#### 步骤 3: 编辑 pg_hba.conf

1. 以**管理员身份**打开记事本
2. 打开 `pg_hba.conf`
3. 在文件末尾添加：
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   # IPv6 local connections:
   host    all             all             ::1/128                 scram-sha-256
   ```
4. 保存文件

#### 步骤 4: 重启 PostgreSQL 服务

以**管理员身份**运行 PowerShell：
```powershell
Restart-Service postgresql-x64-18
```

或者在服务管理器中重启：
1. Win + R，输入 `services.msc`
2. 找到 "postgresql-x64-18"
3. 右键 → 重新启动

#### 步骤 5: 验证

```powershell
netstat -an | Select-String "5432"
```

应该看到：
```
TCP    127.0.0.1:5432         0.0.0.0:0              LISTENING
```

---

## 🎯 推荐流程

**如果你只是想快速测试项目：**

1. ✅ 使用 **方法 1（pgAdmin）** 或 **方法 2（SQL Shell）** 创建数据库
2. ✅ 暂时使用 **SQLite** 代替 PostgreSQL

**修改 `.env` 文件使用 SQLite：**
```env
# 使用 SQLite（无需配置）
DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db
```

**优点：**
- ✅ 无需配置
- ✅ 立即可用
- ✅ 适合开发测试
- ✅ 数据库文件在项目目录

**缺点：**
- ❌ 生产环境不推荐
- ❌ 并发性能较低

---

## 📝 创建数据库后的步骤

### 1. 更新 .env 文件

如果使用 PostgreSQL（需要知道密码）：
```env
DATABASE_URL=postgresql+asyncpg://postgres:你的密码@localhost:5432/zen_bazi
```

如果使用 SQLite：
```env
DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db
```

### 2. 重启 FastAPI 服务

```bash
# 停止当前服务（Ctrl+C）
# 重新启动
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

### 3. 验证

访问：http://127.0.0.1:9000/docs

应该看到：
```
✅ 数据库初始化完成
```

---

## 💡 建议

**对于当前项目：**
1. 先使用 **pgAdmin** 或 **SQL Shell** 创建 `zen_bazi` 数据库
2. 如果 TCP 连接仍然有问题，暂时使用 **SQLite**
3. 等项目稳定后再配置 PostgreSQL 的 TCP 连接

**SQLite 已经足够用于：**
- ✅ 开发和测试
- ✅ 学习和原型
- ✅ 小型应用

---

## 🆘 需要帮助？

如果以上方法都不行，请告诉我：
1. 你使用了哪个方法？
2. 遇到了什么错误？
3. PostgreSQL 的安装方式（安装包/Docker/其他）

我会提供更具体的帮助！
