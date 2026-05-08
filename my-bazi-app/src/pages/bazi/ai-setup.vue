<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="AI 八字精批" :show-back="true" />

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">

      <!-- ── 顶部仪式感标题区 ── -->
      <view class="hero-section">
        <view class="hero-glow"></view>
        <view class="hero-badge">
          <text class="hero-badge-text">DeepSeek · 禅师解命</text>
        </view>
        <text class="hero-title">命局深度精批</text>
        <text class="hero-desc">输入生辰，观看短视频，解锁专属于你的命理深度解析</text>
        <!-- 功能亮点 -->
        <view class="feature-row">
          <view class="feature-item">
            <text class="feature-icon">☯</text>
            <text class="feature-label">格局总述</text>
          </view>
          <view class="feature-divider"></view>
          <view class="feature-item">
            <text class="feature-icon">運</text>
            <text class="feature-label">大运流年</text>
          </view>
          <view class="feature-divider"></view>
          <view class="feature-item">
            <text class="feature-icon">緣</text>
            <text class="feature-label">姻缘情感</text>
          </view>
          <view class="feature-divider"></view>
          <view class="feature-item">
            <text class="feature-icon">悟</text>
            <text class="feature-label">禅意寄语</text>
          </view>
        </view>
      </view>

      <!-- ── 表单区 ── -->
      <view class="form-section">

        <!-- 姓名 -->
        <view class="form-item">
          <text class="form-label">
            <text class="label-icon">✦</text>
            姓名
          </text>
          <view class="input-wrap">
            <input
              class="form-input"
              v-model="form.name"
              placeholder="请输入姓名（可匿名）"
              placeholder-class="input-placeholder"
              maxlength="10"
            />
          </view>
        </view>

        <!-- 性别 -->
        <view class="form-item">
          <text class="form-label">
            <text class="label-icon">✦</text>
            性别
          </text>
          <view class="radio-group">
            <view
              class="radio-item"
              :class="{ 'radio-item--active': form.gender === 1 }"
              @tap="form.gender = 1"
            >
              <text class="radio-text">乾 · 男</text>
            </view>
            <view
              class="radio-item"
              :class="{ 'radio-item--active': form.gender === 0 }"
              @tap="form.gender = 0"
            >
              <text class="radio-text">坤 · 女</text>
            </view>
          </view>
        </view>

        <!-- 出生日期 -->
        <view class="form-item">
          <view class="label-row">
            <text class="form-label">
              <text class="label-icon">✦</text>
              出生日期
            </text>
            <!-- 公历/农历切换 -->
            <view class="calendar-toggle">
              <view
                class="toggle-option"
                :class="{ 'toggle-active': !form.isLunar }"
                @tap="form.isLunar = false"
              >
                <text class="toggle-text">公历</text>
              </view>
              <view
                class="toggle-option"
                :class="{ 'toggle-active': form.isLunar }"
                @tap="form.isLunar = true"
              >
                <text class="toggle-text">农历</text>
              </view>
            </view>
          </view>
          <picker mode="date" :value="form.birthDate" @change="onDateChange">
            <view class="picker-display">
              <text class="picker-text">{{ form.birthDate }}</text>
              <text class="material-symbols-outlined picker-icon">calendar_today</text>
            </view>
          </picker>
        </view>

        <!-- 出生时间 -->
        <view class="form-item">
          <text class="form-label">
            <text class="label-icon">✦</text>
            出生时间
          </text>
          <picker mode="time" :value="form.birthTime" @change="onTimeChange">
            <view class="picker-display">
              <text
                class="picker-text"
                :class="{ 'picker-text--placeholder': !form.birthTime }"
              >
                {{ form.birthTime || '请选择时间' }}
              </text>
              <text class="material-symbols-outlined picker-icon">schedule</text>
            </view>
          </picker>
        </view>

      </view>

      <!-- ── 解锁按钮 ── -->
      <view class="unlock-section">
        <!-- 说明文字 -->
        <view class="unlock-hint-row">
          <view class="hint-line"></view>
          <text class="unlock-hint">观看完整视频即可解锁</text>
          <view class="hint-line"></view>
        </view>

        <!-- 主按钮 -->
        <view
          class="unlock-btn"
          hover-class="unlock-btn--hover"
          @tap="handleUnlock"
        >
          <view class="unlock-btn-inner">
            <text class="unlock-btn-icon">🎬</text>
            <view class="unlock-btn-text-wrap">
              <text class="unlock-btn-title">观看 30s 视频，解锁深度精批</text>
              <text class="unlock-btn-sub">WATCH AD · UNLOCK AI ANALYSIS</text>
            </view>
            <text class="material-symbols-outlined unlock-btn-arrow">arrow_forward</text>
          </view>
          <!-- 按钮底部光晕 -->
          <view class="unlock-btn-glow"></view>
        </view>

        <text class="privacy-note">生辰数据仅用于本次命理推演，不会上传或存储</text>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 隐藏原生 TabBar
