<template>
  <view class="page-container">
    <ZenHeader title="塔罗占卜" :show-back="true" />

    <!-- ══════════════════════════════════════
         步骤一：提问界面
    ══════════════════════════════════════ -->
    <view v-if="currentStep === 'ask'" class="main-content">

      <!-- 顶部仪式感标题区 -->
      <view class="hero-section">
        <view class="hero-orb"></view>
        <text class="hero-eyebrow">TAROT · 内在神谕</text>
        <text class="hero-title">向宇宙提问</text>
        <text class="hero-desc">将你此刻最真实的困惑，化为一个清晰的问题</text>
      </view>

      <!-- 核心输入区 -->
      <view class="input-card">
        <view class="input-label-row">
          <text class="material-symbols-outlined input-label-icon">edit_note</text>
          <text class="input-label-text">你的问题</text>
        </view>
        <view class="textarea-wrap">
          <textarea
            class="question-textarea"
            v-model="userQuestion"
            :placeholder="placeholder"
            placeholder-class="textarea-placeholder"
            :maxlength="120"
            auto-height
          />
          <view class="textarea-footer">
            <text class="char-count">{{ userQuestion.length }} / 120</text>
            <view class="inspiration-btn" hover-class="inspiration-btn-hover" @click="getInspiration">
              <text class="inspiration-icon">💡</text>
              <text class="inspiration-text">灵感</text>
            </view>
          </view>
        </view>
        <text class="input-tip">建议以「我」开头，聚焦一个具体的问题，避免是非题</text>
      </view>

      <!-- 开始占卜按钮 -->
      <view class="action-wrap">
        <view class="start-btn" hover-class="start-btn-hover" @click="startReading">
          <text class="material-symbols-outlined start-icon">auto_awesome</text>
          <text class="start-text">洗牌 · 开始占卜</text>
        </view>
      </view>

      <!-- 弹幕区 -->
      <view class="barrage-section">
        <text class="barrage-label">众人之问</text>
        <!-- Row 1：从右向左 35s -->
        <view class="barrage-track">
          <view class="barrage-row barrage-row--r1">
            <view v-for="(item, idx) in barrageRows[0]" :key="'r1'+idx" class="barrage-tag" @click="fillBarrage(item)">
              <text class="barrage-text">{{ item }}</text>
            </view>
          </view>
        </view>
        <!-- Row 2：从左向右 45s（反向） -->
        <view class="barrage-track">
          <view class="barrage-row barrage-row--r2">
            <view v-for="(item, idx) in barrageRows[1]" :key="'r2'+idx" class="barrage-tag" @click="fillBarrage(item)">
              <text class="barrage-text">{{ item }}</text>
            </view>
          </view>
        </view>
        <!-- Row 3：从右向左 40s -->
        <view class="barrage-track">
          <view class="barrage-row barrage-row--r3">
            <view v-for="(item, idx) in barrageRows[2]" :key="'r3'+idx" class="barrage-tag" @click="fillBarrage(item)">
              <text class="barrage-text">{{ item }}</text>
            </view>
          </view>
        </view>
      </view>

    </view>

    <!-- ══════════════════════════════════════
         步骤二：抽牌界面
    ══════════════════════════════════════ -->
    <view v-else-if="currentStep === 'draw'" class="draw-container">

      <!-- 顶部提示 -->
      <view class="draw-header">
        <text class="draw-eyebrow">PAST · PRESENT · FUTURE</text>
        <text class="draw-title">{{ drawHint }}</text>
        <text class="draw-question">「{{ userQuestion }}」</text>
      </view>

      <!-- ══ 圣三角牌阵 ══ -->
      <view class="triangle-spread">

        <!-- 塔尖：未来（槽位 2） -->
        <view class="triangle-row triangle-row--top">
          <view
            class="tri-slot"
            :class="{ 'tri-slot--filled': selectedCards[2] !== undefined }"
          >
            <view v-if="selectedCards[2] !== undefined" class="tri-slot-card tri-slot-card--popin">
              <!-- 未翻转：显示牌背 -->
              <view v-if="!isFlipped[2]" class="tri-card-back">
                <view class="card-rune-ring tri-rune"></view>
                <text class="tri-card-symbol">✦</text>
              </view>
              <!-- 已翻转：显示韦特牌图 -->
              <view v-else class="tri-card-front tri-card-front--reveal">
                <image
                  :src="majorArcana[selectedCards[2]]?.imgUrl"
                  mode="aspectFill"
                  class="tri-card-img"
                  @error="onImgError(selectedCards[2])"
                />
                <view class="tri-card-front-label">
                  <text class="tri-card-front-name">{{ majorArcana[selectedCards[2]]?.name }}</text>
                  <text class="tri-card-front-pos">未來</text>
                </view>
              </view>
            </view>
            <view v-else class="tri-slot-empty">
              <text class="tri-slot-label">未來</text>
              <text class="tri-slot-label-en">FUTURE</text>
            </view>
          </view>
        </view>

        <!-- 塔底：过去（槽位 0）+ 现在（槽位 1） -->
        <view class="triangle-row triangle-row--bottom">
          <!-- 过去 -->
          <view
            class="tri-slot"
            :class="{ 'tri-slot--filled': selectedCards[0] !== undefined }"
          >
            <view v-if="selectedCards[0] !== undefined" class="tri-slot-card tri-slot-card--popin">
              <view v-if="!isFlipped[0]" class="tri-card-back">
                <view class="card-rune-ring tri-rune"></view>
                <text class="tri-card-symbol">✦</text>
              </view>
              <view v-else class="tri-card-front tri-card-front--reveal">
                <image
                  :src="majorArcana[selectedCards[0]]?.imgUrl"
                  mode="aspectFill"
                  class="tri-card-img"
                  @error="onImgError(selectedCards[0])"
                />
                <view class="tri-card-front-label">
                  <text class="tri-card-front-name">{{ majorArcana[selectedCards[0]]?.name }}</text>
                  <text class="tri-card-front-pos">過去</text>
                </view>
              </view>
            </view>
            <view v-else class="tri-slot-empty">
              <text class="tri-slot-label">過去</text>
              <text class="tri-slot-label-en">PAST</text>
            </view>
          </view>

          <!-- 现在 -->
          <view
            class="tri-slot"
            :class="{ 'tri-slot--filled': selectedCards[1] !== undefined }"
          >
            <view v-if="selectedCards[1] !== undefined" class="tri-slot-card tri-slot-card--popin">
              <view v-if="!isFlipped[1]" class="tri-card-back">
                <view class="card-rune-ring tri-rune"></view>
                <text class="tri-card-symbol">✦</text>
              </view>
              <view v-else class="tri-card-front tri-card-front--reveal">
                <image
                  :src="majorArcana[selectedCards[1]]?.imgUrl"
                  mode="aspectFill"
                  class="tri-card-img"
                  @error="onImgError(selectedCards[1])"
                />
                <view class="tri-card-front-label">
                  <text class="tri-card-front-name">{{ majorArcana[selectedCards[1]]?.name }}</text>
                  <text class="tri-card-front-pos">現在</text>
                </view>
              </view>
            </view>
            <view v-else class="tri-slot-empty">
              <text class="tri-slot-label">現在</text>
              <text class="tri-slot-label-en">PRESENT</text>
            </view>
          </view>
        </view>

      </view>

      <!-- ══ 洗牌动画覆盖层 ══ -->
      <view v-if="isShuffling" class="shuffle-overlay">
        <text class="shuffle-hint">正在洗牌...</text>
        <view class="shuffle-deck">
          <view class="shuffle-pile shuffle-pile--left">
            <view v-for="n in 11" :key="'l'+n" class="tarot-card tarot-card--shuffle" :style="{ '--i': n }">
              <view class="tarot-card-inner">
                <view class="tarot-card-back"></view>
                <view class="tarot-card-front"></view>
              </view>
            </view>
          </view>
          <view class="shuffle-pile shuffle-pile--right">
            <view v-for="n in 11" :key="'r'+n" class="tarot-card tarot-card--shuffle" :style="{ '--i': n }">
              <view class="tarot-card-inner">
                <view class="tarot-card-back"></view>
                <view class="tarot-card-front"></view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- ══ 底部手牌区（三国杀式） ══ -->
      <view v-else class="hand-zone-wrap">
        <text class="hand-hint">
          {{ selectedCards.length < 3 ? '滑动选牌，点击抽取' : '解读中...' }}
        </text>
        <scroll-view scroll-x="true" class="hand-zone" :show-scrollbar="false">
          <view class="hand-cards-wrapper">
            <view
              v-for="(cardIdx, i) in deckOrder"
              :key="cardIdx"
              class="hand-card"
              :class="{
                'hand-card--picked':  pickedSet.has(cardIdx),
                'hand-card--hover':   hoveredCard === cardIdx && !pickedSet.has(cardIdx),
              }"
              :style="{
                marginLeft: i === 0 ? '0' : '-80rpx',
                zIndex: hoveredCard === cardIdx ? 50 : i,
                animationDelay: (i * 0.04) + 's',
              }"
              @click="pickHandCard(cardIdx)"
              @touchstart.stop="hoveredCard = cardIdx"
              @touchend.stop="hoveredCard = -1"
            >
              <!-- 牌背 -->
              <view class="hand-card-back">
                <view class="card-rune-ring hand-rune"></view>
                <text class="card-back-symbol">✦</text>
              </view>
              <!-- 已选中标记 -->
              <view v-if="pickedSet.has(cardIdx)" class="hand-card-picked-mark">
                <text class="hand-card-picked-icon">✓</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed, toRaw } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { majorArcana } from '@/data/tarot'

