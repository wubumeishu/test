<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="塔罗解读" :show-back="true" />

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">

      <!-- ── 顶部装饰 ── -->
      <view class="hero-bg">
        <view class="hero-orb hero-orb--1"></view>
        <view class="hero-orb hero-orb--2"></view>
      </view>

      <!-- ── 问题回显 ── -->
      <view class="question-card">
        <text class="question-eyebrow">YOUR QUESTION</text>
        <text class="question-text">「{{ question }}」</text>
      </view>

      <!-- ── 三张牌解读 ── -->
      <view class="cards-section">
        <view
          v-for="(cardIdx, slotIdx) in cards"
          :key="slotIdx"
          class="card-block"
        >
          <!-- 牌面头部：点击触发放大观察 -->
          <view class="card-header" @click="zoomCard(getCard(cardIdx))">
            <view class="card-position-tag">
              <text class="card-position-text">{{ positionLabels[slotIdx] }}</text>
            </view>
            <view class="card-name-wrap">
              <text class="card-number">{{ cardIdx }}</text>
              <text class="card-name">{{ getCard(cardIdx).name }}</text>
              <text class="card-name-en">{{ getCard(cardIdx).nameEn }}</text>
            </view>
            <!-- 卡图缩略图 + 点击提示 -->
            <view class="card-thumb-wrap">
              <image
                :src="getCard(cardIdx).imgUrl"
                mode="aspectFill"
                class="card-thumb"
              />
              <view class="card-thumb-hint">
                <text class="material-symbols-outlined thumb-hint-icon">zoom_in</text>
              </view>
            </view>
          </view>

          <!-- 关键词 -->
          <view class="card-keywords">
            <text class="keywords-label">关键词</text>
            <text class="keywords-text">{{ getCard(cardIdx).keywords }}</text>
          </view>

          <!-- 深度解读 -->
          <view class="card-desc">
            <text class="desc-text">{{ getCard(cardIdx).description }}</text>
          </view>

          <!-- 分隔线（非最后一张） -->
          <view v-if="slotIdx < 2" class="card-divider">
            <view class="divider-line"></view>
            <text class="divider-symbol">✦</text>
            <view class="divider-line"></view>
          </view>
        </view>
      </view>

      <!-- ── 综合解读 ── -->
      <view class="synthesis-section">
        <view class="section-header">
          <text class="section-en">SYNTHESIS</text>
          <text class="section-zh">综合解读</text>
        </view>
        <view class="synthesis-card">
          <text class="synthesis-text">{{ synthesisText }}</text>
        </view>
      </view>

      <!-- ── 禅意建议 ── -->
      <view class="zen-section">
        <text class="material-symbols-outlined zen-icon">spa</text>
        <text class="zen-text">{{ zenAdvice }}</text>
      </view>

      <!-- ── 操作按钮 ── -->
      <view class="action-section">
        <view class="action-btn action-btn--retry" hover-class="btn-hover" @click="retake">
          <text class="material-symbols-outlined btn-icon">refresh</text>
          <text class="btn-text">重新占卜</text>
        </view>
        <view class="action-btn action-btn--home" hover-class="btn-hover" @click="goHome">
          <text class="material-symbols-outlined btn-icon">home</text>
          <text class="btn-text">返回大厅</text>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- ══ 沉浸式卡片观察层 ══ -->
    <view
      v-if="magnifiedCard"
      class="zoom-overlay"
      @click="closeZoom"
    >
      <!-- 点击任意处退出，内容区不阻止冒泡 -->
      <view class="zoom-content">

        <!-- 大图 -->
        <view class="zoom-card-wrap">
          <image
            :src="magnifiedCard.imgUrl"
            mode="aspectFit"
            class="zoom-card-img"
          />
          <!-- 金色边框光晕 -->
          <view class="zoom-card-glow"></view>
        </view>

        <!-- 牌名 -->
        <view class="zoom-card-title">
          <text class="zoom-card-name">{{ magnifiedCard.name }}</text>
          <text class="zoom-card-name-en">{{ magnifiedCard.nameEn }}</text>
        </view>

        <!-- 禅意引导语 -->
        <text class="zoom-guide">
          闭上眼，深呼吸。{{ '\n' }}观察画面中的色彩与符号，{{ '\n' }}哪个细节最先触动了你？{{ '\n' }}那就是命运给你的回响。
        </text>

        <!-- 关闭提示 -->
        <text class="zoom-close-hint">轻触任意处关闭</text>

      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { majorArcana, type TarotCard } from '../../data/tarot'

// ── 数据 ──
const question   = ref('')
const cards      = ref<number[]>([])
const isHistory  = ref(false)   // 是否为历史回显模式

