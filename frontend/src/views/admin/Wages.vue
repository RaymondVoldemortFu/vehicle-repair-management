<template>
  <div class="wages-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>工资管理</h1>
        <p class="page-description">管理工人工资计算、发放记录和提成统计</p>
      </div>
      <div class="header-right">
        <el-button @click="showCalculateDialog = true">
          <el-icon><Calculator /></el-icon>
          工资计算
        </el-button>
        <el-button @click="showBatchPayDialog = true">
          <el-icon><CreditCard /></el-icon>
          批量发放
        </el-button>
        <el-button type="primary" @click="showPayDialog = true">
          <el-icon><Money /></el-icon>
          发放工资
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="5">
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
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="发放状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待发放" value="pending" />
            <el-option label="已发放" value="paid" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-date-picker
            v-model="searchForm.month"
            type="month"
            placeholder="选择月份"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-input-number
            v-model="searchForm.minAmount"
            placeholder="最低金额"
            :min="0"
            :precision="2"
            style="width: 100%"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="3">
          <el-switch
            v-model="searchForm.showOvertime"
            active-text="含加班费"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="exportWages">导出</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.totalAmount.toFixed(0) }}</div>
            <div class="stat-label">本月总工资</div>
          </div>
          <el-icon class="stat-icon"><Money /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.pendingCount }}</div>
            <div class="stat-label">待发放人数</div>
          </div>
          <el-icon class="stat-icon pending"><Clock /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.avgWage.toFixed(0) }}</div>
            <div class="stat-label">平均工资</div>
          </div>
          <el-icon class="stat-icon avg"><TrendCharts /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.totalBonus.toFixed(0) }}</div>
            <div class="stat-label">本月提成</div>
          </div>
          <el-icon class="stat-icon bonus"><Star /></el-icon>
        </el-card>
      </el-col>
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
        <el-table-column prop="worker" label="工人信息" width="150">
          <template #default="{ row }">
            <div class="worker-info">
              <el-avatar :size="30" :src="row.worker.avatar">
                {{ row.worker.name.charAt(0) }}
              </el-avatar>
              <div class="worker-details">
                <div class="worker-name">{{ row.worker.name }}</div>
                <div class="worker-id">{{ row.worker.workerId }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="工资期间" width="120" />
        <el-table-column prop="baseSalary" label="基础工资" width="100">
          <template #default="{ row }">
            ¥{{ row.baseSalary.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="workDays" label="工作天数" width="100" />
        <el-table-column prop="overtimeHours" label="加班时长" width="100">
          <template #default="{ row }">
            {{ row.overtimeHours }}h
          </template>
        </el-table-column>
        <el-table-column prop="overtimePay" label="加班费" width="100">
          <template #default="{ row }">
            ¥{{ row.overtimePay.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="提成" width="100">
          <template #default="{ row }">
            ¥{{ row.commission.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="100">
          <template #default="{ row }">
            ¥{{ row.bonus.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="deductions" label="扣款" width="100">
          <template #default="{ row }">
            <span class="deduction-text">-¥{{ row.deductions.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalAmount" label="实发工资" width="120">
          <template #default="{ row }">
            <span class="total-amount">¥{{ row.totalAmount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payDate" label="发放日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewWage(row)">详情</el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              size="small" 
              type="primary" 
              @click="payWage(row)"
            >
              发放
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`recalculate-${row.id}`">重新计算</el-dropdown-item>
                  <el-dropdown-item :command="`adjust-${row.id}`">调整工资</el-dropdown-item>
                  <el-dropdown-item :command="`slip-${row.id}`">工资条</el-dropdown-item>
                  <el-dropdown-item :command="`history-${row.id}`" divided>历史记录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
    <el-dialog v-model="showDetailDialog" title="工资详情" width="800px">
      <div v-if="selectedWage" class="wage-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="工人姓名">{{ selectedWage.worker.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ selectedWage.worker.workerId }}</el-descriptions-item>
          <el-descriptions-item label="工资期间">{{ selectedWage.period }}</el-descriptions-item>
          <el-descriptions-item label="发放状态">
            <el-tag :type="getStatusTagType(selectedWage.status)">
              {{ getStatusName(selectedWage.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="基础工资">¥{{ selectedWage.baseSalary.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="工作天数">{{ selectedWage.workDays }}天</el-descriptions-item>
          <el-descriptions-item label="加班时长">{{ selectedWage.overtimeHours }}小时</el-descriptions-item>
          <el-descriptions-item label="加班费">¥{{ selectedWage.overtimePay.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="提成">¥{{ selectedWage.commission.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="奖金">¥{{ selectedWage.bonus.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="扣款">¥{{ selectedWage.deductions.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="实发工资">
            <span class="total-amount">¥{{ selectedWage.totalAmount.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">{{ selectedWage.payDate || '未发放' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedWage.notes || '无' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 工作明细 -->
        <el-divider>工作明细</el-divider>
        <el-table :data="selectedWage.workDetails" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="orderCount" label="完成订单" width="100" />
          <el-table-column prop="workHours" label="工作时长" width="100">
            <template #default="{ row }">
              {{ row.workHours }}h
            </template>
          </el-table-column>
          <el-table-column prop="overtimeHours" label="加班时长" width="100">
            <template #default="{ row }">
              {{ row.overtimeHours }}h
            </template>
          </el-table-column>
          <el-table-column prop="commission" label="当日提成" width="100">
            <template #default="{ row }">
              ¥{{ row.commission.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="rating" label="评分" width="120">
            <template #default="{ row }">
              <el-rate v-model="row.rating" disabled show-score />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 发放工资对话框 -->
    <el-dialog v-model="showPayDialog" title="发放工资" width="600px">
      <el-form
        ref="payFormRef"
        :model="payForm"
        :rules="payFormRules"
        label-width="100px"
      >
        <el-form-item label="选择工人" prop="workerId">
          <el-select v-model="payForm.workerId" placeholder="选择工人" style="width: 100%">
            <el-option
              v-for="worker in workers"
              :key="worker.id"
              :label="`${worker.name} (${worker.workerId})`"
              :value="worker.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工资期间" prop="period">
          <el-date-picker
            v-model="payForm.period"
            type="month"
            placeholder="选择月份"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="发放金额" prop="amount">
          <el-input-number
            v-model="payForm.amount"
            :min="0"
            :precision="2"
            placeholder="请输入发放金额"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="发放方式" prop="method">
          <el-select v-model="payForm.method" placeholder="选择发放方式" style="width: 100%">
            <el-option label="银行转账" value="bank" />
            <el-option label="现金发放" value="cash" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="payForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPayDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPay" :loading="saving">确认发放</el-button>
      </template>
    </el-dialog>

    <!-- 工资计算对话框 -->
    <el-dialog v-model="showCalculateDialog" title="工资计算" width="800px">
      <div class="calculate-form">
        <el-form :model="calculateForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="计算月份">
                <el-date-picker
                  v-model="calculateForm.month"
                  type="month"
                  placeholder="选择月份"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="计算范围">
                <el-select v-model="calculateForm.scope" placeholder="选择范围" style="width: 100%">
                  <el-option label="全部工人" value="all" />
                  <el-option label="指定工人" value="specific" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item v-if="calculateForm.scope === 'specific'" label="选择工人">
            <el-select
              v-model="calculateForm.workerIds"
              multiple
              placeholder="选择工人"
              style="width: 100%"
            >
              <el-option
                v-for="worker in workers"
                :key="worker.id"
                :label="`${worker.name} (${worker.workerId})`"
                :value="worker.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <!-- 计算结果 -->
        <div v-if="calculateResult.length" class="calculate-result">
          <el-divider>计算结果</el-divider>
          <el-table :data="calculateResult" style="width: 100%">
            <el-table-column prop="workerName" label="工人姓名" />
            <el-table-column prop="baseSalary" label="基础工资">
              <template #default="{ row }">
                ¥{{ row.baseSalary.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="commission" label="提成">
              <template #default="{ row }">
                ¥{{ row.commission.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="overtimePay" label="加班费">
              <template #default="{ row }">
                ¥{{ row.overtimePay.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="totalAmount" label="应发工资">
              <template #default="{ row }">
                <span class="total-amount">¥{{ row.totalAmount.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCalculateDialog = false">取消</el-button>
        <el-button @click="calculateWages" :loading="calculating">计算工资</el-button>
        <el-button 
          v-if="calculateResult.length" 
          type="primary" 
          @click="saveCalculateResult"
          :loading="saving"
        >
          保存结果
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Calculator, CreditCard, Money, Clock, TrendCharts, Star, 
  ArrowDown 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const calculating = ref(false)
const showDetailDialog = ref(false)
const showPayDialog = ref(false)
const showCalculateDialog = ref(false)
const showBatchPayDialog = ref(false)
const selectedWage = ref(null)
const selectedWages = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  month: null,
  minAmount: null,
  showOvertime: false
})

// 发放表单
const payForm = reactive({
  workerId: '',
  period: null,
  amount: 0,
  method: '',
  notes: ''
})

// 计算表单
const calculateForm = reactive({
  month: null,
  scope: 'all',
  workerIds: []
})

// 表单验证规则
const payFormRules = {
  workerId: [{ required: true, message: '请选择工人', trigger: 'change' }],
  period: [{ required: true, message: '请选择工资期间', trigger: 'change' }],
  amount: [{ required: true, message: '请输入发放金额', trigger: 'blur' }],
  method: [{ required: true, message: '请选择发放方式', trigger: 'change' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 数据
const wages = ref([])
const workers = ref([])
const calculateResult = ref([])

// 统计数据
const stats = reactive({
  totalAmount: 0,
  pendingCount: 0,
  avgWage: 0,
  totalBonus: 0
})

// 表单引用
const payFormRef = ref()

// 方法
const fetchWages = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    wages.value = [
      {
        id: 1,
        worker: {
          id: 1,
          name: '张师傅',
          workerId: 'W001',
          avatar: ''
        },
        period: '2024-01',
        baseSalary: 8000.00,
        workDays: 22,
        overtimeHours: 15,
        overtimePay: 450.00,
        commission: 1200.00,
        bonus: 500.00,
        deductions: 200.00,
        totalAmount: 9950.00,
        status: 'paid',
        payDate: '2024-02-01',
        notes: '表现优秀，额外奖金500元',
        workDetails: [
          {
            date: '2024-01-01',
            orderCount: 3,
            workHours: 8,
            overtimeHours: 2,
            commission: 150.00,
            rating: 4.8
          }
        ]
      },
      {
        id: 2,
        worker: {
          id: 2,
          name: '李师傅',
          workerId: 'W002',
          avatar: ''
        },
        period: '2024-01',
        baseSalary: 9500.00,
        workDays: 20,
        overtimeHours: 8,
        overtimePay: 240.00,
        commission: 1800.00,
        bonus: 0.00,
        deductions: 0.00,
        totalAmount: 11540.00,
        status: 'pending',
        payDate: null,
        notes: '',
        workDetails: []
      }
    ]
    
    // 更新统计数据
    stats.totalAmount = wages.value.reduce((sum, w) => sum + w.totalAmount, 0)
    stats.pendingCount = wages.value.filter(w => w.status === 'pending').length
    stats.avgWage = wages.value.length > 0 ? stats.totalAmount / wages.value.length : 0
    stats.totalBonus = wages.value.reduce((sum, w) => sum + w.bonus + w.commission, 0)
    
    pagination.total = wages.value.length
  } catch (error) {
    ElMessage.error('获取工资列表失败')
  } finally {
    loading.value = false
  }
}

const fetchWorkers = async () => {
  try {
    // 模拟数据
    workers.value = [
      { id: 1, name: '张师傅', workerId: 'W001' },
      { id: 2, name: '李师傅', workerId: 'W002' },
      { id: 3, name: '王师傅', workerId: 'W003' }
    ]
  } catch (error) {
    ElMessage.error('获取工人列表失败')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  // 在实际应用中，这里会调用API进行搜索
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    month: null,
    minAmount: null,
    showOvertime: false
  })
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
  Object.assign(payForm, {
    workerId: wage.worker.id,
    period: new Date(wage.period),
    amount: wage.totalAmount,
    method: '',
    notes: ''
  })
  showPayDialog.value = true
}

const submitPay = async () => {
  if (!payFormRef.value) return
  
  try {
    await payFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('工资发放成功')
    showPayDialog.value = false
    await fetchWages()
  } catch (error) {
    console.error('发放失败:', error)
  } finally {
    saving.value = false
  }
}

const calculateWages = async () => {
  calculating.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟计算结果
    calculateResult.value = [
      {
        workerId: 1,
        workerName: '张师傅',
        baseSalary: 8000.00,
        commission: 1200.00,
        overtimePay: 450.00,
        totalAmount: 9650.00
      },
      {
        workerId: 2,
        workerName: '李师傅',
        baseSalary: 9500.00,
        commission: 1800.00,
        overtimePay: 240.00,
        totalAmount: 11540.00
      }
    ]
    
    ElMessage.success('工资计算完成')
  } catch (error) {
    ElMessage.error('计算失败')
  } finally {
    calculating.value = false
  }
}

const saveCalculateResult = async () => {
  saving.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('计算结果保存成功')
    showCalculateDialog.value = false
    calculateResult.value = []
    await fetchWages()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const wage = wages.value.find(w => w.id === parseInt(id))
  
  switch (action) {
    case 'recalculate':
      try {
        await ElMessageBox.confirm(
          `确定要重新计算 ${wage.worker.name} 的工资吗？`,
          '确认重新计算',
          { type: 'warning' }
        )
        
        ElMessage.success('重新计算成功')
        await fetchWages()
      } catch {
        // 用户取消
      }
      break
    case 'adjust':
      try {
        const { value } = await ElMessageBox.prompt('请输入调整后的金额', '调整工资', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: wage.totalAmount.toString(),
          inputType: 'number'
        })
        
        ElMessage.success('工资调整成功')
        await fetchWages()
      } catch {
        // 用户取消
      }
      break
    case 'slip':
      ElMessage.info('工资条生成功能开发中')
      break
    case 'history':
      ElMessage.info('历史记录查看功能开发中')
      break
  }
}

const exportWages = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchWages()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchWages()
}

// 辅助方法
const getStatusName = (status) => {
  const statusMap = {
    pending: '待发放',
    paid: '已发放',
    confirmed: '已确认'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'warning',
    paid: 'success',
    confirmed: 'primary'
  }
  return typeMap[status] || ''
}

const getRowClassName = ({ row }) => {
  if (row.status === 'pending') {
    return 'pending-row'
  }
  return ''
}

// 生命周期
onMounted(() => {
  fetchWorkers()
  fetchWages()
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

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  color: #e4e7ed;
  z-index: 1;
}

.stat-icon.pending {
  color: #e6a23c;
}

.stat-icon.avg {
  color: #409eff;
}

.stat-icon.bonus {
  color: #f56c6c;
}

.table-card {
  margin-bottom: 20px;
}

.worker-info {
  display: flex;
  align-items: center;
  gap: 8px;
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

.calculate-form {
  padding: 20px 0;
}

.calculate-result {
  margin-top: 20px;
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