// ── 塔罗历史记录结构（与 tarot-result.vue 保持一致）──
interface TarotRecord {
  id:        string
  title:     string
  question:  string
  cards:     number[]
  createdAt: number
}

// ── 保存历史到 storage（在抽牌完成时立即保存，不依赖结果页）──
const saveTarotHistory = (q: string, c: number[]) => {
  try {
    const raw = uni.getStorageSync('tarot_history')
    const history: TarotRecord[] = (Array.isArray(raw) ? raw : [])
    const newRecord: TarotRecord = {
      id:        `tarot_${Date.now()}`,
      title:     '塔罗·命运圣三角',
      question:  q,
      cards:     [...c],
      createdAt: Date.now(),
    }
    const updated = [newRecord, ...history].slice(0, 50)
    uni.setStorageSync('tarot_history', updated)
    console.log('[Tarot] 历史记录已保存，id:', newRecord.id, '共', updated.length, '条')
  } catch (e) {
    console.warn('[Tarot] 保存历史记录失败', e)
  }
}

// ── 步骤状态 ──
const currentStep = ref<'ask' | 'draw'>('ask')

// ── 洗牌状态 ──
const isShuffling = ref(false)

// ── 提问阶段 ──
const userQuestion = ref('')
const placeholder   = '例如：我在这段关系中，最需要看清的是什么？'

