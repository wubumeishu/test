# Kiro 工作目录

AI 辅助开发的专属目录，所有与业务代码无关的文档、脚本、笔记统一存放于此，保持项目根目录整洁。

> ⚠️ 此目录已加入 `.gitignore`，不进入版本控制。

---

## 目录结构

```
kiro/
├── rules/          # AI 规则配置（最高优先级）
│   └── user-preferences.md   # 语言、风格、编码规范等偏好设置
│
├── docs/           # 技术文档
│   ├── backend/    # 后端文档（FastAPI / 数据库 / 部署）
│   └── frontend/   # 前端文档（uni-app / 组件 / 设计规范）
│
├── notes/          # 笔记 & 整理记录
│
├── scripts/        # 测试 & 工具脚本（Python）
│   ├── test_*.py   # 各模块功能测试
│   └── setup_*.py  # 数据库初始化脚本
│
└── templates/      # 代码片段模板（备用）
```

---

## 规则说明（`rules/`）

`user-preferences.md` 是最高优先级规则，每次对话开始前 AI 必须读取，包含：

- 语言：**必须使用中文**
- 风格：精炼、专业、直接，能用代码解决的直接给代码
- 大规模重构前必须先说明思路并征求同意
- 技术栈：前端 UniApp (Vue3 + Vite + TypeScript)，后端 Python (FastAPI)

---

## 文档索引（`docs/`）

### 后端

| 文档 | 说明 |
|------|------|
| `快速参考手册.md` | 常用命令速查 |
| `快速启动指南.md` | 本地启动步骤 |
| `数据库模型设计.md` | 表结构设计 |
| `认证系统说明.md` | JWT + 验证码认证体系 |
| `八字排盘API文档.md` | 排盘接口详细说明 |
| `八字排盘引擎文档.md` | 排盘引擎核心逻辑 |
| `档案同步接口文档.md` | 归宗算法 & 云端同步 |
| `AI精批功能完整检查清单.md` | AI 流式分析功能检查 |
| `DeepSeek接入问题排查.md` | DeepSeek API 调试 |
| `服务器代码更新指南.md` | 服务器部署更新流程 |
| `FastAPI静态文件CORS配置.md` | 静态文件跨域配置 |

### 前端

| 文档 | 说明 |
|------|------|
| `ui-design-guide.md` | 禅意暗金设计规范 |
| `pages-guide.md` | 页面路由结构说明 |
| `useBaziStore使用指南.md` | Pinia Store 使用说明 |
| `五行颜色映射参考.md` | 五行配色方案 |
| `AI八字精批调试指南.md` | AI 精批前端调试 |
| `登录页面实现完成.md` | 登录 / 持久化实现说明 |

---

## 脚本说明（`scripts/`）

| 脚本 | 用途 |
|------|------|
| `test_auth.py` | 认证接口测试 |
| `test_fortune_api.py` | 排盘接口测试 |
| `test_archive_sync.py` | 档案同步测试 |
| `test_ai_flow.py` | AI 流式分析测试 |
| `test_bazi_engine.py` | 八字引擎单元测试 |
| `setup_database.py` | 数据库初始化 |
| `create_database.py` | 创建数据库 |
| `drop_tables.py` | 清空数据库表（慎用） |
| `diagnose_network.py` | 网络连通性诊断 |

---

## 文件放置规范

| 类型 | 放置位置 |
|------|---------|
| AI 规则 / Prompt | `kiro/rules/` |
| 技术文档 | `kiro/docs/backend/` 或 `kiro/docs/frontend/` |
| 整理记录 / 笔记 | `kiro/notes/` |
| 测试 / 工具脚本 | `kiro/scripts/` |
| 代码模板 | `kiro/templates/` |

**禁止**在 `bazi-admin/` 或 `my-bazi-app/src/` 下创建临时文档或测试脚本。

---

最后更新：2026-05-09
