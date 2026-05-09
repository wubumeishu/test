/**
 * 八字状态管理 Store
 * 负责管理八字排盘的状态和业务逻辑
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import request, { get, post, registerTimer, unregisterTimer } from '../utils/request'

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
  is_lunar?: boolean    // 是否农历，默认 false（公历）
  is_deep_analysis?: boolean
}

/**
 * 命主基本信息（排盘前设置，供结果页和历史页读取）
 */
export interface BaseInfo {
  name: string       // 命主姓名
  gender: number     // 0=女, 1=男
  archiveId?: string // 档案ID（档案排盘时有值）
}

// ==================== Store 定义 ====================

export const useBaziStore = defineStore('bazi', () => {
  // ==================== 状态 ====================
  
  /**
   * 加载状态
   */
  const isLoading = ref<boolean>(false)
  
  /**
   * 命主基本信息（排盘前/排盘后均可读取）
   */
  const baseInfo = ref<BaseInfo>({ name: '', gender: 1 })

  /**
   * 当前排盘数据 (最近一次排盘的完整结果)
   */
  const currentBaziData = ref<BaziCalculateResponse | null>(null)

  /**
   * AI 异步任务状态
   */
  const currentAiReport  = ref<string>('')          // 已生成的 AI 报告文本（轮询追加）
  const aiTaskId         = ref<string>('')           // 当前任务 ID
  const aiTaskStatus     = ref<'idle' | 'pending' | 'running' | 'done' | 'error'>('idle')
  const aiPollingTimer   = ref<ReturnType<typeof setInterval> | null>(null)
  
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
      // AI 深度分析需要更长的超时时间（60 秒）
      const response = await request<BaziCalculateResponse>({
        url: '/api/fortune/calculate',
        method: 'POST',
        data: requestData,
        timeout: isDeepAnalysis ? 60000 : 10000  // AI 分析 60 秒，普通排盘 10 秒
      })

      console.log('📥 [useBaziStore] 后端响应:', response)

      // 检查响应状态
      if (!response.success) {
        throw new Error(response.message || '排盘失败')
      }

      // 保存到当前数据
      currentBaziData.value = response

      // 同步命主基本信息（name 由后端从档案查出并写入响应）
      baseInfo.value = {
        name:      response.name,
        gender:    response.gender,
        archiveId: archiveId,
      }

      // 确保历史记录中 name 字段有值（兜底用 baseInfo）
      const recordToSave: BaziCalculateResponse = {
        ...response,
        name: response.name || baseInfo.value.name,
      }

      // 保存到历史记录
      addToHistory(recordToSave)

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
      // AI 深度分析需要更长的超时时间（60 秒）
      const response = await request<BaziCalculateResponse>({
        url: '/api/fortune/calculate-by-data',
        method: 'POST',
        data: data,
        timeout: data.is_deep_analysis ? 60000 : 10000  // AI 分析 60 秒，普通排盘 10 秒
      })

      console.log('📥 [useBaziStore] 后端响应:', response)

      // 检查响应状态
      if (!response.success) {
        throw new Error(response.message || '排盘失败')
      }

      // 保存到当前数据
      currentBaziData.value = response

      // 同步命主基本信息（name 优先取后端响应，兜底用入参 data.name）
      baseInfo.value = {
        name:   response.name || data.name,
        gender: response.gender ?? data.gender,
      }

      // 确保历史记录中 name 字段有值（兜底用 baseInfo）
      const recordToSave: BaziCalculateResponse = {
        ...response,
        name: response.name || baseInfo.value.name,
      }

      // 保存到历史记录
      addToHistory(recordToSave)

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
   * 从云端获取历史记录并更新本地列表
   */
  async function fetchHistoryFromCloud() {
    try {
      console.log('📥 [useBaziStore] 开始从云端获取历史记录...')
      const res = await request<{ total: number; records: any[] }>({
        url: '/api/fortune/records?limit=50&offset=0',
        method: 'GET'
      })
      
      const cloudRecords = res.records || []
      
      // 转换云端记录为本地所需的格式
      const convertedRecords = cloudRecords.map(raw => {
        const fej = raw.five_elements_json ?? {}
        const resolvedName = raw.name ?? fej.name ?? raw.bazi_json?.name ?? '未知'
        
        return {
          success: true,
          message: '历史记录恢复',
          record_id: raw.record_id ?? '',
          name: resolvedName,
          gender: raw.gender ?? fej.gender ?? 1,
          solar_date: fej.solar_date ?? raw.solar_date ?? '',
          lunar_date: fej.lunar_date ?? raw.lunar_date ?? '',
          shengxiao: fej.shengxiao ?? raw.shengxiao ?? '',
          bazi_string: fej.bazi_string ?? raw.bazi_string ?? raw.bazi_str ?? '',
          year_pillar: fej.year_pillar ?? raw.year_pillar ?? {},
          month_pillar: fej.month_pillar ?? raw.month_pillar ?? {},
          day_pillar: fej.day_pillar ?? raw.day_pillar ?? {},
          hour_pillar: fej.hour_pillar ?? raw.hour_pillar ?? {},
          day_master: fej.day_master ?? raw.day_master ?? '',
          day_master_wuxing: fej.day_master_wuxing ?? raw.day_master_wuxing ?? '',
          wuxing_strength: fej.wuxing_strength ?? raw.wuxing_strength ?? { jin: 0, mu: 0, shui: 0, huo: 0, tu: 0 },
          wuxing_summary: fej.wuxing_summary ?? raw.wuxing_summary ?? { 金: 0, 木: 0, 水: 0, 火: 0, 土: 0 },
          ai_report: raw.ai_report_markdown ?? raw.ai_report ?? null,
          created_at: raw.created_at ?? raw.timestamp
        }
      })
      
      historyList.value = convertedRecords
      saveToLocalStorage()
      console.log(`✅ [useBaziStore] 已从云端获取 ${convertedRecords.length} 条历史记录并同步到本地`)
    } catch (error) {
      console.error('❌ [useBaziStore] 从云端获取历史记录失败:', error)
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
   * 从历史记录恢复完整排盘数据到 Store
   * 兼容后端 RecordResponse 格式（five_elements_json 存四柱）和直接的 BaziCalculateResponse 格式
   * @param raw 后端原始记录对象（含 five_elements_json）或完整的 BaziCalculateResponse
   * @param resolvedName 已解析好的命主姓名（history.vue 传入）
   */
  function restoreHistoryData(raw: any, resolvedName?: string) {
    try {
      // 优先从 five_elements_json 取四柱数据（后端 /records 接口格式）
      const fej = raw.five_elements_json ?? {}

      // 构造符合 BaziCalculateResponse 的完整对象
      const restored: BaziCalculateResponse = {
        success:           true,
        message:           '历史记录恢复',
        record_id:         raw.record_id         ?? '',
        name:              resolvedName           ?? raw.name ?? fej.name ?? '',
        gender:            raw.gender             ?? fej.gender ?? 1,
        solar_date:        fej.solar_date         ?? raw.solar_date         ?? '',
        lunar_date:        fej.lunar_date         ?? raw.lunar_date         ?? '',
        shengxiao:         fej.shengxiao          ?? raw.shengxiao          ?? '',
        bazi_string:       fej.bazi_string        ?? raw.bazi_string        ?? raw.bazi_str ?? '',
        year_pillar:       fej.year_pillar        ?? raw.year_pillar        ?? {},
        month_pillar:      fej.month_pillar       ?? raw.month_pillar       ?? {},
        day_pillar:        fej.day_pillar         ?? raw.day_pillar         ?? {},
        hour_pillar:       fej.hour_pillar        ?? raw.hour_pillar        ?? {},
        day_master:        fej.day_master         ?? raw.day_master         ?? '',
        day_master_wuxing: fej.day_master_wuxing  ?? raw.day_master_wuxing  ?? '',
        wuxing_strength:   fej.wuxing_strength    ?? raw.wuxing_strength    ?? { jin: 0, mu: 0, shui: 0, huo: 0, tu: 0 },
        wuxing_summary:    fej.wuxing_summary     ?? raw.wuxing_summary     ?? { 金: 0, 木: 0, 水: 0, 火: 0, 土: 0 },
        ai_report:         raw.ai_report_markdown ?? raw.ai_report          ?? null,
      }

      // 写入当前排盘数据
      currentBaziData.value = restored

      // 同步 baseInfo
      baseInfo.value = {
        name:      restored.name   || '未知',
        gender:    restored.gender ?? 1,
        archiveId: raw.archive_id  ?? undefined,
      }

      console.log('✅ [useBaziStore] 历史数据恢复成功，命主:', restored.name)
    } catch (error) {
      console.error('❌ [useBaziStore] 历史数据恢复失败:', error)
    }
  }

  /**
   * 清空当前排盘数据
   */
  function clearCurrentBaziData() {
    currentBaziData.value = null
    console.log('✅ [useBaziStore] 已清空当前排盘数据')
  }

  // ==================== AI 异步任务 ====================

  /**
   * 停止当前 AI 轮询定时器
   */
  function stopAiPolling() {
    if (aiPollingTimer.value !== null) {
      unregisterTimer(aiPollingTimer.value)
      aiPollingTimer.value = null
      console.log('⏹️ [useBaziStore] AI 轮询已停止')
    }
  }

  /**
   * 重置 AI 任务状态（开始新任务前调用）
   */
  function resetAiTask() {
    stopAiPolling()
    currentAiReport.value = ''
    aiTaskId.value = ''
    aiTaskStatus.value = 'idle'
  }

  /**
   * 提交 AI 深度分析任务到后端队列
   * 后端立即返回 task_id，前端随后开始轮询进度
   *
   * @param baziData 完整的排盘数据（BaziCalculateResponse）
   */
  async function submitAiTask(baziData: BaziCalculateResponse): Promise<void> {
    resetAiTask()
    aiTaskStatus.value = 'pending'

    try {
      console.log('📤 [useBaziStore] 提交 AI 分析任务...')

      const res = await post<{ task_id: string; status: string }>('/api/ai/analyze', {
        name:              baziData.name || '命主',
        gender:            baziData.gender,
        solar_date:        baziData.solar_date,
        lunar_date:        baziData.lunar_date,
        shengxiao:         baziData.shengxiao,
        bazi_string:       baziData.bazi_string,
        day_master:        baziData.day_master,
        day_master_wuxing: baziData.day_master_wuxing,
        year_pillar:       baziData.year_pillar,
        month_pillar:      baziData.month_pillar,
        day_pillar:        baziData.day_pillar,
        hour_pillar:       baziData.hour_pillar,
      })

      aiTaskId.value = res.task_id
      console.log('✅ [useBaziStore] 任务已入队，task_id:', res.task_id)

      // 立即开始轮询
      startAiPolling()
    } catch (error: any) {
      aiTaskStatus.value = 'error'
      console.error('❌ [useBaziStore] 提交 AI 任务失败:', error)
      uni.showToast({ title: '星路繁忙，请稍后重试', icon: 'none', duration: 2000 })
    }
  }

  /**
   * 启动轮询，每 1.5 秒查询一次任务进度
   * 连续失败 3 次后自动停止并提示用户
   */
  function startAiPolling() {
    if (!aiTaskId.value) return

    let failCount = 0
    const MAX_FAIL = 3

    console.log('🔄 [useBaziStore] 开始轮询 AI 任务进度...')

    const timer = setInterval(async () => {
      try {
        const res = await get<{
          task_id: string
          status: string
          content: string
          error: string | null
        }>(`/api/ai/task/${aiTaskId.value}`)

        failCount = 0  // 成功则重置失败计数

        // 更新状态
        aiTaskStatus.value = res.status as any

        // 更新已生成内容（后端返回的是完整累积文本，直接替换）
        if (res.content) {
          currentAiReport.value = res.content
        }

        // 任务完成
        if (res.status === 'done') {
          console.log(`✅ [useBaziStore] AI 分析完成，字数: ${res.content?.length || 0}`)
          // 同步到 currentBaziData.ai_report，供历史记录使用
          if (currentBaziData.value) {
            currentBaziData.value.ai_report = res.content
          }
          stopAiPolling()
          return
        }

        // 任务失败
        if (res.status === 'error') {
          console.error('❌ [useBaziStore] AI 任务失败:', res.error)
          uni.showToast({ title: res.error || '星路繁忙，请稍后重试', icon: 'none', duration: 2500 })
          stopAiPolling()
          return
        }

      } catch (error) {
        failCount++
        console.warn(`⚠️ [useBaziStore] 轮询失败 (${failCount}/${MAX_FAIL})`)

        if (failCount >= MAX_FAIL) {
          aiTaskStatus.value = 'error'
          uni.showToast({ title: '星路繁忙，请稍后重试', icon: 'none', duration: 2500 })
          stopAiPolling()
        }
      }
    }, 1500)

    // 注册到全局定时器表（登出时自动清除）
    registerTimer(timer)
    aiPollingTimer.value = timer
  }

  // ==================== 返回 ====================

  return {
    // 状态
    isLoading,
    baseInfo,
    currentBaziData,
    historyList,
    // AI 异步任务状态
    currentAiReport,
    aiTaskId,
    aiTaskStatus,

    // Actions
    calculateByArchive,
    calculateByData,
    loadFromLocalStorage,
    fetchHistoryFromCloud,
    clearHistory,
    deleteHistoryItem,
    setCurrentBaziData,
    clearCurrentBaziData,
    restoreHistoryData,
    // AI 异步任务
    submitAiTask,
    resetAiTask,
    stopAiPolling,
  }
})

