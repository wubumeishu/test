<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="" :show-back="true" />

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">

      <!-- ══════════════════════════════════════
           沉浸式结果视图
      ══════════════════════════════════════ -->

      <!-- 中心呼吸光晕 -->
      <view class="breath-orb"></view>

      <!-- 顶部小字 -->
      <view class="result-eyebrow-wrap">
        <text class="result-eyebrow">灵魂印记</text>
        <view class="eyebrow-line"></view>
      </view>

      <!-- 核心编码 -->
      <view class="result-core">
        <text class="result-base-type">{{ baseType }}</text>
        <view class="result-dash-wrap">
          <view class="result-dash"></view>
        </view>
        <text class="result-suffix">{{ typeAO }}{{ typeHC }}</text>
      </view>

      <!-- 性格标签 -->
      <view class="result-tag-wrap">
        <view class="result-tag">
          <text class="result-tag-text">{{ suffixLabel }}</text>
        </view>
      </view>

      <!-- 戳心文案 -->
      <view class="result-insight-wrap">
        <text class="result-insight-text">{{ insightText }}</text>
      </view>

      <!-- 维度解析卡片 -->
      <view class="dim-cards-wrap">

        <!-- AO 卡片 -->
        <view class="dim-card">
          <view class="dim-card-header">
            <text class="material-symbols-outlined dim-card-icon">{{ typeAO === 'A' ? 'bolt' : 'psychology' }}</text>
            <text class="dim-card-title">{{ typeAO === 'A' ? 'A · 果断行动' : 'O · 深度思虑' }}</text>
          </view>
          <text class="dim-card-text">{{ aoDetail }}</text>
        </view>

        <!-- HC 卡片 -->
        <view class="dim-card">
          <view class="dim-card-header">
            <text class="material-symbols-outlined dim-card-icon">{{ typeHC === 'H' ? 'favorite_border' : 'shield' }}</text>
            <text class="dim-card-title">{{ typeHC === 'H' ? 'H · 温暖亲和' : 'C · 冷静独立' }}</text>
          </view>
          <text class="dim-card-text">{{ hcDetail }}</text>
        </view>

      </view>

      <!-- 禅意建议 -->
      <view class="zen-wrap">
        <text class="zen-symbol">✦</text>
        <text class="zen-text">{{ zenAdvice }}</text>
        <text class="zen-symbol">✦</text>
      </view>

      <!-- 操作按钮 -->
      <view class="action-wrap">
        <view class="action-btn action-btn--share" hover-class="btn-hover" @click="openShareModal">
          <text class="material-symbols-outlined btn-icon">share</text>
          <text class="btn-text">生成分享海报</text>
        </view>
        <view class="action-btn action-btn--home" hover-class="btn-hover" @click="goHome">
          <text class="material-symbols-outlined btn-icon">home</text>
          <text class="btn-text">返回大厅</text>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- ══════════════════════════════════════
         分享海报模态框
    ══════════════════════════════════════ -->
    <view v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
      <view class="modal-content">

        <!-- 海报卡片 -->
        <view class="poster-card" id="shareCard">

          <!-- 海报顶部装饰 -->
          <view class="poster-top-bar">
            <view class="poster-top-line"></view>
            <text class="poster-top-symbol">✦</text>
            <view class="poster-top-line"></view>
          </view>

          <!-- 海报眉题 -->
          <text class="poster-eyebrow">我的灵魂印记 · 64 型人格</text>

          <!-- 海报核心编码 -->
          <view class="poster-core">
            <text class="poster-base">{{ baseType }}</text>
            <text class="poster-sep">—</text>
            <text class="poster-suffix">{{ typeAO }}{{ typeHC }}</text>
          </view>

          <!-- 海报标签 -->
          <view class="poster-tag">
            <text class="poster-tag-text">{{ suffixLabel }}</text>
          </view>

          <!-- 海报文案 -->
          <text class="poster-insight">{{ insightText }}</text>

          <!-- 海报分隔线 -->
          <view class="poster-divider">
            <view class="poster-divider-line"></view>
          </view>

          <!-- 海报底部营销区 -->
          <view class="poster-footer">
            <view class="poster-qr">
              <text class="material-symbols-outlined poster-qr-icon">qr_code_2</text>
            </view>
            <view class="poster-brand-wrap">
              <text class="poster-brand">云水禅心</text>
              <text class="poster-slogan">遇见更真实的自己</text>
            </view>
          </view>

        </view>

        <!-- 模态框操作 -->
        <view class="modal-actions">
          <view class="modal-btn modal-btn--save" hover-class="btn-hover" @click="savePoster">
            <text class="material-symbols-outlined btn-icon">download</text>
            <text class="btn-text">保存海报到相册</text>
          </view>
          <view class="modal-btn modal-btn--close" hover-class="btn-hover" @click="showShareModal = false">
            <text class="btn-text">关闭</text>
          </view>
        </view>

      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'

