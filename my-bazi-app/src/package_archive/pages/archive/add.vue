<template>
  <view class="page-container">
    <ZenBg />
    <ZenHeader :title="isEditMode ? '编辑档案' : '新建档案'" :show-back="true" />

    <main class="main-content">
      <view class="form-card">
        <!-- 姓名 -->
        <view class="form-item">
          <text class="form-label">姓名</text>
          <view class="input-wrapper">
            <input 
              class="form-input" 
              v-model="formData.name"
              placeholder="请输入姓名"
              placeholder-class="placeholder-style"
              maxlength="20"
            />
          </view>
        </view>

        <!-- 性别 -->
        <view class="form-item">
          <text class="form-label">性别</text>
          <view class="gender-group">
            <view 
              class="gender-item" 
              :class="{ active: formData.gender === 1 }"
              @click="formData.gender = 1"
              hover-class="gender-hover"
            >
              <text class="gender-text">乾造 (男)</text>
            </view>
            <view 
              class="gender-item" 
              :class="{ active: formData.gender === 0 }"
              @click="formData.gender = 0"
              hover-class="gender-hover"
            >
              <text class="gender-text">坤造 (女)</text>
            </view>
          </view>
        </view>

        <!-- 出生日期 -->
        <view class="form-item">
          <!-- 标签行：左侧文字 + 右侧历法切换 -->
          <view class="date-label-row">
            <text class="form-label" style="margin-bottom: 0;">出生日期</text>
            <view class="calendar-toggle">
              <view
                class="toggle-option"
                :class="{ 'toggle-active': !formData.isLunar }"
                @click="formData.isLunar = false"
              >
                <text class="toggle-text">公历</text>
              </view>
              <view
                class="toggle-option"
                :class="{ 'toggle-active': formData.isLunar }"
                @click="formData.isLunar = true"
              >
                <text class="toggle-text">农历</text>
              </view>
            </view>
          </view>
          <picker 
            mode="date" 
            :value="formData.birthDate"
            :end="todayDate"
            @change="onDateChange"
          >
            <view class="picker-wrapper">
              <text class="picker-text">
                {{ formData.birthDate }}
              </text>
              <text class="material-symbols-outlined picker-icon">calendar_today</text>
            </view>
          </picker>
        </view>

        <!-- 出生时间 -->
        <view class="form-item">
          <text class="form-label">出生时间</text>
          <picker 
            mode="time" 
            :value="formData.birthTime"
            @change="onTimeChange"
          >
            <view class="picker-wrapper">
              <text class="picker-text" :class="{ placeholder: !formData.birthTime }">
                {{ formData.birthTime || '请选择出生时间' }}
              </text>
              <text class="material-symbols-outlined picker-icon">schedule</text>
            </view>
          </picker>
          <view class="time-hint">
            <text class="hint-text">💡 如不知道具体时辰，可选择 12:00</text>
          </view>
        </view>

        <!-- 标签 -->
        <view class="form-item">
          <text class="form-label">标签</text>

          <!-- 层一：已选标签展示 -->
          <view v-if="formData.tags.length > 0" class="selected-tags">
            <view
              v-for="(tag, index) in formData.tags"
              :key="tag"
              class="selected-tag"
            >
              <text class="selected-tag-text">{{ tag }}</text>
              <text class="selected-tag-remove" @click="removeTag(index)">×</text>
            </view>
          </view>

          <!-- 层二：自定义输入 -->
          <view class="tag-input-row">
            <text class="tag-input-label">添加标签</text>
            <input
              class="tag-input"
              v-model="newTag"
              placeholder="自定义标签"
              placeholder-class="tag-placeholder"
              maxlength="10"
              confirm-type="done"
              @confirm="addTag"
            />
            <text class="tag-add-btn" @click="addTag">+</text>
          </view>

          <!-- 层三：预设快捷标签 -->
          <view class="preset-tags">
            <view
              v-for="tag in presetTags"
              :key="tag"
              class="preset-tag"
              :class="{ 'preset-tag-active': formData.tags.includes(tag) }"
              hover-class="preset-tag-hover"
              @click="addPresetTag(tag)"
            >
              <text class="preset-tag-text">{{ tag }}</text>
            </view>
          </view>
        </view>

        <!-- 设为默认 -->
        <view class="form-item">
          <view class="default-row" @click="formData.isDefault = !formData.isDefault">
            <view class="default-left">
              <text class="form-label" style="margin-bottom: 0;">设为默认档案</text>
              <text class="default-hint">默认档案将在「我的」页面优先展示</text>
            </view>
            <!-- Switch 样式开关 -->
            <view class="switch-track" :class="{ 'switch-on': formData.isDefault }">
              <view class="switch-thumb" :class="{ 'switch-thumb-on': formData.isDefault }"></view>
            </view>
          </view>
        </view>

        <!-- 提交按钮 -->
        <view class="button-container">
          <button 
            class="save-button" 
            :class="{ loading: isLoading }"
            hover-class="button-hover"
            :disabled="isLoading"
            @click="handleSubmit"
          >
            <text v-if="!isLoading" class="button-text">{{ isEditMode ? '保存修改' : '确认添加' }}</text>
            <text v-else class="button-text">保存中...</text>
          </button>
        </view>

        <!-- 删除按钮（仅编辑模式） -->
        <view v-if="isEditMode" class="delete-container">
          <button 
            class="delete-button" 
            hover-class="delete-hover"
            @click="handleDelete"
          >
            <text class="material-symbols-outlined delete-icon">delete</text>
            <text class="delete-text">删除此档案</text>
          </button>
        </view>
      </view>
    </main>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import ZenBg from '@/components/ZenBg/ZenBg.vue'
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useArchiveStore } from '@/store/useArchiveStore'

