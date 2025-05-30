<template>
  <div class="page-container">
    <div class="dashboard-header">
      <h1>数据分析</h1>
      <p>深度分析系统运营数据，为决策提供支持</p>
    </div>

    <!-- 时间范围选择 -->
    <div class="card-container">
      <el-form :inline="true" :model="dateForm" class="date-filter">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 关键指标卡片 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-icon orders">
            <el-icon><List /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.totalOrders }}</div>
            <div class="metric-label">总订单数</div>
            <div class="metric-change">
              <span :class="metrics.orderChange >= 0 ? 'positive' : 'negative'">
                {{ metrics.orderChange >= 0 ? '↗' : '↘' }}
                {{ Math.abs(metrics.orderChange) }}%
              </span>
              <span class="vs-last">vs 上期</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">¥{{ formatNumber(metrics.totalRevenue) }}</div>
            <div class="metric-label">总收入</div>
            <div class="metric-change">
              <span :class="metrics.revenueChange >= 0 ? 'positive' : 'negative'">
                {{ metrics.revenueChange >= 0 ? '↗' : '↘' }}
                {{ Math.abs(metrics.revenueChange) }}%
              </span>
              <span class="vs-last">vs 上期</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-icon users">
            <el-icon><User /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.newUsers }}</div>
            <div class="metric-label">新增用户</div>
            <div class="metric-change">
              <span :class="metrics.userChange >= 0 ? 'positive' : 'negative'">
                {{ metrics.userChange >= 0 ? '↗' : '↘' }}
                {{ Math.abs(metrics.userChange) }}%
              </span>
              <span class="vs-last">vs 上期</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-icon satisfaction">
            <el-icon><Star /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.satisfaction }}%</div>
            <div class="metric-label">客户满意度</div>
            <div class="metric-change">
              <span :class="metrics.satisfactionChange >= 0 ? 'positive' : 'negative'">
                {{ metrics.satisfactionChange >= 0 ? '↗' : '↘' }}
                {{ Math.abs(metrics.satisfactionChange) }}%
              </span>
              <span class="vs-last">vs 上期</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card-container">
          <h3>订单趋势分析</h3>
          <div class="chart-container" ref="orderTrendChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <h3>收入分析</h3>
          <div class="chart-container" ref="revenueChart" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <div class="card-container">
          <h3>订单状态分布</h3>
          <div class="chart-container" ref="statusChart" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card-container">
          <h3>服务类型分析</h3>
          <div class="chart-container" ref="serviceChart" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card-container">
          <h3>工人工作量</h3>
          <div class="chart-container" ref="workerChart" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <div class="card-container">
      <h3>详细数据分析</h3>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="订单分析" name="orders">
          <el-table :data="orderAnalytics" stripe>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="total_orders" label="总订单" width="100" />
            <el-table-column prop="completed_orders" label="完成订单" width="100" />
            <el-table-column prop="completion_rate" label="完成率" width="100">
              <template #default="{ row }">
                {{ row.completion_rate }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_completion_time" label="平均完成时间" width="120">
              <template #default="{ row }">
                {{ row.avg_completion_time }}小时
              </template>
            </el-table-column>
            <el-table-column prop="revenue" label="收入" width="120">
              <template #default="{ row }">
                ¥{{ formatNumber(row.revenue) }}
              </template>
            </el-table-column>
            <el-table-column prop="customer_rating" label="客户评分" width="100">
              <template #default="{ row }">
                <el-rate v-model="row.customer_rating" disabled show-score />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="用户分析" name="users">
          <el-table :data="userAnalytics" stripe>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="new_users" label="新用户" width="100" />
            <el-table-column prop="active_users" label="活跃用户" width="100" />
            <el-table-column prop="retention_rate" label="留存率" width="100">
              <template #default="{ row }">
                {{ row.retention_rate }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_orders_per_user" label="人均订单" width="120">
              <template #default="{ row }">
                {{ row.avg_orders_per_user }}
              </template>
            </el-table-column>
            <el-table-column prop="avg_revenue_per_user" label="人均消费" width="120">
              <template #default="{ row }">
                ¥{{ formatNumber(row.avg_revenue_per_user) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="工人分析" name="workers">
          <el-table :data="workerAnalytics" stripe>
            <el-table-column prop="worker_name" label="工人姓名" width="120" />
            <el-table-column prop="total_orders" label="总订单" width="100" />
            <el-table-column prop="completed_orders" label="完成订单" width="100" />
            <el-table-column prop="efficiency" label="效率" width="100">
              <template #default="{ row }">
                {{ row.efficiency }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_rating" label="平均评分" width="120">
              <template #default="{ row }">
                <el-rate v-model="row.avg_rating" disabled show-score />
              </template>
            </el-table-column>
            <el-table-column prop="total_revenue" label="创造收入" width="120">
              <template #default="{ row }">
                ¥{{ formatNumber(row.total_revenue) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'
import * as echarts from 'echarts'

const loading = ref(false)
const activeTab = ref('orders')

// 图表实例
const orderTrendChart = ref()
const revenueChart = ref()
const statusChart = ref()
const serviceChart = ref()
const workerChart = ref()

let orderTrendInstance = null
let revenueInstance = null
let statusInstance = null
let serviceInstance = null
let workerInstance = null

const dateForm = reactive({
  dateRange: [
    dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD')
  ]
})

const metrics = reactive({
  totalOrders: 0,
  totalRevenue: 0,
  newUsers: 0,
  satisfaction: 0,
  orderChange: 0,
  revenueChange: 0,
  userChange: 0,
  satisfactionChange: 0
})

const orderAnalytics = ref([])
const userAnalytics = ref([])
const workerAnalytics = ref([])

// 获取分析数据
const fetchAnalyticsData = async () => {
  loading.value = true
  try {
    const [metricsRes, orderRes, userRes, workerRes] = await Promise.all([
      request.get('/analytics/metrics', {
        params: {
          start_date: dateForm.dateRange[0],
          end_date: dateForm.dateRange[1]
        }
      }),
      request.get('/analytics/orders', {
        params: {
          start_date: dateForm.dateRange[0],
          end_date: dateForm.dateRange[1]
        }
      }),
      request.get('/analytics/users', {
        params: {
          start_date: dateForm.dateRange[0],
          end_date: dateForm.dateRange[1]
        }
      }),
      request.get('/analytics/workers', {
        params: {
          start_date: dateForm.dateRange[0],
          end_date: dateForm.dateRange[1]
        }
      })
    ])

    Object.assign(metrics, metricsRes)
    orderAnalytics.value = orderRes.items || []
    userAnalytics.value = userRes.items || []
    workerAnalytics.value = workerRes.items || []

    await nextTick()
    initCharts()
  } catch (error) {
    console.error('获取分析数据失败:', error)
    // 使用模拟数据
    loadMockData()
  } finally {
    loading.value = false
  }
}

// 加载模拟数据
const loadMockData = () => {
  Object.assign(metrics, {
    totalOrders: 1284,
    totalRevenue: 256800,
    newUsers: 89,
    satisfaction: 92.5,
    orderChange: 12.3,
    revenueChange: 8.7,
    userChange: 15.2,
    satisfactionChange: 2.1
  })

  // 生成模拟订单分析数据
  orderAnalytics.value = Array.from({ length: 7 }, (_, i) => ({
    date: dayjs().subtract(6 - i, 'day').format('YYYY-MM-DD'),
    total_orders: Math.floor(Math.random() * 50) + 20,
    completed_orders: Math.floor(Math.random() * 40) + 15,
    completion_rate: Math.floor(Math.random() * 20) + 80,
    avg_completion_time: Math.floor(Math.random() * 12) + 6,
    revenue: Math.floor(Math.random() * 10000) + 5000,
    customer_rating: Math.floor(Math.random() * 2) + 4
  }))

  // 生成模拟用户分析数据
  userAnalytics.value = Array.from({ length: 7 }, (_, i) => ({
    date: dayjs().subtract(6 - i, 'day').format('YYYY-MM-DD'),
    new_users: Math.floor(Math.random() * 15) + 5,
    active_users: Math.floor(Math.random() * 100) + 50,
    retention_rate: Math.floor(Math.random() * 20) + 70,
    avg_orders_per_user: (Math.random() * 2 + 1).toFixed(1),
    avg_revenue_per_user: Math.floor(Math.random() * 500) + 200
  }))

  // 生成模拟工人分析数据
  workerAnalytics.value = [
    { worker_name: '张师傅', total_orders: 85, completed_orders: 82, efficiency: 96, avg_rating: 4.8, total_revenue: 45600 },
    { worker_name: '李师傅', total_orders: 72, completed_orders: 68, efficiency: 94, avg_rating: 4.6, total_revenue: 38900 },
    { worker_name: '王师傅', total_orders: 91, completed_orders: 87, efficiency: 96, avg_rating: 4.9, total_revenue: 52300 },
    { worker_name: '刘师傅', total_orders: 66, completed_orders: 61, efficiency: 92, avg_rating: 4.5, total_revenue: 34200 },
    { worker_name: '陈师傅', total_orders: 78, completed_orders: 74, efficiency: 95, avg_rating: 4.7, total_revenue: 41800 }
  ]

  nextTick(() => {
    initCharts()
  })
}

// 初始化图表
const initCharts = () => {
  initOrderTrendChart()
  initRevenueChart()
  initStatusChart()
  initServiceChart()
  initWorkerChart()
}

// 订单趋势图表
const initOrderTrendChart = () => {
  if (orderTrendInstance) {
    orderTrendInstance.dispose()
  }
  orderTrendInstance = echarts.init(orderTrendChart.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['总订单', '完成订单'] },
    xAxis: {
      type: 'category',
      data: orderAnalytics.value.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '总订单',
        type: 'line',
        data: orderAnalytics.value.map(item => item.total_orders),
        smooth: true,
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '完成订单',
        type: 'line',
        data: orderAnalytics.value.map(item => item.completed_orders),
        smooth: true,
        itemStyle: { color: '#52c41a' }
      }
    ]
  }
  orderTrendInstance.setOption(option)
}

// 收入分析图表
const initRevenueChart = () => {
  if (revenueInstance) {
    revenueInstance.dispose()
  }
  revenueInstance = echarts.init(revenueChart.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: orderAnalytics.value.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '收入',
      type: 'bar',
      data: orderAnalytics.value.map(item => item.revenue),
      itemStyle: { color: '#722ed1' }
    }]
  }
  revenueInstance.setOption(option)
}

// 订单状态分布图表
const initStatusChart = () => {
  if (statusInstance) {
    statusInstance.dispose()
  }
  statusInstance = echarts.init(statusChart.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    series: [{
      name: '订单状态',
      type: 'pie',
      radius: '60%',
      data: [
        { value: 450, name: '已完成', itemStyle: { color: '#52c41a' } },
        { value: 180, name: '进行中', itemStyle: { color: '#1890ff' } },
        { value: 85, name: '待处理', itemStyle: { color: '#faad14' } },
        { value: 32, name: '已取消', itemStyle: { color: '#f5222d' } }
      ]
    }]
  }
  statusInstance.setOption(option)
}

// 服务类型分析图表
const initServiceChart = () => {
  if (serviceInstance) {
    serviceInstance.dispose()
  }
  serviceInstance = echarts.init(serviceChart.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    series: [{
      name: '服务类型',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 320, name: '常规保养', itemStyle: { color: '#1890ff' } },
        { value: 240, name: '故障维修', itemStyle: { color: '#f5222d' } },
        { value: 180, name: '零件更换', itemStyle: { color: '#faad14' } },
        { value: 120, name: '深度检修', itemStyle: { color: '#52c41a' } },
        { value: 90, name: '其他服务', itemStyle: { color: '#722ed1' } }
      ]
    }]
  }
  serviceInstance.setOption(option)
}

// 工人工作量图表
const initWorkerChart = () => {
  if (workerInstance) {
    workerInstance.dispose()
  }
  workerInstance = echarts.init(workerChart.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: workerAnalytics.value.map(item => item.worker_name),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      name: '完成订单数',
      type: 'bar',
      data: workerAnalytics.value.map(item => item.completed_orders),
      itemStyle: { color: '#13c2c2' }
    }]
  }
  workerInstance.setOption(option)
}

