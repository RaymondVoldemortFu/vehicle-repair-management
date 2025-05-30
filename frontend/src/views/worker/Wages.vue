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
                <div class="stat-value">¥{{ currentMonthWage.toLocaleString() }}</div>
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
                <div class="stat-value">¥{{ totalEarnings.toLocaleString() }}</div>
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
                <div class="stat-value">{{ currentMonthHours }}h</div>
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
                <div class="stat-value">¥{{ currentMonthBonus.toLocaleString() }}</div>
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
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            @change="handleDateRangeChange"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" placeholder="工资状态" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="已发放" value="paid" />
            <el-option label="待发放" value="pending" />
            <el-option label="处理中" value="processing" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="exportWageData">
            <el-icon><Download /></el-icon>
            导出工资单
          </el-button>
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
        :data="filteredWageRecords"
        stripe
        style="width: 100%"
        @row-click="showWageDetail"
      >
        <el-table-column prop="month" label="月份" width="120">
          <template #default="{ row }">
            <span>{{ formatMonth(row.month) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="basicSalary" label="基本工资" width="120">
          <template #default="{ row }">
            <span>¥{{ row.basicSalary.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="overtimePay" label="加班费" width="100">
          <template #default="{ row }">
            <span>¥{{ row.overtimePay.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="100">
          <template #default="{ row }">
            <span>¥{{ row.bonus.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="deduction" label="扣款" width="100">
          <template #default="{ row }">
            <span class="deduction-amount">-¥{{ row.deduction.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalAmount" label="实发工资" width="120">
          <template #default="{ row }">
            <span class="total-amount">¥{{ row.totalAmount.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="workHours" label="工作时长" width="100">
          <template #default="{ row }">
            <span>{{ row.workHours }}h</span>
          </template>
        </el-table-column>
        <el-table-column prop="completedOrders" label="完成订单" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paidDate" label="发放时间" width="120">
          <template #default="{ row }">
            <span>{{ row.paidDate ? formatDate(row.paidDate) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click.stop="showWageDetail(row)">
              查看详情
            </el-button>
            <el-button 
              v-if="row.status === 'paid'" 
              type="text" 
              size="small" 
              @click.stop="downloadWageSlip(row)"
            >
              下载工资条
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 工资详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="工资详情"
      width="800px"
      :before-close="handleDetailClose"
    >
      <div v-if="selectedWage" class="wage-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>工资月份：</label>
                <span>{{ formatMonth(selectedWage.month) }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>工作时长：</label>
                <span>{{ selectedWage.workHours }}小时</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>完成订单：</label>
                <span>{{ selectedWage.completedOrders }}个</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>工资状态：</label>
                <el-tag :type="getStatusType(selectedWage.status)">
                  {{ getStatusText(selectedWage.status) }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 工资构成 -->
        <div class="detail-section">
          <h3>工资构成</h3>
          <el-table :data="wageBreakdown" border>
            <el-table-column prop="item" label="项目" width="200" />
            <el-table-column prop="amount" label="金额" width="150">
              <template #default="{ row }">
                <span :class="{ 'deduction-amount': row.amount < 0 }">
                  {{ row.amount >= 0 ? '¥' : '-¥' }}{{ Math.abs(row.amount).toLocaleString() }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
          
          <div class="total-summary">
            <el-row>
              <el-col :span="12">
                <div class="summary-item">
                  <label>应发工资：</label>
                  <span class="gross-amount">¥{{ (selectedWage.basicSalary + selectedWage.overtimePay + selectedWage.bonus).toLocaleString() }}</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="summary-item">
                  <label>扣款合计：</label>
                  <span class="deduction-amount">-¥{{ selectedWage.deduction.toLocaleString() }}</span>
                </div>
              </el-col>
              <el-col :span="24">
                <div class="summary-item total">
                  <label>实发工资：</label>
                  <span class="total-amount">¥{{ selectedWage.totalAmount.toLocaleString() }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 订单明细 -->
        <div class="detail-section">
          <h3>订单明细</h3>
          <el-table :data="selectedWage.orderDetails" border max-height="300">
            <el-table-column prop="orderId" label="订单号" width="120" />
            <el-table-column prop="customerName" label="客户" width="100" />
            <el-table-column prop="serviceName" label="服务项目" width="150" />
            <el-table-column prop="completedDate" label="完成时间" width="120">
              <template #default="{ row }">
                <span>{{ formatDate(row.completedDate) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="workHours" label="工时" width="80">
              <template #default="{ row }">
                <span>{{ row.workHours }}h</span>
              </template>
            </el-table-column>
            <el-table-column prop="commission" label="提成" width="100">
              <template #default="{ row }">
                <span>¥{{ row.commission.toLocaleString() }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button 
            v-if="selectedWage && selectedWage.status === 'paid'" 
            type="primary" 
            @click="downloadWageSlip(selectedWage)"
          >
            下载工资条
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Money, TrendCharts, Clock, Star, Download, Refresh } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const wageRecords = ref([])
const dateRange = ref([])
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

// 对话框相关
const detailDialogVisible = ref(false)
const selectedWage = ref(null)

// 统计数据
const currentMonthWage = ref(8500)
const totalEarnings = ref(125000)
const currentMonthHours = ref(168)
const currentMonthBonus = ref(1200)

// 计算属性
const filteredWageRecords = computed(() => {
  let filtered = wageRecords.value

  // 日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [startMonth, endMonth] = dateRange.value
    filtered = filtered.filter(record => {
      return record.month >= startMonth && record.month <= endMonth
    })
  }

  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(record => record.status === statusFilter.value)
  }

  totalRecords.value = filtered.length
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const wageBreakdown = computed(() => {
  if (!selectedWage.value) return []
  
  return [
    { item: '基本工资', amount: selectedWage.value.basicSalary, description: '月度基本工资' },
    { item: '加班费', amount: selectedWage.value.overtimePay, description: '超时工作补贴' },
    { item: '绩效奖金', amount: selectedWage.value.bonus, description: '根据工作表现发放' },
    { item: '社保扣款', amount: -selectedWage.value.deduction, description: '个人承担部分' }
  ]
})

// 方法
const fetchWageRecords = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    wageRecords.value = [
      {
        id: 1,
        month: '2024-01',
        basicSalary: 6000,
        overtimePay: 1200,
        bonus: 800,
        deduction: 500,
        totalAmount: 7500,
        workHours: 180,
        completedOrders: 25,
        status: 'paid',
        paidDate: '2024-02-05',
        orderDetails: [
          { orderId: 'ORD001', customerName: '张三', serviceName: '发动机维修', completedDate: '2024-01-15', workHours: 8, commission: 200 },
          { orderId: 'ORD002', customerName: '李四', serviceName: '刹车系统检修', completedDate: '2024-01-18', workHours: 4, commission: 120 }
        ]
      },
      {
        id: 2,
        month: '2024-02',
        basicSalary: 6000,
        overtimePay: 1500,
        bonus: 1000,
        deduction: 500,
        totalAmount: 8000,
        workHours: 190,
        completedOrders: 28,
        status: 'paid',
        paidDate: '2024-03-05',
        orderDetails: []
      },
      {
        id: 3,
        month: '2024-03',
        basicSalary: 6000,
        overtimePay: 1000,
        bonus: 1200,
        deduction: 500,
        totalAmount: 7700,
        workHours: 175,
        completedOrders: 30,
        status: 'paid',
        paidDate: '2024-04-05',
        orderDetails: []
      },
      {
        id: 4,
        month: '2024-04',
        basicSalary: 6000,
        overtimePay: 1300,
        bonus: 1200,
        deduction: 500,
        totalAmount: 8000,
        workHours: 185,
        completedOrders: 32,
        status: 'processing',
        paidDate: null,
        orderDetails: []
      }
    ]
  } catch (error) {
    ElMessage.error('获取工资记录失败')
    console.error('Error fetching wage records:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchWageRecords()
}

const handleDateRangeChange = () => {
  currentPage.value = 1
}

const handleFilterChange = () => {
  currentPage.value = 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const showWageDetail = (row) => {
  selectedWage.value = row
  detailDialogVisible.value = true
}

const handleDetailClose = () => {
  detailDialogVisible.value = false
  selectedWage.value = null
}

const exportWageData = async () => {
  try {
    ElMessage.success('工资数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const downloadWageSlip = async (wage) => {
  try {
    ElMessage.success(`${formatMonth(wage.month)}工资条下载成功`)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 工具方法
const formatMonth = (month) => {
  const [year, monthNum] = month.split('-')
  return `${year}年${monthNum}月`
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const statusMap = {
    'paid': 'success',
    'pending': 'warning',
    'processing': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'paid': '已发放',
    'pending': '待发放',
    'processing': '处理中'
  }
  return statusMap[status] || '未知'
}

// 生命周期
onMounted(() => {
  fetchWageRecords()
})
</script>

<style scoped>
.wages-container {
  padding: 20px;
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.deduction-amount {
  color: #f56c6c;
}

.total-amount {
  color: #67c23a;
  font-weight: 600;
}

.wage-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.detail-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.total-summary {
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.summary-item.total {
  border-top: 1px solid #e4e7ed;
  padding-top: 8px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: 600;
}

.gross-amount {
  color: #409eff;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 