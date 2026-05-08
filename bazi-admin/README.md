# 云水禅心 · 后端（FastAPI）

基于 **FastAPI + PostgreSQL** 的八字应用后端 API 服务，部署在 `https://api.aiyuechuan.cn`。

---

## 目录结构

```
bazi-admin/
├── main.py                 # 应用入口，路由注册，CORS，静态文件挂载
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量（不进 git）
├── .env.example            # 环境变量模板
├── alembic/                # 数据库迁移
│   └── versions/           # 迁移脚本
├── deploy/
│   ├── nginx.conf          # Nginx 反向代理配置
│   ├── gunicorn.conf.py    # Gunicorn 配置
│   └── zenfortune.service  # systemd 服务配置
├── static/                 # 云端静态资源
│   ├── fonts/              # 字体文件（子集化）
│   ├── tarot/              # 塔罗牌图片
│   ├── handmade-paper.png
│   ├── logo.png
│   └── cta-bg.jpg
└── src/
    ├── database.py         # 异步数据库连接
    ├── routers/
    │   ├── auth.py         # 认证（注册 / 登录 / 验证码）
    │   ├── fortune.py      # 八字排盘 & 记录管理
    │   ├── archive.py      # 档案 CRUD & 云端同步
    │   └── ai.py           # AI 流式分析（SSE）
    ├── models/
    │   ├── user.py         # 用户模型
    │   ├── archive.py      # 档案模型
    │   └── record.py       # 测算记录模型
    ├── schemas/
    │   ├── auth.py         # 认证请求/响应
    │   ├── bazi.py         # 排盘请求/响应
    │   └── archive.py      # 档案请求/响应
    ├── services/
    │   └── bazi_engine.py  # 八字计算核心引擎
    ├── core/
    │   ├── security.py     # JWT 生成与验证
    │   └── redis.py        # Redis 连接（验证码存储）
    └── api/
        └── deps.py         # 依赖注入（get_current_user）
```

---

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/zen_bazi
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 3. 启动服务

```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

启动时自动执行 `init_db()`，创建所有数据库表。

### 4. 访问 API 文档

- Swagger UI：`http://127.0.0.1:9000/docs`
- ReDoc：`http://127.0.0.1:9000/redoc`

---

## API 接口

### 健康检查

```
GET /api/health
```

### 认证 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/send-code` | 发送手机验证码（存入 Redis，60s 过期） |
| `POST` | `/api/auth/register` | 注册，返回 JWT |
| `POST` | `/api/auth/login` | 密码登录，返回 JWT |
| `POST` | `/api/auth/login/code` | 验证码登录，返回 JWT |

### 八字排盘 `/api/fortune`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/fortune/calculate` | 通过档案 ID 排盘，结果存入数据库 |
| `POST` | `/api/fortune/calculate-by-data` | 直接传入生辰数据排盘 |
| `GET` | `/api/fortune/records` | 获取测算记录列表（`limit` / `offset` 分页） |
| `GET` | `/api/fortune/records/{record_id}` | 获取单条记录详情 |
| `DELETE` | `/api/fortune/records/{record_id}` | 删除测算记录 |

**排盘请求示例：**

```json
POST /api/fortune/calculate-by-data
{
  "name": "张三",
  "gender": 1,
  "birth_year": 1990,
  "birth_month": 5,
  "birth_day": 15,
  "birth_hour": 8,
  "birth_minute": 30,
  "is_lunar": false,
  "is_deep_analysis": false
}
```

### AI 分析 `/api/ai`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/ai/stream/{record_id}` | 流式 AI 深度解析（SSE，`text/event-stream`） |

SSE 数据格式：

```
data: {"text": "...", "done": false}
data: {"text": "", "done": true, "total": 1234, "cached": false}
```

### 档案管理 `/api/archives`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/archives/sync` | 档案云端同步（归宗算法） |
| `GET` | `/api/archives/list` | 获取用户所有档案 |
| `DELETE` | `/api/archives/{archive_id}` | 删除指定档案 |

**归宗算法**：以 `local_created_at` 时间戳为仲裁依据，本地更新则覆盖云端，否则保留云端版本。

### 静态文件

```
GET /static/{path}
```

由 Nginx 直接 serve（不经过 Python），配置了 30 天缓存和 CORS 头。

---

## 数据库模型

### `users` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `phone` | VARCHAR | 手机号（唯一） |
| `hashed_password` | VARCHAR | bcrypt 哈希密码 |
| `created_at` | TIMESTAMP | 注册时间 |

### `archives` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `archive_id` | UUID | 主键（前端生成） |
| `user_id` | UUID | 关联用户 |
| `name` | VARCHAR | 命主姓名 |
| `gender` | INTEGER | 性别（1=男，0=女） |
| `birth_year/month/day/hour/minute` | INTEGER | 生辰 |
| `is_lunar` | BOOLEAN | 是否农历 |
| `tags` | ARRAY | 标签 |
| `is_default` | BOOLEAN | 是否默认档案 |
| `local_created_at` | BIGINT | 本地时间戳（毫秒，归宗仲裁依据） |

### `records` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `record_id` | UUID | 主键 |
| `user_id` | UUID | 关联用户 |
| `archive_id` | UUID | 关联档案（可为空） |
| `bazi_str` | VARCHAR | 八字字符串 |
| `five_elements_json` | JSONB | 完整排盘结果 |
| `ai_report_markdown` | TEXT | AI 深度分析报告 |
| `is_deep_analysis` | BOOLEAN | 是否深度分析 |
| `created_at` | TIMESTAMP | 创建时间 |

---

## 服务器部署

参考 `deploy/` 目录：

```bash
# 复制 Nginx 配置
sudo cp deploy/nginx.conf /etc/nginx/sites-available/zenfortune
sudo ln -s /etc/nginx/sites-available/zenfortune /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 安装 systemd 服务
sudo cp deploy/zenfortune.service /etc/systemd/system/
sudo systemctl enable zenfortune
sudo systemctl start zenfortune
```

Nginx 配置要点：
- `location /static/` 直接 serve 磁盘文件，字体文件设置 `Access-Control-Allow-Origin: *` 和 30 天缓存
- `location /` 反向代理到 Gunicorn（`127.0.0.1:9000`），AI 接口超时设为 120s

---

## 注意事项

- 所有需要登录的接口通过 `Depends(get_current_user)` 注入当前用户，从 JWT 解析 `user_id`
- 验证码存储在 Redis，Key 格式：`sms_code:{phone}`，TTL 60 秒
- AI 流式接口使用 `StreamingResponse`，前端通过微信 `wx.request({ enableChunked: true })` 接收
- 生产环境 CORS 已限制为小程序域名，开发环境允许所有来源
