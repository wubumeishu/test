# 云水禅心 · 前端（uni-app）

基于 **uni-app + Vue 3 + TypeScript** 构建的微信小程序 / H5 前端。

---

## 目录结构

```
src/
├── components/
│   ├── ZenBg/          # 宣纸背景组件
│   ├── ZenCard/        # 毛玻璃卡片组件
│   ├── ZenHeader/      # 自定义导航栏
│   └── ZenTabBar/      # 自定义底部 TabBar
│
├── pages/              # 主包页面
│   ├── login/          # 登录 / 注册
│   ├── index/          # 首页（每日运势）
│   ├── questions/      # 测算大厅
│   ├── bazi/           # 排盘信息填写（setup / ai-setup）
│   ├── result/         # 排盘结果
│   ├── zen/            # 禅修（开发中、欲改为发现）
│   ├── mine/           # 个人中心
│   └── legal/          # 用户协议 / 隐私政策
│
├── package_archive/    # 分包：档案 & 历史
│   └── pages/
│       ├── archive/    # 档案库 / 编辑档案
│       └── history/    # 测算历史
│
├── package_tests/      # 分包：测试功能
│   ├── data/
│   │   ├── mbtiDict.ts     # MBTI 16 型人格字典
│   │   ├── mbti93.ts       # 93 题题库
│   │   └── tarot.ts        # 22 张塔罗牌数据
│   └── pages/questions/
│       ├── mbti            # MBTI 答题
│       ├── mbti-result     # MBTI 结果
│       ├── mbti-advanced   # 64 型附加测试
│       ├── tarot           # 塔罗占卜
│       └── tarot-result    # 塔罗解读
│
├── static/
│   ├── handmade-paper.png  # 宣纸背景（打包进小程序）
│   └── logo.png            # 应用 Logo（打包进小程序）
│
├── store/
│   ├── useBaziStore.ts     # 八字排盘状态
│   ├── useUserStore.ts     # 用户登录状态（含持久化）
│   └── useArchiveStore.ts  # 档案状态
│
└── utils/
    └── request.ts          # 请求封装（Token 注入 / 401 拦截）
```

---

## 快速启动

```bash
npm install

# 微信小程序开发
npm run dev:mp-weixin

# H5 开发
npm run dev:h5
```

---

## 环境变量

`.env.development` / `.env.production`：

```env
VITE_API_BASE_URL=https://api.aiyuechuan.cn
```

---

## 关键设计说明

### 分包策略

主包体积控制在 **< 400KB**，MBTI / 塔罗数据文件（约 200KB）放在 `package_tests/data/`，不打入主包。

### 字体加载

字体文件托管在云端，通过 `uni.loadFontFace({ global: true })` 异步加载，不阻塞首屏渲染：

```
https://api.aiyuechuan.cn/static/fonts/material-symbols-subset.woff2
https://api.aiyuechuan.cn/static/fonts/MaShanZheng-subset.woff2
```

### 登录持久化

`useUserStore` 的 `token` / `userInfo` 初始值直接从 `uni.getStorageSync` 读取，避免 `onLaunch` 之前的竞态。Storage Key：`token`、`user_info`。

### 路由守卫

- `login.vue` 的 `onShow`：已登录则 `switchTab` 跳首页（主逻辑）
- `App.vue` 的 `onShow`：双向守卫（已登录在登录页 → 跳首页；未登录在受保护页 → 跳登录页）
- `index.vue` 的 `onShow`：无 token 则 `reLaunch` 跳登录页（兜底）

### 请求封装（`utils/request.ts`）

- 每次请求实时读取 Storage 中的 token，注入 `Authorization: Bearer {token}`
- 401 响应：通过 `useUserStore().logout()` 清理状态，节流防止多次跳转

---

## 构建

```bash
# 微信小程序
npm run build:mp-weixin

# H5
npm run build:h5
```
