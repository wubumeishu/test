/**
 * 八字状态管理 Store
 * 负责管理八字排盘的状态和业务逻辑
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'

// ==================== 类型定义 ====================

/**
 * 四柱信息
 */
export interface Pillar {
  gan: string // 天干
  zhi: string // 地支
  nayin: string // 纳音
  canggan: string[] // 藏干
}

/**
 * 五行强度 (百分比)
 */
export interface WuxingStrength {
  jin: number // 金 (%)
  mu: number // 木 (%)
  shui: number // 水 (%)
  huo: number // 火 (%)
  tu: number // 土 (%)
}

/**
 * 五行统计 (个数)
 */
export interface WuxingSummary {
  金: number
  木: number
  水: number
  火: number
  土: number
}

/**
 * 后端排盘响应接口
 */
export interface BaziCalculateResponse {
  success: boolean
  message: string
  record_id: string
  name: string
  gender: number
  solar_date: string
  lunar_date: string
  shengxiao: string
  bazi_string: string
  year_pillar: Pillar
  month_pillar: Pillar
  day_pillar: Pillar
  hour_pillar: Pillar
  day_master: string
  day_master_wuxing: string
  wuxing_strength: WuxingStrength
  wuxing_summary: WuxingSummary
  ai_report: string | null
}

/**
 * 通过档案ID排盘的请求参数
 */
export interface CalculateByArchiveRequest {
  archive_id: string
  is_deep_analysis?: boolean
}

/**
 * 通过原始数据排盘的请求参数
 */
export interface CalculateByDataRequest {
  name: string
  gender: number // 0=女, 1=男
  birth_year: number
  birth_month: number
  birth_day: number
  birth_hour: number
  birth_minute: number
  is_deep_analysis?: boolean
}

// ==================== Store 定义 ====================

