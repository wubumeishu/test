<template>
  <view class="page-container">
    <!-- 加载状态 -->
    <view v-if="baziStore.isLoading" class="loading-container">
      <view class="loading-content">
        <view class="zen-circle">
          <view class="circle-outer"></view>
          <view class="circle-inner"></view>
        </view>
        <text class="loading-text">天机推演中</text>
        <view class="loading-dots">
          <view class="dot"></view>
          <view class="dot"></view>
          <view class="dot"></view>
        </view>
      </view>
    </view>

    <!-- 结果展示 -->
    <view v-else-if="baziStore.currentBaziData" class="result-container">
      <!-- 顶部信息栏 -->
      <view class="header-bar">
        <view class="back-button" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <view class="header-info">
          <text class="name-text" :style="nameLetterSpacing">{{ displayName }}</text>
          <text class="gender-text">{{ genderText }}</text>
        </view>
      </view>

      <!-- 基础信息卡片 -->
      <view class="info-card glass-card">
        <view class="info-row">
          <text class="info-label">公历</text>
          <text class="info-value">{{ baziStore.currentBaziData.solar_date }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">农历</text>
          <text class="info-value">{{ baziStore.currentBaziData.lunar_date }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">生肖</text>
          <text class="info-value">{{ baziStore.currentBaziData.shengxiao }}</text>
        </view>
      </view>

      <!-- 核心命盘矩阵 -->
      <view class="bazi-matrix glass-card">
        <view class="matrix-title">
          <view class="title-line"></view>
          <text class="title-text">命盘八字</text>
          <view class="title-line"></view>
        </view>

        <view class="pillars-container">
          <view 
            v-for="(pillar, index) in pillarList" 
            :key="index"
            class="pillar-column"
            :class="{ 'pillar-day': pillar.isDayMaster }"
            :style="{ animationDelay: (index * 0.1) + 's' }"
          >
            <!-- 柱子标题 -->
            <view class="pillar-header">
              <text class="pillar-label">{{ pillar.title }}</text>
            </view>
            
            <!-- 十神 -->
            <view class="cell shishen-cell" :class="{ 'day-master-label': pillar.isDayMaster }">
              <text 
                class="shishen-text" 
                :class="{ 'highlight': pillar.isDayMaster }"
                @tap="handleTermClick(pillar.shishen)"
              >
                {{ pillar.shishen }}
              </text>
            </view>
            
            <!-- 天干 -->
            <view class="cell gan-cell">
              <text 
                class="gan-text" 
                :class="{ 'highlight': pillar.isDayMaster }"
                :style="{ color: getWuxingColor(pillar.gan) }"
              >
                {{ pillar.gan }}
              </text>
            </view>
            
            <!-- 地支 -->
            <view class="cell zhi-cell">
              <text 
                class="zhi-text"
                :style="{ color: getWuxingColor(pillar.zhi) }"
              >
                {{ pillar.zhi }}
              </text>
            </view>
            
            <!-- 藏干 + 藏干十神 -->
            <view class="cell canggan-cell">
              <view class="canggan-box">
                <view 
                  v-for="(cg, cgIndex) in pillar.canggan" 
                  :key="'cg' + cgIndex"
                  class="cg-item"
                >
                  <text 
                    class="cg-text"
                    :style="{ color: getWuxingColor(cg) }"
                  >
                    {{ cg }}
                  </text>
                  <text 
                    class="cg-ss"
                    @tap="handleTermClick(pillar.canggan_shishen[cgIndex])"
                  >
                    {{ pillar.canggan_shishen[cgIndex] || '-' }}
                  </text>
                </view>
                <view v-if="pillar.canggan.length === 0" class="cg-item">
                  <text class="cg-text">-</text>
                </view>
              </view>
            </view>
            
            <!-- 十二长生 -->
            <view class="cell changsheng-cell">
              <text class="changsheng-text">{{ pillar.changsheng }}</text>
            </view>
            
            <!-- 纳音 -->
            <view class="cell nayin-cell">
              <text 
                class="nayin-text"
                @tap="handleTermClick(pillar.nayin)"
              >
                {{ pillar.nayin }}
              </text>
            </view>
            
            <!-- 神煞 -->
            <view class="cell shensha-cell">
              <view class="shensha-box">
                <template v-if="pillar.shensha && pillar.shensha.length > 0">
                  <text 
                    v-for="(ss, ssIndex) in pillar.shensha" 
                    :key="'ss' + ssIndex" 
                    class="ss-tag"
                    @click="showShenshaDetail(ss)"
                  >
                    {{ ss }}
                  </text>
                </template>
                <text v-else class="ss-empty">-</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 日主信息 -->
      <view class="daymaster-card glass-card">
        <view class="daymaster-content">
          <text class="daymaster-label">日主</text>
          <text 
            class="daymaster-char"
            :style="{ color: getWuxingColor(baziStore.currentBaziData.day_master) }"
          >{{ baziStore.currentBaziData.day_master }}</text>
          <text class="daymaster-wuxing">{{ baziStore.currentBaziData.day_master_wuxing }}命</text>
        </view>
      </view>

      <!-- 五行能量进度条 -->
      <view class="wuxing-energy glass-card">
        <view class="section-title">
          <text class="title-text">五行能量</text>
        </view>
        
        <view class="energy-bars">
          <view 
            v-for="item in wuxingList" 
            :key="item.name"
            class="energy-row"
          >
            <view class="energy-header">
              <text class="energy-name">{{ item.name }}</text>
              <text class="energy-value">{{ item.percent.toFixed(1) }}%</text>
            </view>
            <view class="energy-bar-container">
              <view 
                class="energy-bar" 
                :style="{ 
                  width: item.percent + '%', 
                  backgroundColor: item.color,
                  animationDelay: item.delay
                }"
              ></view>
            </view>
            <text class="energy-count">{{ item.count }}个</text>
          </view>
        </view>
      </view>

      <!-- AI 分析报告 - 每篇独立卡片 -->
      <template v-if="aiReportText || isAiLoading">

        <!-- Loading 状态：正在分析中 -->
        <view v-if="isAiLoading" class="ai-loading-card glass-card">
          <view class="ai-loading-inner">
            <view class="ai-loading-orbit">
              <view class="ai-loading-planet"></view>
            </view>
            <view class="ai-loading-texts">
              <text class="ai-loading-title">{{ aiLoadingHint }}</text>
              <text class="ai-loading-sub">深度报告约需 30-60 秒，请稍候</text>
            </view>
          </view>
          <!-- 已生成部分先展示（running 状态时） -->
          <view v-if="aiReportText" class="ai-partial-hint">
            <text class="ai-partial-text">已生成 {{ aiReportText.length }} 字，持续更新中</text>
          </view>
        </view>

        <!-- 错误提示 -->
        <view v-if="isAiError" class="stream-error-bar">
          <text class="stream-error-text">星路繁忙，请稍后重试</text>
        </view>

        <!-- 篇章卡片（有内容时展示，loading 中也实时展示已生成部分） -->
        <template v-if="parsedAiSections.length > 0">
          <view
            v-for="(section, index) in parsedAiSections"
            :key="index"
            class="ai-section-card glass-card"
          >
            <view class="ai-section-header">
              <view class="ai-section-line"></view>
              <rich-text :nodes="section.title" class="ai-section-title-text"></rich-text>
            </view>
            <rich-text :nodes="section.content" class="ai-rich-text"></rich-text>
          </view>

          <!-- 生成中：末尾光标动效 -->
          <view v-if="isAiLoading" class="stream-cursor-row">
            <view class="stream-cursor"></view>
          </view>
        </template>

        <!-- 尚未生成任何章节时的占位 -->
        <view v-else-if="isAiLoading" class="stream-placeholder glass-card">
          <text class="stream-placeholder-text">正在连接星宿...</text>
          <view class="stream-cursor"></view>
        </view>

      </template>

      <!-- 底部留白 -->
      <view class="bottom-spacer"></view>
    </view>

    <!-- 无数据状态 -->
    <view v-else class="empty-container">
      <view class="empty-content">
        <text class="empty-icon">📜</text>
        <text class="empty-text">暂无排盘数据</text>
        <text class="empty-tip">请先进行八字排盘</text>
        <button class="empty-button" @click="goBack">
          <text class="button-text">返回上页</text>
        </button>
      </view>
    </view>

    <!-- 自定义知识弹窗 -->
    <view v-if="showPopup" class="popup-mask" @tap="showPopup = false" @touchmove.stop.prevent>
      <view class="popup-content">
        <view class="popup-title">{{ popupTitle }}</view>
        <scroll-view class="popup-body" scroll-y>
          <text class="popup-text">{{ popupContent }}</text>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useBaziStore } from '@/store/useBaziStore'