// 强制隐藏原生 TabBar
onMounted(() => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [archive/add] 原生 TabBar 已隐藏'),
    fail: () => {}
  })
})

// 引入 Store
const archiveStore = useArchiveStore()

// 页面状态
const isEditMode = ref(false)
const editArchiveId = ref('')
const isLoading = ref(false)

// 今天的日期（用于限制日期选择器）
const todayDate = ref('')

// 预设标签
const presetTags = ['本人', '伴侣', '子女', '父母', '朋友', '客户', '其他']

// 自定义标签输入
const newTag = ref('')

// 表单数据
const formData = reactive({
  name: '',
  gender: 1 as 0 | 1,
  birthDate: '2000-01-01',
  birthTime: '12:00',
  isLunar: false,
  tags: [] as string[],
  isDefault: false
})

// ==================== 标签方法 ====================

/** 添加自定义标签（回车或点击+） */
const addTag = () => {
  const val = newTag.value.trim()
  if (!val) return
  if (formData.tags.includes(val)) {
    newTag.value = ''
    return
  }
  if (formData.tags.length >= 8) {
    uni.showToast({ title: '最多添加 8 个标签', icon: 'none' })
    return
  }
  formData.tags.push(val)
  newTag.value = ''
}

/** 点击预设标签：已有则移除，没有则添加 */
const addPresetTag = (tag: string) => {
  const idx = formData.tags.indexOf(tag)
  if (idx !== -1) {
    formData.tags.splice(idx, 1)
  } else {
    if (formData.tags.length >= 8) {
      uni.showToast({ title: '最多添加 8 个标签', icon: 'none' })
      return
    }
    formData.tags.push(tag)
  }
}

/** 删除已选标签 */
const removeTag = (index: number) => {
  formData.tags.splice(index, 1)
}

// ==================== 页面初始化 ====================
onMounted(() => {
  const today = new Date()
  todayDate.value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}

  console.log('📋 [archive/add] 页面参数:', options)

  if (options.id) {
    isEditMode.value = true
    editArchiveId.value = options.id

    const archive = archiveStore.archives.find(item => item.id === options.id)

    if (archive) {
      console.log('✅ [archive/add] 找到档案，回显数据:', archive)
      formData.name = archive.name
      formData.gender = archive.gender
      formData.birthDate = archive.birthDate
      formData.birthTime = archive.birthTime
      formData.isLunar = archive.isLunar ?? false
      // 兼容旧数据：tags 可能不存在
      formData.tags = Array.isArray(archive.tags) ? [...archive.tags] : []
      formData.isDefault = archive.isDefault
    } else {
      console.error('❌ [archive/add] 档案不存在:', options.id)
      uni.showToast({ title: '档案不存在', icon: 'error', duration: 2000 })
      setTimeout(() => uni.navigateBack(), 2000)
    }
  } else {
    console.log('📝 [archive/add] 新建模式')
    isEditMode.value = false
    if (archiveStore.archives.length === 0) {
      formData.isDefault = true
    }
  }
})

// ==================== 表单操作 ====================

const onDateChange = (e: any) => {
  formData.birthDate = e.detail.value
}

const onTimeChange = (e: any) => {
  formData.birthTime = e.detail.value
}

