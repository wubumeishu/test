<template>
  <view class="page-container">
    <ZenHeader title="每日运势" :show-menu="true" @menu="handleMenu" />

    <main class="main-scroll">
      <section class="top-card-section">
        <ZenCard padding="0" class="top-banner">
          <view class="banner-left">
            <view class="ink-bg">
              <text class="material-symbols-outlined ink-icon">cloud</text>
            </view>
            
            <view class="banner-info">
              <view v-if="isSolarTerm">
                <text class="tag-text">二十四节气 · 第{{ solarTermIndex }}</text>
                <text class="date-text">{{ lunarDateStr }} · 公历 {{ todayStr }}</text>
              </view>
              <view v-else>
                <text class="tag-text">月影禅心 · {{ moonPhaseName }}</text>
                <text class="date-text">{{ lunarDateStr }} · {{ weekDayStr }}</text>
              </view>
              
              <view class="quote-area">
                <text class="quote-text">{{ dailyQuote }}</text>
              </view>
            </view>
          </view>
          
          <view class="banner-right">
            <text class="writing-vertical brush-font">{{ isSolarTerm ? currentSolarTerm : lunarMonthDay }}</text>
          </view>
        </ZenCard>
      </section>

      <section class="fortune-index-section">
        <view class="brush-circle">
          <svg class="svg-ring" viewBox="0 0 100 100">
            <circle class="ring-bg" cx="50" cy="50" r="45"></circle>
            <circle class="ring-progress" cx="50" cy="50" r="45" :style="{ strokeDashoffset: 283 - (283 * fortuneScore) / 100 }"></circle>
          </svg>
          <view class="score-box">
            <text class="score-num brush-font">{{ fortuneScore }}</text>
            <text class="score-label">今日运势指数</text>
          </view>
        </view>
        
        <view class="calendar-info">
          <text class="ganzhi-text">{{ ganzhiDate }}</text>
          <view class="gold-divider"></view>
          <text class="advice-text">秋水长天，神安则泰。岁运交替，宜守成、省身、积德。</text>
        </view>
      </section>

      <section class="grid-section">
        <view class="fortune-grid">
          <ZenCard padding="30rpx 0" class="grid-item" v-for="item in fortuneDimensions" :key="item.label">
            <text class="material-symbols-outlined grid-icon">{{ item.icon }}</text>
            <text class="grid-label">{{ item.label }}</text>
            <view class="dots-row">
              <view class="dot" v-for="i in 4" :key="i" :class="{ active: i <= item.score }"></view>
            </view>
          </ZenCard>
        </view>
      </section>

      <section class="almanac-section">
        <ZenCard padding="0" class="almanac-card">
          <view class="almanac-header">
            <text class="almanac-en">Traditional Calendar</text>
            <text class="almanac-lunar">{{ lunarMonthDay }}</text>
          </view>
          <view class="almanac-body">
            <view class="almanac-col">
              <text class="col-tag">宜</text>
              <view class="col-content">
                <text class="luck-text">纳采</text>
                <text class="luck-text">乞巧</text>
              </view>
            </view>
            <view class="almanac-col">
              <text class="col-tag">忌</text>
              <view class="col-content">
                <text class="unluck-text">开市</text>
                <text class="unluck-text">动土</text>
              </view>
            </view>
          </view>
        </ZenCard>
      </section>

      <section class="cta-section">
        <ZenCard padding="40rpx" class="cta-card">
          <image class="cta-bg" src="https://images.unsplash.com/photo-1518133910546-b6c2fb7d79e3?q=80&w=400" mode="aspectFill"></image>
          <view class="cta-content">
            <view class="cta-tag-row">
              <view class="cta-line"></view>
              <text class="cta-tag">大师亲测</text>
            </view>
            <text class="cta-title">年度深度运势解析</text>
            <text class="cta-desc">探寻生命律动，预见未来先机</text>
          </view>
          <view class="cta-arrow">
            <text class="material-symbols-outlined">arrow_forward</text>
          </view>
        </ZenCard>
      </section>
    </main>

    <!-- 测试按钮 (开发环境) -->
    <view class="test-button-float" @click="goToTest">
      <text class="test-icon">🧪</text>
      <text class="test-text">测试</text>
    </view>

    <ZenTabBar :current="0" />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
import { Solar, Lunar } from 'lunar-javascript'

// --- 状态逻辑 ---
const isSolarTerm = ref(true)
const currentSolarTerm = ref('立秋')
const solarTermIndex = ref(13)
const lunarMonthDay = ref('七月初七')
const lunarDateStr = ref('八月初七')
const moonPhaseName = ref('蛾眉月')
const todayStr = ref('08.07')
const weekDayStr = ref('星期三')
const ganzhiDate = ref('甲辰年 · 壬申月 · 癸卯日')
const dailyQuote = ref('“秋风起，宜敛神。暑气渐消，万物从容。”')
const fortuneScore = ref(88)

const fortuneDimensions = ref([
  { label: '姻缘', icon: 'favorite', score: 3 },
  { label: '财富', icon: 'potted_plant', score: 4 },
  { label: '事业', icon: 'self_improvement', score: 2 }
])

// 菜单点击事件
const handleMenu = () => {
  uni.showToast({ title: '菜单功能', icon: 'none' })
}

// 跳转到测试页面
const goToTest = () => {
  uni.navigateTo({
    url: '/pages/test/test'
  })
}