import { useUserStore } from '@/store/useUserStore'

// Store
const baziStore = useBaziStore()
const userStore = useUserStore()

// ── AI 轮询状态（从 store 读取，result.vue 只负责展示和触发）────────────────
// aiReportText：优先展示轮询中的实时内容，完成后用 store 中的持久化数据
const aiReportText = computed(() => {
  // 轮询进行中或已完成，优先用 currentAiReport（实时追加）
  if (baziStore.currentAiReport) return baziStore.currentAiReport
  // 从历史记录进入时，直接用 ai_report
  return baziStore.currentBaziData?.ai_report || ''
})

const isAiLoading = computed(() =>
  baziStore.aiTaskStatus === 'pending' || baziStore.aiTaskStatus === 'running'
)
const isAiDone    = computed(() => baziStore.aiTaskStatus === 'done')
const isAiError   = computed(() => baziStore.aiTaskStatus === 'error')

// ── AI Loading 文案轮播 ───────────────────────────────────────────────────────
const AI_HINTS = [
  '正在沟通星宿，深度解析中...',
  '天干地支，正在排列命盘...',
  '五行能量，正在精密推演...',
  '洞察灵魂底色，请稍候...',
  '流年大运，正在逐一推算...',
  '禅意报告即将呈现...',
]
const aiHintIndex = ref(0)
const aiLoadingHint = computed(() => AI_HINTS[aiHintIndex.value])
let _hintTimer: ReturnType<typeof setInterval> | null = null

watch(isAiLoading, (loading) => {
  if (loading) {
    aiHintIndex.value = 0
    _hintTimer = setInterval(() => {
      aiHintIndex.value = (aiHintIndex.value + 1) % AI_HINTS.length
    }, 4000)
  } else {
    if (_hintTimer) { clearInterval(_hintTimer); _hintTimer = null }
  }
})

// 弹窗状态
const showPopup = ref(false)
const popupTitle = ref('')
const popupContent = ref('')

// 命主姓名：优先取 baseInfo（排盘时已同步），兜底 currentBaziData.name，再兜底「未知」
const displayName = computed(() => {
  return baziStore.baseInfo?.name
    || baziStore.currentBaziData?.name
    || '未知'
})

// 短名字（≤2字）加大字间距，匹配整体排版美学
const nameLetterSpacing = computed(() => {
  const len = displayName.value.length
  if (len <= 1) return { letterSpacing: '20rpx' }
  if (len <= 2) return { letterSpacing: '12rpx' }
  return { letterSpacing: '6rpx' }
})

// 性别文本
const genderText = computed(() => {
  if (!baziStore.currentBaziData) return ''
  return baziStore.currentBaziData.gender === 1 ? '乾造' : '坤造'
})

// 日柱标题：根据性别显示「元男」或「元女」
const dayPillarTitle = computed(() => {
  if (!baziStore.currentBaziData) return '日柱'
  return baziStore.currentBaziData.gender === 1 ? '元男' : '元女'
})

// 四柱列表（按照现代习惯：从左到右 = 年月日时）
const pillarList = computed(() => {
  if (!baziStore.currentBaziData) return []
  
  const data = baziStore.currentBaziData
  
  return [
    {
      title: '年柱',
      gan: data.year_pillar.gan,
      zhi: data.year_pillar.zhi,
      nayin: data.year_pillar.nayin,
      canggan: data.year_pillar.canggan || [],
      shishen: data.year_pillar.shishen || '-',
      changsheng: data.year_pillar.changsheng || '-',
      canggan_shishen: data.year_pillar.canggan_shishen || [],
      shensha: data.year_pillar.shensha || [],
      isDayMaster: false
    },
    {
      title: '月柱',
      gan: data.month_pillar.gan,
      zhi: data.month_pillar.zhi,
      nayin: data.month_pillar.nayin,
      canggan: data.month_pillar.canggan || [],
      shishen: data.month_pillar.shishen || '-',
      changsheng: data.month_pillar.changsheng || '-',
      canggan_shishen: data.month_pillar.canggan_shishen || [],
      shensha: data.month_pillar.shensha || [],
      isDayMaster: false
    },
    {
      title: dayPillarTitle.value,
      gan: data.day_pillar.gan,
      zhi: data.day_pillar.zhi,
      nayin: data.day_pillar.nayin,
      canggan: data.day_pillar.canggan || [],
      shishen: data.day_pillar.shishen || '日主',
      changsheng: data.day_pillar.changsheng || '-',
      canggan_shishen: data.day_pillar.canggan_shishen || [],
      shensha: data.day_pillar.shensha || [],
      isDayMaster: true
    },
    {
      title: '时柱',
      gan: data.hour_pillar.gan,
      zhi: data.hour_pillar.zhi,
      nayin: data.hour_pillar.nayin,
      canggan: data.hour_pillar.canggan || [],
      shishen: data.hour_pillar.shishen || '-',
      changsheng: data.hour_pillar.changsheng || '-',
      canggan_shishen: data.hour_pillar.canggan_shishen || [],
      shensha: data.hour_pillar.shensha || [],
      isDayMaster: false
    }
  ]
})

