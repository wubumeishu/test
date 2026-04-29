import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { get, post, del } from '@/utils/request'

/**
 * 档案接口定义
 */
export interface Archive {
  id: string                    // 唯一标识
  name: string                  // 姓名
  gender: 0 | 1                 // 性别：0-女(坤造)，1-男(乾造)
  birthDate: string             // 公历出生日期 YYYY-MM-DD
  birthTime: string             // 出生时间 HH:mm
  relation: string              // 关系标签（如'本人'、'伴侣'、'子女'）
  isDefault: boolean            // 是否为默认档案
  createdAt: number             // 创建时间戳
}

/**
 * 云端档案接口定义 (与后端对应)
 */
interface CloudArchive {
  archive_id: string
  name: string
  gender: number
  calendar_type: string
  birth_year: number
  birth_month: number
  birth_day: number
  birth_hour: number
  birth_minute: number
  tags: string | null
  is_default: boolean
  local_created_at: number
  cloud_uploaded_at?: number
  created_at?: string
  updated_at?: string
}

/**
 * 云端同步请求接口
 */
interface SyncRequest {
  archives: CloudArchive[]
}

/**
 * 云端同步响应接口
 */
interface SyncResponse {
  success: boolean
  message: string
  synced_count: number
  archives: CloudArchive[]
}

/**
 * 档案管理 Store
 * 负责管理用户的测算对象档案，支持增删改查和本地持久化
 */