onMounted(() => {
  uni.hideTabBar({ animation: false })
})

// ── 表单状态 ──────────────────────────────────────────────────────────────────
const form = reactive({
  name:      '',
  gender:    1 as 0 | 1,
  birthDate: '2000-01-01',
  birthTime: '12:00',
  isLunar:   false,
})

const onDateChange = (e: any) => { form.birthDate = e.detail.value }
const onTimeChange = (e: any) => { form.birthTime = e.detail.value }

// ── 表单校验 ──────────────────────────────────────────────────────────────────
function validate(): boolean {
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入姓名', icon: 'none', duration: 1500 })
    return false
  }
  if (!form.birthDate) {
    uni.showToast({ title: '请选择出生日期', icon: 'none', duration: 1500 })
    return false
  }
  if (!form.birthTime) {
    uni.showToast({ title: '请选择出生时间', icon: 'none', duration: 1500 })
    return false
  }
  return true
}

// ── 广告看完后的核心逻辑 ──────────────────────────────────────────────────────
async function onAdFinished() {
  uni.showLoading({ title: '禅师正在为您解惑...', mask: true })

  try {
    // 1. 先排盘（写入 currentBaziData）
    const [year, month, day] = form.birthDate.split('-').map(Number)
    const [hour, minute]     = form.birthTime.split(':').map(Number)

    await baziStore.calculateByData({
      name:             form.name.trim() || '命主',
      gender:           form.gender,
      birth_year:       year,
      birth_month:      month,
      birth_day:        day,
      birth_hour:       hour,
      birth_minute:     minute,
      is_lunar:         form.isLunar,
      is_deep_analysis: false,
    })

    // 2. 调用 AI 精批（写入 aiAnalysisData）
    await baziStore.fetchAiAnalysis()

    uni.hideLoading()

    // 3. 跳转结果页
    uni.navigateTo({ url: '/pages/result/result' })

  } catch (err: any) {
    uni.hideLoading()
    console.error('❌ [ai-setup] 精批失败:', err)
    uni.showToast({
      title: err?.message || '解析失败，请稍后重试',
      icon: 'none',
      duration: 2500,
    })
  }
}