// 五行颜色映射
const getWuxingColor = (char: string): string => {
  const colors = {
    wood: '#4CAF50',   // 木：绿色
    fire: '#E53935',   // 火：红色
    earth: '#8D6E63',  // 土：褐色
    metal: '#D4AF37',  // 金：金色
    water: '#1E88E5'   // 水：蓝色
  }
  
  const wuxingMap: Record<string, string> = {
    // 木
    '甲': colors.wood, '乙': colors.wood, '寅': colors.wood, '卯': colors.wood,
    // 火
    '丙': colors.fire, '丁': colors.fire, '巳': colors.fire, '午': colors.fire,
    // 土
    '戊': colors.earth, '己': colors.earth, '辰': colors.earth, '戌': colors.earth, '丑': colors.earth, '未': colors.earth,
    // 金
    '庚': colors.metal, '辛': colors.metal, '申': colors.metal, '酉': colors.metal,
    // 水
    '壬': colors.water, '癸': colors.water, '亥': colors.water, '子': colors.water
  }
  
  return wuxingMap[char] || '#333333' // 默认深灰
}

// 五行列表
const wuxingList = computed(() => {
  if (!baziStore.currentBaziData) return []
  
  const { wuxing_strength, wuxing_summary } = baziStore.currentBaziData
  
  return [
    { 
      name: '金', 
      percent: wuxing_strength.jin, 
      count: wuxing_summary.金 || 0,
      color: 'rgba(212, 175, 55, 0.7)',  // 金色 (降低饱和度)
      delay: '0s'
    },
    { 
      name: '木', 
      percent: wuxing_strength.mu, 
      count: wuxing_summary.木 || 0,
      color: 'rgba(76, 129, 68, 0.7)',  // 深绿 (降低饱和度)
      delay: '0.1s'
    },
    { 
      name: '水', 
      percent: wuxing_strength.shui, 
      count: wuxing_summary.水 || 0,
      color: 'rgba(52, 108, 156, 0.7)',  // 深蓝 (降低饱和度)
      delay: '0.2s'
    },
    { 
      name: '火', 
      percent: wuxing_strength.huo, 
      count: wuxing_summary.火 || 0,
      color: 'rgba(192, 57, 43, 0.7)',  // 朱砂红 (降低饱和度)
      delay: '0.3s'
    },
    { 
      name: '土', 
      percent: wuxing_strength.tu, 
      count: wuxing_summary.土 || 0,
      color: 'rgba(139, 115, 85, 0.7)',  // 土黄 (降低饱和度)
      delay: '0.4s'
    }
  ]
})

// 页面加载时隐藏 TabBar
onMounted(() => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [结果页] TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [结果页] 当前页面无 TabBar')
  })
})

// 接收页面参数，判断是否启动 AI 分析
onLoad((options: any) => {
  const needAi   = options?.stream === '1'
  const recordId = options?.record_id || baziStore.currentBaziData?.record_id

  if (needAi && baziStore.currentBaziData) {
    // 重置上一次的 AI 报告，开始新任务
    baziStore.submitAiTask(baziStore.currentBaziData)
  } else if (recordId && !baziStore.currentAiReport && !baziStore.currentBaziData?.ai_report) {
    // 从历史记录进入且没有报告时，也可触发
    if (baziStore.currentBaziData) {
      baziStore.submitAiTask(baziStore.currentBaziData)
    }
  }
})

// 页面卸载时停止轮询（防止内存泄漏）
onUnmounted(() => {
  // 只在任务未完成时停止，已完成的不需要处理
  if (baziStore.aiTaskStatus !== 'done') {
    baziStore.stopAiPolling()
  }
})

// 返回上一页（兼容从历史记录或排盘准备页进入的场景）
const goBack = () => {
  uni.navigateBack()
}

// 显示神煞详情弹窗
const showShenshaDetail = (shenshaName: string) => {
  // 神煞解释字典
  const shenshaDict: Record<string, string> = {
    '将星': '将星主权威、领导才能，命带将星者多有统御之能，适合从事管理、军警等职业。',
    '天德贵人': '天德贵人为大吉之神，主逢凶化吉、遇难呈祥，一生多得贵人相助。',
    '月德贵人': '月德贵人主福德深厚，性格温和，处事圆融，易得长辈提携。',
    '天乙贵人': '天乙贵人为最吉之神，主聪明智慧，遇事多有贵人相助，逢凶化吉。',
    '文昌贵人': '文昌主聪明好学，利于学业、考试，适合从事文化、教育、科研等工作。',
    '太极贵人': '太极者，物极而生。主命主悟性极高，直觉敏锐，与玄学、哲学、心理学有极其深厚的缘分。做事有始有终，遇难往往能冥冥中逢凶化吉。',
    '天厨贵人': '天上之厨，主食禄丰厚。命中带天厨者，一生不愁吃穿，多有口福。适宜在公职、行政、餐饮或农业领域发展，主一生生活平稳安逸。',
    '驿马': '驿马主奔波、变动，命带驿马者多走动，适合外出发展、经商、旅游等。',
    '桃花': '桃花主人缘、异性缘，命带桃花者多有魅力，但需注意感情纷扰。',
    '红艳': '红艳主异性缘佳，容貌姣好，但需注意感情问题，避免桃色纠纷。',
    '华盖': '华盖主艺术、宗教、玄学天赋，性格孤高，喜欢独处思考。',
    '金舆': '金舆主富贵、享受，命带金舆者多有物质福报，生活安逸。',
    '天厨': '天厨主衣食无忧，善于烹饪美食，注重生活品质。',
    '劫煞': '劫煞主波折、破财，需注意防范意外、官非、破财等事。',
    '灾煞': '灾煞主疾病、灾祸，需注意身体健康，防范意外伤害。',
    '孤辰': '孤辰主孤独、独立，性格内向，不善交际，但独立性强。',
    '寡宿': '寡宿主孤独、寡合，婚姻感情易有波折，需注意经营感情。',
    '亡神': '亡神主消耗、损失，需注意防范破财、失物等事。',
    '羊刃': '羊刃主刚强、果断，但易冲动、暴躁，需注意控制情绪。',
    '飞刃': '飞刃主意外、伤灾，需注意安全，防范意外伤害。',
    '空亡': '空亡主虚空、不实，做事易虎头蛇尾，需注意脚踏实地。',
    '咸池': '咸池主桃花、异性缘，但需注意感情纷扰，避免桃色纠纷。',
    '红鸾': '主喜庆、浪漫与正缘桃花。命中带红鸾者，往往面容姣好、极具亲和力，一生容易遇到良缘，婚姻多主幸福美满。',
    '天喜': '主开心、消除灾厄。与红鸾星相呼应，逢之能化解忧愁，常有意外之喜，所谓"一喜挡三灾"，是极好的清明之星。',
    '魁罡': '主刚烈、掌权、不信邪。带魁罡者性格极为坚毅，有大将之风，能逢凶化吉。但脾气往往较硬，需注意刚直易折，宜修柔和之气。',
    '童子': '传说中仙童转世。主第六感强、极具灵气、长相年轻。但也暗示心思细腻敏感，早年易有体弱或情路羁绊，需多亲近禅修、顺其自然。',
    '阴阳差错': '主男女感情、婚姻多有波折或时机不巧。逢此煞者，易在感情中遇到"错的时间遇到对的人"或沟通频道不一致的状况。晚婚、或与伴侣保持一定独立空间可有效化解。'
  }
  
  const description = shenshaDict[shenshaName] || '暂无详细解释'
  
  popupTitle.value = shenshaName
  popupContent.value = description
  showPopup.value = true
}

