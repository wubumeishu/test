<template>
  <view class="page-container">
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
          <text class="form-label">出生日期</text>
          <picker 
            mode="date" 
            :value="formData.birthDate"
            :end="todayDate"
            @change="onDateChange"
          >
            <view class="picker-wrapper">
              <text class="picker-text" :class="{ placeholder: !formData.birthDate }">
                {{ formData.birthDate || '请选择出生日期' }}
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

        <!-- 关系标签 -->
        <view class="form-item">
          <text class="form-label">关系</text>
          <view class="tag-group">
            <view 
              v-for="tag in relationTags" 
              :key="tag"
              class="tag-item" 
              :class="{ active: formData.relation === tag }"
              @click="formData.relation = tag"
              hover-class="tag-hover"
            >
              <text class="tag-text">{{ tag }}</text>
            </view>
          </view>
        </view>

        <!-- 设为默认 -->
        <view class="form-item">
          <view class="default-row" @click="formData.isDefault = !formData.isDefault">
            <view class="default-left">
              <text class="form-label">设为默认档案</text>
              <text class="default-hint">默认档案将优先显示</text>
            </view>
            <view class="checkbox" :class="{ checked: formData.isDefault }">
              <text v-if="formData.isDefault" class="material-symbols-outlined check-icon">check</text>
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
import ZenHeader from '@/components/ZenHeader/ZenHeader.vue'
import { useArchiveStore } from '@/store/useArchiveStore'
import type { Archive } from '@/store/useArchiveStore'

// 强制隐藏原生 TabBar
onMounted(() => {
  uni.hideTabBar({
    animation: false,
    success: () => console.log('✅ [archive/add] 原生 TabBar 已隐藏'),
    fail: () => console.log('ℹ️ [archive/add] 当前页面无 TabBar')
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

// 关系标签预设
const relationTags = ['本人', '伴侣', '子女', '父母', '朋友', '其他']

// 表单数据
const formData = reactive({
  name: '',
  gender: 1 as 0 | 1,
  birthDate: '',
  birthTime: '',
  relation: '本人',
  isDefault: false
})

// 页面加载
onMounted(() => {
  // 设置今天的日期
  const today = new Date()
  todayDate.value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}
  
  console.log('📋 [archive/add] 页面参数:', options)
  
  // 判断是否为编辑模式
  if (options.id) {
    isEditMode.value = true
    editArchiveId.value = options.id
    
    // 从 Store 中找出对应档案并回显数据
    const archive = archiveStore.archives.find(item => item.id === options.id)
    
    if (archive) {
      console.log('✅ [archive/add] 找到档案，回显数据:', archive)
      
      formData.name = archive.name
      formData.gender = archive.gender
      formData.birthDate = archive.birthDate
      formData.birthTime = archive.birthTime
      formData.relation = archive.relation || '本人'
      formData.isDefault = archive.isDefault
    } else {
      console.error('❌ [archive/add] 档案不存在:', options.id)
      
      uni.showToast({
        title: '档案不存在',
        icon: 'error',
        duration: 2000
      })
      
      // 返回上一页
      setTimeout(() => {
        uni.navigateBack()
      }, 2000)
    }
  } else {
    console.log('📝 [archive/add] 新建模式')
    isEditMode.value = false
  }
})

// 日期选择器变化
const onDateChange = (e: any) => {
  formData.birthDate = e.detail.value
  console.log('📅 [archive/add] 选择日期:', formData.birthDate)
}

// 时间选择器变化
const onTimeChange = (e: any) => {
  formData.birthTime = e.detail.value
  console.log('⏰ [archive/add] 选择时间:', formData.birthTime)
}

// 表单验证
const validateForm = (): boolean => {
  if (!formData.name.trim()) {
    uni.showToast({
      title: '请输入姓名',
      icon: 'none',
      duration: 1500
    })
    return false
  }

  if (!formData.birthDate) {
    uni.showToast({
      title: '请选择出生日期',
      icon: 'none',
      duration: 1500
    })
    return false
  }

  if (!formData.birthTime) {
    uni.showToast({
      title: '请选择出生时间',
      icon: 'none',
      duration: 1500
    })
    return false
  }

  return true
}

// 提交表单
const handleSubmit = async () => {
  // 表单验证
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    if (isEditMode.value) {
      // 编辑模式：更新档案
      console.log('📝 [archive/add] 更新档案:', editArchiveId.value)
      
      await archiveStore.updateArchive(editArchiveId.value, {
        name: formData.name.trim(),
        gender: formData.gender,
        birthDate: formData.birthDate,
        birthTime: formData.birthTime,
        relation: formData.relation,
        isDefault: formData.isDefault
      })

      // 设置为当前档案
      archiveStore.currentArchiveId = editArchiveId.value

      console.log('✅ [archive/add] 档案更新成功')
    } else {
      // 新建模式：添加档案
      console.log('📝 [archive/add] 添加档案')
      
      const newArchive = await archiveStore.addArchive({
        name: formData.name.trim(),
        gender: formData.gender,
        birthDate: formData.birthDate,
        birthTime: formData.birthTime,
        relation: formData.relation,
        isDefault: formData.isDefault
      })

      // 设置为当前档案
      if (newArchive) {
        archiveStore.currentArchiveId = newArchive.id
        console.log('✅ [archive/add] 档案添加成功，已设为当前档案:', newArchive.id)
      }
    }

    // 返回上一页
    setTimeout(() => {
      uni.navigateBack()
    }, 500)
  } catch (error) {
    console.error('❌ [archive/add] 保存失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 删除档案
const handleDelete = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个档案吗？删除后无法恢复。',
    confirmText: '删除',
    confirmColor: '#B22222',
    cancelText: '取消',
    success: async (res) => {
      if (res.confirm) {
        console.log('🗑️ [archive/add] 删除档案:', editArchiveId.value)
        
        const success = await archiveStore.deleteArchive(editArchiveId.value)
        
        if (success) {
          console.log('✅ [archive/add] 档案删除成功')
          
          // 返回上一页
          setTimeout(() => {
            uni.navigateBack()
          }, 500)
        }
      }
    }
  })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,200,0,0&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@300;400;500&display=swap');

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

/* 标签组 */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-item {
  padding: 16rpx 32rpx;
  background: var(--zen-white);
  border: 1px solid var(--zen-border);
  border-radius: 24rpx;
  transition: all 0.3s ease;
}

.tag-item.active {
  background: var(--zen-cinnabar-light);
  border-color: var(--zen-cinnabar);
}

.tag-hover {
  opacity: 0.8;
}

.tag-text {
  font-size: 26rpx;
  color: var(--zen-gray);
}

.tag-item.active .tag-text {
  color: var(--zen-cinnabar);
  font-weight: 500;
}

/* 默认档案选项 */
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

.checkbox {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--zen-border);
  border-radius: 8rpx;
  transition: all 0.3s ease;
}

.checkbox.checked {
  background-color: var(--zen-cinnabar);
  border-color: var(--zen-cinnabar);
}

.check-icon {
  font-size: 32rpx;
  color: var(--zen-white);
  font-weight: 500;
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
