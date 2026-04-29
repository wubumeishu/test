<template>
  <view class="page-container">
    <ZenHeader title="禅修" />

    <view class="main-content">
      <view class="zen-intro">
        <text class="intro-title">静心禅修</text>
        <text class="intro-subtitle">MINDFUL MEDITATION</text>
        <text class="intro-desc">在喧嚣中寻找内心的宁静，在呼吸间感受生命的律动</text>
      </view>

      <ZenCard padding="50rpx" margin="0 0 40rpx 0">
        <view class="meditation-section">
          <text class="material-symbols-outlined meditation-icon">spa</text>
          <text class="section-label">冥想练习</text>
          <text class="section-hint">即将上线</text>
        </view>
      </ZenCard>

      <ZenCard padding="50rpx" margin="0 0 40rpx 0">
        <view class="meditation-section">
          <text class="material-symbols-outlined meditation-icon">self_improvement</text>
          <text class="section-label">呼吸引导</text>
          <text class="section-hint">即将上线</text>
        </view>
      </ZenCard>

      <ZenCard padding="50rpx" margin="0 0 40rpx 0">
        <view class="meditation-section">
          <text class="material-symbols-outlined meditation-icon">music_note</text>
          <text class="section-label">禅音疗愈</text>
          <text class="section-hint">即将上线</text>
        </view>
      </ZenCard>

      <view class="zen-quote">
        <text>"心若止水，万物自明"</text>
      </view>
    </view>

    <ZenTabBar :current="3" />
  </view>
</template>

<script setup lang="ts">
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import ZenCard from '@/components/ZenCard/ZenCard.vue'
import ZenTabBar from '@/components/ZenTabBar/ZenTabBar.vue'
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&display=swap');

.page-container {
  min-height: 100vh;
  background-color: #F9F6F1;
  background-image: url("https://www.transparenttextures.com/patterns/handmade-paper.png");
}

.main-content {
  padding: 40rpx 40rpx 200rpx;
  max-width: 800px;
  margin: 0 auto;
}

/* 禅修介绍区 */
.zen-intro {
  text-align: center;
  padding: 60rpx 0 80rpx;
}

.intro-title {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 48rpx;
  font-weight: 700;
  color: #2C2C2C;
  letter-spacing: 0.2em;
  margin-bottom: 16rpx;
}

.intro-subtitle {
  display: block;
  font-size: 20rpx;
  color: #B23A34;
  letter-spacing: 0.4em;
  font-weight: 300;
  margin-bottom: 40rpx;
}

.intro-desc {
  display: block;
  font-size: 26rpx;
  color: rgba(51, 51, 51, 0.7);
  line-height: 1.8;
  letter-spacing: 0.1em;
}

/* 冥想模块 */
.meditation-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.meditation-icon {
  font-size: 100rpx;
  color: rgba(178, 58, 52, 0.6);
  margin-bottom: 30rpx;
  font-weight: 200;
}

.section-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 36rpx;
  font-weight: 500;
  color: #2C2C2C;
  letter-spacing: 0.15em;
  margin-bottom: 16rpx;
}

.section-hint {
  font-size: 24rpx;
  color: rgba(51, 51, 51, 0.4);
  letter-spacing: 0.2em;
}

/* 禅语 */
.zen-quote {
  margin-top: 100rpx;
  text-align: center;
}

.zen-quote text {
  font-family: 'Noto Serif SC', serif;
  font-size: 28rpx;
  color: rgba(51, 51, 51, 0.6);
  letter-spacing: 0.3em;
  font-style: italic;
}
</style>
