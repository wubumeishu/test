# 八字 Store 使用说明

## 概述

`useBaziStore` 是一个基于 Pinia 的状态管理 Store，用于管理八字计算、存储和历史记录。支持在线和离线两种模式。

## 功能特性

### 1. 在线/离线自适应
- **在线模式**：前端计算基础八字 + 后端 AI 深度解析
- **离线模式**：仅前端计算基础八字，自动提示用户

### 2. 本地缓存
- 自动将每次计算结果保存到本地存储
- 最多保存 50 条历史记录
- App 启动时自动加载历史记录

### 3. 网络状态检测
- 自动检测网络连接状态
- 网络异常时自动降级为离线模式

## 使用方法

### 基础使用

```typescript
import { useBaziStore } from '@/store/useBaziStore'

// 在组件中使用
const baziStore = useBaziStore()

// 计算八字
async function handleCalculate() {
  try {
    const result = await baziStore.calculateBazi(
      1990,  // 年
      5,     // 月
      15,    // 日
      14,    // 时
      30     // 分
    )
    console.log('计算结果:', result)
  } catch (error) {
    console.error('计算失败:', error)
  }
}
```

### 访问状态

```typescript
// 当前八字
const current = baziStore.currentBazi

// 历史记录
const history = baziStore.history

// 网络状态
const isOnline = baziStore.isOnline

// 加载状态
const loading = baziStore.loading
```

### 历史记录管理

```typescript
// 加载历史记录（App 启动时自动调用）
baziStore.loadHistory()

// 清空所有历史记录
baziStore.clearHistory()

// 删除单条历史记录
baziStore.deleteHistoryItem('记录ID')

// 检查网络状态
await baziStore.checkNetworkStatus()
```

## 数据结构

### BaziInfo 接口

```typescript
interface BaziInfo {
  id: string                    // 唯一标识
  timestamp: number             // 时间戳
  solar: {                      // 公历信息
    year: number
    month: number
    day: number
    hour: number
    minute: number
  }
  lunar: {                      // 农历信息
    year: string
    month: string
    day: string
    hour: string
  }
  bazi: {                       // 八字信息
    year: string                // 年柱
    month: string               // 月柱
    day: string                 // 日柱
    hour: string                // 时柱
    baziString: string          // 完整八字字符串
  }
  aiAnalysis?: string           // AI 深度解析（在线模式）
  isOffline: boolean            // 是否离线模式
  createdAt: string             // 创建时间
}
```

## 工作流程

1. **用户输入** → 年月日时分
2. **前端计算** → 使用 lunar-javascript 计算基础八字
3. **本地存储** → 立即保存到 uni.storage
4. **网络检测** → 判断是否在线
5. **在线模式** → 调用后端 API 获取 AI 分析
6. **离线模式** → 跳过后端请求，提示用户
7. **更新状态** → 更新 currentBazi 和 history

## 注意事项

1. 确保已安装 `lunar-javascript` 和 `pinia` 依赖
2. 确保 `request.ts` 工具已正确配置
3. 后端 API 地址在 `.env.development` 中配置
4. 历史记录存储在 `bazi_history` 键下

## 示例页面

```vue
<template>
  <view class="container">
    <view v-if="baziStore.loading">计算中...</view>
    <view v-else-if="baziStore.currentBazi">
      <text>八字：{{ baziStore.currentBazi.bazi.baziString }}</text>
      <text v-if="!baziStore.currentBazi.isOffline">
        AI 分析：{{ baziStore.currentBazi.aiAnalysis }}
      </text>
    </view>
    
    <view class="history">
      <text>历史记录 ({{ baziStore.history.length }})</text>
      <view v-for="item in baziStore.history" :key="item.id">
        <text>{{ item.bazi.baziString }}</text>
        <text>{{ item.createdAt }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()
</script>
```

## 后续扩展

- [ ] 添加收藏功能
- [ ] 支持分享八字
- [ ] 添加更多分析维度
- [ ] 支持批量计算
- [ ] 添加数据导出功能
