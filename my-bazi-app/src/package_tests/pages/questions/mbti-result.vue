<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="测算报告" :show-back="true" />

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">

      <!-- ── 顶部装饰背景 ── -->
      <view class="hero-bg">
        <view class="hero-ink-circle hero-ink-circle--1"></view>
        <view class="hero-ink-circle hero-ink-circle--2"></view>
      </view>

      <!-- ── 核心卡片：类型 + 称号 ── -->
      <view class="type-card">
        <text class="type-eyebrow">YOUR PERSONALITY TYPE</text>
        <text class="type-letters">{{ mbtiType }}</text>
        <text class="type-title">{{ info?.title }}</text>
        <view class="type-divider">
          <view class="divider-line"></view>
          <text class="divider-dot">✦</text>
          <view class="divider-line"></view>
        </view>
        <text class="type-desc">{{ info?.desc }}</text>
      </view>

      <!-- ── 完整版专属区域 ── -->
      <view v-if="version === 'full' && details" class="full-section">

        <!-- 维度能量分布 -->
        <view class="section-block">
          <view class="section-header">
            <text class="section-en">DIMENSION DISTRIBUTION</text>
            <text class="section-zh">人格维度能量分布</text>
          </view>

          <!-- EI -->
          <view class="dim-item">
            <view class="dim-labels">
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.EI.percent ?? 0) >= 50 }">E 外向</text>
              <text class="dim-pct">{{ details.EI.percent }}% · {{ 100 - (details.EI.percent ?? 0) }}%</text>
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.EI.percent ?? 0) < 50 }">内向 I</text>
            </view>
            <view class="dim-track">
              <view class="dim-fill dim-fill--left"
                :style="{ width: (details.EI.percent ?? 0) + '%' }"
                :class="{ 'dim-fill--active': (details.EI.percent ?? 0) >= 50 }"
              ></view>
              <view class="dim-fill dim-fill--right"
                :style="{ width: (100 - (details.EI.percent ?? 0)) + '%' }"
                :class="{ 'dim-fill--active': (details.EI.percent ?? 0) < 50 }"
              ></view>
            </view>
            <view class="dim-scores">
              <text class="dim-score-val">{{ details.EI.E }} 票</text>
              <text class="dim-score-sep">vs</text>
              <text class="dim-score-val">{{ details.EI.I }} 票</text>
            </view>
          </view>

          <!-- SN -->
          <view class="dim-item">
            <view class="dim-labels">
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.SN.percent ?? 0) >= 50 }">S 实感</text>
              <text class="dim-pct">{{ details.SN.percent }}% · {{ 100 - (details.SN.percent ?? 0) }}%</text>
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.SN.percent ?? 0) < 50 }">直觉 N</text>
            </view>
            <view class="dim-track">
              <view class="dim-fill dim-fill--left"
                :style="{ width: (details.SN.percent ?? 0) + '%' }"
                :class="{ 'dim-fill--active': (details.SN.percent ?? 0) >= 50 }"
              ></view>
              <view class="dim-fill dim-fill--right"
                :style="{ width: (100 - (details.SN.percent ?? 0)) + '%' }"
                :class="{ 'dim-fill--active': (details.SN.percent ?? 0) < 50 }"
              ></view>
            </view>
            <view class="dim-scores">
              <text class="dim-score-val">{{ details.SN.S }} 票</text>
              <text class="dim-score-sep">vs</text>
              <text class="dim-score-val">{{ details.SN.N }} 票</text>
            </view>
          </view>

          <!-- TF -->
          <view class="dim-item">
            <view class="dim-labels">
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.TF.percent ?? 0) >= 50 }">T 理智</text>
              <text class="dim-pct">{{ details.TF.percent }}% · {{ 100 - (details.TF.percent ?? 0) }}%</text>
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.TF.percent ?? 0) < 50 }">情感 F</text>
            </view>
            <view class="dim-track">
              <view class="dim-fill dim-fill--left"
                :style="{ width: (details.TF.percent ?? 0) + '%' }"
                :class="{ 'dim-fill--active': (details.TF.percent ?? 0) >= 50 }"
              ></view>
              <view class="dim-fill dim-fill--right"
                :style="{ width: (100 - (details.TF.percent ?? 0)) + '%' }"
                :class="{ 'dim-fill--active': (details.TF.percent ?? 0) < 50 }"
              ></view>
            </view>
            <view class="dim-scores">
              <text class="dim-score-val">{{ details.TF.T }} 票</text>
              <text class="dim-score-sep">vs</text>
              <text class="dim-score-val">{{ details.TF.F }} 票</text>
            </view>
          </view>

          <!-- JP -->
          <view class="dim-item">
            <view class="dim-labels">
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.JP.percent ?? 0) >= 50 }">J 判断</text>
              <text class="dim-pct">{{ details.JP.percent }}% · {{ 100 - (details.JP.percent ?? 0) }}%</text>
              <text class="dim-name" :class="{ 'dim-name--dominant': (details.JP.percent ?? 0) < 50 }">感知 P</text>
            </view>
            <view class="dim-track">
              <view class="dim-fill dim-fill--left"
                :style="{ width: (details.JP.percent ?? 0) + '%' }"
                :class="{ 'dim-fill--active': (details.JP.percent ?? 0) >= 50 }"
              ></view>
              <view class="dim-fill dim-fill--right"
                :style="{ width: (100 - (details.JP.percent ?? 0)) + '%' }"
                :class="{ 'dim-fill--active': (details.JP.percent ?? 0) < 50 }"
              ></view>
            </view>
            <view class="dim-scores">
              <text class="dim-score-val">{{ details.JP.J }} 票</text>
              <text class="dim-score-sep">vs</text>
              <text class="dim-score-val">{{ details.JP.P }} 票</text>
            </view>
          </view>
        </view>

        <!-- 深度灵魂剖析 -->
        <view class="section-block">
          <view class="section-header">
            <text class="section-en">DEEP ANALYSIS</text>
            <text class="section-zh">深度灵魂剖析</text>
          </view>
          <view class="analysis-card">
            <text class="analysis-text">{{ info?.deepAnalysis }}</text>
          </view>
        </view>

        <!-- 四维解析网格 -->
        <view class="section-block">
          <view class="section-header">
            <text class="section-en">FOUR DIMENSIONS</text>
            <text class="section-zh">四维人格图谱</text>
          </view>
          <view class="dim4-grid">

            <!-- 核心优势 -->
            <view class="dim4-card dim4-card--strengths">
              <view class="dim4-header">
                <text class="material-symbols-outlined dim4-icon dim4-icon--strengths">auto_awesome</text>
                <text class="dim4-label">核心优势</text>
              </view>
              <text class="dim4-text">{{ info?.strengths }}</text>
            </view>

            <!-- 潜在盲区 -->
            <view class="dim4-card dim4-card--weaknesses">
              <view class="dim4-header">
                <text class="material-symbols-outlined dim4-icon dim4-icon--weaknesses">visibility_off</text>
                <text class="dim4-label">潜在盲区</text>
              </view>
              <text class="dim4-text">{{ info?.weaknesses }}</text>
            </view>

            <!-- 职场偏好 -->
            <view class="dim4-card dim4-card--career">
              <view class="dim4-header">
                <text class="material-symbols-outlined dim4-icon dim4-icon--career">work_outline</text>
                <text class="dim4-label">职场偏好</text>
              </view>
              <text class="dim4-text">{{ info?.career }}</text>
            </view>

            <!-- 亲密关系 -->
            <view class="dim4-card dim4-card--love">
              <view class="dim4-header">
                <text class="material-symbols-outlined dim4-icon dim4-icon--love">favorite_border</text>
                <text class="dim4-label">亲密关系</text>
              </view>
              <text class="dim4-text">{{ info?.love }}</text>
            </view>

          </view>
        </view>

        <!-- 禅意建议 -->
        <view class="section-block">
          <view class="section-header">
            <text class="section-en">ZEN ADVICE</text>
            <text class="section-zh">禅意锦囊</text>
          </view>
          <view class="advice-card">
            <text class="material-symbols-outlined advice-icon">spa</text>
            <text class="advice-text">{{ info?.advice }}</text>
          </view>
        </view>

      </view>

      <!-- ── 隐藏测试钩子（仅 93 题完整版显示）── -->
      <view v-if="version === 'full'" class="hook-card" hover-class="hook-card-hover" @click="goToAdvancedTest">
        <view class="hook-glow"></view>
        <view class="hook-content">
          <view class="hook-header">
            <text class="material-symbols-outlined hook-icon">mystery</text>
            <text class="hook-eyebrow">HIDDEN LAYER</text>
          </view>
          <text class="hook-title">你以为这就结束了？</text>
          <text class="hook-sub">点击测试你的隐藏社交面具与内心剧场，解锁全新 64 型人格。</text>
          <view class="hook-footer">
            <text class="hook-cta">解锁附加测试</text>
            <text class="material-symbols-outlined hook-arrow">arrow_forward</text>
          </view>
        </view>
      </view>

      <!-- ── 底部操作 ── -->
      <view class="action-bar">
        <!-- 保存到相册（预留） -->
        <view class="action-btn action-btn--ghost" hover-class="btn-hover" @click="saveToAlbum">
          <text class="material-symbols-outlined btn-icon">download</text>
          <text class="btn-text">保存报告</text>
        </view>
        <!-- 返回首页 -->
        <view class="action-btn action-btn--primary" hover-class="btn-hover" @click="goHome">
          <text class="material-symbols-outlined btn-icon">home</text>
          <text class="btn-text">返回首页</text>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { mbtiDict } from '../../data/mbtiDict'
