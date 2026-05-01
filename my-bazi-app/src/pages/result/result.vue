<template>
  <view class="page-container">
    <!-- 加载状态 -->
    <view v-if="baziStore.isLoading" class="loading-container">
      <view class="loading-content">
        <view class="zen-circle">
          <view class="circle-outer"></view>
          <view class="circle-inner"></view>
        </view>
        <text class="loading-text">天机推演中</text>
        <view class="loading-dots">
          <view class="dot"></view>
          <view class="dot"></view>
          <view class="dot"></view>
        </view>
      </view>
    </view>

    <!-- 结果展示 -->
    <view v-else-if="baziStore.currentBaziData" class="result-container">
      <!-- 顶部信息栏 -->
      <view class="header-bar">
        <view class="back-button" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <view class="header-info">
          <text class="name-text" :style="nameLetterSpacing">{{ displayName }}</text>
          <text class="gender-text">{{ genderText }}</text>
        </view>
      </view>

      <!-- 基础信息卡片 -->
      <view class="info-card glass-card">
        <view class="info-row">
          <text class="info-label">公历</text>
          <text class="info-value">{{ baziStore.currentBaziData.solar_date }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">农历</text>
          <text class="info-value">{{ baziStore.currentBaziData.lunar_date }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">生肖</text>
          <text class="info-value">{{ baziStore.currentBaziData.shengxiao }}</text>
        </view>
      </view>

      <!-- 核心命盘矩阵 -->
      <view class="bazi-matrix glass-card">
        <view class="matrix-title">
          <view class="title-line"></view>
          <text class="title-text">命盘八字</text>
          <view class="title-line"></view>
        </view>

        <view class="pillars-container">
          <view 
            v-for="(pillar, index) in pillarList" 
            :key="index"
            class="pillar-column"
            :class="{ 'pillar-day': pillar.isDayMaster }"
            :style="{ animationDelay: (index * 0.1) + 's' }"
          >
            <!-- 柱子标题 -->
            <view class="pillar-header">
              <text class="pillar-label">{{ pillar.title }}</text>
            </view>
            
            <!-- 十神 -->
            <view class="cell shishen-cell" :class="{ 'day-master-label': pillar.isDayMaster }">
              <text class="shishen-text" :class="{ 'highlight': pillar.isDayMaster }">
                {{ pillar.shishen }}
              </text>
            </view>
            
            <!-- 天干 -->
            <view class="cell gan-cell">
              <text 
                class="gan-text" 
                :class="{ 'highlight': pillar.isDayMaster }"
                :style="{ color: getWuxingColor(pillar.gan) }"
              >
                {{ pillar.gan }}
              </text>
            </view>
            
            <!-- 地支 -->
            <view class="cell zhi-cell">
              <text 
                class="zhi-text"
                :style="{ color: getWuxingColor(pillar.zhi) }"
              >
                {{ pillar.zhi }}
              </text>
            </view>
            
            <!-- 藏干 + 藏干十神 -->
            <view class="cell canggan-cell">
              <view class="canggan-box">
                <view 
                  v-for="(cg, cgIndex) in pillar.canggan" 
                  :key="'cg' + cgIndex"
                  class="cg-item"
                >
                  <text 
                    class="cg-text"
                    :style="{ color: getWuxingColor(cg) }"
                  >
                    {{ cg }}
                  </text>
                  <text class="cg-ss">
                    {{ pillar.canggan_shishen[cgIndex] || '-' }}
                  </text>
                </view>
                <view v-if="pillar.canggan.length === 0" class="cg-item">
                  <text class="cg-text">-</text>
                </view>
              </view>
            </view>
            
            <!-- 十二长生 -->
            <view class="cell changsheng-cell">
              <text class="changsheng-text">{{ pillar.changsheng }}</text>
            </view>
            
            <!-- 纳音 -->
            <view class="cell nayin-cell">
              <text class="nayin-text">{{ pillar.nayin }}</text>
            </view>
            
            <!-- 神煞 -->
            <view class="cell shensha-cell">
              <view class="shensha-box">
                <template v-if="pillar.shensha && pillar.shensha.length > 0">
                  <text 
                    v-for="(ss, ssIndex) in pillar.shensha" 
                    :key="'ss' + ssIndex" 
                    class="ss-tag"
                  >
                    {{ ss }}
                  </text>
                </template>
                <text v-else class="ss-empty">-</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 日主信息 -->
      <view class="daymaster-card glass-card">
        <view class="daymaster-content">
          <text class="daymaster-label">日主</text>
          <text 
            class="daymaster-char"
            :style="{ color: getWuxingColor(baziStore.currentBaziData.day_master) }"
          >{{ baziStore.currentBaziData.day_master }}</text>
          <text class="daymaster-wuxing">{{ baziStore.currentBaziData.day_master_wuxing }}命</text>
        </view>
      </view>

      <!-- 五行能量进度条 -->
      <view class="wuxing-energy glass-card">
        <view class="section-title">
          <text class="title-text">五行能量</text>
        </view>
        
        <view class="energy-bars">
          <view 
            v-for="item in wuxingList" 
            :key="item.name"
            class="energy-row"
          >
            <view class="energy-header">
              <text class="energy-name">{{ item.name }}</text>
              <text class="energy-value">{{ item.percent.toFixed(1) }}%</text>
            </view>
            <view class="energy-bar-container">
              <view 
                class="energy-bar" 
                :style="{ 
                  width: item.percent + '%', 
                  backgroundColor: item.color,
                  animationDelay: item.delay
                }"
              ></view>
            </view>
            <text class="energy-count">{{ item.count }}个</text>
          </view>
        </view>
      </view>

      <!-- AI 分析报告 (如果有) -->
      <view v-if="baziStore.currentBaziData.ai_report" class="ai-report glass-card">
        <view class="section-title">
          <text class="title-text">深度解析</text>
        </view>
        <view class="ai-content">
          <text class="ai-text">{{ baziStore.currentBaziData.ai_report }}</text>
        </view>
      </view>

      <!-- 底部留白 -->
      <view class="bottom-spacer"></view>
    </view>

    <!-- 无数据状态 -->
    <view v-else class="empty-container">
      <view class="empty-content">
        <text class="empty-icon">📜</text>
        <text class="empty-text">暂无排盘数据</text>
        <text class="empty-tip">请先进行八字排盘</text>
        <button class="empty-button" @click="goBack">
          <text class="button-text">返回上页</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useBaziStore } from '@/store/useBaziStore'

