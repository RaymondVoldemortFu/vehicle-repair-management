<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索订单号或车牌号"
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
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
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
        <el-table-column prop="user_name" label="用户" width="120" />
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
        <el-table-column label="维修工人" width="120">
           <template #default="{ row }">
            <span v-if="row.assigned_workers && row.assigned_workers.length > 0">
              {{ row.assigned_workers.map(w => w.worker.name).join(', ') }}
            </span>
            <span v-else>待分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_cost" label="总费用" width="100">
           <template #default="{ row }">
            <span v-if="row.status === 'completed' && row.total_cost > 0">¥{{ row.total_cost }}</span>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleAssign(row)">
              分配
            </el-button>
            <el-button type="success" size="small" @click="handleUpdateStatus(row)">
              状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: center"
      />
    </div>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="800px">
       <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentOrder.status)">
              {{ getStatusText(currentOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户姓名">{{ currentOrder.user?.name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentOrder.user?.phone }}</el-descriptions-item>
          <el-descriptions-item label="车辆信息" :span="2">
            {{ currentOrder.vehicle?.license_plate }} - {{ currentOrder.vehicle?.manufacturer }} {{ currentOrder.vehicle?.model }}
          </el-descriptions-item>
           <el-descriptions-item label="维修工人" :span="2">
            <span v-if="currentOrder.assigned_workers && currentOrder.assigned_workers.length > 0">
                {{ currentOrder.assigned_workers.map(w => w.worker.name).join(', ') }}
            </span>
            <span v-else>待分配</span>
          </el-descriptions-item>
          <el-descriptions-item label="工时费" v-if="currentOrder.status === 'completed'">
            {{ currentOrder.total_labor_cost ? `¥${currentOrder.total_labor_cost}` : '¥0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="材料费" v-if="currentOrder.status === 'completed'">
            {{ currentOrder.total_material_cost ? `¥${currentOrder.total_material_cost}` : '¥0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="总费用" :span="currentOrder.status !== 'completed' ? 2 : 1">
            <span v-if="currentOrder.status === 'completed'">
              <strong>¥{{ currentOrder.total_cost || '0.00' }}</strong>
            </span>
            <span v-else>维修完成后计算</span>
          </el-descripti_ons-item>
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
          <h4>维修记录/备注</h4>
          <p style="white-space: pre-wrap;">{{ currentOrder.internal_notes }}</p>
        </div>

        <div v-if="currentOrder.status === 'completed' && currentOrder.used_materials && currentOrder.used_materials.length > 0" style="margin-top: 20px;">
          <h4>使用材料清单</h4>
          <el-table :data="currentOrder.used_materials" stripe border size="small">
            <el-table-column prop="name" label="材料名称" />
            <el-table-column prop="price" label="单价">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" />
            <el-table-column label="小计">
              <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const detailDialogVisible = ref(false)
const currentOrder = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

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
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    const response = await request.get('/repair-orders/', { params })
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: ''
  })
  handleSearch()
}

// 查看详情
const handleView = async (row) => {
  try {
    const response = await request.get(`/repair-orders/admin/${row.id}`)
    currentOrder.value = response
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取订单详情失败')
    console.error('获取订单详情失败:', error)
  }
}

// 分配工人
const handleAssign = (row) => {
  // 打开分配工人对话框
  console.log('分配工人:', row)
}

// 更新状态
const handleUpdateStatus = (row) => {
  // 打开状态更新对话框
  console.log('更新状态:', row)
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

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
// 使用全局样式
</style> 