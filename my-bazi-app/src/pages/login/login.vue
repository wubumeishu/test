<template>
  <view class="login-page">
    <!-- 背景 -->
    <view class="bg-layer"></view>

    <!-- 主内容区 -->
    <view class="content-wrapper">
      <!-- Logo 和 Slogan -->
      <view class="header-section">
        <text class="slogan brush-font">云水之间</text>
        <text class="slogan-sub">照见本心</text>
      </view>

      <!-- 毛玻璃表单卡片 -->
      <view class="form-card">
        <view class="form-inner">
          <!-- 模式切换标题 -->
          <view class="mode-title">
            <text class="mode-title-text">{{ isLoginMode ? '登录' : '注册' }}</text>
          </view>

          <!-- ==================== 登录模式 ==================== -->
          <view v-if="isLoginMode" class="form-content">
            <!-- 手机号输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">phone_iphone</text>
                <input
                  v-model="loginForm.phone"
                  type="number"
                  class="zen-input"
                  placeholder="请输入手机号"
                  maxlength="11"
                  :adjust-position="false"
                />
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 密码输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">lock</text>
                <input
                  v-model="loginForm.password"
                  :type="showLoginPassword ? 'text' : 'password'"
                  :password="!showLoginPassword"
                  class="zen-input"
                  placeholder="请输入密码"
                  :adjust-position="false"
                />
                <text
                  class="material-symbols-outlined eye-icon"
                  @click="showLoginPassword = !showLoginPassword"
                >
                  {{ showLoginPassword ? 'visibility' : 'visibility_off' }}
                </text>
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 登录按钮 -->
            <button
              class="submit-btn"
              :class="{ loading: isLoading }"
              :disabled="isLoading"
              @click="handleLogin"
            >
              <text v-if="!isLoading">登录</text>
              <text v-else>登录中...</text>
            </button>
          </view>

          <!-- ==================== 注册模式 ==================== -->
          <view v-else class="form-content">
            <!-- 手机号输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">phone_iphone</text>
                <input
                  v-model="registerForm.phone"
                  type="number"
                  class="zen-input"
                  placeholder="请输入手机号"
                  maxlength="11"
                  :adjust-position="false"
                />
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 验证码输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">verified_user</text>
                <input
                  v-model="registerForm.code"
                  type="number"
                  class="zen-input"
                  placeholder="请输入验证码"
                  maxlength="6"
                  :adjust-position="false"
                />
                <text
                  class="code-btn"
                  :class="{ disabled: countdown > 0 }"
                  @click="handleSendCode"
                >
                  {{ countdown > 0 ? `${countdown}秒` : '获取验证码' }}
                </text>
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 设置密码输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">lock</text>
                <input
                  v-model="registerForm.password"
                  :type="showRegPassword ? 'text' : 'password'"
                  :password="!showRegPassword"
                  class="zen-input"
                  placeholder="设置密码（不少于6位）"
                  :adjust-position="false"
                />
                <text
                  class="material-symbols-outlined eye-icon"
                  @click="showRegPassword = !showRegPassword"
                >
                  {{ showRegPassword ? 'visibility' : 'visibility_off' }}
                </text>
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 确认密码输入 -->
            <view class="input-group">
              <view class="input-wrapper">
                <text class="material-symbols-outlined input-icon">check_circle</text>
                <input
                  v-model="registerForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  :password="!showConfirmPassword"
                  class="zen-input"
                  placeholder="确认密码"
                  :adjust-position="false"
                />
                <text
                  class="material-symbols-outlined eye-icon"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  {{ showConfirmPassword ? 'visibility' : 'visibility_off' }}
                </text>
              </view>
              <view class="input-line"></view>
            </view>

            <!-- 注册按钮 -->
            <button
              class="submit-btn"
              :class="{ loading: isLoading }"
              :disabled="isLoading"
              @click="handleRegister"
            >
              <text v-if="!isLoading">注册</text>
              <text v-else>注册中...</text>
            </button>
          </view>

          <!-- 模式切换按钮 -->
          <view class="mode-switch">
            <text class="switch-text" @click="toggleMode">
              {{ isLoginMode ? '还没有账号？去注册' : '已有账号？去登录' }}
            </text>
          </view>

          <!-- 协议勾选（合规强制，不可默认勾选） -->
          <view class="agreement-row" @click="agreedToTerms = !agreedToTerms">
            <view class="checkbox" :class="{ checked: agreedToTerms }">
              <text v-if="agreedToTerms" class="material-symbols-outlined check-icon">check</text>
            </view>
            <view class="agreement-text-wrap">
              <text class="agreement-text">我已阅读并同意</text>
              <text class="agreement-link" @click.stop="goToAgreement">《用户服务协议》</text>
              <text class="agreement-text">与</text>
              <text class="agreement-link" @click.stop="goToPrivacy">《隐私政策》</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部装饰 -->
      <view class="footer-decoration">
        <text class="decoration-text">· 禅心若水 · 静观自在 ·</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/useUserStore'

