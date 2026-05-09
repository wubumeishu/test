/**
 * 网络请求封装工具 (v3.0)
 *
 * 核心升级：
 *   1. AbortController 请求注册表 —— 防止登出后"幽灵数据"写入 Store
 *   2. 6步核爆清理 —— 捕获 401 后严格按序执行，彻底消灭串号
 *   3. 微信登录接口支持 —— POST /api/auth/login/wechat
 *
 * 6步清理顺序（不可调换）：
 *   1. 捕获 401
 *   2. AbortController 取消所有进行中请求 + 清除定时器
 *   3. 路由跳转回 Login（先切走页面，防止组件因 null 数据白屏）
 *   4. Pinia $reset() 清空内存 Store
 *   5. uni.clearStorageSync() 清空本地缓存
 *   6. Toast 提示用户
 */

const baseURL = import.meta.env.VITE_API_BASE_URL || 'https://api.aiyuechuan.cn'

// ── 防止 401 触发多次跳转的节流标志 ──
let _redirectingToLogin = false

// ── 全局请求注册表（用于 AbortController 批量取消）──
// key: 请求唯一标识（method + url + timestamp）
// value: 对应的 abort 函数（uni.request 返回的 task.abort）
const _requestRegistry = new Map<string, () => void>()

// ── 全局定时器注册表（用于批量清除轮询）──
// 业务层通过 registerTimer / unregisterTimer 管理
const _timerRegistry = new Set<ReturnType<typeof setInterval>>()

/**
 * 注册一个定时器到全局注册表
 * 业务层（如 SSE 轮询）调用此方法，确保登出时能被统一清除
 */
export function registerTimer(timerId: ReturnType<typeof setInterval>): void {
  _timerRegistry.add(timerId)
}

/**
 * 从全局注册表移除一个定时器（定时器正常结束时调用）
 */
export function unregisterTimer(timerId: ReturnType<typeof setInterval>): void {
  clearInterval(timerId)
  _timerRegistry.delete(timerId)
}

// ── 类型定义 ──────────────────────────────────────────────────

interface RequestConfig {
  url: string
  data?: any
  header?: any
  timeout?: number
}

interface ResponseData<T = any> {
  data: T
  statusCode: number
  header: any
  cookies: string[]
}

// ── 核心请求方法 ──────────────────────────────────────────────

/**
 * 通用请求方法
 *
 * 每个请求会被注册到 _requestRegistry，登出时统一 abort。
 */
