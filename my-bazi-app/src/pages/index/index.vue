<template>
  <view class="page-container">
    <ZenHeader title="每日运势" :show-menu="true" @menu="handleMenu" />

    <main class="main-scroll">
      <section class="top-card-section">
        <ZenCard class="top-banner">
          <view class="banner-container">
            <view class="banner-left">
              <view class="ink-bg">
                <text class="material-symbols-outlined ink-icon">nights_stay</text>
              </view>

              <view class="banner-info">
                <view class="info-top">
                  <view v-if="isSolarTerm">
                    <text class="tag-text">二十四节气 · 第{{ solarTermIndex }}</text>
                    <text class="date-text">{{ displayLunarDate }} · 公历 {{ displaySolarDate }}</text>
                  </view>
                  <view v-else>
                    <text class="tag-text">月影禅心 · {{ yueXiangText }}</text>
                    <text class="date-text">{{ displayLunarDate }} · {{ displayWeekDay }}</text>
                  </view>
                </view>

                <view class="quote-area">
                  <text class="quote-text">{{ currentShortQuote }}</text>
                </view>
              </view>
            </view>

            <view class="banner-right">
              <text class="writing-vertical brush-font">{{ solarChineseDateDisplay }}</text>
            </view>
          </view>
        </ZenCard>
      </section>

      <section class="fortune-index-section">
        <view class="brush-circle">
          <!-- 使用双半圆实现进度圆环 -->
          <view class="ring-wrapper">
            <view class="ring-bg"></view>
            <view class="ring-progress-wrapper">
              <view class="ring-left" :style="{ transform: fortuneScore >= 50 ? 'rotate(180deg)' : `rotate(${(fortuneScore / 50) * 180}deg)` }"></view>
              <view class="ring-right" :style="{ transform: fortuneScore >= 50 ? `rotate(${((fortuneScore - 50) / 50) * 180}deg)` : 'rotate(0deg)' }"></view>
            </view>
          </view>
          <view class="score-box">
            <text class="score-num brush-font">{{ fortuneScore }}</text>
            <text class="score-label">今日运势指数</text>
          </view>
        </view>

        <!-- 干支日期：分段渲染，间隔点单独着色 -->
        <view class="calendar-info">
          <view class="ganzhi-row">
            <text class="ganzhi-seg">{{ displayBaziParts[0] }}</text>
            <text class="ganzhi-dot">·</text>
            <text class="ganzhi-seg">{{ displayBaziParts[1] }}</text>
            <text class="ganzhi-dot">·</text>
            <text class="ganzhi-seg">{{ displayBaziParts[2] }}</text>
          </view>
          <view class="gold-divider"></view>
          <text class="advice-text">{{ currentLongQuote }}</text>
        </view>
      </section>

      <section class="grid-section">
        <view class="fortune-grid">
          <ZenCard class="grid-item" v-for="item in fortuneDimensions" :key="item.label">
            <view class="grid-content">
              <text class="material-symbols-outlined grid-icon">{{ item.icon }}</text>
              <text class="grid-label">{{ item.label }}</text>
              <view class="dots-row">
                <view
                  class="dot"
                  v-for="i in 5"
                  :key="i"
                  :class="{ active: i <= item.level }"
                ></view>
              </view>
            </view>
          </ZenCard>
        </view>
      </section>

      <section class="almanac-section">
        <ZenCard padding="0" class="almanac-card">
          <view class="almanac-header">
            <text class="almanac-en">Traditional Calendar</text>
            <text class="almanac-lunar">{{ lunarMonthDay }} · {{ yueXiangText }}</text>
          </view>
          <view class="almanac-body">
            <view class="almanac-col">
              <text class="col-tag col-tag--yi">宜</text>
              <view class="col-content">
                <text
                  v-for="item in dayYiList"
                  :key="item"
                  class="luck-text"
                >{{ item }}</text>
                <text v-if="dayYiList.length === 0" class="luck-text luck-text--empty">—</text>
              </view>
            </view>
            <view class="almanac-col">
              <text class="col-tag col-tag--ji">忌</text>
              <view class="col-content">
                <text
                  v-for="item in dayJiList"
                  :key="item"
                  class="unluck-text"
                >{{ item }}</text>
                <text v-if="dayJiList.length === 0" class="unluck-text unluck-text--empty">—</text>
              </view>
            </view>
          </view>
        </ZenCard>
      </section>

      <section class="cta-section">
        <ZenCard class="cta-card">
          <view class="cta-container">
            <!-- 使用服务器托管的背景图 -->
            <view class="cta-bg"></view>
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
          </view>
        </ZenCard>
      </section>
    </main>

    <ZenTabBar :current="0" />

    <!-- 零档案破冰引导遮罩 -->
    <InitialGuideOverlay
      :visible="showGuideOverlay"
      @start="handleGuideStart"
      @dismiss="showGuideOverlay = false"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
