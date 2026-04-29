# 档案 Store 云端同步集成

## 修改时间
2026-04-27

## 修改文件
`my-bazi-app/src/store/useArchiveStore.ts`

## 修改内容

### 1. 新增接口定义

#### CloudArchive (云端档案格式)
```typescript
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
```

#### SyncRequest (同步请求)
```typescript
interface SyncRequest {
  archives: CloudArchive[]
}
```

#### SyncResponse (同步响应)
```typescript
interface SyncResponse {
  success: boolean
  message: string
  synced_count: number
  archives: CloudArchive[]
}
```

### 2. 新增 State

```typescript
const isSyncing = ref<boolean>(false)  // 同步状态
const isLoggedIn = ref<boolean>(true)  // 模拟登录状态
```

**说明**:
- `isSyncing`: 防止重复同步
- `isLoggedIn`: 当前模拟为 `true`，后续接入真实登录系统

### 3. 新增转换函数

#### convertToCloudArchive
将本地档案格式转换为云端格式:

```typescript
const convertToCloudArchive = (archive: Archive): CloudArchive => {
  const [year, month, day] = archive.birthDate.split('-').map(Number)
  const [hour, minute] = archive.birthTime.split(':').map(Number)

  return {
    archive_id: archive.id,
    name: archive.name,
    gender: archive.gender,
    calendar_type: 'solar',
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
```

**转换规则**:
- `id` → `archive_id`
- `birthDate` (YYYY-MM-DD) → `birth_year`, `birth_month`, `birth_day`
- `birthTime` (HH:mm) → `birth_hour`, `birth_minute`
- `relation` → `tags`
- `isDefault` → `is_default`
- `createdAt` → `local_created_at`

#### convertToLocalArchive
将云端档案格式转换为本地格式:

```typescript
const convertToLocalArchive = (cloudArchive: CloudArchive): Archive => {
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
```

**转换规则**:
- `archive_id` → `id`
- `birth_year`, `birth_month`, `birth_day` → `birthDate` (YYYY-MM-DD)
- `birth_hour`, `birth_minute` → `birthTime` (HH:mm)
- `tags` → `relation`
- `is_default` → `isDefault`
- `local_created_at` → `createdAt`

### 4. 核心方法: syncWithCloud

```typescript
const syncWithCloud = async () => {
  // 防止重复同步
  if (isSyncing.value) {
    return
  }

  // 检查登录状态
  if (!isLoggedIn.value) {
    return
  }

  isSyncing.value = true

  try {
    // 1. 转换本地档案为云端格式
    const cloudArchives = archives.value.map(convertToCloudArchive)

    // 2. 调用后端同步接口
    const response = await post<SyncResponse>('/api/archives/sync', {
      archives: cloudArchives
    })

    // 3. 转换云端档案为本地格式
    const newArchives = response.archives.map(convertToLocalArchive)

    // 4. 覆盖更新本地档案列表
    archives.value = newArchives

    // 5. 检查当前选中的档案是否还存在
    if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
      if (archives.value.length > 0) {
        currentArchiveId.value = archives.value[0].id
      } else {
        currentArchiveId.value = ''
      }
    }

    // 6. watch 自动触发持久化

    uni.showToast({
      title: '云端同步成功',
      icon: 'success',
      duration: 2000
    })

  } catch (error) {
    console.error('❌ 云端同步失败:', error)
    
    // 网络请求失败不影响本地数据
    uni.showToast({
      title: '同步失败，使用本地数据',
      icon: 'none',
      duration: 2000
    })
  } finally {
    isSyncing.value = false
  }
}
```

**功能说明**:
1. 防止重复同步 (通过 `isSyncing` 标志)
2. 检查登录状态
3. 将本地档案转换为云端格式
4. 调用后端 `POST /api/archives/sync` 接口
5. 接收云端返回的最新档案列表
6. 转换为本地格式并覆盖更新
7. 自动触发持久化 (通过 `watch` 机制)
8. 错误处理: 失败时不影响本地数据

### 5. 修改 loadFromStorage

```typescript
const loadFromStorage = async () => {
  try {
    // ... 原有的加载逻辑 ...

    // 如果用户已登录，自动触发云端同步
    if (isLoggedIn.value) {
      console.log('🔄 检测到用户已登录，开始云端同步...')
      await syncWithCloud()
    }
  } catch (error) {
    console.error('❌ 档案数据加载失败:', error)
  }
}
```

**自动触发时机**:
- Store 初始化时调用 `loadFromStorage()`
- 从本地读取数据后
- 检测到用户已登录 (`isLoggedIn.value === true`)
- 自动调用 `syncWithCloud()`

### 6. 导出新增内容

