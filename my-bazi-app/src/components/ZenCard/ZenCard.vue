<template>
  <view 
    class="zen-card" 
    :class="{ 'glass-effect': glass }"
    :style="cardStyle"
  >
    <slot />
  </view>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue'

// 定义 Props
interface Props {
  padding?: string
  margin?: string
  glass?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: '30rpx',
  margin: '0',
  glass: true
})

// 动态计算卡片样式
const cardStyle = computed(() => {
  return {
    padding: props.padding,
    margin: props.margin
  }
})
</script>

<style scoped>
.zen-card {
  /* 新中式卡片基础样式 */
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 32rpx;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

/* 毛玻璃深度效果 */
.zen-card.glass-effect {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 8rpx 32rpx rgba(139, 38, 38, 0.04);
}

/* 悬停效果（PC 端） */
@media (hover: hover) {
  .zen-card:hover {
    border-color: rgba(212, 175, 55, 0.25);
    box-shadow: 0 12rpx 48rpx rgba(139, 38, 38, 0.06);
    transform: translateY(-2rpx);
  }
}

/* 点击效果（移动端） */
.zen-card:active {
  transform: scale(0.98);
}
</style>