import InitialGuideOverlay from '@/components/InitialGuideOverlay/InitialGuideOverlay.vue'
import { Solar } from 'lunar-javascript'
import { useArchiveStore } from '@/store/useArchiveStore'
import { useUserStore } from '@/store/useUserStore'

// --- 档案 Store ---
const archiveStore = useArchiveStore()
const userStore    = useUserStore()

// ── 零档案破冰遮罩 ──
// 初始值 false，等 onShow 拉取档案后再判断，避免闪烁
const showGuideOverlay = ref(false)

/**
 * 点击「开启起卦之旅」→ 跳转档案创建页
 * 带 isFirst=true 参数，让创建页显示更温馨的引导文案
 */
function handleGuideStart() {
  uni.navigateTo({
    url: '/package_archive/pages/archive/add?isFirst=true'
  })
}

// ── 页面守卫：每次页面显示时检查登录态 ──
onShow(() => {
  if (!userStore.token) {
    console.log('[Index.onShow] 未检测到 token，reLaunch → /pages/login/login')
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }

  // 拉取最新档案列表，完成后判断是否显示遮罩
  archiveStore.fetchArchives().then(() => {
    showGuideOverlay.value = archiveStore.archives.length === 0
  }).catch(() => {
    // 拉取失败时保守处理：不显示遮罩，避免误导用户
    showGuideOverlay.value = false
  })
})

// --- 实时日期状态 ---
const displaySolarDate     = ref('')          // 例：5月1日
const displayWeekDay       = ref('')          // 例：星期五
const displayLunarDate     = ref('')          // 例：三月廿七
const displayBaziParts     = ref<string[]>(['', '', ''])  // ['丙午年','壬辰月','乙亥日']
const solarChineseDateDisplay = ref('')       // 例：五月一日（公历汉字，用于竖排）

// --- 其他页面状态 ---
const isSolarTerm      = ref(false)
const currentSolarTerm = ref('')
const solarTermIndex   = ref(0)
const lunarMonthDay    = ref('')
const moonPhaseName    = ref('')
const yueXiang         = ref('')
const yueXiangText     = ref('')
const dayYiList        = ref<string[]>([])
const dayJiList        = ref<string[]>([])

// ==================== 禅意语录库 ====================
const shortQuotes = [
  '风起，宜敛神',
  '水复，宜静心',
  '云散，且徐行',

  '月明，宜远望',
  '花开，且从容',
]
const longQuotes = [
  '神安则泰，心定则宁。今日宜顺势而为。',
  '万物有时，不可强求。留一份空白，得一份自在。',
  '行到水穷处，坐看云起时。心境澄明，无往不利。',
  '竹密不妨流水过，山高岂碍白云飞。心怀坦荡，好运自来。',
]

const currentShortQuote = ref(shortQuotes[0])
const currentLongQuote  = ref(longQuotes[0])

const dailyQuote = currentShortQuote  // 保持向后兼容，模板直接用 currentShortQuote

// ==================== 千人千面运势算法 ====================

/**
 * 生成每日种子：将出生日期与今日日期拼接后做 djb2 哈希
 * 同一人同一天结果恒定，不同人或不同天结果不同
 */
const getDailySeed = (birthDate: string): number => {
  const today = new Date().toISOString().split('T')[0]
  const str = `${birthDate}-${today}`
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i)
    hash |= 0  // 转为 32 位整数
  }
  return Math.abs(hash)
}

// 运势指数（60–98），无默认档案时显示固定值 88
const fortuneScore = computed<number>(() => {
  const archive = archiveStore.defaultArchive
  if (!archive) return 88
  const seed = getDailySeed(archive.birthDate)
  return 60 + (seed % 39)
})

// 事业点数（1–5）
const careerLevel = computed<number>(() => {
  const archive = archiveStore.defaultArchive
  if (!archive) return 3
  const seed = getDailySeed(archive.birthDate)
  return (seed % 5) + 1
})

// 财富点数（1–5）
const wealthLevel = computed<number>(() => {
  const archive = archiveStore.defaultArchive
  if (!archive) return 4
  const seed = getDailySeed(archive.birthDate)
  return ((seed >> 1) % 5) + 1
})

