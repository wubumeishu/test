<template>
  <view class="page-container">
    <ZenHeader title="每日运势" :show-menu="true" @menu="handleMenu" />

    <main class="main-scroll">
      <section class="top-card-section">
        <ZenCard padding="0" class="top-banner">
          <view class="banner-left">
            <view class="ink-bg">
              <!-- 月相图片：有图时显示，加载失败或无图时回退 cloud 图标 -->
              <image
                v-if="moonImageSrc"
                class="moon-phase-img"
                :src="moonImageSrc"
                mode="aspectFit"
                @error="onMoonImageError"
              />
              <text v-else class="material-symbols-outlined ink-icon">cloud</text>
            </view>

            <view class="banner-info">
              <view v-if="isSolarTerm">
                <text class="tag-text">二十四节气 · 第{{ solarTermIndex }}</text>
                <text class="date-text">{{ displayLunarDate }} · 公历 {{ displaySolarDate }}</text>
              </view>
              <view v-else>
                <text class="tag-text">月影禅心 · {{ yueXiangText }}</text>
                <text class="date-text">{{ displayLunarDate }} · {{ displayWeekDay }}</text>
              </view>

              <view class="quote-area">
                <text class="quote-text">{{ currentShortQuote }}</text>
              </view>
            </view>
          </view>

          <view class="banner-right">
            <text class="writing-vertical brush-font">{{ solarChineseDateDisplay }}</text>
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
          <ZenCard padding="30rpx 0" class="grid-item" v-for="item in fortuneDimensions" :key="item.label">
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
import { ref, computed, onMounted } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
import { Solar } from 'lunar-javascript'
import { useArchiveStore } from '@/store/useArchiveStore'

// --- 档案 Store ---
const archiveStore = useArchiveStore()

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
const moonPhaseName    = ref('')   // 月相名（getYueXiang），如：蛾眉、望
const yueXiang         = ref('')   // 同上，用于 almanac-header 显示
const yueXiangText     = ref('')   // 同上，语义化别名，供模板绑定
const moonImageSrc     = ref('')   // 月相图片路径
const dayYiList        = ref<string[]>([])  // 宜，取前两项
const dayJiList        = ref<string[]>([])  // 忌，取前两项

// ── 月相图片映射（农历日 1-30 → 8 种基础月相图）──
const getMoonPhaseImage = (day: number): string => {
  const base = '../../static/moon/'
  if (day === 1 || day === 30) return `${base}phase-1.svg`  // 新月 / 朔 / 晦
  if (day >= 2  && day <= 6)   return `${base}phase-2.svg`  // 蛾眉月（上升）
  if (day === 7 || day === 8)  return `${base}phase-3.svg`  // 上弦月
  if (day >= 9  && day <= 14)  return `${base}phase-4.svg`  // 盈凸月
  if (day === 15 || day === 16) return `${base}phase-5.svg` // 满月 / 望
  if (day >= 17 && day <= 21)  return `${base}phase-6.svg`  // 亏凸月
  if (day === 22 || day === 23) return `${base}phase-7.svg` // 下弦月
  if (day >= 24 && day <= 29)  return `${base}phase-8.svg`  // 残月（蛾眉亏）
  return `${base}phase-1.svg`  // 兜底
}

// 月相图片加载失败时回退到占位符
const onMoonImageError = () => {
  moonImageSrc.value = ''
}
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

// 跳转到测试页面
const goToTest = () => {
  uni.navigateTo({ url: '/pages/test/test' })
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
  const lunarDay = lunar.getDay()           // 农历数字日（1-30），用于图片映射
  const xiang = lunar.getYueXiang()
  moonPhaseName.value  = xiang
  yueXiang.value       = xiang
  yueXiangText.value   = xiang
  moonImageSrc.value   = getMoonPhaseImage(lunarDay)
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

/* 月相图片：撑满 ink-bg 容器，保持透明度与背景装饰一致 */
.moon-phase-img {
  width: 220rpx;
  height: 220rpx;
  opacity: 0.25;
  filter: sepia(0.3);
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
