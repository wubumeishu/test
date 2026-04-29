# 项目配置总结

## 项目结构

```
G:\2\
├── bazi-admin/              # Python FastAPI 后端
│   ├── main.py             # 主应用文件
│   ├── requirements.txt    # Python 依赖
│   └── README.md           # 后端文档
├── my-bazi-app/            # uni-app 前端
│   ├── src/
│   │   ├── pages/          # 页面
│   │   │   ├── index/      # 首页
│   │   │   └── result/     # 结果页
│   │   ├── store/          # Pinia 状态管理
│   │   │   ├── index.ts    # Store 入口
│   │   │   └── useBaziStore.ts  # 八字 Store
│   │   ├── utils/
│   │   │   └── request.ts  # 网络请求封装
│   │   ├── App.vue         # 应用入口
│   │   └── main.ts         # 主文件
│   ├── .env.development    # 开发环境配置
│   ├── package.json        # 前端依赖
│   └── tsconfig.json       # TypeScript 配置
└── .kiro/                  # 项目管理文件（隐藏目录）
    ├── rules/              # 用户规则
    └── docs/               # 文档
```

## 技术栈

### 后端 (bazi-admin)
- Python 3.x
- FastAPI - Web 框架
- Uvicorn - ASGI 服务器
- lunar-python - 八字计算库
- Pydantic - 数据验证

### 前端 (my-bazi-app)
- Vue 3 + TypeScript
- uni-app - 跨平台框架
- Vite - 构建工具
- Pinia - 状态管理
- lunar-javascript - 八字计算库

## 服务端口

- **后端**: http://127.0.0.1:9000
- **前端**: http://localhost:5173

## 启动命令

### 后端
```bash
cd bazi-admin
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

### 前端
```bash
cd my-bazi-app
npm run dev:h5
```

## API 接口

### 1. 健康检查
- **URL**: `GET /api/health`
- **响应**:
```json
{
  "status": "ok",
  "message": "Python 后端服务运行正常"
}
```

### 2. 八字分析
- **URL**: `POST /api/analyze`
- **请求**:
```json
{
  "bazi_string": "甲子 乙丑 丙寅 丁卯"
}
```
- **响应**:
```json
{
  "success": true,
  "bazi_string": "甲子 乙丑 丙寅 丁卯",
  "analysis": "详细分析报告...",
  "message": "分析完成"
}
```

## 核心功能

### 1. 在线/离线自适应
- 自动检测网络状态
- 在线：前端计算 + 后端 AI 分析
- 离线：仅前端计算，自动提示

### 2. 本地缓存
- 自动保存计算结果
- 最多保存 50 条历史记录
- App 启动自动加载

### 3. 八字计算
- 使用 lunar-javascript 前端计算
- 支持公历转农历
- 自动生成年月日时四柱

### 4. AI 深度解析
- 后端预留 AI 接口
- 当前返回 Mock 数据
- 未来接入大模型

## 已完成功能

- [x] Git 仓库初始化
- [x] Python 后端搭建
- [x] FastAPI 基础框架
- [x] CORS 跨域配置
- [x] 健康检查接口
- [x] 八字分析接口（Mock）
- [x] uni-app 前端搭建
- [x] 网络请求封装
- [x] Pinia 状态管理
- [x] 八字计算逻辑
- [x] 在线/离线模式
- [x] 本地缓存功能
- [x] 历史记录管理
- [x] 新中式风格首页
- [x] 结果展示页面

## 待开发功能

- [ ] 历史记录列表页面
- [ ] 接入真实 AI 模型
- [ ] 用户认证系统
- [ ] 数据库集成
- [ ] 小程序适配
- [ ] App 打包发布

## 开发注意事项

1. **端口配置**: 后端使用 9000 端口，避免与其他项目冲突
2. **依赖安装**: 前端使用 `--legacy-peer-deps` 解决版本冲突
3. **TypeScript**: 已配置 `verbatimModuleSyntax` 替代旧选项
4. **网络请求**: 已封装 get/post 方法，支持超时和错误处理
5. **状态管理**: 使用 Pinia，支持 TypeScript 类型推导

## 文档链接

- 后端文档: `bazi-admin/README.md`
- Store 使用: `.kiro/docs/bazi-store-usage.md`
- 页面功能: `.kiro/docs/pages-guide.md`
- UI 设计: `.kiro/docs/ui-design-guide.md`
- 用户规则: `.kiro/rules/user-preferences.md`

## Git 仓库

- 远程地址: https://github.com/wubumeishu/test
- 当前分支: main
- 提交状态: 已推送

## 下一步计划

1. 测试完整流程
2. 优化 UI 细节
3. 添加历史记录页面
4. 接入真实 AI 模型
5. 准备小程序发布
