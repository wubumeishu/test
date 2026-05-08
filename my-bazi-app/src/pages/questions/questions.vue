<template>
  <view class="page-container">
    <ZenHeader title="测算大厅" :show-menu="true" :show-history="true" @menu="handleMenu" @history="handleHistory" />

    <main class="main-content">
      <view class="search-container">
        <view class="search-box">
          <text class="material-symbols-outlined search-icon">search</text>
          <input 
            class="search-input" 
            placeholder="探寻心中所惑..." 
            placeholder-class="placeholder-style"
          />
        </view>
      </view>

      <scroll-view scroll-x class="category-scroll" :show-scrollbar="false">
        <view class="tab-list">
          <view 
            class="tab-item" 
            v-for="(tab, index) in tabs" 
            :key="index"
            :class="{ active: currentTab === index }"
            @click="currentTab = index"
          >
            <text class="tab-text">{{ tab }}</text>
          </view>
        </view>
      </scroll-view>

      <view class="section-title-box">
        <text class="section-title">精选推荐</text>
        <text class="section-subtitle">CURATED SELECTION</text>
      </view>

      <view class="grid-container">
        <view 
          class="grid-item" 
          v-for="(item, index) in gridItems" 
          :key="index"
          hover-class="grid-item-hover"
          @click="handleGridItemClick(item)"
        >
          <view class="icon-wrapper">
            <text class="material-symbols-outlined ink-wash-icon">{{ item.icon }}</text>
          </view>
          <text class="item-title">{{ item.title }}</text>
          <text class="item-subtitle">{{ item.subtitle }}</text>
          <view class="divider"></view>
          <text class="item-action">{{ item.action }}</text>
        </view>
      </view>

      <!-- MBTI 灵性探索入口 -->
      <view class="mbti-section" @click="goToMBTI">
        <view class="mbti-card">
          <view class="mbti-left">
            <view class="mbti-icon-wrap">
              <text class="mbti-icon">✦</text>
            </view>
          </view>
          <view class="mbti-body">
            <view class="mbti-tag-row">
              <view class="mbti-tag-line"></view>
              <text class="mbti-tag">PERSONALITY · 性格探索</text>
            </view>
            <text class="mbti-title">MBTI 灵性探索</text>
            <text class="mbti-desc">结合现代心理学，遇见最真实的自己</text>
          </view>
          <view class="mbti-arrow">
            <text class="material-symbols-outlined">arrow_forward</text>
          </view>
        </view>
      </view>

      <view class="banner-section">
        <ZenCard padding="0" class="daily-banner" @click="goToDailyFortune">
          <view class="banner-bg-wrapper"></view>
          <view class="banner-content">
            <text class="banner-tag">DAILY FLOW</text>
            <text class="banner-title">今日运势</text>
            <view class="banner-link">
              <view class="link-line"></view>
              <text class="link-text">查看今日大吉方位</text>
            </view>
          </view>
        </ZenCard>
      </view>
    </main>

    <ZenTabBar :current="1" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'

// 分类 Tabs - 更新为完整的 8 个类目以测试横向滚动
const tabs = ref(['全部', '传统命理', '西方星象', '情感占卜', '居家风水', '姓名解密', '起卦周易', '前世今生'])
const currentTab = ref(0)

// 网格数据源 (方便后期从 Python 后端动态获取)
const gridItems = ref([
  { icon: 'view_quilt',   title: '八字排盘', subtitle: 'BAZI CHART',        action: 'BAZI_SETUP' },
  { icon: 'auto_stories', title: '八字精批', subtitle: 'DESTINY INSIGHT',   action: 'BAZI_DEEP'  },
  { icon: 'grain',        title: '紫微斗数', subtitle: 'CELESTIAL CHART',   action: 'VIEW'       },
  { icon: 'style',        title: '塔罗占卜', subtitle: 'INNER ORACLE',      action: 'REVEAL'     },
  { icon: 'architecture', title: '居家风水', subtitle: 'HARMONIOUS LIVING', action: 'ANALYZE'    },
  { icon: 'psychology',   title: 'MBTI 测试', subtitle: 'PERSONALITY',      action: 'MBTI' },
])

