# useBaziStore 使用指南

## 概述

`useBaziStore` 是八字排盘应用的核心状态管理模块,负责管理排盘数据、历史记录和与后端 API 的交互。

**位置**: `my-bazi-app/src/store/useBaziStore.ts`

**技术栈**:
- Pinia - Vue 3 状态管理库
- TypeScript - 类型安全
- uni-app - 跨平台框架

---

## 类型定义

### Pillar (四柱信息)

```typescript
export interface Pillar {
  gan: string        // 天干: 甲乙丙丁戊己庚辛壬癸
  zhi: string        // 地支: 子丑寅卯辰巳午未申酉戌亥
  nayin: string      // 纳音: 如"路旁土"
  canggan: string[]  // 藏干: 地支中藏的天干
}
```

**示例**:
```typescript
{
  gan: "庚",
  zhi: "午",
  nayin: "路旁土",
  canggan: ["丁", "己"]
}
```

### WuxingStrength (五行强度)

```typescript
export interface WuxingStrength {
  jin: number   // 金 (%)
  mu: number    // 木 (%)
  shui: number  // 水 (%)
  huo: number   // 火 (%)
  tu: number    // 土 (%)
}
```

**示例**:
```typescript
{
  jin: 38.89,
  mu: 2.78,
  shui: 13.89,
  huo: 21.53,
  tu: 22.92
}
```

### BaziCalculateResponse (排盘响应)

```typescript
export interface BaziCalculateResponse {
  success: boolean              // 是否成功
  message: string               // 响应消息
  record_id: string             // 记录ID (UUID)
  name: string                  // 姓名
  gender: number                // 性别 (0=女, 1=男)
  solar_date: string            // 公历日期 "1990-05-15 14:30"
  lunar_date: string            // 农历日期 "一九九〇年四月廿一"
  shengxiao: string             // 生肖 "马"
  bazi_string: string           // 八字字符串 "庚午 辛巳 庚辰 癸未"
  year_pillar: Pillar           // 年柱
  month_pillar: Pillar          // 月柱
  day_pillar: Pillar            // 日柱
  hour_pillar: Pillar           // 时柱
  day_master: string            // 日主 "庚"
  day_master_wuxing: string     // 日主五行 "金"
  wuxing_strength: WuxingStrength  // 五行强度
  wuxing_summary: WuxingSummary    // 五行统计
  ai_report: string | null      // AI 分析报告
}
```

---

## 状态 (State)

### isLoading

**类型**: `Ref<boolean>`  
**默认值**: `false`  
**说明**: 控制加载状态,用于显示加载动画

**使用场景**:
```vue
<template>
  <button :disabled="baziStore.isLoading">
    {{ baziStore.isLoading ? '计算中...' : '开始排盘' }}
  </button>
</template>
```

### currentBaziData

**类型**: `Ref<BaziCalculateResponse | null>`  
**默认值**: `null`  
**说明**: 存储最近一次排盘的完整结果

**使用场景**:
```vue
<template>
  <view v-if="baziStore.currentBaziData">
    <text>八字: {{ baziStore.currentBaziData.bazi_string }}</text>
    <text>生肖: {{ baziStore.currentBaziData.shengxiao }}</text>
  </view>
</template>
```

### historyList

**类型**: `Ref<BaziCalculateResponse[]>`  
**默认值**: `[]`  
**说明**: 历史记录列表 (最多保存 50 条)

**使用场景**:
```vue
<template>
  <view v-for="item in baziStore.historyList" :key="item.record_id">
    <text>{{ item.name }} - {{ item.bazi_string }}</text>
  </view>
</template>
```

---

## Actions (方法)

### calculateByArchive

**功能**: 通过档案ID计算八字

**签名**:
```typescript
async function calculateByArchive(
  archiveId: string,
  isDeepAnalysis: boolean = false
): Promise<BaziCalculateResponse>
```

**参数**:
- `archiveId` (必填): 档案ID,UUID 格式
- `isDeepAnalysis` (可选): 是否进行深度分析,默认 `false`

**返回**: `Promise<BaziCalculateResponse>` - 排盘结果