const positionLabels = ['过去', '现在', '未来']

// ── 塔罗历史记录结构 ──
interface TarotRecord {
  id:        string
  title:     string     // 阵型名称，如「塔罗·命运圣三角」
  question:  string
  cards:     number[]   // [过去, 现在, 未来] 的 majorArcana 索引
  createdAt: number
}

// ── 保存历史记录到本地（必须在 onLoad 之前定义） ──
const saveTarotHistory = (q: string, c: number[]) => {
  try {
    const raw = uni.getStorageSync('tarot_history')
    const history: TarotRecord[] = Array.isArray(raw) ? raw : []
    // 去重：同一问题+同一组牌在 5 秒内不重复保存
    const now = Date.now()
    const isDuplicate = history.some(r =>
      r.question === q &&
      JSON.stringify(r.cards) === JSON.stringify(c) &&
      now - r.createdAt < 5000
    )
    if (isDuplicate) {
      console.log('[TarotResult] 跳过重复保存')
      return
    }
    const newRecord: TarotRecord = {
      id:        `tarot_${now}`,
      title:     '塔罗·命运圣三角',
      question:  q,
      cards:     [...c],
      createdAt: now,
    }
    const updated = [newRecord, ...history].slice(0, 50)
    uni.setStorageSync('tarot_history', updated)
    console.log('[TarotResult] 历史记录已保存，id:', newRecord.id, '当前共', updated.length, '条')
  } catch (e) {
    console.warn('[TarotResult] 保存历史记录失败', e)
  }
}

// ── 加载逻辑 ──
onLoad((options: Record<string, string> = {}) => {
  if ((options.isHistory === '1' || options.isHistory === 'true') && options.historyId) {
    // ── 路径 B：从历史记录跳来，按 historyId 查找 ──
    isHistory.value = true
    const history: TarotRecord[] = uni.getStorageSync('tarot_history') || []
    const record = history.find(r => r.id === options.historyId)
    if (record) {
      question.value = record.question
      cards.value    = record.cards
      console.log('[TarotResult] 历史回显，id:', options.historyId)
    } else {
      // 找不到记录，回退到当前 storage（兜底）
      question.value = uni.getStorageSync('tarot_question') || ''
      cards.value    = uni.getStorageSync('tarot_cards')    || []
      console.warn('[TarotResult] 未找到历史记录，已回退到 storage，id:', options.historyId)
    }
  } else {
    // ── 路径 A：刚抽完牌，从 storage 读取 ──
    isHistory.value = false
    // tarot_question / tarot_cards 由旧代码写入，key 无 uni- 前缀，需直接读 localStorage
    const rawQ = uni.getStorageSync('tarot_question') || localStorage.getItem('tarot_question') || ''
    const rawC = uni.getStorageSync('tarot_cards')
    const rawCArr = Array.isArray(rawC) ? rawC
      : (typeof rawC === 'string' && rawC ? JSON.parse(rawC) : null)
      ?? (() => { try { return JSON.parse(localStorage.getItem('tarot_cards') || '[]') } catch { return [] } })()
    question.value = rawQ
    cards.value    = rawCArr
    console.log('[TarotResult] 路径A 读取: question=', question.value, 'cards=', JSON.stringify(cards.value))

    // 保存到历史记录（仅新占卜时保存，回显不重复保存）
    if (question.value && cards.value.length === 3) {
      saveTarotHistory(question.value, cards.value)
    } else {
      console.warn('[TarotResult] 数据不完整，跳过保存：question=', question.value, 'cards=', cards.value)
    }
  }
})

const getCard = (idx: number) => majorArcana[idx] ?? majorArcana[0]

// ── 沉浸式卡片观察 ──
const magnifiedCard = ref<TarotCard | null>(null)

const zoomCard = (card: TarotCard) => {
  magnifiedCard.value = card
  uni.pageScrollTo({ scrollTop: 0, duration: 0 })
}

const closeZoom = () => {
  magnifiedCard.value = null
}

// ── 综合解读（根据三张牌动态生成） ──
const synthesisText = computed(() => {
  if (cards.value.length < 3) return ''
  const past    = getCard(cards.value[0])
  const present = getCard(cards.value[1])
  const future  = getCard(cards.value[2])
  return `过去的「${past.name}」塑造了你今日的处境，它的能量仍在你身上留有印记。当下的「${present.name}」揭示了你此刻真实的状态与核心课题。而未来的「${future.name}」并非命运的判决，而是一种可能性的邀请——当你整合过去的经验，清醒地面对当下，这张牌所代表的能量便会自然流向你的生命。`
})