// ── 广告入口：区分 H5 / 小程序 ───────────────────────────────────────────────
function handleUnlock() {
  if (!validate()) return

  // ── H5 / 开发环境：弹模拟框 ──
  // #ifdef H5
  uni.showModal({
    title: '🎬 模拟广告',
    content: '[测试环境] 模拟观看了一段 30 秒的广告，是否看完？',
    confirmText: '已看完，解锁',
    cancelText: '取消',
    success: (res) => { if (res.confirm) onAdFinished() },
  })
  return
  // #endif

  // ── 小程序：真实激励视频广告 ──
  // #ifndef H5
  let rewardedAd: UniApp.RewardedVideoAdContext | null = null

  try {
    rewardedAd = uni.createRewardedVideoAd({ adUnitId: 'adunit-xxxxx' })
  } catch {
    // 开发者工具不支持广告，降级为模拟框
    uni.showModal({
      title: '🎬 模拟广告',
      content: '[当前环境不支持广告] 模拟观看了一段 30 秒的广告，是否看完？',
      confirmText: '已看完，解锁',
      cancelText: '取消',
      success: (res) => { if (res.confirm) onAdFinished() },
    })
    return
  }

  rewardedAd.onClose((res: { isEnded: boolean }) => {
    if (res.isEnded) {
      onAdFinished()
    } else {
      uni.showToast({ title: '请看完广告后再解锁', icon: 'none', duration: 1500 })
    }
  })

  rewardedAd.onError((err: any) => {
    console.error('[ai-setup] 广告加载失败:', err)
    uni.showToast({ title: '广告加载失败，请稍后重试', icon: 'none', duration: 1500 })
  })

  rewardedAd.show().catch(() => {
    uni.showToast({ title: '广告暂时不可用，请稍后重试', icon: 'none', duration: 1500 })
  })
  // #endif
}
</script>

<style scoped>
/* 页面样式 */

/* ── 页面容器 ── */
.page-container {
  --zen-bg:       #F9F6F1;
  --zen-ink:      #1A1A1A;
  --zen-gray:     #8E8E93;
  --zen-border:   rgba(212, 175, 55, 0.15);
  --zen-surface:  rgba(255, 255, 255, 0.72);
  --zen-muted:    rgba(51, 51, 51, 0.5);
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

/* ── 顶部仪式感区 ── */
.hero-section {
  position: relative;
  padding: 52rpx 48rpx 48rpx;
  text-align: center;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  top: -80rpx; left: 50%;
  transform: translateX(-50%);
  width: 500rpx; height: 500rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 28rpx;
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 40rpx;
  background: rgba(212, 175, 55, 0.06);
  margin-bottom: 28rpx;
}

.hero-badge-text {
  font-size: 20rpx;
  color: var(--zen-gold);
  letter-spacing: 0.25em;
  font-weight: 300;
}

.hero-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 52rpx;
  font-weight: 600;
  color: var(--zen-ink);
  letter-spacing: 0.15em;
  margin-bottom: 20rpx;
}

.hero-desc {
  display: block;
  font-size: 24rpx;
  color: var(--zen-muted);
  line-height: 1.8;
  letter-spacing: 0.04em;
  margin-bottom: 44rpx;
}

/* 功能亮点行 */
.feature-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 0 28rpx;
}

.feature-icon {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: var(--zen-gold);
  line-height: 1;
}

.feature-label {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.1em;
}

.feature-divider {
  width: 1px;
  height: 48rpx;
  background: rgba(212, 175, 55, 0.2);
  flex-shrink: 0;
}

/* ── 表单区 ── */
.form-section {
  margin: 0 40rpx;
  padding: 44rpx 44rpx 8rpx;
  background: var(--zen-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  position: relative;
}

/* 表单顶部金色微光条 */
.form-section::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(212, 175, 55, 0.4) 50%, transparent 100%);
}

.form-item {
  margin-bottom: 44rpx;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.1em;
  margin-bottom: 20rpx;
}

.label-icon {
  font-size: 18rpx;
  color: var(--zen-gold);
  line-height: 1;
}

/* 姓名输入框 */
.input-wrap {
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(212, 175, 55, 0.12);
  border-radius: 12rpx;
  padding: 0 28rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
}

.form-input {
  flex: 1;
  height: 100%;
  font-size: 30rpx;
  color: var(--zen-ink);
  background: transparent;
  border: none;
  letter-spacing: 0.05em;
}

.input-placeholder {
  color: rgba(142, 142, 147, 0.4);
  font-weight: 300;
  font-size: 28rpx;
}

/* 性别单选 */
.radio-group {
  display: flex;
  gap: 20rpx;
}

.radio-item {
  flex: 1;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(212, 175, 55, 0.12);
  border-radius: 12rpx;
  transition: all 0.25s;
}

