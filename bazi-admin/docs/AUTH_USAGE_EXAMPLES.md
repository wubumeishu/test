# JWT 认证使用示例

## 📚 目录

1. [基础使用](#基础使用)
2. [前端集成](#前端集成)
3. [保护现有接口](#保护现有接口)
4. [错误处理](#错误处理)
5. [最佳实践](#最佳实践)

## 基础使用

### 1. 手机号登录

**请求示例**:
```bash
curl -X POST http://localhost:9000/api/auth/login/phone \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000"
  }'
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTU3MDQ4MDB9.xxx",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "用户8000"
}
```

### 2. 获取当前用户信息

**请求示例**:
```bash
curl -X GET http://localhost:9000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "13800138000",
  "nickname": "用户8000",
  "avatar_url": null,
  "created_at": "2026-05-07T10:30:00",
  "last_login": "2026-05-07T12:45:00"
}
```

### 3. 刷新 Token

**请求示例**:
```bash
curl -X POST http://localhost:9000/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_token...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "用户8000"
}
```

## 前端集成

### Vue 3 + TypeScript 示例

#### 1. 创建 API 工具类

```typescript
// src/utils/request.ts
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:9000',
  timeout: 10000
})

// 请求拦截器：自动添加 Token
request.interceptors.request.use(
  (config) => {
    const token = uni.getStorageSync('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理 401 错误
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，清除本地存储并跳转到登录页
      uni.removeStorageSync('access_token')
      uni.removeStorageSync('user_info')
      uni.reLaunch({ url: '/pages/login/login' })
    }
    return Promise.reject(error)
  }
)

export default request
```

#### 2. 创建认证 Store

```typescript
// src/store/useAuthStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'

interface UserInfo {
  user_id: string
  phone: string
  nickname: string
  avatar_url?: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const isLoggedIn = ref<boolean>(false)

  /**
   * 手机号登录
   */
  async function loginByPhone(phone: string) {
    try {
      const response = await request.post('/api/auth/login/phone', { phone })
      
      // 保存 Token
      token.value = response.access_token
      uni.setStorageSync('access_token', response.access_token)
      
      // 保存用户信息
      userInfo.value = {
        user_id: response.user_id,
        phone: phone,
        nickname: response.nickname
      }
      uni.setStorageSync('user_info', userInfo.value)
      
      isLoggedIn.value = true
      
      uni.showToast({
        title: '登录成功',
        icon: 'success'
      })
      
      return response
    } catch (error) {
      console.error('登录失败:', error)
      uni.showToast({
        title: '登录失败',
        icon: 'none'
      })
      throw error
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchUserInfo() {
    try {
      const response = await request.get('/api/auth/me')
      userInfo.value = response
      uni.setStorageSync('user_info', response)
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    token.value = ''
    userInfo.value = null
    isLoggedIn.value = false
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('user_info')
    
    uni.showToast({
      title: '已退出登录',
      icon: 'success'
    })
  }

  /**
   * 从本地存储恢复登录状态
   */
  function restoreLoginState() {
    const savedToken = uni.getStorageSync('access_token')
    const savedUserInfo = uni.getStorageSync('user_info')
    
    if (savedToken && savedUserInfo) {
      token.value = savedToken
      userInfo.value = savedUserInfo
      isLoggedIn.value = true
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    loginByPhone,
    fetchUserInfo,
    logout,
    restoreLoginState
  }
})
```

#### 3. 登录页面

```vue
<!-- pages/login/login.vue -->
<template>
  <view class="login-page">
    <view class="login-form">
      <input
        v-model="phone"
        type="number"
        placeholder="请输入手机号"
        maxlength="11"
      />
      <button @click="handleLogin" :disabled="isLoading">
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/useAuthStore'

const authStore = useAuthStore()
const phone = ref('')
const isLoading = ref(false)

async function handleLogin() {
  if (!phone.value || phone.value.length !== 11) {
    uni.showToast({
      title: '请输入正确的手机号',
      icon: 'none'
    })
    return
  }

  isLoading.value = true
  try {
    await authStore.loginByPhone(phone.value)
    // 登录成功，跳转到首页
    uni.reLaunch({ url: '/pages/index/index' })
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
```

#### 4. 在 App.vue 中恢复登录状态

```vue
<!-- App.vue -->
<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'
import { useAuthStore } from '@/store/useAuthStore'

const authStore = useAuthStore()

onLaunch(() => {
  // 恢复登录状态
  authStore.restoreLoginState()
})
</script>
```

## 保护现有接口

### 示例 1: 档案接口（必须登录）

```python
# src/routers/archive.py
from fastapi import APIRouter, Depends
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/archives", tags=["档案"])

@router.get("/my-archives")
async def get_my_archives(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的档案列表（需要登录）
    """
    # 只返回当前用户的档案
    archives = await get_archives_by_user_id(current_user.user_id)
    return {
        "success": True,
        "archives": archives
    }

@router.post("/create")
async def create_archive(
    data: ArchiveCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    创建档案（需要登录）
    """
    # 自动关联到当前用户
    archive = await create_archive_for_user(
        user_id=current_user.user_id,
        data=data
    )
    return {
        "success": True,
        "archive": archive
    }
```

### 示例 2: 排盘接口（可选登录）

```python
# src/routers/fortune.py
from fastapi import APIRouter, Depends
from src.api.deps import get_current_user_optional
from src.models.user import User
from typing import Optional

router = APIRouter(prefix="/api/fortune", tags=["排盘"])

@router.post("/calculate")
async def calculate_bazi(
    data: BaziCalculateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    八字排盘（可选登录）
    - 登录用户：保存到个人历史记录
    - 未登录用户：仅返回结果，不保存
    """
    # 计算八字
    result = await calculate_bazi_data(data)
    
    # 如果用户已登录，保存到历史记录
    if current_user:
        await save_to_user_history(
            user_id=current_user.user_id,
            result=result
        )
    
    return {
        "success": True,
        "result": result,
        "saved": current_user is not None
    }
```

## 错误处理

### 后端错误响应

```python
# 401 Unauthorized
{
  "detail": "无效的认证凭证"
}

# 401 Unauthorized (用户不存在)
{
  "detail": "用户不存在"
}
```

### 前端错误处理

```typescript
// 统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.detail || '请求失败'
    
    switch (status) {
      case 401:
        // Token 过期或无效
        uni.showToast({
          title: '登录已过期，请重新登录',
          icon: 'none'
        })
        // 清除本地数据并跳转到登录页
        uni.removeStorageSync('access_token')
        uni.reLaunch({ url: '/pages/login/login' })
        break
      
      case 403:
        // 权限不足
        uni.showToast({
          title: '权限不足',
          icon: 'none'
        })
        break
      
      case 500:
        // 服务器错误
        uni.showToast({
          title: '服务器错误，请稍后重试',
          icon: 'none'
        })
        break
      
      default:
        uni.showToast({
          title: message,
          icon: 'none'
        })
    }
    
    return Promise.reject(error)
  }
)
```

## 最佳实践

### 1. Token 存储

✅ **推荐**:
```typescript
// 使用 uni.setStorageSync 存储（加密存储）
uni.setStorageSync('access_token', token)
```

❌ **不推荐**:
```typescript
// 不要存储在全局变量或 localStorage（H5 环境不安全）
window.token = token  // ❌
```

### 2. Token 刷新策略

```typescript
// 方案 1: Token 快过期时自动刷新
async function autoRefreshToken() {
  const token = uni.getStorageSync('access_token')
  if (!token) return
  
  // 解析 Token 获取过期时间
  const payload = parseJWT(token)
  const expiresAt = payload.exp * 1000  // 转换为毫秒
  const now = Date.now()
  
  // 如果 Token 在 1 天内过期，自动刷新
  if (expiresAt - now < 24 * 60 * 60 * 1000) {
    await authStore.refreshToken()
  }
}

// 方案 2: 接口返回 401 时刷新
request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        // 尝试刷新 Token
        await authStore.refreshToken()
        // 重试原请求
        return request(error.config)
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        uni.reLaunch({ url: '/pages/login/login' })
      }
    }
    return Promise.reject(error)
  }
)
```

### 3. 路由守卫

```typescript
// router/index.ts
import { useAuthStore } from '@/store/useAuthStore'

// 需要登录的页面列表
const authPages = [
  '/pages/profile/profile',
  '/pages/archives/archives',
  '/pages/history/history'
]

// 路由守卫
uni.addInterceptor('navigateTo', {
  invoke(args) {
    const authStore = useAuthStore()
    const url = args.url.split('?')[0]
    
    // 检查是否需要登录
    if (authPages.includes(url) && !authStore.isLoggedIn) {
      uni.showToast({
        title: '请先登录',
        icon: 'none'
      })
      uni.navigateTo({ url: '/pages/login/login' })
      return false
    }
    
    return true
  }
})
```

### 4. 安全建议

1. **HTTPS**: 生产环境必须使用 HTTPS
2. **Token 过期时间**: 建议 7-30 天
3. **敏感操作**: 重要操作（如删除数据）需要二次确认
4. **日志记录**: 记录登录日志（IP、设备、时间）
5. **异常登录检测**: 检测异常登录行为（如异地登录）

---

**最后更新**: 2026-05-07