// ── 状态 ──
const baseType       = ref('????')
const fullType       = ref('????-??')
const typeAO         = ref<'A' | 'O'>('A')
const typeHC         = ref<'H' | 'C'>('H')
const showShareModal = ref(false)

// ── 读取 Storage ──
onLoad(() => {
  try {
    const stored = uni.getStorageSync('mbti_advanced_result')
    if (!stored) {
      uni.showToast({ title: '暂无测试结果', icon: 'none' })
      return
    }
    baseType.value = stored.baseType ?? '????'
    fullType.value = stored.fullType ?? '????-??'
    typeAO.value   = stored.typeAO   ?? 'A'
    typeHC.value   = stored.typeHC   ?? 'H'
  } catch {
    uni.showToast({ title: '数据读取失败', icon: 'none' })
  }
})

// ── 后缀组合标签字典 ──
const suffixLabelMap: Record<string, string> = {
  AH: '果断 · 温暖',
  AC: '果断 · 高冷',
  OH: '纠结 · 温暖',
  OC: '表面高冷，内心疯狂纠结',
}

const suffixLabel = computed(() => suffixLabelMap[`${typeAO.value}${typeHC.value}`] ?? '')

// ── 戳心文案 ──
const insightText = computed(() => {
  const ao = typeAO.value
  const hc = typeHC.value
  const base = baseType.value
  if (ao === 'A' && hc === 'H') return `${base} 的你，行动果断，从不在原地踏步，同时以温暖的方式与世界连接。这是你最真实的灵魂底色。`
  if (ao === 'A' && hc === 'C') return `${base} 的你，行动果断，从不在原地踏步，却在人群中戴着一副高冷的面具。内心的温柔只留给真正懂你的人。`
  if (ao === 'O' && hc === 'H') return `作为 ${base}，你本该运筹帷幄，却总在深夜反复推演每一个细节。你用温暖包裹着内心的不安，是最容易被误解的灵魂。`
  return `作为 ${base}，你本该运筹帷幄，但 OC 面具让你在深夜独自精神内耗，却在人群中戴着一副高冷的面具。没有人知道你脑海里正在上演什么剧场。`
})

// ── AO 维度解析 ──
const aoDetail = computed(() => typeAO.value === 'A'
  ? '你是天生的行动派。面对不确定性，你倾向于先动起来再说，用行动消解焦虑。这种特质让你在快节奏的环境中如鱼得水，但也要注意偶尔放慢脚步，给深度思考留出空间。'
  : '你是深度思考者。在做决定前，你需要充分的信息和内心的确认。这种谨慎让你的决策质量更高，但过度的反刍有时会消耗你的精力。学会在"足够好"时果断出手，是你的成长方向。'
)

// ── HC 维度解析 ──
const hcDetail = computed(() => typeHC.value === 'H'
  ? '你天生散发温暖。你善于感知他人的情绪，并本能地想要靠近和帮助。这种特质让你在人际关系中备受喜爱，但也要注意设立边界，避免因过度付出而耗尽自己。'
  : '你是独立的冷静者。你重视个人空间，不轻易向他人敞开心扉，但一旦信任建立，你的忠诚度极高。偶尔主动释放一点温度，会让关系更加丰盈。'
)

// ── 禅意建议 ──
const zenAdvice = computed(() => {
  const ao = typeAO.value === 'A' ? '行者无疆，但偶尔驻足，方能看清来路与去处。' : '思深者远，但思而不行，终是纸上谈兵。'
  const hc = typeHC.value === 'H' ? '温柔是力量，但先温柔地对待自己。' : '独立是自由，但偶尔放下铠甲，才能真正被人看见。'
  return `${ao} ${hc}`
})

