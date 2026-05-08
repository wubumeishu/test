<template>
  <view class="page-container">
    <ZenHeader :title="pageTitle" :show-back="true" />

    <main class="main-content">
      <!-- Tab 切换 -->
      <view class="tab-container">
        <view 
          class="tab-item" 
          :class="{ active: currentTab === 0 }"
          @click="currentTab = 0"
        >
          <text class="tab-text">选择档案</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: currentTab === 1 }"
          @click="currentTab = 1"
        >
          <text class="tab-text">快速排盘</text>
        </view>
      </view>

      <!-- 选择档案板块 -->
      <view v-if="currentTab === 0" class="archive-section">
        <!-- 新建档案入口 -->
        <view class="create-archive-card" hover-class="card-hover" @click="goToCreateArchive">
          <text class="material-symbols-outlined add-icon">add_circle</text>
          <text class="create-text">新建并保存档案</text>
        </view>

        <!-- 档案列表 -->
        <view v-if="archiveStore.archives.length > 0" class="archive-list">
          <view 
            v-for="archive in archiveStore.archives" 
            :key="archive.id"
            class="archive-item"
            hover-class="card-hover"
            @click="selectArchive(archive)"
          >
            <!-- 第一行：姓名 + 性别 + 默认标签 -->
            <view class="archive-header">
              <view class="archive-name-row">
                <text class="archive-name">{{ archive.name }}</text>
                <text class="archive-gender-chip">{{ archive.gender === 1 ? '男' : '女' }}</text>
              </view>
              <view v-if="archive.isDefault" class="default-badge">
                <text class="badge-text">默认</text>
              </view>
            </view>

            <!-- 第二行：双历法日期 -->
            <view class="archive-dates">
              <text class="date-solar">阳历：{{ formatArchiveDate(archive).solar }}</text>
              <text class="date-lunar">农历：{{ formatArchiveDate(archive).lunar }}</text>
            </view>

            <!-- 第三行：全量标签 -->
            <view v-if="archive.tags && archive.tags.length > 0" class="archive-tags">
              <text
                v-for="tag in archive.tags"
                :key="tag"
                class="tag-chip"
              >{{ tag }}</text>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view v-else class="empty-state">
          <text class="material-symbols-outlined empty-icon">folder_open</text>
          <text class="empty-text">暂无档案</text>
          <text class="empty-hint">点击上方按钮创建第一个档案</text>
        </view>
      </view>

      <!-- 快速排盘板块 -->
      <view v-if="currentTab === 1" class="quick-section">
        <view class="form-container">
          <!-- 性别 -->
          <view class="form-item">
            <text class="form-label">性别</text>
            <view class="radio-group">
              <view 
                class="radio-item" 
                :class="{ active: quickForm.gender === 1 }"
                @click="quickForm.gender = 1"
              >
                <text class="radio-text">男</text>
              </view>
              <view 
                class="radio-item" 
                :class="{ active: quickForm.gender === 0 }"
                @click="quickForm.gender = 0"
              >
                <text class="radio-text">女</text>
              </view>
            </view>
          </view>

          <!-- 出生日期 -->
          <view class="form-item">
            <view class="date-label-row">
              <text class="form-label" style="margin-bottom: 0;">出生日期</text>
              <!-- 公历/农历切换胶囊 -->
              <view class="calendar-toggle">
                <view
                  class="toggle-option"
                  :class="{ 'toggle-active': !quickForm.isLunar }"
                  @click="quickForm.isLunar = false"
                >
                  <text class="toggle-text">公历</text>
                </view>
                <view
                  class="toggle-option"
                  :class="{ 'toggle-active': quickForm.isLunar }"
                  @click="quickForm.isLunar = true"
                >
                  <text class="toggle-text">农历</text>
                </view>
              </view>
            </view>
            <picker 
              mode="date" 
              :value="quickForm.birthDate"
              @change="onDateChange"
            >
              <view class="picker-display">
                <text class="picker-text">
                  {{ quickForm.birthDate }}
                </text>
                <text class="material-symbols-outlined picker-icon">calendar_today</text>
              </view>
            </picker>
          </view>

          <!-- 出生时间 -->
          <view class="form-item">
            <text class="form-label">出生时间</text>
            <picker 
              mode="time" 
              :value="quickForm.birthTime"
              @change="onTimeChange"
            >
              <view class="picker-display">
                <text class="picker-text" :class="{ placeholder: !quickForm.birthTime }">
                  {{ quickForm.birthTime || '请选择时间' }}
                </text>
                <text class="material-symbols-outlined picker-icon">schedule</text>
              </view>
            </picker>
          </view>

          <!-- 排盘按钮 -->
          <view class="button-container">
            <button 
              class="calculate-button" 
              hover-class="button-hover"
              @click="quickCalculate"
            >
              <text class="button-text">开始排盘 (不留档)</text>
            </button>
          </view>
        </view>
      </view>
    </main>

    <!-- ══════════════════════════════════════
         Premium Modal：AI 精批拦截弹窗
    ══════════════════════════════════════ -->
    <view v-if="showPremiumModal" class="premium-overlay" @click="closePremiumModal">
      <view class="premium-modal" @click.stop>
        <!-- 顶部装饰 -->
        <view class="modal-glow"></view>
        
        <!-- 图标 -->
        <view class="modal-icon-wrap">
          <text class="material-symbols-outlined modal-icon">auto_awesome</text>
        </view>

        <!-- 标题 -->
        <text class="modal-title">AI 深度解析</text>
        
        <!-- 描述 -->
        <text class="modal-desc">
          结合大模型，为您提供万字深度的心理与命运解析。此为高级服务。
        </text>

        <!-- 按钮组 -->
        <view class="modal-actions">
          <view class="modal-btn modal-btn--secondary" hover-class="btn-hover" @click="handleVipClick">
            <text class="material-symbols-outlined btn-icon">workspace_premium</text>
            <text class="btn-text">解锁 VIP</text>
            <text class="btn-hint">(暂未开放)</text>
          </view>
          
          <view class="modal-btn modal-btn--primary" hover-class="btn-hover" @click="handleMockAd">
            <text class="material-symbols-outlined btn-icon">play_circle</text>
            <text class="btn-text">看视频免费解锁</text>
          </view>
        </view>

        <!-- 关闭按钮 -->
        <view class="modal-close" @click="closePremiumModal">
          <text class="material-symbols-outlined">close</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { onShow, onLoad } from '@dcloudio/uni-app'