// ==================== Markdown 解析器 ====================

/**
 * 将 AI 返回的 Markdown 按 ### 切分为独立篇章数组
 * 每个元素：{ title: string(HTML), content: string(HTML) }
 */
const parsedAiSections = computed(() => {
  const raw = aiReportText.value
  if (!raw) return []

  // 按 ### 切分，保留标题行
  const blocks = raw.split(/(?=###\s)/).filter(b => b.trim())

  return blocks.map(block => {
    const lines = block.split('\n')
    const titleLine = lines[0].replace(/^###\s*/, '').trim()
    const bodyLines = lines.slice(1).join('\n').trim()

    // 标题 HTML
    const titleHtml = `<span style="font-size:30rpx;font-weight:600;color:#8B4513;letter-spacing:4rpx;">${titleLine}</span>`

    // 正文处理
    let body = bodyLines

    // ## 标题
    body = body.replace(/##\s+(.+)/g,
      '<h2 style="font-size:32rpx;font-weight:600;color:#C0392B;letter-spacing:5rpx;margin:32rpx 0 12rpx;padding-bottom:10rpx;border-bottom:1px solid rgba(192,57,43,0.15);">$1</h2>'
    )

    // **粗体**
    body = body.replace(/\*\*(.+?)\*\*/g,
      '<strong style="font-weight:700;color:#B8860B;background:rgba(184,134,11,0.08);padding:0 6rpx;border-radius:4rpx;">$1</strong>'
    )

    // 双换行 → 段落
    body = body.split('\n\n').map(para => {
      const t = para.trim()
      if (!t) return ''
      if (t.startsWith('<h')) return t
      return `<p style="font-size:28rpx;color:#1A1A1A;line-height:1.9;letter-spacing:2rpx;text-align:justify;text-indent:2em;padding:20rpx 0;margin:0;border-bottom:0.5px solid rgba(0,0,0,0.06);">${t}</p>`
    }).filter(Boolean).join('')

    // 单换行 → <br>
    body = body.replace(/(?<!>)\n(?!<)/g, '<br/>')

    return { title: titleHtml, content: body }
  })
})

// 小知识百科弹窗
const handleTermClick = (term: string) => {
  // 过滤无效点击
  if (!term || term === '-' || term === '日主') return
  
  // 完整的术语字典
  const termDict: Record<string, string> = {
    // 核心概念
    "主星": "【含义】指八字天干透出的十神。\n【解析】代表一个人展现给外界的社会形象、外在性格以及显性的吉凶事件。",
    "副星": "【含义】指八字地支藏干所对应的十神。\n【解析】代表一个人的内在性格、潜意识、家庭内部关系以及隐蔽的特质。",
    "自坐": "【含义】指日干下方的日支。\n【解析】如庚午，即庚金自坐午火。代表命主的内心世界，同时也代表配偶宫的状态。",
    "纳音": "【含义】古人将六十甲子与五音十二律结合衍生的特殊五行。\n【解析】如'海中金'、'炉中火'。纳音多用于补充分析个人的气质特征、性格底色以及两人八字的合婚参考。",
    
    // 十神百科
    "正官": "【十神】克我且阴阳异性。\n【解析】主威严、自律、贵人、法律与秩序。女命代表正式的丈夫，男命代表事业与女儿。",
    "七杀": "【十神】克我且阴阳同性（又称偏官）。\n【解析】主魄力、野心、压力、果断甚至叛逆。女命也代表情人或非传统姻缘，男命代表儿子。",
    "正印": "【十神】生我且阴阳异性。\n【解析】主仁慈、学业、名誉、涵养与长辈缘。代表母亲、文书与庇护之神。",
    "偏印": "【十神】生我且阴阳同性（极凶时称枭神）。\n【解析】主领悟力、玄学天赋、孤独感与偏门艺术。代表继母、非正规学历或特殊技能。",
    "正财": "【十神】我克且阴阳异性。\n【解析】主正当收入、勤俭节约、踏实肯干。男命代表正式的妻子。",
    "偏财": "【十神】我克且阴阳同性。\n【解析】主意外之财、交际能力、慷慨与投资理财。男命代表父亲或红颜知己。",
    "食神": "【十神】我生且阴阳同性。\n【解析】主福气、享受、温和、艺术才华与美食。女命代表女儿。",
    "伤官": "【十神】我生且阴阳异性。\n【解析】主才华横溢、傲气、打破常规与创新。女命代表儿子，同时伤官克官，女命逢之感情易起波澜。",
    "比肩": "【十神】与我同五行同阴阳。\n【解析】主自我意志、独立、平辈朋友与合作。过旺则易生争执与固执。",
    "劫财": "【十神】与我同五行异阴阳。\n【解析】主竞争、掠夺、爆发力与人际交往。过旺易破财或冲动。",
    
    // 神煞百科
    "天乙贵人": "【神煞·极吉】\n【解析】八字最尊贵之神。主聪明智慧，人缘极佳，遇事能逢凶化吉，一生多有贵人提携帮扶。",
    "文昌贵人": "【神煞·吉】\n【解析】主才华出众，气质文雅。命中带文昌，利于读书考学，逢考运佳，适合从事文化、学术、教育工作。",
    "天德贵人": "【神煞·吉】\n【解析】乃天地德秀之气，主心性仁慈，做事公道，能化解诸多灾厄。",
    "月德贵人": "【神煞·吉】\n【解析】犹如月亮之光辉，主逢凶化吉，福分深厚，多得女性长辈或贵人相助。",
    "羊刃": "【神煞·双刃剑】\n【解析】五行极旺之星。性情刚烈，坚毅果敢。身弱逢之为帮身利器，身旺逢之则易暴躁冲动，利武职（公检法、军人、外科医生等）。",
    "禄神": "【神煞·吉】\n【解析】代表食禄、福气与财富。命中带禄，主一生衣食无忧，身体健康，能安享福分。",
    "驿马": "【神煞·中性】\n【解析】主动荡、变迁、奔波。带驿马者多离乡发展、出国或从事交通、物流、销售等需频繁走动的行业。",
    "桃花": "【神煞·中性】\n【解析】主风流倜傥、异性缘佳、有艺术或审美天赋。适宜从事演艺、公关、美业等，但也需防感情纠纷。",
    "华盖": "【神煞·中性】\n【解析】古代帝王车驾之伞盖。主孤高不群，聪颖绝伦。多与佛道玄学有缘，耐得住寂寞，适合深耕专业技能或艺术创作。",
    "将星": "【神煞·吉】\n【解析】主威权、领导力与组织统御能力。命中带将星，易在职场或官场中掌握实权，成为团队核心。",
    "孤辰": "【神煞·偏凶】\n【解析】主性格孤僻，不善交际，男命逢之易妨克妻子或异性缘薄。",
    "寡宿": "【神煞·偏凶】\n【解析】主内心孤独，清心寡欲，女命逢之易妨克丈夫或感情难聚易散。",
    
    // 神煞补充
    "阴阳差错": "【神煞·偏凶】\n【解析】主男女感情、婚姻多有波折或时机不巧。逢此煞者，易在感情中遇到'错的时间遇到对的人'或沟通频道不一致的状况。晚婚、或与伴侣保持一定独立空间可有效化解。",
    "太极贵人": "【神煞·吉】\n【解析】太极者，物极而生。主命主悟性极高，直觉敏锐，与玄学、哲学、心理学有极其深厚的缘分。做事有始有终，遇难往往能冥冥中逢凶化吉。",
    "天厨贵人": "【神煞·吉】\n【解析】天上之厨，主食禄丰厚。命中带天厨者，一生不愁吃穿，多有口福。适宜在公职、行政、餐饮或农业领域发展，主一生生活平稳安逸。",
    "劫煞": "【神煞·双刃剑】\n【解析】为五行绝处。主突发性的波折、变故或竞争。但劫煞若为喜用神，则主其人决断力极强，聪明敏捷，能在动荡中果断抓住机遇，险中求胜。",
    
    // 宫位与特殊名词补充
    "正宫": "【宫位】八字中常指代'夫妻宫'（即日柱的地支）。\n【解析】代表一个人真实的婚姻状态、家庭内部环境以及最终伴侣的特质。若吉星（如正官、正财）安稳落在正宫，主婚姻美满稳定、得良缘。",
    
    // ================= 宫位与基础概念 =================
    "日元": "【概念·核心】又称'日干'。\n【解析】代表您自己的'本我'与核心灵魂。整个八字命盘的吉凶、强弱，都是以日元为中心来推演的。",
    "年柱": "【宫位·根基】代表 1-16 岁（早年运势）。\n【解析】代表祖辈余荫、原生家庭背景以及一个人最早期的成长环境。",
    "月柱": "【宫位·枝干】代表 17-32 岁（青年运势）。\n【解析】代表父母、兄弟姐妹以及人生最重要的性格'基本盘'与青年时期的发展土壤。",
    "日支": "【宫位·花朵】代表 33-48 岁（中年运势），即'夫妻宫'。\n【解析】代表您最隐秘的内心世界，以及婚姻伴侣的特质和两人相处的模式。",
    "时柱": "【宫位·果实】代表 49 岁以后（晚年运势），即'子女宫'。\n【解析】代表晚年生活状态、对下属及子女的影响力，也暗示着人生最终的归宿与隐藏潜能。",
    
    // ================= 常见纳音五行 =================
    "海中金": "【纳音·金】\n【解析】如深海沉金，光芒内敛。主性格深藏不露，有极强的潜力和城府。不鸣则已，一鸣惊人，但也需伯乐（火）来发掘锻炼。",
    "炉中火": "【纳音·火】\n【解析】如炉膛之火，热情奔放且持久。主性格积极、有感染力，但也容易急躁。一生需有'木'相生（如多读书、沉淀心性）方能保持长盛不衰。",
    "大林木": "【纳音·木】\n【解析】枝繁叶茂，生生不息。主为人仁慈、包容力强、有担当。多能在团队中成为庇护他人的大树，适合从政、教育或管理岗位。",
    "路旁土": "【纳音·土】\n【解析】广袤平坦，承载万物。主性格踏实稳重、有极强的忍耐力和服务精神。不与人争锋，但却是不可或缺的基石型人才。",
    "剑锋金": "【纳音·金】\n【解析】百炼成钢，锋芒毕露。主刚毅果决，执行力极强。适合从事专业技术、公检法、外科医疗等需要'锐气'与纪律的行业。",
    "涧下水": "【纳音·水】\n【解析】山间清泉，柔和清澈。主为人聪慧灵动，善于变通，做事如润物细无声。虽不似大江大河般波澜壮阔，但极具生活情趣与艺术灵感。",
    "杨柳木": "【纳音·木】\n【解析】如杨柳般柔顺婉转，随风飘摇。主性格柔和、善于交际与变通。极具韧性，但内心易有随波逐流的迷茫感，需有坚实的依靠（如土、水）方能成材。",
    "天河水": "【纳音·水】\n【解析】天上之水，沛然清高，能润泽万物。主气度不凡，心胸宽广，乐于施舍与助人。天河水不惧土克（土在地上，水在天上），思想境界往往较高，格局清奇。",
    "山头火": "【纳音·火】\n【解析】如山顶烽火，光芒远照。主性格开朗、有领导气质，能照亮他人。但需注意高处不胜寒，宜保持谦逊。",
    "屋上土": "【纳音·土】\n【解析】如屋顶之土，遮风挡雨。主为人稳重、有责任感，能为家庭和团队提供庇护。",
    "霹雳火": "【纳音·火】\n【解析】如雷电之火，瞬间爆发。主性格急躁、行动力强，能在短时间内完成大事，但需注意持久力。",
    "松柏木": "【纳音·木】\n【解析】如松柏常青，坚韧不拔。主性格坚毅、有原则，能经受风霜考验，晚年运势尤佳。",
    "长流水": "【纳音·水】\n【解析】如江河长流，源远流长。主智慧深远、做事有恒心，能持续发展，一生财运稳定。",
    "沙中金": "【纳音·金】\n【解析】如沙中淘金，需要磨砺。主早年辛苦，但经过努力能成大器，中晚年运势转好。",
    "山下火": "【纳音·火】\n【解析】如山脚之火，温暖平和。主性格温和、有亲和力，能温暖身边的人，适合服务行业。",
    "平地木": "【纳音·木】\n【解析】如平原树木，根基稳固。主性格务实、脚踏实地，能稳步发展，事业根基扎实。",
    "壁上土": "【纳音·土】\n【解析】如墙壁之土，坚固可靠。主为人忠诚、有担当，能成为他人依靠，适合建筑、房地产行业。",
    "金箔金": "【纳音·金】\n【解析】如金箔薄片，华丽精致。主外表光鲜、注重形象，有艺术天赋，但需注意内在修养。",
    "覆灯火": "【纳音·火】\n【解析】如灯笼之火，照亮一方。主性格细腻、善于照顾他人，能在小范围内发挥影响力。",
    "天上火": "【纳音·火】\n【解析】如太阳之火，光芒万丈。主性格豪爽、有领袖气质，能成就大事业，但需注意不可过于刚烈。",
    "石榴木": "【纳音·木】\n【解析】如石榴多子，繁荣昌盛。主子女运佳、家庭和睦，晚年享福，适合从事教育或家族事业。",
    "大海水": "【纳音·水】\n【解析】如大海浩瀚，包容万物。主心胸宽广、格局大，能成就大事业，但需注意情绪波动。",
    "钗钏金": "【纳音·金】\n【解析】如首饰之金，精致美丽。主注重品味、有审美能力，适合艺术、设计、珠宝等行业。",
    "桑柘木": "【纳音·木】\n【解析】如桑树养蚕，默默奉献。主为人勤劳、善于培养他人，适合教育、培训等行业。",
    "大驿土": "【纳音·土】\n【解析】如驿站之土，四通八达。主善于交际、人脉广阔，适合从事贸易、物流等需要沟通的行业。",
    "泉中水": "【纳音·水】\n【解析】如泉水清澈，源源不断。主智慧清明、思维敏捷，能持续创新，适合研发、咨询等行业。",
    "白蜡金": "【纳音·金】\n【解析】如蜡烛之金，柔中带刚。主性格温和但有原则，能在柔和中坚持自我，适合调解、协调工作。",
    "城头土": "【纳音·土】\n【解析】如城墙之土，坚固防御。主有保护意识、责任心强，能守护家庭和事业，适合安保、管理工作。",
    
    // ================= 进阶神煞补充 =================
    "红鸾": "【神煞·吉】\n【解析】主喜庆、浪漫与正缘桃花。命中带红鸾者，往往面容姣好、极具亲和力，一生容易遇到良缘，婚姻多主幸福美满。",
    "天喜": "【神煞·吉】\n【解析】主开心、消除灾厄。与红鸾星相呼应，逢之能化解忧愁，常有意外之喜，所谓'一喜挡三灾'，是极好的清明之星。",
    "空亡": "【神煞·中性】\n【解析】并非绝对的'没有'或'凶兆'，而是指物质维度的'放空'。带空亡者往往淡泊名利，对精神维度、哲学、玄学有极高领悟力，是修心修行之良材。",
    "魁罡": "【神煞·特殊】\n【解析】主刚烈、掌权、不信邪。带魁罡者性格极为坚毅，有大将之风，能逢凶化吉。但脾气往往较硬，需注意刚直易折，宜修柔和之气。",
    "金舆": "【神煞·吉】\n【解析】古代贵族的'金色马车'。主物质生活丰裕，出入有豪车相伴。命中带金舆，多能得到伴侣或家族的得力助益，生活安逸。",
    "童子": "【神煞·中性】\n【解析】传说中仙童转世。主第六感强、极具灵气、长相年轻。但也暗示心思细腻敏感，早年易有体弱或情路羁绊，需多亲近禅修、顺其自然。"
  }
  
  const description = termDict[term] || '暂无详细解释'
  
  popupTitle.value = term
  popupContent.value = description
  showPopup.value = true
}

</script>

<style scoped>
/* 页面样式 - Material Symbols 图标字体已在 App.vue 全局定义 */

/* ==================== 全局变量 ==================== */
.page-container {
  --zen-bg: #F8F6F3;
  --zen-white: #FEFEFE;
  --zen-ink: #1A1A1A;
  --zen-gray: #8E8E93;
  --zen-border: rgba(0, 0, 0, 0.08);
  --zen-cinnabar: #C0392B;
  --zen-shadow: rgba(0, 0, 0, 0.05);
}

/* ==================== 页面容器 ==================== */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8F6F3 0%, #F0EDE8 100%);
  background-image: 
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* ==================== 毛玻璃卡片 ==================== */
.glass-card {
  background: rgba(254, 254, 254, 0.75);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.04);
}

/* ==================== 加载状态 ==================== */

.loading-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.zen-circle {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 60rpx;
}

.circle-outer {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  border: 2rpx solid rgba(192, 57, 43, 0.3);
  border-radius: 50%;
  animation: rotate 3s linear infinite;
}

.circle-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120rpx;
  height: 120rpx;
  border: 2rpx solid rgba(192, 57, 43, 0.6);
  border-radius: 50%;
  animation: rotate 2s linear infinite reverse;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 300;
  color: #1A1A1A;
  letter-spacing: 12rpx;
  margin-bottom: 30rpx;
}

.loading-dots {
  display: flex;
  gap: 16rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  background-color: #C0392B;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* ==================== 结果容器 ==================== */

.result-container {
  padding: 30rpx 30rpx 120rpx;
  max-width: 750rpx;
  margin: 0 auto;
}

/* ==================== 顶部信息栏 ==================== */
.header-bar {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  padding: 80rpx 0 20rpx;
}

.back-button {
  margin-right: 30rpx;
}

.back-icon {
  font-size: 48rpx;
  color: #1A1A1A;
}

.header-info {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 20rpx;
}

.name-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 44rpx;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 6rpx;
}

.gender-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 26rpx;
  color: #8E8E93;
  letter-spacing: 4rpx;
}