const validateForm = (): boolean => {
  if (!formData.name.trim()) {
    uni.showToast({ title: '请输入姓名', icon: 'none', duration: 1500 })
    return false
  }
  if (!formData.birthDate) {
    uni.showToast({ title: '请选择出生日期', icon: 'none', duration: 1500 })
    return false
  }
  if (!formData.birthTime) {
    uni.showToast({ title: '请选择出生时间', icon: 'none', duration: 1500 })
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  isLoading.value = true

  try {
    const payload = {
      name: formData.name.trim(),
      gender: formData.gender,
      birthDate: formData.birthDate,
      birthTime: formData.birthTime,
      isLunar: formData.isLunar,
      tags: [...formData.tags],
      isDefault: formData.isDefault
    }

    if (isEditMode.value) {
      console.log('📝 [archive/add] 更新档案:', editArchiveId.value)
      await archiveStore.updateArchive(editArchiveId.value, payload)
      archiveStore.currentArchiveId = editArchiveId.value
      console.log('✅ [archive/add] 档案更新成功')
    } else {
      console.log('📝 [archive/add] 添加档案')
      const newArchive = await archiveStore.addArchive(payload)
      if (newArchive) {
        archiveStore.currentArchiveId = newArchive.id
        console.log('✅ [archive/add] 档案添加成功:', newArchive.id)
      }
    }

    // 保存成功后直接返回，无需确认提示
    // 上一页的 onShow 会自动刷新数据，用户立即感知到变更
    uni.navigateBack()
  } catch (error) {
    console.error('❌ [archive/add] 保存失败:', error)
    uni.showToast({ title: '保存失败，请重试', icon: 'none', duration: 1500 })
  } finally {
    isLoading.value = false
  }
}

const handleDelete = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个档案吗？删除后无法恢复。',
    confirmText: '删除',
    confirmColor: '#B22222',
    cancelText: '取消',
    success: async (res) => {
      if (res.confirm) {
        const success = await archiveStore.deleteArchive(editArchiveId.value)
        if (success) setTimeout(() => uni.navigateBack(), 500)
      }
    }
  })
}
</script>

<style scoped>
/* 页面样式 */
/* 全局变量 */
.page-container {
  --zen-bg: #F5F5F5;
  --zen-white: #FFFFFF;
  --zen-ink: #333333;
  --zen-gray: #666666;
  --zen-light-gray: #999999;
  --zen-border: #E0E0E0;
  --zen-cinnabar: #B23A34;
  --zen-cinnabar-light: #FFF5F5;
  
  min-height: 100vh;
  background-color: var(--zen-bg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: var(--zen-ink);
}

/* 主内容区 */
.main-content {
  padding: 32rpx;
  padding-bottom: 200rpx;
}

/* 表单卡片 */
.form-card {
  background-color: var(--zen-white);
  border-radius: 24rpx;
  padding: 48rpx 32rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

/* 表单项 */
.form-item {
  margin-bottom: 48rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 28rpx;
  font-weight: 400;
  color: var(--zen-ink);
  margin-bottom: 24rpx;
}

/* 输入框 */
.input-wrapper {
  position: relative;
  background: var(--zen-white);
  border-radius: 12rpx;
  border: 1px solid var(--zen-border);
  transition: all 0.3s ease;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: var(--zen-ink);
  background: transparent;
}

.placeholder-style {
  color: var(--zen-light-gray);
  font-weight: 300;
}

/* 性别选择 */
.gender-group {
  display: flex;
  gap: 24rpx;
}

.gender-item {
  flex: 1;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--zen-white);
  border: 1px solid var(--zen-border);
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.gender-item.active {
  background: var(--zen-cinnabar-light);
  border-color: var(--zen-cinnabar);
}

.gender-hover {
  opacity: 0.8;
}

.gender-text {
  font-size: 28rpx;
  color: var(--zen-gray);
}

.gender-item.active .gender-text {
  color: var(--zen-cinnabar);
  font-weight: 500;
}

/* 出生日期标签行（含历法切换） */
.date-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

/* 公历/农历胶囊切换 */
.calendar-toggle {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 32rpx;
  padding: 4rpx;
  gap: 0;
}

.toggle-option {
  padding: 8rpx 24rpx;
  border-radius: 28rpx;
  transition: all 0.2s ease;
}

.toggle-active {
  background: var(--zen-cinnabar);
}

.toggle-text {
  font-size: 22rpx;
  color: var(--zen-light-gray);
  letter-spacing: 1rpx;
}

.toggle-active .toggle-text {
  color: #FFFFFF;
  font-weight: 500;
}

/* 选择器 */
.picker-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 24rpx;
  background: var(--zen-white);
  border: 1px solid var(--zen-border);
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.picker-text {
  font-size: 28rpx;
  color: var(--zen-ink);
}

.picker-text.placeholder {
  color: var(--zen-light-gray);
  font-weight: 300;
}

.picker-icon {
  font-size: 40rpx;
  color: var(--zen-cinnabar);
  font-weight: 200;
}

/* 时间提示 */
.time-hint {
  margin-top: 16rpx;
  padding-left: 8rpx;
}

.hint-text {
  font-size: 24rpx;
  color: var(--zen-light-gray);
  line-height: 1.6;
}

/* ==================== 标签区域 ==================== */

/* 层一：已选标签 */
.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.selected-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  background: rgba(178, 58, 52, 0.12);
  border: 1px solid rgba(178, 58, 52, 0.5);
  border-radius: 32rpx;
}

.selected-tag-text {
  font-size: 24rpx;
  color: var(--zen-cinnabar);
  font-weight: 500;
}

.selected-tag-remove {
  font-size: 28rpx;
  color: var(--zen-cinnabar);
  line-height: 1;
  opacity: 0.7;
  padding: 0 4rpx;
}

/* 层二：自定义输入行 */
.tag-input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 24rpx;
}

