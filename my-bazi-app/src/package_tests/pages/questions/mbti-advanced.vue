<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="64 型附加测试" :show-back="true" />

    <main class="main-content">

      <!-- ══════════════════════════════════════
           答题界面
      ══════════════════════════════════════ -->

      <!-- ── 维度切换提示条 ── -->
      <view class="dim-banner" :class="currentDimBanner === 'AO' ? 'dim-banner--ao' : 'dim-banner--hc'">
        <text class="material-symbols-outlined dim-banner-icon">{{ currentDimBanner === 'AO' ? 'bolt' : 'people' }}</text>
        <view class="dim-banner-text">
          <text class="dim-banner-title">{{ currentDimBanner === 'AO' ? '决断力维度' : '社交温度维度' }}</text>
          <text class="dim-banner-sub">{{ currentDimBanner === 'AO' ? 'A 果断行动 vs O 深度思虑' : 'H 温暖亲和 vs C 冷静独立' }}</text>
        </view>
        <text class="dim-banner-progress">{{ currentDimIndex + 1 }} / {{ currentDimTotal }}</text>
      </view>

      <!-- ── 进度区 ── -->
      <view class="progress-section">
        <view class="progress-meta">
          <text class="progress-label">第 {{ currentIndex + 1 }} 题</text>
          <text class="progress-total">/ {{ questions.length }}</text>
        </view>
        <view class="progress-track">
          <view
            class="progress-fill"
            :style="{ width: progressPercent + '%' }"
          ></view>
        </view>
      </view>

      <!-- ── 题目区 ── -->
      <view class="question-section">
        <text class="question-index">Q{{ currentIndex + 1 }}</text>
        <text class="question-title">{{ currentQuestion?.title }}</text>
      </view>

      <!-- ── 选项区 ── -->
      <view class="options-section">
        <view
          v-for="(opt, idx) in currentQuestion?.options"
          :key="idx"
          class="option-item"
          :class="{
            selected: selectedValue === opt.value,
            answered: answers[currentIndex] === opt.value && selectedValue !== opt.value
          }"
          hover-class="option-hover"
          @click="selectOption(opt.value)"
        >
          <view class="option-indicator">
            <text class="option-letter">{{ String.fromCharCode(65 + idx) }}</text>
          </view>
          <text class="option-label">{{ opt.label }}</text>
          <view class="option-check" v-if="selectedValue === opt.value || answers[currentIndex] === opt.value">
            <text class="material-symbols-outlined check-icon">check</text>
          </view>
        </view>
      </view>

      <!-- ── 上一题按钮 ── -->
      <view v-if="currentIndex > 0" class="prev-btn" hover-class="prev-btn-hover" @click="prevQuestion">
        <text class="material-symbols-outlined prev-icon">arrow_back</text>
        <text class="prev-text">返回上一题</text>
      </view>

      <!-- ── 底部提示 ── -->
      <view class="footer-hint">
        <text class="hint-text">直觉作答，无需过多思考</text>
      </view>

    </main>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, toRaw } from 'vue'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'

// ── 数据结构 ──
interface Option { label: string; value: string }
interface AdvancedQuestion {
  id: number
  dimension: 'AO' | 'HC'
  title: string
  options: [Option, Option]
}