/* ==================== 基础信息卡片 ==================== */
.info-card {
  padding: 30rpx 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
}

.info-row:not(:last-child) {
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
}

.info-label {
  font-size: 26rpx;
  color: #8E8E93;
  width: 100rpx;
  letter-spacing: 4rpx;
}

.info-value {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: #1A1A1A;
  letter-spacing: 2rpx;
}

/* ==================== 核心命盘矩阵 ==================== */
.bazi-matrix {
  padding: 40rpx 30rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.matrix-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  margin-bottom: 50rpx;
}

.title-line {
  width: 80rpx;
  height: 0.5px;
  background-color: rgba(0, 0, 0, 0.15);
}

.title-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 12rpx;
}

/* 四柱容器 */
.pillars-container {
  display: flex;
  justify-content: space-around;
  gap: 16rpx;
}

/* 柱子列 */
.pillar-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 12rpx;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.5);
  text-align: center;
  opacity: 0;
  transform: translateY(30rpx);
  animation: slideUp 0.6s ease-out forwards;
}

/* 日柱高亮 */
.pillar-day {
  border: 1px solid rgba(192, 57, 43, 0.3);
  background: rgba(192, 57, 43, 0.02);
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 柱子标题 */
.pillar-header {
  padding: 16rpx 0;
  text-align: center;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
}

.pillar-label {
  font-size: 22rpx;
  color: #8E8E93;
  letter-spacing: 4rpx;
}

/* 单元格 */
.cell {
  padding: 16rpx 8rpx;
  text-align: center;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.03);
  min-height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell:last-child {
  border-bottom: none;
}

/* 十神 */
.shishen-cell {
  background: rgba(0, 0, 0, 0.01);
}

.shishen-text {
  font-size: 22rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
}

.day-master-label {
  background: rgba(192, 57, 43, 0.05);
}

.shishen-text.highlight {
  color: #C0392B;
  font-weight: 500;
}

/* 天干 */
.gan-cell {
  background: rgba(255, 255, 255, 0.8);
}

.gan-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 4rpx;
}

