<template>
  <view class="tabbar-wrapper">
    <view class="tabbar-container">
      <view class="tab-item" :class="{ active: current === 0 }" @click="switchTab('/pages/index/index')">
        <text class="material-symbols-outlined tab-icon">home</text>
        <text class="tab-text">首页</text>
      </view>

      <view class="tab-item" :class="{ active: current === 1 }" @click="switchTab('/pages/questions/questions')">
        <text class="material-symbols-outlined tab-icon">auto_stories</text>
        <text class="tab-text">解惑</text>
      </view>

      <view class="tab-item center-wrapper" @click="onCenterClick">
        <view class="center-btn">
          <text class="material-symbols-outlined center-icon">flare</text>
        </view>
      </view>

      <view class="tab-item" :class="{ active: current === 3 }" @click="switchTab('/pages/zen/zen')">
        <text class="material-symbols-outlined tab-icon">self_improvement</text>
        <text class="tab-text">禅修</text>
      </view>

      <view class="tab-item" :class="{ active: current === 4 }" @click="switchTab('/pages/mine/mine')">
        <text class="material-symbols-outlined tab-icon">person</text>
        <text class="tab-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { defineProps, onMounted } from 'vue'

const props = defineProps({
  // 当前高亮的索引 (0:首页, 1:解惑, 3:禅修, 4:我的)
  // 注意：索引 2 被中心按钮占据
  current: {
    type: Number,
    default: 0
  }
})

/**
 * 组件挂载时强制隐藏原生 TabBar
 * 防止原生 TabBar 在页面切换时"复活"
 */
onMounted(() => {
  // #ifdef H5
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [ZenTabBar] 原生 TabBar 已强制隐藏'),
    fail: () => console.log('ℹ️ [ZenTabBar] 当前页面无原生 TabBar')
  })
  // #endif
})

/**
 * 切换 Tab 页面
 * 使用 uni.switchTab 确保正确的页面跳转
 */
const switchTab = (path: string) => {
  uni.switchTab({ 
    url: path,
    fail: (err) => {
      console.error('Tab 切换失败:', err)
      // 如果 switchTab 失败，尝试使用 navigateTo
      uni.navigateTo({ url: path })
    }
  })
}

/**
 * 中心按钮点击事件
 * 用于触发核心功能（如快速排盘）
 */
const onCenterClick = () => {
  uni.showToast({ 
    title: '灵光一现：快速排盘', 
    icon: 'none',
    duration: 1500
  })
  // 未来可以跳转到快速排盘页面
  // uni.navigateTo({ url: '/pages/quick-bazi/quick-bazi' })
}
</script>

<style scoped>
/* 引入材质图标 (如果全局已引入可删除此行) */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');

/* 底部安全区与悬浮定位 */
.tabbar-wrapper {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  /* iPhone 底部小黑条适配 */
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
  display: flex;
  justify-content: center;
  z-index: 999;
  pointer-events: none; /* 让wrapper不遮挡背后的点击事件 */
}

/* 毛玻璃主容器 - 深度优化通透质感 */
.tabbar-container {
  pointer-events: auto; /* 恢复容器的点击事件 */
  width: 85%;
  max-width: 400px; /* 适配 PC 端 */
  height: 112rpx;
  /* 增强通透感：更透明的背景 */
  background-color: rgba(255, 255, 255, 0.4);
  /* 滤镜升级：更强的模糊 + 饱和度提升 */
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  /* 高光边缘：细腻的白色半透明边框，模拟玻璃折射 */
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 40rpx;
  /* 阴影优化：极淡的扩散阴影 */
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 10rpx;
  box-sizing: border-box;
}

/* 常规 Tab 项 */
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(51, 51, 51, 0.4);
  transition: all 0.3s ease;
  height: 100%;
}

.tab-icon {
  font-size: 44rpx;
  margin-bottom: 4rpx;
}

.tab-text {
  font-size: 18rpx;
  font-weight: 500;
  letter-spacing: -0.5px;
}

/* 选中状态：变为朱砂红 */
.tab-item.active {
  color: #B23A34;
}

/* ================================= */
/* 中心凸出大按钮特效 */
/* ================================= */
.center-wrapper {
  position: relative;
  flex: 1.2; /* 给中间留出稍微多一点的空间 */
}

.center-btn {
  position: absolute;
  top: -60rpx; /* 向上凸出 */
  left: 50%;
  transform: translateX(-50%);
  width: 100rpx;
  height: 100rpx;
  background-color: #B23A34; /* 朱砂红 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 宣纸白边框，制造与导航栏断开的错觉 */
  border: 8rpx solid #F9F6F1; 
  /* 外发光效果：模拟能量内核 */
  box-shadow: 
    0 10rpx 30rpx rgba(178, 58, 52, 0.4),
    0 0 40rpx rgba(178, 58, 52, 0.2);
  transition: transform 0.2s, box-shadow 0.3s;
}

.center-btn:active {
  transform: translateX(-50%) scale(0.95);
  /* 点击时增强发光效果 */
  box-shadow: 
    0 10rpx 30rpx rgba(178, 58, 52, 0.6),
    0 0 50rpx rgba(178, 58, 52, 0.3);
}

.center-icon {
  color: #FFFFFF;
  font-size: 50rpx;
}
</style>