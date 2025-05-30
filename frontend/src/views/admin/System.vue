<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h1>系统管理</h1>
      <p>管理系统配置、管理员账号等</p>
    </div>

    <el-tabs v-model="activeTab" class="system-tabs">
      <!-- 管理员管理 -->
      <el-tab-pane label="管理员管理" name="admins">
        <div class="card-container">
          <div class="toolbar" style="margin-bottom: 20px;">
            <div class="search-form">
              <el-input
                v-model="adminSearch.keyword"
                placeholder="搜索管理员用户名或姓名"
                style="width: 300px"
                clearable
                @keyup.enter="searchAdmins"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button type="primary" @click="searchAdmins">搜索</el-button>
              <el-button @click="resetAdminSearch">重置</el-button>
            </div>
            <div>
              <el-button type="primary" @click="handleAddAdmin">
                <el-icon><Plus /></el-icon>
                添加管理员
              </el-button>
            </div>
          </div>

          <el-table v-loading="adminLoading" :data="adminData" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="getRoleType(row.role)">
                  {{ getRoleText(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '激活' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_login" label="最后登录" width="150">
              <template #default="{ row }">
                {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleEditAdmin(row)">
                  编辑
                </el-button>
                <el-button 
                  :type="row.is_active ? 'danger' : 'success'" 
                  size="small" 
                  @click="handleToggleAdminStatus(row)"
                >
                  {{ row.is_active ? '禁用' : '激活' }}
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteAdmin(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 系统配置 -->
      <el-tab-pane label="系统配置" name="config">
        <div class="card-container">
          <el-form :model="systemConfig" label-width="150px" style="max-width: 600px;">
            <h3>基本配置</h3>
            <el-form-item label="系统名称">
              <el-input v-model="systemConfig.system_name" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input v-model="systemConfig.system_description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="systemConfig.version" readonly />
            </el-form-item>
            <el-form-item label="维护模式">
              <el-switch 
                v-model="systemConfig.maintenance_mode" 
                active-text="开启" 
                inactive-text="关闭" 
              />
            </el-form-item>
            <el-form-item label="维护提示">
              <el-input 
                v-model="systemConfig.maintenance_message" 
                type="textarea" 
                :rows="2"
                placeholder="系统维护中，请稍后访问"
              />
            </el-form-item>

            <h3 style="margin-top: 40px;">安全配置</h3>
            <el-form-item label="密码最小长度">
              <el-input-number v-model="systemConfig.min_password_length" :min="6" :max="20" />
            </el-form-item>
            <el-form-item label="登录失败限制">
              <el-input-number v-model="systemConfig.max_login_attempts" :min="3" :max="10" />
            </el-form-item>
            <el-form-item label="锁定时间(分钟)">
              <el-input-number v-model="systemConfig.lockout_duration" :min="5" :max="60" />
            </el-form-item>
            <el-form-item label="会话超时(小时)">
              <el-input-number v-model="systemConfig.session_timeout" :min="1" :max="24" />
            </el-form-item>

            <h3 style="margin-top: 40px;">业务配置</h3>
            <el-form-item label="订单自动分配">
              <el-switch 
                v-model="systemConfig.auto_assign_orders" 
                active-text="开启" 
                inactive-text="关闭" 
              />
            </el-form-item>
            <el-form-item label="工作时间开始">
              <el-time-picker v-model="systemConfig.work_start_time" format="HH:mm" />
            </el-form-item>
            <el-form-item label="工作时间结束">
              <el-time-picker v-model="systemConfig.work_end_time" format="HH:mm" />
            </el-form-item>
            <el-form-item label="客服电话">
              <el-input v-model="systemConfig.service_phone" />
            </el-form-item>
            <el-form-item label="客服邮箱">
              <el-input v-model="systemConfig.service_email" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="configLoading" @click="saveConfig">
                保存配置
              </el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 系统信息 -->
      <el-tab-pane label="系统信息" name="info">
        <div class="card-container">
          <el-descriptions title="系统运行信息" :column="2" border>
            <el-descriptions-item label="系统版本">{{ systemInfo.version }}</el-descriptions-item>
            <el-descriptions-item label="运行时间">{{ systemInfo.uptime }}</el-descriptions-item>
            <el-descriptions-item label="服务器时间">{{ systemInfo.server_time }}</el-descriptions-item>
            <el-descriptions-item label="数据库版本">{{ systemInfo.database_version }}</el-descriptions-item>
            <el-descriptions-item label="总用户数">{{ systemInfo.total_users }}</el-descriptions-item>
            <el-descriptions-item label="总订单数">{{ systemInfo.total_orders }}</el-descriptions-item>
            <el-descriptions-item label="总收入">¥{{ formatNumber(systemInfo.total_revenue) }}</el-descriptions-item>
            <el-descriptions-item label="活跃工人数">{{ systemInfo.active_workers }}</el-descriptions-item>
          </el-descriptions>

          <h3 style="margin-top: 30px;">服务器资源</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="resource-card">
                <div class="resource-title">CPU使用率</div>
                <div class="resource-value">{{ systemInfo.cpu_usage }}%</div>
                <el-progress :percentage="systemInfo.cpu_usage" :color="getProgressColor(systemInfo.cpu_usage)" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="resource-card">
                <div class="resource-title">内存使用率</div>
                <div class="resource-value">{{ systemInfo.memory_usage }}%</div>
                <el-progress :percentage="systemInfo.memory_usage" :color="getProgressColor(systemInfo.memory_usage)" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="resource-card">
                <div class="resource-title">磁盘使用率</div>
                <div class="resource-value">{{ systemInfo.disk_usage }}%</div>
                <el-progress :percentage="systemInfo.disk_usage" :color="getProgressColor(systemInfo.disk_usage)" />
              </div>
            </el-col>
            <el-col :span="6">
              <div class="resource-card">
                <div class="resource-title">网络负载</div>
                <div class="resource-value">{{ systemInfo.network_load }}%</div>
                <el-progress :percentage="systemInfo.network_load" :color="getProgressColor(systemInfo.network_load)" />
              </div>
            </el-col>
          </el-row>

          <div style="margin-top: 30px; text-align: center;">
            <el-button type="primary" @click="refreshSystemInfo">
              <el-icon><Refresh /></el-icon>
              刷新信息
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 管理员表单对话框 -->
    <el-dialog v-model="adminDialogVisible" :title="adminDialogTitle" width="600px">
      <el-form :model="adminForm" :rules="adminRules" ref="adminFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="adminForm.username" :disabled="!!adminForm.id" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="adminForm.name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="adminForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="adminForm.role" style="width: 100%">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!adminForm.id" label="密码" prop="password">
          <el-input v-model="adminForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="adminForm.is_active" active-text="激活" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adminDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="adminSubmitting" @click="submitAdmin">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'

const activeTab = ref('admins')
const adminLoading = ref(false)
const configLoading = ref(false)
const adminSubmitting = ref(false)
const adminDialogVisible = ref(false)
const adminDialogTitle = ref('')

const adminData = ref([])
const adminFormRef = ref()

const adminSearch = reactive({
  keyword: ''
})

const adminForm = reactive({
  id: null,
  username: '',
  name: '',
  email: '',
  role: 'admin',
  password: '',
  is_active: true
})

const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ]
}

const systemConfig = reactive({
  system_name: '车辆维修管理系统',
  system_description: '专业的车辆维修服务管理平台',
  version: 'v1.0.0',
  maintenance_mode: false,
  maintenance_message: '系统维护中，请稍后访问',
  min_password_length: 6,
  max_login_attempts: 5,
  lockout_duration: 15,
  session_timeout: 8,
  auto_assign_orders: true,
  work_start_time: '08:00',
  work_end_time: '18:00',
  service_phone: '400-123-4567',
  service_email: 'service@example.com'
})

const systemInfo = reactive({
  version: 'v1.0.0',
  uptime: '7天 15小时',
  server_time: '',
  database_version: 'PostgreSQL 13.8',
  total_users: 0,
  total_orders: 0,
  total_revenue: 0,
  active_workers: 0,
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0,
  network_load: 0
})

// 获取管理员列表
const fetchAdmins = async () => {
  adminLoading.value = true
  try {
    const params = {
      keyword: adminSearch.keyword
    }
    const response = await request.get('/system/admins', { params })
    adminData.value = response.items || []
  } catch (error) {
    console.error('获取管理员列表失败:', error)
    // 使用模拟数据
    adminData.value = [
      {
        id: 1,
        username: 'admin',
        name: '系统管理员',
        email: 'admin@example.com',
        role: 'super_admin',
        is_active: true,
        last_login: new Date().toISOString(),
        created_at: new Date().toISOString()
      }
    ]
  } finally {
    adminLoading.value = false
  }
}

// 搜索管理员
const searchAdmins = () => {
  fetchAdmins()
}

// 重置管理员搜索
const resetAdminSearch = () => {
  adminSearch.keyword = ''
  fetchAdmins()
}

// 添加管理员
const handleAddAdmin = () => {
  adminDialogTitle.value = '添加管理员'
  Object.assign(adminForm, {
    id: null,
    username: '',
    name: '',
    email: '',
    role: 'admin',
    password: '',
    is_active: true
  })
  adminDialogVisible.value = true
}

// 编辑管理员
const handleEditAdmin = (row) => {
  adminDialogTitle.value = '编辑管理员'
  Object.assign(adminForm, { ...row, password: '' })
  adminDialogVisible.value = true
}

// 提交管理员表单
const submitAdmin = async () => {
  const valid = await adminFormRef.value.validate()
  if (!valid) return

  adminSubmitting.value = true
  try {
    if (adminForm.id) {
      await request.put(`/system/admins/${adminForm.id}`, adminForm)
      ElMessage.success('更新成功')
    } else {
      await request.post('/system/admins', adminForm)
      ElMessage.success('添加成功')
    }
    adminDialogVisible.value = false
    fetchAdmins()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    adminSubmitting.value = false
  }
}

// 切换管理员状态
const handleToggleAdminStatus = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '禁用' : '激活'}管理员 ${row.name} 吗？`,
      '提示',
      { type: 'warning' }
    )
    
    await request.put(`/system/admins/${row.id}/toggle-status`)
    ElMessage.success('操作成功')
    fetchAdmins()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

// 删除管理员
const handleDeleteAdmin = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 ${row.name} 吗？此操作不可恢复！`,
      '警告',
      { type: 'error' }
    )
    
    await request.delete(`/system/admins/${row.id}`)
    ElMessage.success('删除成功')
    fetchAdmins()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 获取系统配置
const fetchSystemConfig = async () => {
  try {
    const response = await request.get('/system/config')
    Object.assign(systemConfig, response)
  } catch (error) {
    console.error('获取系统配置失败:', error)
  }
}

// 保存系统配置
const saveConfig = async () => {
  configLoading.value = true
  try {
    await request.put('/system/config', systemConfig)
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    configLoading.value = false
  }
}

// 重置配置
const resetConfig = () => {
  fetchSystemConfig()
}

// 获取系统信息
const fetchSystemInfo = async () => {
  try {
    const response = await request.get('/system/info')
    Object.assign(systemInfo, response)
  } catch (error) {
    console.error('获取系统信息失败:', error)
    // 使用模拟数据
    Object.assign(systemInfo, {
      version: 'v1.0.0',
      uptime: '7天 15小时',
      server_time: new Date().toLocaleString(),
      database_version: 'PostgreSQL 13.8',
      total_users: 1250,
      total_orders: 3480,
      total_revenue: 856400,
      active_workers: 28,
      cpu_usage: Math.floor(Math.random() * 80) + 10,
      memory_usage: Math.floor(Math.random() * 70) + 20,
      disk_usage: Math.floor(Math.random() * 60) + 30,
      network_load: Math.floor(Math.random() * 50) + 20
    })
  }
}

// 刷新系统信息
const refreshSystemInfo = () => {
  fetchSystemInfo()
}

// 获取角色类型
const getRoleType = (role) => {
  const typeMap = {
    'super_admin': 'danger',
    'admin': 'warning',
    'operator': 'primary'
  }
  return typeMap[role] || 'info'
}

// 获取角色文本
const getRoleText = (role) => {
  const textMap = {
    'super_admin': '超级管理员',
    'admin': '管理员',
    'operator': '操作员'
  }
  return textMap[role] || '未知'
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

// 格式化数字
const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchAdmins()
  fetchSystemConfig()
  fetchSystemInfo()
})
</script>

<style lang="scss" scoped>
.dashboard-header {
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

.system-tabs {
  :deep(.el-tabs__content) {
    padding-top: 20px;
  }
}

.resource-card {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .resource-title {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
  }

  .resource-value {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 12px;
  }
}

h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}
</style> 