onMounted(() => {
  // 这里可以实时计算节气和农历
  const now = new Date()
  const solar = Solar.fromDate(now)
  const lunar = solar.getLunar()
  
  lunarMonthDay.value = `${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`
  ganzhiDate.value = `${lunar.getYearInGanZhi()}年 · ${lunar.getMonthInGanZhi()}月 · ${lunar.getDayInGanZhi()}日`
  
  // 简单节气检测逻辑
  const term = lunar.getJieQi()
  if (term) {
    isSolarTerm.value = true
    currentSolarTerm.value = term
  } else {
    isSolarTerm.value = false
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Ma+Shan+Zheng&display=swap');

/* 布局基础 */
.page-container {
  min-height: 100vh;
  background-color: #F9F6F1;
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
}

/* 主内容滚动 */
.main-scroll {
  padding: 30rpx 40rpx 200rpx;
  max-width: 800px;
  margin: 0 auto;
}

/* 顶部 Banner */
.top-banner {
  height: 380rpx;
  display: flex;
  overflow: hidden;
}

.banner-left {
  flex: 1;
  position: relative;
  padding: 50rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.ink-bg {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.15;
}

.ink-icon {
  font-size: 240rpx;
  transform: rotate(12deg);
  color: #333;
}

.tag-text {
  display: block;
  font-size: 20rpx;
  font-weight: bold;
  color: #B23A34;
  letter-spacing: 0.3em;
  margin-bottom: 8rpx;
}

.date-text {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.1em;
}

.quote-area {
  border-left: 2rpx solid rgba(178, 58, 52, 0.3);
  padding-left: 24rpx;
  margin-right: 40rpx;
}

.quote-text {
  font-size: 24rpx;
  line-height: 1.6;
  color: rgba(51, 51, 51, 0.8);
  font-style: italic;
}

.banner-right {
  width: 120rpx;
  background: rgba(255, 255, 255, 0.3);
  border-left: 1rpx solid rgba(212, 175, 55, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 字体：竖排书法 */
.writing-vertical {
  writing-mode: vertical-rl;
  text-orientation: upright;
}

.brush-font {
  font-family: 'Ma Shan Zheng', cursive;
}

.banner-right .brush-font {
  font-size: 60rpx;
  color: #B23A34;
  letter-spacing: 20rpx;
}

/* 运势圆环 */
.fortune-index-section {
  padding: 60rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brush-circle {
  position: relative;
  width: 360rpx;
  height: 360rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.svg-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #D4AF37;
  stroke-width: 1;
  opacity: 0.2;
}

.ring-progress {
  fill: none;
  stroke: #B23A34;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s ease-out;
}

.score-box {
  text-align: center;
  z-index: 10;
}

.score-num {
  font-size: 100rpx;
  color: #B23A34;
  line-height: 1;
}

.score-label {
  display: block;
  font-size: 18rpx;
  color: rgba(51, 51, 51, 0.5);
  letter-spacing: 0.4em;
  margin-top: 10rpx;
}

.calendar-info {
  text-align: center;
}

.ganzhi-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: bold;
  letter-spacing: 0.15em;
}

.gold-divider {
  width: 50rpx;
  height: 2rpx;
  background: rgba(212, 175, 55, 0.4);
  margin: 20rpx auto;
}

.advice-text {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.7);
  padding: 0 40rpx;
  line-height: 1.8;
}

/* 宫格运势 */
.fortune-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30rpx;
  margin-bottom: 60rpx;
}

.grid-item {
  padding: 30rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.grid-icon {
  color: rgba(178, 58, 52, 0.6);
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.grid-label {
  font-size: 24rpx;
  font-weight: 500;
  letter-spacing: 0.1em;
}

.dots-row {
  display: flex;
  gap: 4rpx;
  margin-top: 16rpx;
}

.dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: rgba(178, 58, 52, 0.1);
}

.dot.active {
  background: #B23A34;
}

/* 黄历宜忌 */
.almanac-section {
  margin-bottom: 60rpx;
}

.almanac-card {
  overflow: hidden;
}

.almanac-header {
  background: rgba(255, 255, 255, 0.2);
  padding: 16rpx 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid rgba(212, 175, 55, 0.1);
}

.almanac-en {
  font-size: 20rpx;
  font-weight: bold;
  letter-spacing: 0.3em;
  color: rgba(51, 51, 51, 0.5);
  text-transform: uppercase;
}

.almanac-lunar {
  font-size: 20rpx;
  color: #B23A34;
  font-weight: 500;
}

.almanac-body {
  display: flex;
}

.almanac-col {
  flex: 1;
  padding: 40rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1rpx solid rgba(212, 175, 55, 0.1);
}

.almanac-col:last-child {
  border-right: none;
}

.col-tag {
  font-size: 20rpx;
  color: rgba(51, 51, 51, 0.4);
  margin-bottom: 24rpx;
  letter-spacing: 0.2em;
}

.luck-text {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: rgba(178, 58, 52, 0.8);
  margin-bottom: 10rpx;
  letter-spacing: 0.2em;
}

.unluck-text {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: rgba(51, 51, 51, 0.6);
  margin-bottom: 10rpx;
  letter-spacing: 0.2em;
}

/* 底部引导卡片 */
.cta-card {
  height: 280rpx;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.cta-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  filter: grayscale(0.5);
  opacity: 0.3;
}

.cta-content {
  position: relative;
  z-index: 2;
  flex: 1;
}

.cta-tag-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.cta-line {
  width: 32rpx;
  height: 2rpx;
  background: #B23A34;
}

.cta-tag {
  font-size: 24rpx;
  color: #B23A34;
  font-weight: bold;
  letter-spacing: 0.3em;
}

.cta-title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #1A1A1A;
  margin-bottom: 12rpx;
  letter-spacing: 0.1em;
}

.cta-desc {
  font-size: 20rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.2em;
}

.cta-arrow {
  position: relative;
  z-index: 2;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 1px solid rgba(178, 58, 52, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #B23A34;
}
</style>