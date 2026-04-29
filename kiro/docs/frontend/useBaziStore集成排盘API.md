# useBaziStore 集成排盘 API 使用指南

## 概述

`useBaziStore` 已集成后端八字排盘 API,支持通过档案ID或原始数据进行八字计算。

## 新增功能

### 1. 新增状态

```typescript
const isLoading = ref(false)  // 加载状态 (用于控制转圈)
const lastResult = ref<BaziCalculateResponse | null>(null)  // 最近一次排盘结果
```

### 2. 新增类型定义

**四柱信息**:
```typescript
interface Pillar {
  gan: string        // 天干
  zhi: string        // 地支
  nayin: string      // 纳音
  canggan: string[]  // 藏干
}
```

**五行强度**:
```typescript
interface WuxingStrength {
  jin: number   // 金 (%)
  mu: number    // 木 (%)
  shui: number  // 水 (%)
  huo: number   // 火 (%)
  tu: number    // 土 (%)
}
```

**后端响应**:
```typescript
interface BaziCalculateResponse {
  success: boolean
  message: string
  record_id: string
  name: string
  gender: number
  solar_date: string
  lunar_date: string
  shengxiao: string
  bazi_string: string
  year_pillar: Pillar
  month_pillar: Pillar
  day_pillar: Pillar
  hour_pillar: Pillar
  day_master: string
  day_master_wuxing: string
  wuxing_strength: WuxingStrength
  wuxing_summary: Record<string, number>
  ai_report: string | null
}
```

### 3. 修改的方法

**calculateBazi** - 通过档案ID计算:
```typescript
async function calculateBazi(
  archiveId: string,
  isDeepAnalysis: boolean = false
): Promise<BaziCalculateResponse>
```

### 4. 新增的方法

**calculateBaziByData** - 通过原始数据计算:
```typescript
async function calculateBaziByData(data: {
  name: string
  gender: number
  birth_year: number
  birth_month: number
  birth_day: number
  birth_hour: number
  birth_minute: number
  is_deep_analysis?: boolean
}): Promise<BaziCalculateResponse>
```

---

## 使用示例

### 示例 1: 通过档案ID计算

```vue
<script setup lang="ts">
import { useBaziStore } from '@/store/useBaziStore'
import { useArchiveStore } from '@/store/useArchiveStore'

const baziStore = useBaziStore()
const archiveStore = useArchiveStore()

// 计算八字
async function handleCalculate() {
  try {
    // 获取当前档案ID
    const archiveId = archiveStore.currentArchiveId
    
    if (!archiveId) {
      uni.showToast({
        title: '请先选择档案',
        icon: 'none'
      })
      return
    }
    
    // 调用排盘API
    const result = await baziStore.calculateBazi(archiveId, false)
    
    // 跳转到结果页
    uni.navigateTo({
      url: '/pages/result/result'
    })
  } catch (error) {
    console.error('排盘失败:', error)
  }
}
</script>

<template>
  <view class="container">
    <button 
      @click="handleCalculate" 
      :loading="baziStore.isLoading"
      :disabled="baziStore.isLoading"
    >
      {{ baziStore.isLoading ? '计算中...' : '开始排盘' }}
    </button>
  </view>
</template>
```

### 示例 2: 通过原始数据计算

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 表单数据
const formData = ref({
  name: '',
  gender: 1,
  birthYear: 1990,
  birthMonth: 5,
  birthDay: 15,
  birthHour: 14,
  birthMinute: 30
})

// 计算八字
async function handleCalculate() {
  try {
    const result = await baziStore.calculateBaziByData({
      name: formData.value.name,
      gender: formData.value.gender,
      birth_year: formData.value.birthYear,
      birth_month: formData.value.birthMonth,
      birth_day: formData.value.birthDay,
      birth_hour: formData.value.birthHour,
      birth_minute: formData.value.birthMinute,
      is_deep_analysis: false
    })
    
    console.log('排盘结果:', result)
    
    // 跳转到结果页
    uni.navigateTo({
      url: '/pages/result/result'
    })
  } catch (error) {
    console.error('排盘失败:', error)
  }
}
</script>

<template>
  <view class="container">
    <input v-model="formData.name" placeholder="姓名" />
    <picker :value="formData.gender" @change="onGenderChange">
      <view>性别: {{ formData.gender === 1 ? '男' : '女' }}</view>
    </picker>
    <!-- 其他表单项... -->
    
    <button 
      @click="handleCalculate" 
      :loading="baziStore.isLoading"
      :disabled="baziStore.isLoading"
    >
      {{ baziStore.isLoading ? '计算中...' : '开始排盘' }}
    </button>
  </view>