const inspirationList: string[] = [
  '为了突破目前的事业瓶颈，我最需要改变的心态是什么？',
  '在这段关系中，我真正需要的是什么？',
  '我现在的状态，最需要放下的是什么？',
  '关于这个重要决定，我内心深处真实的感受是什么？',
  '我在哪个方面对自己最不诚实？',
  '什么样的改变，会让我的生活更接近我真正想要的样子？',
  '我现在的困境，在向我传递什么信息？',
  '在这段友谊中，我忽视了什么重要的信号？',
  '我对未来的恐惧，根源究竟是什么？',
  '什么力量正在支撑着我，而我却没有意识到？',
]

const barrageList: string[] = [
  '这段感情还能继续吗？',
  '下半年的财运在哪个方向？',
  '我该换工作吗？',
  '他/她对我的感情是真实的吗？',
  '这次创业的时机成熟了吗？',
  '我们之间还有缘分吗？',
  '我现在的低落是暂时的吗？',
  '这段友谊值得我继续付出吗？',
  '我应该主动联系他/她吗？',
  '这个机会是我该抓住的吗？',
  '我的身体在向我发出什么信号？',
  '离开这座城市，是正确的选择吗？',
  '我和家人的关系，如何才能改善？',
  '我现在的迷茫，出路在哪里？',
]

// 将弹幕均分为 3 行，每行数据翻倍拼接（无缝循环用）
const barrageRows: string[][] = (() => {
  const r1 = barrageList.slice(0, 5)
  const r2 = barrageList.slice(5, 10)
  const r3 = barrageList.slice(10)
  return [
    [...r1, ...r1],  // Row 1：翻倍
    [...r2, ...r2],  // Row 2：翻倍
    [...r3, ...r3],  // Row 3：翻倍
  ]
})()

const getInspiration = () => {
  userQuestion.value = inspirationList[Math.floor(Math.random() * inspirationList.length)]
}

const fillBarrage = (text: string) => {
  userQuestion.value = text
  uni.pageScrollTo({ scrollTop: 0, duration: 300 })
}

const startReading = () => {
  const q = userQuestion.value.trim()
  if (!q) {
    uni.showToast({ title: '请先写下你的问题', icon: 'none', duration: 1500 })
    return
  }
  uni.setStorageSync('tarot_question', q)
  // 初始化牌堆并进入抽牌步骤
  initDeck()
  currentStep.value = 'draw'
  // 先进入洗牌阶段，2.5s 后自动结束
  isShuffling.value = true
  setTimeout(() => {
    isShuffling.value = false
    // 洗牌结束，CSS fanSpread 动画自动触发扇形展开
  }, 2500)
}

// ── 抽牌阶段 ──

// 槽位顺序：过去(0) → 现在(1) → 未来(2)
// 三角形布局：底部左=过去，底部右=现在，顶部=未来
const slots = [
  { label: '過去', labelEn: 'PAST'    },
  { label: '現在', labelEn: 'PRESENT' },
  { label: '未來', labelEn: 'FUTURE'  },
]

// 已选中的牌索引（按槽位顺序 0/1/2，最多 3 个）
const selectedCards = ref<number[]>([])

// 各槽位翻牌状态：飞入落稳后延迟触发
const isFlipped = ref<boolean[]>([false, false, false])