**异常**: 如果请求失败,会抛出错误

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 基础排盘
try {
  const result = await baziStore.calculateByArchive(
    '59563ce9-6527-489e-9790-649c2b43e700'
  )
  console.log('排盘成功:', result.bazi_string)
} catch (error) {
  console.error('排盘失败:', error)
}

// 深度分析
try {
  const result = await baziStore.calculateByArchive(
    '59563ce9-6527-489e-9790-649c2b43e700',
    true  // 开启深度分析
  )
  console.log('AI 分析:', result.ai_report)
} catch (error) {
  console.error('排盘失败:', error)
}
```

**流程**:
```
1. 设置 isLoading = true
   ↓
2. 调用后端 API: POST /api/fortune/calculate
   ↓
3. 检查响应状态
   ↓
4. 保存到 currentBaziData
   ↓
5. 添加到历史记录
   ↓
6. 保存到本地存储
   ↓
7. 显示成功提示
   ↓
8. 设置 isLoading = false
```

---

### calculateByData

**功能**: 通过原始数据计算八字 (快速排盘,不保存档案)

**签名**:
```typescript
async function calculateByData(
  data: CalculateByDataRequest
): Promise<BaziCalculateResponse>
```

**参数**:
```typescript
interface CalculateByDataRequest {
  name: string              // 姓名
  gender: number            // 性别 (0=女, 1=男)
  birth_year: number        // 出生年份 (1000-2100)
  birth_month: number       // 出生月份 (1-12)
  birth_day: number         // 出生日期 (1-31)
  birth_hour: number        // 出生小时 (0-23)
  birth_minute: number      // 出生分钟 (0-59)
  is_deep_analysis?: boolean  // 是否深度分析 (可选)
}
```

**返回**: `Promise<BaziCalculateResponse>` - 排盘结果

**异常**: 如果请求失败,会抛出错误

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

try {
  const result = await baziStore.calculateByData({
    name: '张三',
    gender: 1,
    birth_year: 1990,
    birth_month: 5,
    birth_day: 15,
    birth_hour: 14,
    birth_minute: 30,
    is_deep_analysis: false
  })
  
  console.log('排盘成功:', result.bazi_string)
} catch (error) {
  console.error('排盘失败:', error)
}
```

**使用场景**:
- 快速排盘 (不需要保存档案)
- 临时查询
- 测试功能

---

### loadFromLocalStorage

**功能**: 从本地存储加载历史记录

**签名**:
```typescript
function loadFromLocalStorage(): void
```

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 在应用启动时加载
baziStore.loadFromLocalStorage()
```

**建议**: 在 `App.vue` 的 `onLaunch` 中调用

---

### clearHistory

**功能**: 清空所有历史记录

**签名**:
```typescript
function clearHistory(): void
```

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 清空历史记录
baziStore.clearHistory()
```

**效果**:
- 清空内存中的 `historyList`
- 删除本地存储中的数据
- 显示成功提示

---

### deleteHistoryItem

**功能**: 删除单条历史记录

**签名**:
```typescript
function deleteHistoryItem(recordId: string): void
```

**参数**:
- `recordId` (必填): 记录ID

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 删除指定记录
baziStore.deleteHistoryItem('record-uuid-123')
```

---

### setCurrentBaziData

**功能**: 设置当前排盘数据 (用于查看历史记录)

**签名**:
```typescript
function setCurrentBaziData(data: BaziCalculateResponse): void
```

**参数**:
- `data` (必填): 排盘结果

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 从历史记录中选择一条查看
const historyItem = baziStore.historyList[0]
baziStore.setCurrentBaziData(historyItem)
```

---

### clearCurrentBaziData

**功能**: 清空当前排盘数据

**签名**:
```typescript
function clearCurrentBaziData(): void
```

**示例**:
```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 清空当前数据
baziStore.clearCurrentBaziData()
```

---

## 完整使用示例

### 示例 1: 基础排盘页面