// 姻缘点数（1–5）
const loveLevel = computed<number>(() => {
  const archive = archiveStore.defaultArchive
  if (!archive) return 2
  const seed = getDailySeed(archive.birthDate)
  return ((seed >> 2) % 5) + 1
})

// 宫格运势数据（由 computed 驱动，响应 defaultArchive 变化）
const fortuneDimensions = computed(() => [
  { label: '事业', icon: 'self_improvement', level: careerLevel.value },
  { label: '财富', icon: 'potted_plant',     level: wealthLevel.value },
  { label: '姻缘', icon: 'favorite',         level: loveLevel.value  },
])

const WEEK_NAMES = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
const CHINESE_MONTHS = ['一','二','三','四','五','六','七','八','九','十','十一','十二']
const CHINESE_DAYS = ['','一','二','三','四','五','六','七','八','九','十',
                      '十一','十二','十三','十四','十五','十六','十七','十八','十九','二十',
                      '二十一','二十二','二十三','二十四','二十五','二十六','二十七','二十八','二十九','三十','三十一']

// 菜单点击事件
const handleMenu = () => {
  uni.showToast({ title: '菜单功能', icon: 'none' })
}

onMounted(() => {
  const now   = new Date()
  const solar = Solar.fromDate(now) as any
  const lunar = solar.getLunar() as any

  // ── 公历 ──
  const m = now.getMonth() + 1
  const d = now.getDate()
  displaySolarDate.value = `${m}月${d}日`
  // 公历汉字格式，用于竖排书法位置，例：五月一日
  const solarChineseDate = `${CHINESE_MONTHS[m - 1]}月${CHINESE_DAYS[d]}日`
  solarChineseDateDisplay.value = solarChineseDate

  // ── 星期 ──
  displayWeekDay.value = WEEK_NAMES[now.getDay()]

  // ── 农历 ──
  const lunarStr = `${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`
  displayLunarDate.value = lunarStr
  lunarMonthDay.value    = lunarStr

  // ── 月相 & 黄历宜忌 ──
  const lunarDay = lunar.getDay()
  const xiang = lunar.getYueXiang()
  moonPhaseName.value  = xiang
  yueXiang.value       = xiang
  yueXiangText.value   = xiang
  dayYiList.value = (lunar.getDayYi() as string[]).slice(0, 2)
  dayJiList.value = (lunar.getDayJi() as string[]).slice(0, 2)

  // ── 干支（分段，供模板单独渲染间隔点颜色）──
  const yearGz  = lunar.getYearInGanZhi()
  const monthGz = lunar.getMonthInGanZhi()
  const dayGz   = lunar.getDayInGanZhi()
  displayBaziParts.value = [`${yearGz}年`, `${monthGz}月`, `${dayGz}日`]

  // ── 节气检测 ──
  const term = lunar.getJieQi()
  if (term) {
    isSolarTerm.value      = true
    currentSolarTerm.value = term
    const allTerms = ['小寒','大寒','立春','雨水','惊蛰','春分','清明','谷雨',
                      '立夏','小满','芒种','夏至','小暑','大暑','立秋','处暑',
                      '白露','秋分','寒露','霜降','立冬','小雪','大雪','冬至']
    solarTermIndex.value = allTerms.indexOf(term) + 1
  } else {
    isSolarTerm.value = false
  }

  // ── 禅意语录：基于 seed 随机抽取 ──
  // seed 优先使用默认档案的出生日期，否则用今日日期字符串
  const archive = archiveStore.defaultArchive
  const seedSource = archive
    ? getDailySeed(archive.birthDate)
    : (() => {
        const today = now.toISOString().split('T')[0]
        let h = 0
        for (let i = 0; i < today.length; i++) {
          h = ((h << 5) - h) + today.charCodeAt(i)
          h |= 0
        }
        return Math.abs(h)
      })()

  currentShortQuote.value = shortQuotes[seedSource % shortQuotes.length]
  currentLongQuote.value  = longQuotes[seedSource % longQuotes.length]

  // 节气感知：今天是节气则强制覆盖短语录
  if (term) {
    currentShortQuote.value = `今日${term}，宜调息`
  }
})
</script>

<style scoped>
/* 页面样式 - Material Symbols 图标字体已在 App.vue 全局定义 */

/* 布局基础 */
.page-container {
  min-height: 100vh;
  background-color: #F9F6F1;
  background-image: url("/static/handmade-paper.png");
}

/* 主内容滚动 */
.main-scroll {
  padding: 30rpx 40rpx 200rpx;
  max-width: 800px;
  margin: 0 auto;
}

/* 顶部 Banner */
.top-banner {
  overflow: hidden;
}

.banner-container {
  height: 380rpx;
  display: flex;
  overflow: hidden;
}