import { Solar, Lunar } from 'lunar-javascript'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useArchiveStore } from '@/store/useArchiveStore'
import { useBaziStore } from '@/store/useBaziStore'
import type { Archive } from '@/store/useArchiveStore'

// ==================== 页面参数 ====================
const mode = ref<string>('') // 'depth' 表示 AI 精批模式

onLoad((options: Record<string, string> = {}) => {
  mode.value = options.mode || ''
  console.log('📋 [setup] 页面加载，mode:', mode.value)
})

// 动态标题
const pageTitle = computed(() => {
  return mode.value === 'depth' ? 'AI 深度解析' : '排盘信息'
})

// ==================== Premium Modal 状态 ====================
const showPremiumModal = ref(false)
const pendingArchive = ref<Archive | null>(null) // 暂存选中的档案
const pendingQuickForm = ref<any>(null) // 暂存快速排盘表单

// 打开弹窗
const openPremiumModal = () => {
  showPremiumModal.value = true
}

// 关闭弹窗
const closePremiumModal = () => {
  showPremiumModal.value = false
  pendingArchive.value = null
  pendingQuickForm.value = null
}

// VIP 按钮点击
const handleVipClick = () => {
  uni.showToast({
    title: 'VIP 系统建设中',
    icon: 'none',
    duration: 1500
  })
}

