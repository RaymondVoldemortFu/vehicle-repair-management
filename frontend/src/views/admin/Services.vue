<template>
  <div class="page-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>服务管理</h1>
        <p class="page-description">管理维修服务项目、价格和分类</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleEdit()">
          <el-icon><Plus /></el-icon>
          添加服务
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
                placeholder="搜索服务名称或代码"
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

    <!-- 服务列表 -->
    <el-card class="table-card">
      <el-table v-loading="loading" :data="services" style="width: 100%">
        <el-table-column prop="service_code" label="服务代码" width="120" />
        <el-table-column prop="name" label="服务名称" width="200" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="standard_price" label="价格" width="120">
          <template #default="{ row }">
            <span>¥{{ row.standard_price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="estimated_hours" label="预计时长(h)" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
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

    <!-- 添加/编辑服务对话框 -->
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
        <el-form-item label="服务代码" prop="service_code">
          <el-input v-model="form.service_code" placeholder="请输入服务代码" />
        </el-form-item>
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入服务名称" />
        </el-form-item>
        <el-form-item label="服务分类" prop="category">
          <el-input v-model="form.category" placeholder="请输入服务分类" />
        </el-form-item>
        <el-form-item label="服务描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入服务描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务价格" prop="standard_price">
              <el-input-number
                v-model="form.standard_price"
                :min="0"
                :precision="2"
                placeholder="请输入价格"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计时长" prop="estimated_hours">
              <el-input-number
                v-model="form.estimated_hours"
                :min="1"
                placeholder="小时"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="服务状态" prop="status">
          <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="废弃" value="deprecated" />
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
const services = ref([])
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
  service_code: '',
  name: '',
  description: '',
  category: '',
  standard_price: 0,
  estimated_hours: 1,
  status: 'active'
}
const form = reactive({ ...initialForm })

// Rules
const formRules = {
  service_code: [{ required: true, message: '请输入服务代码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入服务分类', trigger: 'blur' }],
  standard_price: [{ required: true, message: '请输入服务价格', trigger: 'blur' }],
  estimated_hours: [{ required: true, message: '请输入预计时长', trigger: 'blur' }]
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
    const response = await request.get('/services/', { params: filteredParams })
    services.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取服务列表失败:', error)
    ElMessage.error('获取服务列表失败')
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
    dialogTitle.value = '编辑服务'
    Object.assign(form, row)
  } else {
    dialogTitle.value = '添加服务'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) {
      await request.put(`/services/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/services/', form)
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
  await ElMessageBox.confirm(`确定要删除服务 "${row.name}" 吗?`, '警告', {
    type: 'warning'
  })
  try {
    await request.delete(`/services/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
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
</style> 