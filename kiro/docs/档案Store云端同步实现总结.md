# 档案 Store 云端同步实现总结

## 完成时间
2026-04-27

## 修改文件
`my-bazi-app/src/store/useArchiveStore.ts`

## 实现功能

### ✅ 1. 云端同步接口集成

**新增 Action**: `syncWithCloud()`

**功能**:
- 调用后端 `POST /api/archives/sync` 接口
- 将本地档案全部发送给后端
- 接收云端返回的最新档案列表
- 覆盖更新本地 archives 状态
- 自动触发持久化 (通过 watch 机制)

### ✅ 2. 数据格式转换

**convertToCloudArchive**: 本地 → 云端
```typescript
Archive {
  id, name, gender,
  birthDate, birthTime,
  relation, isDefault, createdAt
}
↓
CloudArchive {
  archive_id, name, gender,
  birth_year, birth_month, birth_day,
  birth_hour, birth_minute,
  tags, is_default, local_created_at
}
```

**convertToLocalArchive**: 云端 → 本地
```typescript
CloudArchive → Archive
```

### ✅ 3. 自动触发机制

**修改 loadFromStorage**:
```typescript
const loadFromStorage = async () => {
  // 1. 从本地读取数据
  // 2. 检查登录状态
  if (isLoggedIn.value) {
    // 3. 自动调用 syncWithCloud()
    await syncWithCloud()
  }
}
```

**触发时机**:
- Store 初始化时
- 用户已登录时 (当前模拟为 true)

### ✅ 4. 错误处理

**网络请求失败**:
```typescript
catch (error) {
  console.error('❌ 云端同步失败:', error)
  
  // 不影响本地数据的正常使用
  uni.showToast({
    title: '同步失败，使用本地数据',
    icon: 'none'
  })
}
```

**特点**:
- 失败时不抛出异常
- 不影响本地功能
- 显示友好提示

### ✅ 5. 防止重复同步

```typescript
const isSyncing = ref<boolean>(false)

if (isSyncing.value) {
  return  // 跳过
}

isSyncing.value = true
try {
  // 同步逻辑
} finally {
  isSyncing.value = false
}
```

### ✅ 6. 登录状态检查

```typescript
const isLoggedIn = ref<boolean>(true)  // 模拟登录

if (!isLoggedIn.value) {
  return  // 跳过同步
}
```

## 技术实现

### 1. 接口调用

```typescript
import { post } from '@/utils/request'

const response = await post<SyncResponse>('/api/archives/sync', {
  archives: cloudArchives
})
```

### 2. 数据转换

**日期时间拆分**:
```typescript
const [year, month, day] = archive.birthDate.split('-').map(Number)
const [hour, minute] = archive.birthTime.split(':').map(Number)
```

**日期时间组合**:
```typescript
const birthDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
const birthTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
```

### 3. 状态更新

```typescript
// 覆盖更新
archives.value = newArchives

// watch 自动触发持久化
// 无需手动调用 saveArchivesToStorage()
```

### 4. 当前选中档案处理

```typescript
// 如果当前选中的档案不存在了，重新选择
if (currentArchiveId.value && !archives.value.find(a => a.id === currentArchiveId.value)) {
  if (archives.value.length > 0) {
    currentArchiveId.value = archives.value[0].id
  } else {
    currentArchiveId.value = ''
  }
}
```

## 工作流程

```
App 启动
  ↓
Store 初始化
  ↓
loadFromStorage()
  ↓
从本地读取档案
  ↓
检查登录状态
  ↓
isLoggedIn === true
  ↓
syncWithCloud()
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
watch 自动触发持久化
  ↓
uni.setStorageSync('bazi_archives', archives.value)
  ↓
完成
```

## 新增 State

```typescript
const isSyncing = ref<boolean>(false)    // 同步状态
const isLoggedIn = ref<boolean>(true)    // 登录状态 (模拟)
```

## 新增方法

```typescript
// 转换函数
convertToCloudArchive(archive: Archive): CloudArchive
convertToLocalArchive(cloudArchive: CloudArchive): Archive

// 同步方法
syncWithCloud(): Promise<void>
```

## 导出内容

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

## 测试验证

### 测试场景
1. ✅ 首次启动自动同步
2. ✅ 本地数据上传到云端
3. ✅ 云端数据下载到本地
4. ✅ 数据格式转换正确
5. ✅ 网络失败不影响本地
6. ✅ 防止重复同步
7. ✅ 自动持久化

### 测试方法
```bash
# 1. 启动后端
cd bazi-admin
uvicorn main:app --host 127.0.0.1 --port 9000 --reload

# 2. 启动前端
cd my-bazi-app
npm run dev:h5

# 3. 访问
http://localhost:5173
```

## 配套文档

1. **档案Store云端同步集成.md** - 详细的实现说明
2. **前后端联调测试指南.md** - 完整的测试指南
3. **档案同步接口文档.md** - 后端接口文档

## 后续工作

### 待实现
- [ ] 接入真实登录系统
- [ ] 从 JWT Token 获取用户信息
- [ ] 实现增量同步
- [ ] 添加同步冲突解决
- [ ] 支持离线队列
- [ ] 添加同步进度提示

### 优化建议
- [ ] 添加同步间隔限制
- [ ] 实现智能同步 (检测变化)
- [ ] 添加同步历史记录
- [ ] 支持手动解决冲突

## 关键特性

### 1. 自动同步
- Store 初始化时自动触发
- 用户登录后自动同步
- 无需手动调用

### 2. 自动持久化
- 通过 watch 机制
- 数据变化自动保存
- 无需手动调用

### 3. 错误容错
- 网络失败不影响本地
- 显示友好提示
- 用户可继续使用

### 4. 防止重复
- isSyncing 标志
- 同步中跳过新请求
- 避免并发问题

### 5. 数据一致性
- 归宗算法保证
- 时间戳对比
- 云端数据为准

## 验收清单

✅ 代码无语法错误  
✅ 接口调用正确  
✅ 数据格式转换无误  
✅ 自动触发机制正常  
✅ 错误处理完善  
✅ 防止重复同步  
✅ 自动持久化正常  
✅ 文档完整详细  

---

完成时间: 2026-04-27  
状态: ✅ 完成