// 时间范围变化
const handleDateChange = () => {
  refreshData()
}

// 刷新数据
const refreshData = () => {
  fetchAnalyticsData()
}

// 导出报告
const exportReport = () => {
  ElMessage.success('导出功能开发中')
}

// 格式化数字
const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

onMounted(() => {
  fetchAnalyticsData()
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

.date-filter {
  margin-bottom: 0;
}

.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;

  .metric-icon {
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

    &.orders {
      background: #1890ff;
    }

    &.revenue {
      background: #722ed1;
    }

    &.users {
      background: #52c41a;
    }

    &.satisfaction {
      background: #faad14;
    }
  }

  .metric-content {
    flex: 1;

    .metric-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      line-height: 1;
      margin-bottom: 4px;
    }

    .metric-label {
      font-size: 14px;
      color: #606266;
      margin-bottom: 8px;
    }

    .metric-change {
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 4px;

      .positive {
        color: #52c41a;
      }

      .negative {
        color: #f5222d;
      }

      .vs-last {
        color: #909399;
      }
    }
  }
}

.chart-container {
  width: 100%;
}

h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .metrics-row {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }

  .metric-card {
    padding: 16px;

    .metric-icon {
      width: 48px;
      height: 48px;
      margin-right: 12px;

      .el-icon {
        font-size: 20px;
      }
    }

    .metric-content .metric-value {
      font-size: 20px;
    }
  }
}
</style> 