export const useArchiveStore = defineStore('archive', () => {
  // ==================== State ====================
  const archives = ref<Archive[]>([])
  const currentArchiveId = ref<string>('')
  const isLoading = ref<boolean>(false)  // 加载状态
  const isSyncing = ref<boolean>(false)  // 同步状态
  const isLoggedIn = ref<boolean>(true)  // 模拟登录状态 (TODO: 后续接入真实登录)

  // ==================== Getters ====================
  /**
   * 获取当前选中的档案对象
   */
  const currentArchive = computed(() => {
    return archives.value.find(item => item.id === currentArchiveId.value) || null
  })

  /**
   * 获取默认档案
   */
  const defaultArchive = computed(() => {
    return archives.value.find(item => item.isDefault) || null
  })

  // ==================== 持久化逻辑 ====================
  /**
   * 从本地存储加载数据
   */
  const loadFromStorage = async () => {
    try {
      const storedArchives = uni.getStorageSync('bazi_archives')
      const storedCurrentId = uni.getStorageSync('bazi_current_id')

      if (storedArchives && Array.isArray(storedArchives)) {
        archives.value = storedArchives
      }

      if (storedCurrentId) {
        currentArchiveId.value = storedCurrentId
      } else if (archives.value.length > 0) {
        // 如果没有存储当前 ID，但有档案，则选中第一个
        currentArchiveId.value = archives.value[0].id
      }

      console.log('📂 档案数据加载成功:', archives.value.length, '条')

      // 如果用户已登录，自动触发云端同步
      if (isLoggedIn.value) {
        console.log('🔄 检测到用户已登录，开始云端同步...')
        await syncWithCloud()
      }
    } catch (error) {
      console.error('❌ 档案数据加载失败:', error)
    }
  }

  /**
   * 保存档案列表到本地存储
   */
  const saveArchivesToStorage = () => {
    try {
      uni.setStorageSync('bazi_archives', archives.value)
      console.log('💾 档案列表已保存')
    } catch (error) {
      console.error('❌ 档案列表保存失败:', error)
    }
  }

  /**
   * 保存当前选中 ID 到本地存储
   */
  const saveCurrentIdToStorage = () => {
    try {
      uni.setStorageSync('bazi_current_id', currentArchiveId.value)
      console.log('💾 当前档案 ID 已保存:', currentArchiveId.value)
    } catch (error) {
      console.error('❌ 当前档案 ID 保存失败:', error)
    }
  }

  // 深度监听 archives，自动持久化
  watch(
    archives,
    () => {
      saveArchivesToStorage()
    },
    { deep: true }
  )

  // 监听 currentArchiveId，自动持久化
  watch(currentArchiveId, () => {
    saveCurrentIdToStorage()
  })

  // ==================== 云端同步逻辑 ====================
  /**
   * 从云端获取档案列表
   * GET /api/archives/list
   */
  const fetchArchives = async () => {
    // 如果未登录，跳过
    if (!isLoggedIn.value) {
      console.log('⚠️ 用户未登录，跳过获取档案列表')
      return
    }

    isLoading.value = true

    try {
      console.log('📥 开始获取云端档案列表...')

      const cloudArchives = await get<CloudArchive[]>('/api/archives/list')

      console.log('✅ 获取云端档案列表成功:', cloudArchives.length, '条')

      // 将云端档案转换为本地格式
      archives.value = cloudArchives.map(convertToLocalArchive)

      // 如果当前选中的档案不存在了，重新选择
      if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
        if (archives.value.length > 0) {
          currentArchiveId.value = archives.value[0].id
        } else {
          currentArchiveId.value = ''
        }
      }

      uni.showToast({
        title: '档案列表已更新',
        icon: 'success',
        duration: 2000
      })

    } catch (error) {
      console.error('❌ 获取档案列表失败:', error)
      
      uni.showToast({
        title: '获取档案列表失败',
        icon: 'error',
        duration: 2000
      })
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 将本地档案转换为云端格式
   */
  const convertToCloudArchive = (archive: Archive): CloudArchive => {
    // 解析日期和时间
    const [year, month, day] = archive.birthDate.split('-').map(Number)
    const [hour, minute] = archive.birthTime.split(':').map(Number)

    return {
      archive_id: archive.id,
      name: archive.name,
      gender: archive.gender,
      calendar_type: 'solar',  // 默认公历
      birth_year: year,
      birth_month: month,
      birth_day: day,
      birth_hour: hour,
      birth_minute: minute,
      tags: archive.relation || null,
      is_default: archive.isDefault,
      local_created_at: archive.createdAt
    }
  }

  /**
   * 将云端档案转换为本地格式
   */
  const convertToLocalArchive = (cloudArchive: CloudArchive): Archive => {
    // 格式化日期和时间
    const birthDate = `${cloudArchive.birth_year}-${String(cloudArchive.birth_month).padStart(2, '0')}-${String(cloudArchive.birth_day).padStart(2, '0')}`
    const birthTime = `${String(cloudArchive.birth_hour).padStart(2, '0')}:${String(cloudArchive.birth_minute).padStart(2, '0')}`

    return {
      id: cloudArchive.archive_id,
      name: cloudArchive.name,
      gender: cloudArchive.gender as 0 | 1,
      birthDate,
      birthTime,
      relation: cloudArchive.tags || '',
      isDefault: cloudArchive.is_default,
      createdAt: cloudArchive.local_created_at
    }
  }

  /**
   * 云端同步
   * 将本地档案同步到云端，并获取最新的云端档案列表
   * POST /api/archives/sync
   */
  const syncWithCloud = async () => {
    // 如果正在同步，跳过
    if (isSyncing.value) {
      console.log('⏳ 正在同步中，跳过本次请求')
      return
    }

    // 如果未登录，跳过
    if (!isLoggedIn.value) {
      console.log('⚠️ 用户未登录，跳过云端同步')
      return
    }

    isSyncing.value = true
    isLoading.value = true

    try {
      console.log('🔄 开始云端同步...')
      console.log('📤 本地档案数量:', archives.value.length)

      // 将本地档案转换为云端格式
      const cloudArchives = archives.value.map(convertToCloudArchive)

      // 调用后端同步接口
      const response = await post<SyncResponse>('/api/archives/sync', {
        archives: cloudArchives
      })

      console.log('✅ 云端同步成功:', response.message)
      console.log('📥 云端档案数量:', response.archives.length)
      console.log('🔄 实际同步数量:', response.synced_count)

      // 将云端档案转换为本地格式
      const newArchives = response.archives.map(convertToLocalArchive)

      // 覆盖更新本地档案列表
      archives.value = newArchives

      // 如果当前选中的档案不存在了，重新选择
      if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
        if (archives.value.length > 0) {
          currentArchiveId.value = archives.value[0].id
        } else {
          currentArchiveId.value = ''
        }
      }

      // watch 会自动触发持久化，无需手动调用

      uni.showToast({
        title: '云端同步成功',
        icon: 'success',
        duration: 2000
      })

    } catch (error) {
      console.error('❌ 云端同步失败:', error)
      
      // 网络请求失败不影响本地数据的正常使用
      uni.showToast({
        title: '同步失败，使用本地数据',
        icon: 'none',
        duration: 2000
      })
    } finally {
      isSyncing.value = false
      isLoading.value = false
    }
  }

  // ==================== Actions (CRUD) ====================
  /**
   * 添加新档案
   * 先在本地添加，然后调用云端同步
   * @param data 档案数据（不含 id 和 createdAt）
   */
  const addArchive = async (data: Omit<Archive, 'id' | 'createdAt'>) => {
    isLoading.value = true

    try {
      // 生成标准 UUID 格式的 ID
      const generateUUID = () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          const r = Math.random() * 16 | 0
          const v = c === 'x' ? r : (r & 0x3 | 0x8)
          return v.toString(16)
        })
      }
      
      const newArchive: Archive = {
        ...data,
        id: generateUUID(), // 使用 UUID 格式
        createdAt: Date.now()
      }

      // 如果是第一条数据，自动设为默认
      if (archives.value.length === 0) {
        newArchive.isDefault = true
      } else if (newArchive.isDefault) {
        // 如果新档案设为默认，取消其他档案的默认状态
        archives.value.forEach(item => {
          item.isDefault = false
        })
      }

      // 添加到数组头部
      archives.value.unshift(newArchive)

      // 如果是第一条数据，自动选中
      if (archives.value.length === 1) {
        currentArchiveId.value = newArchive.id
      }

      console.log('✅ 本地档案添加成功:', newArchive.name)

      // 如果用户已登录，同步到云端
      if (isLoggedIn.value) {
        await syncWithCloud()
      }

      uni.showToast({
        title: '档案添加成功',
        icon: 'success',
        duration: 1500
      })

      return newArchive

    } catch (error) {
      console.error('❌ 添加档案失败:', error)
      
      uni.showToast({
        title: '添加档案失败',
        icon: 'error',
        duration: 2000
      })

      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新档案信息
   * 先在本地更新，然后调用云端同步
   * @param id 档案 ID
   * @param data 要更新的数据
   */
  const updateArchive = async (id: string, data: Partial<Omit<Archive, 'id' | 'createdAt'>>) => {
    isLoading.value = true

    try {
      const index = archives.value.findIndex(item => item.id === id)
      
      if (index === -1) {
        console.error('❌ 档案不存在:', id)
        uni.showToast({
          title: '档案不存在',
          icon: 'error'
        })
        return false
      }

      // 如果要设置为默认，取消其他档案的默认状态
      if (data.isDefault) {
        archives.value.forEach(item => {
          if (item.id !== id) {
            item.isDefault = false
          }
        })
      }

      // 更新档案
      archives.value[index] = {
        ...archives.value[index],
        ...data
      }

      console.log('✅ 本地档案更新成功:', archives.value[index].name)

      // 如果用户已登录，同步到云端
      if (isLoggedIn.value) {
        await syncWithCloud()
      }

      uni.showToast({
        title: '档案更新成功',
        icon: 'success',
        duration: 1500
      })

      return true

    } catch (error) {
      console.error('❌ 更新档案失败:', error)
      
      uni.showToast({
        title: '更新档案失败',
        icon: 'error',
        duration: 2000
      })

      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除档案
   * 先调用云端删除接口，成功后刷新列表
   * DELETE /api/archives/{archive_id}
   * @param id 档案 ID
   */
  const deleteArchive = async (id: string) => {
    isLoading.value = true

    try {
      const index = archives.value.findIndex(item => item.id === id)
      
      if (index === -1) {
        console.error('❌ 档案不存在:', id)
        uni.showToast({
          title: '档案不存在',
          icon: 'error'
        })
        return false
      }

      // 如果用户已登录，先调用云端删除接口
      if (isLoggedIn.value) {
        console.log('🗑️ 开始删除云端档案:', id)
        
        await del(`/api/archives/${id}`)
        
        console.log('✅ 云端档案删除成功')
      }

      // 删除本地档案
      archives.value.splice(index, 1)

      // 如果删除的是当前选中的档案
      if (currentArchiveId.value === id) {
        if (archives.value.length > 0) {
          // 自动选中第一个档案
          currentArchiveId.value = archives.value[0].id
        } else {
          // 没有档案了，清空选中
          currentArchiveId.value = ''
        }
      }

      // 如果用户已登录，刷新档案列表
      if (isLoggedIn.value) {
        await fetchArchives()
      }

      uni.showToast({
        title: '档案删除成功',
        icon: 'success',
        duration: 1500
      })

      return true

    } catch (error) {
      console.error('❌ 删除档案失败:', error)
      
      uni.showToast({
        title: '删除档案失败',
        icon: 'error',
        duration: 2000
      })

      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 切换当前测算对象
   * @param id 档案 ID
   */
  const switchCurrentArchive = (id: string) => {
    const archive = archives.value.find(item => item.id === id)
    
    if (!archive) {
      console.error('❌ 档案不存在:', id)
      uni.showToast({
        title: '档案不存在',
        icon: 'error'
      })
      return false
    }

    currentArchiveId.value = id

    uni.showToast({
      title: `已切换至：${archive.name}`,
      icon: 'success',
      duration: 1500
    })

    return true
  }

  /**
   * 设置默认档案
   * @param id 档案 ID
   */
  const setDefaultArchive = (id: string) => {
    const archive = archives.value.find(item => item.id === id)
    
    if (!archive) {
      console.error('❌ 档案不存在:', id)
      return false
    }

    // 取消所有档案的默认状态
    archives.value.forEach(item => {
      item.isDefault = false
    })

    // 设置新的默认档案
    archive.isDefault = true

    uni.showToast({
      title: '默认档案已设置',
      icon: 'success',
      duration: 1500
    })

    return true
  }

  /**
   * 清空所有档案（慎用）
   */
  const clearAllArchives = () => {
    archives.value = []
    currentArchiveId.value = ''
    
    uni.showToast({
      title: '所有档案已清空',
      icon: 'success',
      duration: 1500
    })
  }

  // ==================== 初始化 ====================
  // Store 创建时自动加载数据
  loadFromStorage()

  return {
    // State
    archives,
    currentArchiveId,
    isLoading,
    isSyncing,
    isLoggedIn,
    
    // Getters
    currentArchive,
    defaultArchive,
    
    // Actions
    fetchArchives,      // 新增：获取档案列表
    addArchive,
    updateArchive,
    deleteArchive,
    switchCurrentArchive,
    setDefaultArchive,
    clearAllArchives,
    loadFromStorage,
    syncWithCloud       // 云端同步方法
  }
})