.tag-input-label {
  font-size: 26rpx;
  color: var(--zen-light-gray);
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-input {
  flex: 1;
  height: 60rpx;
  font-size: 26rpx;
  color: var(--zen-ink);
  background: transparent;
  padding: 0 8rpx;
}

.tag-add-btn {
  font-size: 40rpx;
  color: var(--zen-cinnabar);
  line-height: 1;
  padding: 0 8rpx;
  opacity: 0.8;
  flex-shrink: 0;
}

/* 层三：预设快捷标签 */
.preset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.preset-tag {
  padding: 10rpx 24rpx;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 32rpx;
  transition: all 0.2s ease;
}

.preset-tag-active {
  border-color: rgba(178, 58, 52, 0.4);
  background: rgba(178, 58, 52, 0.06);
}

.preset-tag-hover {
  opacity: 0.6;
}

.preset-tag-text {
  font-size: 22rpx;
  color: var(--zen-light-gray);
}

.preset-tag-active .preset-tag-text {
  color: var(--zen-cinnabar);
}

/* 默认档案开关 */
.default-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
}

.default-left {
  flex: 1;
}

.default-hint {
  display: block;
  font-size: 24rpx;
  color: var(--zen-light-gray);
  margin-top: 8rpx;
}

/* Switch 轨道 */
.switch-track {
  width: 96rpx;
  height: 52rpx;
  border-radius: 26rpx;
  background: var(--zen-border);
  position: relative;
  transition: background 0.25s ease;
  flex-shrink: 0;
}

.switch-track.switch-on {
  background: var(--zen-cinnabar);
}

/* Switch 滑块 */
.switch-thumb {
  position: absolute;
  top: 6rpx;
  left: 6rpx;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.15);
  transition: left 0.25s ease;
}

.switch-thumb.switch-thumb-on {
  left: 50rpx;
}

/* 按钮容器 */
.button-container {
  margin-top: 80rpx;
}

.save-button {
  width: 100%;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--zen-cinnabar);
  border: none;
  border-radius: 48rpx;
  box-shadow: 0 4rpx 16rpx rgba(178, 58, 52, 0.2);
  transition: all 0.3s ease;
}

.save-button.loading {
  opacity: 0.6;
}

.button-hover {
  transform: scale(0.98);
  box-shadow: 0 2rpx 12rpx rgba(178, 58, 52, 0.15);
}

.button-text {
  font-size: 32rpx;
  font-weight: 500;
  color: var(--zen-white);
  letter-spacing: 2rpx;
}

/* 删除按钮 */
.delete-container {
  margin-top: 32rpx;
  display: flex;
  justify-content: center;
}

.delete-button {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 40rpx;
  background: transparent;
  border: 1px solid rgba(178, 58, 52, 0.3);
  border-radius: 48rpx;
  transition: all 0.3s ease;
}

.delete-hover {
  background: rgba(178, 58, 52, 0.05);
}

.delete-icon {
  font-size: 36rpx;
  color: var(--zen-cinnabar);
  font-weight: 200;
}

.delete-text {
  font-size: 26rpx;
  color: var(--zen-cinnabar);
}
</style>
