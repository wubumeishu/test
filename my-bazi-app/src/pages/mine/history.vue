<template>
  <view class="page-container">
    <ZenHeader title="测算历史" :show-back="true" />

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">

      <!-- 加载中 -->
      <view v-if="isLoading" class="loading-state">
        <text class="loading-text">正在加载历史记录…</text>
      </view>

      <!-- 空状态 -->
      <view v-else-if="mergedList.length === 0" class="empty-state">
        <text class="material-symbols-outlined empty-icon">history_edu</text>
        <text class="empty-title">暂无测算记录</text>
        <text class="empty-desc">完成一次排盘或 MBTI 测试后，记录将在此显示</text>
      </view>

      <!-- 记录列表 -->
      <view v-else class="list-body">
        <view
          v-for="item in mergedList"
          :key="item.id"
          class="record-card"
          :class="`record-card--${item.type}`"
          hover-class="record-card-hover"
          @click="goToDetail(item)"
        >
          <!-- 左侧类型色条 -->
          <view class="card-stripe" :class="`card-stripe--${item.type}`"></view>

          <view class="card-body">
            <!-- 顶部：类型标签 + 时间 -->
            <view class="card-header">
              <view class="type-tag" :class="`type-tag--${item.type}`">
                <text class="material-symbols-outlined tag-icon">{{ typeIcon(item.type) }}</text>
                <text class="tag-text">{{ typeLabel(item.type) }}</text>
              </view>
              <text class="card-time">{{ item.timeStr }}</text>
            </view>

            <!-- 核心摘要 -->
            <view class="card-summary">
              <!-- 八字：姓名 + 八字简码 -->
              <template v-if="item.type === 'bazi'">
                <text class="summary-name">{{ item.name }}</text>
                <text class="summary-sub">{{ item.baziStr }}</text>
              </template>
              <!-- MBTI：类型字母 + 称号 -->
              <template v-else-if="item.type === 'mbti'">
                <text class="summary-name summary-name--mbti">{{ item.mbtiType }}</text>
                <text class="summary-sub">{{ item.mbtiTitle }}</text>
              </template>
              <!-- 塔罗：问题摘要 + 三张牌名 -->
              <template v-else-if="item.type === 'tarot'">
                <text class="summary-name summary-name--tarot">🌙 {{ item.tarotTitle }}</text>
                <text class="summary-sub summary-sub--question">心中的困惑：{{ item.tarotQuestion }}</text>
                <text class="summary-sub" v-if="item.tarotCards?.length === 3">
                  {{ ['过去', '现在', '未来'].map((pos, i) => `${pos}·${majorArcana[item.tarotCards![i]]?.name ?? '?'}`).join('　') }}
                </text>
              </template>
              <!-- 兜底 -->
              <template v-else>
                <text class="summary-name">{{ item.name }}</text>
              </template>
            </view>
          </view>

          <!-- 右侧箭头 -->
          <text class="material-symbols-outlined card-arrow">chevron_right</text>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { get } from '@/utils/request'
import { useBaziStore } from '@/store/useBaziStore'
import type { BaziCalculateResponse } from '@/store/useBaziStore'
import { mbtiDict } from '@/data/mbtiDict'
import { majorArcana } from '@/data/tarot'

const baziStore = useBaziStore()

// ── 统一记录类型 ──
type RecordType = 'bazi' | 'mbti' | 'tarot'

interface HistoryItem {
  id: string
  type: RecordType
  timeStr: string        // 格式化时间
  rawTime: number        // 用于排序的时间戳
  // 八字专属
  name?: string
  baziStr?: string
  rawBazi?: BaziCalculateResponse
  // MBTI 专属
  mbtiType?: string
  mbtiTitle?: string
  rawMbti?: any
  // 塔罗专属
  tarotQuestion?: string   // 用户提问
  tarotTitle?: string      // 阵型名称，如「塔罗·命运圣三角」
  tarotCards?: number[]    // [过去, 现在, 未来] majorArcana 索引
}

// ── 工具：兼容有无 uni- 前缀的 storage 读取 ──
// H5 下 uni.setStorageSync 会加 uni- 前缀，但旧数据可能是直接用 localStorage 写的（无前缀）
const getStorage = (key: string): any => {
  const v = uni.getStorageSync(key)  // 读 uni-{key}
  if (v !== '' && v !== null && v !== undefined) return v
  // 兜底：尝试直接读无前缀的 key
  try {
    const raw = localStorage.getItem(key)
    if (raw === null || raw === '') return null
    try { return JSON.parse(raw) } catch { return raw }
  } catch { return null }
}