// Store
const baziStore = useBaziStore()

// 命主姓名：优先取 baseInfo（排盘时已同步），兜底 currentBaziData.name，再兜底「未知」
const displayName = computed(() => {
  return baziStore.baseInfo?.name
    || baziStore.currentBaziData?.name
    || '未知'
})

// 短名字（≤2字）加大字间距，匹配整体排版美学
const nameLetterSpacing = computed(() => {
  const len = displayName.value.length
  if (len <= 1) return { letterSpacing: '20rpx' }
  if (len <= 2) return { letterSpacing: '12rpx' }
  return { letterSpacing: '6rpx' }
})

// 性别文本
const genderText = computed(() => {
  if (!baziStore.currentBaziData) return ''
  return baziStore.currentBaziData.gender === 1 ? '乾造' : '坤造'
})

// 日柱标题：根据性别显示「元男」或「元女」
const dayPillarTitle = computed(() => {
  if (!baziStore.currentBaziData) return '日柱'
  return baziStore.currentBaziData.gender === 1 ? '元男' : '元女'
})

// 四柱列表（按照现代习惯：从左到右 = 年月日时）
const pillarList = computed(() => {
  if (!baziStore.currentBaziData) return []
  
  const data = baziStore.currentBaziData
  
  return [
    {
      title: '年柱',
      gan: data.year_pillar.gan,
      zhi: data.year_pillar.zhi,
      nayin: data.year_pillar.nayin,
      canggan: data.year_pillar.canggan || [],
      shishen: data.year_pillar.shishen || '-',
      changsheng: data.year_pillar.changsheng || '-',
      canggan_shishen: data.year_pillar.canggan_shishen || [],
      shensha: data.year_pillar.shensha || [],
      isDayMaster: false
    },
    {
      title: '月柱',
      gan: data.month_pillar.gan,
      zhi: data.month_pillar.zhi,
      nayin: data.month_pillar.nayin,
      canggan: data.month_pillar.canggan || [],
      shishen: data.month_pillar.shishen || '-',
      changsheng: data.month_pillar.changsheng || '-',
      canggan_shishen: data.month_pillar.canggan_shishen || [],
      shensha: data.month_pillar.shensha || [],
      isDayMaster: false
    },
    {
      title: dayPillarTitle.value,
      gan: data.day_pillar.gan,
      zhi: data.day_pillar.zhi,
      nayin: data.day_pillar.nayin,
      canggan: data.day_pillar.canggan || [],
      shishen: data.day_pillar.shishen || '日主',
      changsheng: data.day_pillar.changsheng || '-',
      canggan_shishen: data.day_pillar.canggan_shishen || [],
      shensha: data.day_pillar.shensha || [],
      isDayMaster: true
    },
    {
      title: '时柱',
      gan: data.hour_pillar.gan,
      zhi: data.hour_pillar.zhi,
      nayin: data.hour_pillar.nayin,
      canggan: data.hour_pillar.canggan || [],
      shishen: data.hour_pillar.shishen || '-',
      changsheng: data.hour_pillar.changsheng || '-',
      canggan_shishen: data.hour_pillar.canggan_shishen || [],
      shensha: data.hour_pillar.shensha || [],
      isDayMaster: false
    }
  ]
})

