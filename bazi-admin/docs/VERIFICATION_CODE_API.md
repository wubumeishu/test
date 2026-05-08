# 验证码登录 API 文档

## 📋 概述

本文档说明基于 Redis 的验证码发送和登录接口的使用方法。

## 🏗️ 架构设计

### 登录流程

```
1. 用户输入手机号
2. 前端调用 /api/auth/send-code 发送验证码
3. 后端生成 6 位验证码，存入 Redis（5 分钟过期）
4. 联调阶段：验证码打印在控制台（不真实发送短信）
5. 用户输入验证码
6. 前端调用 /api/auth/login 验证登录
7. 后端验证验证码，查询或创建用户
8. 返回 JWT Token 和用户信息
```

### 技术栈

- **Redis**: 存储验证码（5 分钟过期）
- **JWT**: 用户认证令牌
- **PostgreSQL**: 用户数据持久化

## 📦 安装依赖

```bash
cd bazi-admin
pip install -r requirements.txt
```

新增的依赖包括：
- `redis[hiredis]` - Redis 客户端（带 C 扩展）
- `aioredis` - 异步 Redis 支持

## ⚙️ 环境变量配置

在 `bazi-admin/.env` 文件中添加 Redis 配置：

```bash
# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 如果 Redis 有密码
# REDIS_URL=redis://:password@localhost:6379/0
```

## 🚀 启动 Redis

### Windows
```bash
# 下载 Redis for Windows
# https://github.com/tporadowski/redis/releases
# 解压后运行 redis-server.exe
```

### Linux/Mac
```bash
# 使用包管理器安装
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# 启动 Redis
redis-server
```

### Docker
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

## 📡 API 接口

### 1. 发送验证码

**接口**: `POST /api/auth/send-code`

**请求参数**:
```json
{
  "phone": "13800138000"
}
```

**响应示例**:
```json
{
  "msg": "验证码已发送"
}
```

**控制台输出**（联调阶段）:
```
============================================================
📱 验证码发送成功（模拟）
   手机号: 13800138000
   验证码: 123456
   有效期: 5 分钟
============================================================
```

**错误响应**:
```json
{
  "detail": "手机号格式错误"
}
```

### 2. 验证码登录

**接口**: `POST /api/auth/login`

**请求参数**:
```json
{
  "phone": "13800138000",
  "code": "123456"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "13800138000",
    "nickname": "用户8000"
  }
}
```

**错误响应**:

验证码过期:
```json
{
  "detail": "验证码已过期或不存在，请重新获取"
}
```

验证码错误:
```json
{
  "detail": "验证码错误"
}
```

## 🧪 测试

### 1. 测试 Redis 连接

```bash
python test_verification_code.py
```

预期输出:
```
🧪 ============================================================
🧪  验证码功能测试
🧪 ============================================================

============================================================
测试 1: Redis 连接
============================================================
✅ Redis 连接成功
✅ Redis 写入成功
✅ Redis 读取成功: test_value
✅ Redis 设置过期时间成功

============================================================
测试 2: 验证码存储
============================================================
✅ 验证码存储成功: 13800138000 -> 123456
✅ 验证码读取成功: 123456
✅ 验证码删除成功

============================================================
测试 3: 验证码过期
============================================================
✅ 验证码存储成功（2秒过期）: 13800138001 -> 654321
✅ 立即读取成功: 654321
⏳ 等待 3 秒...
✅ 验证码已过期（符合预期）

============================================================
测试结果汇总
============================================================
✅ 通过 - Redis 连接
✅ 通过 - 验证码存储
✅ 通过 - 验证码过期
============================================================

🎉 所有测试通过！验证码功能已就绪。
```

### 2. 测试 API 接口

#### 使用 curl

```bash
# 1. 发送验证码
curl -X POST http://localhost:9000/api/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'

# 2. 查看控制台获取验证码（例如: 123456）

# 3. 登录
curl -X POST http://localhost:9000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "code": "123456"}'
```

#### 使用 Swagger UI

1. 启动服务: `uvicorn main:app --host 0.0.0.0 --port 9000 --reload`
2. 访问: http://localhost:9000/docs
3. 找到 `/api/auth/send-code` 接口，点击 "Try it out"
4. 输入手机号，点击 "Execute"
5. 查看控制台获取验证码
6. 找到 `/api/auth/login` 接口，输入手机号和验证码
7. 点击 "Execute"，获取 Token

## 💻 前端集成

### Vue 3 + TypeScript 示例

#### 1. 发送验证码

```typescript
// src/api/auth.ts
import request from '@/utils/request'

/**
 * 发送验证码
 */
export async function sendVerificationCode(phone: string) {
  return await request.post('/api/auth/send-code', { phone })
}

/**
 * 验证码登录
 */
export async function loginWithCode(phone: string, code: string) {
  return await request.post('/api/auth/login', { phone, code })
}
```

#### 2. 登录页面