// ── 打开海报模态框 ──
const openShareModal = () => {
  showShareModal.value = true
}

// ── 保存海报（预留） ──
const savePoster = () => {
  uni.showToast({ title: '海报生成中...', icon: 'loading', duration: 1500 })
}

// ── 返回大厅 ──
const goHome = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style scoped>
/* 页面样式 */

/* ══════════════════════════════════════
   全局：禅意米白主题（与项目一致）
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
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
  position: relative;
}

.scroll-body {
  height: calc(100vh - 140rpx);
  position: relative;
  z-index: 1;
}

/* ── 中心呼吸光晕（浅色版） ── */
.breath-orb {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 700rpx;
  height: 700rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(178, 58, 52, 0.05) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
  animation: breathe 5s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50%       { opacity: 1;   transform: translate(-50%, -50%) scale(1.12); }
}

/* ══════════════════════════════════════
   沉浸式结果视图
══════════════════════════════════════ */

/* 眉题 */
.result-eyebrow-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80rpx;
  margin-bottom: 60rpx;
}

.result-eyebrow {
  font-size: 20rpx;
  color: rgba(212, 175, 55, 0.7);
  letter-spacing: 0.5em;
  font-weight: 300;
  margin-bottom: 20rpx;
}

.eyebrow-line {
  width: 60rpx;
  height: 1px;
  background: rgba(212, 175, 55, 0.25);
}

/* 核心编码 */
.result-core {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 48rpx;
  padding: 0 40rpx;
}

.result-base-type {
  font-family: 'Noto Serif SC', serif;
  font-size: 100rpx;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--zen-ink);
  line-height: 1;
}

.result-dash-wrap {
  padding: 0 20rpx;
  display: flex;
  align-items: center;
}

.result-dash {
  width: 40rpx;
  height: 2rpx;
  background: rgba(212, 175, 55, 0.4);
}

/* 后缀：斜体 + 发光 */
.result-suffix {
  font-family: 'Noto Serif SC', serif;
  font-size: 100rpx;
  font-weight: 900;
  letter-spacing: 0.06em;
  line-height: 1;
  font-style: italic;
  background: linear-gradient(135deg, var(--cinnabar) 0%, #E8704A 50%, var(--gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 12rpx rgba(178, 58, 52, 0.2));
}

/* 性格标签 */
.result-tag-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 64rpx;
}

.result-tag {
  padding: 12rpx 40rpx;
  border: 1px solid rgba(178, 58, 52, 0.4);
  border-radius: 40rpx;
  background: rgba(178, 58, 52, 0.06);
}

.result-tag-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: var(--cinnabar);
  letter-spacing: 0.1em;
  font-weight: 500;
}

/* 戳心文案 */
.result-insight-wrap {
  padding: 0 64rpx;
  margin-bottom: 80rpx;
}

.result-insight-text {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: var(--zen-muted);
  line-height: 2.1;
  letter-spacing: 0.05em;
  text-align: center;
}

/* 维度解析卡片 */
.dim-cards-wrap {
  padding: 0 40rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 80rpx;
}

.dim-card {
  padding: 44rpx 40rpx;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.dim-card-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.dim-card-icon {
  font-size: 32rpx;
  font-weight: 200;
  color: var(--gold);
}

.dim-card-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.08em;
}

.dim-card-text {
  font-size: 24rpx;
  color: var(--zen-muted);
  line-height: 2;
  letter-spacing: 0.04em;
}

/* 禅意建议 */
.zen-wrap {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 20rpx;
  padding: 0 64rpx;
  margin-bottom: 80rpx;
}

.zen-symbol {
  font-size: 18rpx;
  color: rgba(212, 175, 55, 0.4);
  margin-top: 8rpx;
  flex-shrink: 0;
}

.zen-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  color: var(--zen-muted);
  line-height: 2;
  letter-spacing: 0.06em;
  text-align: center;
}