// ── 工具函数 ──
const typeLabel = (type: RecordType) => {
  const map: Record<RecordType, string> = { bazi: '八字排盘', mbti: 'MBTI', tarot: '塔罗占卜' }
  return map[type] ?? '测算'
}

const typeIcon = (type: RecordType) => {
  const map: Record<RecordType, string> = { bazi: 'view_quilt', mbti: 'psychology', tarot: 'style' }
  return map[type] ?? 'auto_awesome'
}

const formatTime = (ts: number | string): { str: string; stamp: number } => {
  const d = typeof ts === 'number' ? new Date(ts) : new Date(ts)
  const stamp = d.getTime()
  const pad = (n: number) => String(n).padStart(2, '0')
  const str = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  return { str, stamp }
}

// ── 加载数据 ──
const loadHistory = async () => {
  isLoading.value = true
  const items: HistoryItem[] = []

  // 1. 从后端拉取八字记录
  try {
    const res = await get<{ total: number; records: any[] }>('/api/fortune/records?limit=50&offset=0')
    for (const r of res.records ?? []) {
      const { str, stamp } = formatTime(r.created_at ?? Date.now())
      const resolvedName = r.name ?? r.five_elements_json?.name ?? r.bazi_json?.name ?? '未知'
      items.push({
        id:      r.record_id,
        type:    'bazi',
        timeStr: str,
        rawTime: stamp,
        name:    resolvedName,
        baziStr: r.bazi_str ?? '',
        rawBazi: { ...r, name: resolvedName },
      })
    }
  } catch (e) {
    console.warn('⚠️ [history] 获取八字记录失败:', e)
  }

  // 2. 从本地缓存读取 MBTI 记录（兼容有无 uni- 前缀）
  try {
    const mbtiRaw = getStorage('mbti_result')
    console.log('📦 [history] mbti_result:', JSON.stringify(mbtiRaw))
    if (mbtiRaw && typeof mbtiRaw === 'object' && mbtiRaw.type) {
      const info = mbtiDict[mbtiRaw.type]
      const { str, stamp } = formatTime(mbtiRaw.timestamp ?? Date.now())
      items.push({
        id:        `mbti-${stamp}`,
        type:      'mbti',
        timeStr:   str,
        rawTime:   stamp,
        mbtiType:  mbtiRaw.type,
        mbtiTitle: info?.title ?? '',
        rawMbti:   mbtiRaw,
      })
    }
  } catch (e) {
    console.warn('⚠️ [history] 读取 MBTI 缓存失败:', e)
  }

  // 3. 从本地缓存读取塔罗历史记录（兼容有无 uni- 前缀）
  try {
    const tarotRaw = getStorage('tarot_history')
    const tarotHistory: Array<{
      id: string; title?: string; question: string; cards: number[]; createdAt: number
    }> = Array.isArray(tarotRaw) ? tarotRaw : []
    console.log('📦 [history] tarot_history 条数:', tarotHistory.length)

    for (const r of tarotHistory) {
      if (!r.question || !Array.isArray(r.cards) || r.cards.length < 3) continue
      const { str, stamp } = formatTime(r.createdAt ?? Date.now())
      items.push({
        id:            r.id,
        type:          'tarot',
        timeStr:       str,
        rawTime:       stamp,
        tarotTitle:    r.title || '塔罗·命运圣三角',
        tarotQuestion: r.question,
        tarotCards:    r.cards,
      })
    }
  } catch (e) {
    console.warn('⚠️ [history] 读取塔罗缓存失败:', e)
  }

  // 4. 按时间倒序合并
  mergedList.value = items.sort((a, b) => b.rawTime - a.rawTime)
  isLoading.value  = false
}

// ── 点击跳转 ──
const goToDetail = (item: HistoryItem) => {
  if (item.type === 'bazi') {
    if (item.rawBazi) {
      baziStore.restoreHistoryData(item.rawBazi, item.name)
    }
    uni.navigateTo({ url: '/pages/result/result' })

  } else if (item.type === 'mbti') {
    uni.setStorageSync('mbti_result', item.rawMbti)
    uni.navigateTo({ url: '/pages/questions/mbti-result' })

  } else if (item.type === 'tarot') {
    // 携带 isHistory=true 和 historyId，结果页会从 tarot_history 中查找对应记录
    uni.navigateTo({
      url: `/pages/questions/tarot-result?isHistory=true&historyId=${item.id}`
    })
  }
}