// 已被抽走的牌索引集合
const pickedSet = ref<Set<number>>(new Set())

// 洗牌后的牌堆顺序（0-21 随机排列）
const deckOrder = ref<number[]>([])

// 当前悬浮高亮的手牌
const hoveredCard = ref<number>(-1)

// 废弃的旧变量（保留兼容）
const currentSwiperIndex = ref(0)
const deckEntering       = ref(false)
const flyingCards        = ref<any[]>([])
const cardPositions      = ref<any[]>([])
const activeCard         = ref<number>(-1)

// 顶部提示文案
const drawHint = computed(() => {
  const labels = ['过去', '现在', '未来']
  if (selectedCards.value.length < 3) {
    return `请抽取第 ${selectedCards.value.length + 1} 张牌 · ${labels[selectedCards.value.length]}`
  }
  return '三张牌已就位'
})

// 初始化洗牌
const initDeck = () => {
  const arr = Array.from({ length: 22 }, (_, i) => i)
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]]
  }
  deckOrder.value          = arr
  selectedCards.value      = []
  pickedSet.value          = new Set()
  hoveredCard.value        = -1
  deckEntering.value       = false
  currentSwiperIndex.value = 0
  flyingCards.value        = []
  activeCard.value         = -1
  cardPositions.value      = []
  isFlipped.value          = [false, false, false]
}

// 废弃的旧回调（保留兼容）
const onSwiperChange    = (_e: any) => {}
const generatePositions = () => {}
const pickTableCard     = (_c: number, _i: number) => {}
const drawFromDeck      = () => {}
const pickCard          = (_c: number, _i?: number) => {}

// ── 图片加载错误监听 ──
const onImgError = (cardIdx: number) => {
  const card = majorArcana[cardIdx]
  const msg  = card
    ? `图片加载失败：${card.name}（${card.imgUrl}）`
    : `图片加载失败：cardIdx=${cardIdx}`
  console.error('[Tarot]', msg)
  uni.showToast({ title: `${card?.name ?? '未知牌'} 图片加载失败`, icon: 'none', duration: 2000 })
}

// ── 手牌区选牌逻辑 ──
// 点击手牌 → 标记已抽 → 写入对应槽位 → 延迟翻牌
const pickHandCard = (cardIdx: number) => {
  if (pickedSet.value.has(cardIdx) || selectedCards.value.length >= 3) return

  uni.vibrateShort({ type: 'light' })

  // 标记已抽走（手牌区隐藏）
  pickedSet.value = new Set([...pickedSet.value, cardIdx])

  // 写入下一个空槽位（0=过去, 1=现在, 2=未来）
  const slotIdx = selectedCards.value.length
  selectedCards.value = [...selectedCards.value, cardIdx]

  // 飞入动画约 550ms，落稳后再延迟 300ms 触发翻牌
  setTimeout(() => {
    const flipped = [...isFlipped.value]
    flipped[slotIdx] = true
    isFlipped.value = flipped
  }, 850)

  // 3 张全满 → 立即保存历史 + 延迟 2400ms 跳转
  if (selectedCards.value.length === 3) {
    const cardsToSave = toRaw(selectedCards.value)
    uni.setStorageSync('tarot_cards', cardsToSave)
    // 直接用 userQuestion.value，不依赖 storage 中转（避免 key 前缀不一致问题）
    const question = userQuestion.value.trim()
    if (question && cardsToSave.length === 3) {
      saveTarotHistory(question, cardsToSave)
    }
    console.log('[Tarot] 已保存 tarot_cards:', JSON.stringify(cardsToSave), 'question:', question)
    setTimeout(() => {
      uni.navigateTo({ url: '/pages/questions/tarot-result' })
    }, 2400)
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;500;700&family=Inter:wght@300;400;500&display=swap');

/* ══════════════════════════════════════
   全局变量
══════════════════════════════════════ */
.page-container {
  --zen-bg:      #F9F6F1;
  --zen-ink:     #1A1A1A;
  --zen-gray:    #8E8E93;
  --zen-border:  rgba(212, 175, 55, 0.15);
  --zen-surface: rgba(255, 255, 255, 0.72);
  --zen-muted:   rgba(51, 51, 51, 0.52);
  --gold:        #D4AF37;
  --cinnabar:    #B23A34;
  --accent:      #A68B67;

  min-height: 100vh;
  background-color: var(--zen-bg);
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

/* ══════════════════════════════════════
   步骤一：提问界面
══════════════════════════════════════ */
.main-content {
  padding: 0 40rpx 160rpx;
}

.hero-section {
  position: relative;
  text-align: center;
  padding: 60rpx 0 52rpx;
  overflow: hidden;
}

.hero-orb {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 500rpx; height: 500rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(178, 58, 52, 0.06) 0%, transparent 70%);
  pointer-events: none;
  animation: heroBreath 6s ease-in-out infinite;
}

@keyframes heroBreath {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50%       { opacity: 1;   transform: translate(-50%, -50%) scale(1.1); }
}

.hero-eyebrow {
  display: block;
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.7);
  letter-spacing: 0.45em;
  font-weight: 300;
  margin-bottom: 20rpx;
  position: relative;
}

.hero-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 56rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.15em;
  margin-bottom: 20rpx;
  position: relative;
}

