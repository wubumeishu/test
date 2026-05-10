<template>
  <view class="zen-lot-card">

    <!-- 未抽签：签筒 + 按钮 -->
    <view v-if="!drawn" class="lot-action">
      <text class="lot-hint">静心一刻，感受今日天机</text>
      <view class="qian-tong" :class="{ shaking: isShaking }">
        <text class="qian-tong-icon">🪬</text>
      </view>
      <view class="draw-btn-wrapper">
        <view class="draw-btn" hover-class="draw-btn-hover" @click="handleDraw">
          <text class="material-symbols-outlined draw-icon">auto_awesome</text>
          <text class="draw-text">点击抽签</text>
        </view>
        <view class="draw-ring draw-ring-1"></view>
        <view class="draw-ring draw-ring-2"></view>
      </view>
    </view>

    <!-- 已抽签：签文 + 运势（淡入） -->
    <view v-else class="lot-result" :class="{ 'lot-result-in': resultVisible }">
      <text class="lot-number">第 {{ lotNumber }} 签</text>
      <text class="lot-text brush-font">{{ zenContent }}</text>
      <text v-if="zenAuthor" class="lot-author">—— {{ zenAuthor }}</text>
      <view class="lot-divider"></view>

      <!-- Case B：有档案 → 运势指数条 -->
      <view v-if="hasArchive && fortuneScores" class="fortune-section">
        <text class="fortune-title">今日运势指数</text>
        <view class="fortune-bars">
          <view v-for="item in fortuneList" :key="item.label" class="fortune-row">
            <text class="fortune-label">{{ item.label }}</text>
            <view class="fortune-bar-bg">
              <view
                class="fortune-bar-fill"
                :style="{
                  width: resultVisible ? item.score + '%' : '0%',
                  backgroundColor: item.color,
                }"
              ></view>
            </view>
            <text class="fortune-score">{{ item.score }}</text>
          </view>
        </view>
      </view>

      <!-- Case A：无档案 → 引导 -->
      <view v-else class="lot-cta-area">
        <text class="lot-cta-hint">录入生辰，解锁每日专属运势曲线</text>
        <view class="lot-cta-btn" hover-class="lot-cta-btn-hover" @click="handleGoCreate">
          <text class="lot-cta-text">建立我的命盘</text>
          <text class="material-symbols-outlined lot-cta-arrow">arrow_forward</text>
        </view>
      </view>

    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { get } from '@/utils/request'

interface Props {
  hasArchive?: boolean
}
const props = withDefaults(defineProps<Props>(), { hasArchive: false })
const emit  = defineEmits<{ (e: 'goCreate'): void }>()

interface FortuneScores {
  overall: number
  wealth:  number
  career:  number
  love:    number
  health:  number
}

interface ZenData {
  id:              number
  content:         string
  author?:         string
  date:            string
  fortune_scores?: FortuneScores
}

// ── 本地兜底 ─────────────────────────────────────────────────────────────────
const FALLBACK = [
  '云无心以出岫，鸟倦飞而知还。',
  '此心安处是吾乡。',
  '竹密不妨流水过，山高岂碍白云飞。',
  '行到水穷处，坐看云起时。',
  '随缘自适，烦恼即菩提。',
  '若无闲事挂心头，便是人间好时节。',
  '上善若水，水善利万物而不争。',
]

// ── 状态 ─────────────────────────────────────────────────────────────────────
const drawn         = ref(false)
const isShaking     = ref(false)
const resultVisible = ref(false)
const lotNumber     = ref(1)
const zenContent    = ref('')
const zenAuthor     = ref('')
const fortuneScores = ref<FortuneScores | null>(null)

// ── 运势指数列表（computed，响应 fortuneScores）────────────────────────────
const fortuneList = computed(() => {
  if (!fortuneScores.value) return []
  const s = fortuneScores.value
  return [
    { label: '综合', score: s.overall, color: '#B23A34' },
    { label: '财富', score: s.wealth,  color: '#D4AF37' },
    { label: '事业', score: s.career,  color: '#4A7C59' },
    { label: '姻缘', score: s.love,    color: '#C0392B' },
    { label: '健康', score: s.health,  color: '#2980B9' },
  ]
})

// ── 初始化：拉取今日禅语 ─────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const res = await get<ZenData>('/api/zen/daily')
    lotNumber.value    = res.id
    zenContent.value   = res.content
    zenAuthor.value    = res.author || ''
    fortuneScores.value = res.fortune_scores ?? null
  } catch {
    const today = new Date().toISOString().split('T')[0]
    let seed = 0
    for (let i = 0; i < today.length; i++) {
      seed = ((seed << 5) - seed) + today.charCodeAt(i)
      seed |= 0
    }
    const idx = Math.abs(seed) % FALLBACK.length
    lotNumber.value  = idx + 1
    zenContent.value = FALLBACK[idx]
  }
})

// ── 抽签：签筒摇晃 → 展示结果 ───────────────────────────────────────────────
function handleDraw() {
  if (isShaking.value) return

  // 签筒摇晃动画（600ms）
  isShaking.value = true
  setTimeout(() => {
    isShaking.value = false
    drawn.value     = true
    // 延一帧触发 CSS 淡入
    setTimeout(() => { resultVisible.value = true }, 30)
  }, 600)
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

/* ── 未抽签 ── */
.lot-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32rpx;
}
.lot-hint {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.45);
  letter-spacing: 0.1em;
}

/* 签筒 */
.qian-tong {
  font-size: 80rpx;
  line-height: 1;
  transform-origin: bottom center;
}
.shaking {
  animation: shake 0.6s ease-in-out;
}
@keyframes shake {
  0%   { transform: rotate(0deg); }
  15%  { transform: rotate(-18deg); }
  30%  { transform: rotate(16deg); }
  45%  { transform: rotate(-14deg); }
  60%  { transform: rotate(12deg); }
  75%  { transform: rotate(-8deg); }
  90%  { transform: rotate(4deg); }
  100% { transform: rotate(0deg); }
}

/* 抽签按钮 */
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
  background: linear-gradient(135deg, #B23A34 0%, #8B2E29 100%);
  border-radius: 48rpx;
  box-shadow: 0 8rpx 24rpx rgba(178, 58, 52, 0.25);
}
.draw-btn-hover { opacity: 0.85; }
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
  margin-bottom: 20rpx;
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
  margin-bottom: 12rpx;
}
.lot-author {
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.4);
  letter-spacing: 0.1em;
}
.lot-divider {
  width: 48rpx;
  height: 1rpx;
  background: rgba(212, 175, 55, 0.4);
  margin: 28rpx auto;
}

/* ── 运势指数条（Case B）── */
.fortune-section {
  width: 100%;
}
.fortune-title {
  display: block;
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.45);
  letter-spacing: 0.2em;
  text-align: center;
  margin-bottom: 28rpx;
}
.fortune-bars {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}
.fortune-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.fortune-label {
  width: 60rpx;
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.7);
  text-align: right;
  flex-shrink: 0;
}
.fortune-bar-bg {
  flex: 1;
  height: 12rpx;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 6rpx;
  overflow: hidden;
}
.fortune-bar-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.fortune-score {
  width: 56rpx;
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.6);
  text-align: left;
  flex-shrink: 0;
}

/* ── 无档案引导（Case A）── */
.lot-cta-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}
.lot-cta-hint {
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.4);
  letter-spacing: 0.05em;
  text-align: center;
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
.lot-cta-btn-hover { background: rgba(178, 58, 52, 0.08); }
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
