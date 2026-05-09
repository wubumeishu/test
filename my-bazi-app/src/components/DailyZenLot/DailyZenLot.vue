<template>
  <view class="zen-lot-card">
    <!-- 标题行 -->
    <view class="lot-header">
      <view class="lot-line"></view>
      <text class="lot-title">今日机缘</text>
      <view class="lot-line"></view>
    </view>

    <!-- 未抽签：抽签按钮 -->
    <view v-if="!drawn" class="lot-action">
      <text class="lot-hint">静心一刻，感受今日天机</text>
      <view class="draw-btn-wrapper">
        <view class="draw-btn" hover-class="draw-btn-hover" @click="handleDraw">
          <text class="material-symbols-outlined draw-icon">casino</text>
          <text class="draw-text">点击抽签</text>
        </view>
        <view class="draw-ring draw-ring-1"></view>
        <view class="draw-ring draw-ring-2"></view>
      </view>
    </view>

    <!-- 已抽签：签文展示（淡入动画） -->
    <view v-else class="lot-result" :class="{ 'lot-result-in': resultVisible }">
      <text class="lot-number">第 {{ lotNumber }} 签</text>
      <text class="lot-text brush-font">{{ currentLot.content }}</text>
      <text class="lot-sub">{{ currentLot.sub || currentLot.author }}</text>
      <view class="lot-divider"></view>
      <text class="lot-cta-hint">若想开启深度命盘解析，请录入生辰</text>
      <view class="lot-cta-btn" hover-class="lot-cta-btn-hover" @click="handleGoCreate">
        <text class="lot-cta-text">建立我的命盘</text>
        <text class="material-symbols-outlined lot-cta-arrow">arrow_forward</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const emit = defineEmits<{ (e: 'goCreate'): void }>()

interface ZenData {
  id: number
  content: string
  author?: string
  date: string
}

// ── 本地兜底数据（网络失败时使用）────────────────────────────────────────────
const FALLBACK_LOTS = [
  { id: 1,  content: '云无心以出岫，鸟倦飞而知还。',         sub: '顺势而为，不必强求，归处即是安处。' },
  { id: 2,  content: '此心安处是吾乡。',                     sub: '内心平静，无论身在何处，皆是故乡。' },
  { id: 3,  content: '竹密不妨流水过，山高岂碍白云飞。',     sub: '障碍只是表象，心若通透，万物皆可穿越。' },
  { id: 4,  content: '行到水穷处，坐看云起时。',             sub: '绝境之后，往往是新的开始。静待，便是智慧。' },
  { id: 5,  content: '随缘自适，烦恼即菩提。',               sub: '接纳当下的一切，烦恼与智慧本是一体。' },
  { id: 6,  content: '若无闲事挂心头，便是人间好时节。',     sub: '清空杂念，当下便是天堂。' },
  { id: 7,  content: '上善若水，水善利万物而不争。',         sub: '柔弱胜刚强，以柔克刚是今日的智慧。' },
]

const drawn         = ref(false)
const resultVisible = ref(false)
const lotNumber     = ref(1)
const currentLot    = ref({ content: '', sub: '', author: '' })

onMounted(async () => {
  try {
    const res = await get<ZenData>('/api/zen/daily')
    lotNumber.value  = res.id
    currentLot.value = {
      content: res.content,
      sub:     '',          // 后端暂无 sub，留空或后续扩展
      author:  res.author || '',
    }
  } catch {
    // 网络失败：用本地兜底，基于今日日期选一条
    const today = new Date().toISOString().split('T')[0]
    let seed = 0
    for (let i = 0; i < today.length; i++) {
      seed = ((seed << 5) - seed) + today.charCodeAt(i)
      seed |= 0
    }
    const item = FALLBACK_LOTS[Math.abs(seed) % FALLBACK_LOTS.length]
    lotNumber.value  = item.id
    currentLot.value = { content: item.content, sub: item.sub, author: '' }
  }
})

function handleDraw() {
  drawn.value = true
  setTimeout(() => { resultVisible.value = true }, 30)
}

function handleGoCreate() {
  emit('goCreate')
}
</script>

<style scoped>
.zen-lot-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(16px);
  border: 0.5px solid rgba(212, 175, 55, 0.2);
  border-radius: 24rpx;
  padding: 48rpx 40rpx 44rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.04);
}

/* ── 标题 ── */
.lot-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.lot-line {
  flex: 1;
  height: 1rpx;
  background: rgba(212, 175, 55, 0.3);
}

.lot-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.3em;
  white-space: nowrap;
}

/* ── 未抽签 ── */
.lot-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 36rpx;
}

.lot-hint {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.45);
  letter-spacing: 0.1em;
}

.draw-btn-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.draw-ring {
  position: absolute;
  border-radius: 48rpx;
  border: 1.5rpx solid rgba(178, 58, 52, 0.3);
  pointer-events: none;
}

.draw-ring-1 {
  width: calc(100% + 20rpx);
  height: calc(100% + 20rpx);
  animation: ring-breath 2.2s ease-out infinite;
}

.draw-ring-2 {
  width: calc(100% + 40rpx);
  height: calc(100% + 40rpx);
  animation: ring-breath 2.2s ease-out 0.7s infinite;
}

@keyframes ring-breath {
  0%   { opacity: 0.7; transform: scale(0.96); }
  100% { opacity: 0;   transform: scale(1.12); }
}

.draw-btn {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 22rpx 56rpx;
  background: linear-gradient(135deg, rgba(178, 58, 52, 0.9) 0%, rgba(139, 46, 41, 0.9) 100%);
  border-radius: 48rpx;
  box-shadow: 0 8rpx 24rpx rgba(178, 58, 52, 0.25);
}

.draw-btn-hover {
  opacity: 0.85;
}

.draw-icon {
  font-size: 36rpx;
  color: rgba(255, 255, 255, 0.9);
}

.draw-text {
  font-size: 30rpx;
  color: #fff;
  letter-spacing: 0.15em;
}

/* ── 签文结果 ── */
.lot-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0;
  transform: translateY(12rpx);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.lot-result-in {
  opacity: 1;
  transform: translateY(0);
}

.lot-number {
  font-size: 20rpx;
  color: rgba(178, 58, 52, 0.5);
  letter-spacing: 0.2em;
  margin-bottom: 24rpx;
}

.brush-font {
  font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif;
}

.lot-text {
  font-size: 40rpx;
  color: #1A1A1A;
  letter-spacing: 0.2em;
  text-align: center;
  line-height: 1.7;
  margin-bottom: 16rpx;
}

.lot-sub {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.55);
  text-align: center;
  line-height: 1.8;
  letter-spacing: 0.05em;
  padding: 0 20rpx;
}

.lot-divider {
  width: 48rpx;
  height: 1rpx;
  background: rgba(212, 175, 55, 0.4);
  margin: 32rpx auto;
}

.lot-cta-hint {
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.4);
  letter-spacing: 0.05em;
  text-align: center;
  margin-bottom: 24rpx;
}

.lot-cta-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 36rpx;
  border: 1rpx solid rgba(178, 58, 52, 0.3);
  border-radius: 40rpx;
  background: rgba(178, 58, 52, 0.04);
}

.lot-cta-btn-hover {
  background: rgba(178, 58, 52, 0.08);
}

.lot-cta-text {
  font-size: 26rpx;
  color: #B23A34;
  letter-spacing: 0.1em;
}

.lot-cta-arrow {
  font-size: 28rpx;
  color: #B23A34;
}
</style>
