<template>
  <div class="analytics-container">
    <div class="page-header">
      <h1>数据分析</h1>
      <p>深入洞察业务数据，驱动决策</p>
    </div>

    <!-- 成本分析 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>成本构成趋势</span>
          <el-radio-group v-model="costPeriod" size="small" @change="fetchData">
            <el-radio-button label="month">月度</el-radio-button>
            <el-radio-button label="quarter">季度</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="costChart" style="height: 400px;"></div>
    </el-card>

    <el-row :gutter="20">
      <!-- 车型维修统计 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header><span>车型维修统计</span></template>
          <div ref="vehicleRepairChart" style="height: 400px;"></div>
        </el-card>
      </el-col>

      <!-- 工种任务分布 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header><span>工种任务分布</span></template>
          <div ref="taskDistributionChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 负面反馈工单 -->
    <el-card class="table-card">
       <template #header><span>低评分工单追踪 (评分 ≤ 2)</span></template>
      <el-table :data="analyticsData.negative_feedback_cases" stripe height="300">
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column prop="worker_name" label="涉及员工" width="120" />
        <el-table-column prop="rating" label="评分" width="100">
            <template #default="{ row }">
                <el-rate v-model="row.rating" disabled />
            </template>
        </el-table-column>
        <el-table-column prop="feedback_comment" label="负面反馈内容" show-overflow-tooltip />
      </el-table>
    </el-card>

     <!-- 未完成订单统计 -->
    <el-card class="table-card">
       <template #header><span>待处理/进行中订单</span></template>
       <el-table :data="analyticsData.unfinished_order_stats" stripe>
        <el-table-column prop="status" label="状态" align="center">
            <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : 'primary'">
                    {{ row.status === 'pending' ? '待处理' : '进行中' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="count" label="数量" align="center" />
       </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElLoading } from 'element-plus'
import * as echarts from 'echarts'

const costPeriod = ref('month')
const analyticsData = reactive({
  vehicle_repair_stats: [],
  cost_trends: [],
  negative_feedback_cases: [],
  worker_task_distribution: [],
  unfinished_order_stats: [],
})

const costChart = ref(null)
const vehicleRepairChart = ref(null)
const taskDistributionChart = ref(null)

let costChartInstance = null
let vehicleRepairChartInstance = null
let taskDistributionChartInstance = null

const fetchData = async () => {
  const loading = ElLoading.service({ text: '正在加载分析数据...', background: 'rgba(0, 0, 0, 0.7)' })
  try {
    const params = { cost_period: costPeriod.value }
    const res = await request.get('/analytics/comprehensive', { params })
    Object.assign(analyticsData, res)
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error("获取分析数据失败:", error)
    ElMessage.error("获取分析数据失败，请稍后再试")
  } finally {
    loading.close()
  }
}

const renderCharts = () => {
  // 成本趋势图
  if (costChart.value) {
    costChartInstance = echarts.init(costChart.value)
    costChartInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['工时费', '材料费', '服务费', '总费用'] },
      xAxis: { type: 'category', data: analyticsData.cost_trends.map(d => d.period) },
      yAxis: { type: 'value' },
      series: [
        { name: '工时费', type: 'bar', stack: 'total', data: analyticsData.cost_trends.map(d => d.labor_cost) },
        { name: '材料费', type: 'bar', stack: 'total', data: analyticsData.cost_trends.map(d => d.material_cost) },
        { name: '服务费', type: 'bar', stack: 'total', data: analyticsData.cost_trends.map(d => d.service_cost) },
        { name: '总费用', type: 'line', yAxisIndex: 0, data: analyticsData.cost_trends.map(d => d.total_cost) }
      ]
    })
  }

  // 车型维修统计图
  if (vehicleRepairChart.value) {
    vehicleRepairChartInstance = echarts.init(vehicleRepairChart.value)
    vehicleRepairChartInstance.setOption({
       tooltip: { trigger: 'item' },
       legend: { top: '5%', left: 'center' },
       series: [{
          name: '车型维修统计',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false, position: 'center' },
          emphasis: {
            label: { show: true, fontSize: '20', fontWeight: 'bold' }
          },
          labelLine: { show: false },
          data: analyticsData.vehicle_repair_stats.map(d => ({ value: d.repair_count, name: d.model }))
       }]
    })
  }
  
  // 工种任务分布图
  if (taskDistributionChart.value) {
    taskDistributionChartInstance = echarts.init(taskDistributionChart.value)
     taskDistributionChartInstance.setOption({
        tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
        legend: {
            orient: 'vertical',
            left: 10,
            data: analyticsData.worker_task_distribution.map(d => d.skill_type)
        },
        series: [{
            name: '任务分布',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: analyticsData.worker_task_distribution.map(d => ({ value: d.task_count, name: d.skill_type })),
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    })
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', () => {
      costChartInstance?.resize()
      vehicleRepairChartInstance?.resize()
      taskDistributionChartInstance?.resize()
  })
})
</script>

<style scoped>
.analytics-container {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.chart-card, .table-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 