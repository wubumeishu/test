<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { get } from "./utils/request";
import { useBaziStore } from "./store/useBaziStore";

const baziStore = useBaziStore();

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

onLaunch(() => {
  console.log("App Launch");
  
  // 强制隐藏原生 TabBar (多次尝试)
  forceHideNativeTabBar();
  
  // 测试后端连通性
  testBackendConnection();
  
  // 加载历史记录
  baziStore.loadFromLocalStorage();
});

onShow(() => {
  console.log("App Show");
  
  // 有些平台在页面显示后原生 TabBar 会重新计算显示
  // 所以在 onShow 再次强制隐藏
  forceHideNativeTabBar();
  
  // H5 平台版本检测（每次页面显示时检测）
  // #ifdef H5
  checkUpdate();
  // #endif
});

onHide(() => {
  console.log("App Hide");
});

/**
 * 测试后端连接
 */
async function testBackendConnection() {
  try {
    console.log("正在测试后端连接...");
    const response = await get("/api/health");
    console.log("✅ 后端连接成功！", response);
    console.log("状态:", response.status);
    console.log("消息:", response.message);
  } catch (error) {
    console.error("❌ 后端连接失败:", error);
  }
}

/**
 * 版本检测与强制更新（仅 H5 平台）
 * 每次页面显示时静默检查更新
 */
// #ifdef H5
async function checkUpdate() {
  try {
    // 加上时间戳防止请求到缓存的 version.json
    const timestamp = new Date().getTime();
    const response = await fetch(`/version.json?t=${timestamp}`);
    
    // 检查响应状态
    if (!response.ok) {
      console.warn('⚠️ [版本检测] version.json 文件不存在或无法访问');
      return;
    }
    
    // 检查响应类型
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.warn('⚠️ [版本检测] version.json 返回的不是 JSON 格式');
      return;
    }
    
    const data = await response.json();
    const serverVersion = data.version;
    const localVersion = uni.getStorageSync('APP_VERSION');

    if (localVersion && localVersion !== serverVersion) {
      // 发现新版本，更新本地版本号
      uni.setStorageSync('APP_VERSION', serverVersion);
      
      // 强制重载页面清除缓存
      uni.showModal({
        title: '发现新版本',
        content: '系统已升级，请点击确定刷新页面加载最新内容。',
        showCancel: false,
        success: () => {
          window.location.reload(true); // true 表示硬刷新
        }
      });
    } else if (!localVersion) {
      // 首次访问，记录版本号
      uni.setStorageSync('APP_VERSION', serverVersion);
    }
  } catch (error) {
    console.error('❌ [版本检测] 检查版本更新失败:', error);
    // 静默失败，不影响应用正常使用
  }
}
// #endif
</script>
<style></style>
