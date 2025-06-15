<template>
  <div class="workers-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>工人管理</h1>
        <p class="page-description">管理维修工人信息、技能和工作状态</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddWorker">
          <el-icon><Plus /></el-icon>
          添加工人
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" layout="inline">
      <el-row :gutter="20">
        <el-col :span="6">
            <el-form-item>
          <el-input
            v-model="searchForm.keyword"
                placeholder="搜索工人姓名或工号"
            clearable
                @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
            </el-form-item>
        </el-col>
          <el-col :span="5">
            <el-form-item>
          <el-select v-model="searchForm.status" placeholder="工作状态" clearable @change="handleSearch">
            <el-option label="在职" value="active" />
                <el-option label="休假" value="on_leave" />
            <el-option label="离职" value="inactive" />
          </el-select>
            </el-form-item>
        </el-col>
          <el-col :span="5">
             <el-form-item>
              <el-select v-model="searchForm.skill_type" placeholder="技能类型" clearable @change="handleSearch">
                <el-option label="机械" value="mechanical" />
                <el-option label="电气" value="electrical" />
                <el-option label="钣金" value="bodywork" />
                <el-option label="发动机" value="engine" />
                <el-option label="变速箱" value="transmission" />
                <el-option label="刹车" value="brake" />
                <el-option label="悬挂" value="suspension" />
                <el-option label="空调" value="air_conditioning" />
          </el-select>
            </el-form-item>
        </el-col>
          <el-col :span="8">
             <el-form-item>
          <el-button @click="resetSearch">重置</el-button>
            </el-form-item>
        </el-col>
      </el-row>
      </el-form>
    </el-card>

    <!-- 工人列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="workers"
        style="width: 100%"
      >
        <el-table-column prop="employee_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="skill_type" label="技能类型" width="120">
           <template #default="{ row }">
            {{ getSkillName(row.skill_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="skill_level" label="技能等级" width="100">
          <template #default="{ row }">
            {{ getSkillLevelName(row.skill_level) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
         <el-table-column prop="hourly_rate" label="时薪" width="100">
          <template #default="{ row }">
             ¥{{ row.hourly_rate }}
          </template>
        </el-table-column>
        <el-table-column prop="hire_date" label="入职日期" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEditWorker(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteWorker(row)">删除</el-button>
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
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑工人对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="workerFormRef"
        :model="workerForm"
        :rules="workerFormRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="workerForm.employee_id" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="workerForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="workerForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="workerForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="技能类型" prop="skill_type">
               <el-select v-model="workerForm.skill_type" placeholder="选择技能类型" style="width: 100%">
                <el-option label="机械" value="mechanical" />
                <el-option label="电气" value="electrical" />
                <el-option label="钣金" value="bodywork" />
                <el-option label="发动机" value="engine" />
                <el-option label="变速箱" value="transmission" />
                <el-option label="刹车" value="brake" />
                <el-option label="悬挂" value="suspension" />
                <el-option label="空调" value="air_conditioning" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="技能等级" prop="skill_level">
              <el-select v-model="workerForm.skill_level" placeholder="选择技能等级" style="width: 100%">
                <el-option label="初级" value="junior" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="senior" />
                <el-option label="专家" value="expert" />
              </el-select>
        </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker
                v-model="workerForm.hire_date"
            type="date"
            placeholder="选择入职日期"
            style="width: 100%"
                value-format="YYYY-MM-DD"
          />
        </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时薪" prop="hourly_rate">
          <el-input-number
                v-model="workerForm.hourly_rate"
            :min="0"
            :precision="2"
                placeholder="请输入时薪"
            style="width: 100%"
          />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="资质证书" prop="certifications">
          <el-input v-model="workerForm.certifications" type="textarea" placeholder="请输入资质证书，多项请用逗号隔开" />
        </el-form-item>
        <el-form-item v-if="!workerForm.id" label="初始密码" prop="password">
          <el-input v-model="workerForm.password" type="password" show-password placeholder="请输入初始密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWorker" :loading="saving">
          {{ workerForm.id ? '更新' : '添加' }}
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
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const workers = ref([])
const workerFormRef = ref()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  skill_type: ''
})

const initialFormState = {
  id: null,
  employee_id: '',
  name: '',
  phone: '',
  email: '',
  skill_type: 'mechanical',
  skill_level: 'junior',
  hourly_rate: 0,
  hire_date: '',
  certifications: '',
  password: ''
}

// 工人表单
const workerForm = reactive({ ...initialFormState })

// 表单验证规则
const workerFormRules = {
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { min: 4, message: '工号长度必须超过3位', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
  skill_type: [{ required: true, message: '请选择技能类型', trigger: 'change' }],
  skill_level: [{ required: true, message: '请选择技能等级', trigger: 'change' }],
  hire_date: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  hourly_rate: [{ required: true, message: '请输入时薪', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入初始密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
}

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取工人列表
const fetchWorkers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      status: searchForm.status,
      skill_type: searchForm.skill_type
    }
    // 过滤掉空的参数
    const filteredParams = Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null && v !== ''))
    
    const response = await request.get('/workers/', { params: filteredParams })
    workers.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('获取工人列表失败:', error)
    ElMessage.error('获取工人列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchWorkers()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.skill_type = ''
  handleSearch()
}

// 分页大小变化
const handleSizeChange = (val) => {
  pagination.size = val
  fetchWorkers()
}

// 当前页变化
const handleCurrentChange = (val) => {
  pagination.page = val
  fetchWorkers()
}

// 重置表单
const resetForm = () => {
  Object.assign(workerForm, initialFormState)
  if (workerFormRef.value) {
    workerFormRef.value.clearValidate()
  }
}

// 添加工人
const handleAddWorker = () => {
  resetForm()
  dialogTitle.value = '添加工人'
  dialogVisible.value = true
}

// 编辑工人
const handleEditWorker = (row) => {
  resetForm()
  dialogTitle.value = '编辑工人'
  // 注意：需要从row中复制数据到workerForm
  Object.assign(workerForm, row)
  dialogVisible.value = true
}

// 保存工人
const saveWorker = async () => {
  if (!workerFormRef.value) return
  await workerFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        if (workerForm.id) {
          // 更新
          const { id, ...data } = workerForm
          await request.put(`/workers/${id}`, data)
          ElMessage.success('更新成功')
    } else {
          // 创建
          await request.post('/workers/', workerForm)
          ElMessage.success('添加成功')
    }
        dialogVisible.value = false
        fetchWorkers()
  } catch (error) {
        console.error('保存工人失败:', error)
  } finally {
    saving.value = false
  }
}
  })
}

