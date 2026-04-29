<template>
  <view class="page-container">
    <ZenHeader title="个人中心" />

    <view class="main-content">
      <view class="profile-section">
        <view class="avatar-wrapper">
          <view class="avatar-border">
            <image 
              class="avatar-img" 
              src="https://api.dicebear.com/7.x/adventurer-neutral/svg?seed=Zen" 
              mode="aspectFill"
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
          <view class="add-btn" @click="handleAddArchive">
            <text class="material-symbols-outlined text-xs">add</text>
            <text>添加档案</text>
          </view>
        </view>
        
        <ZenCard padding="36rpx" class="archive-card">
          <view class="archive-icon-wrapper">
            <text class="material-symbols-outlined">person_pin</text>
          </view>
          <view class="archive-info">
            <view class="archive-name-row">
              <text class="archive-name">{{ archiveStore.currentArchive?.name || '本人档案' }}</text>
              <text v-if="archiveStore.currentArchive?.isDefault" class="default-badge">默认</text>
            </view>
            <text class="archive-date">{{ archiveStore.currentArchive ? (archiveStore.currentArchive.birthDate + ' ' + archiveStore.currentArchive.birthTime) : '暂无出生数据' }}</text>
          </view>
          <text class="material-symbols-outlined arrow-icon">chevron_right</text>
        </ZenCard>
      </view>

      <ZenCard padding="0 36rpx" class="menu-group">
        <view class="menu-item" hover-class="menu-item-hover">
          <view class="menu-left">
            <text class="material-symbols-outlined menu-icon">history_edu</text>
            <text class="menu-text">我的测算</text>
          </view>
          <view class="menu-right">
            <text class="menu-hint">12条记录</text>
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
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
import { useArchiveStore } from '@/store/useArchiveStore'

// 初始化 Store
const archiveStore = useArchiveStore()

/**
 * 跳转到添加档案页面
 */
const handleAddArchive = () => {
  uni.navigateTo({
    url: '/pages/archive/add'
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

.archive-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
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
}

.archive-info {
  flex: 1;
}

.archive-name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.archive-name {
  font-size: 32rpx;
  font-weight: 500;
  color: var(--zen-ink);
}

.default-badge {
  font-size: 20rpx;
  padding: 2rpx 14rpx;
  border-radius: 8rpx;
  border: 1px solid rgba(178, 58, 52, 0.25);
  color: var(--zen-cinnabar);
}

.archive-date {
  font-size: 24rpx;
  color: var(--zen-stone);
  margin-top: 10rpx;
  display: block;
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