.radio-item--active {
  background: var(--zen-cinnabar);
  border-color: var(--zen-cinnabar);
}

.radio-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: var(--zen-gray);
  letter-spacing: 0.1em;
}

.radio-item--active .radio-text {
  color: #fff;
  font-weight: 500;
}

/* 日期标签行 */
.label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.label-row .form-label {
  margin-bottom: 0;
}

/* 公历/农历切换 */
.calendar-toggle {
  display: flex;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 32rpx;
  padding: 4rpx;
}

.toggle-option {
  padding: 8rpx 24rpx;
  border-radius: 28rpx;
  transition: all 0.2s;
}

.toggle-active {
  background: var(--zen-cinnabar);
}

.toggle-text {
  font-size: 22rpx;
  color: rgba(142, 142, 147, 0.8);
  letter-spacing: 0.05em;
}

.toggle-active .toggle-text {
  color: #fff;
  font-weight: 500;
}

/* 选择器 */
.picker-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 28rpx;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(212, 175, 55, 0.12);
  border-radius: 12rpx;
}

.picker-text {
  font-size: 30rpx;
  color: var(--zen-ink);
  letter-spacing: 0.03em;
}

.picker-text--placeholder {
  color: rgba(142, 142, 147, 0.4);
  font-weight: 300;
  font-size: 28rpx;
}

.picker-icon {
  font-size: 36rpx;
  color: var(--zen-gray);
  font-weight: 200;
}

/* ── 解锁按钮区 ── */
.unlock-section {
  padding: 48rpx 40rpx 0;
}

.unlock-hint-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.hint-line {
  flex: 1;
  height: 1px;
  background: rgba(212, 175, 55, 0.2);
}

.unlock-hint {
  font-size: 20rpx;
  color: rgba(212, 175, 55, 0.6);
  letter-spacing: 0.2em;
  font-weight: 300;
  white-space: nowrap;
}

/* 主解锁按钮 */
.unlock-btn {
  position: relative;
  border-radius: 16rpx;
  overflow: hidden;
  background: linear-gradient(135deg, #1A0A0A 0%, #2D1010 50%, #1A0A0A 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  box-shadow:
    0 8rpx 40rpx rgba(178, 58, 52, 0.25),
    0 0 0 1px rgba(212, 175, 55, 0.08);
  animation: btnPulse 3s ease-in-out infinite;
}

@keyframes btnPulse {
  0%, 100% { box-shadow: 0 8rpx 40rpx rgba(178, 58, 52, 0.25), 0 0 0 1px rgba(212, 175, 55, 0.08); }
  50%       { box-shadow: 0 12rpx 56rpx rgba(178, 58, 52, 0.4), 0 0 0 1px rgba(212, 175, 55, 0.25); }
}

.unlock-btn--hover {
  opacity: 0.82;
  transform: scale(0.985);
}

.unlock-btn-inner {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 36rpx 40rpx;
  position: relative;
  z-index: 1;
}

.unlock-btn-icon {
  font-size: 52rpx;
  line-height: 1;
  flex-shrink: 0;
}

.unlock-btn-text-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.unlock-btn-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.06em;
  line-height: 1.4;
}

.unlock-btn-sub {
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.6);
  letter-spacing: 0.2em;
  font-weight: 300;
}

.unlock-btn-arrow {
  font-size: 36rpx;
  font-weight: 200;
  color: rgba(212, 175, 55, 0.7);
  flex-shrink: 0;
}

/* 按钮底部光晕 */
.unlock-btn-glow {
  position: absolute;
  bottom: -20rpx; left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 40rpx;
  background: radial-gradient(ellipse, rgba(178, 58, 52, 0.35) 0%, transparent 70%);
  pointer-events: none;
}

/* 隐私说明 */
.privacy-note {
  display: block;
  text-align: center;
  font-size: 20rpx;
  color: rgba(142, 142, 147, 0.5);
  letter-spacing: 0.05em;
  margin-top: 24rpx;
}

.safe-bottom {
  height: 120rpx;
}
</style>
