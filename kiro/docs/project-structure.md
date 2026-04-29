# 项目文件结构

## 完整目录树

```
G:\2\
├── .git/                           # Git 版本控制
├── .gitignore                      # Git 忽略配置
│
├── .kiro/                          # 项目管理文件（隐藏目录）
│   ├── rules/
│   │   └── user-preferences.md    # 用户偏好规则
│   └── docs/
│       ├── bazi-store-usage.md    # Store 使用说明
│       ├── pages-guide.md         # 页面功能说明
│       ├── ui-design-guide.md     # UI 设计指南
│       ├── project-setup-summary.md # 项目配置总结
│       └── project-structure.md   # 本文件
│
├── bazi-admin/                     # Python FastAPI 后端
│   ├── __pycache__/               # Python 缓存
│   ├── main.py                    # 主应用文件
│   ├── requirements.txt           # Python 依赖
│   └── README.md                  # 后端文档
│
└── my-bazi-app/                    # uni-app 前端
    ├── node_modules/              # 前端依赖包
    ├── src/                       # 源代码目录
    │   ├── pages/                 # 页面
    │   │   ├── index/
    │   │   │   └── index.vue     # 首页 - 八字排盘表单
    │   │   └── result/
    │   │       └── result.vue    # 结果页 - 测算结果展示
    │   ├── store/                 # Pinia 状态管理
    │   │   ├── index.ts          # Store 入口
    │   │   └── useBaziStore.ts   # 八字 Store
    │   ├── utils/                 # 工具函数
    │   │   └── request.ts        # 网络请求封装
    │   ├── static/                # 静态资源
    │   │   └── logo.png          # Logo 图片
    │   ├── App.vue                # 应用入口
    │   ├── main.ts                # 主文件
    │   ├── pages.json             # 页面配置
    │   ├── manifest.json          # 应用配置
    │   ├── uni.scss               # 全局样式
    │   ├── env.d.ts               # 环境变量类型
    │   └── shime-uni.d.ts         # uni-app 类型声明
    ├── .env.development           # 开发环境配置
    ├── .gitignore                 # Git 忽略配置
    ├── index.html                 # HTML 入口
    ├── package.json               # 前端依赖配置
    ├── package-lock.json          # 依赖锁定文件
    ├── tsconfig.json              # TypeScript 配置
    ├── vite.config.ts             # Vite 配置
    ├── shims-uni.d.ts             # uni-app 类型声明
    └── README.md                  # 前端文档
```

## 目录说明

### 根目录
- `.git/` - Git 版本控制目录
- `.gitignore` - Git 忽略配置
- `.kiro/` - 项目管理文件（隐藏目录，保持工作区整洁）

### .kiro/ - 项目管理目录
所有与项目核心业务无关的 AI 辅助文件、规划、笔记等统一存放在此。

#### .kiro/rules/
- `user-preferences.md` - 用户偏好规则，AI 助手的行为准则

#### .kiro/docs/
- `bazi-store-usage.md` - Pinia Store 使用说明
- `pages-guide.md` - 页面功能详细说明
- `ui-design-guide.md` - UI 设计规范和指南
- `project-setup-summary.md` - 项目配置总结
- `project-structure.md` - 项目文件结构说明（本文件）

### bazi-admin/ - 后端目录
Python FastAPI 后端服务。

- `main.py` - FastAPI 主应用文件，包含所有路由和接口
- `requirements.txt` - Python 依赖列表
- `README.md` - 后端文档和使用说明

### my-bazi-app/ - 前端目录
uni-app 跨平台前端应用。

#### src/ - 源代码
- `pages/` - 页面组件
  - `index/index.vue` - 首页，八字排盘输入表单
  - `result/result.vue` - 结果页，测算结果展示
- `store/` - Pinia 状态管理
  - `index.ts` - Store 入口，初始化 Pinia
  - `useBaziStore.ts` - 八字 Store，管理八字计算和历史记录