const userStore = useUserStore()

// ==================== 状态 ====================

// 模式切换：true = 登录，false = 注册
const isLoginMode = ref(true)

// 登录表单
const loginForm = ref({
  phone: '',
  password: ''
})

// 注册表单
const registerForm = ref({
  phone: '',
  code: '',
  password: '',
  confirmPassword: ''
})

// 密码显示/隐藏
const showLoginPassword = ref(false)
const showRegPassword = ref(false)
const showConfirmPassword = ref(false)

// 验证码倒计时
const countdown = ref(0)

// 加载状态
const isLoading = ref(false)

// 协议勾选状态（合规要求：默认不勾选）
const agreedToTerms = ref(false)

// ── 登录页自身的跳转守卫 ──
// 这是最可靠的触发点：onShow 时页面栈已就绪，route 一定有值。
// App.vue 的 onShow 是双重保险，此处是主逻辑。
onShow(() => {
  const pages = getCurrentPages()
  const currentRoute = pages[pages.length - 1]?.route ?? ''
  console.log(
    `[Login.onShow] isLoggedIn=${userStore.isLoggedIn}`,
    `| 页面栈长度=${pages.length}`,
    `| 当前路由="${currentRoute}"`,
    `| 完整页面栈=`, pages.map(p => p.route)
  )
  if (userStore.isLoggedIn) {
    console.log('[Login.onShow] 已登录，即将跳转 → /pages/index/index')
    uni.switchTab({ url: '/pages/index/index' })
  }
})

// 跳转协议页
function goToAgreement() {
  uni.navigateTo({ url: '/pages/legal/user-agreement' })
}
function goToPrivacy() {
  uni.navigateTo({ url: '/pages/legal/privacy-policy' })
}

// 校验协议勾选
function checkAgreement(): boolean {
  if (!agreedToTerms.value) {
    uni.showModal({
      title: '请先同意协议',
      content: '请阅读并勾选《用户服务协议》与《隐私政策》后继续',
      showCancel: false,
      confirmText: '知道了'
    })
    return false
  }
  return true
}

// ==================== 方法 ====================

/**
 * 切换登录/注册模式
 */
function toggleMode() {
  isLoginMode.value = !isLoginMode.value
  
  // 清空表单
  loginForm.value = { phone: '', password: '' }
  registerForm.value = { phone: '', code: '', password: '', confirmPassword: '' }
  
  // 重置密码显示状态
  showLoginPassword.value = false
  showRegPassword.value = false
  showConfirmPassword.value = false
}

/**
 * 验证手机号格式
 */
function validatePhone(phone: string): boolean {
  if (!phone) {
    uni.showToast({
      title: '请输入手机号',
      icon: 'none',
      duration: 2000
    })
    return false
  }

  if (phone.length !== 11) {
    uni.showToast({
      title: '请输入正确的手机号',
      icon: 'none',
      duration: 2000
    })
    return false
  }

  const phoneReg = /^1[3-9]\d{9}$/
  if (!phoneReg.test(phone)) {
    uni.showToast({
      title: '手机号格式不正确',
      icon: 'none',
      duration: 2000
    })
    return false
  }

  return true
}

/**
 * 发送验证码
 */
async function handleSendCode() {
  // 倒计时中不可点击
  if (countdown.value > 0) {
    return
  }

  // 验证手机号
  if (!validatePhone(registerForm.value.phone)) {
    return
  }

  try {
    // 调用 Store 发送验证码
    await userStore.sendVerificationCode(registerForm.value.phone)

    // 开始倒计时（60秒）
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
  }
}