// 删除工人
const handleDeleteWorker = async (row) => {
      try {
    await ElMessageBox.confirm(`确定要删除工人 ${row.name} 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/workers/${row.id}`)
        ElMessage.success('删除成功')
    fetchWorkers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工人失败:', error)
}
  }
}

// 辅助函数，用于显示名称
const getSkillName = (type) => {
  const map = {
    mechanical: '机械', electrical: '电气', bodywork: '钣金',
    engine: '发动机', transmission: '变速箱', brake: '刹车',
    suspension: '悬挂', air_conditioning: '空调'
  }
  return map[type] || type
}

const getSkillLevelName = (level) => {
  const map = { junior: '初级', intermediate: '中级', senior: '高级', expert: '专家' }
  return map[level] || level
}

const getStatusName = (status) => {
  const map = { active: '在职', on_leave: '休假', inactive: '离职' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { active: 'success', on_leave: 'warning', inactive: 'danger' }
  return map[status] || 'info'
  }

onMounted(() => {
  fetchWorkers()
})

</script>

<style lang="scss" scoped>
.workers-container {
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

    h1 {
  margin: 0;
      font-size: 24px;
}
.page-description {
      color: #606266;
  font-size: 14px;
      margin-top: 4px;
}
}

  .search-card, .table-card {
  margin-bottom: 20px;
}

  .el-form-item {
    margin-bottom: 0;
}

.pagination-container {
  display: flex;
    justify-content: flex-end;
  margin-top: 20px;
}

.danger {
    color: var(--el-color-danger);
  }
}
</style> 