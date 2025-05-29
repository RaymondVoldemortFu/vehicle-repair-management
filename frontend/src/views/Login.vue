<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>车辆维修管理系统</h1>
        <p>请选择登录类型</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="用户登录" name="user">
          <el-form
            ref="userFormRef"
            :model="userForm"
            :rules="userRules"
            @submit.prevent="handleUserLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="userForm.username"
                placeholder="请输入用户名"
                size="large"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="userForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                @click="handleUserLogin"
                style="width: 100%"
              >
                用户登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="管理员登录" name="admin">
          <el-form
            ref="adminFormRef"
            :model="adminForm"
            :rules="adminRules"
            @submit.prevent="handleAdminLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="adminForm.username"
                placeholder="请输入管理员用户名"
                size="large"
                prefix-icon="UserFilled"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="adminForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                @click="handleAdminLogin"
                style="width: 100%"
              >
                管理员登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="维修工人登录" name="worker">
          <el-form
            ref="workerFormRef"
            :model="workerForm"
            :rules="workerRules"
            @submit.prevent="handleWorkerLogin"
          >
            <el-form-item prop="employee_id">
              <el-input
                v-model="workerForm.employee_id"
                placeholder="请输入工号"
                size="large"
                prefix-icon="Postcard"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="workerForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                @click="handleWorkerLogin"
                style="width: 100%"
              >
                维修工人登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <el-button type="text" @click="$router.push('/register')">
          还没有账号？立即注册
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('user')
const loading = ref(false)

// 表单引用
const userFormRef = ref()
const adminFormRef = ref()
const workerFormRef = ref()

// 用户登录表单
const userForm = reactive({
  username: '',
  password: ''
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ]
}

// 管理员登录表单
const adminForm = reactive({
  username: '',
  password: ''
})

const adminRules = {
  username: [
    { required: true, message: '请输入管理员用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ]
}

// 维修工人登录表单
const workerForm = reactive({
  employee_id: '',
  password: ''
})

const workerRules = {
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { min: 3, max: 20, message: '工号长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ]
}

// 用户登录
const handleUserLogin = async () => {
  const valid = await userFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginUser(userForm)
    ElMessage.success('登录成功')
    router.push('/user/dashboard')
  } catch (error) {
    console.error('用户登录失败:', error)
  } finally {
    loading.value = false
  }
}

// 管理员登录
const handleAdminLogin = async () => {
  const valid = await adminFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginAdmin(adminForm)
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (error) {
    console.error('管理员登录失败:', error)
  } finally {
    loading.value = false
  }
}

// 维修工人登录
const handleWorkerLogin = async () => {
  const valid = await workerFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginWorker(workerForm)
    ElMessage.success('登录成功')
    router.push('/worker/dashboard')
  } catch (error) {
    console.error('维修工人登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    color: #303133;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  p {
    color: #909399;
    font-size: 14px;
  }
}

.login-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 30px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
  }
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input__inner) {
  height: 48px;
  font-size: 16px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 20px;
  }
}
</style> 