// ── 64 型附加题库（24 题：AO×12 + HC×12）──
const ADVANCED_QUESTIONS: AdvancedQuestion[] = [
  // ── A / O 维度（果断行动 vs 深度思虑）──
  { id: 94,  dimension: 'AO', title: '面对突发状况或棘手挑战，你的第一反应通常是：',           options: [{ label: '迅速评估现状并立刻采取行动', value: 'A' }, { label: '脑海中反复推演可能出现的最坏结果', value: 'O' }] },
  { id: 95,  dimension: 'AO', title: '晚上躺在床上准备入睡时，你的大脑状态更偏向于：',         options: [{ label: '容易放空，很快就能平静入睡', value: 'A' }, { label: '不受控制地复盘白天发生的事或担忧明天', value: 'O' }] },
  { id: 96,  dimension: 'AO', title: '在工作中遭遇失败或犯错后，你的内心活动是：',             options: [{ label: '吸取教训，迅速翻篇，不再内耗', value: 'A' }, { label: '长时间陷入懊恼、内疚或自责的情绪中', value: 'O' }] },
  { id: 97,  dimension: 'AO', title: '当你需要做一个重要决定，但手中信息还不完整时，你倾向于：', options: [{ label: '凭直觉和经验快速拍板，边做边调整', value: 'A' }, { label: '推迟决定，强迫自己去收集极其详尽的信息', value: 'O' }] },
  { id: 98,  dimension: 'AO', title: '面对"完美主义"，你更认同以下哪种工作理念：',             options: [{ label: '完成比完美更重要，先跑起来再说', value: 'A' }, { label: '细节决定成败，达不到完美宁可先不做', value: 'O' }] },
  { id: 99,  dimension: 'AO', title: '在日常消费或点餐时，你通常是：',                         options: [{ label: '看中就买，很快就能做决定', value: 'A' }, { label: '货比三家，反复对比纠结很久', value: 'O' }] },
  { id: 100, dimension: 'AO', title: '当面对他人的负面评价或批评时，你通常：',                 options: [{ label: '有则改之，无则加勉，不会往心里去', value: 'A' }, { label: '表面平静，但内心会纠结和揣摩很久', value: 'O' }] },
  { id: 101, dimension: 'AO', title: '对于未来的不确定性，你的感受更多是：',                   options: [{ label: '充满掌控感，兵来将挡水来土掩', value: 'A' }, { label: '充满担忧，总是害怕事情脱离正轨', value: 'O' }] },
  { id: 102, dimension: 'AO', title: '当别人催促你给出一个结论时，你会：',                     options: [{ label: '立刻给出现有的判断和结论', value: 'A' }, { label: '感到焦虑，觉得还需要更多时间思考', value: 'O' }] },
  { id: 103, dimension: 'AO', title: '你如何看待"试错成本"：',                                 options: [{ label: '试错是常态，错了换条路就行', value: 'A' }, { label: '试错成本太高，必须尽量避免走弯路', value: 'O' }] },
  { id: 104, dimension: 'AO', title: '在执行一个长期计划时，如果中途遇到阻碍，你会：',         options: [{ label: '果断修改甚至放弃原计划，寻找新捷径', value: 'A' }, { label: '纠结于沉没成本，难以轻易做出改变', value: 'O' }] },
  { id: 105, dimension: 'AO', title: '一天的行程结束后，你的感受往往是：',                     options: [{ label: '充满成就感，准备迎接明天', value: 'A' }, { label: '总觉得哪里做得不够好，还有遗憾', value: 'O' }] },
  // ── H / C 维度（温暖亲和 vs 冷静独立）──
  { id: 106, dimension: 'HC', title: '在初次见面的社交场合中，你给人的第一印象通常是：',       options: [{ label: '热情亲切，像太阳一样容易接近', value: 'H' }, { label: '礼貌得体，但带着冰山般的距离感', value: 'C' }] },
  { id: 107, dimension: 'HC', title: '当朋友向你倾诉烦恼，即使你觉得是对方做错了，表面上你会：', options: [{ label: '依然表现出强烈的共情、顺从和安慰', value: 'H' }, { label: '保持客观中立，甚至直接指出对方的问题', value: 'C' }] },
  { id: 108, dimension: 'HC', title: '你对"人际边界感"的把控倾向于：',                         options: [{ label: '容易和人打成一片，边界感较弱', value: 'H' }, { label: '极度注重个人隐私，不允许他人轻易越界', value: 'C' }] },
  { id: 109, dimension: 'HC', title: '在路上偶然遇到半生不熟的同事或熟人，你会：',             options: [{ label: '主动热情地打招呼，甚至寒暄几句', value: 'H' }, { label: '假装没看见，或只是礼貌地点点头走开', value: 'C' }] },
  { id: 110, dimension: 'HC', title: '在工作群或班级群等线上社交中，你的发言风格更接近：',     options: [{ label: '常发表情包和语气词，显得活跃随和', value: 'H' }, { label: '简明扼要，直奔主题，极少闲聊', value: 'C' }] },
  { id: 111, dimension: 'HC', title: '面对同事或同学非分内之事的求助，你通常：',               options: [{ label: '很难拒绝，害怕破坏彼此的和谐关系', value: 'H' }, { label: '果断拒绝，不想浪费自己的精力和时间', value: 'C' }] },
  { id: 112, dimension: 'HC', title: '你如何看待"人情世故"的经营：',                           options: [{ label: '很重要，愿意花时间和情绪价值去维护关系', value: 'H' }, { label: '很麻烦，觉得顺其自然最好，从不刻意讨好', value: 'C' }] },
  { id: 113, dimension: 'HC', title: '在表达对他人的善意或关心时，你倾向于：',                 options: [{ label: '经常通过温暖的言语或肢体接触来表达', value: 'H' }, { label: '很少表露，更多是默默记在心里或做实事', value: 'C' }] },
  { id: 114, dimension: 'HC', title: '对待自己的社交媒体（如朋友圈），你通常：',               options: [{ label: '乐于分享生活日常，与大家频繁互动', value: 'H' }, { label: '三天可见，或极少发私人动态，像个隐形人', value: 'C' }] },
  { id: 115, dimension: 'HC', title: '公司或团队组织非强制性的聚餐团建，你的态度是：',         options: [{ label: '积极响应，享受和大家聚在一起的氛围', value: 'H' }, { label: '能推就推，迫不得已去了也只待在角落', value: 'C' }] },
  { id: 116, dimension: 'HC', title: '在与人交往中，你更容易对哪种人敞开心扉：',               options: [{ label: '只要感觉对了，很容易与人交心', value: 'H' }, { label: '充满防备，需要极长的时间考核才能信任', value: 'C' }] },
  { id: 117, dimension: 'HC', title: '当你一个人独处时，你的内心感受是：',                     options: [{ label: '有时会感到孤独，渴望有人陪伴', value: 'H' }, { label: '极度享受，觉得这才是真正的充电时间', value: 'C' }] },
]