// 模拟广告逻辑
const handleMockAd = async () => {
  const archiveToProcess = pendingArchive.value
  const formToProcess = pendingQuickForm.value
  
  closePremiumModal()
  
  // ── 第一阶段：模拟广告加载，同时发起排盘请求（不含 AI）──────────
  uni.showLoading({ title: '正在加载广告...', mask: true })

  // 并行发起排盘请求（is_deep_analysis 仍为 true，用于标记记录类型）
  const baziRequestPromise = (async () => {
    if (archiveToProcess) {
      return await baziStore.calculateByArchive(archiveToProcess.id, true)
    } else if (formToProcess) {
      return await baziStore.calculateByData({ ...formToProcess, is_deep_analysis: true })
    } else {
      throw new Error('没有待处理的排盘数据')
    }
  })()

  // ── 第二阶段：模拟广告播放 2.5 秒 ──────────────────────────────
  await new Promise(resolve => setTimeout(resolve, 2500))
  uni.showLoading({ title: '广告观看完成，正在解析命盘...', mask: true })

  // ── 第三阶段：等待排盘完成（通常 < 1 秒，早已完成）──────────────
  try {
    await baziRequestPromise
    uni.hideLoading()

    const recordId = baziStore.currentBaziData?.record_id
    // 跳转结果页，携带 stream=1 标记，结果页会自动发起流式 AI 请求
    uni.navigateTo({
      url: recordId
        ? `/pages/result/result?record_id=${recordId}&stream=1`
        : '/pages/result/result',
      fail: (err) => console.error('❌ [setup] 跳转失败:', err)
    })
  } catch (error: any) {
    console.error('❌ [setup] 排盘失败:', error)
    uni.hideLoading()
    uni.showModal({
      title: '解析失败',
      content: error.message || '网络异常，请稍后重试',
      showCancel: false
    })
  }
}

// 强制隐藏原生 TabBar
onMounted(() => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [setup] 原生 TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [setup] 当前页面无 TabBar')
  })
})

// 页面显示时刷新档案列表
onShow(() => {
  console.log('📋 [setup] 页面显示，刷新档案列表')
  archiveStore.fetchArchives()
})

// 引入 Store
const archiveStore = useArchiveStore()
const baziStore = useBaziStore()

// Tab 状态
const currentTab = ref(0) // 0=选择档案, 1=快速排盘

// 快速排盘表单（name 不在 UI 显示，内部静默传递）
const quickForm = reactive({
  name: '未知',
  gender: 1 as 0 | 1,
  birthDate: '2000-01-01',
  birthTime: '12:00',
  isLunar: false
})

// 跳转到新建档案页
const goToCreateArchive = () => {
  uni.navigateTo({
    url: '/package_archive/pages/archive/add'
  })
}

// 地支时辰对照（用于农历时辰显示）
const DIZHI_HOURS = [
  '子','丑','丑','寅','寅','卯','卯','辰','辰','巳','巳','午',
  '午','未','未','申','申','酉','酉','戌','戌','亥','亥','子'
]

/**
 * 根据档案数据生成阳历/农历双行显示
 */
const formatArchiveDate = (archive: Archive) => {
  const { birthDate, birthTime, isLunar } = archive
  if (!birthDate || !birthTime) return { solar: '—', lunar: '—' }

  try {
    const [year, month, day] = birthDate.split('-').map(Number)
    const [hour] = birthTime.split(':').map(Number)

    if (isLunar) {
      // 档案本身是农历，birthDate 是农历日期，需转公历
      const lunarObj = Lunar.fromYmd(year, month, day)
      const solarObj = lunarObj.getSolar()
      const sy = solarObj.getYear()
      const sm = solarObj.getMonth()
      const sd = solarObj.getDay()
      const solar = `${sy}年${String(sm).padStart(2,'0')}月${String(sd).padStart(2,'0')}日 ${birthTime}`
      const lunar = `${year}年${lunarObj.getMonthInChinese()}月${lunarObj.getDayInChinese()} ${DIZHI_HOURS[hour]}时`
      return { solar, lunar }
    } else {
      // 档案是公历，转农历
      const solarObj = Solar.fromYmd(year, month, day)
      const lunarObj = solarObj.getLunar()
      const solar = `${year}年${String(month).padStart(2,'0')}月${String(day).padStart(2,'0')}日 ${birthTime}`
      const lunar = `${lunarObj.getYear()}年${lunarObj.getMonthInChinese()}月${lunarObj.getDayInChinese()} ${DIZHI_HOURS[hour]}时`
      return { solar, lunar }
    }
  } catch {
    return { solar: `${birthDate} ${birthTime}`, lunar: '—' }
  }
}