import type { MbtiInfo } from '../../data/mbtiDict'

// ── 维度详情结构（与 mbti.vue 中 calculateMBTI 返回值对齐）──
interface DimDetail {
  E?: number; I?: number
  S?: number; N?: number
  T?: number; F?: number
  J?: number; P?: number
  percent: number
}
interface StoredResult {
  type: string
  details: Record<string, DimDetail>
  version: 'short' | 'full' | ''
}

// ── 响应式状态 ──
const mbtiType = ref('')
const version  = ref<'short' | 'full' | ''>('')
const details  = ref<Record<string, DimDetail> | null>(null)
const info     = ref<MbtiInfo | null>(null)

// ── 读取缓存数据 ──
onLoad(() => {
  try {
    const stored = uni.getStorageSync('mbti_result') as StoredResult | null
    if (!stored || !stored.type) {
      uni.showToast({ title: '暂无测试结果', icon: 'none' })
      return
    }
    mbtiType.value = stored.type
    version.value  = stored.version ?? ''
    details.value  = stored.version === 'full' ? stored.details : null
    info.value     = mbtiDict[stored.type] ?? null
  } catch {
    uni.showToast({ title: '数据读取失败', icon: 'none' })
  }
})

// ── 跳转附加测试 ──
const goToAdvancedTest = () => {
  uni.navigateTo({ url: '/package_tests/pages/questions/mbti-advanced' })
}