// ── 禅意建议 ──
const zenAdvice = computed(() => {
  if (cards.value.length < 3) return ''
  const future = getCard(cards.value[2])
  return `牌不预言命运，它只是镜子。「${future.name}」在提醒你：${future.keywords.split('、')[0]}，是此刻最值得你关注的方向。`
})

// ── 操作 ──
const retake = () => {
  uni.navigateBack()
}

const goHome = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style scoped>
/* 页面样式 */

.page-container {
  --zen-bg:      #F9F6F1;
  --zen-ink:     #1A1A1A;
  --zen-border:  rgba(212, 175, 55, 0.18);
  --zen-surface: rgba(255, 255, 255, 0.72);
  --zen-muted:   rgba(51, 51, 51, 0.52);
  --gold:        #D4AF37;
  --cinnabar:    #B23A34;
  --accent:      #A68B67;

  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

.scroll-body { height: calc(100vh - 140rpx); }

/* 装饰光晕 */
.hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 500rpx;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.06;
}

.hero-orb--1 {
  width: 400rpx; height: 400rpx;
  background: var(--cinnabar);
  top: -150rpx; right: -80rpx;
}

.hero-orb--2 {
  width: 300rpx; height: 300rpx;
  background: var(--gold);
  top: 80rpx; left: -100rpx;
}

/* 问题回显 */
.question-card {
  position: relative;
  z-index: 1;
  margin: 40rpx 40rpx 0;
  padding: 44rpx 48rpx;
  background: var(--zen-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  text-align: center;
}

.question-eyebrow {
  display: block;
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.5);
  letter-spacing: 0.35em;
  font-weight: 300;
  margin-bottom: 20rpx;
}

.question-text {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: var(--zen-muted);
  line-height: 1.9;
  letter-spacing: 0.05em;
}

/* 三张牌解读 */
.cards-section {
  padding: 48rpx 40rpx 0;
}

.card-block { margin-bottom: 8rpx; }

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
  margin-bottom: 28rpx;
}

.card-position-tag {
  flex-shrink: 0;
  padding: 8rpx 20rpx;
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 6rpx;
  background: rgba(212, 175, 55, 0.06);
  margin-top: 4rpx;
}

.card-position-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 22rpx;
  color: var(--gold);
  letter-spacing: 0.1em;
}

.card-name-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.card-number {
  font-size: 18rpx;
  color: rgba(51, 51, 51, 0.25);
  letter-spacing: 0.1em;
}

.card-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 40rpx;
  font-weight: 700;
  color: var(--zen-ink);
  letter-spacing: 0.08em;
  line-height: 1;
}

.card-name-en {
  font-size: 20rpx;
  color: rgba(51, 51, 51, 0.3);
  letter-spacing: 0.15em;
  font-weight: 300;
}

.card-keywords {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding: 16rpx 24rpx;
  background: rgba(212, 175, 55, 0.04);
  border-left: 3rpx solid rgba(212, 175, 55, 0.4);
  border-radius: 0 4rpx 4rpx 0;
}

.keywords-label {
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.6);
  letter-spacing: 0.1em;
  flex-shrink: 0;
}

.keywords-text {
  font-size: 22rpx;
  color: var(--zen-muted);
  letter-spacing: 0.04em;
  line-height: 1.7;
}

.card-desc {
  padding: 32rpx 36rpx;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  margin-bottom: 40rpx;
}

.desc-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: var(--zen-muted);
  line-height: 2.1;
  letter-spacing: 0.04em;
}

.card-divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--zen-border);
}

.divider-symbol {
  font-size: 16rpx;
  color: rgba(212, 175, 55, 0.3);
}

/* 综合解读 */
.synthesis-section {
  padding: 0 40rpx;
  margin-top: 8rpx;
}

.section-header { margin-bottom: 24rpx; }

.section-en {
  display: block;
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.6);
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

.synthesis-card {
  padding: 44rpx 40rpx;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  position: relative;
}

.synthesis-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0;
  width: 4rpx; height: 100%;
  background: linear-gradient(180deg, var(--cinnabar) 0%, var(--gold) 100%);
  border-radius: 4rpx 0 0 4rpx;
}

.synthesis-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: var(--zen-muted);
  line-height: 2.1;
  letter-spacing: 0.04em;
}

/* 禅意建议 */
.zen-section {
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
  margin: 40rpx 40rpx 0;
  padding: 40rpx;
  background: linear-gradient(135deg, rgba(178,58,52,0.04) 0%, rgba(212,175,55,0.06) 100%);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 4rpx;
}

.zen-icon {
  font-size: 40rpx;
  font-weight: 200;
  color: var(--gold);
  flex-shrink: 0;
  margin-top: 4rpx;
}