// 选择档案并排盘
const selectArchive = async (archive: Archive) => {
  try {
    console.log('📋 [setup] 选择档案:', archive)

    // ── AI 精批模式：拦截并弹窗 ──
    if (mode.value === 'depth') {
      pendingArchive.value = archive
      openPremiumModal()
      return
    }

    // ── 普通排盘模式：直接请求 ──
    uni.showLoading({
      title: '正在排盘...',
      mask: true
    })

    await baziStore.calculateByArchive(archive.id)

    uni.hideLoading()

    console.log('✅ [setup] 排盘成功，跳转到结果页')

    uni.navigateTo({
      url: '/pages/result/result'
    })
  } catch (error: any) {
    console.error('❌ [setup] 排盘失败:', error)
    uni.hideLoading()
  }
}

// 日期选择器变化
const onDateChange = (e: any) => {
  quickForm.birthDate = e.detail.value
  console.log('📅 [setup] 选择日期:', quickForm.birthDate)
}

// 时间选择器变化
const onTimeChange = (e: any) => {
  quickForm.birthTime = e.detail.value
  console.log('⏰ [setup] 选择时间:', quickForm.birthTime)
}

// 快速排盘
const quickCalculate = async () => {
  // 表单验证
  if (!quickForm.birthDate) {
    uni.showToast({
      title: '请选择出生日期',
      icon: 'none',
      duration: 1500
    })
    return
  }

  if (!quickForm.birthTime) {
    uni.showToast({
      title: '请选择出生时间',
      icon: 'none',
      duration: 1500
    })
    return
  }

  try {
    console.log('🚀 [setup] 开始快速排盘:', quickForm)

    // 解析日期和时间
    const [year, month, day] = quickForm.birthDate.split('-').map(Number)
    const [hour, minute] = quickForm.birthTime.split(':').map(Number)

    const formData = {
      name: quickForm.name.trim(),
      gender: quickForm.gender,
      birth_year: year,
      birth_month: month,
      birth_day: day,
      birth_hour: hour,
      birth_minute: minute,
      is_lunar: quickForm.isLunar,
      is_deep_analysis: false
    }

    // ── AI 精批模式：拦截并弹窗 ──
    if (mode.value === 'depth') {
      pendingQuickForm.value = formData
      openPremiumModal()
      return
    }

    // ── 普通排盘模式：直接请求 ──
    uni.showLoading({
      title: '正在排盘...',
      mask: true
    })

    await baziStore.calculateByData(formData)

    uni.hideLoading()

    console.log('✅ [setup] 排盘成功，跳转到结果页')

    uni.navigateTo({
      url: '/pages/result/result'
    })
  } catch (error: any) {
    console.error('❌ [setup] 排盘失败:', error)
    uni.hideLoading()
  }
}
</script>

<style scoped>
/* 页面样式 - Material Symbols 图标字体已在 App.vue 全局定义 */

/* CSS 变量定义在根容器 */
.page-container {
  --zen-bg: #FCFAF8;
  --zen-ink: #1A1A1A;
  --zen-gray: #8E8E93;
  --zen-border: #F0F0F0;
  --zen-accent: #A68B67;
  --zen-cinnabar: #B22222;

  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--zen-ink);
}

/* 主内容区 */
.main-content {
  padding-bottom: 200rpx;
}

/* Tab 切换 */
.tab-container {
  display: flex;
  border-bottom: 1px solid var(--zen-border);
  margin: 0 40rpx;
}

.tab-item {
  flex: 1;
  padding: 30rpx 0;
  text-align: center;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item.active {
  border-bottom-color: var(--zen-ink);
}

.tab-text {
  font-size: 28rpx;
  font-weight: 300;
  letter-spacing: 0.1em;
  color: var(--zen-gray);
}

.tab-item.active .tab-text {
  font-weight: 500;
  color: var(--zen-ink);
}

/* 选择档案板块 */
.archive-section {
  padding: 40rpx;
}

/* 新建档案卡片 */
.create-archive-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  padding: 40rpx;
  background-color: #fff;
  border: 2px dashed var(--zen-border);
  border-radius: 16rpx;
  margin-bottom: 40rpx;
  transition: all 0.3s;
}