.gan-text.highlight {
  /* 日主高亮时使用朱砂红，优先级高于五行颜色 */
  font-weight: 900;
}

/* 地支 */
.zhi-cell {
  background: rgba(255, 255, 255, 0.8);
}

.zhi-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 4rpx;
}

/* 藏干容器 - 固定高度解决错位问题 */
.canggan-cell {
  padding: 12rpx 8rpx;
  min-height: 180rpx; /* 确保容纳3行藏干 */
}

.canggan-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 140rpx; /* 强制固定高度，确保能容纳3行小字且底部留白 */
  margin: 10rpx 0;
  gap: 4rpx;
}

.cg-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
  height: 40rpx; /* 每行藏干固定高度 */
  width: 100%;
}

.cg-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 24rpx;
  font-weight: 500;
  letter-spacing: 1rpx;
}

.cg-ss {
  font-size: 20rpx;
  color: #888; /* 藏干十神保持灰色 */
  letter-spacing: 1rpx;
}

/* 十二长生 - 固定高度 */
.changsheng-cell {
  min-height: 50rpx;
  background: rgba(0, 0, 0, 0.01);
}

.changsheng-text {
  display: block;
  height: 40rpx; /* 固定高度 */
  line-height: 40rpx;
  font-size: 22rpx;
  color: #666;
  letter-spacing: 2rpx;
}