- `utils/` - 工具函数
  - `request.ts` - 网络请求封装，支持 GET/POST 等方法
- `static/` - 静态资源（图片、字体等）
- `App.vue` - 应用入口组件
- `main.ts` - 应用主文件，注册 Pinia
- `pages.json` - 页面路由配置
- `manifest.json` - 应用配置（名称、图标、权限等）
- `uni.scss` - 全局样式变量

#### 配置文件
- `.env.development` - 开发环境配置（API 地址等）
- `package.json` - 前端依赖和脚本配置
- `tsconfig.json` - TypeScript 编译配置
- `vite.config.ts` - Vite 构建配置

## 文件命名规范

### 组件文件
- 页面组件：`kebab-case.vue`（如 `index.vue`）
- 通用组件：`PascalCase.vue`（如 `BaziCard.vue`）

### TypeScript 文件
- Store：`useCamelCase.ts`（如 `useBaziStore.ts`）
- 工具函数：`camelCase.ts`（如 `request.ts`）
- 类型定义：`PascalCase.ts` 或 `camelCase.d.ts`

### 样式文件
- 全局样式：`kebab-case.scss`（如 `uni.scss`）
- 组件样式：写在 `.vue` 文件的 `<style>` 标签中

### 文档文件
- Markdown：`kebab-case.md`（如 `project-structure.md`）
- 使用小写字母和连字符

## Git 忽略规则

### 根目录 .gitignore
```
# 依赖目录
node_modules/
**/node_modules/

# Python 缓存
__pycache__/
**/__pycache__/

# 构建输出
dist/
dist-dev/
**/dist/
unpackage/
**/unpackage/

# 日志文件
*.log

# 系统文件
.DS_Store
Thumbs.db

# 编辑器
.idea/
.vscode/

# 环境变量
.env.local
.env.*.local
```

## 重要文件说明

### 后端核心文件
1. `bazi-admin/main.py` - 所有 API 接口定义
2. `bazi-admin/requirements.txt` - Python 依赖管理

### 前端核心文件
1. `my-bazi-app/src/store/useBaziStore.ts` - 八字计算和状态管理
2. `my-bazi-app/src/utils/request.ts` - 网络请求封装
3. `my-bazi-app/src/pages/index/index.vue` - 首页表单
4. `my-bazi-app/src/pages/result/result.vue` - 结果展示
5. `my-bazi-app/src/pages.json` - 页面路由配置

### 配置文件
1. `.kiro/rules/user-preferences.md` - AI 助手行为规则
2. `my-bazi-app/.env.development` - 开发环境配置
3. `my-bazi-app/tsconfig.json` - TypeScript 配置
4. `my-bazi-app/vite.config.ts` - Vite 构建配置

## 文件大小统计

### 后端
- 总文件数：约 5 个
- 代码行数：约 200 行
- 依赖包：4 个

### 前端
- 总文件数：约 20 个（不含 node_modules）
- 代码行数：约 1000 行
- 依赖包：约 20 个

### 文档
- 文档文件：5 个
- 文档行数：约 1500 行

## 后续扩展

### 计划添加的目录
- `my-bazi-app/src/components/` - 通用组件
- `my-bazi-app/src/api/` - API 接口定义
- `my-bazi-app/src/types/` - TypeScript 类型定义
- `bazi-admin/models/` - 数据模型
- `bazi-admin/services/` - 业务逻辑
- `bazi-admin/utils/` - 工具函数

### 计划添加的文件
- `my-bazi-app/src/pages/history/history.vue` - 历史记录页面
- `bazi-admin/database.py` - 数据库连接
- `bazi-admin/config.py` - 配置管理
- `.kiro/notes/development-log.md` - 开发日志

## 维护建议

1. **定期清理**：删除未使用的文件和依赖
2. **文档同步**：代码变更时同步更新文档
3. **版本控制**：重要变更及时提交 Git
4. **备份策略**：定期备份 `.kiro/` 目录
5. **依赖更新**：定期检查并更新依赖包
