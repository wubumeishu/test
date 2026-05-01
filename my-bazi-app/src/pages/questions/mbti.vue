<template>
  <view class="page-container">
    <ZenHeader title="MBTI 测试" :show-back="true" />

    <main class="main-content">

      <!-- ══════════════════════════════════════
           版本选择界面
      ══════════════════════════════════════ -->
      <view v-if="currentStep === 'select'" class="select-view">

        <!-- 顶部标题 -->
        <view class="select-header">
          <text class="select-eyebrow">MBTI · 灵性探索</text>
          <text class="select-title">请选择探索深度</text>
          <text class="select-desc">不同的题目数量，带来不同颗粒度的灵魂解析</text>
        </view>

        <!-- 装饰分隔线 -->
        <view class="select-divider">
          <view class="divider-line"></view>
          <text class="divider-symbol">✦</text>
          <view class="divider-line"></view>
        </view>

        <!-- 继续上次进度（有缓存时显示） -->
        <view
          v-if="savedProgress"
          class="resume-card"
          hover-class="resume-card-hover"
          @click="resumeTest"
        >
          <view class="resume-card-left">
            <text class="material-symbols-outlined resume-icon">history</text>
          </view>
          <view class="resume-card-body">
            <text class="resume-title">继续上次测试</text>
            <text class="resume-sub">
              {{ savedProgress.version === 'full' ? '93 题完整版' : '28 题精简版' }}
              · 已答 {{ savedProgress.currentIndex }} 题
            </text>
          </view>
          <view class="resume-arrow">
            <text class="material-symbols-outlined">chevron_right</text>
          </view>
        </view>

        <!-- 精简版卡片 -->
        <view
          class="version-card"
          hover-class="version-card-hover"
          @click="startTest('short')"
        >
          <view class="version-card-left">
            <view class="version-icon-wrap">
              <text class="material-symbols-outlined version-icon">bolt</text>
            </view>
          </view>
          <view class="version-card-body">
            <view class="version-tags">
              <text class="version-tag">约需 5 分钟</text>
              <text class="version-tag">快速了解核心性格</text>
            </view>
            <text class="version-title">28 题 精简版</text>
            <text class="version-sub">覆盖四大维度，快速定位你的人格类型</text>
          </view>
          <view class="version-arrow">
            <text class="material-symbols-outlined">chevron_right</text>
          </view>
        </view>

        <!-- 完整版卡片（推荐，朱砂红高亮边框） -->
        <view
          class="version-card version-card--featured"
          hover-class="version-card-hover"
          @click="startTest('full')"
        >
          <!-- 推荐角标 -->
          <view class="featured-badge">
            <text class="featured-badge-text">推荐</text>
          </view>

          <view class="version-card-left">
            <view class="version-icon-wrap version-icon-wrap--featured">
              <text class="material-symbols-outlined version-icon version-icon--featured">self_improvement</text>
            </view>
          </view>
          <view class="version-card-body">
            <view class="version-tags">
              <text class="version-tag">约需 15 分钟</text>
              <text class="version-tag version-tag--featured">深度剖析</text>
            </view>
            <text class="version-title">93 题 完整版</text>
            <text class="version-sub">深度剖析 16 型人格细节，洞见灵魂底色</text>
          </view>
          <view class="version-arrow version-arrow--featured">
            <text class="material-symbols-outlined">chevron_right</text>
          </view>
        </view>

        <!-- 底部提示 -->
        <view class="select-footer">
          <text class="select-footer-text">答案无对错之分，请遵从第一直觉</text>
        </view>

      </view>

      <!-- ══════════════════════════════════════
           答题界面
      ══════════════════════════════════════ -->
      <view v-else class="testing-view">

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
          <text class="question-title">{{ currentQuestion.title }}</text>
        </view>

        <!-- ── 选项区 ── -->
        <view class="options-section">
          <view
            v-for="(opt, idx) in currentQuestion.options"
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

      </view>




    </main>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, toRaw, onMounted } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { mbti93Questions } from '@/data/mbti93'
