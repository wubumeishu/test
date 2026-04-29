# TabBar 双导航栏问题修复

## 问题描述

**时间**: 2026-04-28

**问题**: 
- 底部出现了两个导航栏:原生 TabBar 和自定义的毛玻璃 ZenTabBar
- 新建档案页面(子页面)也显示了底部导航栏

**原因**:
1. uni-app 的 `tabBar.custom: true` 只是告诉框架使用自定义 TabBar,但不会自动隐藏原生 TabBar
2. 不同平台(H5/小程序/App)的渲染时机不同,需要多次强制隐藏
3. 非 TabBar 页面(如新建档案页)需要单独处理

---

## 解决方案

### 1. 核心配置 - pages.json

**位置**: `my-bazi-app/src/pages.json`

#### 1.1 确保 tabBar.custom 为 true

```json
{
  "tabBar": {
    "custom": true,  // ✅ 核心配置: 使用自定义 TabBar
    "color": "#999999",
    "selectedColor": "#B23A34",
    "backgroundColor": "#F9F6F1",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页"
      },
      {
        "pagePath": "pages/questions/questions",
        "text": "解惑"
      },
      {
        "pagePath": "pages/zen/zen",
        "text": "禅修"
      },
      {
        "pagePath": "pages/mine/mine",
        "text": "我的"
      }
    ]
  }
}
```

**注意**: 
- ✅ `pages/archive/add` (新建档案) **不在** `tabBar.list` 中
- ✅ `pages/test/test` (测试页) **不在** `tabBar.list` 中
- ✅ 只有主要的 4 个页面在 TabBar 列表中

#### 1.2 配置非 TabBar 页面

```json
{
  "pages": [
    // ... 其他页面
    {
      "path": "pages/archive/add",
      "style": {
        "navigationStyle": "custom",
        "navigationBarTitleText": "新建档案",
        "enablePullDownRefresh": false
      }
    },
    {
      "path": "pages/test/test",
      "style": {
        "navigationBarTitleText": "后端排盘测试",
        "navigationBarBackgroundColor": "#667eea",
        "navigationBarTextStyle": "white"
      }
    }
  ]
}
```

---

### 2. 全局隐藏逻辑 - App.vue

**位置**: `my-bazi-app/src/App.vue`

#### 2.1 强化隐藏函数

```typescript
/**
 * 隐藏原生 TabBar (强化版)
 * 确保在所有平台和所有时机都能彻底隐藏原生 TabBar
 */
const hideNativeTabBar = () => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ 原生 TabBar 已隐藏'),
    fail: (err) => console.log('⚠️ 隐藏 TabBar 失败或当前不在 TabBar 页面', err)
  });
};

/**
 * 强制隐藏原生 TabBar (多次尝试)
 * 用于处理不同平台的异步渲染差异
 */
const forceHideNativeTabBar = () => {
  // 立即执行一次
  hideNativeTabBar();
  
  // 50ms 后再执行一次 (处理异步渲染)
  setTimeout(() => {
    hideNativeTabBar();
  }, 50);
  
  // 100ms 后再执行一次 (确保彻底隐藏)
  setTimeout(() => {
    hideNativeTabBar();
  }, 100);
};
```

#### 2.2 在生命周期中调用

```typescript
onLaunch(() => {
  console.log("App Launch");
  
  // 强制隐藏原生 TabBar (多次尝试)
  forceHideNativeTabBar();
  
  // 其他初始化逻辑...
});

onShow(() => {
  console.log("App Show");
  
  // 有些平台在页面显示后原生 TabBar 会重新计算显示
  // 所以在 onShow 再次强制隐藏
  forceHideNativeTabBar();
});
```

**为什么需要多次调用?**
- ⏱️ **0ms**: 立即隐藏 (处理同步渲染)
- ⏱️ **50ms**: 第二次隐藏 (处理异步渲染)
- ⏱️ **100ms**: 第三次隐藏 (确保彻底隐藏)

**为什么在 onShow 中也要调用?**
- 某些平台(如微信小程序)在页面切换后会重新计算 TabBar 显示状态
- 从后台切换到前台时,原生 TabBar 可能会重新出现
- 在 onShow 中再次强制隐藏可以确保始终使用自定义 TabBar

---

### 3. 页面级别隐藏 - 非 TabBar 页面

#### 3.1 新建档案页面

**位置**: `my-bazi-app/src/pages/archive/add.vue`

```typescript
import { reactive, onMounted } from 'vue'

// 页面加载时确保隐藏 TabBar
onMounted(() => {
  // 这是一个非 TabBar 页面,确保不显示任何底部导航
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [新建档案页] TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [新建档案页] 当前页面无 TabBar')
  })
})
```

