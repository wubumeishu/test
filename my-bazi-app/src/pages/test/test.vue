<template>
  <view class="test-page">
    <!-- 标题 -->
    <view class="header">
      <text class="title">🧪 后端排盘 API 测试</text>
      <text class="subtitle">端口: 9000</text>
    </view>

    <!-- 当前档案信息 -->
    <view class="section">
      <view class="section-title">📋 当前选中档案</view>
      <view class="archive-info" v-if="currentArchive">
        <view class="info-row">
          <text class="label">姓名:</text>
          <text class="value">{{ currentArchive.name }}</text>
        </view>
        <view class="info-row">
          <text class="label">性别:</text>
          <text class="value">{{ currentArchive.gender === 1 ? '男' : '女' }}</text>
        </view>
        <view class="info-row">
          <text class="label">生日:</text>
          <text class="value">{{ currentArchive.birthDate }} {{ currentArchive.birthTime }}</text>
        </view>
        <view class="info-row">
          <text class="label">关系:</text>
          <text class="value">{{ currentArchive.relation }}</text>
        </view>
        <view class="info-row">
          <text class="label">档案ID:</text>
          <text class="value id">{{ currentArchive.id }}</text>
        </view>
      </view>
      <view class="empty" v-else>
        <text>❌ 未选中档案</text>
        <text class="tip">请先在首页创建并选择档案</text>
      </view>
    </view>

    <!-- 测试按钮 -->
    <view class="section">
      <button 
        class="test-button"
        :class="{ loading: baziStore.isLoading }"
        :disabled="!currentArchive || baziStore.isLoading"
        @click="handleTest"
      >
        <view class="button-content">
          <text class="icon" v-if="baziStore.isLoading">⏳</text>
          <text class="icon" v-else>🚀</text>
          <text class="text">
            {{ baziStore.isLoading ? '正在连接 9000 端口计算中...' : '开始测试后端排盘' }}
          </text>
        </view>
      </button>
    </view>

    <!-- 加载状态 -->
    <view class="section" v-if="baziStore.isLoading">
      <view class="loading-box">
        <view class="spinner"></view>
        <text class="loading-text">正在连接后端 API...</text>
        <text class="loading-tip">http://localhost:9000/api/fortune/calculate</text>
      </view>
    </view>

    <!-- 结果展示 -->
    <view class="section" v-if="lastResult && !baziStore.isLoading">
      <view class="section-title">✅ 排盘结果</view>
      
      <!-- 核心信息卡片 -->
      <view class="result-card">
        <view class="card-row">
          <text class="card-label">八字:</text>
          <text class="card-value bazi">{{ lastResult.bazi_string }}</text>
        </view>
        <view class="card-row">
          <text class="card-label">生肖:</text>
          <text class="card-value">{{ lastResult.shengxiao }}</text>
        </view>
        <view class="card-row">
          <text class="card-label">日主:</text>
          <text class="card-value">{{ lastResult.day_master }} ({{ lastResult.day_master_wuxing }})</text>
        </view>
        <view class="card-row">
          <text class="card-label">记录ID:</text>
          <text class="card-value id">{{ lastResult.record_id }}</text>
        </view>
      </view>

      <!-- 四柱详情 -->
      <view class="pillars-box">
        <view class="pillar-item">
          <text class="pillar-label">年柱</text>
          <text class="pillar-value">{{ lastResult.year_pillar.gan }}{{ lastResult.year_pillar.zhi }}</text>
          <text class="pillar-nayin">{{ lastResult.year_pillar.nayin }}</text>
          <text class="pillar-canggan">藏干: {{ lastResult.year_pillar.canggan.join(', ') }}</text>
        </view>
        <view class="pillar-item">
          <text class="pillar-label">月柱</text>
          <text class="pillar-value">{{ lastResult.month_pillar.gan }}{{ lastResult.month_pillar.zhi }}</text>
          <text class="pillar-nayin">{{ lastResult.month_pillar.nayin }}</text>
          <text class="pillar-canggan">藏干: {{ lastResult.month_pillar.canggan.join(', ') }}</text>
        </view>
        <view class="pillar-item">
          <text class="pillar-label">日柱</text>
          <text class="pillar-value">{{ lastResult.day_pillar.gan }}{{ lastResult.day_pillar.zhi }}</text>
          <text class="pillar-nayin">{{ lastResult.day_pillar.nayin }}</text>
          <text class="pillar-canggan">藏干: {{ lastResult.day_pillar.canggan.join(', ') }}</text>
        </view>
        <view class="pillar-item">
          <text class="pillar-label">时柱</text>
          <text class="pillar-value">{{ lastResult.hour_pillar.gan }}{{ lastResult.hour_pillar.zhi }}</text>
          <text class="pillar-nayin">{{ lastResult.hour_pillar.nayin }}</text>
          <text class="pillar-canggan">藏干: {{ lastResult.hour_pillar.canggan.join(', ') }}</text>
        </view>
      </view>

      <!-- 五行强度 -->
      <view class="wuxing-box">
        <text class="wuxing-title">五行强度</text>
        <view class="wuxing-item" v-for="item in wuxingList" :key="item.name">
          <text class="wuxing-name">{{ item.name }}</text>
          <view class="wuxing-bar-container">
            <view 
              class="wuxing-bar" 
              :style="{ width: item.value + '%', backgroundColor: item.color }"
            ></view>
          </view>
          <text class="wuxing-value">{{ item.value }}%</text>
          <text class="wuxing-count">({{ item.count }}个)</text>
        </view>
      </view>

      <!-- 完整 JSON 数据 -->
      <view class="json-box">
        <text class="json-title">📄 完整响应数据 (JSON)</text>
        <view class="json-content">
          <pre class="json-pre">{{ JSON.stringify(lastResult, null, 2) }}</pre>
        </view>
      </view>
    </view>

    <!-- 错误提示 -->
    <view class="section" v-if="errorMessage">
      <view class="error-box">
        <text class="error-icon">❌</text>
        <text class="error-text">{{ errorMessage }}</text>
      </view>
    </view>

    <!-- 操作提示 -->
    <view class="tips-box">
      <text class="tips-title">💡 使用提示</text>
      <text class="tips-item">1. 确保后端服务已启动 (端口 9000)</text>
      <text class="tips-item">2. 确保已创建并选择档案</text>
      <text class="tips-item">3. 点击按钮测试排盘功能</text>
      <text class="tips-item">4. 查看返回的八字、五行等数据</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useArchiveStore } from '@/store/useArchiveStore'
