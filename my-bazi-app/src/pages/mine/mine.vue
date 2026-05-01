<template>
  <view class="page-container">
    <ZenHeader title="个人中心" />

    <view class="main-content">
      <view class="profile-section">
        <view class="avatar-wrapper">
          <view class="avatar-border">
            <image 
              class="avatar-img" 
              :src="avatarSrc"
              mode="aspectFill"
              @error="onAvatarError"
            ></image>
          </view>
          <view class="edit-badge">
            <text class="material-symbols-outlined edit-icon">edit</text>
          </view>
        </view>
        <text class="user-name">云水禅心</text>
        <text class="user-tag">ZEN PRACTITIONER</text>
      </view>

      <view class="section-container">
        <view class="section-header">
          <text class="section-title">我的档案</text>
          <view class="manage-btn" hover-class="manage-btn-hover" @click="handleManageArchive">
            <text class="manage-btn-text">档案库管理</text>
            <text class="material-symbols-outlined manage-btn-arrow">chevron_right</text>
          </view>
        </view>
        
        <!-- 默认档案卡片：有默认档案时展示 -->
        <ZenCard 
          v-if="archiveStore.defaultArchive"
          padding="36rpx" 
          class="archive-card"
          hover-class="archive-card-hover"
          @click="handleEditArchive(archiveStore.defaultArchive!.id)"
        >
          <!-- 默认档案标识条 -->
          <view class="default-indicator">
            <view class="default-dot"></view>
            <text class="default-label">默认档案</text>
          </view>
          <view class="archive-card-body">
            <view class="archive-icon-wrapper">
              <text class="material-symbols-outlined">person_pin</text>
            </view>
            <view class="archive-info">
              <view class="archive-name-row">
                <text class="archive-name">{{ archiveStore.defaultArchive.name }}</text>
                <text class="gender-chip">{{ archiveStore.defaultArchive.gender === 1 ? '男' : '女' }}</text>
              </view>
              <text class="archive-date">
                {{ archiveStore.defaultArchive.birthDate }} {{ archiveStore.defaultArchive.birthTime }}
              </text>
              <text v-if="archiveStore.defaultArchive.tags?.length" class="archive-tags">
                {{ archiveStore.defaultArchive.tags.join(' · ') }}
              </text>
            </view>
            <text class="material-symbols-outlined arrow-icon">chevron_right</text>
          </view>
        </ZenCard>

        <!-- 空状态：无默认档案时展示 -->
        <view 
          v-else 
          class="archive-empty"
          hover-class="archive-empty-hover"
          @click="handleCreateArchive"
        >
          <text class="material-symbols-outlined empty-icon">person_add</text>
          <text class="empty-text">暂无默认档案，点击去创建</text>
          <text class="material-symbols-outlined empty-arrow">chevron_right</text>
        </view>
      </view>

      <ZenCard padding="0 36rpx" class="menu-group">
        <view class="menu-item" hover-class="menu-item-hover" @click="goToHistory">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">history_edu</text>
            <text class="menu-text">我的测算</text>
          </view>
          <view class="menu-right">
            <text class="menu-hint">{{ recordCount }} 条记录</text>
            <text class="material-symbols-outlined arrow-icon">chevron_right</text>
          </view>
        </view>
        <view class="menu-item" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">bookmark_heart</text>
            <text class="menu-text">我的收藏</text>
          </view>
          <text class="material-symbols-outlined arrow-icon">chevron_right</text>
        </view>
        <view class="menu-item" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">verified_user</text>
            <text class="menu-text">隐私与安全</text>
          </view>
          <text class="material-symbols-outlined arrow-icon">chevron_right</text>
        </view>
        <view class="menu-item border-none" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">tune</text>
            <text class="menu-text">系统设置</text>
          </view>
          <text class="material-symbols-outlined arrow-icon">chevron_right</text>
        </view>
      </ZenCard>

      <ZenCard padding="0 36rpx" class="menu-group">
        <view class="menu-item" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">help_center</text>
            <text class="menu-text">帮助与反馈</text>
          </view>
          <text class="material-symbols-outlined arrow-icon">chevron_right</text>
        </view>
        <view class="menu-item border-none" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">info</text>
            <text class="menu-text">关于我们</text>
          </view>
          <text class="menu-hint">v1.2.4</text>
        </view>
      </ZenCard>

      <view class="footer-quote">
        <text>"随缘自适，烦恼即菩提"</text>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <ZenTabBar :current="4" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
import { useArchiveStore } from '@/store/useArchiveStore'
import { get } from '@/utils/request'

// 初始化 Store
const archiveStore = useArchiveStore()

// ==================== 测算记录数量 ====================
const recordCount = ref(0)

const fetchRecordCount = async () => {
  try {
    const res = await get<{ total: number }>('/api/fortune/records?limit=1&offset=0')
    recordCount.value = res.total ?? 0
  } catch (e) {
    // 静默失败，保持上次数值
    console.warn('⚠️ [mine] 获取测算记录数失败:', e)
  }
}

// ==================== 头像逻辑 ====================

/** 本地兜底头像 */
const DEFAULT_AVATAR = '/static/logo.png'

/**
 * 头像 src：
 * - 优先使用用户自定义头像（后续接入登录后替换）
 * - 默认使用 PNG 格式的 DiceBear 头像（避免小程序/App 不支持 SVG）
 * - 加载失败时自动降级为本地 logo
 */
const avatarSrc = ref('https://api.dicebear.com/7.x/adventurer-neutral/png?seed=Zen')

/** 头像加载失败 → 降级为本地 logo */
const onAvatarError = () => {
  console.warn('⚠️ [mine] 头像加载失败，降级为本地默认头像')
  avatarSrc.value = DEFAULT_AVATAR
}

