<template>
  <div class="page-container">
    <div class="profile-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息和账户设置</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <!-- 头像和基本信息 -->
        <div class="card-container">
          <div class="avatar-section">
            <el-avatar :size="120" :src="userInfo.avatar" class="avatar">
              <el-icon size="40"><User /></el-icon>
            </el-avatar>
            <el-upload
              action="#"
              :before-upload="handleAvatarUpload"
              :show-file-list="false"
            >
              <el-button type="primary" size="small" style="margin-top: 16px;">
                <el-icon><Upload /></el-icon>
                更换头像
              </el-button>
            </el-upload>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.totalOrders }}</div>
              <div class="stat-label">总订单数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.completedOrders }}</div>
              <div class="stat-label">已完成</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.totalVehicles }}</div>
              <div class="stat-label">车辆数量</div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="16">
        <div class="card-container">
          <el-tabs v-model="activeTab">
            <!-- 基本信息 -->
            <el-tab-pane label="基本信息" name="basic">
              <el-form :model="basicForm" :rules="basicRules" ref="basicFormRef" label-width="100px">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="basicForm.username" disabled />
                </el-form-item>
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="basicForm.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                  <el-radio-group v-model="basicForm.gender">
                    <el-radio label="male">男</el-radio>
                    <el-radio label="female">女</el-radio>
                    <el-radio label="other">其他</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="出生日期" prop="birth_date">
                  <el-date-picker
                    v-model="basicForm.birth_date"
                    type="date"
                    placeholder="选择出生日期"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item label="地址" prop="address">
                  <el-input 
                    v-model="basicForm.address" 
                    type="textarea" 
                    :rows="3" 
                    placeholder="请输入详细地址" 
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="basicSubmitting" @click="handleBasicSubmit">
                    保存信息
                  </el-button>
                  <el-button @click="resetBasicForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 修改密码 -->
            <el-tab-pane label="修改密码" name="password">
              <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input 
                    v-model="passwordForm.oldPassword" 
                    type="password" 
                    show-password 
                    placeholder="请输入当前密码" 
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="newPassword">
                  <el-input 
                    v-model="passwordForm.newPassword" 
                    type="password" 
                    show-password 
                    placeholder="请输入新密码" 
                  />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input 
                    v-model="passwordForm.confirmPassword" 
                    type="password" 
                    show-password 
                    placeholder="请再次输入新密码" 
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="passwordSubmitting" @click="handlePasswordSubmit">
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 账户设置 -->
            <el-tab-pane label="账户设置" name="settings">
              <el-form :model="settingsForm" label-width="150px">
                <el-form-item label="邮件通知">
                  <el-switch 
                    v-model="settingsForm.emailNotification" 
                    active-text="开启" 
                    inactive-text="关闭" 
                  />
                  <div class="form-tip">接收订单状态更新等重要通知</div>
                </el-form-item>
                <el-form-item label="短信通知">
                  <el-switch 
                    v-model="settingsForm.smsNotification" 
                    active-text="开启" 
                    inactive-text="关闭" 
                  />
                  <div class="form-tip">接收订单状态变更短信提醒</div>
                </el-form-item>
                <el-form-item label="推广信息">
                  <el-switch 
                    v-model="settingsForm.promotionalEmails" 
                    active-text="接收" 
                    inactive-text="不接收" 
                  />
                  <div class="form-tip">接收优惠活动和服务推荐</div>
                </el-form-item>
                <el-form-item label="隐私设置">
                  <el-checkbox-group v-model="settingsForm.privacySettings">
                    <el-checkbox label="hidePhone">隐藏手机号</el-checkbox>
                    <el-checkbox label="hideEmail">隐藏邮箱</el-checkbox>
                    <el-checkbox label="hideAddress">隐藏地址</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="settingsSubmitting" @click="handleSettingsSubmit">
                    保存设置
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 登录记录 -->
            <el-tab-pane label="登录记录" name="logs">
              <el-table v-loading="logsLoading" :data="loginLogs" stripe>
                <el-table-column prop="login_time" label="登录时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.login_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="ip_address" label="IP地址" width="150" />
                <el-table-column prop="device" label="设备" width="200" />
                <el-table-column prop="location" label="地理位置" width="150" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                      {{ row.status === 'success' ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
              
              <div style="margin-top: 20px; text-align: center;">
                <el-button @click="fetchLoginLogs">
                  <el-icon><Refresh /></el-icon>
                  刷新记录
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const activeTab = ref('basic')
const basicSubmitting = ref(false)
const passwordSubmitting = ref(false)
const settingsSubmitting = ref(false)
const logsLoading = ref(false)

const basicFormRef = ref()
const passwordFormRef = ref()

const userInfo = computed(() => authStore.userInfo || {})

const userStats = reactive({
  totalOrders: 0,
  completedOrders: 0,
  totalVehicles: 0
})

const basicForm = reactive({
  username: '',
  name: '',
  phone: '',
  email: '',
  gender: '',
  birth_date: '',
  address: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const settingsForm = reactive({
  emailNotification: true,
  smsNotification: true,
  promotionalEmails: false,
  privacySettings: []
})

const loginLogs = ref([])

const basicRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 获取用户统计信息
const fetchUserStats = async () => {
  try {
    const response = await request.get('/users/stats')
    Object.assign(userStats, response)
  } catch (error) {
    console.error('获取用户统计失败:', error)
    // 使用模拟数据
    Object.assign(userStats, {
      totalOrders: 12,
      completedOrders: 10,
      totalVehicles: 2
    })
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await request.get('/users/profile')
    Object.assign(basicForm, response)
    Object.assign(settingsForm, response.settings || {})
  } catch (error) {
    console.error('获取用户信息失败:', error)
    // 使用当前认证信息
    Object.assign(basicForm, userInfo.value)
  }
}

// 获取登录记录
const fetchLoginLogs = async () => {
  logsLoading.value = true
  try {
    const response = await request.get('/users/login-logs')
    loginLogs.value = response || []
  } catch (error) {
    console.error('获取登录记录失败:', error)
    // 使用模拟数据
    loginLogs.value = [
      {
        login_time: new Date().toISOString(),
        ip_address: '192.168.1.100',
        device: 'Chrome 120 / macOS',
        location: '北京市',
        status: 'success'
      }
    ]
  } finally {
    logsLoading.value = false
  }
}

// 处理头像上传
const handleAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 这里应该上传到服务器
  ElMessage.success('头像上传功能开发中')
  return false
}

// 提交基本信息
const handleBasicSubmit = async () => {
  const valid = await basicFormRef.value.validate()
  if (!valid) return

  basicSubmitting.value = true
  try {
    await request.put('/users/profile', basicForm)
    ElMessage.success('信息更新成功')
    authStore.updateUserInfo(basicForm)
  } catch (error) {
    console.error('更新信息失败:', error)
  } finally {
    basicSubmitting.value = false
  }
}

// 重置基本信息表单
const resetBasicForm = () => {
  fetchUserInfo()
}

// 提交密码修改
const handlePasswordSubmit = async () => {
  const valid = await passwordFormRef.value.validate()
  if (!valid) return

  passwordSubmitting.value = true
  try {
    await request.put('/users/change-password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    ElMessage.success('密码修改成功')
    resetPasswordForm()
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordSubmitting.value = false
  }
}

// 重置密码表单
const resetPasswordForm = () => {
  Object.assign(passwordForm, {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
}

// 提交设置
const handleSettingsSubmit = async () => {
  settingsSubmitting.value = true
  try {
    await request.put('/users/settings', settingsForm)
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
  } finally {
    settingsSubmitting.value = false
  }
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  fetchUserInfo()
  fetchUserStats()
  fetchLoginLogs()
})
</script>

<style lang="scss" scoped>
.profile-header {
  margin-bottom: 24px;

  h1 {
    margin: 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;
  }

  p {
    margin: 8px 0 0 0;
    color: #606266;
    font-size: 14px;
  }
}

.avatar-section {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;

  .avatar {
    display: block;
    margin: 0 auto;
  }
}

.user-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #1890ff;
      margin-bottom: 4px;
    }

    .stat-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .profile-header h1 {
    font-size: 20px;
  }

  .user-stats {
    .stat-item .stat-value {
      font-size: 20px;
    }
  }
}
</style> 