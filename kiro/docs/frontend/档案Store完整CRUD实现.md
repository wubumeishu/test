# 档案 Store 完整 CRUD 实现

## 更新时间
2026-04-29

## 概述
完善了前端档案状态管理文件 `src/store/useArchiveStore.ts`，实现了完整的 CRUD 操作，打通了前后端数据流。

## 主要更新内容

### 1. 引入依赖
```typescript
import { get, post, del } from '@/utils/request'
```
- 引入了 `get`、`post`、`del` 方法，用于与后端 API 通信

### 2. State 定义
```typescript
const archives = ref<Archive[]>([])           // 档案列表数组
const currentArchiveId = ref<string>('')      // 当前选中的档案 ID
const isLoading = ref<boolean>(false)         // 加载状态（新增）
const isSyncing = ref<boolean>(false)         // 同步状态
const isLoggedIn = ref<boolean>(true)         // 登录状态
```

### 3. 完整的 CRUD Actions

#### 3.1 fetchArchives() - 获取档案列表
- **接口**: `GET /api/archives/list`
- **功能**: 从云端获取用户的所有档案列表
- **流程**:
  1. 检查登录状态
  2. 设置 `isLoading = true`
  3. 调用后端 API 获取云端档案
  4. 将云端格式转换为本地格式
  5. 更新 `archives` 状态
  6. 处理当前选中档案的有效性
  7. 显示成功提示
- **异常处理**: 
  - 捕获错误并显示错误提示
  - 确保 `isLoading` 在 finally 中重置

#### 3.2 addArchive(archiveData) - 添加档案
- **接口**: 通过 `syncWithCloud()` 同步到云端
- **功能**: 添加新档案到本地，然后同步到云端
- **流程**:
  1. 设置 `isLoading = true`
  2. 生成 UUID 格式的档案 ID
  3. 创建新档案对象
  4. 处理默认档案逻辑
  5. 添加到本地数组头部
  6. 如果已登录，调用 `syncWithCloud()` 同步到云端
  7. 显示成功提示
- **异常处理**:
  - 捕获错误并显示错误提示
  - 抛出错误供调用方处理
  - 确保 `isLoading` 在 finally 中重置

#### 3.3 updateArchive(archiveId, updateData) - 更新档案
- **接口**: 通过 `syncWithCloud()` 同步到云端
- **功能**: 更新档案信息，然后同步到云端
- **流程**:
  1. 设置 `isLoading = true`
  2. 查找要更新的档案
  3. 处理默认档案逻辑
  4. 更新本地档案数据
  5. 如果已登录，调用 `syncWithCloud()` 同步到云端
  6. 显示成功提示
- **异常处理**:
  - 档案不存在时显示错误提示并返回 false
  - 捕获错误并显示错误提示
  - 确保 `isLoading` 在 finally 中重置

#### 3.4 deleteArchive(archiveId) - 删除档案
- **接口**: `DELETE /api/archives/{archive_id}`
- **功能**: 删除指定档案，先调用云端删除，成功后刷新列表
- **流程**:
  1. 设置 `isLoading = true`
  2. 查找要删除的档案
  3. 如果已登录，先调用云端删除接口
  4. 删除本地档案
  5. 如果删除的是当前选中档案，自动选中其他档案或清空
  6. 如果已登录，调用 `fetchArchives()` 刷新列表
  7. 显示成功提示
- **异常处理**:
  - 档案不存在时显示错误提示并返回 false
  - 捕获错误并显示错误提示
  - 确保 `isLoading` 在 finally 中重置

#### 3.5 syncWithCloud() - 云端同步（优化）
- **接口**: `POST /api/archives/sync`
- **功能**: 将本地档案同步到云端，并获取最新的云端档案列表
- **优化**: 
  - 添加了 `isLoading` 状态管理
  - 在 finally 中同时重置 `isSyncing` 和 `isLoading`

## 异常处理机制

### 统一的错误处理模式
所有 CRUD 操作都遵循以下异常处理模式：

```typescript
try {
  isLoading.value = true
  
  // 执行业务逻辑
  // ...
  
  // 显示成功提示
  uni.showToast({
    title: '操作成功',
    icon: 'success',
    duration: 1500
  })
  
} catch (error) {
  console.error('❌ 操作失败:', error)
  
  uni.showToast({
    title: '操作失败',
    icon: 'error',
    duration: 2000
  })
  
} finally {
  isLoading.value = false
}
```

### 错误提示
- 使用 `uni.showToast` 向用户显示友好的错误提示
- 使用 `console.error` 记录详细的错误信息，便于调试
- 区分不同类型的错误（档案不存在、网络错误等）