.hero-desc {
  display: block;
  font-size: 24rpx;
  color: var(--zen-muted);
  letter-spacing: 0.06em;
  line-height: 1.8;
  position: relative;
}

.input-card {
  background: var(--zen-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
}

.input-label-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.input-label-icon {
  font-size: 28rpx;
  font-weight: 200;
  color: var(--gold);
}

.input-label-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.08em;
}

.textarea-wrap {
  background: rgba(15, 10, 10, 0.72);
  border: none;
  border-radius: 12rpx;
  padding: 40rpx 32rpx 20rpx;
  margin-bottom: 20rpx;
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.12),
    0 0 30rpx rgba(178, 58, 52, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.03);
  animation: inputBreath 4s ease-in-out infinite;
}

@keyframes inputBreath {
  0%, 100% { box-shadow: 0 0 0 1px rgba(212,175,55,0.12), 0 0 20rpx rgba(178,58,52,0.06); }
  50%       { box-shadow: 0 0 0 1px rgba(212,175,55,0.25), 0 0 40rpx rgba(178,58,52,0.14); }
}

.question-textarea {
  width: 100%;
  min-height: 180rpx;
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.88);
  line-height: 2.1;
  letter-spacing: 0.06em;
  text-align: center;
  background: transparent;
  border: none;
  outline: none;
}

.textarea-placeholder {
  color: rgba(255, 255, 255, 0.18);
  font-size: 28rpx;
  font-weight: 300;
  text-align: center;
}

.textarea-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.char-count {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.2);
  letter-spacing: 0.05em;
}

.inspiration-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 20rpx;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 30rpx;
  background: rgba(212, 175, 55, 0.06);
}

.inspiration-btn-hover { opacity: 0.6; }

.inspiration-icon { font-size: 22rpx; line-height: 1; }

.inspiration-text {
  font-size: 20rpx;
  color: rgba(212, 175, 55, 0.7);
  letter-spacing: 0.1em;
}

.input-tip {
  font-size: 20rpx;
  color: rgba(51, 51, 51, 0.35);
  letter-spacing: 0.04em;
  line-height: 1.7;
}

.action-wrap { margin-bottom: 64rpx; }

.start-btn {
  width: 100%;
  height: 104rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  background: var(--cinnabar);
  border-radius: 4rpx;
  box-shadow: 0 8rpx 32rpx rgba(178, 58, 52, 0.25);
}

.start-btn-hover { opacity: 0.8; }

.start-icon { font-size: 32rpx; font-weight: 200; color: rgba(255,255,255,0.9); }

.start-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  color: #fff;
  letter-spacing: 0.2em;
  font-weight: 400;
}

.barrage-section {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.barrage-label {
  display: block;
  font-size: 18rpx;
  color: rgba(51, 51, 51, 0.2);
  letter-spacing: 0.3em;
  text-align: center;
  margin-bottom: 24rpx;
}

.barrage-track {
  display: flex;
  overflow: hidden;
  width: 100%;
}

/* 三行各自透明度略有差异，营造层次感 */
.barrage-track:nth-child(2) { opacity: 0.6; }
.barrage-track:nth-child(3) { opacity: 0.45; }
.barrage-track:nth-child(4) { opacity: 0.55; }

/* 基础行：数据已翻倍，动画只走 -50% 实现无缝循环 */
.barrage-row {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  white-space: nowrap;
}

/* Row 1：从右向左，35s */
.barrage-row--r1 { animation: marqueeL 35s linear infinite; }

/* Row 2：从左向右（反向），45s */
.barrage-row--r2 { animation: marqueeR 45s linear infinite; }

/* Row 3：从右向左，40s */
.barrage-row--r3 { animation: marqueeL 40s linear infinite; }

/* 关键：只走 50%，第二段数据无缝接上第一段 */
@keyframes marqueeL {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

@keyframes marqueeR {
  0%   { transform: translateX(-50%); }
  100% { transform: translateX(0); }
}

.barrage-tag {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 32rpx;
  margin: 0 14rpx;
  border-radius: 40rpx;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(166, 139, 103, 0.12);
  white-space: nowrap;
  flex-shrink: 0;
  filter: blur(0.2px);
}

.barrage-tag:active { opacity: 0.5; }

.barrage-text {
  font-size: 24rpx;
  color: rgba(90, 65, 40, 0.75);
  letter-spacing: 0.04em;
  text-shadow: 0 0 8rpx rgba(212, 175, 55, 0.25);
}

/* ══════════════════════════════════════
   步骤二：抽牌界面
══════════════════════════════════════ */
.draw-container {
  min-height: calc(100vh - 140rpx);
  display: flex;
  flex-direction: column;
  padding: 0 0 0;
  overflow: hidden;
}

/* 顶部提示 */
.draw-header {
  text-align: center;
  padding: 32rpx 40rpx 24rpx;
}

.draw-eyebrow {
  display: block;
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.6);
  letter-spacing: 0.35em;
  font-weight: 300;
  margin-bottom: 12rpx;
}

.draw-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.1em;
  margin-bottom: 10rpx;
}

