# Kiro 项目管理目录

本目录存放所有与项目核心业务无关的 AI 辅助文件、规划、笔记等。

## 目录结构

```
kiro/
├── README.md                    # 本文件
├── rules/                       # 规则配置
│   └── user-preferences.md     # 用户偏好规则
├── docs/                        # 项目文档
│   ├── backend/                # 后端文档
│   │   ├── README.md
│   │   ├── 配置PostgreSQL.md
│   │   ├── 配置成功.md
│   │   ├── DATABASE_SETUP.md
│   │   ├── POSTGRESQL_SETUP.md
│   │   ├── SETUP_POSTGRESQL.md
│   │   ├── QUICK_FIX.md
│   │   └── 开始配置.txt
│   ├── frontend/               # 前端文档
│   │   ├── README.md
│   │   ├── pages-guide.md
│   │   ├── bazi-store-usage.md
│   │   └── ui-design-guide.md
│   ├── project-structure.md    # 项目文件结构
│   ├── project-setup-summary.md # 项目配置总结
│   └── file-organization-summary.md # 文件整理总结
└── scripts/                     # 配置脚本
    ├── README.md
    ├── setup_database.py
    ├── switch_to_postgresql.py
    ├── test_pg_connection.py
    ├── test_connection_final.py
    ├── test_db_connection.py
    ├── create_database.py
    ├── fix_postgresql_connection.py
    └── check_postgresql.py
```

## 文档分类

### 规则配置 (rules/)
存放 AI 助手的行为规则和配置文件。

- `user-preferences.md` - 用户偏好规则（语言、沟通风格、编码规范等）

### 项目文档 (docs/)

#### 后端文档 (docs/backend/)
- PostgreSQL 数据库配置相关文档
- 数据库架构和模型说明
- 快速修复和问题排查指南

#### 前端文档 (docs/frontend/)
- 页面功能详细说明
- Pinia Store 使用指南
- UI 设计规范（新中式风格）

#### 通用文档 (docs/)
- 项目文件结构说明
- 项目配置总结
- 文件整理记录

### 配置脚本 (scripts/)
数据库配置和测试相关的辅助脚本。

**注意**: 所有脚本需要在 `bazi-admin` 目录下运行。

## 使用说明

### 查看文档
所有文档使用 Markdown 格式，可以直接在编辑器中查看。

### 运行脚本
```bash
cd bazi-admin
python ../kiro/scripts/setup_database.py
```

### 添加新文档
1. 确定文档类型（后端/前端/通用）
2. 放入对应子目录
3. 更新对应的 README.md
4. 使用 `kebab-case.md` 命名

## 维护规范

1. **不要删除此目录** - 包含重要的规则和文档
2. **保持目录结构** - 不要随意改变子目录结构
3. **及时更新文档** - 代码变更时同步更新相关文档
4. **遵循命名规范** - 使用 `kebab-case.md` 命名

## 项目信息

- **项目名称**: 八字排盘应用
- **技术栈**: 
  - 前端: Vue 3 + uni-app + TypeScript
  - 后端: Python + FastAPI
- **Git 仓库**: https://github.com/wubumeishu/test

---

最后更新: 2026-04-27