// ── 保存到相册（预留，后续接入截图 API）──
const saveToAlbum = () => {
  uni.showToast({ title: '保存功能即将上线', icon: 'none', duration: 1500 })
}

// ── 返回首页 ──
const goHome = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style scoped>
/* 页面样式 */

/* ── CSS 变量 ── */
.page-container {
  --zen-bg:       #F9F6F1;
  --zen-ink:      #1A1A1A;
  --zen-gray:     #8E8E93;
  --zen-border:   rgba(212, 175, 55, 0.18);
  --zen-surface:  rgba(255, 255, 255, 0.72);
  --zen-muted:    rgba(51, 51, 51, 0.52);
  --zen-cinnabar: #B23A34;
  --zen-gold:     #D4AF37;
  --zen-accent:   #A68B67;

  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

.scroll-body {
  height: calc(100vh - 140rpx);
}

/* ── 顶部装饰墨圈 ── */
.hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 600rpx;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.hero-ink-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.06;
}

.hero-ink-circle--1 {
  width: 500rpx; height: 500rpx;
  background: var(--zen-cinnabar);
  top: -200rpx; right: -100rpx;
}

.hero-ink-circle--2 {
  width: 360rpx; height: 360rpx;
  background: var(--zen-gold);
  top: 100rpx; left: -120rpx;
}