export default function request<T = any>(config: {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
  timeout?: number
}): Promise<T> {
  return new Promise((resolve, reject) => {
    const fullUrl = config.url.startsWith('http')
      ? config.url
      : `${baseURL}${config.url}`

    // ── 请求拦截：注入 Token ──
    const token = uni.getStorageSync('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.header,
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    console.log(`📡 [Request] ${config.method} ${fullUrl}`)

    // ── 注册请求到注册表（用于 AbortController）──
    const requestKey = `${config.method}_${fullUrl}_${Date.now()}`

    const task = uni.request({
      url: fullUrl,
      method: config.method,
      data: config.data,
      header: headers,
      timeout: config.timeout || 10000,

      success: (res) => {
        // 请求完成，从注册表移除
        _requestRegistry.delete(requestKey)

        const result = res as unknown as ResponseData<T>

        // 2xx 成功
        if (result.statusCode >= 200 && result.statusCode < 300) {
          console.log(`✅ [Request] ${config.method} ${fullUrl} - ${result.statusCode}`)
          resolve(result.data)
          return
        }

        // 401 Token 过期 / 未登录
        if (result.statusCode === 401) {
          console.warn(`⚠️ [Request] 401 Unauthorized - ${fullUrl}`)
          _handle401()
          reject({ statusCode: 401, message: '登录已过期', data: result.data })
          return
        }

        // 其他错误
        console.error(`❌ [Request] ${config.method} ${fullUrl} - ${result.statusCode}`)
        reject({
          statusCode: result.statusCode,
          message: `请求失败: ${result.statusCode}`,
          data: result.data,
        })
      },

      fail: (err) => {
        _requestRegistry.delete(requestKey)
        // 被 abort() 取消的请求会走 fail，errMsg 包含 'abort'，静默处理
        if (err.errMsg?.includes('abort')) {
          console.log(`🚫 [Request] 请求已取消: ${fullUrl}`)
          return
        }
        console.error(`❌ [Request] ${config.method} ${fullUrl} - 网络错误:`, err)
        reject({ statusCode: 0, message: '网络请求失败', error: err })
      },
    })

    // 将 abort 函数注册到注册表
    if (task && typeof task.abort === 'function') {
      _requestRegistry.set(requestKey, () => task.abort())
    }
  })
}

// ── 6步核爆清理 ───────────────────────────────────────────────

/**
 * 处理 401：严格按 6 步顺序执行，彻底消灭串号与幽灵数据
 *
 * ⚠️ 步骤顺序不可调换，原因见各步骤注释
 */
function _handle401(): void {
  if (_redirectingToLogin) return
  _redirectingToLogin = true

  // ── 步骤 2：取消所有进行中的请求 + 清除所有定时器 ──
  // 必须在路由跳转前执行，否则 SSE/轮询回调会在跳转后继续向 Store 写数据
  _abortAllRequests()
  _clearAllTimers()

  // ── 步骤 3：路由跳转（必须先切走页面，再清数据）──
  // 若先清数据再跳转，当前页面监听 Store 的组件会因 null 数据报错白屏
  uni.reLaunch({ url: '/pages/login/login' })

  // ── 步骤 4 & 5 & 6：跳转后异步执行清理（等页面切走后再清数据）──
  // 使用 setTimeout 确保路由跳转已完成，新页面已挂载
  setTimeout(() => {
    // 步骤 4：Pinia 深度重置（动态导入避免循环依赖）
    import('../store/useUserStore').then(({ useUserStore }) => {
      try { useUserStore().$reset?.() } catch (e) { /* store 未初始化时忽略 */ }
    })
    import('../store/useArchiveStore').then(({ useArchiveStore }) => {
      try { useArchiveStore().$reset?.() } catch (e) { /* store 未初始化时忽略 */ }
    })
    import('../store/useBaziStore').then(({ useBaziStore }) => {
      try { useBaziStore().$reset?.() } catch (e) { /* store 未初始化时忽略 */ }
    })

    // 步骤 5：清空本地存储（在 Store reset 之后执行）
    uni.clearStorageSync()

    // 步骤 6：提示用户
    uni.showToast({
      title: '登录状态已过期，请重新进入',
      icon: 'none',
      duration: 2500,
    })

    // 重置节流标志，允许下次正常触发
    setTimeout(() => { _redirectingToLogin = false }, 3000)
  }, 100)
}

/**
 * 取消所有注册表中的进行中请求
 */
function _abortAllRequests(): void {
  if (_requestRegistry.size === 0) return
  console.log(`🚫 [Request] 取消 ${_requestRegistry.size} 个进行中的请求`)
  _requestRegistry.forEach((abort) => {
    try { abort() } catch (e) { /* 忽略已完成的请求 */ }
  })
  _requestRegistry.clear()
}

/**
 * 清除所有注册的定时器
 */
function _clearAllTimers(): void {
  if (_timerRegistry.size === 0) return
  console.log(`⏹️ [Request] 清除 ${_timerRegistry.size} 个定时器`)
  _timerRegistry.forEach((id) => {
    try { clearInterval(id) } catch (e) { /* 忽略 */ }
  })
  _timerRegistry.clear()
}

// ── 快捷方法 ──────────────────────────────────────────────────

export function get<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({ url, method: 'GET', data, ...config })
}

export function post<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({ url, method: 'POST', data, ...config })
}

export function put<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({ url, method: 'PUT', data, ...config })
}

export function del<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({ url, method: 'DELETE', data, ...config })
}

export { baseURL }