import { mbtiDict } from '@/data/mbtiDict'
import type { MbtiInfo } from '@/data/mbtiDict'

// ── 数据结构 ──
interface Option { label: string; value: string }
interface Question {
  dimension: 'EI' | 'SN' | 'TF' | 'JP'
  title: string
  options: [Option, Option]
}
interface DimDetail { E?: number; I?: number; S?: number; N?: number; T?: number; F?: number; J?: number; P?: number; percent: number }
interface MbtiResult {
  type: string
  details: Record<string, DimDetail>
}

// ── 将 93 题 JSON 转换为内部 Question 格式 ──
const toQuestions = (raw: typeof mbti93Questions): Question[] =>
  raw.map(item => ({
    dimension: item.dim,
    title: item.q,
    options: [
      { label: item.a[0].t, value: item.a[0].v },
      { label: item.a[1].t, value: item.a[1].v },
    ],
  }))

// ── 28 题精简题库（每维度 7 题，EI×7 / SN×7 / TF×7 / JP×7）──
const SHORT_QUESTIONS: Question[] = [
  // ── E / I ──
  { dimension: 'EI', title: '在社交聚会中，你通常会……',         options: [{ label: '主动和很多人交谈，包括陌生人', value: 'E' }, { label: '只和认识的少数人交谈', value: 'I' }] },
  { dimension: 'EI', title: '一个漫长的工作日结束后，你更想……', options: [{ label: '和朋友出去聚聚，充充电', value: 'E' }, { label: '独自待在家里，安静放松', value: 'I' }] },
  { dimension: 'EI', title: '在团队讨论中，你通常……',           options: [{ label: '积极发言，边说边理清思路', value: 'E' }, { label: '先在心里想清楚，再开口', value: 'I' }] },
  { dimension: 'EI', title: '你更享受哪种周末？',               options: [{ label: '参加派对或各种社交活动', value: 'E' }, { label: '在家读书、看剧或独处', value: 'I' }] },
  { dimension: 'EI', title: '认识新朋友时，你……',               options: [{ label: '很快就能打开话匣子，感觉自然', value: 'E' }, { label: '需要一段时间才能放开', value: 'I' }] },
  { dimension: 'EI', title: '你的能量来源更多是……',             options: [{ label: '与他人互动、交流想法', value: 'E' }, { label: '独处、内省和安静思考', value: 'I' }] },
  { dimension: 'EI', title: '在陌生环境中，你倾向于……',         options: [{ label: '主动探索，结交新朋友', value: 'E' }, { label: '先观察，等熟悉后再融入', value: 'I' }] },
  // ── S / N ──
  { dimension: 'SN', title: '学习新技能时，你更喜欢……',         options: [{ label: '按步骤来，先掌握基础细节', value: 'S' }, { label: '先了解整体框架，再填充细节', value: 'N' }] },
  { dimension: 'SN', title: '你更信任……',                       options: [{ label: '亲身经历和具体事实', value: 'S' }, { label: '直觉和对未来的预感', value: 'N' }] },
  { dimension: 'SN', title: '描述一次旅行，你更倾向于……',       options: [{ label: '讲述具体发生的事情和细节', value: 'S' }, { label: '分享旅途带给你的感悟和联想', value: 'N' }] },
  { dimension: 'SN', title: '面对问题，你更习惯……',             options: [{ label: '从已有经验出发，找实际可行的方案', value: 'S' }, { label: '跳出框架，探索全新的可能性', value: 'N' }] },
  { dimension: 'SN', title: '你更享受……',                       options: [{ label: '把事情做得精准、扎实', value: 'S' }, { label: '构想新点子、探索未知领域', value: 'N' }] },
  { dimension: 'SN', title: '阅读时，你更喜欢……',               options: [{ label: '有实际案例和具体数据的内容', value: 'S' }, { label: '充满隐喻、象征和深层含义的内容', value: 'N' }] },
  { dimension: 'SN', title: '你对未来的态度更接近……',           options: [{ label: '脚踏实地，一步一个脚印', value: 'S' }, { label: '充满想象，喜欢规划各种可能', value: 'N' }] },
  // ── T / F ──
  { dimension: 'TF', title: '做重要决定时，你更依赖……',         options: [{ label: '逻辑分析和客观标准', value: 'T' }, { label: '内心感受和对他人的影响', value: 'F' }] },
  { dimension: 'TF', title: '朋友向你倾诉烦恼，你更倾向于……',   options: [{ label: '帮他分析问题，提出解决方案', value: 'T' }, { label: '先倾听和共情，让他感到被理解', value: 'F' }] },
  { dimension: 'TF', title: '评价一个想法时，你首先关注……',     options: [{ label: '它是否合理、有没有逻辑漏洞', value: 'T' }, { label: '它是否符合大家的价值观和感受', value: 'F' }] },
  { dimension: 'TF', title: '在争论中，你更在意……',             options: [{ label: '谁的论点更有说服力', value: 'T' }, { label: '争论是否伤害了彼此的感情', value: 'F' }] },
  { dimension: 'TF', title: '给别人反馈时，你更倾向于……',       options: [{ label: '直接指出问题，哪怕对方不舒服', value: 'T' }, { label: '先肯定优点，再委婉提出不足', value: 'F' }] },
  { dimension: 'TF', title: '你认为公平更接近……',               options: [{ label: '一视同仁，按规则办事', value: 'T' }, { label: '因人而异，考虑每个人的处境', value: 'F' }] },
  { dimension: 'TF', title: '选择职业时，你更看重……',           options: [{ label: '能力发挥和成就感', value: 'T' }, { label: '能帮助他人、有意义感', value: 'F' }] },
  // ── J / P ──
  { dimension: 'JP', title: '对于计划，你的态度是……',           options: [{ label: '提前做好详细安排，按计划执行', value: 'J' }, { label: '保持灵活，随机应变', value: 'P' }] },
  { dimension: 'JP', title: '你的工作桌/房间通常……',            options: [{ label: '整洁有序，东西各归其位', value: 'J' }, { label: '看起来乱，但自己知道东西在哪', value: 'P' }] },
  { dimension: 'JP', title: '面对截止日期，你通常……',           options: [{ label: '提前完成，不喜欢最后一刻的压力', value: 'J' }, { label: '在截止前才进入状态，压力反而激发效率', value: 'P' }] },
  { dimension: 'JP', title: '旅行时，你更喜欢……',               options: [{ label: '提前规划好行程和住宿', value: 'J' }, { label: '随性出发，走到哪算哪', value: 'P' }] },
  { dimension: 'JP', title: '事情没有结论时，你会……',           options: [{ label: '感到不安，想尽快做出决定', value: 'J' }, { label: '觉得还好，可以继续观望', value: 'P' }] },
  { dimension: 'JP', title: '你更喜欢哪种工作方式？',           options: [{ label: '有明确的目标和流程', value: 'J' }, { label: '灵活自由，可以随时调整方向', value: 'P' }] },
  { dimension: 'JP', title: '购物时，你通常……',                 options: [{ label: '列好清单，按需购买', value: 'J' }, { label: '随心所欲，看到喜欢的就买', value: 'P' }] },
]