// 每次页面显示时刷新档案数据和测算记录数
onShow(() => {
  console.log('👤 [mine] 页面显示，刷新档案数据')
  archiveStore.fetchArchives()
  fetchRecordCount()
})

/**
 * 点击档案卡片 → 跳转编辑页
 */
const handleEditArchive = (id: string) => {
  uni.navigateTo({
    url: `/pages/archive/add?id=${id}`
  })
}

/**
 * 空状态点击 → 跳转新建页
 */
const handleCreateArchive = () => {
  uni.navigateTo({
    url: '/pages/archive/add'
  })
}

/**
 * 跳转到档案库管理页面
 */
const handleManageArchive = () => {
  uni.navigateTo({
    url: '/pages/archive/list'
  })
}

/**
 * 跳转到测算历史页面
 */
const goToHistory = () => {
  uni.navigateTo({
    url: '/pages/mine/history'
  })
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Noto+Sans+SC:wght@300;400;500&display=swap');

page {
  --zen-offwhite: #F9F6F1;
  --zen-cinnabar: #B23A34;
  --zen-gold: rgba(212, 175, 55, 1);
  --zen-charcoal: #333333;
  --zen-ink: #1A1A1A;
  --zen-stone: #A8A29E;
  
  background-color: var(--zen-offwhite);
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--zen-charcoal);
}

.page-container {
  min-height: 100vh;
}

.main-content {
  padding: 0 40rpx 120rpx;
  max-width: 800px;
  margin: 0 auto;
}

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 24rpx;
}

.avatar-border {
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.3);
  padding: 8rpx;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  filter: grayscale(0.2);
  background-color: #f0f0f0;
}

.edit-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 56rpx;
  height: 56rpx;
  background-color: #fff;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.05);
}

.edit-icon {
  font-size: 28rpx;
  color: var(--zen-cinnabar);
}

.user-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 42rpx;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--zen-ink);
}

.user-tag {
  font-size: 20rpx;
  color: var(--zen-stone);
  letter-spacing: 0.2em;
  margin-top: 10rpx;
}

.section-container {
  margin-bottom: 40rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 0 10rpx;
}

.section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--zen-charcoal);
  opacity: 0.8;
}

.add-btn {
  font-size: 22rpx;
  color: var(--zen-cinnabar);
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.manage-btn {
  display: flex;
  align-items: center;
  gap: 2rpx;
  padding: 8rpx 0;
}

.manage-btn-hover {
  opacity: 0.6;
}

.manage-btn-text {
  font-size: 24rpx;
  color: #B23A34;
  letter-spacing: 0.05em;
}

.manage-btn-arrow {
  font-size: 28rpx;
  color: #B23A34;
  font-weight: 300;
}

.archive-card {
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  padding: 0 !important;
  cursor: pointer;
}

.archive-card-hover {
  opacity: 0.85;
}

/* 默认档案标识条 */
.default-indicator {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 14rpx 36rpx;
  background: rgba(178, 58, 52, 0.06);
  border-bottom: 1rpx solid rgba(178, 58, 52, 0.1);
}

.default-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: var(--zen-cinnabar);
}

.default-label {
  font-size: 20rpx;
  color: var(--zen-cinnabar);
  font-weight: 500;
  letter-spacing: 0.1em;
}

/* 卡片主体 */
.archive-card-body {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 36rpx;
}

.archive-icon-wrapper {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: rgba(178, 58, 52, 0.06);
  color: var(--zen-cinnabar);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.archive-info {
  flex: 1;
}

.archive-name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 10rpx;
}

.archive-name {
  font-size: 32rpx;
  font-weight: 500;
  color: var(--zen-ink);
}

.gender-chip {
  font-size: 20rpx;
  padding: 2rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(178, 58, 52, 0.08);
  color: var(--zen-cinnabar);
}

.archive-date {
  font-size: 24rpx;
  color: var(--zen-stone);
  display: block;
}

.archive-tags {
  font-size: 22rpx;
  color: var(--zen-stone);
  margin-top: 6rpx;
  display: block;
  opacity: 0.7;
}

/* 空状态 */
.archive-empty {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 40rpx 36rpx;
  background: rgba(178, 58, 52, 0.03);
  border: 1rpx dashed rgba(178, 58, 52, 0.25);
  border-radius: 16rpx;
}

.archive-empty-hover {
  opacity: 0.7;
}

.empty-icon {
  font-size: 48rpx;
  color: rgba(178, 58, 52, 0.4);
  font-weight: 200;
}

.empty-text {
  flex: 1;
  font-size: 28rpx;
  color: rgba(178, 58, 52, 0.6);
  letter-spacing: 0.05em;
}

.empty-arrow {
  font-size: 36rpx;
  color: rgba(178, 58, 52, 0.3);
}

.menu-group {
  margin-bottom: 40rpx;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 0;
  border-bottom: 1px solid rgba(212, 175, 55, 0.08);
}

.menu-item.border-none {
  border-bottom: none;
}

.menu-item-hover {
  opacity: 0.7;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.menu-icon {
  color: rgba(178, 58, 52, 0.65);
  font-size: 42rpx;
}

.menu-text {
  font-size: 30rpx;
  font-weight: 500;
  letter-spacing: 0.1em;
}

.menu-right {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.menu-hint {
  font-size: 22rpx;
  color: var(--zen-stone);
}

.arrow-icon {
  color: var(--zen-stone);
  opacity: 0.6;
  font-size: 42rpx;
}

.footer-quote {
  margin-top: 100rpx;
  margin-bottom: 60rpx;
  text-align: center;
}

.footer-quote text {
  font-size: 22rpx;
  color: var(--zen-stone);
  letter-spacing: 0.35em;
  font-family: 'Noto Serif SC', serif;
  font-style: italic;
}
</style>
