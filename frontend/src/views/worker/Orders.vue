<template>
  <div class="worker-orders-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>我的订单</h1>
        <p class="page-description">管理接收的维修订单和工作进度</p>
      </div>
      <div class="header-right">
        <el-button @click="refreshOrders">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showAvailableOrders = true">
          <el-icon><Plus /></el-icon>
          接新订单
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索订单号或车辆信息"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="订单状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待开始" value="assigned" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="待确认" value="pending_confirm" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.priority" placeholder="优先级" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="普通" value="normal" />
            <el-option label="低" value="low" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="5">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总订单数</div>
          </div>
          <el-icon class="stat-icon"><List /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.inProgress }}</div>
            <div class="stat-label">进行中</div>
          </div>
          <el-icon class="stat-icon progress"><Loading /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <el-icon class="stat-icon completed"><CircleCheck /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.avgRating.toFixed(1) }}</div>
            <div class="stat-label">平均评分</div>
          </div>
          <el-icon class="stat-icon rating"><Star /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="orders"
        style="width: 100%"
        :row-class-name="getRowClassName"
      >
        <el-table-column prop="orderNumber" label="订单号" width="140" />
        <el-table-column prop="customer" label="客户信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <div class="customer-name">{{ row.customer.name }}</div>
              <div class="customer-phone">{{ row.customer.phone }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vehicle" label="车辆信息" width="180">
          <template #default="{ row }">
            <div class="vehicle-info">
              <div class="vehicle-model">{{ row.vehicle.manufacturer }} {{ row.vehicle.model }}</div>
              <div class="vehicle-plate">{{ row.vehicle.plateNumber }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="serviceType" label="服务类型" width="120" />
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ getPriorityName(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedTime" label="预计时长" width="100">
          <template #default="{ row }">
            {{ row.estimatedTime }}h
          </template>
        </el-table-column>
        <el-table-column prop="scheduledTime" label="预约时间" width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrder(row)">详情</el-button>
            <el-button 
              v-if="row.status === 'assigned'" 
              size="small" 
              type="primary" 
              @click="startOrder(row)"
            >
              开始
            </el-button>
            <el-button 
              v-if="row.status === 'in_progress'" 
              size="small" 
              type="success" 
              @click="completeOrder(row)"
            >
              完成
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`progress-${row.id}`">更新进度</el-dropdown-item>
                  <el-dropdown-item :command="`materials-${row.id}`">材料使用</el-dropdown-item>
                  <el-dropdown-item :command="`photos-${row.id}`">上传照片</el-dropdown-item>
                  <el-dropdown-item :command="`contact-${row.id}`" divided>联系客户</el-dropdown-item>
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
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="订单详情" width="900px">
      <div v-if="selectedOrder" class="order-detail">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="订单号">{{ selectedOrder.orderNumber }}</el-descriptions-item>
              <el-descriptions-item label="订单状态">
                <el-tag :type="getStatusTagType(selectedOrder.status)">
                  {{ getStatusName(selectedOrder.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="客户姓名">{{ selectedOrder.customer.name }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ selectedOrder.customer.phone }}</el-descriptions-item>
              <el-descriptions-item label="车辆品牌">{{ selectedOrder.vehicle.manufacturer }}</el-descriptions-item>
              <el-descriptions-item label="车辆型号">{{ selectedOrder.vehicle.model }}</el-descriptions-item>
              <el-descriptions-item label="车牌号">{{ selectedOrder.vehicle.plateNumber }}</el-descriptions-item>
              <el-descriptions-item label="服务类型">{{ selectedOrder.serviceType }}</el-descriptions-item>
              <el-descriptions-item label="预约时间">{{ selectedOrder.scheduledTime }}</el-descriptions-item>
              <el-descriptions-item label="预计时长">{{ selectedOrder.estimatedTime }}小时</el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityTagType(selectedOrder.priority)">
                  {{ getPriorityName(selectedOrder.priority) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ selectedOrder.createdAt }}</el-descriptions-item>
              <el-descriptions-item label="问题描述" :span="2">
                {{ selectedOrder.description }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="8">
            <div class="order-progress">
              <h4>工作进度</h4>
              <el-progress 
                :percentage="selectedOrder.progress" 
                :status="selectedOrder.status === 'completed' ? 'success' : null"
              />
              <div class="progress-info">
                <span>{{ selectedOrder.progress }}% 完成</span>
                <span v-if="selectedOrder.estimatedCompletion">
                  预计完成：{{ selectedOrder.estimatedCompletion }}
                </span>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 工作记录 -->
        <el-divider>工作记录</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in selectedOrder.workRecords"
            :key="index"
            :timestamp="record.timestamp"
            :type="getTimelineType(record.type)"
          >
            <div class="timeline-content">
              <div class="timeline-title">{{ record.title }}</div>
              <div class="timeline-description">{{ record.description }}</div>
              <div v-if="record.photos && record.photos.length" class="timeline-photos">
                <el-image
                  v-for="(photo, photoIndex) in record.photos"
                  :key="photoIndex"
                  :src="photo"
                  :preview-src-list="record.photos"
                  fit="cover"
                  style="width: 60px; height: 60px; margin-right: 8px"
                />
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>

        <!-- 使用材料 -->
        <el-divider>使用材料</el-divider>
        <el-table :data="selectedOrder.usedMaterials" style="width: 100%">
          <el-table-column prop="name" label="材料名称" />
          <el-table-column prop="quantity" label="使用数量" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="unitPrice" label="单价" width="100">
            <template #default="{ row }">
              ¥{{ row.unitPrice.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalPrice" label="小计" width="100">
            <template #default="{ row }">
              ¥{{ (row.quantity * row.unitPrice).toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 可接订单对话框 -->
    <el-dialog v-model="showAvailableOrders" title="可接订单" width="800px">
      <el-table :data="availableOrders" style="width: 100%">
        <el-table-column prop="orderNumber" label="订单号" width="140" />
        <el-table-column prop="serviceType" label="服务类型" width="120" />
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ getPriorityName(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedTime" label="预计时长" width="100">
          <template #default="{ row }">
            {{ row.estimatedTime }}h
          </template>
        </el-table-column>
        <el-table-column prop="scheduledTime" label="预约时间" width="150" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="acceptOrder(row)">接单</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 完成订单对话框 -->
    <el-dialog v-model="showCompleteDialog" title="完成订单" width="600px">
      <el-form
        ref="completeFormRef"
        :model="completeForm"
        :rules="completeFormRules"
        label-width="100px"
      >
        <el-form-item label="工作总结" prop="summary">
          <el-input
            v-model="completeForm.summary"
            type="textarea"
            :rows="4"
            placeholder="请输入工作总结"
          />
        </el-form-item>
        <el-form-item label="实际用时" prop="actualTime">
          <el-input-number
            v-model="completeForm.actualTime"
            :min="0.5"
            :step="0.5"
            :precision="1"
            placeholder="小时"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="完成照片">
          <el-upload
            v-model:file-list="completeForm.photos"
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="5"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="completeForm.notes"
            type="textarea"
            :rows="2"
            placeholder="其他备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCompleteDialog = false">取消</el-button>
        <el-button type="primary" @click="submitComplete" :loading="saving">确认完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Refresh, Plus, List, Loading, CircleCheck, Star, ArrowDown 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showDetailDialog = ref(false)
const showAvailableOrders = ref(false)
const showCompleteDialog = ref(false)
const selectedOrder = ref(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  priority: '',
  dateRange: null
})

// 完成表单
const completeForm = reactive({
  summary: '',
  actualTime: 0,
  photos: [],
  notes: ''
})

// 表单验证规则
const completeFormRules = {
  summary: [{ required: true, message: '请输入工作总结', trigger: 'blur' }],
  actualTime: [{ required: true, message: '请输入实际用时', trigger: 'blur' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 数据
const orders = ref([])
const availableOrders = ref([])

// 统计数据
const stats = reactive({
  total: 0,
  inProgress: 0,
  completed: 0,
  avgRating: 0
})

// 表单引用
const completeFormRef = ref()

// 方法
const fetchOrders = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    orders.value = [
      {
        id: 1,
        orderNumber: 'ORD20240115001',
        customer: {
          name: '张先生',
          phone: '13800138001'
        },
        vehicle: {
          manufacturer: '奥迪',
          model: 'A4L',
          plateNumber: '京A12345'
        },
        serviceType: '发动机维修',
        description: '发动机异响，怠速不稳，需要检查维修',
        priority: 'high',
        status: 'in_progress',
        estimatedTime: 4,
        scheduledTime: '2024-01-15 09:00',
        createdAt: '2024-01-14 16:30',
        progress: 60,
        estimatedCompletion: '2024-01-15 13:00',
        workRecords: [
          {
            timestamp: '2024-01-15 09:00',
            type: 'start',
            title: '开始维修',
            description: '接收订单，开始检查发动机状况'
          },
          {
            timestamp: '2024-01-15 10:30',
            type: 'progress',
            title: '问题诊断',
            description: '发现点火线圈故障，需要更换',
            photos: ['/images/engine1.jpg', '/images/engine2.jpg']
          }
        ],
        usedMaterials: [
          {
            name: '点火线圈',
            quantity: 1,
            unit: '个',
            unitPrice: 280.00
          }
        ]
      },
      {
        id: 2,
        orderNumber: 'ORD20240115002',
        customer: {
          name: '李女士',
          phone: '13800138002'
        },
        vehicle: {
          manufacturer: '宝马',
          model: 'X3',
          plateNumber: '京B67890'
        },
        serviceType: '刹车系统检修',
        description: '刹车片磨损严重，需要更换',
        priority: 'normal',
        status: 'assigned',
        estimatedTime: 2,
        scheduledTime: '2024-01-15 14:00',
        createdAt: '2024-01-14 18:20',
        progress: 0,
        workRecords: [],
        usedMaterials: []
      }
    ]
    
    // 更新统计数据
    stats.total = orders.value.length
    stats.inProgress = orders.value.filter(o => o.status === 'in_progress').length
    stats.completed = orders.value.filter(o => o.status === 'completed').length
    stats.avgRating = 4.8 // 模拟平均评分
    
    pagination.total = orders.value.length
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchAvailableOrders = async () => {
  try {
    // 模拟可接订单数据
    availableOrders.value = [
      {
        id: 3,
        orderNumber: 'ORD20240115003',
        serviceType: '轮胎更换',
        description: '前轮胎磨损严重，需要更换两条轮胎',
        priority: 'normal',
        estimatedTime: 1.5,
        scheduledTime: '2024-01-16 10:00'
      },
      {
        id: 4,
        orderNumber: 'ORD20240115004',
        serviceType: '电路检修',
        description: '车灯不亮，疑似电路故障',
        priority: 'urgent',
        estimatedTime: 3,
        scheduledTime: '2024-01-15 16:00'
      }
    ]
  } catch (error) {
    ElMessage.error('获取可接订单失败')
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
    priority: '',
    dateRange: null
  })
  handleSearch()
}

const refreshOrders = () => {
  fetchOrders()
  ElMessage.success('订单列表已刷新')
}

const viewOrder = (order) => {
  selectedOrder.value = order
  showDetailDialog.value = true
}

const startOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要开始处理订单 ${order.orderNumber} 吗？`,
      '确认开始',
      { type: 'info' }
    )
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    order.status = 'in_progress'
    order.progress = 10
    
    ElMessage.success('订单已开始处理')
    await fetchOrders()
  } catch {
    // 用户取消
  }
}

const completeOrder = (order) => {
  selectedOrder.value = order
  Object.assign(completeForm, {
    summary: '',
    actualTime: order.estimatedTime,
    photos: [],
    notes: ''
  })
  showCompleteDialog.value = true
}

const submitComplete = async () => {
  if (!completeFormRef.value) return
  
  try {
    await completeFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    selectedOrder.value.status = 'pending_confirm'
    selectedOrder.value.progress = 100
    
    ElMessage.success('订单已完成，等待客户确认')
    showCompleteDialog.value = false
    await fetchOrders()
  } catch (error) {
    console.error('完成订单失败:', error)
  } finally {
    saving.value = false
  }
}

const acceptOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要接收订单 ${order.orderNumber} 吗？`,
      '确认接单',
      { type: 'info' }
    )
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    ElMessage.success('接单成功')
    showAvailableOrders.value = false
    await fetchOrders()
    await fetchAvailableOrders()
  } catch {
    // 用户取消
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const order = orders.value.find(o => o.id === parseInt(id))
  
  switch (action) {
    case 'progress':
      try {
        const { value } = await ElMessageBox.prompt('请输入当前进度百分比', '更新进度', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: order.progress.toString(),
          inputType: 'number'
        })
        
        order.progress = Math.min(100, Math.max(0, parseInt(value)))
        ElMessage.success('进度更新成功')
      } catch {
        // 用户取消
      }
      break
    case 'materials':
      ElMessage.info('材料使用记录功能开发中')
      break
    case 'photos':
      ElMessage.info('照片上传功能开发中')
      break
    case 'contact':
      ElMessage.info(`客户联系方式：${order.customer.phone}`)
      break
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchOrders()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchOrders()
}

// 辅助方法
const getStatusName = (status) => {
  const statusMap = {
    assigned: '待开始',
    in_progress: '进行中',
    pending_confirm: '待确认',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    assigned: 'warning',
    in_progress: 'primary',
    pending_confirm: 'info',
    completed: 'success'
  }
  return typeMap[status] || ''
}

const getPriorityName = (priority) => {
  const priorityMap = {
    urgent: '紧急',
    high: '高',
    normal: '普通',
    low: '低'
  }
  return priorityMap[priority] || priority
}

const getPriorityTagType = (priority) => {
  const typeMap = {
    urgent: 'danger',
    high: 'warning',
    normal: '',
    low: 'info'
  }
  return typeMap[priority] || ''
}

const getTimelineType = (type) => {
  const typeMap = {
    start: 'primary',
    progress: 'warning',
    complete: 'success',
    issue: 'danger'
  }
  return typeMap[type] || 'primary'
}

const getRowClassName = ({ row }) => {
  if (row.priority === 'urgent') {
    return 'urgent-row'
  }
  if (row.status === 'in_progress') {
    return 'progress-row'
  }
  return ''
}

// 生命周期
onMounted(() => {
  fetchOrders()
  fetchAvailableOrders()
})
</script>

<style scoped>
.worker-orders-container {
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

.stat-icon.progress {
  color: #409eff;
}

.stat-icon.completed {
  color: #67c23a;
}

.stat-icon.rating {
  color: #f56c6c;
}

.table-card {
  margin-bottom: 20px;
}

.customer-info, .vehicle-info {
  display: flex;
  flex-direction: column;
}

.customer-name, .vehicle-model {
  font-weight: bold;
  font-size: 14px;
}

.customer-phone, .vehicle-plate {
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.order-detail {
  padding: 20px 0;
}

.order-progress {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.order-progress h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.timeline-content {
  padding: 10px 0;
}

.timeline-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.timeline-description {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.timeline-photos {
  margin-top: 8px;
}

:deep(.urgent-row) {
  background-color: #fef0f0;
}

:deep(.urgent-row:hover) {
  background-color: #fde2e2 !important;
}

:deep(.progress-row) {
  background-color: #f0f9ff;
}

:deep(.progress-row:hover) {
  background-color: #e1f5fe !important;
}

@media (max-width: 768px) {
  .worker-orders-container {
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