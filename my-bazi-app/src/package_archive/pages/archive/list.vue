<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader title="档案库" :show-back="true" />

    <main class="main-content">
      <!-- 新建档案入口 -->
      <view class="create-archive-card" hover-class="card-hover" @click="handleAdd">
        <text class="material-symbols-outlined add-icon">add_circle</text>
        <text class="create-text">新建并保存档案</text>
      </view>

      <!-- 空状态 -->
      <view v-if="archiveStore.archives.length === 0" class="empty-state">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无档案</text>
        <text class="empty-hint">点击上方按钮创建第一个档案</text>
      </view>

      <!-- 档案列表 -->
      <view v-else class="archive-list">
        <view 
          v-for="archive in sortedList" 
          :key="archive.id"
          class="list-archive-card"
          hover-class="list-card-hover"
        >
          <!-- 左侧信息区 -->
          <view class="list-card-left">
            <view class="list-name-row">
              <text class="list-archive-name">{{ archive.name }}</text>
              <text class="list-gender-tag">{{ archive.gender === 1 ? '男' : '女' }}</text>
            </view>
            
            <view class="list-info-row">
              <text class="list-relation-tag">{{ archive.tags && archive.tags.length > 0 ? archive.tags[0] : '—' }}</text>
              <text v-if="archiveStore.defaultArchive && archive.id === archiveStore.defaultArchive.id" class="list-default-badge">默认</text>
            </view>
            
            <!-- 双历法显示 -->
            <view class="list-date-block">
              <text class="list-date-solar">阳历：{{ formatBirthDate(archive.birthDate, archive.birthTime).solar }}</text>
              <text class="list-date-lunar">农历：{{ formatBirthDate(archive.birthDate, archive.birthTime).lunar }}</text>
            </view>
          </view>

          <!-- 右侧操作区 -->
          <view class="list-card-right">
            <view 
              class="list-action-btn list-edit-btn" 
              hover-class="list-btn-hover"
              @click.stop="handleEdit(archive.id)"
            >
              <text class="material-symbols-outlined list-btn-icon">edit</text>
            </view>
            
            <view 
              class="list-action-btn list-delete-btn" 
              hover-class="list-btn-hover"
              @click.stop="handleDelete(archive.id, archive.name)"
            >
              <text class="material-symbols-outlined list-btn-icon">delete</text>
            </view>
          </view>
        </view>
      </view>
    </main>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import { Solar } from 'lunar-javascript'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useArchiveStore } from '@/store/useArchiveStore'

// 引入 Store
const archiveStore = useArchiveStore()

// 本地排序：默认档案置顶，其余按 updatedAt 降序
// 基于 archiveStore.archives 派生，与 v-if 用同一数据源，避免时序问题
const sortedList = computed(() => {
  return [...archiveStore.archives].sort((a, b) => {
    if (a.isDefault !== b.isDefault) return a.isDefault ? -1 : 1
    return (b.updatedAt ?? b.createdAt) - (a.updatedAt ?? a.createdAt)
  })
})

// 防止 onShow 重复触发时并发请求
let fetchTimer: ReturnType<typeof setTimeout> | null = null

// 地支时辰对照表（按小时 0-23）
const DIZHI_HOURS = [
  '子', '丑', '丑', '寅', '寅', '卯',
  '卯', '辰', '辰', '巳', '巳', '午',
  '午', '未', '未', '申', '申', '酉',
  '酉', '戌', '戌', '亥', '亥', '子'
]

/**
 * 将 birthDate (YYYY-MM-DD) + birthTime (HH:mm) 转换为双历法显示字符串
 * 返回 { solar: string, lunar: string }
 */
const formatBirthDate = (birthDate: string, birthTime: string) => {
  if (!birthDate || !birthTime) {
    return { solar: '—', lunar: '—' }
  }

  try {
    const [year, month, day] = birthDate.split('-').map(Number)
    const [hour, minute] = birthTime.split(':').map(Number)

    // 阳历格式：YYYY年MM月DD日 HH:mm
    const solar = `${year}年${String(month).padStart(2, '0')}月${String(day).padStart(2, '0')}日 ${birthTime}`

    // 农历转换
    const solarObj = Solar.fromYmd(year, month, day)
    const lunarObj = solarObj.getLunar()

    const lunarYear = lunarObj.getYear()
    const lunarMonth = lunarObj.getMonthInChinese()
    const lunarDay = lunarObj.getDayInChinese()
    const dizhi = DIZHI_HOURS[hour] ?? '子'

    const lunar = `${lunarYear}年${lunarMonth}月${lunarDay} ${dizhi}时`

    return { solar, lunar }
  } catch (e) {
    console.error('农历转换失败:', e)
    return { solar: birthDate + ' ' + birthTime, lunar: '—' }
  }
}

// 页面显示时刷新数据
onShow(() => {
  // 防抖：延迟 100ms 执行，避免页面切换时并发触发
  if (fetchTimer) clearTimeout(fetchTimer)
  fetchTimer = setTimeout(() => {
    archiveStore.fetchArchives()
  }, 100)

  // 强制隐藏原生 TabBar
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [archive/list] 原生 TabBar 已隐藏'),
    fail: () => {}
  })
})