```vue
<template>
  <view class="page">
    <!-- 加载状态 -->
    <view v-if="baziStore.isLoading" class="loading">
      <text>正在计算中...</text>
    </view>

    <!-- 排盘按钮 -->
    <button 
      :disabled="baziStore.isLoading"
      @click="handleCalculate"
    >
      开始排盘
    </button>

    <!-- 结果展示 -->
    <view v-if="baziStore.currentBaziData" class="result">
      <text>八字: {{ baziStore.currentBaziData.bazi_string }}</text>
      <text>生肖: {{ baziStore.currentBaziData.shengxiao }}</text>
      <text>日主: {{ baziStore.currentBaziData.day_master }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useBaziStore } from '@/store/useBaziStore'
import { useArchiveStore } from '@/store/useArchiveStore'

const baziStore = useBaziStore()
const archiveStore = useArchiveStore()

async function handleCalculate() {
  try {
    const archiveId = archiveStore.currentArchiveId
    if (!archiveId) {
      uni.showToast({
        title: '请先选择档案',
        icon: 'none'
      })
      return
    }

    await baziStore.calculateByArchive(archiveId)
  } catch (error) {
    console.error('排盘失败:', error)
  }
}
</script>
```

### 示例 2: 快速排盘页面

```vue
<template>
  <view class="page">
    <!-- 表单 -->
    <input v-model="formData.name" placeholder="姓名" />
    <picker mode="date" @change="onDateChange">
      <text>{{ formData.birthDate || '选择日期' }}</text>
    </picker>
    <picker mode="time" @change="onTimeChange">
      <text>{{ formData.birthTime || '选择时间' }}</text>
    </picker>

    <!-- 排盘按钮 -->
    <button 
      :disabled="baziStore.isLoading"
      @click="handleQuickCalculate"
    >
      {{ baziStore.isLoading ? '计算中...' : '快速排盘' }}
    </button>

    <!-- 结果展示 -->
    <view v-if="baziStore.currentBaziData">
      <text>{{ baziStore.currentBaziData.bazi_string }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

const formData = reactive({
  name: '',
  birthDate: '',
  birthTime: ''
})

function onDateChange(e: any) {
  formData.birthDate = e.detail.value
}

function onTimeChange(e: any) {
  formData.birthTime = e.detail.value
}

async function handleQuickCalculate() {
  if (!formData.name || !formData.birthDate || !formData.birthTime) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    })
    return
  }

  try {
    const [year, month, day] = formData.birthDate.split('-').map(Number)
    const [hour, minute] = formData.birthTime.split(':').map(Number)

    await baziStore.calculateByData({
      name: formData.name,
      gender: 1,
      birth_year: year,
      birth_month: month,
      birth_day: day,
      birth_hour: hour,
      birth_minute: minute
    })
  } catch (error) {
    console.error('排盘失败:', error)
  }
}
</script>
```

### 示例 3: 历史记录页面

```vue
<template>
  <view class="page">
    <!-- 清空按钮 -->
    <button @click="baziStore.clearHistory">
      清空历史记录
    </button>

    <!-- 历史记录列表 -->
    <view 
      v-for="item in baziStore.historyList" 
      :key="item.record_id"
      class="history-item"
      @click="handleViewDetail(item)"
    >
      <view class="item-header">
        <text class="name">{{ item.name }}</text>
        <text class="date">{{ item.solar_date }}</text>
      </view>
      <view class="item-body">
        <text class="bazi">{{ item.bazi_string }}</text>
      </view>
      <button 
        class="delete-btn"
        @click.stop="handleDelete(item.record_id)"
      >
        删除
      </button>
    </view>

    <!-- 空状态 -->
    <view v-if="baziStore.historyList.length === 0" class="empty">
      <text>暂无历史记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'
import type { BaziCalculateResponse } from '@/store/useBaziStore'

const baziStore = useBaziStore()

onMounted(() => {
  // 加载历史记录
  baziStore.loadFromLocalStorage()
})

function handleViewDetail(item: BaziCalculateResponse) {
  // 设置为当前数据
  baziStore.setCurrentBaziData(item)
  
  // 跳转到详情页
  uni.navigateTo({
    url: '/pages/result/result'
  })
}

function handleDelete(recordId: string) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条记录吗?',
    success: (res) => {
      if (res.confirm) {
        baziStore.deleteHistoryItem(recordId)
      }
    }
  })
}
</script>
```

---

## 错误处理

### 网络错误