.zen-text {
  flex: 1;
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: var(--zen-ink);
  line-height: 2;
  letter-spacing: 0.05em;
}

/* 操作按钮 */
.action-section {
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

.action-btn--retry {
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
}

.action-btn--home {
  background: var(--cinnabar);
  border: none;
}

.btn-hover { opacity: 0.75; }

.btn-icon { font-size: 30rpx; font-weight: 200; }
.action-btn--retry .btn-icon { color: var(--accent); }
.action-btn--home  .btn-icon { color: rgba(255,255,255,0.85); }

.btn-text { font-size: 26rpx; letter-spacing: 0.12em; font-weight: 300; }
.action-btn--retry .btn-text { color: var(--zen-ink); }
.action-btn--home  .btn-text { color: #fff; }

.safe-bottom { height: 120rpx; }

/* ══════════════════════════════════════
   沉浸式卡片观察层
══════════════════════════════════════ */

/* 全屏遮罩 */
.zoom-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 透明背景 + 毛玻璃效果 */
  background: transparent;
  backdrop-filter: blur(40px) brightness(0.3);
  -webkit-backdrop-filter: blur(40px) brightness(0.3);
  animation: overlayIn 0.3s ease forwards;
}

@keyframes overlayIn {
  0%   { opacity: 0; }
  100% { opacity: 1; }
}

/* 内容容器：居中，不响应点击冒泡 */
.zoom-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32rpx;
  padding: 0 48rpx;
  width: 100%;
  animation: zoomContentIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes zoomContentIn {
  0%   { transform: scale(0.72); opacity: 0; }
  100% { transform: scale(1);    opacity: 1; }
}

/* 卡片容器：相对定位，用于叠加光晕 */
.zoom-card-wrap {
  position: relative;
  width: 380rpx;
  /* 保持塔罗牌比例约 2:3 */
  height: 570rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

/* 大图 */
.zoom-card-img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 16rpx;
  /* 极细亮金色边框 */
  box-shadow:
    0 0 0 1.5px rgba(248, 210, 94, 0.6),
    0 0 50rpx rgba(248, 210, 94, 0.20),
    0 0 100rpx rgba(248, 210, 94, 0.08),
    0 40rpx 80rpx rgba(0, 0, 0, 0.6);
}

/* 呼吸感外发光圈 */
.zoom-card-glow {
  position: absolute;
  inset: -4rpx;
  border-radius: 20rpx;
  border: 1px solid rgba(248, 210, 94, 0.25);
  animation: glowBreath 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowBreath {
  0%, 100% {
    box-shadow: 0 0 20rpx rgba(248, 210, 94, 0.15);
    opacity: 0.6;
  }
  50% {
    box-shadow: 0 0 48rpx rgba(248, 210, 94, 0.40);
    opacity: 1;
  }
}

/* 牌名区 */
.zoom-card-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.zoom-card-name {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 40rpx;
  font-weight: 500;
  color: rgba(248, 210, 94, 0.92);
  letter-spacing: 0.15em;
  text-shadow: 0 0 20rpx rgba(248, 210, 94, 0.4);
}

.zoom-card-name-en {
  display: block;
  font-size: 18rpx;
  color: rgba(248, 210, 94, 0.35);
  letter-spacing: 0.35em;
  font-weight: 300;
}

/* 禅意引导语 */
.zoom-guide {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 22rpx;
  color: rgba(200, 190, 175, 0.55);
  letter-spacing: 0.18em;
  line-height: 2.2;
  text-align: center;
  /* 延迟出现，营造空灵感 */
  animation: guideIn 0.8s ease 0.3s both;
}

@keyframes guideIn {
  0%   { opacity: 0; transform: translateY(12rpx); }
  100% { opacity: 1; transform: translateY(0); }
}

/* 关闭提示 */
.zoom-close-hint {
  display: block;
  font-size: 18rpx;
  color: rgba(255, 255, 255, 0.15);
  letter-spacing: 0.2em;
  animation: guideIn 0.8s ease 0.6s both;
}

/* 卡片头部：加入缩略图和点击提示 */
.card-thumb-wrap {
  position: relative;
  flex-shrink: 0;
  width: 72rpx;
  height: 108rpx;
  border-radius: 8rpx;
  overflow: hidden;
  border: 1px solid rgba(212, 175, 55, 0.3);
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.2);
}

.card-thumb {
  width: 100%;
  height: 100%;
  display: block;
}

/* 悬浮放大提示图标 */
.card-thumb-hint {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.card-header:active .card-thumb-hint {
  opacity: 1;
}

.thumb-hint-icon {
  font-size: 28rpx;
  font-weight: 200;
  color: rgba(248, 210, 94, 0.9);
}
</style>