</template>
```

### 示例 3: 在结果页展示数据

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 获取最近一次排盘结果
const result = computed(() => baziStore.lastResult)

// 格式化五行强度
const wuxingList = computed(() => {
  if (!result.value) return []
  
  const strength = result.value.wuxing_strength
  return [
    { name: '金', value: strength.jin, color: '#FFD700' },
    { name: '木', value: strength.mu, color: '#228B22' },
    { name: '水', value: strength.shui, color: '#1E90FF' },
    { name: '火', value: strength.huo, color: '#FF4500' },
    { name: '土', value: strength.tu, color: '#8B4513' }
  ]
})
</script>

<template>
  <view class="result-page" v-if="result">
    <!-- 基础信息 -->
    <view class="info-section">
      <text class="name">{{ result.name }}</text>
      <text class="gender">{{ result.gender === 1 ? '男' : '女' }}</text>
      <text class="shengxiao">{{ result.shengxiao }}年</text>
    </view>
    
    <!-- 八字 -->
    <view class="bazi-section">
      <text class="title">八字</text>
      <text class="bazi-string">{{ result.bazi_string }}</text>
    </view>
    
    <!-- 四柱详情 -->
    <view class="pillar-section">
      <view class="pillar-item">
        <text class="label">年柱</text>
        <text class="value">{{ result.year_pillar.gan }}{{ result.year_pillar.zhi }}</text>
        <text class="nayin">{{ result.year_pillar.nayin }}</text>
      </view>
      <view class="pillar-item">
        <text class="label">月柱</text>
        <text class="value">{{ result.month_pillar.gan }}{{ result.month_pillar.zhi }}</text>
        <text class="nayin">{{ result.month_pillar.nayin }}</text>
      </view>
      <view class="pillar-item">
        <text class="label">日柱</text>
        <text class="value">{{ result.day_pillar.gan }}{{ result.day_pillar.zhi }}</text>
        <text class="nayin">{{ result.day_pillar.nayin }}</text>
      </view>
      <view class="pillar-item">
        <text class="label">时柱</text>
        <text class="value">{{ result.hour_pillar.gan }}{{ result.hour_pillar.zhi }}</text>
        <text class="nayin">{{ result.hour_pillar.nayin }}</text>
      </view>
    </view>
    
    <!-- 日主 -->
    <view class="daymaster-section">
      <text class="label">日主</text>
      <text class="value">{{ result.day_master }} ({{ result.day_master_wuxing }})</text>
    </view>
    
    <!-- 五行强度 -->
    <view class="wuxing-section">
      <text class="title">五行强度</text>
      <view 
        v-for="item in wuxingList" 
        :key="item.name"
        class="wuxing-item"
      >
        <text class="name">{{ item.name }}</text>
        <view class="bar-container">
          <view 
            class="bar" 
            :style="{ width: item.value + '%', backgroundColor: item.color }"
          ></view>
        </view>
        <text class="value">{{ item.value }}%</text>
      </view>
    </view>
    
    <!-- AI 分析报告 -->
    <view class="ai-section" v-if="result.ai_report">
      <text class="title">AI 深度分析</text>
      <text class="content">{{ result.ai_report }}</text>
    </view>
  </view>
  
  <view class="empty" v-else>
    <text>暂无排盘结果</text>
  </view>
</template>

<style scoped>
.result-page {
  padding: 20rpx;
}

.info-section {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.bazi-section {
  margin-bottom: 30rpx;
}

.bazi-string {
  font-size: 36rpx;
  font-weight: bold;
  letter-spacing: 10rpx;
}

.pillar-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
}

.pillar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.wuxing-section {
  margin-bottom: 30rpx;
}

.wuxing-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.bar-container {
  flex: 1;
  height: 20rpx;
  background-color: #f0f0f0;
  border-radius: 10rpx;
  overflow: hidden;
  margin: 0 20rpx;
}

.bar {
  height: 100%;
  transition: width 0.3s;
}
</style>
```

---

## 加载状态处理

### 显示加载动画

```vue
<template>
  <view class="container">
    <!-- 加载遮罩 -->
    <view class="loading-mask" v-if="baziStore.isLoading">
      <view class="loading-content">
        <view class="spinner"></view>
        <text>正在排盘中...</text>
      </view>
    </view>
    
    <!-- 按钮加载状态 -->
    <button 
      @click="handleCalculate"
      :loading="baziStore.isLoading"
      :disabled="baziStore.isLoading"
    >
      {{ baziStore.isLoading ? '计算中...' : '开始排盘' }}
    </button>
  </view>
</template>

<style scoped>
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background-color: white;
  padding: 40rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid #f3f3f3;
  border-top: 4rpx solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

---

## 错误处理

### 捕获错误并显示提示

```typescript
async function handleCalculate() {
  try {
    const result = await baziStore.calculateBazi(archiveId)
    // 成功处理...
  } catch (error: any) {
    // 错误已在 Store 中处理并显示 Toast
    // 这里可以做额外的错误处理
    console.error('排盘失败:', error)
    
    // 可选: 显示更详细的错误信息
    if (error.message.includes('档案不存在')) {
      uni.showModal({
        title: '提示',
        content: '档案不存在，请先创建档案',
        showCancel: false
      })
    }
  }
}
```

---

## API 接口说明

### 后端接口

**POST /api/fortune/calculate**
- 功能: 通过档案ID计算八字
- 请求体: `{ archive_id: string, is_deep_analysis: boolean }`
- 响应: `BaziCalculateResponse`

**POST /api/fortune/calculate-by-data**
- 功能: 通过原始数据计算八字
- 请求体: 生辰数据对象
- 响应: `BaziCalculateResponse`

---

## 注意事项

1. **档案ID验证**: 调用 `calculateBazi` 前确保档案ID存在
2. **加载状态**: 使用 `isLoading` 控制UI加载状态
3. **错误处理**: Store 已内置错误提示,无需额外处理
4. **数据持久化**: 排盘结果会自动保存到历史记录
5. **兼容性**: 保留了旧的 `BaziInfo` 格式,兼容现有代码

---

## 完整流程

```
1. 用户选择档案或输入数据
   ↓
2. 调用 calculateBazi 或 calculateBaziByData
   ↓
3. Store 设置 isLoading = true
   ↓
4. 发送请求到后端 API
   ↓
5. 接收响应并保存到 lastResult
   ↓
6. 转换为 BaziInfo 格式并保存到历史
   ↓
7. Store 设置 isLoading = false
   ↓
8. 跳转到结果页展示数据
```

---

最后更新: 2026-04-27