// 五行颜色映射
const getWuxingColor = (char: string): string => {
  const colors = {
    wood: '#4CAF50',   // 木：绿色
    fire: '#E53935',   // 火：红色
    earth: '#8D6E63',  // 土：褐色
    metal: '#D4AF37',  // 金：金色
    water: '#1E88E5'   // 水：蓝色
  }
  
  const wuxingMap: Record<string, string> = {
    // 木
    '甲': colors.wood, '乙': colors.wood, '寅': colors.wood, '卯': colors.wood,
    // 火
    '丙': colors.fire, '丁': colors.fire, '巳': colors.fire, '午': colors.fire,
    // 土
    '戊': colors.earth, '己': colors.earth, '辰': colors.earth, '戌': colors.earth, '丑': colors.earth, '未': colors.earth,
    // 金
    '庚': colors.metal, '辛': colors.metal, '申': colors.metal, '酉': colors.metal,
    // 水
    '壬': colors.water, '癸': colors.water, '亥': colors.water, '子': colors.water
  }
  
  return wuxingMap[char] || '#333333' // 默认深灰
}

// 五行列表
const wuxingList = computed(() => {
  if (!baziStore.currentBaziData) return []
  
  const { wuxing_strength, wuxing_summary } = baziStore.currentBaziData
  
  return [
    { 
      name: '金', 
      percent: wuxing_strength.jin, 
      count: wuxing_summary.金 || 0,
      color: 'rgba(212, 175, 55, 0.7)',  // 金色 (降低饱和度)
      delay: '0s'
    },
    { 
      name: '木', 
      percent: wuxing_strength.mu, 
      count: wuxing_summary.木 || 0,
      color: 'rgba(76, 129, 68, 0.7)',  // 深绿 (降低饱和度)
      delay: '0.1s'
    },
    { 
      name: '水', 
      percent: wuxing_strength.shui, 
      count: wuxing_summary.水 || 0,
      color: 'rgba(52, 108, 156, 0.7)',  // 深蓝 (降低饱和度)
      delay: '0.2s'
    },
    { 
      name: '火', 
      percent: wuxing_strength.huo, 
      count: wuxing_summary.火 || 0,
      color: 'rgba(192, 57, 43, 0.7)',  // 朱砂红 (降低饱和度)
      delay: '0.3s'
    },
    { 
      name: '土', 
      percent: wuxing_strength.tu, 
      count: wuxing_summary.土 || 0,
      color: 'rgba(139, 115, 85, 0.7)',  // 土黄 (降低饱和度)
      delay: '0.4s'
    }
  ]
})

// 页面加载时隐藏 TabBar
onMounted(() => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [结果页] TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [结果页] 当前页面无 TabBar')
  })
})

