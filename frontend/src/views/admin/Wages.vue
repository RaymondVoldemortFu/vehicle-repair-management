<template>
  <div class="wages-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>工资管理</h1>
        <p class="page-description">管理工人工资计算、发放记录和提成统计</p>
      </div>
      <div class="header-right">
        <el-button @click="showCalculateDialog = true" disabled>
          <el-icon><DataAnalysis /></el-icon>
          工资计算
        </el-button>
        <el-button @click="showBatchPayDialog = true" disabled>
          <el-icon><CreditCard /></el-icon>
          批量发放
        </el-button>
        <el-button type="primary" @click="showPayDialog = true" disabled>
          <el-icon><Money /></el-icon>
          发放工资
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索工人姓名或工号"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="5">
          <el-select v-model="searchForm.status" placeholder="发放状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待发放" value="pending" />
            <el-option label="已发放" value="paid" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-date-picker
            v-model="searchForm.month"
            type="month"
            placeholder="选择月份"
            @change="handleSearch"
            style="width: 100%"
          />
        </el-col>
        <el-col :span="5">
          <el-input-number
            v-model="searchForm.minAmount"
            placeholder="最低实发金额"
            :min="0"
            :precision="2"
            style="width: 100%"
            @change="handleSearch"
            :controls="false"
          />
        </el-col>
        <el-col :span="3">
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 (暂无数据) -->
    <el-row :gutter="20" class="stats-row">
      <!-- 统计卡片内容暂时移除，等待后端接口 -->
    </el-row>

    <!-- 工资列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="wages"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :row-class-name="getRowClassName"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="worker" label="工人信息" width="180">
          <template #default="{ row }">
            <div class="worker-info">
              <el-avatar :size="40" :src="row.worker.avatar">
                {{ row.worker.name.charAt(0) }}
              </el-avatar>
              <div class="worker-details">
                <div class="worker-name">{{ row.worker.name }}</div>
                <div class="worker-id">{{ row.worker.worker_id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="工资期间" width="120" sortable />
        <el-table-column prop="base_salary" label="基础工资" width="110" sortable>
          <template #default="{ row }">
            ¥{{ row.base_salary }}
          </template>
        </el-table-column>
        <el-table-column prop="work_days" label="工作天数" width="100" sortable />
        <el-table-column prop="overtime_hours" label="加班时长(h)" width="120" sortable />
        <el-table-column prop="overtime_pay" label="加班费" width="110" sortable>
          <template #default="{ row }">
            ¥{{ row.overtime_pay }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="提成" width="110" sortable>
          <template #default="{ row }">
            ¥{{ row.commission }}
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="110" sortable>
          <template #default="{ row }">
            ¥{{ row.bonus }}
          </template>
        </el-table-column>
        <el-table-column prop="deductions" label="扣款" width="110" sortable>
          <template #default="{ row }">
            <span class="deduction-text">-¥{{ row.deductions }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="实发工资" width="120" sortable>
          <template #default="{ row }">
            <span class="total-amount">¥{{ row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" fixed="right" sortable>
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_date" label="发放日期" width="120" sortable />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewWage(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="primary"
              @click="payWage(row)"
              disabled
            >
              发放
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 工资详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="工资详情" width="600px">
      <div v-if="selectedWage" class="wage-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="工人姓名">{{ selectedWage.worker.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ selectedWage.worker.worker_id }}</el-descriptions-item>
          <el-descriptions-item label="工资期间">{{ selectedWage.period }}</el-descriptions-item>
          <el-descriptions-item label="发放状态">
            <el-tag :type="getStatusTagType(selectedWage.status)">
              {{ getStatusName(selectedWage.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="基础工资">¥{{ selectedWage.base_salary }}</el-descriptions-item>
          <el-descriptions-item label="工作天数">{{ selectedWage.work_days }}天</el-descriptions-item>
          <el-descriptions-item label="加班时长">{{ selectedWage.overtime_hours }}小时</el-descriptions-item>
          <el-descriptions-item label="加班费">¥{{ selectedWage.overtime_pay }}</el-descriptions-item>
          <el-descriptions-item label="提成">¥{{ selectedWage.commission }}</el-descriptions-item>
          <el-descriptions-item label="奖金">¥{{ selectedWage.bonus }}</el-descriptions-item>
          <el-descriptions-item label="扣款">¥{{ selectedWage.deductions }}</el-descriptions-item>
          <el-descriptions-item label="实发工资">
            <span class="total-amount">¥{{ selectedWage.total_amount }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">{{ selectedWage.pay_date || '未发放' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedWage.notes || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
       <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, DataAnalysis, CreditCard, Money } from '@element-plus/icons-vue'
import request from '@/utils/request'
import dayjs from 'dayjs'

const loading = ref(false)
const showDetailDialog = ref(false)
const selectedWage = ref(null)
const selectedWages = ref([])

const searchForm = reactive({
  keyword: '',
  status: '',
  month: null,
  minAmount: null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const wages = ref([])
const workers = ref([])

const fetchWages = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined,
      month: searchForm.month ? dayjs(searchForm.month).format('YYYY-MM') : undefined,
      min_amount: searchForm.minAmount
    }
    // 移除值为 undefined 的参数
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === null || params[key] === '') {
        delete params[key]
      }
    })
    
    const res = await request.get('/wages', { params })
    wages.value = res.data
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取工资列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 注意：此功能暂时保留，但在新版中可能需要专门的工人列表接口
const fetchWorkers = async () => {
  try {
    const res = await request.get('/wages/workers')
    workers.value = res
  } catch (error) {
    ElMessage.error('获取工人列表失败')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  fetchWages()
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.month = null
  searchForm.minAmount = null
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedWages.value = selection
}

const viewWage = (wage) => {
  selectedWage.value = wage
  showDetailDialog.value = true
}

const payWage = (wage) => {
  ElMessage.info('发放功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchWages()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchWages()
}

const getStatusName = (status) => {
  const statusMap = {
    pending: '待发放',
    paid: '已发放',
    confirmed: '已确认',
    disputed: '有争议'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'warning',
    paid: 'success',
    confirmed: 'primary',
    disputed: 'danger'
  }
  return typeMap[status] || ''
}

const getRowClassName = ({ row }) => {
  if (row.status === 'pending') {
    return 'pending-row'
  }
  return ''
}

onMounted(() => {
  fetchWages()
  fetchWorkers() // 获取工人列表用于筛选等
})
</script>

<style scoped>
.wages-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h1 {
  margin: 0;
  color: #303133;
}

.page-description {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.worker-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.worker-details {
  display: flex;
  flex-direction: column;
}

.worker-name {
  font-size: 14px;
  font-weight: bold;
}

.worker-id {
  font-size: 12px;
  color: #909399;
}

.deduction-text {
  color: #f56c6c;
}

.total-amount {
  font-weight: bold;
  color: #67c23a;
  font-size: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.wage-detail {
  padding: 20px 0;
}

:deep(.pending-row) {
  background-color: #fdf6ec;
}

:deep(.pending-row:hover) {
  background-color: #faecd8 !important;
}

@media (max-width: 768px) {
  .wages-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stats-row .el-col {
    margin-bottom: 15px;
  }
}
</style> 