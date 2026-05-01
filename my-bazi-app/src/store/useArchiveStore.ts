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
  birthDate: string             // 出生日期 YYYY-MM-DD
  birthTime: string             // 出生时间 HH:mm
  isLunar: boolean              // 是否农历：true=农历，false=公历
  tags: string[]                // 标签数组（如 ['本人', '伴侣']）
  isDefault: boolean            // 是否为默认档案
  createdAt: number             // 创建时间戳（毫秒，不可变）
  updatedAt: number             // 最后修改时间戳（毫秒，每次编辑更新）
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

  /**
   * 智能展示档案（用于『我的』页面）
   * 优先返回 isDefault=true 的档案；
   * 若无默认，则返回 createdAt 最大（最新填写）的档案
   */
  const displayArchive = computed(() => {
    if (archives.value.length === 0) return null
    const def = archives.value.find(item => item.isDefault)
    if (def) return def
    return [...archives.value].sort((a, b) => b.createdAt - a.createdAt)[0]
  })

  /**
   * 排序后的档案列表（用于档案库列表页）
   * 规则：默认档案置顶，其余按 updatedAt 降序（最新修改的在前）
   */
  const sortedArchives = computed(() => {
    return [...archives.value].sort((a, b) => {
      // 默认档案永远排第一
      if (a.isDefault !== b.isDefault) return a.isDefault ? -1 : 1
      // 其余按 updatedAt 降序，兼容旧数据用 createdAt 兜底
      return (b.updatedAt ?? b.createdAt) - (a.updatedAt ?? a.createdAt)
    })
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
        // 兼容旧数据：补充 updatedAt 字段，就地更新避免触发空状态闪烁
        const migrated = storedArchives.map((a: any) => ({
          ...a,
          updatedAt: a.updatedAt ?? a.createdAt ?? Date.now()
        }))
        archives.value.splice(0, archives.value.length, ...migrated)
      }

      // 清洗脏数据（本地存储可能存在多个默认档案）
      // watch 会自动将清洗结果持久化到本地存储
      // 本地初始化阶段不触发云端写回，等 fetchArchives 统一处理
      sanitizeDefaults()

      if (storedCurrentId) {
        currentArchiveId.value = storedCurrentId
      } else if (archives.value.length > 0) {
        // 如果没有存储当前 ID，但有档案，则选中第一个
        currentArchiveId.value = archives.value[0].id
      }

      console.log('📂 档案数据加载成功:', archives.value.length, '条')

      // 不在初始化时自动同步，避免与页面 onShow 的 fetchArchives 并发竞争
      // 数据刷新由各页面的 onShow 钩子统一触发
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

  // ==================== 数据清洗 ====================
  /**
   * 清洗脏数据：确保最多只有一个默认档案
   * 若发现多个 isDefault=true，保留 updatedAt 最大的那个，其余置为 false
   * watch 会自动将清洗结果持久化到本地存储。
   * @returns 被清洗（isDefault 被置为 false）的档案 ID 列表；空数组表示无脏数据
   */
  const sanitizeDefaults = (): string[] => {
    const defaultOnes = archives.value.filter(a => a.isDefault)
    if (defaultOnes.length <= 1) return []   // 无脏数据，直接返回

    console.warn(`⚠️ [sanitize] 发现 ${defaultOnes.length} 个默认档案，开始清洗...`)

    // 保留 updatedAt 最大的那个（最后修改的）
    const keeper = defaultOnes.reduce((prev, curr) =>
      (curr.updatedAt ?? curr.createdAt) > (prev.updatedAt ?? prev.createdAt) ? curr : prev
    )

    // 变更标记 & 收集被清洗的档案 ID
    let hasModified = false
    const dirtyIds: string[] = []
    const now = Date.now()

    archives.value.forEach(a => {
      if (a.isDefault && a.id !== keeper.id) {
        a.isDefault = false
        // 必须推进 updatedAt，否则后端时间戳门槛（local_created_at > existing）
        // 不会触发 UPDATE，is_default: false 将被忽略
        a.updatedAt = now
        hasModified = true
        dirtyIds.push(a.id)
        console.log(`🧹 [sanitize] 清除档案「${a.name}」的默认标记，updatedAt 推进至 ${now}`)
      }
    })

    if (hasModified) {
      console.log(`✅ [sanitize] 清洗完成，保留「${keeper.name}」为默认档案，共清洗 ${dirtyIds.length} 条`)
    }

    return dirtyIds   // 返回被清洗的 ID 列表，供调用方决定是否写回云端
  }

  /**
   * 静默将清洗结果写回云端
   * 仅在 sanitizeDefaults 返回非空列表时调用，不弹任何提示。
   * 直接构造 payload 发送，不走 syncWithCloud 的防重入锁，
   * 避免 isSyncing/isLoading 仍为 true 时被跳过。
   */
  const _persistSanitizedToCloud = async () => {
    if (!isLoggedIn.value) return
    try {
      // 直接用当前内存状态（已清洗）组装 payload，绕过 isSyncing 防重入锁
      const cloudArchives = archives.value.map(convertToCloudArchive)
      await post<SyncResponse>('/api/archives/sync', { archives: cloudArchives })
      console.log('☁️ [sanitize] 清洗结果已静默同步到云端（is_default 已写回）')
    } catch (e) {
      // 静默失败，不影响用户体验
      console.warn('⚠️ [sanitize] 清洗结果云端同步失败（静默）:', e)
    }
  }

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

      // 就地合并而非整体替换，避免列表闪烁
      const newArchives = cloudArchives.map(convertToLocalArchive)
      archives.value.splice(0, archives.value.length, ...newArchives)

      // 清洗脏数据；若有修改则静默写回云端，彻底消除重复触发
      const dirtyIds = sanitizeDefaults()
      if (dirtyIds.length > 0) {
        // 不 await，静默后台写回，不阻塞列表渲染
        _persistSanitizedToCloud()
      }

      // 如果当前选中的档案不存在了，重新选择
      if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
        if (archives.value.length > 0) {
          currentArchiveId.value = archives.value[0].id
        } else {
          currentArchiveId.value = ''
        }
      }
      // 静默刷新，不弹 toast

    } catch (error) {
      console.error('❌ 获取档案列表失败:', error)
      // 静默失败，不打扰用户
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
      calendar_type: archive.isLunar ? 'lunar' : 'solar',
      birth_year: year,
      birth_month: month,
      birth_day: day,
      birth_hour: hour,
      birth_minute: minute,
      tags: Array.isArray(archive.tags) && archive.tags.length > 0
        ? archive.tags.join(',')
        : null,
      is_default: archive.isDefault,
      // 用 updatedAt 作为同步时间戳，确保编辑后时间戳比云端更新，触发后端 UPDATE
      local_created_at: archive.updatedAt ?? archive.createdAt
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
      tags: cloudArchive.tags
        ? cloudArchive.tags.split(',').map(t => t.trim()).filter(Boolean)
        : [],
      isLunar: cloudArchive.calendar_type === 'lunar',
      isDefault: cloudArchive.is_default,
      createdAt: cloudArchive.local_created_at,
      updatedAt: cloudArchive.local_created_at   // 从云端回填时两者相同
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

      // 就地合并而非整体替换，避免列表闪烁
      archives.value.splice(0, archives.value.length, ...newArchives)

      // 清洗脏数据（云端可能返回多个默认档案）
      // watch 会自动将清洗结果持久化到本地存储
      // 注意：此处在 syncWithCloud 内部，不再递归调用 _persistSanitizedToCloud，
      // 避免无限循环；清洗结果会在下一次 fetchArchives 时自然写回
      sanitizeDefaults()

      // 如果当前选中的档案不存在了，重新选择
      if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
        if (archives.value.length > 0) {
          currentArchiveId.value = archives.value[0].id
        } else {
          currentArchiveId.value = ''
        }
      }
      // watch 会自动触发持久化，无需手动调用
      // 云端同步静默完成，不弹 toast

    } catch (error) {
      console.error('❌ 云端同步失败:', error)
      // 网络请求失败不影响本地数据的正常使用，静默处理
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
        id: generateUUID(),
        createdAt: Date.now(),
        updatedAt: Date.now()
      }

      // 排他性处理：
      // - 若新档案勾选了默认，静默清除其他所有档案的默认标记
      // - 若未勾选（包括第一条档案），尊重用户意图，允许无默认态
      if (newArchive.isDefault) {
        archives.value.forEach(item => { item.isDefault = false })
      }

      // 添加到数组头部
      archives.value.unshift(newArchive)

      // 如果是第一条数据，自动选中
      if (archives.value.length === 1) {
        currentArchiveId.value = newArchive.id
      }

      console.log('✅ 本地档案添加成功:', newArchive.name)

      // 如果用户已登录，同步到云端（静默）
      if (isLoggedIn.value) {
        await syncWithCloud()
      }

      // 不在 Store 层弹 toast，由调用方统一处理
      return newArchive

    } catch (error) {
      console.error('❌ 添加档案失败:', error)
      throw error  // 抛出让调用方处理
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

      // 排他性处理：
      // - 若本次将该档案设为默认（isDefault: true），静默清除其他所有档案的默认标记
      // - 若设为 false，直接允许，不影响其他档案（允许无默认态）
      if (data.isDefault === true) {
        archives.value.forEach(item => {
          if (item.id !== id) item.isDefault = false
        })
      }

      // 更新档案，同时刷新 updatedAt 确保时间戳比云端更新，触发后端 UPDATE
      archives.value[index] = {
        ...archives.value[index],
        ...data,
        updatedAt: Date.now()
      }

      console.log('✅ 本地档案更新成功:', archives.value[index].name, '| updatedAt:', archives.value[index].updatedAt)

      // 如果用户已登录，同步到云端（静默）
      if (isLoggedIn.value) {
        await syncWithCloud()
      }

      // 不在 Store 层弹 toast，由调用方统一处理
      return true

    } catch (error) {
      console.error('❌ 更新档案失败:', error)
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
    // 静默切换，不弹 toast
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
    // 静默设置，不弹 toast
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
    displayArchive,
    sortedArchives,
    
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