// 返回上一页（兼容从历史记录或排盘准备页进入的场景）
function goBack() {
  uni.navigateBack()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;500;600;700;900&display=swap');

/* ==================== 全局变量 ==================== */
.page-container {
  --zen-bg: #F8F6F3;
  --zen-white: #FEFEFE;
  --zen-ink: #1A1A1A;
  --zen-gray: #8E8E93;
  --zen-border: rgba(0, 0, 0, 0.08);
  --zen-cinnabar: #C0392B;
  --zen-shadow: rgba(0, 0, 0, 0.05);
}

/* ==================== 页面容器 ==================== */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8F6F3 0%, #F0EDE8 100%);
  background-image: 
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* ==================== 毛玻璃卡片 ==================== */
.glass-card {
  background: rgba(254, 254, 254, 0.75);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.04);
}

/* ==================== 加载状态 ==================== */

.loading-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.zen-circle {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 60rpx;
}

.circle-outer {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  border: 2rpx solid rgba(192, 57, 43, 0.3);
  border-radius: 50%;
  animation: rotate 3s linear infinite;
}

.circle-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120rpx;
  height: 120rpx;
  border: 2rpx solid rgba(192, 57, 43, 0.6);
  border-radius: 50%;
  animation: rotate 2s linear infinite reverse;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 300;
  color: #1A1A1A;
  letter-spacing: 12rpx;
  margin-bottom: 30rpx;
}

.loading-dots {
  display: flex;
  gap: 16rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  background-color: #C0392B;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* ==================== 结果容器 ==================== */

.result-container {
  padding: 30rpx 30rpx 120rpx;
  max-width: 750rpx;
  margin: 0 auto;
}

/* ==================== 顶部信息栏 ==================== */
.header-bar {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  padding: 20rpx 0;
}

.back-button {
  margin-right: 30rpx;
}

.back-icon {
  font-size: 48rpx;
  color: #1A1A1A;
}

.header-info {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 20rpx;
}

.name-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 44rpx;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 6rpx;
}

.gender-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: #8E8E93;
  letter-spacing: 4rpx;
}

/* ==================== 基础信息卡片 ==================== */
.info-card {
  padding: 30rpx 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
}

.info-row:not(:last-child) {
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
}

.info-label {
  font-size: 26rpx;
  color: #8E8E93;
  width: 100rpx;
  letter-spacing: 4rpx;
}

.info-value {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: #1A1A1A;
  letter-spacing: 2rpx;
}

/* ==================== 核心命盘矩阵 ==================== */
.bazi-matrix {
  padding: 40rpx 30rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.matrix-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  margin-bottom: 50rpx;
}

.title-line {
  width: 80rpx;
  height: 0.5px;
  background-color: rgba(0, 0, 0, 0.15);
}

.title-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 12rpx;
}

/* 四柱容器 */
.pillars-container {
  display: flex;
  justify-content: space-around;
  gap: 16rpx;
}

/* 柱子列 */
.pillar-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 12rpx;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.5);
  text-align: center;
  opacity: 0;
  transform: translateY(30rpx);
  animation: slideUp 0.6s ease-out forwards;
}

/* 日柱高亮 */
.pillar-day {
  border: 1px solid rgba(192, 57, 43, 0.3);
  background: rgba(192, 57, 43, 0.02);
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 柱子标题 */
.pillar-header {
  padding: 16rpx 0;
  text-align: center;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
}

.pillar-label {
  font-size: 22rpx;
  color: #8E8E93;
  letter-spacing: 4rpx;
}

/* 单元格 */
.cell {
  padding: 16rpx 8rpx;
  text-align: center;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.03);
  min-height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell:last-child {
  border-bottom: none;
}

/* 十神 */
.shishen-cell {
  background: rgba(0, 0, 0, 0.01);
}

.shishen-text {
  font-size: 22rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
}

.day-master-label {
  background: rgba(192, 57, 43, 0.05);
}

.shishen-text.highlight {
  color: #C0392B;
  font-weight: 500;
}

/* 天干 */
.gan-cell {
  background: rgba(255, 255, 255, 0.8);
}

.gan-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 4rpx;
}

.gan-text.highlight {
  /* 日主高亮时使用朱砂红，优先级高于五行颜色 */
  font-weight: 900;
}

/* 地支 */
.zhi-cell {
  background: rgba(255, 255, 255, 0.8);
}

.zhi-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 4rpx;
}

