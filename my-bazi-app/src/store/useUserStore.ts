/**
 * 用户状态管理 Store
 * 负责管理用户登录状态和用户信息
 *
 * 存储 Key 约定（全局唯一，request.ts 与此保持一致）：
 *   token     → uni.getStorageSync('token')
 *   user_info → uni.getStorageSync('user_info')
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post } from '../utils/request'

// ==================== 类型定义 ====================

export interface UserInfo {
  id: string
  phone: string
  nickname?: string
  avatar_url?: string
}

interface SendCodeResponse {
  msg: string
}

interface AuthResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

// ==================== Store 定义 ====================

export const useUserStore = defineStore('user', () => {

  // ── 状态：默认值直接从本地存储读取，避免 onLaunch 之前的竞态 ──
  const token    = ref<string>(uni.getStorageSync('token') || '')
  const userInfo = ref<UserInfo | null>(uni.getStorageSync('user_info') || null)

  /** 是否已登录（token 与 userInfo 同时有效） */
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  // ==================== 私有工具 ====================

  /**
   * 持久化认证信息到内存 + Storage（登录/注册成功后统一调用）
   */
  function _persistAuth(accessToken: string, user: UserInfo): void {
    token.value    = accessToken
    userInfo.value = user
    uni.setStorageSync('token',     accessToken)
    uni.setStorageSync('user_info', user)
    console.log('✅ [useUserStore] 认证信息已持久化，用户:', user.phone)
  }

  // ==================== Actions ====================

  /**
   * 密码登录
   */
  async function loginWithPassword(phone: string, password: string): Promise<void> {
    console.log('📤 [useUserStore] 密码登录:', phone)
    try {
      const res = await post<AuthResponse>('/api/auth/login', { phone, password })
      _persistAuth(res.access_token, res.user)
      uni.showToast({ title: '登录成功', icon: 'success', duration: 1500 })
    } catch (error: any) {
      console.error('❌ [useUserStore] 登录失败:', error)
      const msg = error.data?.detail || error.message || '登录失败，请重试'
      uni.showToast({ title: msg, icon: 'none', duration: 2000 })
      throw error
    }
  }

  /**
   * 验证码登录（保留兼容）
   */
  async function loginWithCode(phone: string, code: string): Promise<void> {
    console.log('📤 [useUserStore] 验证码登录:', phone)
    try {
      const res = await post<AuthResponse>('/api/auth/login/code', { phone, code })
      _persistAuth(res.access_token, res.user)
      uni.showToast({ title: '登录成功', icon: 'success', duration: 1500 })
    } catch (error: any) {
      console.error('❌ [useUserStore] 登录失败:', error)
      const msg = error.data?.detail || error.message || '登录失败，请重试'
      uni.showToast({ title: msg, icon: 'none', duration: 2000 })
      throw error
    }
  }

  /**
   * 注册新用户
   */
  async function register(phone: string, code: string, password: string): Promise<void> {
    console.log('📤 [useUserStore] 注册新用户:', phone)
    try {
      const res = await post<AuthResponse>('/api/auth/register', { phone, code, password })
      _persistAuth(res.access_token, res.user)
      uni.showToast({ title: '注册成功', icon: 'success', duration: 1500 })
    } catch (error: any) {
      console.error('❌ [useUserStore] 注册失败:', error)
      const msg = error.data?.detail || error.message || '注册失败，请重试'
      uni.showToast({ title: msg, icon: 'none', duration: 2000 })
      throw error
    }
  }

  /**
   * 发送验证码
   */
  async function sendVerificationCode(phone: string): Promise<void> {
    console.log('📤 [useUserStore] 发送验证码:', phone)
    try {
      const res = await post<SendCodeResponse>('/api/auth/send-code', { phone })
      console.log('✅ [useUserStore] 验证码发送成功:', res.msg)
      uni.showToast({ title: '验证码已发送', icon: 'success', duration: 2000 })
    } catch (error: any) {
      console.error('❌ [useUserStore] 发送验证码失败:', error)
      const msg = error.data?.detail || error.message || '发送失败，请重试'
      uni.showToast({ title: msg, icon: 'none', duration: 2000 })
      throw error
    }
  }

  /**
   * 退出登录
   * - 重置 Pinia 内存状态（token / userInfo）
   * - 清除本地存储中的认证 Key
   * - 可选：跳转登录页（由调用方决定，避免在 request.ts 拦截器中产生副作用）
   */
  function logout(redirectToLogin = false): void {
    // 1. 清空内存状态
    token.value    = ''
    userInfo.value = null

    // 2. 精确删除认证相关 Key（不影响其他业务缓存，如 bazi_history）
    uni.removeStorageSync('token')
    uni.removeStorageSync('user_info')

    console.log('✅ [useUserStore] 已退出登录，token 已清空')

    // 3. 跳转（使用 reLaunch 清空页面栈，防止返回键回到受保护页面）
    if (redirectToLogin) {
      uni.reLaunch({ url: '/pages/login/login' })
    }
  }

  /**
   * 从本地存储恢复登录状态（App.vue onLaunch 调用）
   *
   * 由于 state 初始化时已经读取了 Storage，此方法主要用于
   * 热重载或 Pinia 状态被意外重置后的兜底恢复。
   */
  function restoreLoginState(): void {
    try {
      const savedToken    = uni.getStorageSync('token')
      const savedUserInfo = uni.getStorageSync('user_info')
      if (savedToken && savedUserInfo) {
        token.value    = savedToken
        userInfo.value = savedUserInfo
        console.log('✅ [useUserStore] 登录状态已恢复:', userInfo.value?.phone)
      } else {
        console.log('ℹ️ [useUserStore] 本地无登录状态')
      }
    } catch (e) {
      console.error('❌ [useUserStore] 恢复登录状态失败:', e)
    }
  }

  /**
   * 更新用户信息（个人资料修改后调用）
   */
  function updateUserInfo(info: Partial<UserInfo>): void {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...info }
      uni.setStorageSync('user_info', userInfo.value)
      console.log('✅ [useUserStore] 用户信息已更新')
    }
  }

  // ==================== 返回 ====================

  return {
    token,
    userInfo,
    isLoggedIn,
    loginWithPassword,
    loginWithCode,
    register,
    sendVerificationCode,
    logout,
    restoreLoginState,
    updateUserInfo,
  }
})