.card-hover {
  background-color: #F5F3F0;
}

.add-icon {
  font-size: 48rpx;
  color: var(--zen-accent);
  font-weight: 200;
}

.create-text {
  font-size: 28rpx;
  color: var(--zen-accent);
  letter-spacing: 0.05em;
}

/* 档案列表 */
.archive-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.archive-item {
  position: relative;
  padding: 32rpx 40rpx;
  background-color: #fff;
  border: 1px solid var(--zen-border);
  border-radius: 16rpx;
  transition: all 0.3s;
}

/* 第一行：姓名 + 性别 + 默认标签 */
.archive-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.archive-name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.archive-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 32rpx;
  font-weight: 500;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.archive-gender-chip {
  font-size: 20rpx;
  color: var(--zen-cinnabar);
  background: rgba(178, 34, 34, 0.06);
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  flex-shrink: 0;
}

.default-badge {
  padding: 6rpx 16rpx;
  background-color: var(--zen-cinnabar);
  border-radius: 6rpx;
  flex-shrink: 0;
  margin-left: 16rpx;
  align-self: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-text {
  font-size: 18rpx;
  color: #fff;
  letter-spacing: 0.1em;
}

/* 第二行：双历法日期 */
.archive-dates {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  margin-bottom: 16rpx;
}

.date-solar {
  font-size: 24rpx;
  color: var(--zen-ink);
  font-weight: 300;
}

.date-lunar {
  font-size: 22rpx;
  color: var(--zen-gray);
}

/* 第三行：全量标签 */
.archive-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.tag-chip {
  font-size: 20rpx;
  color: var(--zen-accent);
  background-color: rgba(166, 139, 103, 0.1);
  padding: 6rpx 18rpx;
  border-radius: 8rpx;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
}

.empty-icon {
  font-size: 120rpx;
  color: var(--zen-border);
  margin-bottom: 40rpx;
  font-weight: 200;
}

.empty-text {
  font-size: 28rpx;
  color: var(--zen-gray);
  margin-bottom: 16rpx;
  letter-spacing: 0.05em;
}

.empty-hint {
  font-size: 22rpx;
  color: rgba(142, 142, 147, 0.6);
  letter-spacing: 0.05em;
}

/* 快速排盘板块 */
.quick-section {
  padding: 40rpx;
}

.form-container {
  background-color: #fff;
  border: 1px solid var(--zen-border);
  border-radius: 16rpx;
  padding: 40rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}


.form-label {
  display: block;
  font-size: 24rpx;
  color: var(--zen-gray);
  margin-bottom: 20rpx;
  letter-spacing: 0.1em;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  color: var(--zen-ink);
  background-color: var(--zen-bg);
  border: 1px solid var(--zen-border);
  border-radius: 12rpx;
  transition: border-color 0.3s;
}

.placeholder-style {
  color: rgba(142, 142, 147, 0.4);
  font-weight: 300;
}

/* 单选组 */
.radio-group {
  display: flex;
  gap: 20rpx;
}

.radio-item {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--zen-bg);
  border: 1px solid var(--zen-border);
  border-radius: 12rpx;
  transition: all 0.3s;
}

.radio-item.active {
  background-color: #B23A34;
  border-color: #B23A34;
}

.radio-text {
  font-size: 26rpx;
  color: var(--zen-gray);
  letter-spacing: 0.05em;
}

.radio-item.active .radio-text {
  color: #fff;
}

/* 出生日期标签行（含历法切换） */
.date-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

/* 公历/农历胶囊切换 */
.calendar-toggle {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 32rpx;
  padding: 4rpx;
}

.toggle-option {
  padding: 8rpx 24rpx;
  border-radius: 28rpx;
  transition: all 0.2s ease;
}

.toggle-active {
  background: #B23A34;
}

.toggle-text {
  font-size: 22rpx;
  color: rgba(142, 142, 147, 0.8);
  letter-spacing: 1rpx;
}

.toggle-active .toggle-text {
  color: #FFFFFF;
  font-weight: 500;
}