// 菜单和历史点击事件
const handleMenu = () => {
  uni.showToast({ title: '菜单功能', icon: 'none' })
}

const handleHistory = () => {
  uni.showToast({ title: '历史记录', icon: 'none' })
}

// 跳转到今日运势页
const goToDailyFortune = () => {
  uni.switchTab({ url: '/pages/index/index' })
}

// 跳转到 MBTI 测算页
const goToMBTI = () => {
  uni.navigateTo({ url: '/package_tests/pages/questions/mbti' })
}

// 跳转到塔罗占卜页
const goToTarot = () => {
  uni.navigateTo({ url: '/package_tests/pages/questions/tarot' })
}

// 网格项点击事件
const handleGridItemClick = (item: any) => {
  console.log('🔘 [questions] 点击网格项:', item)
  
  if (item.action === 'BAZI_SETUP') {
    // 普通排盘：不带参数
    uni.navigateTo({ url: '/pages/bazi/setup' })
  } else if (item.action === 'BAZI_DEEP') {
    // 八字精批：携带 mode=depth 参数
    uni.navigateTo({ url: '/pages/bazi/setup?mode=depth' })
  } else if (item.action === 'MBTI') {
    goToMBTI()
  } else if (item.action === 'REVEAL') {
    goToTarot()
  } else {
    uni.showToast({ title: `${item.title} 功能开发中`, icon: 'none', duration: 1500 })
  }
}
</script>

<style scoped>
/* 页面样式 - Material Symbols 图标字体已在 App.vue 全局定义 */

/* 全局变量 */
.page-container {
  --zen-bg: #FCFAF8;
  --zen-ink: #1A1A1A;
  --zen-gray: #8E8E93;
  --zen-border: #F0F0F0;
  --zen-accent: #A68B67;
  --zen-cinnabar: #B22222;
  
  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

/* 搜索框 */
.search-container {
  padding: 0 40rpx 30rpx;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0;
  color: var(--zen-gray);
  font-size: 36rpx;
  font-weight: 200;
}

.search-input {
  width: 100%;
  height: 60rpx;
  padding-left: 60rpx;
  font-size: 26rpx;
  color: var(--zen-ink);
  border-bottom: 1px solid var(--zen-border);
  transition: border-color 0.3s;
}

.placeholder-style {
  color: rgba(142, 142, 147, 0.4);
  font-weight: 300;
}

/* 主内容区 */
.main-content {
  padding-bottom: 200rpx;
}

/* 横向滚动 Tab */
.category-scroll {
  width: 100%;
  white-space: nowrap; /* 核心 1：强制 scroll-view 层面不换行 */
  border-bottom: 1px solid rgba(240, 240, 240, 0.6);
}

.tab-list {
  /* 核心 2：坚决去除 display: flex，改用 inline-block */
  padding: 10rpx 40rpx;
  display: inline-block;
  min-width: 100%;
  box-sizing: border-box;
}

.tab-item {
  display: inline-block; /* 核心 3：子元素使用行内块级排列 */
  padding-bottom: 24rpx;
  margin-right: 48rpx;
  border-bottom: 2px solid transparent;
}

.tab-item.active {
  border-bottom: 2px solid var(--zen-ink);
}

.tab-text {
  font-size: 24rpx;
  font-weight: 300;
  letter-spacing: 0.15em;
  color: var(--zen-gray);
}

.tab-item.active .tab-text {
  font-weight: 500;
  color: var(--zen-ink);
}

/* 模块标题 */
.section-title-box {
  padding: 60rpx 40rpx 30rpx;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  letter-spacing: 0.15em;
}

.section-subtitle {
  font-size: 18rpx;
  color: var(--zen-gray);
  letter-spacing: 0.2em;
  font-weight: 300;
}

/* 极简网格 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px; /* 制造极细边框 */
  background-color: rgba(240, 240, 240, 0.6); 
}