#### 3.2 测试页面

**位置**: `my-bazi-app/src/pages/test/test.vue`

```typescript
import { computed, ref, onMounted } from 'vue'

// 页面加载时确保隐藏 TabBar
onMounted(() => {
  // 这是一个非 TabBar 页面,确保不显示任何底部导航
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [测试页] TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [测试页] 当前页面无 TabBar')
  })
})
```

**为什么非 TabBar 页面也要调用?**
- uni-app 的路由机制可能会在页面切换时保留 TabBar 状态
- 显式调用 `hideTabBar` 可以确保这些页面不显示底部导航
- 即使调用失败(页面本身就没有 TabBar)也不会影响功能

---

## 修复效果

### 修复前

```
┌─────────────────────────┐
│      页面内容           │
│                         │
│                         │
├─────────────────────────┤
│  原生 TabBar (白色)     │  ❌ 不需要
├─────────────────────────┤
│  ZenTabBar (毛玻璃)     │  ✅ 需要
└─────────────────────────┘
```

### 修复后

**TabBar 页面** (首页/解惑/禅修/我的):
```
┌─────────────────────────┐
│      页面内容           │
│                         │
│                         │
│                         │
├─────────────────────────┤
│  ZenTabBar (毛玻璃)     │  ✅ 只有自定义 TabBar
└─────────────────────────┘
```

**非 TabBar 页面** (新建档案/测试页):
```
┌─────────────────────────┐
│      页面内容           │
│                         │
│                         │
│                         │
│                         │
│                         │  ✅ 没有任何 TabBar
└─────────────────────────┘
```

---

## 技术原理

### uni-app TabBar 机制

1. **原生 TabBar**:
   - 由 uni-app 框架根据 `pages.json` 中的 `tabBar` 配置自动渲染
   - 性能好,但样式固定,难以自定义

2. **自定义 TabBar**:
   - 设置 `tabBar.custom: true` 后,框架允许使用自定义组件
   - 但**不会自动隐藏**原生 TabBar,需要手动调用 `uni.hideTabBar()`

3. **TabBar 显示逻辑**:
   - 只有在 `tabBar.list` 中的页面才会显示 TabBar
   - 其他页面默认不显示 TabBar
   - 但在某些平台上,页面切换时可能会出现显示异常

### 为什么需要多次隐藏?

**不同平台的渲染时机**:

| 平台 | 渲染时机 | 需要隐藏的时机 |
|------|----------|----------------|
| H5 | 同步渲染 | onLaunch 立即执行 |
| 微信小程序 | 异步渲染 | onLaunch + 延迟执行 |
| App | 混合渲染 | onLaunch + onShow |

**解决方案**:
- 在 `onLaunch` 中立即执行 + 延迟执行 (0ms, 50ms, 100ms)
- 在 `onShow` 中再次执行 (处理页面切换)
- 在非 TabBar 页面的 `onMounted` 中执行 (确保页面级别隐藏)

---

## 验证清单

修复后,检查以下内容:

### TabBar 页面 (首页/解惑/禅修/我的)

- [ ] 只显示一个底部导航栏 (ZenTabBar)
- [ ] 没有原生 TabBar
- [ ] 毛玻璃效果正常
- [ ] 点击切换正常
- [ ] 当前页面高亮正常

### 非 TabBar 页面 (新建档案/测试页)

- [ ] 没有任何底部导航栏
- [ ] 页面内容可以完整显示
- [ ] 返回按钮正常工作
- [ ] 页面切换流畅

### 页面切换

- [ ] TabBar 页面之间切换,导航栏保持显示
- [ ] 从 TabBar 页面跳转到非 TabBar 页面,导航栏消失
- [ ] 从非 TabBar 页面返回 TabBar 页面,导航栏重新显示
- [ ] 从后台切换到前台,导航栏状态正确

### 控制台日志

正常情况下应该看到:
```
App Launch
✅ 原生 TabBar 已隐藏
✅ 原生 TabBar 已隐藏
✅ 原生 TabBar 已隐藏
App Show
✅ 原生 TabBar 已隐藏
✅ 原生 TabBar 已隐藏
✅ 原生 TabBar 已隐藏
```

访问非 TabBar 页面时:
```
✅ [新建档案页] TabBar 已隐藏
```
或
```
ℹ️ [新建档案页] 当前页面无 TabBar
```

---

## 常见问题

### 问题 1: 仍然看到两个导航栏

**可能原因**:
1. 前端服务未重启
2. 浏览器缓存
3. 代码修改未生效