// ── 步骤状态 ──
const currentStep        = ref<'select' | 'testing'>('select')
const currentTestVersion = ref<'short' | 'full' | ''>('')   // 记录用户选择的版本

// ── 进度恢复 ──
interface SavedProgress {
  version: 'short' | 'full'
  currentIndex: number
  answers: string[]
}
const savedProgress = ref<SavedProgress | null>(null)

onMounted(() => {
  savedProgress.value = uni.getStorageSync('mbti_progress') || null
})

// ── 题目数组（由 startTest 动态填充）──
const questions = ref<Question[]>([])

// ── 答题状态 ──
const currentIndex  = ref(0)
const answers       = ref<string[]>([])
const selectedValue = ref<string | null>(null)

// ── 最终结果（仅用于暂存，计算完立即写 Storage 并跳转）──
const finalResult    = ref<MbtiResult | null>(null)
const detailedScores = ref<MbtiResult['details'] | null>(null)

// ── 计算属性 ──
const currentQuestion = computed(() => questions.value[currentIndex.value])
const isLastQuestion  = computed(() => currentIndex.value === questions.value.length - 1)
const progressPercent = computed(() =>
  Math.round(((currentIndex.value + (selectedValue.value ? 1 : 0)) / questions.value.length) * 100)
)

// ── 开始测试 ──
const startTest = (type: 'short' | 'full') => {
  currentTestVersion.value = type                          // 记录版本
  questions.value     = type === 'short'
    ? [...SHORT_QUESTIONS]
    : toQuestions(mbti93Questions)
  currentIndex.value  = 0
  answers.value       = []
  selectedValue.value = null
  finalResult.value   = null
  detailedScores.value = null
  currentStep.value   = 'testing'
}

