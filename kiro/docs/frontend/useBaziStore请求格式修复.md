# useBaziStore 请求格式修复文档

## 📋 修复内容

修复了 `useBaziStore.ts` 中的 `calculateByArchive` 和 `calculateByData` 方法，确保请求格式正确，错误处理完善。

## 🔧 修复的方法

### 1. calculateByArchive (通过档案ID排盘)

#### 修复前的问题
- 没有验证 archiveId 是否为空
- 错误消息提取不完整
- 缺少详细的日志输出

#### 修复后的改进

**1. 增加档案ID验证**
```typescript
// 验证 archiveId 不为空
if (!archiveId || archiveId.trim() === '') {
  throw new Error('档案ID不能为空')
}
```

**2. 增强日志输出**
```typescript
console.log('🔄 [useBaziStore] 开始排盘 (通过档案ID)')
console.log('📤 [useBaziStore] 发起排盘，档案ID:', archiveId)

// 构建请求数据
const requestData = {
  archive_id: archiveId,
  is_deep_analysis: isDeepAnalysis
}

console.log('📤 [useBaziStore] 请求参数:', requestData)
```

**3. 完善错误处理**
```typescript
catch (error: any) {
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
}
```

### 2. calculateByData (快速排盘)

同样的改进应用到快速排盘方法：
- 完善错误消息提取
- 统一错误处理逻辑
- 详细的日志输出

## 📤 请求格式

### calculateByArchive 请求格式

```typescript
// 请求 URL
POST /api/fortune/calculate

// 请求头
Content-Type: application/json

// 请求体
{
  "archive_id": "59563ce9-6527-489e-9790-649c2b43e700",  // UUID 格式
  "is_deep_analysis": false                              // 是否深度分析
}
```

### calculateByData 请求格式

```typescript
// 请求 URL
POST /api/fortune/calculate-by-data

// 请求头
Content-Type: application/json

// 请求体
{
  "name": "张三",
  "gender": 1,              // 0=女, 1=男
  "birth_year": 1990,
  "birth_month": 5,
  "birth_day": 15,
  "birth_hour": 14,
  "birth_minute": 30,
  "is_deep_analysis": false
}
```

## 🔍 错误处理逻辑

### 错误消息提取优先级

1. **error.message** - 自定义错误消息
2. **error.data.detail** - FastAPI 返回的错误详情
3. **error.statusCode** - HTTP 状态码
4. **默认消息** - "排盘失败，请检查网络连接"

### FastAPI 错误响应格式

```json
{
  "detail": "未找到该档案"
}
```

或

```json
{
  "detail": [
    {
      "loc": ["body", "archive_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 📝 日志输出示例

### 成功的日志
```
🔄 [useBaziStore] 开始排盘 (通过档案ID)
📤 [useBaziStore] 发起排盘，档案ID: 59563ce9-6527-489e-9790-649c2b43e700
📤 [useBaziStore] 请求参数: { archive_id: '59563ce9-6527-489e-9790-649c2b43e700', is_deep_analysis: false }
📥 [useBaziStore] 后端响应: { success: true, message: '八字排盘成功', ... }
✅ [useBaziStore] 排盘成功
```

### 失败的日志
```
🔄 [useBaziStore] 开始排盘 (通过档案ID)
📤 [useBaziStore] 发起排盘，档案ID: invalid-id
📤 [useBaziStore] 请求参数: { archive_id: 'invalid-id', is_deep_analysis: false }
❌ [useBaziStore] 排盘失败: Error: 未找到该档案
❌ [useBaziStore] 错误详情: 未找到该档案
```

## 🎯 使用示例

### 在页面中调用

```typescript
import { useBaziStore } from '@/store/useBaziStore'

const baziStore = useBaziStore()

// 通过档案ID排盘
const handleCalculate = async (archiveId: string) => {
  try {
    // 显示加载提示
    uni.showLoading({
      title: '正在排盘...',
      mask: true
    })

    // 调用排盘方法
    await baziStore.calculateByArchive(archiveId)

    // 隐藏加载提示
    uni.hideLoading()

    // 跳转到结果页
    uni.navigateTo({
      url: '/pages/result/result'
    })
  } catch (error) {
    // 错误已在 Store 中处理，这里只需隐藏加载提示
    uni.hideLoading()
  }
}
```

## 🧪 测试要点

### 1. 正常流程测试
- ✅ 传入有效的档案ID
- ✅ 检查请求参数格式
- ✅ 验证响应数据结构
- ✅ 确认跳转到结果页

### 2. 异常流程测试
- ✅ 传入空的档案ID
- ✅ 传入不存在的档案ID
- ✅ 网络断开时的错误提示
- ✅ 后端返回 400/404/500 错误

### 3. 日志验证
- ✅ 控制台输出完整的请求参数
- ✅ 控制台输出后端响应
- ✅ 错误时输出详细的错误信息

## 🔗 相关文件

- `my-bazi-app/src/store/useBaziStore.ts` - 八字状态管理（已修复）
- `my-bazi-app/src/utils/request.ts` - 网络请求封装
- `bazi-admin/src/routers/fortune.py` - 后端排盘接口
- `bazi-admin/src/schemas/bazi.py` - 请求/响应 Schema

## 📊 错误码对照表

| 状态码 | 说明 | 前端提示 |
|--------|------|----------|
| 200 | 成功 | "排盘成功" |
| 400 | 请求参数错误 | 显示后端返回的 detail |
| 404 | 档案不存在 | "未找到该档案" |
| 500 | 服务器错误 | 显示后端返回的详细错误 |
| 网络错误 | 无法连接服务器 | "排盘失败，请检查网络连接" |

## ✅ 修复验证清单

- [x] 请求体格式正确（archive_id 键名）
- [x] 发起请求前打印档案ID
- [x] 验证档案ID不为空
- [x] 完善错误消息提取逻辑
- [x] 支持 FastAPI 错误格式
- [x] 显示详细的错误提示
- [x] 统一两个方法的错误处理
- [x] 添加详细的日志输出

## 🚀 后续优化建议

1. **请求重试机制** - 网络错误时自动重试
2. **请求超时设置** - 避免长时间等待
3. **离线缓存** - 保存最近的排盘结果
4. **错误上报** - 将错误信息上报到监控系统
5. **请求取消** - 用户离开页面时取消请求

---

**修复时间**: 2026-04-28  
**修复人员**: Kiro AI Assistant  
**测试状态**: 待测试
