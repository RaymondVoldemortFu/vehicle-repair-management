<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h1>管理员仪表板</h1>
      <p>系统运行状态概览</p>
    </div>

    <!-- 核心数据统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon users">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.userCount || 0 }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon vehicles">
            <el-icon><Van /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.vehicleCount || 0 }}</div>
            <div class="stat-label">车辆总数</div>
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
          <div class="stat-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatMoney(stats.revenue || 0) }}</div>
            <div class="stat-label">本月收入</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 订单状态统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="status-card pending">
          <div class="status-value">{{ orderStats.pending || 0 }}</div>
          <div class="status-label">待处理</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="status-card processing">
          <div class="status-value">{{ orderStats.in_progress || 0 }}</div>
          <div class="status-label">进行中</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="status-card completed">
          <div class="status-value">{{ orderStats.completed || 0 }}</div>
          <div class="status-label">已完成</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="status-card cancelled">
          <div class="status-value">{{ orderStats.cancelled || 0 }}</div>
          <div class="status-label">已取消</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card-container">
          <h3>订单趋势</h3>
          <div class="chart-container">
            <div v-if="!chartLoading" style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              图表组件（需要集成ECharts）
            </div>
            <el-skeleton v-else :rows="8" animated />
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <h3>收入分析</h3>
          <div class="chart-container">
            <div v-if="!chartLoading" style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              图表组件（需要集成ECharts）
            </div>
            <el-skeleton v-else :rows="8" animated />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 最新活动 -->
    <div class="card-container">
      <h3>最新活动</h3>
      <el-table v-loading="loading" :data="recentActivities" stripe>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActivityType(row.type)" size="small">
              {{ getActivityText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column prop="time" label="时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.time) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import dayjs from 'dayjs'

const loading = ref(false)
const chartLoading = ref(false)

const stats = reactive({
  userCount: 0,
  vehicleCount: 0,
  orderCount: 0,
  revenue: 0
})

const orderStats = reactive({
  pending: 0,
  in_progress: 0,
  completed: 0,
  cancelled: 0
})

const recentActivities = ref([])

// 获取仪表板数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    const analyticsRes = await request.get('/analytics/dashboard')

    // 更新统计数据
    if (analyticsRes && analyticsRes.basic_stats) {
      stats.userCount = analyticsRes.basic_stats.total_users
      stats.vehicleCount = analyticsRes.basic_stats.total_vehicles
      stats.orderCount = analyticsRes.basic_stats.total_orders
      stats.revenue = analyticsRes.basic_stats.monthly_revenue
    }
    
    if (analyticsRes && analyticsRes.order_statistics) {
        orderStats.pending = analyticsRes.order_statistics.pending
        orderStats.in_progress = analyticsRes.order_statistics.in_progress
        orderStats.completed = analyticsRes.order_statistics.completed
        orderStats.cancelled = analyticsRes.order_statistics.cancelled
    }

    // 模拟活动数据
    recentActivities.value = [
      {
        type: 'order',
        description: '新维修订单已创建',
        user: '张三',
        time: new Date()
      },
      {
        type: 'user',
        description: '新用户注册',
        user: '李四',
        time: new Date(Date.now() - 30 * 60 * 1000)
      },
      {
        type: 'payment',
        description: '订单付款完成',
        user: '王五',
        time: new Date(Date.now() - 60 * 60 * 1000)
      }
    ]

  } catch (error) {
    console.error('获取仪表板数据失败:', error)
    // 使用模拟数据
    Object.assign(stats, {
      userCount: 1250,
      vehicleCount: 2100,
      orderCount: 450,
      revenue: 125000
    })

    Object.assign(orderStats, {
      pending: 25,
      in_progress: 48,
      completed: 320,
      cancelled: 12
    })
  } finally {
    loading.value = false
  }
}

// 格式化金额
const formatMoney = (amount) => {
  return new Intl.NumberFormat('zh-CN').format(amount)
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取活动类型
const getActivityType = (type) => {
  const typeMap = {
    'order': 'primary',
    'user': 'success',
    'payment': 'warning',
    'system': 'info'
  }
  return typeMap[type] || 'info'
}

// 获取活动文本
const getActivityText = (type) => {
  const textMap = {
    'order': '订单',
    'user': '用户',
    'payment': '支付',
    'system': '系统'
  }
  return textMap[type] || '其他'
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

    &.users {
      background: #1890ff;
    }

    &.vehicles {
      background: #52c41a;
    }

    &.orders {
      background: #faad14;
    }

    &.revenue {
      background: #f759ab;
    }
  }

  .stat-content {
    flex: 1;

    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      line-height: 1;
    }

    .stat-label {
      font-size: 14px;
      color: #606266;
      margin: 4px 0;
    }
  }
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  border-left: 4px solid;

  &.pending {
    border-color: #faad14;
  }

  &.processing {
    border-color: #1890ff;
  }

  &.completed {
    border-color: #52c41a;
  }

  &.cancelled {
    border-color: #f5222d;
  }

  .status-value {
    font-size: 32px;
    font-weight: 600;
    color: #303133;
    line-height: 1;
  }

  .status-label {
    font-size: 14px;
    color: #606266;
    margin-top: 8px;
  }
}

.chart-container {
  height: 300px;
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
      font-size: 20px;
    }
  }

  .status-card {
    padding: 16px;

    .status-value {
      font-size: 24px;
    }
  }
}
</style> 