onShow(() => { loadHistory() })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

.page-container {
  --zen-bg:       #F9F6F1;
  --zen-ink:      #1A1A1A;
  --zen-gray:     #8E8E93;
  --zen-border:   rgba(212, 175, 55, 0.15);
  --zen-surface:  rgba(255, 255, 255, 0.75);
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

.scroll-body {
  height: calc(100vh - 140rpx);
}

/* ── 加载 / 空状态 ── */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 60rpx;
  gap: 24rpx;
}

.loading-text {
  font-size: 26rpx;
  color: var(--zen-muted);
  letter-spacing: 0.1em;
}

.empty-icon {
  font-size: 100rpx;
  color: rgba(212, 175, 55, 0.3);
  font-weight: 200;
}

.empty-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  color: var(--zen-muted);
  letter-spacing: 0.1em;
}

.empty-desc {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.35);
  letter-spacing: 0.05em;
  text-align: center;
  line-height: 1.7;
}

/* ── 列表 ── */
.list-body {
  padding: 32rpx 40rpx 0;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

/* ── 记录卡片 ── */
.record-card {
  display: flex;
  align-items: center;
  background: var(--zen-surface);
  border: 1px solid var(--zen-border);
  border-radius: 4rpx;
  overflow: hidden;
  position: relative;
  transition: opacity 0.2s;
}

.record-card-hover {
  opacity: 0.75;
}

/* 左侧色条 */
.card-stripe {
  width: 6rpx;
  align-self: stretch;
  flex-shrink: 0;
}

.card-stripe--bazi  { background: linear-gradient(180deg, var(--zen-gold) 0%, var(--zen-accent) 100%); }
.card-stripe--mbti  { background: linear-gradient(180deg, var(--zen-cinnabar) 0%, #E8704A 100%); }
.card-stripe--tarot { background: linear-gradient(180deg, #7B68EE 0%, #9B59B6 100%); }

.card-body {
  flex: 1;
  padding: 32rpx 28rpx;
  min-width: 0;
}

/* 顶部：标签 + 时间 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18rpx;
}

.type-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  border: 1px solid;
}

.type-tag--bazi  { border-color: rgba(212, 175, 55, 0.4);  background: rgba(212, 175, 55, 0.07); }
.type-tag--mbti  { border-color: rgba(178, 58, 52, 0.35);  background: rgba(178, 58, 52, 0.06); }
.type-tag--tarot { border-color: rgba(123, 104, 238, 0.35); background: rgba(123, 104, 238, 0.06); }

.tag-icon {
  font-size: 24rpx;
  font-weight: 200;
}

.type-tag--bazi  .tag-icon { color: var(--zen-gold); }
.type-tag--mbti  .tag-icon { color: var(--zen-cinnabar); }
.type-tag--tarot .tag-icon { color: #7B68EE; }

.tag-text {
  font-size: 20rpx;
  letter-spacing: 0.08em;
  font-weight: 400;
}

.type-tag--bazi  .tag-text { color: var(--zen-accent); }
.type-tag--mbti  .tag-text { color: var(--zen-cinnabar); }
.type-tag--tarot .tag-text { color: #7B68EE; }

.card-time {
  font-size: 20rpx;
  color: var(--zen-muted);
  letter-spacing: 0.03em;
  flex-shrink: 0;
}

/* 摘要 */
.card-summary {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.summary-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 30rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 0.05em;
}

/* MBTI 类型字母用渐变色 */
.summary-name--mbti {
  background: linear-gradient(135deg, var(--zen-cinnabar) 0%, var(--zen-gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 34rpx;
  font-weight: 700;
  letter-spacing: 0.15em;
}

/* 塔罗问题：截断省略 */
.summary-name--tarot {
  font-size: 26rpx;
  font-weight: 400;
  color: #7B68EE;
  letter-spacing: 0.04em;
  /* 超长问题截断 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

/* 塔罗「心中的困惑：」行 */
.summary-sub--question {
  font-size: 24rpx;
  color: rgba(123, 104, 238, 0.7);
  letter-spacing: 0.04em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.summary-sub {
  font-size: 24rpx;
  color: var(--zen-muted);
  letter-spacing: 0.05em;
  line-height: 1.5;
}

/* 右侧箭头 */
.card-arrow {
  font-size: 36rpx;
  color: rgba(142, 142, 147, 0.5);
  font-weight: 200;
  padding-right: 24rpx;
  flex-shrink: 0;
}

.safe-bottom {
  height: 120rpx;
}
</style>