// ── 答题状态 ──
const questions    = ref<AdvancedQuestion[]>([...ADVANCED_QUESTIONS])
const currentIndex = ref(0)
const answers      = ref<string[]>([])
const selectedValue = ref<string | null>(null)

// ── 计算属性 ──
const currentQuestion = computed(() => questions.value[currentIndex.value])

const progressPercent = computed(() =>
  Math.round(((currentIndex.value + (selectedValue.value ? 1 : 0)) / questions.value.length) * 100)
)

// 当前维度标识（用于顶部 banner）
const currentDimBanner = computed(() => currentQuestion.value?.dimension ?? 'AO')

// 当前维度内的题序（1-12）
const currentDimIndex = computed(() => {
  const dim = currentDimBanner.value
  const dimQuestions = questions.value.filter(q => q.dimension === dim)
  const globalIdx = currentIndex.value
  // 找到当前题在本维度中的位置
  let count = 0
  for (let i = 0; i <= globalIdx; i++) {
    if (questions.value[i]?.dimension === dim) count++
  }
  return count - 1
})

const currentDimTotal = computed(() =>
  questions.value.filter(q => q.dimension === currentDimBanner.value).length
)

// ── 选择选项（320ms 后自动推进）──
const selectOption = (value: string) => {
  answers.value[currentIndex.value] = value
  selectedValue.value = value

  // 静默保存进度
  uni.setStorageSync('mbti_advanced_progress', {
    currentIndex: currentIndex.value + 1,
    answers:      toRaw(answers.value),
  })

  setTimeout(() => {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      selectedValue.value = null
    } else {
      calculateResult()
    }
  }, 320)
}

