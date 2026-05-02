# 禅意八字 · ZenBazi

> 融合传统命理与现代心理学的东方灵性探索应用

基于 **uni-app + Vue 3 + TypeScript** 构建的 H5/小程序前端，配套 **FastAPI + PostgreSQL** 后端服务。

---

## 功能模块

| 模块 | 说明 |
|------|------|
| 八字排盘 | 输入生辰八字，调用后端引擎计算四柱、五行、十神、神煞 |
| MBTI 测试 | 28 题速测版 / 93 题专业版（含 24 题彩蛋附加题），结果本地缓存 |
| 塔罗占卜 | 命运圣三角牌阵（过去 / 现在 / 未来），22 张大阿尔卡纳 |
| 档案管理 | 云端同步的命主档案库，支持增删改查 |
| 测算历史 | 聚合八字、MBTI、塔罗三类历史记录，支持回看详情 |

---

## 技术栈

**前端**
- uni-app · Vue 3 Composition API · TypeScript
- Pinia 状态管理
- 自定义 ZenTabBar / ZenHeader / ZenCard 组件
- 禅意暗金配色设计系统（`#F9F6F1` 宣纸白 + `#D4AF37` 金 + `#B23A34` 朱砂红）

**后端**（`bazi-admin/`）
- FastAPI · SQLAlchemy Async · PostgreSQL
- lunar-python 农历转换
- 八字计算引擎（`bazi_engine.py`）

---

## 快速启动

### 前端

```bash
cd my-bazi-app
npm install
npm run dev:h5
```

### 后端

```bash
cd bazi-admin
pip install -r requirements.txt
# 配置 .env 中的 DATABASE_URL
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

后端默认运行在 `http://127.0.0.1:9000`，前端代理配置见 `vite.config.ts`。

---

## 目录结构

```
my-bazi-app/
├── src/
│   ├── components/        # ZenHeader / ZenTabBar / ZenCard 等公共组件
│   ├── data/              # mbti93.ts / tarot.ts 等静态数据
│   ├── pages/
│   │   ├── index/         # 首页
│   │   ├── questions/     # 测算大厅 / MBTI / 塔罗
│   │   ├── result/        # 八字排盘结果
│   │   ├── archive/       # 档案管理
│   │   └── mine/          # 个人中心 / 测算历史
│   ├── store/             # Pinia stores
│   ├── static/tarot/      # 22 张塔罗牌图片
│   └── utils/             # request.ts 等工具函数
bazi-admin/
├── main.py
└── src/
    ├── routers/           # fortune / archive 路由
    ├── models/            # SQLAlchemy 模型
    ├── schemas/           # Pydantic 请求/响应模型
    └── services/          # bazi_engine.py 八字计算核心
```

---

## 环境变量

复制 `bazi-admin/.env.example` 为 `.env` 并填写：

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/zen_bazi
HOST=127.0.0.1
PORT=9000
```