/* 藏干容器 - 固定高度解决错位问题 */
.canggan-cell {
  padding: 12rpx 8rpx;
  min-height: 180rpx; /* 确保容纳3行藏干 */
}

.canggan-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 140rpx; /* 强制固定高度，确保能容纳3行小字且底部留白 */
  margin: 10rpx 0;
  gap: 4rpx;
}

.cg-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
  height: 40rpx; /* 每行藏干固定高度 */
  width: 100%;
}

.cg-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  font-weight: 500;
  letter-spacing: 1rpx;
}

.cg-ss {
  font-size: 20rpx;
  color: #888; /* 藏干十神保持灰色 */
  letter-spacing: 1rpx;
}

/* 十二长生 - 固定高度 */
.changsheng-cell {
  min-height: 50rpx;
  background: rgba(0, 0, 0, 0.01);
}

.changsheng-text {
  display: block;
  height: 40rpx; /* 固定高度 */
  line-height: 40rpx;
  font-size: 22rpx;
  color: #666;
  letter-spacing: 2rpx;
}

/* 纳音 - 固定高度 */
.nayin-cell {
  background: rgba(0, 0, 0, 0.01);
}

.nayin-text {
  display: block;
  height: 40rpx; /* 固定高度 */
  line-height: 40rpx;
  font-size: 20rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
}

/* 神煞 - 自适应高度，flex 换行 */
.shensha-cell {
  padding: 12rpx 8rpx;
}

.shensha-box {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-start;
  gap: 6rpx;
}

.ss-tag {
  font-size: 20rpx;
  color: #7f8c8d;
  background-color: rgba(0, 0, 0, 0.04);
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  line-height: 1.2;
  white-space: nowrap;
}

.ss-empty {
  font-size: 20rpx;
  color: #ccc;
}

/* ==================== 日主信息 ==================== */
.daymaster-card {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.daymaster-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 16rpx;
}

.daymaster-label {
  font-size: 24rpx;
  color: #8E8E93;
  letter-spacing: 6rpx;
  text-align: center;
  display: block;
  width: 100%;
}

.daymaster-char {
  font-family: 'Noto Serif SC', serif;
  font-size: 140rpx;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-align: center;
  display: block;
  width: 100%;
}

.daymaster-wuxing {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 400;
  color: #8E8E93;
  letter-spacing: 4rpx;
  text-align: center;
  display: block;
  width: 100%;
}

/* ==================== 五行能量进度条 ==================== */
.wuxing-energy {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.section-title {
  margin-bottom: 40rpx;
  text-align: center;
}

.energy-bars {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.energy-row {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.energy-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.energy-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 4rpx;
}

.energy-value {
  font-size: 24rpx;
  color: #8E8E93;
  letter-spacing: 1rpx;
}

.energy-bar-container {
  height: 32rpx;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 16rpx;
  overflow: hidden;
}

.energy-bar {
  height: 100%;
  border-radius: 16rpx;
  opacity: 0;
  animation: fillBar 1s ease-out forwards;
  transition: width 0.6s ease;
}

@keyframes fillBar {
  to {
    opacity: 1;
  }
}

.energy-count {
  font-size: 22rpx;
  color: #8E8E93;
  text-align: right;
  letter-spacing: 1rpx;
}

/* ==================== AI 分析报告 ==================== */
.ai-report {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.ai-content {
  padding: 30rpx;
  background: rgba(0, 0, 0, 0.02);
  border-left: 4rpx solid #C0392B;
  border-radius: 8rpx;
}

.ai-text {
  font-size: 28rpx;
  color: #1A1A1A;
  line-height: 48rpx;
  letter-spacing: 2rpx;
  white-space: pre-wrap;
}

/* ==================== 无数据状态 ==================== */

.empty-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 60rpx;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 40rpx;
  opacity: 0.5;
}

.empty-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 6rpx;
  margin-bottom: 20rpx;
}

.empty-tip {
  font-size: 26rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
  margin-bottom: 60rpx;
}

.empty-button {
  width: 400rpx;
  height: 88rpx;
  background-color: #B23A34;
  border: none;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-text {
  font-size: 28rpx;
  color: #FFFFFF;
  letter-spacing: 6rpx;
}

/* 底部留白 */
.bottom-spacer {
  height: 80rpx;
}
</style>