.grid-item {
  background-color: var(--zen-bg);
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: background-color 0.3s;
}

.grid-item-hover {
  background-color: #F5F3F0;
}

.icon-wrapper {
  margin-bottom: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ink-wash-icon {
  font-size: 90rpx;
  font-weight: 200;
  color: var(--zen-ink);
  filter: grayscale(1) contrast(1.1);
  opacity: 0.7;
}

.item-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  margin-bottom: 12rpx;
  letter-spacing: 0.05em;
}

.item-subtitle {
  font-size: 18rpx;
  color: var(--zen-gray);
  font-weight: 300;
  letter-spacing: 0.1em;
  margin-bottom: 30rpx;
}

.divider {
  width: 48rpx;
  height: 1px;
  background-color: var(--zen-border);
  margin-bottom: 30rpx;
}

.item-action {
  font-size: 18rpx;
  color: var(--zen-accent);
  letter-spacing: 0.2em;
  font-weight: 300;
}

/* MBTI 灵性探索入口 */
.mbti-section {
  padding: 0 40rpx 60rpx;
}

.mbti-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 44rpx 40rpx;
  background: linear-gradient(135deg, rgba(178, 34, 34, 0.04) 0%, rgba(166, 139, 103, 0.06) 100%);
  border: 1px solid rgba(178, 34, 34, 0.12);
  border-radius: 4rpx;
  position: relative;
  overflow: hidden;
  transition: background 0.3s;
}

.mbti-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4rpx;
  height: 100%;
  background: linear-gradient(180deg, var(--zen-cinnabar) 0%, var(--zen-accent) 100%);
}

.mbti-left {
  flex-shrink: 0;
}

.mbti-icon-wrap {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  border: 1px solid rgba(178, 34, 34, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(178, 34, 34, 0.05);
}

.mbti-icon {
  font-size: 40rpx;
  color: var(--zen-cinnabar);
  line-height: 1;
}

.mbti-body {
  flex: 1;
  min-width: 0;
}

.mbti-tag-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.mbti-tag-line {
  width: 24rpx;
  height: 1px;
  background: var(--zen-accent);
  flex-shrink: 0;
}

.mbti-tag {
  font-size: 18rpx;
  color: var(--zen-accent);
  letter-spacing: 0.2em;
  font-weight: 300;
}

.mbti-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  color: var(--zen-ink);
  letter-spacing: 0.1em;
  margin-bottom: 10rpx;
}

.mbti-desc {
  font-size: 22rpx;
  color: var(--zen-gray);
  letter-spacing: 0.05em;
  font-weight: 300;
  line-height: 1.5;
}

.mbti-arrow {
  flex-shrink: 0;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  border: 1px solid rgba(178, 34, 34, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--zen-cinnabar);
  font-size: 32rpx;
}

/* 底部 Banner */
.banner-section {
  padding: 60rpx 40rpx;
}

.daily-banner {
  position: relative;
  width: 100%;
  height: 260rpx;
  overflow: hidden;
}

.banner-bg-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(178, 58, 52, 0.08) 0%, rgba(212, 175, 55, 0.12) 100%);
  opacity: 0.6;
}

.banner-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 50rpx;
}

.banner-tag {
  font-size: 18rpx;
  color: var(--zen-gray);
  letter-spacing: 0.4em;
  margin-bottom: 16rpx;
}

.banner-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  letter-spacing: 0.15em;
  margin-bottom: 30rpx;
}

.banner-link {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.link-line {
  width: 60rpx;
  height: 1px;
  background-color: var(--zen-ink);
}

.link-text {
  font-size: 18rpx;
  font-weight: 300;
  letter-spacing: 0.15em;
  color: var(--zen-ink);
}
</style>