/**
 * 登录
 */
async function handleLogin() {
  // 校验协议勾选
  if (!checkAgreement()) return

  // 验证手机号
  if (!validatePhone(loginForm.value.phone)) {
    return
  }

  // 验证密码
  if (!loginForm.value.password) {
    uni.showToast({
      title: '请输入密码',
      icon: 'none',
      duration: 2000
    })
    return
  }

  if (loginForm.value.password.length < 6) {
    uni.showToast({
      title: '密码长度不少于6位',
      icon: 'none',
      duration: 2000
    })
    return
  }

  isLoading.value = true

  try {
    // 调用 Store 登录（内部已完成持久化）
    await userStore.loginWithPassword(loginForm.value.phone, loginForm.value.password)

    // 登录成功：跳转首页
    // pages/index/index 是 tabBar 页面，必须用 switchTab，reLaunch 在部分微信版本会静默失败
    const pages = getCurrentPages()
    console.log(`[Login] 登录成功，页面栈长度: ${pages.length}，即将跳转 → /pages/index/index`)
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500) // 等 "登录成功" Toast 展示完毕
  } catch (error) {
    // 错误 Toast 已在 store 内弹出，此处仅记录日志
    console.error('登录失败:', error)
  } finally {
    isLoading.value = false
  }
}

/**
 * 注册
 */
async function handleRegister() {
  // 校验协议勾选
  if (!checkAgreement()) return

  // 验证手机号
  if (!validatePhone(registerForm.value.phone)) {
    return
  }

  // 验证验证码
  if (!registerForm.value.code) {
    uni.showToast({
      title: '请输入验证码',
      icon: 'none',
      duration: 2000
    })
    return
  }

  if (registerForm.value.code.length !== 6) {
    uni.showToast({
      title: '请输入6位验证码',
      icon: 'none',
      duration: 2000
    })
    return
  }

  // 验证密码
  if (!registerForm.value.password) {
    uni.showToast({
      title: '请设置密码',
      icon: 'none',
      duration: 2000
    })
    return
  }

  if (registerForm.value.password.length < 6) {
    uni.showToast({
      title: '密码长度不少于6位',
      icon: 'none',
      duration: 2000
    })
    return
  }

  // 验证确认密码
  if (!registerForm.value.confirmPassword) {
    uni.showToast({
      title: '请确认密码',
      icon: 'none',
      duration: 2000
    })
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    uni.showToast({
      title: '两次输入的密码不一致',
      icon: 'none',
      duration: 2000
    })
    return
  }

  isLoading.value = true

  try {
    // 调用 Store 注册（内部已完成持久化）
    await userStore.register(
      registerForm.value.phone,
      registerForm.value.code,
      registerForm.value.password
    )

    // 注册成功：跳转首页（tabBar 页面必须用 switchTab）
    const pages = getCurrentPages()
    console.log(`[Login] 注册成功，页面栈长度: ${pages.length}，即将跳转 → /pages/index/index`)
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1500)
  } catch (error) {
    // 错误 Toast 已在 store 内弹出，此处仅记录日志
    console.error('注册失败:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
/* 字体由 App.vue 全局 @font-face 声明（本地路径），此处无需重复声明 */

.login-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #F9F6F1;
}

/* 背景层 */
.bg-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #F9F6F1 0%, #F5F2ED 50%, #F9F6F1 100%);
  background-image: url("/static/handmade-paper.png");
  background-size: cover;
  
  &::before {
    content: '';
    position: absolute;
    top: 20%;
    left: 50%;
    transform: translateX(-50%);
    width: 300rpx;
    height: 300rpx;
    background: radial-gradient(circle, rgba(178, 58, 52, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    filter: blur(60rpx);
  }
}

/* 内容包装器 */
.content-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 60rpx 60rpx;
}

/* 头部区域 */
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.slogan {
  font-size: 72rpx;
  color: #1A1A1A;
  letter-spacing: 8rpx;
  margin-bottom: 20rpx;
  text-shadow: 0 2rpx 8rpx rgba(178, 58, 52, 0.15);
}

.slogan-sub {
  font-size: 28rpx;
  color: #666666;
  letter-spacing: 6rpx;
}

/* 毛玻璃表单卡片 */
.form-card {
  width: 100%;
  max-width: 600rpx;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20rpx);
  -webkit-backdrop-filter: blur(20rpx);
  border-radius: 32rpx;
  border: 1rpx solid rgba(212, 175, 55, 0.2);
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.form-inner {
  padding: 50rpx 50rpx 60rpx;
}

/* 模式标题 */
.mode-title {
  text-align: center;
  margin-bottom: 40rpx;
}

.mode-title-text {
  font-size: 40rpx;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 4rpx;
}

/* 表单内容 */
.form-content {
  margin-bottom: 30rpx;
}

/* 输入框组 */
.input-group {
  margin-bottom: 40rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding-bottom: 20rpx;
}

.input-icon {
  font-size: 44rpx;
  color: rgba(178, 58, 52, 0.6);
  margin-right: 20rpx;
  flex-shrink: 0;
}

.zen-input {
  flex: 1;
  font-size: 32rpx;
  color: #1A1A1A;
  background: transparent;
  border: none;
  outline: none;
}

.zen-input::placeholder {
  color: rgba(0, 0, 0, 0.3);
}

.eye-icon {
  font-size: 40rpx;
  color: rgba(0, 0, 0, 0.4);
  margin-left: 10rpx;
  flex-shrink: 0;
  cursor: pointer;
}

.input-line {
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, rgba(212, 175, 55, 0.3) 50%, transparent 100%);
}