// ── 选择选项（选中后 320ms 自动推进）──
const selectOption = (value: string) => {
  answers.value[currentIndex.value] = value
  selectedValue.value = value

  // 静默保存进度
  const nextIndex = currentIndex.value + 1
  uni.setStorageSync('mbti_progress', {
    version:      currentTestVersion.value,
    currentIndex: nextIndex,
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

// ── 统分算法（分毫不差版，含维度百分比供结果页展示能量条）──
const calculateMBTI = (userAnswers: string[]): MbtiResult => {
  // 1. 初始化四个维度的分数
  const scores: Record<string, number> = { E: 0, I: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 }

  // 2. 累加用户的选择
  userAnswers.forEach(val => {
    if (val in scores) scores[val]++
  })

  // 3. 计算最终维度
  //    平票时倾向 I / N / F / P（内倾/直觉/情感/感知），即严格 > 才取前者
  const typeE_I = scores.E > scores.I ? 'E' : 'I'
  const typeS_N = scores.S > scores.N ? 'S' : 'N'
  const typeT_F = scores.T > scores.F ? 'T' : 'F'
  const typeJ_P = scores.J > scores.P ? 'J' : 'P'
  const finalType = typeE_I + typeS_N + typeT_F + typeJ_P

  // 4. 返回结果 + 各维度原始分和百分比（E 占比，S 占比，T 占比，J 占比）
  return {
    type: finalType,
    details: {
      EI: { E: scores.E, I: scores.I, percent: Math.round((scores.E / Math.max(scores.E + scores.I, 1)) * 100) },
      SN: { S: scores.S, N: scores.N, percent: Math.round((scores.S / Math.max(scores.S + scores.N, 1)) * 100) },
      TF: { T: scores.T, F: scores.F, percent: Math.round((scores.T / Math.max(scores.T + scores.F, 1)) * 100) },
      JP: { J: scores.J, P: scores.P, percent: Math.round((scores.J / Math.max(scores.J + scores.P, 1)) * 100) },
    },
  }
}

// ── 触发计算 → 写 Storage → 跳转结果页 ──
const calculateResult = () => {
  const result = calculateMBTI(answers.value)
  finalResult.value    = result
  detailedScores.value = currentTestVersion.value === 'full' ? result.details : null

  // 清除进度缓存
  uni.removeStorageSync('mbti_progress')
  savedProgress.value = null

  // 将结果暂存到本地，供结果页读取
  uni.setStorageSync('mbti_result', {
    type:    result.type,
    details: result.details,
    version: currentTestVersion.value,
  })

  // 跳转到独立结果页
  uni.navigateTo({ url: '/pages/questions/mbti-result' })
}

// ── 回退到上一题 ──
const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    // 恢复该题已选的答案（如有），让用户看到之前的选择
    selectedValue.value = answers.value[currentIndex.value] ?? null
  }
}

// ── 恢复上次进度 ──
const resumeTest = () => {
  if (!savedProgress.value) return
  const p = savedProgress.value
  currentTestVersion.value = p.version
  questions.value = p.version === 'short'
    ? [...SHORT_QUESTIONS]
    : toQuestions(mbti93Questions)
  answers.value       = p.answers
  currentIndex.value  = p.currentIndex
  selectedValue.value = null
  currentStep.value   = 'testing'
}

// ── 重新测试（从结果页返回时调用，或直接重置状态）──
const retakeTest = () => {
  currentStep.value        = 'select'
  currentTestVersion.value = ''
  currentIndex.value       = 0
  answers.value            = []
  selectedValue.value      = null
  finalResult.value        = null
  detailedScores.value     = null
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

/* ── 全局变量：与项目主题完全一致 ── */
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
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

.main-content {
  padding: 60rpx 48rpx 200rpx;
}

/* ══════════════════════════════════════
   版本选择界面
══════════════════════════════════════ */

.select-header {
  text-align: center;
  margin-bottom: 60rpx;
}

.select-eyebrow {
  display: block;
  font-size: 20rpx;
  color: var(--zen-gold);
  letter-spacing: 0.4em;
  margin-bottom: 24rpx;
  font-weight: 300;
}

.select-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 44rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.08em;
  margin-bottom: 20rpx;
  line-height: 1.4;
}

.select-desc {
  display: block;
  font-size: 24rpx;
  color: var(--zen-muted);
  letter-spacing: 0.05em;
  line-height: 1.7;
}

/* 装饰分隔线 */
.select-divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 60rpx;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--zen-border);
}

