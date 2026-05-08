<template>
  <view class="zen-header">
    <view class="header-content">
      <!-- 左侧：返回或菜单图标 -->
      <view class="left-section">
        <view v-if="showBack" class="icon-btn" @click="handleBack">
          <text class="material-symbols-outlined">arrow_back</text>
        </view>
        <view v-else-if="showMenu" class="icon-btn" @click="handleMenu">
          <text class="material-symbols-outlined">menu</text>
        </view>
        <view v-else class="icon-placeholder"></view>
      </view>

      <!-- 中间：标题 -->
      <view class="title-section">
        <text class="header-title">{{ title }}</text>
      </view>

      <!-- 右侧：历史记录图标 -->
      <view class="right-section">
        <view v-if="showHistory" class="icon-btn" @click="handleHistory">
          <text class="material-symbols-outlined">history</text>
        </view>
        <view v-else class="icon-placeholder"></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

// 配置组件选项：关闭样式隔离，允许父组件样式穿透
defineOptions({
  options: {
    styleIsolation: 'shared'
  }
})

// 定义 Props
interface Props {
  title: string
  showBack?: boolean
  showMenu?: boolean
  showHistory?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBack: false,
  showMenu: false,
  showHistory: false
})

// 定义 Emits
const emit = defineEmits<{
  menu: []
  history: []
}>()

// 返回上一页，如果页面栈只有一层则跳回「我的」Tab
const handleBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    // 页面栈只有一层，无法 navigateBack，跳回「我的」页
    uni.switchTab({ url: '/pages/mine/mine' })
  }
}

// 触发菜单事件
const handleMenu = () => {
  emit('menu')
}

// 触发历史记录事件
const handleHistory = () => {
  emit('history')
}
</script>

<style scoped>
/* 页面样式 - Material Symbols 图标字体已在 App.vue 全局定义 */

.zen-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(249, 246, 241, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(139, 38, 38, 0.08);
  padding-top: calc(var(--status-bar-height) + 20rpx);
  padding-bottom: 20rpx;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40rpx;
  height: 88rpx;
}

/* 左侧区域 */
.left-section {
  flex: 0 0 80rpx;
  display: flex;
  align-items: center;
}

/* 中间标题区域 */
.title-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  font-family: 'STSong', 'SimSun', 'Songti SC', 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.2em;
}

/* 右侧区域 */
.right-section {
  flex: 0 0 80rpx;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

/* 图标按钮 */
.icon-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.3s;
}

.icon-btn:active {
  opacity: 0.6;
}

.icon-btn .material-symbols-outlined {
  font-size: 48rpx;
  font-weight: 300;
  color: #2C2C2C;
}

/* 占位符（保持布局平衡） */
.icon-placeholder {
  width: 72rpx;
  height: 72rpx;
}
</style>
