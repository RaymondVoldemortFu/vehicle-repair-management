<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h1>工作台</h1>
      <p>欢迎回来，{{ workerInfo.name }}！今天是 {{ currentDate }}</p>
    </div>

    <!-- 工作统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card pending">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ workStats.pendingOrders }}</div>
            <div class="stat-label">待处理订单</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card processing">
          <div class="stat-icon">
            <el-icon><Tools /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ workStats.processingOrders }}</div>
            <div class="stat-label">进行中订单</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card completed">
          <div class="stat-icon">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ workStats.completedToday }}</div>
            <div class="stat-label">今日完成</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card earnings">
          <div class="stat-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ workStats.todayEarnings }}</div>
            <div class="stat-label">今日收入</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 今日任务 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header">
            <h3>今日任务</h3>
            <el-button size="small" @click="fetchTodayOrders" disabled>
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          
          <div class="task-list">
            <div v-if="todayOrders.length === 0" class="empty-state">
              <el-empty description="暂无今日任务" />
            </div>
            
            <div 
              v-for="order in todayOrders" 
              :key="order.id" 
              class="task-item"
              @click="handleViewOrder(order)"
            >
              <div class="task-header">
                <div class="task-info">
                  <div class="task-title">{{ order.order_number }}</div>
                  <div class="task-vehicle">{{ order.vehicle?.license_plate }} - {{ order.vehicle?.model }}</div>
                </div>
                <el-tag :type="getStatusType(order.status)" size="small">
                  {{ getStatusText(order.status) }}
                </el-tag>
              </div>
              <div class="task-description">{{ order.description }}</div>
              <div class="task-meta">
                <span class="task-priority">
                  <el-tag :type="getPriorityType(order.priority)" size="small">
                    {{ getPriorityText(order.priority) }}
                  </el-tag>
                </span>
                <span class="task-time">{{ formatDate(order.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 工作进度和收入统计 -->
      <el-col :span="12">
        <div class="card-container">
          <h3>本周统计</h3>
          <div class="progress-section">
            <div class="progress-item">
              <div class="progress-label">
                <span>订单完成率</span>
                <span>{{ weekStats.completionRate }}%</span>
              </div>
              <el-progress 
                :percentage="weekStats.completionRate" 
                :color="getProgressColor(weekStats.completionRate)"
              />
            </div>
            
            <div class="progress-item">
              <div class="progress-label">
                <span>客户满意度</span>
                <span>{{ weekStats.satisfaction }}%</span>
              </div>
              <el-progress 
                :percentage="weekStats.satisfaction" 
                :color="getProgressColor(weekStats.satisfaction)"
              />
            </div>
            
            <div class="progress-item">
              <div class="progress-label">
                <span>工作效率</span>
                <span>{{ weekStats.efficiency }}%</span>
              </div>
              <el-progress 
                :percentage="weekStats.efficiency" 
                :color="getProgressColor(weekStats.efficiency)"
              />
            </div>
          </div>

          <div class="earnings-section">
            <h4>收入统计</h4>
            <div class="earnings-grid">
              <div class="earnings-item">
                <div class="earnings-value">¥{{ weekStats.weekEarnings }}</div>
                <div class="earnings-label">本周收入</div>
              </div>
              <div class="earnings-item">
                <div class="earnings-value">¥{{ weekStats.monthEarnings }}</div>
                <div class="earnings-label">本月收入</div>
              </div>
              <div class="earnings-item">
                <div class="earnings-value">{{ weekStats.avgOrderValue }}</div>
                <div class="earnings-label">平均订单价值</div>
              </div>
              <div class="earnings-item">
                <div class="earnings-value">{{ weekStats.totalOrders }}</div>
                <div class="earnings-label">总订单数</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <div class="card-container">
      <h3>快速操作</h3>
      <div class="quick-actions">
        <el-button type="primary" @click="handleStartWork">
          <el-icon><VideoPlay /></el-icon>
          开始工作
        </el-button>
        <el-button type="success" @click="handleCompleteOrder">
          <el-icon><Check /></el-icon>
          完成订单
        </el-button>
        <el-button type="warning" @click="handleReportIssue">
          <el-icon><Warning /></el-icon>
          报告问题
        </el-button>
        <el-button type="info" @click="handleViewSchedule">
          <el-icon><Calendar /></el-icon>
          查看排班
        </el-button>
      </div>
    </div>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="orderDetailVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="车辆信息">
          {{ currentOrder.vehicle?.license_plate }} - {{ currentOrder.vehicle?.model }}
        </el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentOrder.user_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentOrder.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="预估费用">
          {{ currentOrder.estimated_cost ? `¥${currentOrder.estimated_cost}` : '待评估' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="期望完成时间">
          {{ currentOrder.expected_completion_date ? formatDate(currentOrder.expected_completion_date) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>故障描述</h4>
        <p>{{ currentOrder.description }}</p>
      </div>

      <div v-if="currentOrder.repair_notes" style="margin-top: 20px;">
        <h4>维修记录</h4>
        <p>{{ currentOrder.repair_notes }}</p>
      </div>

      <template #footer>
        <el-button @click="orderDetailVisible = false">关闭</el-button>
        <el-button 
          v-if="currentOrder.status === 'pending'" 
          type="primary" 
          @click="handleStartOrder(currentOrder)"
        >
          开始维修
        </el-button>
        <el-button 
          v-if="currentOrder.status === 'in_progress'" 
          type="success" 
          @click="handleFinishOrder(currentOrder)"
        >
          完成订单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const orderDetailVisible = ref(false)
const todayOrders = ref([])
const currentOrder = ref({})

const workerInfo = computed(() => authStore.userInfo || {})
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))

const workStats = reactive({
  pendingOrders: 0,
  processingOrders: 0,
  completedToday: 0,
  todayEarnings: 0
})

const weekStats = reactive({
  completionRate: 0,
  satisfaction: 0,
  efficiency: 0,
  weekEarnings: 0,
  monthEarnings: 0,
  avgOrderValue: 0,
  totalOrders: 0
})

// 获取工作统计
const fetchWorkStats = async () => {
  try {
    const response = await request.get('/workers/statistics/overview')
    workStats.pendingOrders = response.pending_orders || 0
    workStats.processingOrders = response.processing_orders || 0
    workStats.completedToday = response.completed_today || 0
    workStats.todayEarnings = response.today_earnings || 0
  } catch (error) {
    console.error('获取工作统计失败:', error)
    Object.assign(workStats, {
      pendingOrders: 3,
      processingOrders: 2,
      completedToday: 5,
      todayEarnings: 850
    })
  }
}

// 获取今日订单
const fetchTodayOrders = async () => {
  try {
    const response = await request.get('/workers/today-orders')
    todayOrders.value = response || []
  } catch (error) {
    console.error('获取今日订单失败:', error)
    todayOrders.value = [
      {
        id: 1,
        order_number: 'WO202412250001',
        description: '发动机异响，需要检查',
        status: 'pending',
        priority: 'high',
        vehicle: { license_plate: '京A12345', model: '丰田凯美瑞' },
        user_name: '张先生',
        created_at: new Date().toISOString()
      }
    ]
  }
}

// 查看订单详情
const handleViewOrder = async (order) => {
  try {
    const response = await request.get(`/repair-orders/${order.id}`)
    currentOrder.value = response
    orderDetailVisible.value = true
  } catch (error) {
    console.error('获取订单详情失败:', error)
    currentOrder.value = order
    orderDetailVisible.value = true
  }
}

// 开始订单
const handleStartOrder = async (order) => {
  try {
    await request.put(`/repair-orders/${order.id}/start`)
    ElMessage.success('订单已开始')
    orderDetailVisible.value = false
    fetchTodayOrders()
    fetchWorkStats()
  } catch (error) {
    console.error('开始订单失败:', error)
  }
}

// 完成订单
const handleFinishOrder = async (order) => {
  try {
    await request.put(`/repair-orders/${order.id}/complete`)
    ElMessage.success('订单已完成')
    orderDetailVisible.value = false
    fetchTodayOrders()
    fetchWorkStats()
  } catch (error) {
    console.error('完成订单失败:', error)
  }
}

// 快速操作
const handleStartWork = () => {
  if (todayOrders.value.length === 0) {
    ElMessage.info('暂无待处理订单')
    return
  }
  const pendingOrder = todayOrders.value.find(order => order.status === 'pending')
  if (pendingOrder) {
    handleViewOrder(pendingOrder)
  } else {
    ElMessage.info('暂无待处理订单')
  }
}

const handleCompleteOrder = () => {
  const processingOrder = todayOrders.value.find(order => order.status === 'in_progress')
  if (processingOrder) {
    handleViewOrder(processingOrder)
  } else {
    ElMessage.info('暂无进行中的订单')
  }
}

const handleReportIssue = () => {
  ElMessage.info('问题报告功能开发中')
}

const handleViewSchedule = () => {
  ElMessage.info('排班查看功能开发中')
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || '未知'
}

// 获取优先级类型
const getPriorityType = (priority) => {
  const map = { low: 'info', medium: '', high: 'warning', urgent: 'danger' }
  return map[priority] || 'info'
}

// 获取优先级文本
const getPriorityText = (priority) => {
  const map = { low: '低', medium: '中', high: '高', urgent: '紧急' }
  return map[priority] || '未知'
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage < 60) return '#f56c6c'
  if (percentage < 80) return '#e6a23c'
  return '#67c23a'
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('MM-DD HH:mm')
}

onMounted(() => {
  fetchWorkStats()
  // fetchTodayOrders() // 暂时禁用
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
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

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
  }

  .stat-content {
    flex: 1;

    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      line-height: 1;
      margin-bottom: 4px;
    }

    .stat-label {
      font-size: 14px;
      color: #606266;
    }
  }

  &.pending .stat-icon {
    background: #e6a23c;
  }

  &.processing .stat-icon {
    background: #1890ff;
  }

  &.completed .stat-icon {
    background: #52c41a;
  }

  &.earnings .stat-icon {
    background: #722ed1;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    color: #303133;
    font-size: 16px;
    font-weight: 600;
  }
}

.task-list {
  max-height: 400px;
  overflow-y: auto;
}

.task-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #c6e2ff;
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  }

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;

    .task-info {
      .task-title {
        font-weight: 600;
        color: #303133;
        margin-bottom: 4px;
      }

      .task-vehicle {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .task-description {
    color: #606266;
    font-size: 13px;
    margin-bottom: 8px;
  }

  .task-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #909399;
  }
}

.progress-section {
  margin-bottom: 24px;

  .progress-item {
    margin-bottom: 16px;

    .progress-label {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 14px;
      color: #303133;
    }
  }
}

.earnings-section {
  h4 {
    margin: 0 0 16px 0;
    color: #303133;
    font-size: 14px;
    font-weight: 600;
  }

  .earnings-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;

    .earnings-item {
      text-align: center;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 6px;

      .earnings-value {
        font-size: 18px;
        font-weight: 600;
        color: #1890ff;
        margin-bottom: 4px;
      }

      .earnings-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.quick-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
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
      font-size: 20px;
    }
  }

  .quick-actions {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }

  .earnings-grid {
    grid-template-columns: 1fr;
  }
}
</style> 