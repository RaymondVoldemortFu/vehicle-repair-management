<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h1>用户仪表板</h1>
      <p>欢迎回来，{{ userInfo?.name }}！</p>
    </div>

    <!-- 数据统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon vehicles">
            <el-icon><Van /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.vehicleCount || 0 }}</div>
            <div class="stat-label">我的车辆</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon orders">
            <el-icon><List /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.orderCount || 0 }}</div>
            <div class="stat-label">维修订单</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon pending">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pendingCount || 0 }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon completed">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completedCount || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <div class="card-container">
      <h3>快速操作</h3>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button 
            type="primary" 
            size="large" 
            @click="$router.push('/user/vehicles')"
            style="width: 100%; height: 60px;"
          >
            <el-icon><Van /></el-icon>
            管理车辆
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="success" 
            size="large" 
            @click="handleCreateOrder"
            style="width: 100%; height: 60px;"
          >
            <el-icon><Plus /></el-icon>
            新建订单
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="warning" 
            size="large" 
            @click="$router.push('/user/orders')"
            style="width: 100%; height: 60px;"
          >
            <el-icon><List /></el-icon>
            查看订单
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="info" 
            size="large" 
            @click="$router.push('/user/feedback')"
            style="width: 100%; height: 60px;"
          >
            <el-icon><ChatDotSquare /></el-icon>
            意见反馈
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 最近订单 -->
    <div class="card-container">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3>最近订单</h3>
        <el-button type="text" @click="$router.push('/user/orders')">
          查看全部
        </el-button>
      </div>
      <el-table v-loading="loading" :data="recentOrders" stripe>
        <el-table-column prop="order_number" label="订单号" width="120" />
        <el-table-column prop="description" label="故障描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewOrder(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建订单对话框 -->
    <el-dialog v-model="orderDialogVisible" title="新建维修订单" width="600px">
      <el-form :model="orderForm" :rules="orderRules" ref="orderFormRef" label-width="80px">
        <el-form-item label="选择车辆" prop="vehicle_id">
          <el-select v-model="orderForm.vehicle_id" placeholder="请选择要维修的车辆" style="width: 100%">
            <el-option
              v-for="vehicle in vehicles"
              :key="vehicle.id"
              :label="`${vehicle.license_plate} - ${vehicle.model}`"
              :value="vehicle.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="故障描述" prop="description">
          <el-input
            v-model="orderForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述车辆故障情况"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="orderForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitOrder">
          提交订单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'

const router = useRouter()
const authStore = useAuthStore()

const userInfo = computed(() => authStore.userInfo)
const loading = ref(false)
const orderDialogVisible = ref(false)
const submitting = ref(false)

const stats = reactive({
  vehicleCount: 0,
  orderCount: 0,
  pendingCount: 0,
  completedCount: 0
})

const recentOrders = ref([])
const vehicles = ref([])

const orderForm = reactive({
  vehicle_id: '',
  description: '',
  priority: 'medium',
  user_id: userInfo.value?.id
})

const orderFormRef = ref()

const orderRules = {
  vehicle_id: [
    { required: true, message: '请选择车辆', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入故障描述', trigger: 'blur' },
    { min: 10, message: '故障描述至少10个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 获取仪表板数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 获取车辆数量
    const vehiclesRes = await request.get('/vehicles/my-vehicles')
    stats.vehicleCount = vehiclesRes.length
    vehicles.value = vehiclesRes

    // 获取订单数据
    const ordersRes = await request.get('/repair-orders/my-orders', {
      params: { page: 1, size: 5 }
    })
    
    stats.orderCount = ordersRes.total
    stats.pendingCount = ordersRes.items.filter(item => 
      ['pending', 'in_progress'].includes(item.status)
    ).length
    stats.completedCount = ordersRes.items.filter(item => 
      item.status === 'completed'
    ).length
    
    recentOrders.value = ordersRes.items
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理新建订单
const handleCreateOrder = () => {
  if (vehicles.value.length === 0) {
    ElMessage.warning('请先添加车辆信息')
    router.push('/user/vehicles')
    return
  }
  orderDialogVisible.value = true
}

// 提交订单
const submitOrder = async () => {
  const valid = await orderFormRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    await request.post('/repair-orders/', {
      ...orderForm,
      user_id: userInfo.value.id
    })
    ElMessage.success('订单创建成功')
    orderDialogVisible.value = false
    fetchDashboardData() // 刷新数据
  } catch (error) {
    console.error('创建订单失败:', error)
  } finally {
    submitting.value = false
  }
}

// 查看订单详情
const viewOrder = (order) => {
  router.push(`/user/orders?orderId=${order.id}`)
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || '未知'
}

onMounted(() => {
  fetchDashboardData()
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

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;

    .el-icon {
      font-size: 24px;
      color: white;
    }

    &.vehicles {
      background: #1890ff;
    }

    &.orders {
      background: #52c41a;
    }

    &.pending {
      background: #faad14;
    }

    &.completed {
      background: #13c2c2;
    }
  }

  .stat-content {
    flex: 1;

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      line-height: 1;
    }

    .stat-label {
      font-size: 14px;
      color: #606266;
      margin-top: 4px;
    }
  }
}

h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .stats-row {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }

  .stat-card {
    padding: 16px;

    .stat-icon {
      width: 48px;
      height: 48px;
      margin-right: 12px;

      .el-icon {
        font-size: 20px;
      }
    }

    .stat-content .stat-value {
      font-size: 24px;
    }
  }
}
</style> 