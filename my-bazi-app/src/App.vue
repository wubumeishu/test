<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useBaziStore } from "./store/useBaziStore";
import { useUserStore } from "./store/useUserStore";

// ⚠️ 不在顶层调用 store，必须在生命周期内调用，否则小程序端 Pinia 未就绪会报错

// ── 防止 onShow 中 hideTabBar 被重复调用的节流标志 ──
let _tabBarHidden = false;

/**
 * 隐藏原生 TabBar（只在首次或必要时执行，避免 onShow 循环调用）
 */
const hideNativeTabBar = () => {
  try {
    uni.hideTabBar({ animation: false, fail: () => {} });
  } catch (e) {}
};

/**
 * 启动时多次尝试隐藏 TabBar（仅在 onLaunch 调用一次）
 */
const hideTabBarOnLaunch = () => {
  hideNativeTabBar();
  setTimeout(hideNativeTabBar, 50);
  setTimeout(hideNativeTabBar, 200);
  _tabBarHidden = true;
};

onLaunch(() => {
  console.log("App Launch");

  // 在生命周期内获取 store（此时 Pinia 已挂载）
  const baziStore = useBaziStore();
  const userStore = useUserStore();

  // 1. 同步操作：立即执行，不阻塞 UI
  hideTabBarOnLaunch();
  userStore.restoreLoginState();    // 纯本地 Storage 读取，同步且极快
  baziStore.loadFromLocalStorage(); // 纯本地 Storage 读取，同步且极快

  // 2. 字体加载 + 后端探测（推入下一帧，不阻塞首屏渲染）
  //
  //    ⚠️ 微信小程序每个页面是独立 WebView，App.vue <style> 里的 @font-face
  //    不会注入到页面渲染层，图标字体必须用 uni.loadFontFace 才能全局生效。
  //    书法字体同理。local:// 前缀让微信从小程序包内读取，无需网络。
  setTimeout(() => {
    loadAppFonts();
    pingBackend();

    // 3. 微信静默登录（仅在未登录时触发，已登录则跳过）
    //    必须在 pingBackend 之后执行，确保后端已就绪
    //    整个过程对用户无感，失败静默处理不影响 App 启动
    // #ifdef MP-WEIXIN
    if (!userStore.isLoggedIn) {
      console.log('[App] 未检测到登录状态，尝试微信静默登录...');
      userStore.loginWithWechat().catch(() => {
        // 静默失败，用户将在登录页手动登录
      });
    } else {
      console.log('[App] 已登录，跳过微信静默登录');
    }
    // #endif
  }, 0);

  // 注意：启动导航不在此处处理。
  // 原因：onLaunch 触发时页面栈为空（getCurrentPages() === []），
  //       首个页面是异步加载的，此时跳转会与页面初始化竞争，导致不可靠。
  // 正确做法：在登录页的 onShow 里判断 isLoggedIn，由页面自己决定是否跳走。
  // App.vue 的 onShow 作为双重保险（见下方）。
});

