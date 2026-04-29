# 档案 ID 不匹配问题排查

## 问题时间
2026-04-29 23:01

## 问题现象
前端调用 `/api/fortune/calculate` 接口时，传递的档案 ID `7e6ee150-4cad-41d2-8e91-534547c58882` 在数据库中不存在，返回 404 错误。

## 错误日志
```
🚀 [fortune] 开始排盘，档案ID: 7e6ee150-4cad-41d2-8e91-534547c5882
❌ [fortune] 档案不存在: 7e6ee150-4cad-41d2-8e91-534547c58882
INFO: 127.0.0.1:54627 - "POST /api/fortune/calculate HTTP/1.1" 404 Not Found
```

## 数据库中的档案
通过 `kiro/scripts/check_archives.py` 查询，数据库中有 3 条档案：

1. **档案ID**: `00000000-0000-0000-0000-000000000102`
   - 姓名: 李四
   - 性别: 女
   - 出生日期: 1992-08-20 10:00

2. **档案ID**: `00000000-0000-0000-0000-000000000101`
   - 姓名: 张三 (已更新)
   - 性别: 男
   - 出生日期: 1990-05-15 14:30

3. **档案ID**: `59563ce9-6527-489e-9790-649c2b43e700`
   - 姓名: 测试用户
   - 性别: 男
   - 出生日期: 1990-05-15 14:30

## 问题原因

### 1. 前端本地档案未同步到云端
- 前端在本地生成了档案 ID `7e6ee150-4cad-41d2-8e91-534547c58882`
- 该档案存储在前端本地 Storage 中
- 但该档案**没有成功同步到云端数据库**

### 2. 云端同步逻辑
前端 `useArchiveStore.ts` 中的 `loadFromStorage()` 会在 Store 初始化时自动调用 `syncWithCloud()`：

```typescript
// 如果用户已登录，自动触发云端同步
if (isLoggedIn.value) {
  console.log('🔄 检测到用户已登录，开始云端同步...')
  await syncWithCloud()
}
```

但是，可能由于以下原因导致同步失败：
- 网络请求失败
- 后端接口异常
- 前端在同步前就发起了排盘请求

### 3. 同步接口逻辑
后端 `/api/archives/sync` 接口会：
1. 接收前端传递的本地档案列表
2. 使用 `UPSERT` 逻辑（存在则更新，不存在则插入）
3. 返回云端的最新档案列表

## 解决方案

### 方案 1：清空前端本地数据，重新同步（推荐）

在浏览器控制台执行：

```javascript
// 清空本地档案数据
uni.removeStorageSync('bazi_archives')
uni.removeStorageSync('bazi_current_id')

// 刷新页面
location.reload()
```

然后在前端重新创建档案，系统会自动同步到云端。

### 方案 2：手动触发云端同步

在前端页面中添加一个"同步到云端"按钮，手动调用 `syncWithCloud()` 方法。

### 方案 3：使用数据库中已有的档案

直接使用数据库中已有的档案 ID 进行测试：
- `00000000-0000-0000-0000-000000000102` (李四)
- `00000000-0000-0000-0000-000000000101` (张三)
- `59563ce9-6527-489e-9790-649c2b43e700` (测试用户)

### 方案 4：检查同步接口是否正常

运行测试脚本验证同步接口：

```bash
python kiro/scripts/test_archive_sync.py
```

## 预防措施

### 1. 前端增强错误处理
在 `useBaziStore.ts` 的 `calculateBazi()` 方法中，捕获 404 错误并提示用户：

```typescript
if (error.statusCode === 404) {
  uni.showModal({
    title: '档案不存在',
    content: '该档案未同步到云端，是否立即同步？',
    success: (res) => {
      if (res.confirm) {
        archiveStore.syncWithCloud()
      }
    }
  })
}
```

### 2. 排盘前自动检查同步状态
在调用排盘接口前，先检查档案是否已同步：

```typescript
// 如果档案未同步，先同步
if (!archiveStore.isSyncing && archiveStore.isLoggedIn) {
  await archiveStore.syncWithCloud()
}
```

### 3. 后端增加更友好的错误提示
在 `fortune.py` 中，当档案不存在时，返回更详细的错误信息：

```python
if archive is None:
    raise HTTPException(
        status_code=404,
        detail={
            "message": "未找到该档案",
            "archive_id": request.archive_id,
            "suggestion": "请检查档案是否已同步到云端，或使用 /api/archives/sync 接口同步档案"
        }
    )
```

## 测试步骤

1. **清空前端本地数据**
   ```javascript
   uni.removeStorageSync('bazi_archives')
   uni.removeStorageSync('bazi_current_id')
   location.reload()
   ```

2. **在前端创建新档案**
   - 进入档案管理页面
   - 添加新档案
   - 系统会自动同步到云端

3. **验证同步成功**
   ```bash
   python kiro/scripts/check_archives.py
   ```

4. **进行八字排盘**
   - 选择刚创建的档案
   - 点击排盘按钮
   - 应该能成功返回结果

## 相关文件

- **前端档案 Store**: `my-bazi-app/src/store/useArchiveStore.ts`
- **前端排盘 Store**: `my-bazi-app/src/store/useBaziStore.ts`
- **后端同步接口**: `bazi-admin/src/routers/archives.py`
- **后端排盘接口**: `bazi-admin/src/routers/fortune.py`
- **检查脚本**: `kiro/scripts/check_archives.py`
- **测试脚本**: `kiro/scripts/test_archive_sync.py`

---

**状态**: 🔍 问题已定位，等待用户选择解决方案
**优先级**: 高
**影响范围**: 前端排盘功能无法使用