.divider-symbol {
  font-size: 20rpx;
  color: var(--zen-gold);
  opacity: 0.6;
}

/* 版本卡片 */
.version-card {
  display: flex;
  align-items: center;
  gap: 28rpx;
  padding: 44rpx 36rpx;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  margin-bottom: 28rpx;
  position: relative;
  overflow: hidden;
  transition: background 0.25s;
}

/* 完整版：朱砂红微光边框 */
.version-card--featured {
  border-color: rgba(178, 58, 52, 0.35);
  background: rgba(178, 58, 52, 0.03);
}

/* 完整版左侧竖线 */
.version-card--featured::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4rpx;
  height: 100%;
  background: linear-gradient(180deg, var(--zen-cinnabar) 0%, var(--zen-gold) 100%);
}

.version-card-hover {
  background: rgba(178, 58, 52, 0.04) !important;
}

/* 推荐角标 */
.featured-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--zen-cinnabar);
  padding: 8rpx 20rpx;
  border-bottom-left-radius: 8rpx;
}

.featured-badge-text {
  font-size: 18rpx;
  color: #fff;
  letter-spacing: 0.15em;
}

/* 图标区 */
.version-icon-wrap {
  flex-shrink: 0;
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, 0.05);
}

.version-icon-wrap--featured {
  border-color: rgba(178, 58, 52, 0.25);
  background: rgba(178, 58, 52, 0.06);
}

.version-icon {
  font-size: 44rpx;
  font-weight: 200;
  color: var(--zen-accent);
}

.version-icon--featured {
  color: var(--zen-cinnabar);
}

/* 卡片文字区 */
.version-card-body {
  flex: 1;
  min-width: 0;
}

.version-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 14rpx;
}

.version-tag {
  font-size: 18rpx;
  color: var(--zen-gray);
  background: rgba(142, 142, 147, 0.08);
  padding: 4rpx 14rpx;
  border-radius: 20rpx;
  letter-spacing: 0.05em;
}

.version-tag--featured {
  color: var(--zen-cinnabar);
  background: rgba(178, 58, 52, 0.08);
}

.version-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 34rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.05em;
  margin-bottom: 10rpx;
}

.version-sub {
  font-size: 22rpx;
  color: var(--zen-muted);
  letter-spacing: 0.03em;
  line-height: 1.5;
}

/* 箭头 */
.version-arrow {
  flex-shrink: 0;
  color: var(--zen-gray);
}

.version-arrow--featured {
  color: var(--zen-cinnabar);
}

