/**
 * 网络请求封装工具
 * 基于 uni.request 封装 GET 和 POST 方法
 */

// 从环境变量读取 API 基础地址
// 开发环境使用空字符串（通过 vite 代理）
// 生产环境使用完整 URL
const baseURL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:9000')

// 请求配置接口
interface RequestConfig {
  url: string
  data?: any
  header?: any
  timeout?: number
}

// 响应数据接口
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
    uni.request({
      url: `${baseURL}${config.url}`,
      method: config.method,
      data: config.data,
      header: {
        'Content-Type': 'application/json',
        ...config.header,
      },
      timeout: config.timeout || 10000,
      success: (res: ResponseData<T>) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          console.error('请求失败:', res)
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        console.error('网络请求错误:', err)
        reject(err)
      },
    })
  })
}

/**
 * GET 请求
 */
export function get<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({
    url,
    method: 'GET',
    data,
    ...config,
  })
}

/**
 * POST 请求
 */
export function post<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({
    url,
    method: 'POST',
    data,
    ...config,
  })
}

/**
 * PUT 请求
 */
export function put<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({
    url,
    method: 'PUT',
    data,
    ...config,
  })
}

/**
 * DELETE 请求
 */
export function del<T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> {
  return request<T>({
    url,
    method: 'DELETE',
    data,
    ...config,
  })
}

// 导出基础 URL，方便其他地方使用
export { baseURL }