/* ── 核心卡片 ── */
.type-card {
  position: relative;
  z-index: 1;
  margin: 40rpx 40rpx 0;
  padding: 60rpx 48rpx 52rpx;
  background: var(--zen-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  text-align: center;
}

.type-eyebrow {
  display: block;
  font-size: 18rpx;
  color: var(--zen-gold);
  letter-spacing: 0.4em;
  font-weight: 300;
  margin-bottom: 28rpx;
}

/* 渐变大字 */
.type-letters {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 112rpx;
  font-weight: 700;
  letter-spacing: 0.12em;
  line-height: 1;
  margin-bottom: 20rpx;
  background: linear-gradient(135deg, var(--zen-cinnabar) 0%, #E8704A 50%, var(--zen-gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.type-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 44rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.2em;
  margin-bottom: 40rpx;
}

.type-divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin: 0 20rpx 36rpx;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--zen-border);
}

.divider-dot {
  font-size: 18rpx;
  color: var(--zen-gold);
  opacity: 0.7;
}

.type-desc {
  display: block;
  font-size: 26rpx;
  color: var(--zen-muted);
  line-height: 1.9;
  letter-spacing: 0.05em;
}

/* ── 完整版专属区域 ── */
.full-section {
  padding: 0 40rpx;
  margin-top: 48rpx;
}

/* 通用 section 块 */
.section-block {
  margin-bottom: 48rpx;
}

.section-header {
  margin-bottom: 28rpx;
}

.section-en {
  display: block;
  font-size: 18rpx;
  color: var(--zen-gold);
  letter-spacing: 0.35em;
  font-weight: 300;
  margin-bottom: 8rpx;
}

.section-zh {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.1em;
}

/* ── 维度能量条 ── */
.dim-item {
  margin-bottom: 36rpx;
}

.dim-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.dim-name {
  font-size: 22rpx;
  color: var(--zen-muted);
  letter-spacing: 0.05em;
  min-width: 90rpx;
}

.dim-name--dominant {
  color: var(--zen-cinnabar);
  font-weight: 500;
}

.dim-pct {
  font-size: 20rpx;
  color: var(--zen-gray);
  letter-spacing: 0.05em;
}

/* 进度轨道 */
.dim-track {
  width: 100%;
  height: 6rpx;
  display: flex;
  border-radius: 6rpx;
  overflow: hidden;
  background: rgba(212, 175, 55, 0.1);
  margin-bottom: 10rpx;
}