/* 纳音 - 固定高度 */
.nayin-cell {
  background: rgba(0, 0, 0, 0.01);
}

.nayin-text {
  display: block;
  height: 40rpx; /* 固定高度 */
  line-height: 40rpx;
  font-size: 20rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
}

/* 神煞 - 自适应高度，flex 换行 */
.shensha-cell {
  padding: 12rpx 8rpx;
}

.shensha-box {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-start;
  gap: 6rpx;
}

.ss-tag {
  font-size: 20rpx;
  color: #7f8c8d;
  background-color: rgba(0, 0, 0, 0.04);
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  line-height: 1.2;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ss-tag:active {
  background-color: rgba(178, 58, 52, 0.1);
  color: #B23A34;
  transform: scale(0.95);
}

.ss-empty {
  font-size: 20rpx;
  color: #ccc;
}

/* ==================== 日主信息 ==================== */
.daymaster-card {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.daymaster-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 16rpx;
}

.daymaster-label {
  font-size: 24rpx;
  color: #8E8E93;
  letter-spacing: 6rpx;
  text-align: center;
  display: block;
  width: 100%;
}

.daymaster-char {
  font-family: 'Noto Serif SC', serif;
  font-size: 140rpx;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-align: center;
  display: block;
  width: 100%;
}

.daymaster-wuxing {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 400;
  color: #8E8E93;
  letter-spacing: 4rpx;
  text-align: center;
  display: block;
  width: 100%;
}

/* ==================== 五行能量进度条 ==================== */
.wuxing-energy {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

.section-title {
  margin-bottom: 40rpx;
  text-align: center;
}

.energy-bars {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.energy-row {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.energy-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.energy-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 4rpx;
}

.energy-value {
  font-size: 24rpx;
  color: #8E8E93;
  letter-spacing: 1rpx;
}

.energy-bar-container {
  height: 32rpx;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 16rpx;
  overflow: hidden;
}

.energy-bar {
  height: 100%;
  border-radius: 16rpx;
  opacity: 0;
  animation: fillBar 1s ease-out forwards;
  transition: width 0.6s ease;
}

@keyframes fillBar {
  to {
    opacity: 1;
  }
}

.energy-count {
  font-size: 22rpx;
  color: #8E8E93;
  text-align: right;
  letter-spacing: 1rpx;
}

/* ==================== AI 分析报告 ==================== */
.ai-report {
  padding: 40rpx;
  margin-bottom: 30rpx;
  border-radius: 16rpx;
}

/* 每篇独立卡片 */
.ai-section-card {
  padding: 40rpx 36rpx 20rpx;
  margin-bottom: 24rpx;
  border-radius: 16rpx;
}

/* 篇标题区域 */
.ai-section-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

/* 标题左侧竖线装饰 */
.ai-section-line {
  width: 6rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #D4AF37 0%, #B8860B 100%);
  border-radius: 3rpx;
  flex-shrink: 0;
}

.ai-section-title-text {
  flex: 1;
}

.ai-content {
  padding: 0 10rpx;
  background: rgba(0, 0, 0, 0.01);
  border-left: 4rpx solid #C0392B;
  border-radius: 8rpx;
}

/* rich-text 容器 */
.ai-rich-text {
  width: 100%;
}

/* ==================== Markdown 禅意排版 ==================== */

/* 主标题 (# 标题) */
.zen-main-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 40rpx;
  font-weight: 700;
  color: #1A1A1A;
  text-align: center;
  letter-spacing: 8rpx;
  margin: 40rpx 0 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid rgba(192, 57, 43, 0.2);
}

/* 章节标题 (## 标题) */
.zen-chapter-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 600;
  color: #C0392B;
  letter-spacing: 6rpx;
  margin: 50rpx 0 30rpx;
  padding-bottom: 16rpx;
  border-bottom: 0.5px solid rgba(192, 57, 43, 0.15);
}

/* 小节标题 (### 标题) */
.zen-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
  letter-spacing: 4rpx;
  margin: 40rpx 0 24rpx;
  padding-left: 20rpx;
  border-left: 4rpx solid #D4C4A8;
}

