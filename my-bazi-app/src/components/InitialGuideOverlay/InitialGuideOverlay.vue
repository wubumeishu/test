<template>
  <view
    class="overlay-root"
    :class="{ 'overlay-visible': visible, 'overlay-hidden': !visible }"
  >
    <!-- 半透明背景蒙层（不遮 TabBar，bottom 留出 TabBar 高度） -->
    <view class="paper-bg"></view>

    <!-- 内容区 -->
    <view class="overlay-content">

      <!-- 右上角关闭按钮 -->
      <view class="close-btn" @click="handleDismiss">
        <text class="material-symbols-outlined close-icon">close</text>
        <text class="close-text">稍后再说</text>
      </view>

      <!-- 太极星盘动效 -->
      <view class="taiji-wrapper">
        <view class="taiji-halo"></view>
        <view class="taiji-ring-outer"></view>
        <view class="taiji-ring-inner"></view>
        <view class="taiji-core">
          <text class="taiji-symbol">☯</text>
        </view>
      </view>

      <!-- 书法文案 -->
      <view class="copy-block">
        <text class="copy-main brush-font">万物皆有定数</text>
        <text class="copy-main brush-font">此刻即是机缘</text>
        <view class="copy-divider"></view>
        <text class="copy-sub">录入生辰，开启你的本命觉醒</text>
      </view>

      <!-- 呼吸灯按钮 -->
      <view class="cta-wrapper">
        <view
          class="cta-btn"
          hover-class="cta-btn-hover"
          @click="handleStart"
        >
          <text class="material-symbols-outlined cta-icon">auto_awesome</text>
          <text class="cta-text">开启起卦之旅</text>
        </view>
        <view class="breath-ring breath-ring-1"></view>
        <view class="breath-ring breath-ring-2"></view>
      </view>

    </view>
  </view>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'start'): void
  (e: 'dismiss'): void
}>()

function handleStart() {
  emit('start')
}

function handleDismiss() {
  emit('dismiss')
}
</script>

<style scoped>
/* ── 根容器：覆盖页面内容区，底部留出 TabBar 空间 ── */
.overlay-root {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  /* 留出 TabBar 高度（约 100rpx + 安全区），不遮住底部导航 */
  bottom: 100rpx;
  z-index: 99;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.6s ease, visibility 0.6s ease;
}

.overlay-visible {
  opacity: 1;
  visibility: visible;
}

.overlay-hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

/* ── 宣纸纹理背景 ── */
.paper-bg {
  position: absolute;
  inset: 0;
  background-color: #F9F6F1;
  background-image: url("/static/handmade-paper.png");
  background-size: cover;
}

/* ── 内容区 ── */
.overlay-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 60rpx;
  width: 100%;
}

/* ── 关闭按钮 ── */
.close-btn {
  position: absolute;
  top: -60rpx;
  right: 40rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 20rpx;
  opacity: 0.45;
}

.close-icon {
  font-size: 28rpx;
  color: #333;
}

.close-text {
  font-size: 22rpx;
  color: #333;
  letter-spacing: 0.05em;
}

/* ── 太极星盘 ── */
.taiji-wrapper {
  position: relative;
  width: 240rpx;
  height: 240rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 60rpx;
}

.taiji-halo {
  position: absolute;
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(178, 58, 52, 0.08) 0%, transparent 70%);
  animation: halo-pulse 3s ease-in-out infinite;
}

@keyframes halo-pulse {
  0%, 100% { transform: scale(1);   opacity: 0.6; }
  50%       { transform: scale(1.2); opacity: 1;   }
}

.taiji-ring-outer {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  border: 1.5rpx solid rgba(212, 175, 55, 0.35);
  border-top-color: rgba(178, 58, 52, 0.6);
  animation: spin-cw 8s linear infinite;
}

.taiji-ring-inner {
  position: absolute;
  width: 150rpx;
  height: 150rpx;
  border-radius: 50%;
  border: 1rpx solid rgba(178, 58, 52, 0.2);
  border-bottom-color: rgba(212, 175, 55, 0.5);
  animation: spin-ccw 5s linear infinite;
}

@keyframes spin-cw  { to { transform: rotate(360deg);  } }
@keyframes spin-ccw { to { transform: rotate(-360deg); } }

.taiji-core {
  position: relative;
  z-index: 2;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0);     }
  50%       { transform: translateY(-8rpx); }
}

.taiji-symbol {
  font-size: 88rpx;
  color: #B23A34;
  opacity: 0.85;
  line-height: 1;
}

/* ── 书法文案 ── */
.copy-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 64rpx;
}

.brush-font {
  font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif;
}

.copy-main {
  display: block;
  font-size: 44rpx;
  font-weight: 400;
  color: #1A1A1A;
  letter-spacing: 0.25em;
  line-height: 1.6;
  text-align: center;
}

.copy-divider {
  width: 60rpx;
  height: 1rpx;
  background: rgba(212, 175, 55, 0.5);
  margin: 24rpx auto;
}

.copy-sub {
  font-size: 26rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.12em;
  text-align: center;
  line-height: 1.8;
}

/* ── 呼吸灯按钮 ── */
.cta-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.breath-ring {
  position: absolute;
  border-radius: 60rpx;
  border: 1.5rpx solid rgba(178, 58, 52, 0.4);
  pointer-events: none;
}