```typescript
try {
  await baziStore.calculateByArchive(archiveId)
} catch (error: any) {
  if (error.message.includes('网络')) {
    uni.showToast({
      title: '网络连接失败，请检查网络',
      icon: 'none'
    })
  } else {
    uni.showToast({
      title: error.message || '排盘失败',
      icon: 'none'
    })
  }
}
```

### 参数错误

```typescript
try {
  await baziStore.calculateByData({
    name: '张三',
    gender: 1,
    birth_year: 1990,
    birth_month: 13,  // ❌ 错误: 月份超出范围
    birth_day: 15,
    birth_hour: 14,
    birth_minute: 30
  })
} catch (error: any) {
  // 后端会返回参数验证错误
  console.error('参数错误:', error.message)
}
```

---

## 最佳实践

### 1. 在 App.vue 中初始化

```typescript
// App.vue
import { onLaunch } from '@dcloudio/uni-app'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

onLaunch(() => {
  // 加载历史记录
  baziStore.loadFromLocalStorage()
})
```

### 2. 使用 Computed 处理数据

```typescript
import { computed } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 五行列表
const wuxingList = computed(() => {
  if (!baziStore.currentBaziData) return []
  
  const { wuxing_strength, wuxing_summary } = baziStore.currentBaziData
  
  return [
    { name: '金', percent: wuxing_strength.jin, count: wuxing_summary.金 },
    { name: '木', percent: wuxing_strength.mu, count: wuxing_summary.木 },
    { name: '水', percent: wuxing_strength.shui, count: wuxing_summary.水 },
    { name: '火', percent: wuxing_strength.huo, count: wuxing_summary.火 },
    { name: '土', percent: wuxing_strength.tu, count: wuxing_summary.土 }
  ]
})
```

### 3. 统一的错误处理

```typescript
// utils/errorHandler.ts
export function handleBaziError(error: any) {
  console.error('八字排盘错误:', error)
  
  let message = '排盘失败，请重试'
  
  if (error.message) {
    if (error.message.includes('网络')) {
      message = '网络连接失败，请检查网络'
    } else if (error.message.includes('参数')) {
      message = '参数错误，请检查输入'
    } else {
      message = error.message
    }
  }
  
  uni.showToast({
    title: message,
    icon: 'none',
    duration: 2000
  })
}

// 使用
try {
  await baziStore.calculateByArchive(archiveId)
} catch (error) {
  handleBaziError(error)
}
```

---

## 调试技巧

### 1. 查看 Store 状态

```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 在控制台查看状态
console.log('加载状态:', baziStore.isLoading)
console.log('当前数据:', baziStore.currentBaziData)
console.log('历史记录:', baziStore.historyList)
```

### 2. 监听状态变化

```typescript
import { watch } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 监听加载状态
watch(() => baziStore.isLoading, (newValue) => {
  console.log('加载状态变化:', newValue)
})

// 监听当前数据
watch(() => baziStore.currentBaziData, (newValue) => {
  console.log('当前数据变化:', newValue)
})
```

### 3. 使用 Vue DevTools

安装 Vue DevTools 浏览器扩展,可以实时查看 Pinia Store 的状态变化。

---

## 常见问题

### Q1: 为什么调用 calculateByArchive 后没有反应?

**A**: 检查以下几点:
1. 档案ID是否正确 (必须是 UUID 格式)
2. 后端服务是否启动
3. 网络连接是否正常
4. 查看控制台是否有错误信息

### Q2: 历史记录为什么没有保存?

**A**: 确保:
1. 调用了 `loadFromLocalStorage()` 加载数据
2. 排盘成功后会自动保存
3. 检查本地存储是否有权限

### Q3: 如何清除所有数据?

**A**: 
```typescript
// 清空历史记录
baziStore.clearHistory()

// 清空当前数据
baziStore.clearCurrentBaziData()
```

---

## 相关文档

- [Pinia 官方文档](https://pinia.vuejs.org/zh/)
- [uni-app 状态管理](https://uniapp.dcloud.net.cn/tutorial/vue3-pinia.html)
- [TypeScript 文档](https://www.typescriptlang.org/zh/)

---

最后更新: 2026-04-28
