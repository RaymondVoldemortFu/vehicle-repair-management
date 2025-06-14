<template>
  <div class="wages-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>我的工资</h1>
      <p>查看工资记录和收入统计</p>
    </div>

    <!-- 工资统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ summary.currentMonthWage.toLocaleString() }}</div>
                <div class="stat-label">本月工资</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ summary.totalEarnings.toLocaleString() }}</div>
                <div class="stat-label">累计收入</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ summary.currentMonthHours }}h</div>
                <div class="stat-label">本月工时</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ summary.currentMonthBonus.toLocaleString() }}</div>
                <div class="stat-label">本月奖金</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-date-picker
            v-model="dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            @change="fetchWages"
          />
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="fetchWages">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 工资记录表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>工资记录</span>
          <el-button type="text" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="wageRecords"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="pay_period" label="月份" width="120">
          <template #default="{ row }">
            <span>{{ formatMonth(row.pay_period) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="base_salary" label="基本工资" width="120">
          <template #default="{ row }">
            <span>¥{{ formatNumber(row.base_salary) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="overtime_pay" label="加班费" width="100">
          <template #default="{ row }">
            <span>¥{{ formatNumber(row.overtime_pay) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="100">
          <template #default="{ row }">
            <span>¥{{ formatNumber(row.bonus) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_payment" label="实发工资" width="120">
          <template #default="{ row }">
            <span class="total-amount">¥{{ formatNumber(row.total_payment) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="工作时长" width="120">
          <template #default="{ row }">
            <span>{{ formatNumber(row.total_hours) }}h</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_date" label="发放时间" width="120">
          <template #default="{ row }">
            <span>{{ row.pay_date ? formatDate(row.pay_date) : '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Money, TrendCharts, Clock, Star, Download, Refresh } from '@element-plus/icons-vue'
import { getMyWages } from '@/api/wage'
import dayjs from 'dayjs'

const loading = ref(false)
const wageRecords = ref([])
const dateRange = ref(null)

const summary = reactive({
  currentMonthWage: 0,
  totalEarnings: 0,
  currentMonthHours: 0,
  currentMonthBonus: 0,
})

const fetchWages = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await getMyWages(params)
    wageRecords.value = data
    calculateSummary(data)
  } catch (error) {
    console.error('获取工资记录失败:', error)
    ElMessage.error('获取工资记录失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  dateRange.value = null
  fetchWages()
}

const calculateSummary = (wages) => {
  const currentMonthStr = dayjs().format('YYYY-MM')
  const currentMonthData = wages.find(w => w.pay_period === currentMonthStr)

  summary.currentMonthWage = currentMonthData ? parseFloat(currentMonthData.total_payment) : 0
  summary.currentMonthHours = currentMonthData ? parseFloat(currentMonthData.total_hours) : 0
  summary.currentMonthBonus = currentMonthData ? parseFloat(currentMonthData.bonus) : 0
  
  summary.totalEarnings = wages.reduce((total, wage) => total + parseFloat(wage.total_payment), 0)
}

const getStatusText = (status) => {
  const map = {
    calculated: '核算中',
    paid: '已发放',
    disputed: '争议中',
  }
  return map[status] || '未知'
}

const getStatusType = (status) => {
  const map = {
    calculated: 'warning',
    paid: 'success',
    disputed: 'danger',
  }
  return map[status] || 'info'
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatMonth = (month) => {
  const [year, monthNum] = month.split('-')
  return `${year}年${monthNum}月`
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const refreshData = () => {
  fetchWages()
}

onMounted(() => {
  fetchWages()
})
</script>

<style scoped>
.wages-container {
  padding: 20px;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon .el-icon {
  font-size: 24px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-amount {
  font-weight: bold;
  color: #67C23A;
}
</style> 