// 添加新档案
const handleAdd = () => {
  uni.navigateTo({ url: '/package_archive/pages/archive/add' })
}

// 编辑档案
const handleEdit = (id: string) => {
  uni.navigateTo({ url: `/package_archive/pages/archive/add?id=${id}` })
}

// 删除档案
const handleDelete = (id: string, name: string) => {
  uni.showModal({
    title: '确认删除',
    content: `是否不可恢复地删除档案「${name}」？`,
    confirmText: '删除',
    confirmColor: '#B22222',
    cancelText: '取消',
    success: async (res) => {
      if (res.confirm) {
        await archiveStore.deleteArchive(id)
      }
    }
  })
}
</script>

<style>
/* 页面样式 */

/* 全局变量 */
.page-container {
  --zen-bg: #F9F6F0;
  --zen-white: #FFFFFF;
  --zen-ink: #333333;
  --zen-gray: #666666;
  --zen-light-gray: #999999;
  --zen-border: #E8E8E8;
  --zen-cinnabar: #8B2626;
  --zen-cinnabar-light: #FFF5F5;
  --zen-glass: rgba(255, 255, 255, 0.6);
  
  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: 'Inter', 'Noto Serif SC', system-ui, sans-serif;
  color: var(--zen-ink);
}

/* 主内容区 */
.main-content {
  padding: 32rpx 40rpx 40rpx 40rpx;
}

/* 新建档案卡片 */
.create-archive-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  padding: 40rpx;
  background-color: var(--zen-white);
  border: 2px dashed var(--zen-border);
  border-radius: 16rpx;
  margin-bottom: 40rpx;
  transition: all 0.3s ease;
}

.card-hover {
  background-color: rgba(249, 246, 240, 0.5);
  transform: scale(0.98);
}

.add-icon {
  font-size: 48rpx;
  color: var(--zen-cinnabar);
  font-weight: 200;
}

.create-text {
  font-size: 28rpx;
  color: var(--zen-cinnabar);
  letter-spacing: 2rpx;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 40rpx;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 40rpx;
  opacity: 0.3;
}

.empty-text {
  font-size: 32rpx;
  color: var(--zen-gray);
  margin-bottom: 16rpx;
  letter-spacing: 2rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: var(--zen-light-gray);
  letter-spacing: 1rpx;
}

/* 档案列表 */
.archive-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

/* 档案卡片 */
.list-archive-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  background-color: #FFFFFF;
  border-radius: 16rpx;
  padding: 40rpx 36rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  margin-bottom: 24rpx;
  transition: all 0.3s ease;
}

.list-archive-card:last-child {
  margin-bottom: 0;
}

.list-card-hover {
  opacity: 0.9;
}

/* 左侧信息区 */
.list-card-left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding-right: 24rpx;
  align-self: center;
}

.list-name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex-wrap: nowrap;
}

.list-archive-name {
  font-size: 34rpx;
  font-weight: 500;
  color: #333333;
  letter-spacing: 2rpx;
  flex-shrink: 0;
  max-width: 280rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-gender-tag {
  font-size: 20rpx;
  font-weight: 500;
  color: #8B2626;
  padding: 4rpx 14rpx;
  background: #FFF5F5;
  border-radius: 6rpx;
  letter-spacing: 1rpx;
  flex-shrink: 0;
}

.list-info-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10rpx;
}

.list-relation-tag {
  font-size: 22rpx;
  color: #666666;
  padding: 4rpx 16rpx;
  background: rgba(249, 246, 240, 0.8);
  border: 1px solid #E8E8E8;
  border-radius: 6rpx;
  letter-spacing: 1rpx;
}

.list-default-badge {
  font-size: 20rpx;
  color: #8B2626;
  padding: 4rpx 12rpx;
  background: #FFF5F5;
  border: 1px solid #8B2626;
  border-radius: 6rpx;
  letter-spacing: 1rpx;
}

/* 双历法日期块 */
.list-date-block {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.list-date-solar {
  font-size: 22rpx;
  color: #666666;
  line-height: 1.5;
}

.list-date-lunar {
  font-size: 20rpx;
  color: #999999;
  line-height: 1.5;
}

/* 右侧操作区 */
.list-card-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  align-self: center;
}

.list-action-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.list-edit-btn {
  background: rgba(249, 246, 240, 0.8);
  border: 1px solid #E8E8E8;
}

.list-delete-btn {
  background: rgba(178, 34, 34, 0.05);
  border: 1px solid rgba(178, 34, 34, 0.2);
}

.list-btn-hover {
  opacity: 0.7;
}

.list-btn-icon {
  font-size: 40rpx;
  font-weight: 200;
}

.list-edit-btn .list-btn-icon {
  color: #666666;
}

.list-delete-btn .list-btn-icon {
  color: #B22222;
}
</style>