// ── 回退到上一题 ──
const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    selectedValue.value = answers.value[currentIndex.value] ?? null
  }
}

// ── 统分：计算 A/O 和 H/C 两个附加维度 ──
const calculateAdvanced = (userAnswers: string[]) => {
  const scores: Record<string, number> = { A: 0, O: 0, H: 0, C: 0 }
  userAnswers.forEach(val => { if (val in scores) scores[val]++ })

  const typeAO = scores.A >= scores.O ? 'A' : 'O'
  const typeHC = scores.H >= scores.C ? 'H' : 'C'

  return {
    typeAO,
    typeHC,
    details: {
      AO: { A: scores.A, O: scores.O, percent: Math.round((scores.A / Math.max(scores.A + scores.O, 1)) * 100) },
      HC: { H: scores.H, C: scores.C, percent: Math.round((scores.H / Math.max(scores.H + scores.C, 1)) * 100) },
    },
  }
}

// ── 完成 → 合并 16 型基础结果 → 写 Storage → 跳转 ──
const calculateResult = () => {
  const advanced = calculateAdvanced(answers.value)

  // 读取已有的 16 型基础结果
  const base = uni.getStorageSync('mbti_result') || {}
  const baseType: string = base.type ?? '????'

  // 合并为 64 型编码，如 INTJ-AH
  const fullType = `${baseType}-${advanced.typeAO}${advanced.typeHC}`

  // 清除进度缓存
  uni.removeStorageSync('mbti_advanced_progress')

  // 写入 Storage
  uni.setStorageSync('mbti_advanced_result', {
    baseType,
    fullType,
    typeAO:   advanced.typeAO,
    typeHC:   advanced.typeHC,
    details:  advanced.details,
    baseDetails: base.details ?? null,
  })

  // 跳转到附加结果页
  uni.navigateTo({ url: '/package_tests/pages/questions/mbti-advanced-result' })
}
</script>

<style scoped>
/* 页面样式 */
.page-container {
  --zen-bg:       #F9F6F1;
  --zen-ink:      #1A1A1A;
  --zen-gray:     #8E8E93;
  --zen-border:   rgba(212, 175, 55, 0.15);
  --zen-surface:  rgba(255, 255, 255, 0.7);
  --zen-muted:    rgba(51, 51, 51, 0.5);
  --zen-cinnabar: #B23A34;
  --zen-gold:     #D4AF37;
  --zen-accent:   #A68B67;

  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

.main-content {
  padding: 0 48rpx 200rpx;
}

/* ── 维度切换提示条 ── */
.dim-banner {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 48rpx;
  margin: 0 -48rpx 60rpx;
  border-bottom: 1px solid var(--zen-border);
  transition: background 0.4s;
}

.dim-banner--ao {
  background: linear-gradient(90deg, rgba(212, 175, 55, 0.08) 0%, transparent 100%);
}

.dim-banner--hc {
  background: linear-gradient(90deg, rgba(178, 58, 52, 0.06) 0%, transparent 100%);
}

.dim-banner-icon {
  font-size: 36rpx;
  font-weight: 200;
  flex-shrink: 0;
}

.dim-banner--ao .dim-banner-icon { color: var(--zen-gold); }
.dim-banner--hc .dim-banner-icon { color: var(--zen-cinnabar); }

.dim-banner-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.dim-banner-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.06em;
}

.dim-banner-sub {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.04em;
}

