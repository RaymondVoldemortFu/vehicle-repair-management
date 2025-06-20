<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索订单号"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchForm.status" placeholder="订单状态" style="width: 120px" clearable>
          <el-option label="待处理" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      <div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          创建订单
        </el-button>
      </div>
    </div>

    <div class="card-container">
      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="order_number" label="订单号" width="150" />
        <el-table-column prop="vehicle_info" label="车辆信息" width="180">
          <template #default="{ row }">
            {{ row.vehicle?.license_plate }} - {{ row.vehicle?.manufacturer }} {{ row.vehicle?.model }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="故障描述" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="维修技师" width="120">
          <template #default="{ row }">
            <span v-if="row.assigned_workers && row.assigned_workers.length > 0">
              {{ row.assigned_workers.map(w => w.worker.name).join(', ') }}
            </span>
            <span v-else>待分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_cost" label="总费用" width="100">
          <template #default="{ row }">
            <span v-if="row.status === 'completed' && row.total_cost">¥{{ parseFloat(row.total_cost).toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              v-if="row.status === 'completed'" 
              type="success" 
              size="small" 
              @click="goToFeedbackPage"
            >
              评价
            </el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              type="danger" 
              size="small" 
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加分页组件 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center"
      />
    </div>

    <!-- 创建订单对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建维修订单" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="选择车辆" prop="vehicle_id">
          <el-select v-model="createForm.vehicle_id" style="width: 100%" placeholder="请选择车辆">
            <el-option 
              v-for="vehicle in vehicles" 
              :key="vehicle.id" 
              :label="`${vehicle.license_plate} - ${vehicle.manufacturer} ${vehicle.model}`"
              :value="vehicle.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="故障描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="4" 
            placeholder="请详细描述车辆故障情况" 
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="createForm.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="high">高</el-radio>
            <el-radio label="urgent">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="期望时间" prop="expected_completion_date">
          <el-date-picker
            v-model="createForm.expected_completion_date"
            type="date"
            placeholder="选择期望完成日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="createForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateSubmit">
          提交订单
        </el-button>
      </template>
    </el-dialog>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="车辆信息">
          {{ currentOrder.vehicle?.license_plate }} - {{ currentOrder.vehicle?.manufacturer }} {{ currentOrder.vehicle?.model }}
        </el-descriptions-item>
        <el-descriptions-item label="维修工人">
          <span v-if="currentOrder.assigned_workers && currentOrder.assigned_workers.length > 0">
            {{ currentOrder.assigned_workers.map(w => w.worker.name).join(', ') }}
          </span>
          <span v-else>待分配</span>
        </el-descriptions-item>
        <el-descriptions-item label="工时费" v-if="currentOrder.status === 'completed'">
          {{ currentOrder.total_labor_cost ? `¥${parseFloat(currentOrder.total_labor_cost).toFixed(2)}` : '¥0.00' }}
        </el-descriptions-item>
        <el-descriptions-item label="材料费" v-if="currentOrder.status === 'completed'">
          {{ currentOrder.total_material_cost ? `¥${parseFloat(currentOrder.total_material_cost).toFixed(2)}` : '¥0.00' }}
        </el-descriptions-item>
        <el-descriptions-item label="总费用" :span="currentOrder.status !== 'completed' ? 2 : 1">
          <span v-if="currentOrder.status === 'completed'">
            <strong>{{ currentOrder.total_cost ? `¥${parseFloat(currentOrder.total_cost).toFixed(2)}` : '¥0.00' }}</strong>
          </span>
          <span v-else>维修完成后计算</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">
          {{ currentOrder.actual_completion_time ? formatDate(currentOrder.actual_completion_time) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>故障描述</h4>
        <p>{{ currentOrder.description }}</p>
      </div>

      <div v-if="currentOrder.internal_notes" style="margin-top: 20px;">
        <h4>维修记录</h4>
        <p style="white-space: pre-wrap;">{{ currentOrder.internal_notes }}</p>
      </div>
    </el-dialog>

    <!-- 评价对话框 -->
    <el-dialog v-model="feedbackDialogVisible" title="服务评价" width="500px">
      <el-form :model="feedbackForm" label-width="80px">
        <el-form-item label="评分">
          <el-rate v-model="feedbackForm.rating" show-text />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input 
            v-model="feedbackForm.content" 
            type="textarea" 
            :rows="4" 
            placeholder="请分享您的使用体验" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feedbackDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleFeedbackSubmit">
          提交评价
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'

const loading = ref(false)
const submitting = ref(false)
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const feedbackDialogVisible = ref(false)
const tableData = ref([])
const vehicles = ref([])
const currentOrder = ref({})
const router = useRouter()

const searchForm = reactive({
  keyword: '',
  status: ''
})

const createForm = reactive({
  vehicle_id: '',
  description: '',
  priority: 'medium',
  expected_completion_date: '',
  contact_phone: ''
})

const feedbackForm = reactive({
  order_id: '',
  rating: 5,
  content: ''
})

const createFormRef = ref()

const createRules = {
  vehicle_id: [
    { required: true, message: '请选择车辆', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请描述故障情况', trigger: 'blur' },
    { min: 10, message: '故障描述至少10个字符', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ]
}

// 添加分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchForm.keyword,
      status: searchForm.status,
      page: pagination.page,
      size: pagination.size
    }
    const response = await request.get('/repair-orders/my-orders', { params })
    // 正确处理分页响应数据
    tableData.value = response.items || []
    pagination.total = response.total || 0
    pagination.page = response.page || 1
    pagination.size = response.size || 20
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取车辆列表
const fetchVehicles = async () => {
  try {
    const response = await request.get('/vehicles/my-vehicles')
    vehicles.value = response || []
  } catch (error) {
    console.error('获取车辆列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1  // 重置到第一页
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: ''
  })
  fetchData()
}

// 创建订单
const handleAdd = () => {
  if (vehicles.value.length === 0) {
    ElMessage.warning('请先添加车辆信息')
    return
  }
  Object.assign(createForm, {
    vehicle_id: '',
    description: '',
    priority: 'medium',
    expected_completion_date: '',
    contact_phone: ''
  })
  createDialogVisible.value = true
}

// 提交创建订单
const handleCreateSubmit = async () => {
  const valid = await createFormRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    await request.post('/repair-orders/', createForm)
    ElMessage.success('订单创建成功')
    createDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('创建订单失败:', error)
  } finally {
    submitting.value = false
  }
}

// 查看详情
const handleView = async (row) => {
  try {
    const response = await request.get(`/repair-orders/${row.id}`)
    currentOrder.value = response
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取订单详情失败:', error)
    ElMessage.error('获取订单详情失败')
  }
}

// 取消订单
const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消这个订单吗？',
      '提示',
      { type: 'warning' }
    )
    
    await request.put(`/repair-orders/${row.id}/cancel`)
    ElMessage.success('订单已取消')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}

// 评价服务
const handleFeedback = (row) => {
  Object.assign(feedbackForm, {
    order_id: row.id,
    rating: 5,
    content: ''
  })
  feedbackDialogVisible.value = true
}

// 提交评价
const handleFeedbackSubmit = async () => {
  submitting.value = true
  try {
    await request.post('/feedback/', feedbackForm)
    ElMessage.success('评价提交成功')
    feedbackDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('提交评价失败:', error)
  } finally {
    submitting.value = false
  }
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

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 添加分页处理函数
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

const goToFeedbackPage = () => {
  router.push('/user/feedback')
}

onMounted(() => {
  fetchData()
  fetchVehicles()
})
</script>

<style lang="scss" scoped>
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
</style> 