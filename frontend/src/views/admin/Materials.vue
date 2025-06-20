<template>
  <div class="page-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>材料管理</h1>
        <p class="page-description">管理维修材料库存、供应商和采购记录</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleEdit()">
          <el-icon><Plus /></el-icon>
          添加材料
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
       <el-form :model="searchForm" layout="inline" @submit.prevent="handleSearch">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="关键词">
              <el-input
                v-model="searchForm.keyword"
                placeholder="搜索材料名称或编号"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
          </el-col>
           <el-col :span="8">
            <el-form-item label="分类">
              <el-input
                v-model="searchForm.category"
                placeholder="按分类搜索"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="resetSearch">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 材料列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="materials"
        style="width: 100%"
        :row-class-name="getRowClassName"
      >
        <el-table-column prop="material_code" label="材料编号" width="140" />
        <el-table-column prop="name" label="材料名称" width="200" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ parseFloat(row.unit_price).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="当前库存" width="100">
           <template #default="{ row }">
            <span :class="getStockClass(row)">{{ row.stock_quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock_level" label="最低库存" width="100" />
        <el-table-column prop="status" label="状态" width="120">
           <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_purchase_date" label="最后采购" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 添加/编辑材料对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料编号" prop="material_code">
              <el-input v-model="form.material_code" placeholder="请输入材料编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入材料名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料分类" prop="category">
               <el-input v-model="form.category" placeholder="请输入分类" />
            </el-form-item>
          </el-col>
           <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" placeholder="例如: 个, 套, 升" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="材料描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入材料描述"
          />
        </el-form-item>
        <el-row :gutter="20">
           <el-col :span="12">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number
                v-model="form.unit_price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前库存" prop="stock_quantity">
              <el-input-number
                v-model="form.stock_quantity"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
           <el-col :span="12">
            <el-form-item label="最低库存" prop="min_stock_level">
              <el-input-number
                v-model="form.min_stock_level"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
         <el-form-item label="最后采购日期" prop="last_purchase_date">
              <el-date-picker
                v-model="form.last_purchase_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
        </el-form-item>
         <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
            <el-option label="有效" value="active" />
            <el-option label="停产" value="discontinued" />
            <el-option label="缺货" value="out_of_stock" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">
          {{ form.id ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

// Refs
const loading = ref(true)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()

// Data
const materials = ref([])
const searchForm = reactive({
  keyword: '',
  category: ''
})
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const initialForm = {
    id: null,
    material_code: '',
    name: '',
    description: '',
    category: '',
    unit_price: 0,
    unit: '',
    stock_quantity: 0,
    min_stock_level: 0,
    status: 'active',
    last_purchase_date: null
}
const form = reactive({ ...initialForm })

// Rules
const formRules = {
  material_code: [{ required: true, message: '请输入材料编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入材料名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入材料分类', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  stock_quantity: [{ required: true, message: '请输入当前库存', trigger: 'blur' }],
  min_stock_level: [{ required: true, message: '请输入最低库存', trigger: 'blur' }]
}

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      category: searchForm.category
    }
    const filteredParams = Object.fromEntries(Object.entries(params).filter(([_, v]) => v))
    const response = await request.get('/materials/', { params: filteredParams })
    materials.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取材料列表失败:', error)
    ElMessage.error('获取材料列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.category = ''
  handleSearch()
}

const resetForm = () => {
  Object.assign(form, initialForm)
  formRef.value?.clearValidate()
}

const handleEdit = (row = null) => {
  resetForm()
  if (row) {
    dialogTitle.value = '编辑材料'
    Object.assign(form, row)
  } else {
    dialogTitle.value = '添加材料'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) {
      await request.put(`/materials/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/materials/', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定要删除材料 "${row.name}" 吗?`, '警告', {
    type: 'warning'
  })
  try {
    await request.delete(`/materials/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// Helper functions for display
const getStatusName = (status) => {
  const map = { active: '有效', discontinued: '停产', out_of_stock: '缺货' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { active: 'success', discontinued: 'info', out_of_stock: 'danger' }
  return map[status] || 'primary'
}

const getStockClass = (row) => {
  if (row.stock_quantity <= 0) return 'stock-danger'
  if (row.stock_quantity < row.min_stock_level) return 'stock-warning'
  return ''
}

const getRowClassName = ({ row }) => {
  if (row.stock_quantity < row.min_stock_level && row.stock_quantity > 0) {
    return 'warning-row'
  }
  if (row.stock_quantity <= 0) {
    return 'danger-row'
  }
  return ''
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.search-card, .table-card {
  margin-bottom: 20px;
}
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
.stock-warning {
  color: #e6a23c;
  font-weight: bold;
}
.stock-danger {
  color: #f56c6c;
  font-weight: bold;
}

:deep(.el-table .warning-row) {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
:deep(.el-table .danger-row) {
  --el-table-tr-bg-color: var(--el-color-danger-light-9);
}
</style> 