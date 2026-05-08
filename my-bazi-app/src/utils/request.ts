/**
 * 网络请求封装工具
 * 基于 uni.request 封装 GET / POST / PUT / DELETE 方法
 *
 * 请求拦截：自动从 Storage 读取 token，注入 Authorization 头
 * 响应拦截：
 *   - 2xx → resolve
 *   - 401 → 通过 useUserStore.logout() 清理状态，跳转登录页，reject
 *   - 其他错误 → reject
 *
 * 存储 Key：'token' / 'user_info'（与 useUserStore 保持一致）
 */

const baseURL = import.meta.env.VITE_API_BASE_URL || 'https://api.aiyuechuan.cn'

// ── 防止 401 触发多次跳转的节流标志 ──
let _redirectingToLogin = false

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

/**
 * 通用请求方法
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
    // 每次请求时实时读取 Storage，确保 token 刷新后立即生效
    const token = uni.getStorageSync('token')

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.header,
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    console.log(`📡 [Request] ${config.method} ${fullUrl}`)

    uni.request({
      url: fullUrl,
      method: config.method,
      data: config.data,
      header: headers,
      timeout: config.timeout || 10000,

      success: (res) => {
        const result = res as unknown as ResponseData<T>

        // ── 响应拦截 ──

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
        console.error(`❌ [Request] ${config.method} ${fullUrl} - 网络错误:`, err)
        reject({ statusCode: 0, message: '网络请求失败', error: err })
      },
    })
  })
}

/**
 * 处理 401：清理认证状态并跳转登录页
 *
 * 通过 useUserStore().logout() 统一清理，确保内存状态与 Storage 同步。
 * 使用节流标志防止并发请求同时触发多次跳转。
 */
function _handle401(): void {
  if (_redirectingToLogin) return
  _redirectingToLogin = true

  // 动态导入避免循环依赖（store → request → store）
  // 小程序环境下 import() 是同步缓存，不会有性能问题
  import('../store/useUserStore').then(({ useUserStore }) => {
    try {
      useUserStore().logout()   // 清空内存状态 + Storage，不传 redirectToLogin
    } catch (e) {
      // store 未初始化时的兜底：直接清 Storage
      uni.removeStorageSync('token')
      uni.removeStorageSync('user_info')
    }

    uni.showToast({ title: '登录已过期，请重新登录', icon: 'none', duration: 2000 })

    setTimeout(() => {
      _redirectingToLogin = false   // 重置标志，允许下次正常触发
      uni.reLaunch({ url: '/pages/login/login' })
    }, 2000)
  })
}

// ==================== 快捷方法 ====================

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