.version-arrow .material-symbols-outlined,
.version-arrow--featured .material-symbols-outlined {
  font-size: 40rpx;
  font-weight: 200;
}

/* 底部提示 */
.select-footer {
  display: flex;
  justify-content: center;
  padding-top: 40rpx;
}

.select-footer-text {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.2em;
}

/* 继续上次进度卡片 */
.resume-card {
  display: flex;
  align-items: center;
  gap: 28rpx;
  padding: 36rpx 36rpx;
  background: rgba(212, 175, 55, 0.06);
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 4rpx;
  margin-bottom: 28rpx;
  position: relative;
  overflow: hidden;
  transition: background 0.25s;
}

.resume-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4rpx;
  height: 100%;
  background: linear-gradient(180deg, var(--zen-gold) 0%, var(--zen-accent) 100%);
}

.resume-card-hover {
  background: rgba(212, 175, 55, 0.1) !important;
}

.resume-card-left {
  flex-shrink: 0;
}

.resume-icon {
  font-size: 44rpx;
  font-weight: 200;
  color: var(--zen-gold);
}

.resume-card-body {
  flex: 1;
  min-width: 0;
}

.resume-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.05em;
  margin-bottom: 8rpx;
}

.resume-sub {
  font-size: 22rpx;
  color: var(--zen-accent);
  letter-spacing: 0.05em;
}

.resume-arrow {
  flex-shrink: 0;
  color: var(--zen-gold);
}

.resume-arrow .material-symbols-outlined {
  font-size: 40rpx;
  font-weight: 200;
}

/* ══════════════════════════════════════
   答题界面
══════════════════════════════════════ */

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

/* 已答但非当前选中态（回退后显示历史选择） */
.option-item.answered {
  border-color: rgba(178, 58, 52, 0.3);
  background: rgba(178, 58, 52, 0.04);
}

.option-item.answered::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4rpx;
  height: 100%;
  background: rgba(178, 58, 52, 0.5);
}

.option-item.answered .option-indicator {
  border-color: rgba(178, 58, 52, 0.4);
  background: rgba(178, 58, 52, 0.06);
}

.option-item.answered .option-letter {
  color: rgba(178, 58, 52, 0.7);
}

.option-item.answered .option-label {
  color: var(--zen-ink);
}

.option-item.answered .check-icon {
  color: rgba(178, 58, 52, 0.6);
}

.option-item.selected::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4rpx;
  height: 100%;
  background: var(--zen-cinnabar);
}

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

.option-item.selected .option-letter {
  color: var(--zen-cinnabar);
}

.option-label {
  flex: 1;
  font-size: 28rpx;
  line-height: 1.65;
  color: rgba(51, 51, 51, 0.7);
  letter-spacing: 0.03em;
  transition: color 0.25s;
}

.option-item.selected .option-label {
  color: var(--zen-ink);
}

.option-check {
  flex-shrink: 0;
}

.check-icon {
  font-size: 32rpx;
  color: var(--zen-cinnabar);
  font-weight: 300;
}

/* ── 操作按钮 ── */
.action-section {
  margin-bottom: 60rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  height: 100rpx;
  border-radius: 4rpx;
  transition: opacity 0.2s;
}

.action-btn--next {
  background: var(--zen-surface);
  border: 1px solid rgba(212, 175, 55, 0.3);
}

.action-btn--result {
  background: var(--zen-cinnabar);
  border: none;
}

.action-btn-hover {
  opacity: 0.75;
}

.action-btn-text {
  font-size: 28rpx;
  letter-spacing: 0.15em;
  font-weight: 300;
}

.action-btn--next .action-btn-text {
  color: var(--zen-ink);
}

.action-btn--result .action-btn-text {
  color: #fff;
}

.action-btn-icon {
  font-size: 32rpx;
  font-weight: 200;
}

.action-btn--next .action-btn-icon {
  color: var(--zen-accent);
}

.action-btn--result .action-btn-icon {
  color: rgba(255, 255, 255, 0.8);
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

.prev-btn-hover {
  opacity: 0.5;
}

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
