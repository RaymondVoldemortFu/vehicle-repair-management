<template>
  <div class="workers-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>工人管理</h1>
        <p class="page-description">管理维修工人信息、技能和工作状态</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加工人
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索工人姓名、工号或手机号"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="工作状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="在职" value="active" />
            <el-option label="休假" value="vacation" />
            <el-option label="离职" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.skill" placeholder="技能类型" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="发动机维修" value="engine" />
            <el-option label="变速箱维修" value="transmission" />
            <el-option label="电路维修" value="electrical" />
            <el-option label="车身维修" value="body" />
            <el-option label="轮胎更换" value="tire" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.level" placeholder="技能等级" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="初级" value="junior" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="senior" />
            <el-option label="专家" value="expert" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="exportWorkers">导出数据</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总工人数</div>
          </div>
          <el-icon class="stat-icon"><User /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.active }}</div>
            <div class="stat-label">在职工人</div>
          </div>
          <el-icon class="stat-icon active"><UserFilled /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.working }}</div>
            <div class="stat-label">工作中</div>
          </div>
          <el-icon class="stat-icon working"><Tools /></el-icon>
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

    <!-- 工人列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="workers"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :alt="row.name">
              {{ row.name.charAt(0) }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="workerId" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="skills" label="技能" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="skill in row.skills"
              :key="skill.type"
              :type="getSkillTagType(skill.level)"
              size="small"
              class="skill-tag"
            >
              {{ getSkillName(skill.type) }}({{ getSkillLevelName(skill.level) }})
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
        <el-table-column prop="rating" label="评分" width="120">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
          </template>
        </el-table-column>
        <el-table-column prop="completedOrders" label="完成订单" width="100" />
        <el-table-column prop="joinDate" label="入职日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewWorker(row)">详情</el-button>
            <el-button size="small" type="primary" @click="editWorker(row)">编辑</el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`wages-${row.id}`">工资记录</el-dropdown-item>
                  <el-dropdown-item :command="`orders-${row.id}`">工作记录</el-dropdown-item>
                  <el-dropdown-item :command="`status-${row.id}`" divided>
                    {{ row.status === 'active' ? '设为休假' : '设为在职' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="`delete-${row.id}`" class="danger">删除</el-dropdown-item>
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

    <!-- 添加/编辑工人对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingWorker ? '编辑工人' : '添加工人'"
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
            <el-form-item label="工号" prop="workerId">
              <el-input v-model="workerForm.workerId" placeholder="请输入工号" />
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
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="workerForm.idCard" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="workerForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="技能" prop="skills">
          <div class="skills-container">
            <div
              v-for="(skill, index) in workerForm.skills"
              :key="index"
              class="skill-item"
            >
              <el-select v-model="skill.type" placeholder="选择技能类型" style="width: 150px">
                <el-option label="发动机维修" value="engine" />
                <el-option label="变速箱维修" value="transmission" />
                <el-option label="电路维修" value="electrical" />
                <el-option label="车身维修" value="body" />
                <el-option label="轮胎更换" value="tire" />
              </el-select>
              <el-select v-model="skill.level" placeholder="选择等级" style="width: 120px; margin-left: 10px">
                <el-option label="初级" value="junior" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="senior" />
                <el-option label="专家" value="expert" />
              </el-select>
              <el-button
                type="danger"
                size="small"
                @click="removeSkill(index)"
                style="margin-left: 10px"
              >
                删除
              </el-button>
            </div>
            <el-button @click="addSkill" style="margin-top: 10px">添加技能</el-button>
          </div>
        </el-form-item>
        <el-form-item label="入职日期" prop="joinDate">
          <el-date-picker
            v-model="workerForm.joinDate"
            type="date"
            placeholder="选择入职日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="基础工资" prop="baseSalary">
          <el-input-number
            v-model="workerForm.baseSalary"
            :min="0"
            :precision="2"
            placeholder="请输入基础工资"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveWorker" :loading="saving">
          {{ editingWorker ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 工人详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="工人详情" width="800px">
      <div v-if="selectedWorker" class="worker-detail">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="worker-avatar">
              <el-avatar :size="120" :src="selectedWorker.avatar">
                {{ selectedWorker.name.charAt(0) }}
              </el-avatar>
              <h3>{{ selectedWorker.name }}</h3>
              <p>工号：{{ selectedWorker.workerId }}</p>
            </div>
          </el-col>
          <el-col :span="16">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="手机号">{{ selectedWorker.phone }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ selectedWorker.email }}</el-descriptions-item>
              <el-descriptions-item label="身份证号">{{ selectedWorker.idCard }}</el-descriptions-item>
              <el-descriptions-item label="地址">{{ selectedWorker.address }}</el-descriptions-item>
              <el-descriptions-item label="入职日期">{{ selectedWorker.joinDate }}</el-descriptions-item>
              <el-descriptions-item label="工作状态">
                <el-tag :type="getStatusTagType(selectedWorker.status)">
                  {{ getStatusName(selectedWorker.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="评分">
                <el-rate v-model="selectedWorker.rating" disabled show-score />
              </el-descriptions-item>
              <el-descriptions-item label="完成订单">{{ selectedWorker.completedOrders }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        
        <el-divider>技能信息</el-divider>
        <div class="skills-detail">
          <el-tag
            v-for="skill in selectedWorker.skills"
            :key="skill.type"
            :type="getSkillTagType(skill.level)"
            size="large"
            class="skill-tag-large"
          >
            {{ getSkillName(skill.type) }} - {{ getSkillLevelName(skill.level) }}
          </el-tag>
        </div>

        <el-divider>最近工作记录</el-divider>
        <el-table :data="selectedWorker.recentOrders" style="width: 100%">
          <el-table-column prop="orderNumber" label="订单号" />
          <el-table-column prop="vehicleInfo" label="车辆信息" />
          <el-table-column prop="serviceType" label="服务类型" />
          <el-table-column prop="completedAt" label="完成时间" />
          <el-table-column prop="rating" label="评分">
            <template #default="{ row }">
              <el-rate v-model="row.rating" disabled />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, User, UserFilled, Tools, Star, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const editingWorker = ref(null)
const selectedWorker = ref(null)
const selectedWorkers = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  skill: '',
  level: ''
})

// 工人表单
const workerForm = reactive({
  workerId: '',
  name: '',
  phone: '',
  email: '',
  idCard: '',
  address: '',
  skills: [{ type: '', level: '' }],
  joinDate: '',
  baseSalary: 0
})

// 表单验证规则
const workerFormRules = {
  workerId: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  joinDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  baseSalary: [{ required: true, message: '请输入基础工资', trigger: 'blur' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 工人列表
const workers = ref([])

// 统计数据
const stats = reactive({
  total: 0,
  active: 0,
  working: 0,
  avgRating: 0
})

// 表单引用
const workerFormRef = ref()

// 计算属性
const filteredWorkers = computed(() => {
  let result = workers.value
  
  if (searchForm.keyword) {
    result = result.filter(worker => 
      worker.name.includes(searchForm.keyword) ||
      worker.workerId.includes(searchForm.keyword) ||
      worker.phone.includes(searchForm.keyword)
    )
  }
  
  if (searchForm.status) {
    result = result.filter(worker => worker.status === searchForm.status)
  }
  
  if (searchForm.skill) {
    result = result.filter(worker => 
      worker.skills.some(skill => skill.type === searchForm.skill)
    )
  }
  
  if (searchForm.level) {
    result = result.filter(worker => 
      worker.skills.some(skill => skill.level === searchForm.level)
    )
  }
  
  return result
})

// 方法
const fetchWorkers = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    workers.value = [
      {
        id: 1,
        workerId: 'W001',
        name: '张师傅',
        phone: '13800138001',
        email: 'zhang@example.com',
        idCard: '110101199001011234',
        address: '北京市朝阳区',
        avatar: '',
        skills: [
          { type: 'engine', level: 'senior' },
          { type: 'transmission', level: 'intermediate' }
        ],
        status: 'active',
        rating: 4.8,
        completedOrders: 156,
        joinDate: '2020-03-15',
        baseSalary: 8000,
        recentOrders: [
          {
            orderNumber: 'ORD001',
            vehicleInfo: '奥迪A4L',
            serviceType: '发动机维修',
            completedAt: '2024-01-15',
            rating: 5
          }
        ]
      },
      {
        id: 2,
        workerId: 'W002',
        name: '李师傅',
        phone: '13800138002',
        email: 'li@example.com',
        idCard: '110101199002021234',
        address: '北京市海淀区',
        avatar: '',
        skills: [
          { type: 'electrical', level: 'expert' },
          { type: 'body', level: 'senior' }
        ],
        status: 'active',
        rating: 4.9,
        completedOrders: 203,
        joinDate: '2019-08-20',
        baseSalary: 9500,
        recentOrders: []
      }
    ]
    
    // 更新统计数据
    stats.total = workers.value.length
    stats.active = workers.value.filter(w => w.status === 'active').length
    stats.working = workers.value.filter(w => w.status === 'working').length
    stats.avgRating = workers.value.reduce((sum, w) => sum + w.rating, 0) / workers.value.length
    
    pagination.total = workers.value.length
  } catch (error) {
    ElMessage.error('获取工人列表失败')
  } finally {
    loading.value = false
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
    skill: '',
    level: ''
  })
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedWorkers.value = selection
}

const viewWorker = (worker) => {
  selectedWorker.value = worker
  showDetailDialog.value = true
}

const editWorker = (worker) => {
  editingWorker.value = worker
  Object.assign(workerForm, {
    ...worker,
    joinDate: new Date(worker.joinDate)
  })
  showAddDialog.value = true
}

const addSkill = () => {
  workerForm.skills.push({ type: '', level: '' })
}

const removeSkill = (index) => {
  if (workerForm.skills.length > 1) {
    workerForm.skills.splice(index, 1)
  }
}

const saveWorker = async () => {
  if (!workerFormRef.value) return
  
  try {
    await workerFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingWorker.value) {
      ElMessage.success('工人信息更新成功')
    } else {
      ElMessage.success('工人添加成功')
    }
    
    showAddDialog.value = false
    await fetchWorkers()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingWorker.value = null
  Object.assign(workerForm, {
    workerId: '',
    name: '',
    phone: '',
    email: '',
    idCard: '',
    address: '',
    skills: [{ type: '', level: '' }],
    joinDate: '',
    baseSalary: 0
  })
  if (workerFormRef.value) {
    workerFormRef.value.clearValidate()
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const worker = workers.value.find(w => w.id === parseInt(id))
  
  switch (action) {
    case 'wages':
      ElMessage.info('跳转到工资记录页面')
      break
    case 'orders':
      ElMessage.info('跳转到工作记录页面')
      break
    case 'status':
      try {
        await ElMessageBox.confirm(
          `确定要将 ${worker.name} 的状态改为 ${worker.status === 'active' ? '休假' : '在职'} 吗？`,
          '确认操作',
          { type: 'warning' }
        )
        ElMessage.success('状态更新成功')
        await fetchWorkers()
      } catch {
        // 用户取消
      }
      break
    case 'delete':
      try {
        await ElMessageBox.confirm(
          `确定要删除工人 ${worker.name} 吗？此操作不可恢复。`,
          '确认删除',
          { type: 'warning' }
        )
        ElMessage.success('删除成功')
        await fetchWorkers()
      } catch {
        // 用户取消
      }
      break
  }
}

const exportWorkers = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchWorkers()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchWorkers()
}

// 辅助方法
const getStatusName = (status) => {
  const statusMap = {
    active: '在职',
    vacation: '休假',
    inactive: '离职',
    working: '工作中'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    active: 'success',
    vacation: 'warning',
    inactive: 'danger',
    working: 'primary'
  }
  return typeMap[status] || ''
}

const getSkillName = (type) => {
  const skillMap = {
    engine: '发动机维修',
    transmission: '变速箱维修',
    electrical: '电路维修',
    body: '车身维修',
    tire: '轮胎更换'
  }
  return skillMap[type] || type
}

const getSkillLevelName = (level) => {
  const levelMap = {
    junior: '初级',
    intermediate: '中级',
    senior: '高级',
    expert: '专家'
  }
  return levelMap[level] || level
}

const getSkillTagType = (level) => {
  const typeMap = {
    junior: '',
    intermediate: 'success',
    senior: 'warning',
    expert: 'danger'
  }
  return typeMap[level] || ''
}

// 生命周期
onMounted(() => {
  fetchWorkers()
})
</script>

<style scoped>
.workers-container {
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

.stat-icon.active {
  color: #67c23a;
}

.stat-icon.working {
  color: #409eff;
}

.stat-icon.rating {
  color: #f56c6c;
}

.table-card {
  margin-bottom: 20px;
}

.skill-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.skills-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.skill-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.skill-item:last-child {
  margin-bottom: 0;
}

.worker-detail {
  padding: 20px 0;
}

.worker-avatar {
  text-align: center;
}

.worker-avatar h3 {
  margin: 15px 0 5px 0;
  color: #303133;
}

.worker-avatar p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.skills-detail {
  margin: 20px 0;
}

.skill-tag-large {
  margin-right: 10px;
  margin-bottom: 10px;
  padding: 8px 16px;
  font-size: 14px;
}

.danger {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .workers-container {
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