/* 选择器显示 */
.picker-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80rpx;
  padding: 0 30rpx;
  background-color: var(--zen-bg);
  border: 1px solid var(--zen-border);
  border-radius: 12rpx;
}

.picker-text {
  font-size: 28rpx;
  color: var(--zen-ink);
}

.picker-text.placeholder {
  color: rgba(142, 142, 147, 0.4);
  font-weight: 300;
}

.picker-icon {
  font-size: 36rpx;
  color: var(--zen-gray);
  font-weight: 200;
}

/* 按钮容器 */
.button-container {
  margin-top: 60rpx;
}

.calculate-button {
  width: 100%;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #B23A34;
  border: none;
  border-radius: 12rpx;
  transition: all 0.3s;
}

.button-hover {
  opacity: 0.8;
}

.button-text {
  font-size: 28rpx;
  color: #fff;
  letter-spacing: 0.15em;
  font-weight: 300;
}

/* ══════════════════════════════════════
   Premium Modal：AI 精批拦截弹窗
══════════════════════════════════════ */

/* 全屏遮罩 */
.premium-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 毛玻璃背景 */
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  animation: overlayFadeIn 0.3s ease forwards;
}

@keyframes overlayFadeIn {
  0%   { opacity: 0; }
  100% { opacity: 1; }
}

/* 弹窗主体 */
.premium-modal {
  position: relative;
  width: 620rpx;
  max-width: 90vw;
  background: rgba(252, 250, 248, 0.95);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32rpx;
  padding: 90rpx 70rpx 70rpx;
  box-shadow: 
    0 24rpx 80rpx rgba(0, 0, 0, 0.35),
    0 0 1px rgba(212, 175, 55, 0.5);
  animation: modalSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes modalSlideIn {
  0%   { transform: scale(0.8) translateY(40rpx); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* 顶部装饰光晕 */
.modal-glow {
  position: absolute;
  top: -60rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 200rpx;
  height: 200rpx;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.3) 0%, transparent 70%);
  pointer-events: none;
}

/* 图标 */
.modal-icon-wrap {
  width: 120rpx;
  height: 120rpx;
  margin: 0 auto 40rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(178, 58, 52, 0.1) 0%, rgba(212, 175, 55, 0.15) 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(212, 175, 55, 0.2);
}

.modal-icon {
  font-size: 64rpx;
  font-weight: 200;
  color: #D4AF37;
}

/* 标题 */
.modal-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 40rpx;
  font-weight: 500;
  color: var(--zen-ink);
  text-align: center;
  letter-spacing: 0.15em;
  margin-bottom: 24rpx;
}

/* 描述 */
.modal-desc {
  display: block;
  font-size: 26rpx;
  color: rgba(51, 51, 51, 0.7);
  text-align: center;
  line-height: 1.8;
  letter-spacing: 0.05em;
  margin-bottom: 60rpx;
}

/* 按钮组 */
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.modal-btn {
  position: relative;
  height: 108rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  border-radius: 20rpx;
  transition: all 0.3s;
}

/* 主按钮（暗金色） */
.modal-btn--primary {
  background: linear-gradient(135deg, #B23A34 0%, #D4AF37 100%);
  border: none;
  box-shadow: 0 12rpx 32rpx rgba(178, 58, 52, 0.35);
}

.modal-btn--primary .btn-icon,
.modal-btn--primary .btn-text {
  color: #fff;
}

/* 次级按钮（霜白色） */
.modal-btn--secondary {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
}

.modal-btn--secondary .btn-icon,
.modal-btn--secondary .btn-text {
  color: rgba(51, 51, 51, 0.7);
}

.btn-hover {
  opacity: 0.8;
  transform: scale(0.98);
}

.btn-icon {
  font-size: 32rpx;
  font-weight: 200;
}

.btn-text {
  font-size: 28rpx;
  letter-spacing: 0.1em;
  font-weight: 300;
}

.btn-hint {
  font-size: 20rpx;
  color: rgba(51, 51, 51, 0.4);
  margin-left: 8rpx;
}

/* 关闭按钮 */
.modal-close {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(51, 51, 51, 0.5);
  font-size: 32rpx;
  transition: all 0.2s;
}

.modal-close:active {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(0.9);
}
</style>
