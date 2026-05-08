# 云水禅心 · ZenFortune

> 融合传统命理与现代心理学的东方灵性探索小程序

前后端分离全栈项目。前端基于 **uni-app + Vue 3 + TypeScript**，后端基于 **FastAPI + PostgreSQL**，已上线微信小程序。

---

## 项目结构

```
.
├── my-bazi-app/          # 前端（uni-app）
│   └── src/
│       ├── components/       # 公共组件（ZenHeader / ZenTabBar / ZenCard / ZenBg）
│       ├── pages/            # 主包页面（首页 / 登录 / 排盘 / 结果 / 禅修 / 我的）
│       ├── package_archive/  # 分包：档案库 / 测算历史
│       ├── package_tests/    # 分包：MBTI / 塔罗（含数据文件）
│       ├── static/           # 静态资源（宣纸背景 / Logo）
│       ├── store/            # Pinia 状态管理
│       └── utils/            # 工具函数（request.ts）
│
├── bazi-admin/           # 后端（FastAPI）
│   ├── main.py
│   ├── static/               # 云端静态资源（字体 / 塔罗牌图）
│   │   ├── fonts/            # Material Symbols + 马善政书法字体（子集化）
│   │   └── tarot/            # 22 张大阿尔卡纳塔罗牌图
│   ├── deploy/               # 部署配置（Nginx / Gunicorn / systemd）
│   └── src/
│       ├── routers/          # API 路由（auth / fortune / archive / ai）
│       ├── models/           # SQLAlchemy 数据模型
│       ├── schemas/          # Pydantic 请求/响应模型
│       ├── services/         # 业务逻辑（bazi_engine.py）
│       └── core/             # 安全（JWT）/ Redis
│
└── kiro/                 # AI 辅助文档（不进 git）
    ├── docs/             # 开发文档
    ├── notes/            # 笔记 / 整理记录
    ├── rules/            # AI 规则配置
    └── scripts/          # 数据库初始化 / 测试脚本
```

---

## 功能模块

### 🔮 八字排盘
- 公历 / 农历输入，自动历法转换
- 四柱（年/月/日/时）：天干、地支、纳音、藏干、十神、十二长生、神煞
- 五行强弱分析与可视化
- AI 深度解析报告（流式输出，SSE）
- 排盘结果云端持久化，支持历史回看

### 🧠 MBTI 人格测试
- **28 题速测版**：约 5 分钟，快速定位核心人格
- **93 题专业版**：约 15 分钟，深度剖析 16 型人格
- 专业版解锁隐藏的 **64 型人格附加测试**（24 题）
- 维度能量条可视化（E/I、S/N、T/F、J/P）
- 答题进度自动保存，支持断点续测

### 🃏 塔罗占卜
- 命运圣三角牌阵（过去 / 现在 / 未来）
- 22 张大阿尔卡纳，融合荣格原型心理学与东方禅意语境
- 沉浸式卡片放大观察层（毛玻璃 + 金色光晕）
- 综合解读与禅意建议自动生成
- 占卜历史本地持久化

### 📁 档案管理
- 命主档案云端同步（归宗算法，以最新时间戳为准）
- 公历 / 农历生辰录入
- 默认档案标记，支持多档案管理

### 📜 测算历史
- 聚合八字、MBTI、塔罗三类历史记录
- 按时间倒序排列，点击回看完整结果

---

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| uni-app | 3.0.0-408 | 跨端框架（微信小程序 / H5） |
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
| Pydantic v2 | 数据验证与序列化 |
| lunar-python | 农历 ↔ 公历转换 |
| python-jose | JWT 认证 |
| Redis | 验证码存储 |

### 部署

| 组件 | 说明 |
|------|------|
| 服务器 | Linux（宝塔面板） |
| 域名 | `api.aiyuechuan.cn`（HTTPS） |
| 反向代理 | Nginx（静态文件直接 serve，API 转发 Gunicorn） |
| 进程管理 | systemd（`zenfortune.service`） |