/* 验证码按钮 */
.code-btn {
  flex-shrink: 0;
  font-size: 24rpx;
  color: #B23A34;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  background: rgba(178, 58, 52, 0.08);
  transition: all 0.3s ease;
  white-space: nowrap;
  
  &.disabled {
    color: rgba(0, 0, 0, 0.3);
    background: rgba(0, 0, 0, 0.05);
  }
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #B23A34 0%, #8B2E29 100%);
  border-radius: 48rpx;
  border: none;
  font-size: 32rpx;
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 4rpx;
  box-shadow: 0 8rpx 24rpx rgba(178, 58, 52, 0.4);
  transition: all 0.3s ease;
  margin-top: 20rpx;
  
  &:active {
    transform: scale(0.98);
    box-shadow: 0 4rpx 12rpx rgba(178, 58, 52, 0.3);
  }
  
  &.loading {
    opacity: 0.7;
  }
}

/* 模式切换 */
.mode-switch {
  text-align: center;
  margin-top: 30rpx;
  margin-bottom: 20rpx;
}

.switch-text {
  font-size: 28rpx;
  color: #B23A34;
  cursor: pointer;
  transition: opacity 0.3s ease;
  
  &:active {
    opacity: 0.7;
  }
}

/* 提示文字 */
.tips-text {
  margin-top: 20rpx;
  text-align: center;
  font-size: 24rpx;
  color: rgba(0, 0, 0, 0.4);
  line-height: 1.6;
  
  .link {
    color: #B23A34;
  }
}

/* 协议勾选行 */
.agreement-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-top: 32rpx;
  padding: 0 4rpx;
}

.checkbox {
  width: 40rpx;
  height: 40rpx;
  border-radius: 8rpx;
  border: 2rpx solid rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4rpx;
  transition: all 0.2s ease;
}

.checkbox.checked {
  background: #B23A34;
  border-color: #B23A34;
}

.check-icon {
  font-size: 28rpx;
  color: #fff;
  line-height: 1;
}

.agreement-text-wrap {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  line-height: 1.6;
}

.agreement-text {
  font-size: 24rpx;
  color: rgba(0, 0, 0, 0.45);
}

.agreement-link {
  font-size: 24rpx;
  color: #B23A34;
}

/* 底部装饰 */
.footer-decoration {
  margin-top: 60rpx;
}

.decoration-text {
  font-size: 24rpx;
  color: rgba(0, 0, 0, 0.3);
  letter-spacing: 4rpx;
}

/* 毛笔字体 */
.brush-font {
  font-family: 'Ma Shan Zheng', cursive;
}

/* Material Symbols 图标 */
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
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  
  /* 强制使用字体图标，不显示文本 */
  &::before {
    content: attr(data-icon);
  }
}
</style>