### 状态管理
- 在 `try` 块开始时设置 `isLoading = true`
- 在 `finally` 块中重置 `isLoading = false`
- 确保无论成功或失败，加载状态都能正确重置

## 后端 API 对应关系

| 前端方法 | 后端接口 | HTTP 方法 | 说明 |
|---------|---------|----------|------|
| `fetchArchives()` | `/api/archives/list` | GET | 获取档案列表 |
| `addArchive()` | `/api/archives/sync` | POST | 通过同步接口添加 |
| `updateArchive()` | `/api/archives/sync` | POST | 通过同步接口更新 |
| `deleteArchive()` | `/api/archives/{archive_id}` | DELETE | 删除档案 |
| `syncWithCloud()` | `/api/archives/sync` | POST | 云端同步 |

## 数据流转

### 添加档案流程
```
用户输入 → addArchive() → 本地添加 → syncWithCloud() → 后端同步 → 返回最新列表 → 更新本地
```

### 更新档案流程
```
用户修改 → updateArchive() → 本地更新 → syncWithCloud() → 后端同步 → 返回最新列表 → 更新本地
```

### 删除档案流程
```
用户删除 → deleteArchive() → 调用后端删除 → 删除本地 → fetchArchives() → 刷新列表
```

### 获取档案流程
```
页面加载 → fetchArchives() → 调用后端 → 获取云端列表 → 转换格式 → 更新本地
```

## 使用示例

### 1. 获取档案列表
```typescript
import { useArchiveStore } from '@/store/useArchiveStore'

const archiveStore = useArchiveStore()

// 获取档案列表
await archiveStore.fetchArchives()

// 访问档案列表
console.log(archiveStore.archives)

// 检查加载状态
console.log(archiveStore.isLoading)
```

### 2. 添加档案
```typescript
const newArchive = await archiveStore.addArchive({
  name: '张三',
  gender: 1,
  birthDate: '1990-05-15',
  birthTime: '14:30',
  relation: '本人',
  isDefault: true
})
```

### 3. 更新档案
```typescript
await archiveStore.updateArchive('archive-id-123', {
  name: '李四',
  relation: '朋友'
})
```

### 4. 删除档案
```typescript
await archiveStore.deleteArchive('archive-id-123')
```

## 注意事项

1. **登录状态检查**: 所有云端操作都会先检查 `isLoggedIn` 状态
2. **加载状态管理**: 使用 `isLoading` 状态控制 UI 加载提示
3. **错误处理**: 所有操作都有完善的 try-catch-finally 错误处理
4. **自动持久化**: 本地数据通过 watch 自动持久化到 localStorage
5. **当前档案管理**: 删除档案时会自动处理当前选中档案的切换
6. **默认档案逻辑**: 添加/更新档案时会自动处理默认档案的唯一性

## 测试建议

### 1. 测试获取档案列表
```typescript
// 在页面 onMounted 中调用
onMounted(async () => {
  await archiveStore.fetchArchives()
})
```

### 2. 测试添加档案
```typescript
// 在表单提交时调用
const handleSubmit = async () => {
  try {
    await archiveStore.addArchive(formData)
    // 添加成功后的处理
  } catch (error) {
    // 错误处理
  }
}
```

### 3. 测试更新档案
```typescript
// 在编辑表单提交时调用
const handleUpdate = async () => {
  try {
    await archiveStore.updateArchive(archiveId, formData)
    // 更新成功后的处理
  } catch (error) {
    // 错误处理
  }
}
```

### 4. 测试删除档案
```typescript
// 在删除按钮点击时调用
const handleDelete = async (archiveId: string) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个档案吗？',
    success: async (res) => {
      if (res.confirm) {
        await archiveStore.deleteArchive(archiveId)
      }
    }
  })
}
```

## 后续优化建议

1. **接入真实登录系统**: 将 `isLoggedIn` 与真实的用户登录状态绑定
2. **离线支持**: 增强离线模式下的数据处理能力
3. **冲突解决**: 实现更复杂的数据冲突解决策略
4. **批量操作**: 支持批量添加、更新、删除档案
5. **数据缓存**: 实现更智能的数据缓存策略，减少不必要的网络请求
6. **乐观更新**: 实现乐观更新策略，提升用户体验

## 相关文档

- [数据库模型设计](../backend/数据库模型设计.md)
- [档案同步接口文档](../backend/档案同步接口文档.md)
- [前后端联调测试指南](../前后端联调测试指南.md)

---

最后更新: 2026-04-29