/* 段落 */
.zen-paragraph {
  font-size: 28rpx;
  color: #1A1A1A;
  line-height: 1.8;
  letter-spacing: 2rpx;
  margin-bottom: 0;
  padding: 28rpx 0;
  text-align: justify;
  text-indent: 2em;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
}

/* 重点高亮 (**文字**) */
.zen-highlight {
  font-weight: 700;
  color: #B8860B;
  background: rgba(184, 134, 11, 0.08);
  padding: 0 8rpx;
  border-radius: 4rpx;
}

.ai-text {
  font-size: 28rpx;
  color: #1A1A1A;
  line-height: 48rpx;
  letter-spacing: 2rpx;
  white-space: pre-wrap;
}

/* ==================== 无数据状态 ==================== */

.empty-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 60rpx;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 40rpx;
  opacity: 0.5;
}

.empty-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 500;
  color: #1A1A1A;
  letter-spacing: 6rpx;
  margin-bottom: 20rpx;
}

.empty-tip {
  font-size: 26rpx;
  color: #8E8E93;
  letter-spacing: 2rpx;
  margin-bottom: 60rpx;
}

.empty-button {
  width: 400rpx;
  height: 88rpx;
  background-color: #B23A34;
  border: none;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-text {
  font-size: 28rpx;
  color: #FFFFFF;
  letter-spacing: 6rpx;
}

/* ── 底部留白 ── */
.bottom-spacer { height: 80rpx; }

/* ── 流式状态 ── */
.stream-status-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 30rpx;
  margin-bottom: 16rpx;
  background: rgba(212, 175, 55, 0.06);
  border-radius: 12rpx;
  border: 1px solid rgba(212, 175, 55, 0.15);
}

.stream-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #D4AF37;
  flex-shrink: 0;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

.stream-status-text {
  font-size: 24rpx;
  color: #B8860B;
  letter-spacing: 1rpx;
}

.stream-error-bar {
  padding: 20rpx 30rpx;
  margin-bottom: 16rpx;
  background: rgba(178, 58, 52, 0.06);
  border-radius: 12rpx;
  border: 1px solid rgba(178, 58, 52, 0.15);
}

.stream-error-text {
  font-size: 24rpx;
  color: #B23A34;
}

/* 流式进行中的占位卡片 */
.stream-placeholder {
  padding: 40rpx 36rpx;
  margin-bottom: 24rpx;
  border-radius: 16rpx;
  min-height: 200rpx;
}

.stream-placeholder-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.9;
  letter-spacing: 1rpx;
  white-space: pre-wrap;
}

/* 打字机光标 */
.stream-cursor {
  display: inline-block;
  width: 3rpx;
  height: 32rpx;
  background: #B23A34;
  margin-left: 4rpx;
  vertical-align: middle;
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 光标行（生成中末尾） */
.stream-cursor-row {
  display: flex;
  justify-content: center;
  padding: 20rpx 0 40rpx;
}

/* ==================== AI 异步 Loading 卡片 ==================== */
.ai-loading-card {
  margin: 0 0 32rpx;
  padding: 48rpx 40rpx 36rpx;
}

.ai-loading-inner {
  display: flex;
  align-items: center;
  gap: 36rpx;
}

/* 轨道旋转动效 */
.ai-loading-orbit {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(178, 58, 52, 0.15);
  border-top-color: #B23A34;
  animation: orbit-spin 1.2s linear infinite;
  flex-shrink: 0;
  position: relative;
}

.ai-loading-planet {
  position: absolute;
  top: -6rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #B23A34;
}

@keyframes orbit-spin {
  to { transform: rotate(360deg); }
}

.ai-loading-texts {
  flex: 1;
}

.ai-loading-title {
  display: block;
  font-size: 28rpx;
  color: #1A1A1A;
  font-weight: 500;
  letter-spacing: 2rpx;
  margin-bottom: 10rpx;
}

.ai-loading-sub {
  display: block;
  font-size: 22rpx;
  color: rgba(0, 0, 0, 0.4);
  letter-spacing: 1rpx;
}

.ai-partial-hint {
  margin-top: 28rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid rgba(212, 175, 55, 0.15);
}

.ai-partial-text {
  font-size: 22rpx;
  color: rgba(178, 58, 52, 0.6);
  letter-spacing: 1rpx;
}

/* ==================== 自定义知识弹窗 ==================== */
.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 15, 15, 0.55); /* 更深邃的背景，突出弹窗 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 60rpx;
}

.popup-content {
  width: 100%;
  max-width: 600rpx;
  max-height: 70vh;
  background: rgba(255, 255, 255, 0.18); /* 提升霜白色浓度 */
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.25); /* 提亮边框增加边界感 */
  border-radius: 24rpx;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.popup-title {
  padding: 40rpx 40rpx 24rpx;
  font-size: 36rpx;
  font-weight: 600;
  color: #FFFFFF;
  text-align: center;
  letter-spacing: 0.1em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.popup-body {
  flex: 1;
  padding: 32rpx 40rpx 40rpx;
  overflow-y: auto;
}

.popup-text {
  font-size: 28rpx;
  line-height: 1.8;
  color: #EAEAEA;
  white-space: pre-wrap;
  letter-spacing: 0.05em;
}
</style>
