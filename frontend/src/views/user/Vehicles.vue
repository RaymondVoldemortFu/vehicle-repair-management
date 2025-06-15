<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索车牌号或车型"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      <div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加车辆
        </el-button>
      </div>
    </div>

    <div class="card-container">
      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="manufacturer" label="品牌" width="100" />
        <el-table-column prop="model" label="车型" width="150" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="color" label="颜色" width="80" />
        <el-table-column prop="mileage" label="里程(km)" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="登记时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 车辆表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const tableData = ref([])

const searchForm = reactive({
  keyword: ''
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
  user_id: computed(() => authStore.userInfo?.id)
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
      keyword: searchForm.keyword
    }
    const response = await request.get('/vehicles/my-vehicles', { params })
    tableData.value = response || []
  } catch (error) {
    console.error('获取车辆列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  fetchData()
}

// 添加车辆
const handleAdd = () => {
  dialogTitle.value = '添加车辆'
  Object.assign(form, {
    id: null,
    license_plate: '',
    vin: '',
    manufacturer: '',
    model: '',
    year: new Date().getFullYear(),
    color: '',
    mileage: 0
  })
  dialogVisible.value = true
}

// 编辑车辆
const handleEdit = (row) => {
  dialogTitle.value = '编辑车辆'
  form.id = row.id
  form.license_plate = row.license_plate
  form.vin = row.vin
  form.manufacturer = row.manufacturer
  form.model = row.model
  form.year = row.year
  form.color = row.color
  form.mileage = row.mileage
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (form.id) {
      await request.put(`/vehicles/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/vehicles/', form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除车辆
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车辆 ${row.license_plate} 吗？`,
      '提示',
      { type: 'warning' }
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

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
// 使用全局样式
</style> 