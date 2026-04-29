# PostgreSQL 连接问题解决方案

## 🔍 问题诊断

当前错误：`[WinError 1225] 远程计算机拒绝网络连接`

**原因**: PostgreSQL 服务正在运行，但没有监听 TCP 连接（5432 端口）。

## ✅ 解决方案

### 方案 1: 配置 PostgreSQL 监听 TCP 连接（推荐）

#### 步骤 1: 找到 PostgreSQL 配置文件

PostgreSQL 18 的配置文件通常在：
```
C:\Program Files\PostgreSQL\18\data\postgresql.conf
C:\Program Files\PostgreSQL\18\data\pg_hba.conf
```

#### 步骤 2: 编辑 postgresql.conf

1. 用管理员权限打开 `postgresql.conf`
2. 找到 `listen_addresses` 行
3. 修改为：
   ```
   listen_addresses = 'localhost'
   ```
4. 取消注释（删除行首的 `#`）

#### 步骤 3: 编辑 pg_hba.conf

1. 用管理员权限打开 `pg_hba.conf`
2. 在文件末尾添加：
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   # IPv6 local connections:
   host    all             all             ::1/128                 scram-sha-256
   ```

#### 步骤 4: 重启 PostgreSQL 服务

```powershell
# 以管理员身份运行 PowerShell
Restart-Service postgresql-x64-18
```

#### 步骤 5: 验证端口监听

```powershell
netstat -an | Select-String "5432"
```

应该看到类似输出：
```
TCP    127.0.0.1:5432         0.0.0.0:0              LISTENING
```

### 方案 2: 使用 psycopg2 同步驱动（临时方案）

如果配置 TCP 连接有困难，可以暂时使用同步驱动：

#### 修改 .env
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/zen_bazi
```

#### 修改 src/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 使用同步引擎
engine = create_engine(
    DATABASE_URL.replace('+asyncpg', ''),
    echo=True
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

## 🧪 测试连接

### 使用 psql 命令行工具

```bash
# 测试连接
psql -U postgres -d zen_bazi

# 如果成功，你会看到：
# zen_bazi=#
```

### 使用 Python 测试脚本

```bash
python test_db_connection.py
```

## 📝 常见问题

### Q: 找不到配置文件？

**A**: 使用以下命令查找：
```sql
-- 在 psql 中运行
SHOW config_file;
SHOW hba_file;
```

### Q: 修改配置后仍然无法连接？

**A**: 
1. 确认已重启 PostgreSQL 服务
2. 检查防火墙是否阻止了 5432 端口
3. 查看 PostgreSQL 日志文件

### Q: 如何查看 PostgreSQL 日志？

**A**: 日志通常在：
```
C:\Program Files\PostgreSQL\18\data\log\
```

## 🎯 快速测试（推荐）

如果你只是想快速测试，可以使用 SQLite 代替 PostgreSQL：

### 修改 .env
```env
DATABASE_URL=sqlite+aiosqlite:///./zen_bazi.db
```

### 安装 aiosqlite
```bash
pip install aiosqlite
```

### 重启服务
```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

SQLite 不需要额外配置，数据库文件会自动创建在项目目录下。

## 📞 需要帮助？

如果以上方案都无法解决问题，请提供：
1. PostgreSQL 版本：`psql --version`
2. 配置文件位置
3. PostgreSQL 日志内容
4. 错误信息截图