.dim-banner-progress {
  font-size: 22rpx;
  color: var(--zen-gray);
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

/* ── 进度区 ── */
.progress-section {
  margin-bottom: 80rpx;
}

.progress-meta {
  display: flex;
  align-items: baseline;
  gap: 6rpx;
  margin-bottom: 20rpx;
}

.progress-label {
  font-size: 24rpx;
  color: var(--zen-cinnabar);
  letter-spacing: 0.15em;
  font-weight: 500;
}

.progress-total {
  font-size: 22rpx;
  color: var(--zen-muted);
  letter-spacing: 0.1em;
}

.progress-track {
  width: 100%;
  height: 2rpx;
  background: rgba(212, 175, 55, 0.2);
  border-radius: 2rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--zen-cinnabar) 0%, var(--zen-gold) 100%);
  border-radius: 2rpx;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── 题目区 ── */
.question-section {
  margin-bottom: 80rpx;
}

.question-index {
  display: block;
  font-size: 20rpx;
  color: var(--zen-gold);
  letter-spacing: 0.4em;
  margin-bottom: 28rpx;
  font-weight: 300;
}

.question-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 40rpx;
  font-weight: 500;
  line-height: 1.75;
  letter-spacing: 0.05em;
  color: var(--zen-ink);
}

/* ── 选项区 ── */
.options-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 60rpx;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 28rpx;
  padding: 40rpx 36rpx;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  transition: border-color 0.25s, background 0.25s;
  position: relative;
  overflow: hidden;
}

.option-item.selected {
  border-color: rgba(178, 58, 52, 0.4);
  background: rgba(178, 58, 52, 0.05);
}

.option-item.selected::before {
  content: '';
  position: absolute;
  left: 0; top: 0;
  width: 4rpx; height: 100%;
  background: var(--zen-cinnabar);
}

.option-item.answered {
  border-color: rgba(178, 58, 52, 0.3);
  background: rgba(178, 58, 52, 0.04);
}

.option-item.answered::before {
  content: '';
  position: absolute;
  left: 0; top: 0;
  width: 4rpx; height: 100%;
  background: rgba(178, 58, 52, 0.5);
}

.option-item.answered .option-indicator {
  border-color: rgba(178, 58, 52, 0.4);
  background: rgba(178, 58, 52, 0.06);
}

.option-item.answered .option-letter { color: rgba(178, 58, 52, 0.7); }
.option-item.answered .option-label  { color: var(--zen-ink); }
.option-item.answered .check-icon    { color: rgba(178, 58, 52, 0.6); }

.option-hover {
  background: rgba(178, 58, 52, 0.03) !important;
}

.option-indicator {
  flex-shrink: 0;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.25s, background 0.25s;
}

.option-item.selected .option-indicator {
  border-color: var(--zen-cinnabar);
  background: rgba(178, 58, 52, 0.08);
}

.option-letter {
  font-size: 22rpx;
  color: var(--zen-muted);
  font-weight: 400;
}

.option-item.selected .option-letter { color: var(--zen-cinnabar); }

.option-label {
  flex: 1;
  font-size: 28rpx;
  line-height: 1.65;
  color: rgba(51, 51, 51, 0.7);
  letter-spacing: 0.03em;
  transition: color 0.25s;
}

.option-item.selected .option-label { color: var(--zen-ink); }

.option-check { flex-shrink: 0; }

.check-icon {
  font-size: 32rpx;
  color: var(--zen-cinnabar);
  font-weight: 300;
}

/* ── 上一题按钮 ── */
.prev-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 28rpx 0;
  margin-bottom: 8rpx;
  transition: opacity 0.2s;
}

.prev-btn-hover { opacity: 0.5; }

.prev-icon {
  font-size: 28rpx;
  font-weight: 200;
  color: var(--zen-gray);
}

.prev-text {
  font-size: 22rpx;
  color: var(--zen-gray);
  letter-spacing: 0.15em;
  font-weight: 300;
}

/* ── 底部提示 ── */
.footer-hint {
  display: flex;
  justify-content: center;
  padding-top: 20rpx;
}

.hint-text {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.25em;
  font-weight: 300;
}
</style>
