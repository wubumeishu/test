<template>
  <view class="page-container">
    <ZenHeader title="个人资料" :show-back="true" />

    <view class="main-content">

      <!-- ── 头像区域 ── -->
      <view class="section-card">
        <view class="section-title">头像</view>
        <view class="avatar-row">
          <view class="avatar-preview">
            <image
              class="avatar-img"
              :src="form.avatar_url || defaultAvatar"
              mode="aspectFill"
              @error="onAvatarError"
            />
          </view>

          <!--
            微信官方 API：open-type="chooseAvatar"
            用户点击后会弹出微信头像选择器，选择后触发 @chooseavatar 事件。
            ⚠️ 此 button 必须是原生 button 组件，不能用 view 替代。
            ⚠️ 仅在微信小程序环境生效，H5/App 降级为普通上传。
          -->
          <!-- #ifdef MP-WEIXIN -->
          <button
            class="change-avatar-btn"
            :class="{ uploading: isUploadingAvatar }"
            :disabled="isUploadingAvatar"
            open-type="chooseAvatar"
            @chooseavatar="onChooseAvatar"
          >
            <text class="material-symbols-outlined btn-icon">
              {{ isUploadingAvatar ? 'hourglass_empty' : 'photo_camera' }}
            </text>
            <text class="btn-text">{{ isUploadingAvatar ? '上传中...' : '更换头像' }}</text>
          </button>
          <!-- #endif -->

          <!-- H5 / App 降级方案 -->
          <!-- #ifndef MP-WEIXIN -->
          <button
            class="change-avatar-btn"
            :class="{ uploading: isUploadingAvatar }"
            :disabled="isUploadingAvatar"
            @click="onChooseAvatarFallback"
          >
            <text class="material-symbols-outlined btn-icon">
              {{ isUploadingAvatar ? 'hourglass_empty' : 'photo_camera' }}
            </text>
            <text class="btn-text">{{ isUploadingAvatar ? '上传中...' : '更换头像' }}</text>
          </button>
          <!-- #endif -->
        </view>
      </view>

      <!-- ── 昵称区域 ── -->
      <view class="section-card">
        <view class="section-title">昵称</view>
        <!--
          微信官方 API：type="nickname"
          用户聚焦时会弹出微信昵称填写面板，可一键填入微信昵称。
          @blur 时读取最终值（@input 在昵称面板选择时不触发）。
          ⚠️ 仅在微信小程序环境生效，H5/App 降级为普通文本输入。
        -->
        <!-- #ifdef MP-WEIXIN -->
        <view class="input-wrapper">
          <input
            type="nickname"
            class="zen-input"
            :value="form.nickname"
            placeholder="点击填写昵称（可一键使用微信昵称）"
            maxlength="20"
            @blur="onNicknameBlur"
            @input="onNicknameInput"
          />
          <text class="material-symbols-outlined input-suffix">edit</text>
        </view>
        <!-- #endif -->

        <!-- H5 / App 普通输入 -->
        <!-- #ifndef MP-WEIXIN -->
        <view class="input-wrapper">
          <input
            type="text"
            class="zen-input"
            v-model="form.nickname"
            placeholder="请输入昵称"
            maxlength="20"
          />
          <text class="material-symbols-outlined input-suffix">edit</text>
        </view>
        <!-- #endif -->
      </view>

      <!-- ── 手机号绑定区域 ── -->
      <view class="section-card">
        <view class="section-title">手机号</view>

        <!-- 已绑定手机号 -->
        <view v-if="userStore.userInfo?.phone" class="bound-phone-row">
          <text class="bound-phone">{{ maskPhone(userStore.userInfo.phone) }}</text>
          <text class="bound-tag">已绑定</text>
        </view>

        <!-- 未绑定：展示绑定表单 -->
        <view v-else class="phone-bind-form">
          <view class="input-wrapper">
            <text class="material-symbols-outlined input-prefix">phone_iphone</text>
            <input
              type="number"
              class="zen-input"
              v-model="phoneForm.phone"
              placeholder="请输入手机号"
              maxlength="11"
            />
          </view>
          <view class="input-line" />

          <view class="input-wrapper sms-row">
            <text class="material-symbols-outlined input-prefix">verified_user</text>
            <input
              type="number"
              class="zen-input"
              v-model="phoneForm.code"
              placeholder="请输入验证码"
              maxlength="6"
            />
            <text
              class="code-btn"
              :class="{ disabled: countdown > 0 }"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}秒` : '获取验证码' }}
            </text>
          </view>
          <view class="input-line" />
        </view>
      </view>

      <!-- ── 保存按钮 ── -->
      <button
        class="save-btn"
        :class="{ loading: isSaving }"
        :disabled="isSaving"
        @click="handleSave"
      >
        <text v-if="!isSaving">保存资料</text>
        <text v-else>保存中...</text>
      </button>

    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useUserStore } from '@/store/useUserStore'
import { baseURL } from '@/utils/request'

const userStore = useUserStore()

// ── 默认头像 ──────────────────────────────────────────────────
const defaultAvatar = '/static/logo.png'

// ── 表单状态 ──────────────────────────────────────────────────
const form = reactive({
  nickname: userStore.userInfo?.nickname || '',
  avatar_url: userStore.userInfo?.avatar_url || '',
})

const phoneForm = reactive({
  phone: '',
  code: '',
})

const isSaving = ref(false)
const isUploadingAvatar = ref(false)  // 头像上传中状态
const countdown = ref(0)

// ── 头像处理 ──────────────────────────────────────────────────

/**
 * 将临时文件路径上传到服务器，返回可持久访问的 URL
 *
 * 微信临时路径（http://tmp/... 或 wxfile://...）只在本地有效，
 * 必须上传到服务器才能跨设备、跨会话访问。
 */
async function uploadAvatarFile(tempFilePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.uploadFile({
      url: `${baseURL}/api/upload/avatar`,
      filePath: tempFilePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${token}`,
      },
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data)
            if (data.url) {
              console.log('✅ [profile] 头像上传成功:', data.url)
              resolve(data.url)
            } else {
              reject(new Error('上传响应缺少 url 字段'))
            }
          } catch (e) {
            reject(new Error('解析上传响应失败'))
          }
        } else {
          reject(new Error(`上传失败，状态码: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络上传失败'))
      },
    })
  })
}

/**
 * 微信小程序：用户通过 open-type="chooseAvatar" 选择头像后触发
 *
 * ⚠️ event.detail.avatarUrl 是微信临时路径（http://tmp/...），
 *    只在本地有效，无法直接存入数据库或跨页面使用。
 *    必须立即上传到服务器，拿到真实 URL 后再存入 form.avatar_url。
 */
async function onChooseAvatar(event: any) {
  const tempPath = event.detail?.avatarUrl
  if (!tempPath) return

  console.log('🔄 [profile] 开始上传微信头像...')
  isUploadingAvatar.value = true

  // 先用临时路径预览，给用户即时反馈
  form.avatar_url = tempPath

  try {
    const cdnUrl = await uploadAvatarFile(tempPath)
    // 上传成功后替换为真实 URL
    form.avatar_url = cdnUrl
    uni.showToast({ title: '头像已更新', icon: 'success', duration: 1500 })
  } catch (err: any) {
    console.error('❌ [profile] 头像上传失败:', err.message)
    // 上传失败：恢复为原头像，不保留临时路径
    form.avatar_url = userStore.userInfo?.avatar_url || ''
    uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
  } finally {
    isUploadingAvatar.value = false
  }
}

/**
 * H5 / App 降级方案：使用 uni.chooseImage
 */
async function onChooseAvatarFallback() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempPath = res.tempFilePaths[0]
      if (!tempPath) return

      isUploadingAvatar.value = true
      form.avatar_url = tempPath  // 先预览

      try {
        const cdnUrl = await uploadAvatarFile(tempPath)
        form.avatar_url = cdnUrl
        uni.showToast({ title: '头像已更新', icon: 'success', duration: 1500 })
      } catch (err: any) {
        form.avatar_url = userStore.userInfo?.avatar_url || ''
        uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
      } finally {
        isUploadingAvatar.value = false
      }
    },
    fail: (err) => {
      console.warn('⚠️ [profile] 选择头像失败:', err)
    },
  })
}

/** 头像加载失败降级 */
function onAvatarError() {
  form.avatar_url = defaultAvatar
}

// ── 昵称处理 ──────────────────────────────────────────────────

/**
 * 微信小程序：type="nickname" 输入框的 blur 事件
 * 用户从微信昵称面板选择后，值会在 blur 时写入 event.detail.value
 */
function onNicknameBlur(event: any) {
  const val = event.detail?.value
  if (val !== undefined) {
    form.nickname = val
    console.log('✅ [profile] 昵称已更新（blur）:', val)
  }
}

/**
 * 普通 input 事件（用户手动输入时同步）
 */
function onNicknameInput(event: any) {
  const val = event.detail?.value
  if (val !== undefined) {
    form.nickname = val
  }
}

// ── 手机号绑定 ────────────────────────────────────────────────

/** 手机号脱敏显示：138****8888 */
function maskPhone(phone: string): string {
  if (!phone || phone.length < 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/** 发送短信验证码 */
async function handleSendCode() {
  if (countdown.value > 0) return

  const phone = phoneForm.phone
  if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }

  try {
    await userStore.sendVerificationCode(phone)
    // 开始 60 秒倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (e) {
    // 错误 Toast 已在 store 内弹出
  }
}

// ── 保存资料 ──────────────────────────────────────────────────

/**
 * 提交资料更新
 *
 * 构造 payload 时只传有变化的字段，避免覆盖未修改的数据。
 * 绑定手机号时需要同时传 phone + sms_code。
 */
async function handleSave() {
  isSaving.value = true

  try {
    // 构造 payload（只传有值的字段）
    const payload: Record<string, string> = {}

    if (form.nickname && form.nickname !== userStore.userInfo?.nickname) {
      payload.nickname = form.nickname
    }

    if (form.avatar_url && form.avatar_url !== userStore.userInfo?.avatar_url) {
      payload.avatar_url = form.avatar_url
    }

    // 绑定手机号（需要验证码）
    if (phoneForm.phone && phoneForm.code) {
      if (!/^1[3-9]\d{9}$/.test(phoneForm.phone)) {
        uni.showToast({ title: '手机号格式不正确', icon: 'none' })
        return
      }
      if (phoneForm.code.length !== 6) {
        uni.showToast({ title: '请输入6位验证码', icon: 'none' })
        return
      }
      payload.phone = phoneForm.phone
      payload.sms_code = phoneForm.code
    }

    if (Object.keys(payload).length === 0) {
      uni.showToast({ title: '没有需要更新的内容', icon: 'none' })
      return
    }

    // 调用 Store 提交（内部已处理 Toast 和 Store 更新）
    await userStore.updateProfile(payload)

    // 清空手机号表单
    phoneForm.phone = ''
    phoneForm.code = ''

    // 延迟返回上一页
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e) {
    // 错误 Toast 已在 store 内弹出
  } finally {
    isSaving.value = false
  }
}
</script>

<style lang="scss" scoped>
page {
  background-color: #F9F6F1;
  background-image: url("/static/handmade-paper.png");
}

.page-container {
  min-height: 100vh;
}

.main-content {
  padding: 32rpx 40rpx 120rpx;
}

// ── 卡片区块 ──────────────────────────────────────────────────
.section-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20rpx);
  border-radius: 24rpx;
  border: 1rpx solid rgba(212, 175, 55, 0.15);
  padding: 40rpx;
  margin-bottom: 32rpx;
}

.section-title {
  font-size: 24rpx;
  color: rgba(0, 0, 0, 0.4);
  letter-spacing: 0.1em;
  margin-bottom: 28rpx;
}

// ── 头像区域 ──────────────────────────────────────────────────
.avatar-row {
  display: flex;
  align-items: center;
  gap: 40rpx;
}

.avatar-preview {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  border: 2rpx solid rgba(212, 175, 55, 0.3);
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.change-avatar-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 36rpx;
  background: rgba(178, 58, 52, 0.06);
  border: 1rpx solid rgba(178, 58, 52, 0.2);
  border-radius: 48rpx;
  line-height: normal;

  // 重置 button 默认样式
  &::after { border: none; }

  &.uploading {
    opacity: 0.6;
  }
}

.btn-icon {
  font-size: 36rpx;
  color: #B23A34;
}

.btn-text {
  font-size: 28rpx;
  color: #B23A34;
}

// ── 输入框 ────────────────────────────────────────────────────
.input-wrapper {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 0;
}

.input-prefix {
  font-size: 40rpx;
  color: rgba(178, 58, 52, 0.5);
  flex-shrink: 0;
}

.input-suffix {
  font-size: 36rpx;
  color: rgba(0, 0, 0, 0.25);
  flex-shrink: 0;
}

.zen-input {
  flex: 1;
  font-size: 32rpx;
  color: #1A1A1A;
  background: transparent;
  border: none;
  outline: none;
  min-height: 60rpx;
}

.input-line {
  height: 1rpx;
  background: rgba(212, 175, 55, 0.2);
  margin: 4rpx 0 16rpx;
}

// ── 手机号绑定 ────────────────────────────────────────────────
.bound-phone-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.bound-phone {
  font-size: 32rpx;
  color: #1A1A1A;
  letter-spacing: 0.05em;
}

.bound-tag {
  font-size: 22rpx;
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.phone-bind-form {
  display: flex;
  flex-direction: column;
}

.sms-row {
  margin-top: 8rpx;
}

.code-btn {
  flex-shrink: 0;
  font-size: 24rpx;
  color: #B23A34;
  padding: 8rpx 20rpx;
  border-radius: 8rpx;
  background: rgba(178, 58, 52, 0.08);
  white-space: nowrap;

  &.disabled {
    color: rgba(0, 0, 0, 0.3);
    background: rgba(0, 0, 0, 0.05);
  }
}

// ── 保存按钮 ──────────────────────────────────────────────────
.save-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #B23A34 0%, #8B2E29 100%);
  border-radius: 48rpx;
  border: none;
  font-size: 32rpx;
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 4rpx;
  box-shadow: 0 8rpx 24rpx rgba(178, 58, 52, 0.4);
  margin-top: 20rpx;

  &::after { border: none; }

  &:active { opacity: 0.9; }

  &.loading { opacity: 0.7; }
}
</style>