export const useBaziStore = defineStore('bazi', () => {
  // ==================== 状态 ====================
  
  /**
   * 加载状态
   */
  const isLoading = ref<boolean>(false)
  
  /**
   * 当前排盘数据 (最近一次排盘的完整结果)
   */
  const currentBaziData = ref<BaziCalculateResponse | null>(null)
  
  /**
   * 历史记录列表 (本地缓存)
   */
  const historyList = ref<BaziCalculateResponse[]>([])

  // ==================== Actions ====================

  /**
   * 通过档案ID计算八字
   * @param archiveId 档案ID (UUID格式)
   * @param isDeepAnalysis 是否进行深度分析 (默认 false)
   * @returns 排盘结果
   */
  async function calculateByArchive(
    archiveId: string,
    isDeepAnalysis: boolean = false
  ): Promise<BaziCalculateResponse> {
    // 设置加载状态
    isLoading.value = true

    try {
      console.log('🔄 [useBaziStore] 开始排盘 (通过档案ID)')
      console.log('📤 [useBaziStore] 发起排盘，档案ID:', archiveId)
      
      // 验证 archiveId 不为空
      if (!archiveId || archiveId.trim() === '') {
        throw new Error('档案ID不能为空')
      }

      // 构建请求数据
      const requestData = {
        archive_id: archiveId,
        is_deep_analysis: isDeepAnalysis
      }
      
      console.log('📤 [useBaziStore] 请求参数:', requestData)

      // 调用后端 API
      const response = await request<BaziCalculateResponse>({
        url: '/api/fortune/calculate',
        method: 'POST',
        data: requestData
      })

      console.log('📥 [useBaziStore] 后端响应:', response)

      // 检查响应状态
      if (!response.success) {
        throw new Error(response.message || '排盘失败')
      }

      // 保存到当前数据
      currentBaziData.value = response

      // 保存到历史记录
      addToHistory(response)

      // 保存到本地存储
      saveToLocalStorage()

      // 显示成功提示
      uni.showToast({
        title: '排盘成功',
        icon: 'success',
        duration: 1500
      })

      console.log('✅ [useBaziStore] 排盘成功')

      return response
    } catch (error: any) {
      console.error('❌ [useBaziStore] 排盘失败:', error)

      // 提取错误消息
      let errorMessage = '排盘失败，请检查网络连接'
      
      if (error.message) {
        errorMessage = error.message
      } else if (error.data && error.data.detail) {
        // FastAPI 返回的错误格式
        errorMessage = error.data.detail
      } else if (error.statusCode) {
        errorMessage = `请求失败 (${error.statusCode})`
      }

      console.error('❌ [useBaziStore] 错误详情:', errorMessage)

      // 显示错误提示
      uni.showToast({
        title: errorMessage,
        icon: 'none',
        duration: 2000
      })

      // 重新抛出错误,让调用方可以捕获
      throw error
    } finally {
      // 无论成功或失败,都要重置加载状态
      isLoading.value = false
    }
  }

  /**
   * 通过原始数据计算八字 (快速排盘,不保存档案)
   * @param data 生辰数据
   * @returns 排盘结果
   */
  async function calculateByData(
    data: CalculateByDataRequest
  ): Promise<BaziCalculateResponse> {
    // 设置加载状态
    isLoading.value = true

    try {
      console.log('🔄 [useBaziStore] 开始排盘 (通过原始数据)')
      console.log('📤 [useBaziStore] 请求参数:', data)

      // 调用后端 API
      const response = await request<BaziCalculateResponse>({
        url: '/api/fortune/calculate-by-data',
        method: 'POST',
        data: data
      })

      console.log('📥 [useBaziStore] 后端响应:', response)

      // 检查响应状态
      if (!response.success) {
        throw new Error(response.message || '排盘失败')
      }

      // 保存到当前数据
      currentBaziData.value = response

      // 保存到历史记录
      addToHistory(response)

      // 保存到本地存储
      saveToLocalStorage()

      // 显示成功提示
      uni.showToast({
        title: '排盘成功',
        icon: 'success',
        duration: 1500
      })

      console.log('✅ [useBaziStore] 排盘成功')

      return response
    } catch (error: any) {
      console.error('❌ [useBaziStore] 排盘失败:', error)

      // 提取错误消息
      let errorMessage = '排盘失败，请检查网络连接'
      
      if (error.message) {
        errorMessage = error.message
      } else if (error.data && error.data.detail) {
        // FastAPI 返回的错误格式
        errorMessage = error.data.detail
      } else if (error.statusCode) {
        errorMessage = `请求失败 (${error.statusCode})`
      }

      console.error('❌ [useBaziStore] 错误详情:', errorMessage)

      // 显示错误提示
      uni.showToast({
        title: errorMessage,
        icon: 'none',
        duration: 2000
      })

      // 重新抛出错误,让调用方可以捕获
      throw error
    } finally {
      // 无论成功或失败,都要重置加载状态
      isLoading.value = false
    }
  }

  /**
   * 添加到历史记录
   * @param data 排盘结果
   */
  function addToHistory(data: BaziCalculateResponse) {
    // 检查是否已存在 (根据 record_id)
    const existingIndex = historyList.value.findIndex(
      item => item.record_id === data.record_id
    )

    if (existingIndex !== -1) {
      // 如果已存在,移除旧的
      historyList.value.splice(existingIndex, 1)
    }

    // 添加到列表开头
    historyList.value.unshift(data)

    // 限制历史记录数量 (最多保存 50 条)
    if (historyList.value.length > 50) {
      historyList.value = historyList.value.slice(0, 50)
    }

    console.log(`✅ [useBaziStore] 已添加到历史记录 (共 ${historyList.value.length} 条)`)
  }

  /**
   * 保存到本地存储
   */
  function saveToLocalStorage() {
    try {
      uni.setStorageSync('bazi_history', historyList.value)
      console.log('✅ [useBaziStore] 已保存到本地存储')
    } catch (error) {
      console.error('❌ [useBaziStore] 保存到本地存储失败:', error)
    }
  }

  /**
   * 从本地存储加载历史记录
   */
  function loadFromLocalStorage() {
    try {
      const data = uni.getStorageSync('bazi_history')
      if (data && Array.isArray(data)) {
        historyList.value = data
        console.log(`✅ [useBaziStore] 已从本地存储加载 ${data.length} 条历史记录`)
      } else {
        console.log('ℹ️ [useBaziStore] 本地存储中没有历史记录')
      }
    } catch (error) {
      console.error('❌ [useBaziStore] 从本地存储加载失败:', error)
    }
  }

  /**
   * 清空历史记录
   */
  function clearHistory() {
    try {
      historyList.value = []
      uni.removeStorageSync('bazi_history')
      
      uni.showToast({
        title: '历史记录已清空',
        icon: 'success',
        duration: 1500
      })
      
      console.log('✅ [useBaziStore] 历史记录已清空')
    } catch (error) {
      console.error('❌ [useBaziStore] 清空历史记录失败:', error)
      
      uni.showToast({
        title: '清空失败',
        icon: 'none',
        duration: 1500
      })
    }
  }

  /**
   * 删除单条历史记录
   * @param recordId 记录ID
   */
  function deleteHistoryItem(recordId: string) {
    try {
      const index = historyList.value.findIndex(item => item.record_id === recordId)
      
      if (index !== -1) {
        historyList.value.splice(index, 1)
        saveToLocalStorage()
        
        uni.showToast({
          title: '已删除',
          icon: 'success',
          duration: 1000
        })
        
        console.log('✅ [useBaziStore] 已删除历史记录:', recordId)
      }
    } catch (error) {
      console.error('❌ [useBaziStore] 删除历史记录失败:', error)
      
      uni.showToast({
        title: '删除失败',
        icon: 'none',
        duration: 1500
      })
    }
  }

  /**
   * 设置当前排盘数据 (用于查看历史记录)
   * @param data 排盘结果
   */
  function setCurrentBaziData(data: BaziCalculateResponse) {
    currentBaziData.value = data
    console.log('✅ [useBaziStore] 已设置当前排盘数据')
  }

  /**
   * 清空当前排盘数据
   */
  function clearCurrentBaziData() {
    currentBaziData.value = null
    console.log('✅ [useBaziStore] 已清空当前排盘数据')
  }

  // ==================== 返回 ====================

  return {
    // 状态
    isLoading,
    currentBaziData,
    historyList,

    // Actions
    calculateByArchive,
    calculateByData,
    loadFromLocalStorage,
    clearHistory,
    deleteHistoryItem,
    setCurrentBaziData,
    clearCurrentBaziData,
  }
})

