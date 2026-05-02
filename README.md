# 禅意八字 · ZenBazi

> 融合传统命理与现代心理学的东方灵性探索应用

一个前后端分离的全栈项目，前端基于 **uni-app + Vue 3 + TypeScript**，后端基于 **FastAPI + PostgreSQL**，支持 H5 和微信小程序双端部署。

---

## 目录

- [项目结构](#项目结构)
- [功能模块](#功能模块)
- [技术栈](#技术栈)
- [快速启动](#快速启动)
- [后端 API 文档](#后端-api-文档)
- [数据库设计](#数据库设计)
- [前端页面路由](#前端页面路由)
- [设计规范](#设计规范)
- [开发说明](#开发说明)

---

## 项目结构

```
.
├── my-bazi-app/          # 前端（uni-app）
│   └── src/
│       ├── components/   # 公共组件（ZenHeader / ZenTabBar / ZenCard）
│       ├── data/         # 静态数据（MBTI 题库 / 塔罗牌数据）
│       ├── pages/        # 页面
│       ├── static/       # 静态资源（塔罗牌图片等）
│       ├── store/        # Pinia 状态管理
│       └── utils/        # 工具函数（request.ts）
│
├── bazi-admin/           # 后端（FastAPI）
│   └── src/
│       ├── routers/      # API 路由（fortune / archive）
│       ├── models/       # SQLAlchemy 数据模型
│       ├── schemas/      # Pydantic 请求/响应模型
│       └── services/     # 业务逻辑（bazi_engine.py）
│
└── kiro/                 # 项目文档与脚本
    ├── docs/             # 开发文档
    └── scripts/          # 数据库初始化、测试脚本
```

---

## 功能模块

### 🔮 八字排盘
- 支持公历 / 农历输入，自动完成历法转换
- 计算年柱、月柱、日柱、时柱（天干地支）
- 输出纳音、藏干、十神、十二长生、神煞
- 五行强弱分析与五行分布可视化
- 排盘结果云端持久化，支持历史回看

### 🧠 MBTI 人格测试
- **28 题速测版**：约 5 分钟，快速定位核心人格类型
- **93 题专业版**：约 15 分钟，深度剖析 16 型人格，含 24 道彩蛋附加题（共 117 题）
- 维度能量条可视化（E/I、S/N、T/F、J/P 各维度占比）
- 专业版解锁隐藏的 64 型人格附加测试
- 答题进度自动保存，支持断点续测

### 🃏 塔罗占卜
- 命运圣三角牌阵（过去 / 现在 / 未来）
- 22 张大阿尔卡纳完整牌库，融合荣格原型心理学与东方禅意语境
- 沉浸式卡片放大观察层（毛玻璃 + 金色光晕）
- 综合解读与禅意建议自动生成
- 占卜历史本地持久化

### 📁 档案管理
- 命主档案云端同步（归宗算法，以最新时间戳为准）
- 支持公历 / 农历生辰录入
- 默认档案标记，支持多档案管理
- 档案增删改查完整 CRUD

### 📜 测算历史
- 聚合八字、MBTI、塔罗三类历史记录
- 统一卡片样式，按时间倒序排列
- 点击任意记录可回看完整结果
- 塔罗历史展示阵型标题与当时的提问

---

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| uni-app | 3.0.0-408 | 跨端框架（H5 / 微信小程序） |
| Vue 3 | ^3.4.21 | Composition API |
| TypeScript | ^4.9.4 | 类型安全 |
| Pinia | ^2.1.7 | 状态管理 |
| Vite | 5.2.8 | 构建工具 |
| lunar-javascript | ^1.6.13 | 前端农历计算 |

### 后端

| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架，自动生成 OpenAPI 文档 |
| SQLAlchemy (async) | 异步 ORM |
| asyncpg | PostgreSQL 异步驱动 |
| Pydantic | 数据验证与序列化 |
| lunar-python | 农历 ↔ 公历转换 |
| uvicorn | ASGI 服务器 |

---

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14

### 1. 启动后端

```bash
cd bazi-admin

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 DATABASE_URL

# 启动服务（默认 http://127.0.0.1:9000）
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

后端启动时会自动执行 `init_db()`，创建所有数据库表。

### 2. 启动前端

```bash
cd my-bazi-app

# 安装依赖
npm install

# H5 开发模式
npm run dev:h5

# 微信小程序开发模式
npm run dev:mp-weixin
```

前端开发服务器默认运行在 `http://localhost:5173`，`/api` 请求自动代理到 `http://127.0.0.1:9000`。

### 3. 访问

- 前端页面：`http://localhost:5173`
- 后端 API 文档（Swagger）：`http://127.0.0.1:9000/docs`
- 后端 API 文档（ReDoc）：`http://127.0.0.1:9000/redoc`

---

## 后端 API 文档

### 八字排盘 `/api/fortune`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/fortune/calculate` | 通过档案 ID 排盘，结果存入数据库 |
| `POST` | `/api/fortune/calculate-by-data` | 直接传入生辰数据排盘（不存档案） |
| `GET` | `/api/fortune/records` | 获取测算记录列表（支持分页） |
| `GET` | `/api/fortune/records/{record_id}` | 获取单条测算记录详情 |
| `DELETE` | `/api/fortune/records/{record_id}` | 删除测算记录 |

**排盘请求示例（通过原始数据）：**

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
  "calendar_type": "solar",
  "is_deep_analysis": false
}
```

**排盘响应包含：**
- 四柱（年/月/日/时）：天干、地支、纳音、藏干、十神、十二长生、神煞
- 日主天干及五行属性
- 五行强弱分布（金/木/水/火/土各维度数值）

### 档案管理 `/api/archives`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/archives/sync` | 档案云端同步（归宗算法） |
| `GET` | `/api/archives/list` | 获取用户所有档案 |
| `DELETE` | `/api/archives/{archive_id}` | 删除指定档案 |

**同步算法说明：**

档案同步采用「归宗算法」——以 `local_created_at` 时间戳为仲裁依据：
- 云端不存在 → 直接 INSERT
- 云端已存在且本地时间戳更新 → UPDATE
- 云端已存在且本地时间戳更旧 → 跳过（保留云端版本）
- 每个用户最多一条默认档案，新设默认时自动清零其他档案的默认标记

---

## 数据库设计

### `archives` 表（命主档案）

| 字段 | 类型 | 说明 |
|------|------|------|
| `archive_id` | UUID | 主键，前端生成 |
| `user_id` | UUID | 用户 ID |
| `name` | VARCHAR | 命主姓名 |
| `gender` | INTEGER | 性别（1=男，2=女） |
| `calendar_type` | VARCHAR | 历法（solar=公历，lunar=农历） |
| `birth_year/month/day/hour/minute` | INTEGER | 生辰信息 |
| `tags` | ARRAY | 标签（如「本人」「父亲」） |
| `is_default` | BOOLEAN | 是否为默认档案 |
| `local_created_at` | BIGINT | 本地创建时间戳（毫秒） |
| `cloud_uploaded_at` | BIGINT | 云端同步时间戳（毫秒） |

### `records` 表（测算记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| `record_id` | UUID | 主键 |
| `user_id` | UUID | 用户 ID |
| `archive_id` | UUID | 关联档案（可为空） |
| `bazi_str` | VARCHAR | 八字字符串（如「甲子 乙丑 丙寅 丁卯」） |
| `five_elements_json` | JSONB | 完整排盘结果（四柱、五行等） |
| `ai_report_markdown` | TEXT | AI 深度分析报告（预留） |
| `is_deep_analysis` | BOOLEAN | 是否为深度分析 |
| `created_at` | TIMESTAMP | 创建时间 |

---

## 前端页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `pages/index/index` | 首页 | TabBar 首页 |
| `pages/questions/questions` | 测算大厅 | 功能入口网格 |
| `pages/bazi/setup` | 排盘信息 | 填写生辰信息 |
| `pages/result/result` | 排盘结果 | 四柱五行展示 |
| `pages/questions/mbti` | MBTI 测试 | 版本选择 + 答题 |
| `pages/questions/mbti-result` | MBTI 结果 | 人格类型解析 |
| `pages/questions/mbti-advanced` | 64 型附加测试 | 隐藏彩蛋测试 |
| `pages/questions/tarot` | 塔罗占卜 | 提问 + 抽牌 |
| `pages/questions/tarot-result` | 塔罗解读 | 三牌解读 + 综合分析 |
| `pages/archive/list` | 档案库 | 档案列表管理 |
| `pages/archive/add` | 编辑档案 | 新建 / 编辑档案 |
| `pages/mine/mine` | 个人中心 | 用户信息 + 菜单 |
| `pages/mine/history` | 测算历史 | 历史记录聚合 |
| `pages/zen/zen` | 禅修 | 禅意内容（开发中） |

---

## 设计规范

项目采用统一的「禅意暗金」设计系统：

| 变量 | 色值 | 用途 |
|------|------|------|
| `--zen-bg` | `#F9F6F1` | 宣纸白背景 |
| `--zen-ink` | `#1A1A1A` | 主文字色 |
| `--zen-gold` | `#D4AF37` | 金色强调（边框、图标） |
| `--zen-cinnabar` | `#B23A34` | 朱砂红（主操作色） |
| `--zen-accent` | `#A68B67` | 暖棕辅助色 |
| `--zen-muted` | `rgba(51,51,51,0.5)` | 次要文字 |
| `--zen-surface` | `rgba(255,255,255,0.75)` | 卡片背景（毛玻璃） |

字体：
- 标题 / 正文：`Noto Serif SC`（宋体，营造古典气质）
- UI 标签 / 数字：`Inter`（现代无衬线）
- 图标：`Material Symbols Outlined`（weight 200，细线风格）

---

## 开发说明

### 本地 Storage 说明（H5）

uni-app H5 环境下，`uni.setStorageSync(key, value)` 实际写入 `localStorage['uni-{key}']`。项目中部分旧数据（`tarot_question`、`tarot_cards`）可能以无前缀形式存储，`history.vue` 中的 `getStorage()` 工具函数已做兼容处理。

### 用户认证（待接入）

当前版本使用固定的 `MOCK_USER_ID`，后续接入登录系统后，需在 `get_current_user_id()` 中从 JWT Token 解析真实用户 ID。

### AI 深度分析（预留）

`/api/fortune/calculate` 接口支持 `is_deep_analysis: true` 参数，`ai_report_markdown` 字段已预留，待接入大模型（OpenAI / Claude 等）后填充。

### 构建部署

```bash
# H5 生产构建
cd my-bazi-app
npm run build:h5
# 产物在 dist/build/h5/

# 微信小程序构建
npm run build:mp-weixin
# 产物在 dist/build/mp-weixin/，用微信开发者工具上传
```