```vue
<template>
  <view class="login-page">
    <view class="login-form">
      <!-- 手机号输入 -->
      <input
        v-model="phone"
        type="number"
        placeholder="请输入手机号"
        maxlength="11"
      />
      
      <!-- 验证码输入 -->
      <view class="code-input-wrapper">
        <input
          v-model="code"
          type="number"
          placeholder="请输入验证码"
          maxlength="6"
        />
        <button
          @click="handleSendCode"
          :disabled="countdown > 0"
          class="send-code-btn"
        >
          {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
        </button>
      </view>
      
      <!-- 登录按钮 -->
      <button @click="handleLogin" :disabled="isLoading">
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { sendVerificationCode, loginWithCode } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'

const authStore = useAuthStore()

const phone = ref('')
const code = ref('')
const countdown = ref(0)
const isLoading = ref(false)

/**
 * 发送验证码
 */
async function handleSendCode() {
  // 验证手机号
  if (!phone.value || phone.value.length !== 11) {
    uni.showToast({
      title: '请输入正确的手机号',
      icon: 'none'
    })
    return
  }

  try {
    await sendVerificationCode(phone.value)
    
    uni.showToast({
      title: '验证码已发送',
      icon: 'success'
    })
    
    // 开始倒计时（60秒）
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
    uni.showToast({
      title: '发送失败，请重试',
      icon: 'none'
    })
  }
}

/**
 * 登录
 */
async function handleLogin() {
  // 验证输入
  if (!phone.value || phone.value.length !== 11) {
    uni.showToast({
      title: '请输入正确的手机号',
      icon: 'none'
    })
    return
  }

  if (!code.value || code.value.length !== 6) {
    uni.showToast({
      title: '请输入6位验证码',
      icon: 'none'
    })
    return
  }

  isLoading.value = true
  try {
    const response = await loginWithCode(phone.value, code.value)
    
    // 保存 Token
    uni.setStorageSync('access_token', response.access_token)
    
    // 保存用户信息
    uni.setStorageSync('user_info', response.user)
    
    // 更新 Store
    authStore.setUserInfo(response.user)
    
    uni.showToast({
      title: '登录成功',
      icon: 'success'
    })
    
    // 跳转到首页
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/index/index' })
    }, 1000)
  } catch (error: any) {
    console.error('登录失败:', error)
    
    const message = error.response?.data?.detail || '登录失败，请重试'
    uni.showToast({
      title: message,
      icon: 'none'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  padding: 40rpx;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.code-input-wrapper {
  display: flex;
  gap: 20rpx;
}

.send-code-btn {
  flex-shrink: 0;
  width: 200rpx;
  font-size: 28rpx;
}
</style>
```

## 🔒 安全建议

### 联调阶段

1. **验证码打印在控制台**
   - 方便前后端联调
   - 无需真实短信服务

2. **验证码有效期 5 分钟**
   - 防止验证码被长期使用

3. **验证码使用后立即删除**
   - 防止重复使用

### 生产环境必做

1. **集成真实短信服务**
   ```python
   # 示例：阿里云短信服务
   from aliyunsdkcore.client import AcsClient
   from aliyunsdkcore.request import CommonRequest
   
   async def send_sms(phone: str, code: str):
       client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-hangzhou')
       request = CommonRequest()
       request.set_domain('dysmsapi.aliyuncs.com')
       request.set_version('2017-05-25')
       request.set_action_name('SendSms')
       request.add_query_param('PhoneNumbers', phone)
       request.add_query_param('SignName', '您的签名')
       request.add_query_param('TemplateCode', 'SMS_123456789')
       request.add_query_param('TemplateParam', f'{{"code":"{code}"}}')
       response = client.do_action_with_exception(request)
       return response
   ```

2. **速率限制**
   - 同一手机号 1 分钟内只能发送 1 次
   - 同一 IP 1 小时内最多发送 10 次

3. **验证码复杂度**
   - 生产环境可使用字母+数字组合
   - 增加破解难度

4. **日志记录**
   - 记录验证码发送日志
   - 记录登录尝试日志
   - 便于审计和排查问题

## 🐛 常见问题

### Q1: Redis 连接失败

**原因**: Redis 未启动或配置错误

**解决**:
```bash
# 检查 Redis 是否运行
redis-cli ping
# 应该返回: PONG

# 检查 .env 中的 REDIS_URL
echo $REDIS_URL
```

### Q2: 验证码已过期

**原因**: 验证码有效期 5 分钟

**解决**: 重新发送验证码

### Q3: 验证码错误

**原因**: 输入的验证码与 Redis 中存储的不一致

**解决**: 
- 检查控制台打印的验证码
- 确保输入正确

### Q4: 用户自动注册失败

**原因**: 数据库连接失败或字段缺失

**解决**:
```bash
# 检查数据库连接
psql $DATABASE_URL -c "SELECT 1"

# 确保 users 表存在
psql $DATABASE_URL -c "\d users"
```

## 📚 参考资料

- [Redis 文档](https://redis.io/docs/)
- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [阿里云短信服务](https://help.aliyun.com/product/44282.html)
- [腾讯云短信服务](https://cloud.tencent.com/product/sms)

---

**最后更新**: 2026-05-07
