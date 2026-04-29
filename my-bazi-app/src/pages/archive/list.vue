<template>
  <view class="page-container">
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
          v-for="archive in archiveStore.archives" 
          :key="archive.id"
          class="archive-card"
          hover-class="card-hover"
        >
          <!-- 左侧信息区 -->
          <view class="card-left">
            <view class="name-row">
              <text class="archive-name">{{ archive.name }}</text>
              <text class="gender-icon">{{ archive.gender === 1 ? '乾' : '坤' }}</text>
            </view>
            
            <view class="info-row">
              <text class="relation-tag">{{ archive.relation || '本人' }}</text>
              <text v-if="archive.isDefault" class="default-badge">默认</text>
            </view>
            
            <view class="time-row">
              <text class="time-text">公历：{{ archive.birthDate }} {{ archive.birthTime }}</text>
            </view>
          </view>

          <!-- 右侧操作区 -->
          <view class="card-right">
            <view 
              class="action-btn edit-btn" 
              hover-class="btn-hover"
              @click.stop="handleEdit(archive.id)"
            >
              <text class="material-symbols-outlined btn-icon">edit</text>
            </view>
            
            <view 
              class="action-btn delete-btn" 
              hover-class="btn-hover"
              @click.stop="handleDelete(archive.id, archive.name)"
            >
              <text class="material-symbols-outlined btn-icon">delete</text>
            </view>
          </view>
        </view>
      </view>
    </main>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useArchiveStore } from '@/store/useArchiveStore'

// 引入 Store
const archiveStore = useArchiveStore()

// 页面显示时刷新数据
onShow(() => {
  console.log('📋 [archive/list] 页面显示，刷新档案列表')
  archiveStore.fetchArchives()
  
  // 强制隐藏原生 TabBar
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [archive/list] 原生 TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [archive/list] 当前页面无 TabBar')
  })
})

// 添加新档案
const handleAdd = () => {
  console.log('➕ [archive/list] 跳转到添加页面')
  uni.navigateTo({
    url: '/pages/archive/add'
  })
}

// 编辑档案
const handleEdit = (id: string) => {
  console.log('✏️ [archive/list] 编辑档案:', id)
  uni.navigateTo({
    url: `/pages/archive/add?id=${id}`
  })
}

// 删除档案
const handleDelete = (id: string, name: string) => {
  console.log('🗑️ [archive/list] 删除档案:', id, name)
  
  uni.showModal({
    title: '确认删除',
    content: `是否不可恢复地删除档案「${name}」？`,
    confirmText: '删除',
    confirmColor: '#B22222',
    cancelText: '取消',
    success: async (res) => {
      if (res.confirm) {
        console.log('🗑️ [archive/list] 用户确认删除')
        await archiveStore.deleteArchive(id)
      } else {
        console.log('❌ [archive/list] 用户取消删除')
      }
    }
  })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

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
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
  font-family: 'Inter', 'Noto Serif SC', system-ui, sans-serif;
  color: var(--zen-ink);
}

/* 主内容区 */
.main-content {
  padding: 40rpx;
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
.archive-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--zen-white);
  border-radius: 16rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.archive-card:hover {
  transform: scale(0.98);
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

/* 左侧信息区 */
.card-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.archive-name {
  font-size: 36rpx;
  font-weight: 500;
  color: var(--zen-ink);
  letter-spacing: 2rpx;
}

.gender-icon {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  font-weight: 700;
  color: var(--zen-cinnabar);
  padding: 4rpx 12rpx;
  background: var(--zen-cinnabar-light);
  border-radius: 6rpx;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.relation-tag {
  font-size: 24rpx;
  color: var(--zen-gray);
  padding: 4rpx 16rpx;
  background: rgba(249, 246, 240, 0.8);
  border: 1px solid var(--zen-border);
  border-radius: 6rpx;
  letter-spacing: 1rpx;
}

.default-badge {
  font-size: 22rpx;
  color: var(--zen-cinnabar);
  padding: 4rpx 12rpx;
  background: var(--zen-cinnabar-light);
  border: 1px solid var(--zen-cinnabar);
  border-radius: 6rpx;
  letter-spacing: 1rpx;
}

.time-row {
  display: flex;
  align-items: center;
}

.time-text {
  font-size: 24rpx;
  color: var(--zen-light-gray);
  letter-spacing: 1rpx;
}

/* 右侧操作区 */
.card-right {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-left: 24rpx;
}

.action-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.edit-btn {
  background: linear-gradient(135deg, rgba(249, 246, 240, 0.8), rgba(255, 255, 255, 0.6));
  border: 1px solid var(--zen-border);
}

.delete-btn {
  background: rgba(178, 34, 34, 0.05);
  border: 1px solid rgba(178, 34, 34, 0.2);
}

.btn-hover {
  opacity: 0.7;
  transform: scale(0.95);
}

.btn-icon {
  font-size: 40rpx;
  font-weight: 200;
}

.edit-btn .btn-icon {
  color: var(--zen-gray);
}

.delete-btn .btn-icon {
  color: #B22222;
}
</style>