.draw-question {
  display: block;
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.04em;
  line-height: 1.7;
}

/* ══════════════════════════════════════
   圣三角牌阵
══════════════════════════════════════ */
.triangle-spread {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  padding: 0 40rpx 24rpx;
}

/* 塔尖行（未来） */
.triangle-row--top {
  display: flex;
  justify-content: center;
}

/* 塔底行（过去 + 现在） */
.triangle-row--bottom {
  display: flex;
  gap: 48rpx;
  justify-content: center;
}

/* 单个槽位 */
.tri-slot {
  width: 148rpx;
  height: 220rpx;
  border-radius: 12rpx;
  border: 1.5px dashed rgba(248, 210, 94, 0.40);
  background: rgba(248, 210, 94, 0.018);
  position: relative;
  /* 不裁切：3D 翻转时 front 面需要溢出渲染 */
  overflow: visible;
  transition: border-color 0.4s, box-shadow 0.4s;
}

/* 四角装饰 */
.tri-slot::before,
.tri-slot::after {
  content: '';
  position: absolute;
  width: 14rpx;
  height: 14rpx;
  border-color: rgba(212, 175, 55, 0.45);
  border-style: solid;
}
.tri-slot::before { top: 7rpx; left: 7rpx; border-width: 1px 0 0 1px; }
.tri-slot::after  { bottom: 7rpx; right: 7rpx; border-width: 0 1px 1px 0; }

/* 已填充槽位 */
.tri-slot--filled {
  border-color: rgba(212, 175, 55, 0.5);
  border-style: solid;
  box-shadow:
    0 0 20rpx rgba(212, 175, 55, 0.10),
    inset 0 0 16rpx rgba(212, 175, 55, 0.04);
}

/* 空槽位内容 */
.tri-slot-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.tri-slot-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 34rpx;
  font-weight: bold;
  color: #F8D25E;
  letter-spacing: 4rpx;
  text-shadow:
    0 0 12rpx rgba(248, 210, 94, 0.60),
    0 0 24rpx rgba(248, 210, 94, 0.25);
}

.tri-slot-label-en {
  font-size: 15rpx;
  color: rgba(248, 210, 94, 0.45);
  letter-spacing: 0.28em;
  font-weight: 400;
}

/* 已选中的牌卡（填入槽位） */
.tri-slot-card {
  width: 100%;
  height: 100%;
  position: relative;
}

/* 牌背：填满槽位 */
.tri-card-back {
  position: absolute;
  inset: 0;
  border-radius: 10rpx;
  background:
    radial-gradient(ellipse at 50% 35%, rgba(212,175,55,0.14) 0%, transparent 65%),
    linear-gradient(170deg, #1C1008 0%, #0A0808 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 0 28rpx rgba(212, 175, 55, 0.30),
    inset 0 0 20rpx rgba(212, 175, 55, 0.06);
  /* 翻牌消失动画 */
  animation: cardFlipOut 0.35s ease-in forwards;
}

@keyframes cardFlipOut {
  0%   { transform: scaleX(1);   opacity: 1; }
  100% { transform: scaleX(0);   opacity: 0; }
}

.tri-rune {
  width: 60rpx;
  height: 60rpx;
  border-color: rgba(212, 175, 55, 0.20);
  border-top-color: rgba(212, 175, 55, 0.65);
  animation: runeRingRotate 4s linear infinite;
}

.tri-card-symbol {
  position: absolute;
  font-size: 22rpx;
  color: rgba(212, 175, 55, 0.55);
}

/* 牌面：翻转后出现 */
.tri-card-front {
  position: absolute;
  inset: 0;
  border-radius: 10rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 翻牌出现动画 */
.tri-card-front--reveal {
  animation: cardFlipIn 0.4s ease-out forwards;
  box-shadow:
    0 0 24rpx rgba(248, 210, 94, 0.55),
    0 0 48rpx rgba(248, 210, 94, 0.25);
}

@keyframes cardFlipIn {
  0%   { transform: scaleX(0);   opacity: 0; }
  100% { transform: scaleX(1);   opacity: 1; }
}

/* 韦特牌图片：宽高 100% 填满槽位 */
.tri-card-img {
  width: 100%;
  height: 100%;
  display: block;
}

/* 牌面底部标签条：绝对定位叠在图片底部 */
.tri-card-front-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(10, 6, 4, 0.92) 0%, rgba(10, 6, 4, 0.0) 100%);
  padding: 20rpx 8rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rpx;
  border-radius: 0 0 10rpx 10rpx;
}

