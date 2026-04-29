# 页面功能说明

## 页面结构

```
my-bazi-app/src/pages/
├── index/
│   └── index.vue          # 首页 - 八字排盘输入表单
└── result/
    └── result.vue         # 结果页 - 测算结果展示
```

## 1. 首页 (index.vue)

### 功能概述
用户输入个人信息和出生时间，提交后进行八字测算。

### 表单字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 姓名 | input | ✅ | 用户姓名 |
| 性别 | radio | ✅ | 乾造(男) / 坤造(女) |
| 出生日期 | date picker | ✅ | 公历日期 |
| 出生时间 | time picker | ✅ | 具体时辰 |

### 交互流程

```
1. 用户填写表单
   ↓
2. 点击"开启测算"按钮
   ↓
3. 表单验证
   ├─ 失败 → 显示错误提示
   └─ 成功 → 继续
   ↓
4. 解析日期时间
   ↓
5. 调用 baziStore.calculateBazi()
   ├─ 前端计算基础八字
   ├─ 保存到本地缓存
   ├─ 检测网络状态
   └─ 在线时调用后端 API
   ↓
6. 跳转到结果页
   ├─ 传递参数: name, gender
   └─ 八字数据存储在 store 中
```

### 表单验证规则

```typescript
// 姓名验证
if (!formData.name.trim()) {
  uni.showToast({ title: '请输入姓名', icon: 'none' })
  return false
}

// 日期验证
if (!formData.birthDate) {
  uni.showToast({ title: '请选择出生日期', icon: 'none' })
  return false
}

// 时间验证
if (!formData.birthTime) {
  uni.showToast({ title: '请选择出生时间', icon: 'none' })
  return false
}
```

### 数据处理

```typescript
// 日期解析
const [year, month, day] = formData.birthDate.split('-').map(Number)
// 示例: "1990-05-15" → [1990, 5, 15]

// 时间解析
const [hour, minute] = formData.birthTime.split(':').map(Number)
// 示例: "14:30" → [14, 30]

// 调用 store
await baziStore.calculateBazi(year, month, day, hour, minute)
```

### 页面跳转

```typescript
uni.navigateTo({
  url: `/pages/result/result?name=${encodeURIComponent(formData.name)}&gender=${formData.gender}`,
  success: () => console.log('✅ 跳转成功'),
  fail: (err) => console.error('❌ 跳转失败:', err)
})
```

### 控制台输出

```
=== 开始测算 ===
姓名: 张三
性别: 乾造 (男)
出生日期: 1990-05-15
出生时间: 14:30
解析后: { year: 1990, month: 5, day: 15, hour: 14, minute: 30 }
✅ 八字计算完成: { ... }
✅ 跳转到结果页面
```

## 2. 结果页 (result.vue)

### 功能概述
展示八字测算结果，包括基础八字和 AI 深度解析（在线模式）。

### 数据来源

```typescript
// 从 URL 参数获取
const name = decodeURIComponent(options.name || '')
const gender = options.gender || 'male'

// 从 store 获取
const baziInfo = baziStore.currentBazi
```

### 展示内容

#### 基础信息
- 姓名
- 性别（乾造/坤造）

#### 八字信息
```typescript
baziStore.currentBazi.bazi.baziString
// 示例: "庚午 辛巳 丙寅 甲午"
```

#### AI 深度解析（在线模式）
```typescript
baziStore.currentBazi.aiAnalysis
// 包含: 五行分析、格局判断、运势走向等
```

#### 离线提示
```typescript
if (baziStore.currentBazi.isOffline) {
  // 显示: "当前为离线模式，仅展示基础排盘"
}
```

### 交互功能

```typescript
// 返回首页
function goBack() {
  uni.navigateBack()
}
```

### 数据结构

```typescript
interface BaziInfo {
  id: string
  timestamp: number
  solar: { year, month, day, hour, minute }
  lunar: { year, month, day, hour }
  bazi: {
    year: string      // 年柱: "庚午"
    month: string     // 月柱: "辛巳"
    day: string       // 日柱: "丙寅"
    hour: string      // 时柱: "甲午"
    baziString: string // 完整: "庚午 辛巳 丙寅 甲午"
  }
  aiAnalysis?: string  // AI 分析（在线模式）
  isOffline: boolean   // 是否离线
  createdAt: string    // 创建时间
}
```

## 页面配置 (pages.json)

```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "八字排盘",
        "navigationBarBackgroundColor": "#F9F6F0",
        "navigationBarTextStyle": "black"
      }
    },
    {
      "path": "pages/result/result",
      "style": {
        "navigationBarTitleText": "测算结果",
        "navigationBarBackgroundColor": "#F9F6F0",
        "navigationBarTextStyle": "black"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "八字排盘",
    "navigationBarBackgroundColor": "#F9F6F0",
    "backgroundColor": "#F9F6F0"
  }
}
```

## 状态管理集成

### 使用 Store

```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()
```

### 调用计算方法

```typescript
const result = await baziStore.calculateBazi(
  year,   // 年
  month,  // 月
  day,    // 日
  hour,   // 时
  minute  // 分
)
```

### 访问计算结果

```typescript
// 当前八字
baziStore.currentBazi

// 历史记录
baziStore.history

// 加载状态
baziStore.loading

// 网络状态
baziStore.isOnline
```

## 错误处理

### 表单验证失败
```typescript
uni.showToast({
  title: '请输入姓名',
  icon: 'none',
  duration: 2000
})
```

### 计算失败
```typescript
uni.showToast({
  title: '测算失败，请重试',
  icon: 'error',
  duration: 2000
})
```

### 页面跳转失败
```typescript
uni.showToast({
  title: '页面跳转失败',
  icon: 'error',
  duration: 2000
})
```

## 测试场景

### 场景 1: 在线模式完整流程
1. 确保后端服务运行 (http://127.0.0.1:9000)
2. 填写表单: 张三, 男, 1990-05-15, 14:30
3. 点击"开启测算"
4. 查看控制台输出
5. 跳转到结果页
6. 查看八字和 AI 分析

### 场景 2: 离线模式
1. 关闭后端服务或断网
2. 填写表单
3. 点击"开启测算"
4. 看到提示: "当前为离线模式，仅展示基础排盘"
5. 跳转到结果页
6. 仅显示基础八字，无 AI 分析

### 场景 3: 表单验证
1. 不填姓名，点击提交 → 提示"请输入姓名"
2. 不选日期，点击提交 → 提示"请选择出生日期"
3. 不选时间，点击提交 → 提示"请选择出生时间"

### 场景 4: 历史记录
1. 完成多次测算
2. 重启 App
3. 查看控制台: "✅ 已加载 X 条历史记录"
4. 历史记录已从本地缓存恢复

## 性能优化

### 1. 按需加载
- 结果页仅在跳转时加载
- 历史记录按需读取

### 2. 本地缓存
- 立即保存到 uni.storage
- 最多保存 50 条历史

### 3. 网络优化
- 自动检测网络状态
- 离线时跳过 API 请求
- 请求失败自动降级

## 后续扩展

- [ ] 添加历史记录页面
- [ ] 支持分享功能
- [ ] 添加收藏功能
- [ ] 支持多人对比
- [ ] 添加详细解析页
- [ ] 支持导出 PDF