.dim-fill--left {
  height: 100%;
  border-radius: 6rpx 0 0 6rpx;
  background: rgba(212, 175, 55, 0.2);
  transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

.dim-fill--right {
  height: 100%;
  border-radius: 0 6rpx 6rpx 0;
  background: rgba(212, 175, 55, 0.2);
  transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 优势维度高亮朱砂红 */
.dim-fill--active {
  background: var(--zen-cinnabar) !important;
}

.dim-scores {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dim-score-val {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.05em;
}

.dim-score-sep {
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.35);
  letter-spacing: 0.1em;
}

/* ── 深度解析卡片 ── */
.analysis-card {
  padding: 44rpx 40rpx;
  background: var(--zen-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  position: relative;
}

.analysis-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0;
  width: 4rpx; height: 100%;
  background: linear-gradient(180deg, var(--zen-cinnabar) 0%, var(--zen-gold) 100%);
  border-radius: 4rpx 0 0 4rpx;
}

.analysis-text {
  font-size: 26rpx;
  color: var(--zen-muted);
  line-height: 2;
  letter-spacing: 0.04em;
}

/* ── 四维人格图谱网格 ── */
.dim4-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.dim4-card {
  padding: 36rpx 32rpx;
  background: var(--zen-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  position: relative;
  overflow: hidden;
}

/* 各卡片顶部微光色条 */
.dim4-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3rpx;
}

.dim4-card--strengths::before {
  background: linear-gradient(90deg, var(--zen-gold) 0%, #F0C040 100%);
}

.dim4-card--weaknesses::before {
  background: linear-gradient(90deg, #A68B67 0%, #C4A882 100%);
}

.dim4-card--career::before {
  background: linear-gradient(90deg, var(--zen-cinnabar) 0%, #E8704A 100%);
}

.dim4-card--love::before {
  background: linear-gradient(90deg, #C0392B 0%, #E91E63 100%);
}

.dim4-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.dim4-icon {
  font-size: 36rpx;
  font-weight: 200;
  line-height: 1;
}

.dim4-icon--strengths  { color: var(--zen-gold); }
.dim4-icon--weaknesses { color: var(--zen-accent); }
.dim4-icon--career     { color: var(--zen-cinnabar); }
.dim4-icon--love       { color: #C0392B; }

.dim4-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.08em;
}

.dim4-text {
  font-size: 22rpx;
  color: var(--zen-muted);
  line-height: 1.85;
  letter-spacing: 0.03em;
}

/* ── 禅意建议卡片 ── */
.advice-card {
  padding: 44rpx 40rpx;
  background: linear-gradient(135deg, rgba(178, 58, 52, 0.04) 0%, rgba(212, 175, 55, 0.06) 100%);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 4rpx;
  display: flex;
  gap: 28rpx;
  align-items: flex-start;
}

.advice-icon {
  font-size: 44rpx;
  font-weight: 200;
  color: var(--zen-gold);
  flex-shrink: 0;
  margin-top: 4rpx;
}

.advice-text {
  flex: 1;
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: var(--zen-ink);
  line-height: 2;
  letter-spacing: 0.06em;
}

/* ── 隐藏测试钩子卡片 ── */
.hook-card {
  margin: 48rpx 40rpx 0;
  padding: 48rpx 44rpx;
  background: rgba(20, 10, 10, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 4rpx;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(178, 58, 52, 0.4);
  animation: hookPulse 3s ease-in-out infinite;
}

@keyframes hookPulse {
  0%, 100% { border-color: rgba(178, 58, 52, 0.35); box-shadow: 0 0 0 0 rgba(178, 58, 52, 0); }
  50%       { border-color: rgba(212, 175, 55, 0.6); box-shadow: 0 0 24rpx 4rpx rgba(178, 58, 52, 0.15); }
}

/* 背景微光晕 */
.hook-glow {
  position: absolute;
  top: -60rpx; right: -60rpx;
  width: 300rpx; height: 300rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(178, 58, 52, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.hook-card-hover {
  opacity: 0.82;
}

.hook-content {
  position: relative;
  z-index: 1;
}

.hook-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.hook-icon {
  font-size: 36rpx;
  font-weight: 200;
  color: var(--zen-gold);
}

.hook-eyebrow {
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.6);
  letter-spacing: 0.4em;
  font-weight: 300;
}

.hook-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 38rpx;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 20rpx;
  background: linear-gradient(135deg, #E8704A 0%, var(--zen-gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hook-sub {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.8;
  letter-spacing: 0.04em;
  margin-bottom: 36rpx;
}

.hook-footer {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.hook-cta {
  font-size: 24rpx;
  color: var(--zen-gold);
  letter-spacing: 0.15em;
  font-weight: 500;
}

.hook-arrow {
  font-size: 28rpx;
  font-weight: 200;
  color: var(--zen-gold);
}

/* ── 底部操作栏 ── */
.action-bar {
  display: flex;
  gap: 24rpx;
  padding: 48rpx 40rpx 0;
}

.action-btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border-radius: 4rpx;
  transition: opacity 0.2s;
}

.action-btn--ghost {
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
}

.action-btn--primary {
  background: var(--zen-cinnabar);
  border: none;
}

.btn-hover {
  opacity: 0.72;
}

.btn-icon {
  font-size: 32rpx;
  font-weight: 200;
}

.action-btn--ghost .btn-icon { color: var(--zen-accent); }
.action-btn--primary .btn-icon { color: rgba(255,255,255,0.85); }

.btn-text {
  font-size: 26rpx;
  letter-spacing: 0.12em;
  font-weight: 300;
}

.action-btn--ghost .btn-text { color: var(--zen-ink); }
.action-btn--primary .btn-text { color: #fff; }

.safe-bottom {
  height: 120rpx;
}
</style>