import { useBaziStore } from '@/store/useBaziStore'

// Store
const archiveStore = useArchiveStore()
const baziStore = useBaziStore()

// 页面加载时确保隐藏 TabBar
onMounted(() => {
  // 这是一个非 TabBar 页面,确保不显示任何底部导航
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [测试页] TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [测试页] 当前页面无 TabBar')
  })
})

// 错误信息
const errorMessage = ref('')

// 当前档案
const currentArchive = computed(() => {
  const id = archiveStore.currentArchiveId
  if (!id) return null
  return archiveStore.archives.find(a => a.id === id)
})

// 最近一次结果
const lastResult = computed(() => baziStore.currentBaziData)

// 五行列表
const wuxingList = computed(() => {
  if (!lastResult.value) return []
  
  const strength = lastResult.value.wuxing_strength
  const summary = lastResult.value.wuxing_summary
  
  return [
    { name: '金', value: strength.jin, count: summary['金'] || 0, color: '#FFD700' },
    { name: '木', value: strength.mu, count: summary['木'] || 0, color: '#228B22' },
    { name: '水', value: strength.shui, count: summary['水'] || 0, color: '#1E90FF' },
    { name: '火', value: strength.huo, count: summary['火'] || 0, color: '#FF4500' },
    { name: '土', value: strength.tu, count: summary['土'] || 0, color: '#8B4513' }
  ]
})