.banner-left {
  flex: 1;
  position: relative;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.ink-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.ink-icon {
  font-size: 160rpx;
  color: rgba(92, 74, 56, 0.25);
}

.banner-info {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.info-top {
  display: block;
}

.tag-text {
  display: block;
  font-size: 22rpx;
  font-weight: bold;
  color: #B23A34;
  letter-spacing: 0.2em;
  margin-bottom: 8rpx;
}

.date-text {
  display: block;
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.1em;
}

.quote-area {
  border-left: 2rpx solid rgba(178, 58, 52, 0.3);
  padding-left: 20rpx;
  margin-top: 20rpx;
}

.quote-text {
  display: block;
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

/* 圆环包裹器 */
.ring-wrapper {
  position: absolute;
  width: 100%;
  height: 100%;
}

/* 背景圆环 */
.ring-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3rpx solid rgba(212, 175, 55, 0.2);
  box-sizing: border-box;
}

/* 进度圆环包裹器 */
.ring-progress-wrapper {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
}

/* 左半圆 */
.ring-left {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  transform-origin: right center;
  transition: transform 1s ease-out;
}

.ring-left::before {
  content: '';
  position: absolute;
  top: 3rpx;
  left: 3rpx;
  right: 0;
  bottom: 3rpx;
  border: 6rpx solid #B23A34;
  border-radius: 180rpx 0 0 180rpx;
  border-right: none;
  box-sizing: border-box;
  transform-origin: right center;
}

/* 右半圆 */
.ring-right {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  transform-origin: left center;
  transition: transform 1s ease-out;
}

.ring-right::before {
  content: '';
  position: absolute;
  top: 3rpx;
  left: 0;
  right: 3rpx;
  bottom: 3rpx;
  border: 6rpx solid #B23A34;
  border-radius: 0 180rpx 180rpx 0;
  border-left: none;
  box-sizing: border-box;
  transform-origin: left center;
}

.score-box {
  position: relative;
  text-align: center;
  z-index: 10;
}

.score-num {
  display: block;
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

/* 干支行：分段渲染，间隔点朱砂红半透明 */
.ganzhi-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2rpx;
}

.ganzhi-seg {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: bold;
  letter-spacing: 0.1em;
  color: #1A1A1A;
}

.ganzhi-dot {
  font-size: 28rpx;
  color: rgba(178, 58, 52, 0.55);  /* 朱砂红，半透明 */
  font-weight: 400;
  padding: 0 4rpx;
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
  gap: 20rpx;
  margin-bottom: 60rpx;
}

.grid-item {
  overflow: hidden;
}

.grid-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40rpx 20rpx;
  min-height: 220rpx;
}

.grid-icon {
  color: rgba(178, 58, 52, 0.6);
  font-size: 56rpx;
  margin-bottom: 16rpx;
}

.grid-label {
  font-size: 26rpx;
  font-weight: 500;
  letter-spacing: 0.1em;
  margin-bottom: 12rpx;
  color: #333;
}

.dots-row {
  display: flex;
  gap: 6rpx;
  margin-top: 8rpx;
}

.dot {
  width: 10rpx;
  height: 10rpx;
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

/* 宜：主色调朱砂红 */
.col-tag--yi {
  color: #B23A34;
  font-weight: 600;
}

/* 忌：暗灰绿，与宜形成视觉对比 */
.col-tag--ji {
  color: #5A7A5A;
  font-weight: 600;
}

.luck-text {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: rgba(178, 58, 52, 0.8);
  margin-bottom: 10rpx;
  letter-spacing: 0.2em;
}

.luck-text--empty {
  color: rgba(178, 58, 52, 0.3);
}

.unluck-text {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: rgba(51, 51, 51, 0.6);
  margin-bottom: 10rpx;
  letter-spacing: 0.2em;
}

.unluck-text--empty {
  color: rgba(51, 51, 51, 0.2);
}

/* 底部引导卡片 */
.cta-card {
  overflow: hidden;
}

.cta-container {
  position: relative;
  height: 280rpx;
  display: flex;
  align-items: center;
  padding: 40rpx;
  overflow: hidden;
}

.cta-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* 临时使用渐变背景，消除 404 错误 */
  /* 等服务器文件上传成功后，可以改回图片：background-image: url('https://api.aiyuechuan.cn/static/cta-bg.jpg'); */
  background: linear-gradient(135deg, rgba(178, 58, 52, 0.08) 0%, rgba(212, 175, 55, 0.12) 100%);
  opacity: 0.6;
  z-index: 0;
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
  display: block;
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