---

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14
- Redis（验证码功能）

### 1. 启动后端

```bash
cd bazi-admin

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 DATABASE_URL、SECRET_KEY、REDIS_URL 等

# 启动服务（默认 http://127.0.0.1:9000）
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

### 2. 启动前端

```bash
cd my-bazi-app

# 安装依赖
npm install

# 微信小程序开发模式
npm run dev:mp-weixin

# H5 开发模式
npm run dev:h5
```

### 3. 访问

- 后端 API 文档（Swagger）：`http://127.0.0.1:9000/docs`
- 微信小程序：用微信开发者工具打开 `dist/dev/mp-weixin/`

---

## 后端 API 概览

### 认证 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/send-code` | 发送手机验证码 |
| `POST` | `/api/auth/register` | 注册新用户 |
| `POST` | `/api/auth/login` | 密码登录，返回 JWT |
| `POST` | `/api/auth/login/code` | 验证码登录 |

### 八字排盘 `/api/fortune`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/fortune/calculate` | 通过档案 ID 排盘 |
| `POST` | `/api/fortune/calculate-by-data` | 直接传入生辰数据排盘 |
| `GET` | `/api/fortune/records` | 获取测算记录列表（分页） |
| `DELETE` | `/api/fortune/records/{record_id}` | 删除测算记录 |

### AI 分析 `/api/ai`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/ai/stream/{record_id}` | 流式 AI 深度解析（SSE） |

### 档案管理 `/api/archives`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/archives/sync` | 档案云端同步（归宗算法） |
| `GET` | `/api/archives/list` | 获取用户所有档案 |
| `DELETE` | `/api/archives/{archive_id}` | 删除指定档案 |

---

## 前端分包结构

| 包 | 路径 | 页面 |
|---|------|------|
| 主包 | `pages/` | 登录、首页、测算大厅、排盘、结果、禅修、我的、法律页 |
| `package_archive` | `package_archive/pages/` | 档案库、编辑档案、测算历史 |
| `package_tests` | `package_tests/pages/` | MBTI 测试/结果/附加测试、塔罗占卜/解读 |

> MBTI 和塔罗的数据文件（`mbtiDict.ts`、`tarot.ts`）位于 `package_tests/data/`，不打入主包。

---

## 设计规范

**配色系统（禅意暗金）：**

| 变量 | 色值 | 用途 |
|------|------|------|
| `--zen-bg` | `#F9F6F1` | 宣纸白背景 |
| `--zen-ink` | `#1A1A1A` | 主文字 |
| `--zen-gold` | `#D4AF37` | 金色强调 |
| `--zen-cinnabar` | `#B23A34` | 朱砂红（主操作色） |
| `--zen-accent` | `#A68B67` | 暖棕辅助 |
| `--zen-surface` | `rgba(255,255,255,0.75)` | 毛玻璃卡片 |

**字体：**
- 图标：`Material Symbols Outlined`（子集化，云端加载）
- 书法标题：`Ma Shan Zheng`（子集化，云端加载）
- 正文：系统默认无衬线字体

---

## 静态资源

所有静态资源托管在 `https://api.aiyuechuan.cn/static/`：

```
static/
├── fonts/
│   ├── material-symbols-subset.woff2   # 图标字体（子集化，313KB）
│   └── MaShanZheng-subset.woff2        # 书法字体（子集化，4.6KB）
├── tarot/
│   └── major_0.jpg ~ major_21.jpg      # 22 张塔罗牌图
├── handmade-paper.png                   # 宣纸背景纹理
├── logo.png                             # 应用 Logo
└── cta-bg.jpg                           # 引导卡背景
```

---

## 构建部署

```bash
# 微信小程序生产构建
cd my-bazi-app
npm run build:mp-weixin
# 产物在 dist/build/mp-weixin/，用微信开发者工具上传

# H5 生产构建
npm run build:h5
# 产物在 dist/build/h5/
```

服务器部署参考 `bazi-admin/deploy/` 目录下的配置文件。