**解决方案**:
```bash
# 1. 停止前端服务 (Ctrl+C)
# 2. 清除缓存
rm -rf node_modules/.vite

# 3. 重新启动
npm run dev:h5

# 4. 清除浏览器缓存 (Ctrl+Shift+Delete)
# 5. 刷新页面 (Ctrl+F5)
```

### 问题 2: 非 TabBar 页面仍显示导航栏

**可能原因**:
1. 页面在 `tabBar.list` 中
2. 页面级别的 `hideTabBar` 未执行

**解决方案**:
1. 检查 `pages.json`,确保页面不在 `tabBar.list` 中
2. 检查页面的 `onMounted` 钩子是否正确执行
3. 查看控制台日志,确认 `hideTabBar` 被调用

### 问题 3: 页面切换时导航栏闪烁

**可能原因**:
1. 隐藏时机太晚
2. 动画效果导致

**解决方案**:
```typescript
// 确保 animation 为 false
uni.hideTabBar({
  animation: false,  // ✅ 关键: 禁用动画
  success: () => console.log('隐藏成功')
})
```

### 问题 4: 小程序平台仍有问题

**可能原因**:
小程序平台的渲染机制与 H5 不同

**解决方案**:
```typescript
// 增加更多延迟尝试
const forceHideNativeTabBar = () => {
  hideNativeTabBar();
  setTimeout(() => hideNativeTabBar(), 50);
  setTimeout(() => hideNativeTabBar(), 100);
  setTimeout(() => hideNativeTabBar(), 200);  // 小程序可能需要更长延迟
  setTimeout(() => hideNativeTabBar(), 500);
};
```

---

## 最佳实践

### 1. 统一的 TabBar 管理

创建一个 TabBar 工具函数:

```typescript
// src/utils/tabbar.ts

/**
 * 隐藏原生 TabBar
 */
export function hideNativeTabBar() {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ TabBar 已隐藏'),
    fail: (err) => console.log('⚠️ TabBar 隐藏失败', err)
  })
}

/**
 * 强制隐藏原生 TabBar (多次尝试)
 */
export function forceHideNativeTabBar() {
  const delays = [0, 50, 100, 200]
  delays.forEach(delay => {
    setTimeout(() => hideNativeTabBar(), delay)
  })
}

/**
 * 显示原生 TabBar (调试用)
 */
export function showNativeTabBar() {
  uni.showTabBar({
    animation: false,
    success: () => console.log('✅ TabBar 已显示'),
    fail: (err) => console.log('⚠️ TabBar 显示失败', err)
  })
}
```

使用:
```typescript
import { forceHideNativeTabBar } from '@/utils/tabbar'

onLaunch(() => {
  forceHideNativeTabBar()
})
```

### 2. 页面级别的 Mixin

创建一个通用的页面 Mixin:

```typescript
// src/mixins/hideTabBar.ts

import { onMounted } from 'vue'

/**
 * 隐藏 TabBar 的 Mixin
 * 用于非 TabBar 页面
 */
export function useHideTabBar(pageName: string) {
  onMounted(() => {
    uni.hideTabBar({
      animation: false,
      success: () => console.log(`✅ [${pageName}] TabBar 已隐藏`),
      fail: () => console.log(`ℹ️ [${pageName}] 当前页面无 TabBar`)
    })
  })
}
```

使用:
```typescript
import { useHideTabBar } from '@/mixins/hideTabBar'

// 在页面中
useHideTabBar('新建档案页')
```

### 3. 条件编译

针对不同平台使用不同的策略:

```typescript
// #ifdef H5
// H5 平台的处理
forceHideNativeTabBar()
// #endif

// #ifdef MP-WEIXIN
// 微信小程序的处理
setTimeout(() => forceHideNativeTabBar(), 200)
// #endif

// #ifdef APP-PLUS
// App 平台的处理
plus.navigator.setStatusBarStyle('dark')
forceHideNativeTabBar()
// #endif
```

---

## 相关文档

- [uni-app TabBar 文档](https://uniapp.dcloud.net.cn/collocation/pages.html#tabbar)
- [uni-app 自定义 TabBar](https://uniapp.dcloud.net.cn/api/ui/tabbar.html)
- [uni-app 生命周期](https://uniapp.dcloud.net.cn/tutorial/page.html#lifecycle)

---

## 修改文件清单

本次修复涉及的文件:

1. ✅ `my-bazi-app/src/pages.json` - 配置 TabBar 和页面
2. ✅ `my-bazi-app/src/App.vue` - 全局隐藏逻辑
3. ✅ `my-bazi-app/src/pages/archive/add.vue` - 新建档案页面级别隐藏
4. ✅ `my-bazi-app/src/pages/test/test.vue` - 测试页面级别隐藏

---

最后更新: 2026-04-28