/* 操作按钮 */
.action-wrap {
  padding: 0 40rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.action-btn {
  width: 100%;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  border-radius: 4rpx;
  transition: opacity 0.2s;
}

.action-btn--share {
  background: var(--cinnabar);
  border: none;
}

.action-btn--home {
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
}

.btn-hover { opacity: 0.75; }

.btn-icon { font-size: 30rpx; font-weight: 200; }
.action-btn--share .btn-icon { color: rgba(255, 255, 255, 0.9); }
.action-btn--home  .btn-icon { color: var(--accent); }

.btn-text {
  font-size: 26rpx;
  letter-spacing: 0.15em;
  font-weight: 300;
}

.action-btn--share .btn-text { color: #fff; }
.action-btn--home  .btn-text { color: var(--zen-ink); }

.safe-bottom { height: 120rpx; }

/* ══════════════════════════════════════
   分享海报模态框
══════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
}

.modal-content {
  width: 100%;
  max-width: 640rpx;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

/* 海报卡片 */
.poster-card {
  background: #F9F6F1;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 16rpx;
  padding: 52rpx 48rpx 44rpx;
  box-shadow:
    0 0 0 1px rgba(178, 58, 52, 0.08),
    0 40rpx 80rpx rgba(0, 0, 0, 0.12);
}

/* 海报顶部装饰 */
.poster-top-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 36rpx;
}

.poster-top-line {
  flex: 1;
  height: 1px;
  background: rgba(212, 175, 55, 0.25);
}

.poster-top-symbol {
  font-size: 16rpx;
  color: rgba(212, 175, 55, 0.5);
}

/* 海报眉题 */
.poster-eyebrow {
  display: block;
  font-size: 18rpx;
  color: rgba(166, 139, 103, 0.7);
  letter-spacing: 0.3em;
  font-weight: 300;
  text-align: center;
  margin-bottom: 40rpx;
}

/* 海报核心编码 */
.poster-core {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.poster-base {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 700;
  color: #1A1A1A;
  letter-spacing: 0.06em;
  line-height: 1;
}

.poster-sep {
  font-size: 40rpx;
  color: rgba(212, 175, 55, 0.4);
  font-weight: 200;
}

.poster-suffix {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 900;
  font-style: italic;
  letter-spacing: 0.06em;
  line-height: 1;
  background: linear-gradient(135deg, var(--cinnabar) 0%, #E8704A 50%, var(--gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 8rpx rgba(178, 58, 52, 0.15));
}

/* 海报标签 */
.poster-tag {
  display: flex;
  justify-content: center;
  margin-bottom: 36rpx;
}

.poster-tag-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 22rpx;
  color: var(--cinnabar);
  letter-spacing: 0.1em;
  padding: 8rpx 28rpx;
  border: 1px solid rgba(178, 58, 52, 0.35);
  border-radius: 30rpx;
  background: rgba(178, 58, 52, 0.06);
}

/* 海报文案 */
.poster-insight {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 22rpx;
  color: rgba(51, 51, 51, 0.55);
  line-height: 2;
  letter-spacing: 0.04em;
  text-align: center;
  margin-bottom: 40rpx;
}

/* 海报分隔线 */
.poster-divider {
  margin-bottom: 32rpx;
}

.poster-divider-line {
  height: 1px;
  background: rgba(212, 175, 55, 0.2);
}

/* 海报底部营销区 */
.poster-footer {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.poster-qr {
  width: 72rpx;
  height: 72rpx;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, 0.06);
  flex-shrink: 0;
}

.poster-qr-icon {
  font-size: 40rpx;
  font-weight: 200;
  color: rgba(212, 175, 55, 0.5);
}

.poster-brand-wrap {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.poster-brand {
  font-family: 'Noto Serif SC', serif;
  font-size: 22rpx;
  color: rgba(166, 139, 103, 0.8);
  letter-spacing: 0.15em;
}

.poster-slogan {
  font-size: 18rpx;
  color: rgba(51, 51, 51, 0.3);
  letter-spacing: 0.1em;
}

/* 模态框操作按钮 */
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.modal-btn {
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  border-radius: 4rpx;
  transition: opacity 0.2s;
}

.modal-btn--save {
  background: var(--cinnabar);
  border: none;
}

.modal-btn--close {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.modal-btn--save .btn-icon { color: #fff; font-size: 30rpx; font-weight: 200; }
.modal-btn--save .btn-text { color: #fff; font-size: 26rpx; letter-spacing: 0.15em; font-weight: 300; }
.modal-btn--close .btn-text { color: rgba(51, 51, 51, 0.6); font-size: 24rpx; letter-spacing: 0.15em; font-weight: 300; }
</style>
