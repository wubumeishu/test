<template>
  <!--
    纸纹背景组件 —— 云端资源优雅方案
    使用 CSS background-image 引用线上 HTTPS 资源
    微信小程序 WXSS 完全支持网络图片 url()
    H5 / 小程序 / App 三端效果完全一致
  -->
  <view class="zen-bg" />
</template>

<script setup lang="ts">
// 纯展示组件，无逻辑
</script>

<style scoped>
.zen-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  opacity: 0.35;
  pointer-events: none;
  background-image: url('/static/handmade-paper.png');
  background-repeat: repeat;
  background-size: auto;
}
</style>
