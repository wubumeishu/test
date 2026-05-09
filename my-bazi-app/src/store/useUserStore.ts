/**
 * 用户状态管理 Store (v3.0)
 *
 * 新增：
 *   - loginWithWechat()：微信静默登录（code → OpenID → JWT）
 *   - updateProfile()：更新昵称/头像/绑定手机号
 *   - is_vip 字段
 *
 * 存储 Key 约定（全局唯一，request.ts 与此保持一致）：
 *   token     → uni.getStorageSync('token')
 *   user_info → uni.getStorageSync('user_info')
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post, put } from '../utils/request'
import { useArchiveStore } from './useArchiveStore'
import { useBaziStore } from './useBaziStore'

// ==================== 类型定义 ====================

export interface UserInfo {
  id: string
  phone?: string | null
  nickname?: string
  avatar_url?: string
  is_vip?: boolean
  wechat_openid?: string | null
}

interface SendCodeResponse {
  msg: string
}

interface AuthResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

interface UpdateProfilePayload {
  nickname?: string
  avatar_url?: string
  phone?: string
  sms_code?: string
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

    // 登录后强制拉取云端数据对齐
    try {
      const archiveStore = useArchiveStore()
      const baziStore = useBaziStore()
      
      archiveStore.fetchArchives()
      baziStore.fetchHistoryFromCloud()
    } catch (e) {
      console.error('拉取云端数据失败:', e)
    }
  }

  // ==================== Actions ====================

  /**
   * 微信静默登录（v3.0 新增）
   *
   * 流程：
   *   1. 调用 uni.login({ provider: 'weixin' }) 获取临时 code
   *   2. 将 code 发给后端 POST /api/auth/login/wechat
   *   3. 后端用 code 换取 OpenID，静默注册或登录，返回 JWT
   *   4. 持久化 Token 和用户信息
   *
   * 整个过程对用户无感（不弹任何 Toast）。
   * 仅在出错时静默打印日志，不影响 App 启动流程。
   */
  async function loginWithWechat(): Promise<void> {
    // 仅在微信小程序环境执行
    // #ifdef MP-WEIXIN
    try {
      console.log('🔄 [useUserStore] 开始微信静默登录...')

      // 步骤 1：获取微信临时 code
      const loginResult = await new Promise<UniApp.LoginRes>((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: resolve,
          fail: reject,
        })
      })

      if (!loginResult.code) {
        console.warn('⚠️ [useUserStore] 微信登录未返回 code，跳过静默登录')
        return
      }

      console.log('✅ [useUserStore] 获取微信 code 成功')

      // 步骤 2：将 code 发给后端换取 JWT
      const res = await post<AuthResponse>('/api/auth/login/wechat', {
        code: loginResult.code,
      })

      // 步骤 3：持久化（静默，不弹 Toast）
      _persistAuth(res.access_token, res.user)
      console.log('✅ [useUserStore] 微信静默登录成功，用户:', res.user.nickname)
    } catch (error: any) {
      // 静默失败：不弹 Toast，不阻断 App 启动
      // 用户可以在登录页手动登录
      console.warn('⚠️ [useUserStore] 微信静默登录失败（静默处理）:', error?.message ?? error)
    }
    // #endif
  }

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

    // 2. 清理所有本地存储
    uni.clearStorageSync()

    // 3. 清理相关 Store 的状态
    try {
      const archiveStore = useArchiveStore()
      archiveStore.clearAllArchives()
      
      const baziStore = useBaziStore()
      baziStore.clearHistory()
      baziStore.clearCurrentBaziData()
    } catch (e) {
      console.error('清理其他 Store 状态失败:', e)
    }

    console.log('✅ [useUserStore] 已退出登录，数据已彻底打扫干净')

    // 4. 跳转（使用 reLaunch 清空页面栈，防止返回键回到受保护页面）
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

  /**
   * 提交资料更新到后端（v3.0 新增）
   *
   * 支持：昵称、头像、绑定手机号（需同时传 sms_code）
   * 对应后端：PUT /api/auth/profile
   *
   * @param payload 要更新的字段（只传需要修改的）
   */
  async function updateProfile(payload: UpdateProfilePayload): Promise<void> {
    try {
      const res = await put<AuthResponse>('/api/auth/profile', payload)
      // 后端返回最新的用户信息，同步更新本地
      _persistAuth(res.access_token, res.user)
      uni.showToast({ title: '资料已更新', icon: 'success', duration: 1500 })
      console.log('✅ [useUserStore] 资料更新成功')
    } catch (error: any) {
      const msg = error.data?.detail || error.message || '更新失败，请重试'
      uni.showToast({ title: msg, icon: 'none', duration: 2000 })
      throw error
    }
  }

  // ==================== 返回 ====================

  return {
    token,
    userInfo,
    isLoggedIn,
    loginWithWechat,
    loginWithPassword,
    loginWithCode,
    register,
    sendVerificationCode,
    logout,
    restoreLoginState,
    updateUserInfo,
    updateProfile,
  }
})