.tri-card-front-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 18rpx;
  font-weight: 500;
  color: rgba(248, 210, 94, 0.95);
  letter-spacing: 0.06em;
  text-align: center;
  text-shadow: 0 0 8rpx rgba(248, 210, 94, 0.5);
}

.tri-card-front-pos {
  font-size: 13rpx;
  color: rgba(248, 210, 94, 0.45);
  letter-spacing: 0.2em;
}

/* 飞入动画：从下方弹出 */
.tri-slot-card--popin {
  animation: triPopIn 0.55s cubic-bezier(0.34, 1.4, 0.64, 1) forwards;
}

@keyframes triPopIn {
  0%   { transform: translateY(60rpx) scale(0.65); opacity: 0; }
  55%  { transform: translateY(-6rpx) scale(1.04); opacity: 1; }
  75%  { transform: translateY(2rpx)  scale(0.98); }
  100% { transform: translateY(0)     scale(1);    opacity: 1; }
}

/* ══════════════════════════════════════
   底部手牌区（三国杀式）
══════════════════════════════════════ */
.hand-zone-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;   /* 垂直居中，不再贴底 */
  padding: 0 0 20rpx;
  /* 桌面底部渐变背景，营造手牌区质感 */
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(15, 10, 8, 0.06) 40%,
    rgba(15, 10, 8, 0.18) 100%
  );
  border-top: 1px solid rgba(212, 175, 55, 0.06);
}

.hand-hint {
  display: block;
  font-size: 18rpx;
  color: rgba(166, 139, 103, 0.4);
  letter-spacing: 0.2em;
  text-align: center;
  padding: 0 0 16rpx;
  animation: hintPulse 2.5s ease-in-out infinite;
}

/* 横向滚动容器：高度充裕，确保悬浮/选中时卡牌顶部不被截断 */
.hand-zone {
  width: 100%;
  height: 360rpx;   /* 卡牌高 220rpx + 悬浮 40rpx + 上下各 50rpx 余量 */
  overflow: visible; /* 允许内容在垂直方向溢出，防止截断 */
}

/* 手牌行：垂直居中，上下 padding 为悬浮留出缓冲空间 */
.hand-cards-wrapper {
  display: inline-flex;
  align-items: center;
  padding: 60rpx 200rpx;   /* 上下 60rpx 确保抬起时不被裁切 */
  height: 100%;
  box-sizing: border-box;
}

/* 单张手牌：放大至 140×220rpx */
.hand-card {
  flex-shrink: 0;
  width: 140rpx;
  height: 220rpx;
  border-radius: 14rpx;
  position: relative;
  cursor: pointer;
  /* 除第一张外，负边距重叠约 57%（80/140） */
  margin-left: -80rpx;
  /* 入场动画：依次从底部滑入 */
  animation: handDeal 0.45s cubic-bezier(0.34, 1.4, 0.64, 1) both;
  /* 过渡：悬浮上浮 */
  transition:
    transform  0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity    0.25s ease,
    box-shadow 0.25s ease;
}

/* 第一张牌不需要负边距 */
.hand-cards-wrapper .hand-card:first-child {
  margin-left: 0;
}

@keyframes handDeal {
  0%   { opacity: 0; transform: translateY(40rpx) scale(0.85); }
  100% { opacity: 1; transform: translateY(0)     scale(1); }
}

