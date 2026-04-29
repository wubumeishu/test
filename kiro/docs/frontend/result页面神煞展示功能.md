# result 页面神煞展示功能实现

## 修改时间
2026-04-29

## 修改目标
在前端 `result.vue` 页面的四柱命盘中，在纳音下方添加神煞展示区域，展示后端传递的神煞数据。

## 修改内容

### 1. 修改 `<script setup>` 中的 `pillarList` 计算属性

在每个柱子的数据对象中添加 `shensha` 字段：

```typescript
{
  title: '年柱',
  gan: data.year_pillar.gan,
  zhi: data.year_pillar.zhi,
  nayin: data.year_pillar.nayin,
  canggan: data.year_pillar.canggan || [],
  shishen: data.year_pillar.shishen || '-',
  changsheng: data.year_pillar.changsheng || '-',
  canggan_shishen: data.year_pillar.canggan_shishen || [],
  shensha: data.year_pillar.shensha || [],  // ✅ 新增
  isDayMaster: false
}
```

### 2. 修改 `<template>` 模板

在纳音 (`nayin-cell`) 下方添加神煞展示容器：

```vue
<!-- 神煞 -->
<view class="cell shensha-cell">
  <view class="shensha-box">
    <template v-if="pillar.shensha && pillar.shensha.length > 0">
      <text 
        v-for="(ss, ssIndex) in pillar.shensha" 
        :key="'ss' + ssIndex" 
        class="ss-tag"
      >
        {{ ss }}
      </text>
    </template>
    <text v-else class="ss-empty">-</text>
  </view>
</view>
```

**关键点**：
- 使用 `v-for` 循环遍历 `pillar.shensha` 数组
- 如果神煞数组为空或不存在，显示 `-`
- 每个神煞用 `.ss-tag` 样式包裹，形成小标签效果

### 3. 修改 `<style>` 样式

添加神煞容器和标签样式：

```css
/* 神煞 - 固定高度防止错位 */
.shensha-cell {
  padding: 12rpx 8rpx;
  min-height: 120rpx;
  background: rgba(0, 0, 0, 0.01);
}

.shensha-box {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-start;
  align-content: flex-start;
  height: 120rpx; /* 稍微增加一点高度，增加手指触控滑动的面积 */
  margin-top: 12rpx;
  gap: 6rpx;
  overflow-y: auto; /* 开启垂直滑动 */
  -webkit-overflow-scrolling: touch; /* 移动端惯性滑动 */
}

/* 彻底隐藏由于开启滑动而出现的丑陋滚动条 */
.shensha-box::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  color: transparent;
}

.ss-tag {
  font-size: 20rpx;
  color: #7f8c8d;
  background-color: rgba(0, 0, 0, 0.04);
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  line-height: 1.2;
  white-space: nowrap;
}

.ss-empty {
  font-size: 20rpx;
  color: #ccc;
}
```

**设计要点**：
- **固定高度**：`shensha-box` 高度固定为 `120rpx`，确保即使神煞数量不同也不会导致四柱错位
- **垂直滑动**：使用 `overflow-y: auto` 支持神煞过多时内部滑动
- **移动端优化**：`-webkit-overflow-scrolling: touch` 提供 iOS 惯性滑动体验
- **隐藏滚动条**：使用 `::-webkit-scrollbar` 伪类彻底隐藏滚动条，保持极简美观
- **自动换行**：使用 `flex-wrap: wrap` 让神煞标签自动换行
- **低饱和度颜色**：神煞标签使用灰色系 `#7f8c8d`，保持禅意风格
- **小标签样式**：圆角、浅色背景，视觉上轻盈不抢眼

## 数据来源

神煞数据由后端 API 提供：
- **日柱神煞**：吉神 + 凶煞 + 天神（约 10 个）
- **时柱神煞**：天神（约 1 个）
- **年柱和月柱**：lunar-python 未提供方法，返回空数组

## 视觉效果

- 神煞以小标签形式展示，灰色背景，低调不抢眼
- 多个神煞自动换行，整齐排列
- **神煞过多时支持内部垂直滑动**，滚动条完全隐藏
- **iOS 端惯性滑动**，触控体验流畅自然
- 固定高度确保四柱垂直对齐完美
- 无神煞时显示 `-`，保持视觉一致性

## 交互优化

- **触控滑动**：神煞超过容器高度时，用户可以在神煞区域内上下滑动查看
- **隐藏滚动条**：使用 `::-webkit-scrollbar` 伪类彻底隐藏滚动条，保持界面极简美观
- **惯性滑动**：iOS 端使用 `-webkit-overflow-scrolling: touch` 提供原生般的滑动体验
- **固定高度**：容器高度固定为 `120rpx`，确保四柱对齐不受神煞数量影响

## 测试建议

1. 测试日柱神煞展示（应有多个标签）
2. 测试时柱神煞展示（应有 1 个标签）
3. 测试年柱和月柱（应显示 `-`）
4. **测试神煞过多时的内部滑动效果**（手指在神煞区域上下滑动）
5. **验证滚动条是否完全隐藏**（保持界面极简美观）
6. **测试 iOS 端惯性滑动体验**（滑动是否流畅自然）
7. 验证四柱垂直对齐是否完美（神煞数量不同时）

## 相关文件

- **前端页面**：`my-bazi-app/src/pages/result/result.vue`
- **后端引擎**：`bazi-admin/src/services/bazi_engine.py`
- **后端 Schema**：`bazi-admin/src/schemas/bazi.py`
- **后端路由**：`bazi-admin/src/routers/fortune.py`

---

**状态**：✅ 已完成
**下一步**：前后端联调测试，验证神煞数据正确展示