```typescript
return {
  // State
  archives,
  currentArchiveId,
  isSyncing,      // 新增
  isLoggedIn,     // 新增
  
  // Getters
  currentArchive,
  defaultArchive,
  
  // Actions
  addArchive,
  updateArchive,
  deleteArchive,
  switchCurrentArchive,
  setDefaultArchive,
  clearAllArchives,
  loadFromStorage,
  syncWithCloud   // 新增
}
```

## 工作流程

### 初始化流程

```
App 启动
  ↓
Store 初始化
  ↓
loadFromStorage()
  ↓
从本地读取档案数据
  ↓
检查登录状态 (isLoggedIn)
  ↓
如果已登录 → syncWithCloud()
  ↓
调用后端 /api/archives/sync
  ↓
接收云端最新档案列表
  ↓
覆盖更新本地 archives
  ↓
watch 自动触发持久化
  ↓
完成
```

### 手动同步流程

```
用户触发同步
  ↓
调用 syncWithCloud()
  ↓
检查 isSyncing (防止重复)
  ↓
检查 isLoggedIn (确认登录)
  ↓
转换本地档案为云端格式
  ↓
POST /api/archives/sync
  ↓
接收云端响应
  ↓
转换云端档案为本地格式
  ↓
更新 archives.value
  ↓
自动持久化
  ↓
显示成功提示
```

## 数据格式对比

### 本地格式 (Archive)
```json
{
  "id": "1714233600000",
  "name": "张三",
  "gender": 1,
  "birthDate": "1990-05-15",
  "birthTime": "14:30",
  "relation": "本人",
  "isDefault": true,
  "createdAt": 1714233600000
}
```

### 云端格式 (CloudArchive)
```json
{
  "archive_id": "1714233600000",
  "name": "张三",
  "gender": 1,
  "calendar_type": "solar",
  "birth_year": 1990,
  "birth_month": 5,
  "birth_day": 15,
  "birth_hour": 14,
  "birth_minute": 30,
  "tags": "本人",
  "is_default": true,
  "local_created_at": 1714233600000,
  "cloud_uploaded_at": 1714233601000,
  "created_at": "2024-04-27T10:00:00Z",
  "updated_at": "2024-04-27T10:00:01Z"
}
```

## 错误处理

### 网络请求失败
```typescript
catch (error) {
  console.error('❌ 云端同步失败:', error)
  
  // 不影响本地数据的正常使用
  uni.showToast({
    title: '同步失败，使用本地数据',
    icon: 'none',
    duration: 2000
  })
}
```

**特点**:
- 失败时不抛出异常
- 不影响本地数据
- 显示友好提示
- 用户可以继续使用本地功能

### 防止重复同步
```typescript
if (isSyncing.value) {
  console.log('⏳ 正在同步中，跳过本次请求')
  return
}
```

### 未登录处理
```typescript
if (!isLoggedIn.value) {
  console.log('⚠️ 用户未登录，跳过云端同步')
  return
}
```

## 使用示例

### 在组件中手动触发同步

```vue
<template>
  <view>
    <button @click="handleSync" :disabled="archiveStore.isSyncing">
      {{ archiveStore.isSyncing ? '同步中...' : '同步到云端' }}
    </button>
  </view>
</template>

<script setup lang="ts">
import { useArchiveStore } from '@/store/useArchiveStore'

const archiveStore = useArchiveStore()

const handleSync = async () => {
  await archiveStore.syncWithCloud()
}
</script>
```

### 监听同步状态

```vue
<script setup lang="ts">
import { watch } from 'vue'
import { useArchiveStore } from '@/store/useArchiveStore'

const archiveStore = useArchiveStore()

watch(() => archiveStore.isSyncing, (syncing) => {
  if (syncing) {
    console.log('正在同步...')
  } else {
    console.log('同步完成')
  }
})
</script>
```

## 后续优化

### 待实现功能
- [ ] 接入真实的登录系统
- [ ] 从 JWT Token 中获取用户信息
- [ ] 实现增量同步 (只同步变化的档案)
- [ ] 添加同步冲突解决策略
- [ ] 支持离线队列 (离线时记录操作，联网后同步)
- [ ] 添加同步进度提示
- [ ] 实现后台自动同步

### 优化建议
- [ ] 添加同步间隔限制 (避免频繁同步)
- [ ] 实现智能同步 (检测到变化才同步)
- [ ] 添加同步历史记录
- [ ] 支持手动解决冲突

## 注意事项

1. **登录状态**: 当前 `isLoggedIn` 硬编码为 `true`，后续需接入真实登录
2. **时间戳**: 使用毫秒级时间戳 (13位数字)
3. **数据覆盖**: 云端数据会完全覆盖本地数据
4. **自动持久化**: 通过 `watch` 机制自动保存到本地存储
5. **错误容错**: 网络失败不影响本地功能

---

最后更新: 2026-04-27