/* 牌背 */
.hand-card-back {
  position: absolute;
  inset: 0;
  border-radius: 14rpx;
  background:
    radial-gradient(ellipse at 50% 35%, rgba(212,175,55,0.10) 0%, transparent 65%),
    linear-gradient(170deg, #1C1008 0%, #0A0808 100%);
  border: 1px solid rgba(212, 175, 55, 0.22);
  /* 三国杀式左侧深阴影：让重叠层级极其分明 */
  box-shadow:
    -8rpx 0 20rpx rgba(0, 0, 0, 0.60),
    0 8rpx 20rpx rgba(0, 0, 0, 0.45),
    inset 0 0 16rpx rgba(212, 175, 55, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition:
    border-color 0.25s ease,
    box-shadow   0.25s ease;
}

/* 外圈装饰线 */
.hand-card-back::after {
  content: '';
  position: absolute;
  inset: 8rpx;
  border-radius: 8rpx;
  border: 1px solid rgba(212, 175, 55, 0.10);
}

/* 符文环（放大版） */
.hand-rune {
  width: 56rpx;
  height: 56rpx;
  border-color: rgba(212, 175, 55, 0.10);
  border-top-color: rgba(212, 175, 55, 0.28);
  animation: runeRingRotate 9s linear infinite;
}

/* 悬浮：向上抬起 40rpx + 金边高亮 */
.hand-card--hover {
  transform: translateY(-40rpx) scale(1.06) !important;
}
.hand-card--hover .hand-card-back {
  border-color: rgba(212, 175, 55, 0.6);
  box-shadow:
    -8rpx 0 24rpx rgba(0, 0, 0, 0.65),
    0 16rpx 40rpx rgba(178, 58, 52, 0.28),
    0 0 24rpx rgba(212, 175, 55, 0.20),
    inset 0 0 20rpx rgba(212, 175, 55, 0.08);
}

/* 已抽走：淡出，保留占位维持间距 */
.hand-card--picked {
  opacity: 0 !important;
  pointer-events: none;
  transform: translateY(-60rpx) scale(0.8) !important;
}

/* 已抽走标记（可选视觉） */
.hand-card-picked-mark {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, 0.08);
  border-radius: 14rpx;
}

.hand-card-picked-icon {
  font-size: 40rpx;
  color: rgba(212, 175, 55, 0.6);
}

/* ══════════════════════════════════════
   通用符文环 & 符文（洗牌牌 & 散落牌共用）
══════════════════════════════════════ */
.card-rune-ring {
  position: absolute;
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.10);
  border-top-color: rgba(212, 175, 55, 0.28);
  animation: runeRingRotate 8s linear infinite;
}

@keyframes runeRingRotate {
  to { transform: rotate(360deg); }
}

.card-back-symbol {
  position: absolute;
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.18);
}

/* ── 翻牌：显示正面（保留兼容） ── */
.tarot-card--flipped .tarot-card-inner {
  transform: rotateY(180deg);
}

/* ══════════════════════════════════════
   洗牌动画覆盖层
══════════════════════════════════════ */
.shuffle-overlay {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 60rpx;
}

.shuffle-hint {
  display: block;
  font-size: 22rpx;
  color: rgba(212, 175, 55, 0.5);
  letter-spacing: 0.3em;
  margin-bottom: 60rpx;
  animation: hintPulse 1.2s ease-in-out infinite;
}

@keyframes hintPulse {
  0%, 100% { opacity: 0.4; }
  50%       { opacity: 1; }
}

/* 两个牌堆的容器 */
.shuffle-deck {
  position: relative;
  width: 280rpx;
  height: 200rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 左/右牌堆 */
.shuffle-pile {
  position: absolute;
  width: 80rpx;
  height: 120rpx;
}

/* 左堆：向左分离再合拢 */
.shuffle-pile--left {
  animation: shuffleLeft 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* 右堆：向右分离再合拢 */
.shuffle-pile--right {
  animation: shuffleRight 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes shuffleLeft {
  0%   { transform: translateX(0)      translateY(0); }
  20%  { transform: translateX(-60rpx) translateY(-10rpx); }
  50%  { transform: translateX(-60rpx) translateY(0); }
  70%  { transform: translateX(-60rpx) translateY(-6rpx); }
  100% { transform: translateX(0)      translateY(0); }
}

@keyframes shuffleRight {
  0%   { transform: translateX(0)     translateY(0); }
  20%  { transform: translateX(60rpx) translateY(10rpx); }
  50%  { transform: translateX(60rpx) translateY(0); }
  70%  { transform: translateX(60rpx) translateY(6rpx); }
  100% { transform: translateX(0)     translateY(0); }
}

/* 牌堆中每张牌的堆叠偏移 */
.tarot-card--shuffle {
  position: absolute;
  top: 0;
  left: 0;
  /* 每张牌微小偏移，形成厚度感 */
  transform:
    translateX(calc(var(--i, 0) * 0.8rpx))
    translateY(calc(var(--i, 0) * -0.8rpx));
  /* 交错动画：每张牌稍微延迟，产生切牌涟漪感 */
  animation: cardRipple 2.5s calc(var(--i, 0) * 0.04s) ease-in-out infinite;
}

@keyframes cardRipple {
  0%, 100% { transform: translateX(calc(var(--i, 0) * 0.8rpx)) translateY(calc(var(--i, 0) * -0.8rpx)); }
  40%       { transform: translateX(calc(var(--i, 0) * 0.8rpx)) translateY(calc(var(--i, 0) * -0.8rpx - 4rpx)); }
}

/* 洗牌阶段的牌背稍大一点，更有存在感 */
.tarot-card--shuffle .tarot-card-back {
  box-shadow:
    0 4rpx 16rpx rgba(0, 0, 0, 0.4),
    inset 0 0 12rpx rgba(212, 175, 55, 0.08);
}
</style>