// 测试排盘
async function handleTest() {
  if (!currentArchive.value) {
    uni.showToast({
      title: '请先选择档案',
      icon: 'none'
    })
    return
  }

  errorMessage.value = ''

  try {
    console.log('🚀 开始测试后端排盘...')
    console.log('📤 档案ID:', currentArchive.value.id)
    
    // 使用新的 API
    const result = await baziStore.calculateByArchive(currentArchive.value.id, false)
    
    console.log('✅ 排盘成功!')
    console.log('📥 结果:', result)
  } catch (error: any) {
    console.error('❌ 排盘失败:', error)
    errorMessage.value = error.message || '排盘失败，请检查后端服务是否启动'
  }
}
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 30rpx;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 10rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

/* 档案信息 */
.archive-info {
  background: #f8f9fa;
  border-radius: 15rpx;
  padding: 20rpx;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-size: 28rpx;
  color: #666;
  width: 140rpx;
}

.value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.value.id {
  font-size: 24rpx;
  color: #999;
  word-break: break-all;
}

.empty {
  text-align: center;
  padding: 40rpx 0;
}

.empty text {
  display: block;
  font-size: 28rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.tip {
  font-size: 24rpx;
  color: #ccc;
}

/* 测试按钮 */
.test-button {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 50rpx;
  color: white;
  font-size: 32rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

.test-button.loading {
  background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
}

.test-button[disabled] {
  opacity: 0.5;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.icon {
  font-size: 36rpx;
}

/* 加载状态 */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0;
}

.spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid #f3f3f3;
  border-top: 4rpx solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20rpx;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.loading-tip {
  font-size: 24rpx;
  color: #999;
}

/* 结果卡片 */
.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.card-row {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.card-row:last-child {
  margin-bottom: 0;
}

.card-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  width: 140rpx;
}

.card-value {
  font-size: 28rpx;
  color: white;
  font-weight: 500;
}

.card-value.bazi {
  font-size: 36rpx;
  font-weight: bold;
  letter-spacing: 5rpx;
}

.card-value.id {
  font-size: 22rpx;
  word-break: break-all;
}

/* 四柱 */
.pillars-box {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.pillar-item {
  background: #f8f9fa;
  border-radius: 15rpx;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pillar-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.pillar-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.pillar-nayin {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.pillar-canggan {
  font-size: 22rpx;
  color: #999;
}

/* 五行 */
.wuxing-box {
  background: #f8f9fa;
  border-radius: 15rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.wuxing-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.wuxing-item {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.wuxing-item:last-child {
  margin-bottom: 0;
}

.wuxing-name {
  font-size: 26rpx;
  color: #333;
  width: 60rpx;
}

.wuxing-bar-container {
  flex: 1;
  height: 20rpx;
  background: #e0e0e0;
  border-radius: 10rpx;
  overflow: hidden;
  margin: 0 15rpx;
}

.wuxing-bar {
  height: 100%;
  transition: width 0.3s;
}

.wuxing-value {
  font-size: 24rpx;
  color: #333;
  width: 80rpx;
  text-align: right;
}

.wuxing-count {
  font-size: 22rpx;
  color: #999;
  width: 80rpx;
  text-align: right;
}

/* JSON 数据 */
.json-box {
  background: #1e1e1e;
  border-radius: 15rpx;
  padding: 20rpx;
}

.json-title {
  display: block;
  font-size: 28rpx;
  color: #4ec9b0;
  margin-bottom: 15rpx;
}

.json-content {
  max-height: 600rpx;
  overflow-y: auto;
}

.json-pre {
  font-size: 22rpx;
  color: #d4d4d4;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 错误提示 */
.error-box {
  background: #ffebee;
  border-radius: 15rpx;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-icon {
  font-size: 48rpx;
  margin-bottom: 15rpx;
}

.error-text {
  font-size: 26rpx;
  color: #c62828;
  text-align: center;
}

/* 提示 */
.tips-box {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20rpx;
  padding: 30rpx;
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 15rpx;
}

.tips-item {
  display: block;
  font-size: 24rpx;
  color: #666;
  line-height: 2;
  padding-left: 20rpx;
}
</style>