onShow(() => {
  console.log("App Show");

  const userStore = useUserStore();
  const pages     = getCurrentPages();
  const currentRoute = pages[pages.length - 1]?.route ?? '';

  console.log(
    `[App.onShow] isLoggedIn=${userStore.isLoggedIn}`,
    `| token="${userStore.token ? userStore.token.substring(0, 12) + '…' : '(空)'}"`,
    `| 页面栈长度=${pages.length}`,
    `| 当前路由="${currentRoute}"`,
    `| 完整页面栈=`, pages.map(p => p.route)
  );

  // ── 路径判断辅助（兼容带/不带前导斜杠两种格式）──
  const matchRoute = (route: string, target: string) =>
    route === target || route === `/${target}`;

  const isOnLoginPage = matchRoute(currentRoute, 'pages/login/login');

  // ── 守卫一：已登录 + 停留在登录页 → 跳首页 ──
  if (userStore.isLoggedIn && isOnLoginPage) {
    console.log('[App.onShow] 已登录但在登录页，跳转 → /pages/index/index');
    uni.switchTab({ url: '/pages/index/index' });
    return;
  }

  // ── 守卫二：未登录 + 在受保护页面 → 踢回登录页 ──
  // 白名单：不需要登录即可访问的页面
  const PUBLIC_ROUTES = [
    'pages/login/login',
    'pages/legal/user-agreement',
    'pages/legal/privacy-policy',
  ];
  const isPublicPage = PUBLIC_ROUTES.some(r => matchRoute(currentRoute, r));

  if (!userStore.isLoggedIn && !isPublicPage && pages.length > 0) {
    console.log(`[App.onShow] 未登录，当前页 "${currentRoute}" 需要登录，reLaunch → /pages/login/login`);
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  // ── TabBar 隐藏（仅首次，避免循环触发）──
  if (!_tabBarHidden) {
    hideNativeTabBar();
    _tabBarHidden = true;
  }

  // H5 平台版本检测（每次页面显示时检测）
  // #ifdef H5
  checkUpdate();
  // #endif
});

onHide(() => {
  console.log("App Hide");
});

/**
 * 字体加载
/**
 * 字体加载
 *
 * 微信小程序每个页面是独立 WebView，App.vue <style> 的 @font-face 只作用于
 * app-service 层，不会注入页面渲染层（wxss）。
 * uni.loadFontFace({ global: true }) 是唯一能让字体在所有页面生效的方式。
 *
 * source 使用云端 HTTPS 路径，确保微信渲染层可以正常加载。
 */
function loadAppFonts() {
  const BASE = 'https://api.aiyuechuan.cn/static/fonts';

  // ── Material Symbols 图标字体（313KB，含 49 个图标 + rlig 连字特性）──
  uni.loadFontFace({
    global: true,
    family: 'Material Symbols Outlined',
    source: `url('${BASE}/material-symbols-subset.woff2')`,
    success: () => console.log('✅ [Font] Material Symbols 加载成功'),
    fail:    (err: any) => console.warn('⚠️ [Font] Material Symbols 加载失败:', err?.errMsg ?? err),
  });

  // ── 马善政书法字体（4.6KB，含 18 个汉字子集）──
  uni.loadFontFace({
    global: true,
    family: 'Ma Shan Zheng',
    source: `url('${BASE}/MaShanZheng-subset.woff2')`,
    success: () => console.log('✅ [Font] Ma Shan Zheng 加载成功'),
    fail:    (err: any) => console.warn('⚠️ [Font] Ma Shan Zheng 加载失败:', err?.errMsg ?? err),
  });
}

/**
 * 后端连通性探测（非阻塞，静默失败）
 *
 * 设计原则：
 * - 超时缩短为 5s（health 接口应极快响应，超时说明服务异常）
 * - 失败只打日志，不弹 Toast，不触发跳转，不影响任何 UI
 * - 不使用全局 request 封装（避免触发 401 拦截器的 reLaunch 逻辑）
 */
function pingBackend() {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'https://api.aiyuechuan.cn';
  uni.request({
    url: `${baseURL}/api/health`,
    method: 'GET',
    timeout: 5000,
    success: (res) => {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        console.log('✅ [App] 后端连通正常');
      } else {
        console.warn(`⚠️ [App] 后端 health 返回异常状态: ${res.statusCode}`);
      }
    },
    fail: (err) => {
      // 静默失败：网络不通或服务冷启动中，不影响用户使用
      console.warn('⚠️ [App] 后端连通检测失败（不影响使用）:', err.errMsg);
    },
  });
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

<style>
/**
 * 全局样式
 * 字体文件打包在 /static/fonts/ 目录内，通过 @font-face 本地路径引用。
 * font-display: swap 确保字体加载期间先用系统字体渲染，不阻塞显示。
 */

/* ==================== 字体定义 ==================== */

/* Material Symbols 图标字体（子集化，313KB，含 49 个图标 + 完整 a-z）*/
/* 此字体使用 rlig（Required Ligature）渲染图标，非 liga */
@font-face {
  font-family: 'Material Symbols Outlined';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('https://api.aiyuechuan.cn/static/fonts/material-symbols-subset.woff2') format('woff2');
}

/* 马善政书法字体（子集化，4.6KB，含 App 用到的 18 个汉字）*/
@font-face {
  font-family: 'Ma Shan Zheng';
  font-style: normal;
  font-weight: normal;
  font-display: swap;
  src: url('https://api.aiyuechuan.cn/static/fonts/MaShanZheng-subset.woff2') format('woff2');
}

/* ==================== 全局样式重置 ==================== */
page, view, scroll-view, swiper, swiper-item, text, image, input, button {
  box-sizing: border-box;
}

page {
  background-color: #F9F6F1;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
    Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei',
    sans-serif;
}

/* 消除图片 inline-block 幽灵空白 */
image {
  display: block;
  max-width: 100%;
}

/* ==================== 图标字体样式 ==================== */
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined' !important;
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  /* rlig = Required Ligature，Material Symbols 用此特性渲染图标 */
  -webkit-font-feature-settings: 'rlig' 1, 'liga' 1, 'calt' 1;
  font-feature-settings: 'rlig' 1, 'liga' 1, 'calt' 1;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* ==================== 全局字体类 ==================== */
.serif-font {
  font-family: 'STSong', 'SimSun', 'Songti SC', 'Noto Serif SC', serif !important;
}
</style>
