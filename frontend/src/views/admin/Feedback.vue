<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>反馈管理</h1>
      <p>管理用户反馈、投诉建议和满意度调查</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" layout="inline" @submit.prevent="handleSearch">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="关键词">
              <el-input
                v-model="searchForm.keyword"
                placeholder="搜索内容或用户"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="类型">
              <el-select v-model="searchForm.feedback_type" placeholder="反馈类型" clearable @change="handleSearch">
                <el-option label="BUG" value="bug" />
                <el-option label="建议" value="suggestion" />
                <el-option label="投诉" value="complaint" />
                <el-option label="咨询" value="query" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status_filter" placeholder="处理状态" clearable @change="handleSearch">
                <el-option label="待处理" value="pending" />
                <el-option label="处理中" value="in_progress" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 反馈列表 -->
    <el-card class="table-card">
      <el-table v-loading="loading" :data="feedbacks" style="width: 100%">
        <el-table-column prop="user_id" label="用户ID" width="120" />
        <el-table-column prop="feedback_type" label="类型" width="150">
           <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.feedback_type)">
              {{ getTypeName(row.feedback_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip />
         <el-table-column prop="rating" label="评分" width="180">
          <template #default="{ row }">
            <el-rate v-if="row.rating" v-model="row.rating" disabled show-text :texts="['极差', '失望', '一般', '满意', '惊喜']" />
             <span v-else>无评分</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">处理</el-button>
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

    <!-- 处理反馈对话框 -->
    <el-dialog v-model="dialogVisible" title="处理反馈" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="反馈标题">
          <strong>{{ form.title }}</strong>
        </el-form-item>
        <el-form-item label="反馈内容">
          <p>{{ form.content }}</p>
        </el-form-item>
        <el-form-item label="处理状态" prop="status">
          <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
            <el-option label="处理中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容" prop="response">
          <el-input
            v-model="form.response"
            type="textarea"
            :rows="4"
            placeholder="请输入对用户的回复"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// Refs
const loading = ref(true)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref()

// Data
const feedbacks = ref([])
const searchForm = reactive({
  keyword: '',
  feedback_type: '',
  status_filter: ''
})
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const initialForm = {
  id: null,
  title: '',
  content: '',
  status: 'pending',
  response: ''
}
const form = reactive({ ...initialForm })

// Rules
const formRules = {
  status: [{ required: true, message: '请选择处理状态', trigger: 'change' }],
  response: [{ required: true, message: '请输入回复内容', trigger: 'blur' }]
}

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      feedback_type: searchForm.feedback_type,
      status_filter: searchForm.status_filter
    }
    const filteredParams = Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null && v !== ''))
    const response = await request.get('/feedback/admin/all', { params: filteredParams })
    feedbacks.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取反馈列表失败:', error)
    ElMessage.error('获取反馈列表失败')
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
  searchForm.feedback_type = ''
  searchForm.status_filter = ''
  handleSearch()
}

const resetForm = () => {
  Object.assign(form, initialForm)
  formRef.value?.clearValidate()
}

const handleEdit = (row) => {
  resetForm()
  // 只填充需要编辑的字段
  form.id = row.id
  form.title = row.title
  form.content = row.comment
  form.status = row.status
  form.response = row.response || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  saving.value = true
  try {
    // 后端期望一个只包含status和response的对象
    const updateData = {
      status: form.status,
      response: form.response
    }
    await request.put(`/feedback/admin/${form.id}`, updateData)
    ElMessage.success('处理成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('处理失败:', error)
    // 可以在这里显示更详细的错误信息
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定要删除这条反馈吗?`, '警告', {
    type: 'warning'
  })
  try {
    await request.delete(`/feedback/admin/${row.id}`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// Helper functions for display
const getTypeName = (type) => {
  const map = {
    service_quality: '服务质量',
    system_issue: '系统问题',
    suggestion: '功能建议',
    other: '其他问题'
  }
  return map[type] || type
}

const getTypeTagType = (type) => {
    const map = {
    service_quality: 'success',
    system_issue: 'danger',
    suggestion: 'primary',
    other: 'info'
  }
  return map[type] || 'info'
}

const getStatusName = (status) => {
  const map = { pending: '待处理', in_progress: '处理中', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { pending: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
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