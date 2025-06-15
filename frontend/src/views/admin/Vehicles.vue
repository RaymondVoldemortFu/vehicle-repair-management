<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索车牌号或车架号"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchForm.status" placeholder="车辆状态" style="width: 120px" clearable>
          <el-option label="正常" value="normal" />
          <el-option label="维修中" value="repairing" />
          <el-option label="报废" value="scrapped" />
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
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="车主" width="180">
          <template #default="{ row }">
            <div v-if="row.owner">
              <div>{{ row.owner.username }}</div>
              <div style="font-size: 12px; color: #909399;">{{ row.owner.phone }}</div>
            </div>
            <span v-else>未知</span>
          </template>
        </el-table-column>
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="manufacturer" label="品牌" width="120" />
        <el-table-column prop="model" label="车型" width="150" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="mileage" label="里程(km)" width="100" />
        <el-table-column prop="created_at" label="登记时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
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

    <!-- 车辆详情对话框 -->
    <el-dialog v-model="detailVisible" title="车辆详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="车牌号">{{ currentVehicle.license_plate }}</el-descriptions-item>
        <el-descriptions-item label="车架号">{{ currentVehicle.vin }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ currentVehicle.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="车型">{{ currentVehicle.model }}</el-descriptions-item>
        <el-descriptions-item label="年份">{{ currentVehicle.year }}</el-descriptions-item>
        <el-descriptions-item label="颜色">{{ currentVehicle.color }}</el-descriptions-item>
        <el-descriptions-item label="里程">{{ currentVehicle.mileage }} km</el-descriptions-item>
        <el-descriptions-item label="车主">{{ currentVehicle.owner?.name }}</el-descriptions-item>
        <el-descriptions-item label="登记时间">{{ formatDate(currentVehicle.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 编辑车辆对话框 -->
    <el-dialog v-model="editVisible" title="编辑车辆" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="车牌号" prop="license_plate">
          <el-input v-model="form.license_plate" placeholder="请输入车牌号" />
        </el-form-item>
        <el-form-item label="车架号" prop="vin">
          <el-input v-model="form.vin" placeholder="请输入车架号" />
        </el-form-item>
        <el-form-item label="品牌" prop="manufacturer">
          <el-input v-model="form.manufacturer" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="车型" prop="model">
          <el-input v-model="form.model" placeholder="请输入车型" />
        </el-form-item>
        <el-form-item label="年份" prop="year">
          <el-input-number v-model="form.year" :min="1900" :max="2030" style="width: 100%" />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-input v-model="form.color" placeholder="请输入颜色" />
        </el-form-item>
        <el-form-item label="里程" prop="mileage">
          <el-input-number v-model="form.mileage" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="维修中" value="repairing" />
            <el-option label="报废" value="scrapped" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          保存
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

const loading = ref(false)
const submitting = ref(false)
const detailVisible = ref(false)
const editVisible = ref(false)
const tableData = ref([])
const currentVehicle = ref({})

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const form = reactive({
  id: null,
  license_plate: '',
  vin: '',
  manufacturer: '',
  model: '',
  year: new Date().getFullYear(),
  color: '',
  mileage: 0,
  status: 'normal'
})

const formRef = ref()

const rules = {
  license_plate: [
    { required: true, message: '请输入车牌号', trigger: 'blur' }
  ],
  vin: [
    { required: true, message: '请输入车架号', trigger: 'blur' }
  ],
  manufacturer: [
    { required: true, message: '请输入品牌', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入车型', trigger: 'blur' }
  ]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const response = await request.get('/vehicles/', { params })
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取车辆列表失败:', error)
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
    const response = await request.get(`/vehicles/admin/${row.id}`)
    currentVehicle.value = response
    detailVisible.value = true
  } catch (error) {
    console.error('获取车辆详情失败:', error)
  }
}

// 编辑车辆
const handleEdit = (row) => {
  Object.assign(form, row)
  editVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    await request.put(`/vehicles/${form.id}`, form)
    ElMessage.success('更新成功')
    editVisible.value = false
    fetchData()
  } catch (error) {
    console.error('更新失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除车辆
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车辆 ${row.license_plate} 吗？此操作不可恢复！`,
      '警告',
      { type: 'error' }
    )
    
    await request.delete(`/vehicles/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'normal': 'success',
    'repairing': 'warning',
    'scrapped': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'normal': '正常',
    'repairing': '维修中',
    'scrapped': '报废'
  }
  return statusMap[status] || '未知'
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || '未知'
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