.breath-ring-1 {
  width: calc(100% + 24rpx);
  height: calc(100% + 24rpx);
  animation: breath 2.4s ease-out infinite;
}

.breath-ring-2 {
  width: calc(100% + 48rpx);
  height: calc(100% + 48rpx);
  animation: breath 2.4s ease-out 0.8s infinite;
}

@keyframes breath {
  0%   { opacity: 0.8; transform: scale(0.95); }
  100% { opacity: 0;   transform: scale(1.15); }
}

.cta-btn {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 28rpx 72rpx;
  background: linear-gradient(135deg, #B23A34 0%, #8B2E29 100%);
  border-radius: 60rpx;
  box-shadow: 0 12rpx 32rpx rgba(178, 58, 52, 0.35);
}

.cta-btn-hover {
  opacity: 0.88;
}

.cta-icon {
  font-size: 40rpx;
  color: rgba(255, 255, 255, 0.9);
}

.cta-text {
  font-size: 32rpx;
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 0.15em;
}
</style>

<style scoped>
/* ── 根容器：绝对定位覆盖整个页面 ── */
.overlay-root {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.6s ease, visibility 0.6s ease;
}

.overlay-visible {
  opacity: 1;
  visibility: visible;
}

.overlay-hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

/* ── 宣纸纹理背景 ── */
.paper-bg {
  position: absolute;
  inset: 0;
  background-color: #F9F6F1;
  background-image: url("/static/handmade-paper.png");
  background-size: cover;
}

/* ── 内容区 ── */
.overlay-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 60rpx;
  width: 100%;
}

/* ── 太极星盘 ── */
.taiji-wrapper {
  position: relative;
  width: 280rpx;
  height: 280rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 80rpx;
}

/* 外圈光晕（脉冲） */
.taiji-halo {
  position: absolute;
  width: 280rpx;
  height: 280rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(178, 58, 52, 0.08) 0%, transparent 70%);
  animation: halo-pulse 3s ease-in-out infinite;
}

@keyframes halo-pulse {
  0%, 100% { transform: scale(1);   opacity: 0.6; }
  50%       { transform: scale(1.2); opacity: 1;   }
}

/* 外旋转环 */
.taiji-ring-outer {
  position: absolute;
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  border: 1.5rpx solid rgba(212, 175, 55, 0.35);
  border-top-color: rgba(178, 58, 52, 0.6);
  animation: spin-cw 8s linear infinite;
}

/* 内反转环 */
.taiji-ring-inner {
  position: absolute;
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  border: 1rpx solid rgba(178, 58, 52, 0.2);
  border-bottom-color: rgba(212, 175, 55, 0.5);
  animation: spin-ccw 5s linear infinite;
}

@keyframes spin-cw {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

@keyframes spin-ccw {
  from { transform: rotate(0deg); }
  to   { transform: rotate(-360deg); }
}

/* 太极核心 */
.taiji-core {
  position: relative;
  z-index: 2;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0);     }
  50%       { transform: translateY(-8rpx); }
}

.taiji-symbol {
  font-size: 100rpx;
  color: #B23A34;
  opacity: 0.85;
  line-height: 1;
}

/* ── 书法文案 ── */
.copy-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.brush-font {
  font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif;
}

.copy-main {
  display: block;
  font-size: 48rpx;
  font-weight: 400;
  color: #1A1A1A;
  letter-spacing: 0.25em;
  line-height: 1.6;
  text-align: center;
}

.copy-divider {
  width: 60rpx;
  height: 1rpx;
  background: rgba(212, 175, 55, 0.5);
  margin: 28rpx auto;
}

.copy-sub {
  font-size: 26rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.12em;
  text-align: center;
  line-height: 1.8;
}

/* ── 呼吸灯按钮 ── */
.cta-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
}

/* 呼吸光圈 */
.breath-ring {
  position: absolute;
  border-radius: 60rpx;
  border: 1.5rpx solid rgba(178, 58, 52, 0.4);
  pointer-events: none;
}

.breath-ring-1 {
  width: calc(100% + 24rpx);
  height: calc(100% + 24rpx);
  animation: breath 2.4s ease-out infinite;
}

.breath-ring-2 {
  width: calc(100% + 48rpx);
  height: calc(100% + 48rpx);
  animation: breath 2.4s ease-out 0.8s infinite;
}

@keyframes breath {
  0%   { opacity: 0.8; transform: scale(0.95); }
  100% { opacity: 0;   transform: scale(1.15); }
}

.cta-btn {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 28rpx 72rpx;
  background: linear-gradient(135deg, #B23A34 0%, #8B2E29 100%);
  border-radius: 60rpx;
  box-shadow: 0 12rpx 32rpx rgba(178, 58, 52, 0.35);
}

.cta-btn-hover {
  opacity: 0.88;
  transform: scale(0.98);
}

.cta-icon {
  font-size: 40rpx;
  color: rgba(255, 255, 255, 0.9);
}

.cta-text {
  font-size: 32rpx;
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 0.15em;
}

/* ── 底部提示 ── */
.footer-hint {
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.35);
  letter-spacing: 0.08em;
}
</style>
