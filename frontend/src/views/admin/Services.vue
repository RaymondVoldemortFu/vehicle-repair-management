<template>
  <div class="services-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>服务管理</h1>
        <p class="page-description">管理维修服务项目、价格和分类</p>
      </div>
      <div class="header-right">
        <el-button @click="showCategoryDialog = true">
          <el-icon><FolderAdd /></el-icon>
          管理分类
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加服务
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索服务名称或描述"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.category" placeholder="服务分类" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="服务状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input-number
            v-model="searchForm.minPrice"
            placeholder="最低价格"
            :min="0"
            :precision="2"
            style="width: 100%"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="exportServices">导出数据</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总服务数</div>
          </div>
          <el-icon class="stat-icon"><Tools /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.active }}</div>
            <div class="stat-label">启用服务</div>
          </div>
          <el-icon class="stat-icon active"><CircleCheck /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.categories }}</div>
            <div class="stat-label">服务分类</div>
          </div>
          <el-icon class="stat-icon category"><Folder /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.avgPrice.toFixed(0) }}</div>
            <div class="stat-label">平均价格</div>
          </div>
          <el-icon class="stat-icon price"><Money /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="services"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="服务名称" width="200" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag>{{ getCategoryName(row.categoryId) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="预计时长" width="120">
          <template #default="{ row }">
            {{ row.duration }}小时
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度等级" width="120">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTagType(row.difficulty)">
              {{ getDifficultyName(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="orderCount" label="订单数量" width="100" />
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewService(row)">详情</el-button>
            <el-button size="small" type="primary" @click="editService(row)">编辑</el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`status-${row.id}`">
                    {{ row.status === 'active' ? '禁用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="`copy-${row.id}`">复制服务</el-dropdown-item>
                  <el-dropdown-item :command="`history-${row.id}`">价格历史</el-dropdown-item>
                  <el-dropdown-item :command="`delete-${row.id}`" divided class="danger">删除</el-dropdown-item>
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

    <!-- 添加/编辑服务对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingService ? '编辑服务' : '添加服务'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="serviceFormRef"
        :model="serviceForm"
        :rules="serviceFormRules"
        label-width="100px"
      >
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="serviceForm.name" placeholder="请输入服务名称" />
        </el-form-item>
        <el-form-item label="服务分类" prop="categoryId">
          <el-select v-model="serviceForm.categoryId" placeholder="选择服务分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="服务描述" prop="description">
          <el-input
            v-model="serviceForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入服务描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务价格" prop="price">
              <el-input-number
                v-model="serviceForm.price"
                :min="0"
                :precision="2"
                placeholder="请输入价格"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计时长" prop="duration">
              <el-input-number
                v-model="serviceForm.duration"
                :min="0.5"
                :step="0.5"
                :precision="1"
                placeholder="小时"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="serviceForm.difficulty" placeholder="选择难度等级" style="width: 100%">
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
                <el-option label="专家级" value="expert" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务状态" prop="status">
              <el-select v-model="serviceForm.status" placeholder="选择状态" style="width: 100%">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="所需技能" prop="requiredSkills">
          <el-select
            v-model="serviceForm.requiredSkills"
            multiple
            placeholder="选择所需技能"
            style="width: 100%"
          >
            <el-option label="发动机维修" value="engine" />
            <el-option label="变速箱维修" value="transmission" />
            <el-option label="电路维修" value="electrical" />
            <el-option label="车身维修" value="body" />
            <el-option label="轮胎更换" value="tire" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务说明">
          <el-input
            v-model="serviceForm.notes"
            type="textarea"
            :rows="2"
            placeholder="服务注意事项或特殊说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveService" :loading="saving">
          {{ editingService ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 服务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="服务详情" width="800px">
      <div v-if="selectedService" class="service-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="服务名称">{{ selectedService.name }}</el-descriptions-item>
          <el-descriptions-item label="服务分类">
            <el-tag>{{ getCategoryName(selectedService.categoryId) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务价格">
            <span class="price-text">¥{{ selectedService.price.toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="预计时长">{{ selectedService.duration }}小时</el-descriptions-item>
          <el-descriptions-item label="难度等级">
            <el-tag :type="getDifficultyTagType(selectedService.difficulty)">
              {{ getDifficultyName(selectedService.difficulty) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务状态">
            <el-tag :type="selectedService.status === 'active' ? 'success' : 'danger'">
              {{ selectedService.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="订单数量">{{ selectedService.orderCount }}</el-descriptions-item>
          <el-descriptions-item label="服务评分">
            <el-rate v-model="selectedService.rating" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="服务描述" :span="2">
            {{ selectedService.description }}
          </el-descriptions-item>
          <el-descriptions-item label="所需技能" :span="2">
            <el-tag
              v-for="skill in selectedService.requiredSkills"
              :key="skill"
              style="margin-right: 8px"
            >
              {{ getSkillName(skill) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务说明" :span="2">
            {{ selectedService.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>价格历史</el-divider>
        <el-table :data="selectedService.priceHistory" style="width: 100%">
          <el-table-column prop="price" label="价格">
            <template #default="{ row }">
              ¥{{ row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="changeDate" label="变更日期" />
          <el-table-column prop="operator" label="操作人" />
          <el-table-column prop="reason" label="变更原因" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 分类管理对话框 -->
    <el-dialog v-model="showCategoryDialog" title="分类管理" width="600px">
      <div class="category-management">
        <div class="category-form">
          <el-input
            v-model="newCategoryName"
            placeholder="输入分类名称"
            style="width: 200px; margin-right: 10px"
          />
          <el-button type="primary" @click="addCategory">添加分类</el-button>
        </div>
        <el-table :data="categories" style="width: 100%; margin-top: 20px">
          <el-table-column prop="name" label="分类名称" />
          <el-table-column prop="serviceCount" label="服务数量" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="editCategory(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
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
import { Plus, Search, Tools, CircleCheck, Folder, Money, FolderAdd, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showCategoryDialog = ref(false)
const editingService = ref(null)
const selectedService = ref(null)
const selectedServices = ref([])
const newCategoryName = ref('')

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
  minPrice: null
})

// 服务表单
const serviceForm = reactive({
  name: '',
  categoryId: '',
  description: '',
  price: 0,
  duration: 1,
  difficulty: '',
  status: 'active',
  requiredSkills: [],
  notes: ''
})

// 表单验证规则
const serviceFormRules = {
  name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择服务分类', trigger: 'change' }],
  description: [{ required: true, message: '请输入服务描述', trigger: 'blur' }],
  price: [{ required: true, message: '请输入服务价格', trigger: 'blur' }],
  duration: [{ required: true, message: '请输入预计时长', trigger: 'blur' }],
  difficulty: [{ required: true, message: '请选择难度等级', trigger: 'change' }],
  status: [{ required: true, message: '请选择服务状态', trigger: 'change' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 数据
const services = ref([])
const categories = ref([])

// 统计数据
const stats = reactive({
  total: 0,
  active: 0,
  categories: 0,
  avgPrice: 0
})

// 表单引用
const serviceFormRef = ref()

// 方法
const fetchServices = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    services.value = [
      {
        id: 1,
        name: '发动机大修',
        categoryId: 1,
        description: '全面检修发动机，包括活塞、气缸、曲轴等核心部件',
        price: 3500.00,
        duration: 8,
        difficulty: 'expert',
        status: 'active',
        requiredSkills: ['engine'],
        notes: '需要专业设备和经验丰富的技师',
        orderCount: 45,
        rating: 4.8,
        priceHistory: [
          { price: 3500.00, changeDate: '2024-01-01', operator: '管理员', reason: '市场调研后调整' },
          { price: 3200.00, changeDate: '2023-12-01', operator: '管理员', reason: '初始价格' }
        ]
      },
      {
        id: 2,
        name: '刹车片更换',
        categoryId: 2,
        description: '更换前后刹车片，检查刹车系统',
        price: 280.00,
        duration: 1.5,
        difficulty: 'easy',
        status: 'active',
        requiredSkills: ['brake'],
        notes: '常规保养项目',
        orderCount: 156,
        rating: 4.9,
        priceHistory: [
          { price: 280.00, changeDate: '2024-01-01', operator: '管理员', reason: '价格稳定' }
        ]
      }
    ]
    
    // 更新统计数据
    stats.total = services.value.length
    stats.active = services.value.filter(s => s.status === 'active').length
    stats.categories = categories.value.length
    stats.avgPrice = services.value.reduce((sum, s) => sum + s.price, 0) / services.value.length
    
    pagination.total = services.value.length
  } catch (error) {
    ElMessage.error('获取服务列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    // 模拟数据
    categories.value = [
      { id: 1, name: '发动机维修', serviceCount: 12, status: 'active' },
      { id: 2, name: '制动系统', serviceCount: 8, status: 'active' },
      { id: 3, name: '电气系统', serviceCount: 15, status: 'active' },
      { id: 4, name: '车身维修', serviceCount: 6, status: 'active' },
      { id: 5, name: '轮胎服务', serviceCount: 4, status: 'active' }
    ]
    
    stats.categories = categories.value.length
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  // 在实际应用中，这里会调用API进行搜索
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    category: '',
    status: '',
    minPrice: null
  })
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedServices.value = selection
}

const viewService = (service) => {
  selectedService.value = service
  showDetailDialog.value = true
}

const editService = (service) => {
  editingService.value = service
  Object.assign(serviceForm, service)
  showAddDialog.value = true
}

const saveService = async () => {
  if (!serviceFormRef.value) return
  
  try {
    await serviceFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingService.value) {
      ElMessage.success('服务更新成功')
    } else {
      ElMessage.success('服务添加成功')
    }
    
    showAddDialog.value = false
    await fetchServices()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingService.value = null
  Object.assign(serviceForm, {
    name: '',
    categoryId: '',
    description: '',
    price: 0,
    duration: 1,
    difficulty: '',
    status: 'active',
    requiredSkills: [],
    notes: ''
  })
  if (serviceFormRef.value) {
    serviceFormRef.value.clearValidate()
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const service = services.value.find(s => s.id === parseInt(id))
  
  switch (action) {
    case 'status':
      try {
        await ElMessageBox.confirm(
          `确定要${service.status === 'active' ? '禁用' : '启用'}服务 ${service.name} 吗？`,
          '确认操作',
          { type: 'warning' }
        )
        ElMessage.success('状态更新成功')
        await fetchServices()
      } catch {
        // 用户取消
      }
      break
    case 'copy':
      editingService.value = null
      Object.assign(serviceForm, {
        ...service,
        name: service.name + ' (副本)'
      })
      showAddDialog.value = true
      break
    case 'history':
      viewService(service)
      break
    case 'delete':
      try {
        await ElMessageBox.confirm(
          `确定要删除服务 ${service.name} 吗？此操作不可恢复。`,
          '确认删除',
          { type: 'warning' }
        )
        ElMessage.success('删除成功')
        await fetchServices()
      } catch {
        // 用户取消
      }
      break
  }
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    categories.value.push({
      id: Date.now(),
      name: newCategoryName.value,
      serviceCount: 0,
      status: 'active'
    })
    
    newCategoryName.value = ''
    ElMessage.success('分类添加成功')
  } catch (error) {
    ElMessage.error('添加分类失败')
  }
}

const editCategory = async (category) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的分类名称', '编辑分类', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: category.name
    })
    
    category.name = value
    ElMessage.success('分类更新成功')
  } catch {
    // 用户取消
  }
}

const deleteCategory = async (category) => {
  if (category.serviceCount > 0) {
    ElMessage.warning('该分类下还有服务项目，无法删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 ${category.name} 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const index = categories.value.findIndex(c => c.id === category.id)
    if (index > -1) {
      categories.value.splice(index, 1)
    }
    
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const exportServices = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchServices()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchServices()
}

// 辅助方法
const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : '未知分类'
}

const getDifficultyName = (difficulty) => {
  const difficultyMap = {
    easy: '简单',
    medium: '中等',
    hard: '困难',
    expert: '专家级'
  }
  return difficultyMap[difficulty] || difficulty
}

const getDifficultyTagType = (difficulty) => {
  const typeMap = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger',
    expert: 'info'
  }
  return typeMap[difficulty] || ''
}

const getSkillName = (skill) => {
  const skillMap = {
    engine: '发动机维修',
    transmission: '变速箱维修',
    electrical: '电路维修',
    body: '车身维修',
    tire: '轮胎更换',
    brake: '制动系统'
  }
  return skillMap[skill] || skill
}

// 生命周期
onMounted(() => {
  fetchCategories()
  fetchServices()
})
</script>

<style scoped>
.services-container {
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

.stat-icon.category {
  color: #409eff;
}

.stat-icon.price {
  color: #f56c6c;
}

.table-card {
  margin-bottom: 20px;
}

.price-text {
  font-weight: bold;
  color: #f56c6c;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.service-detail {
  padding: 20px 0;
}

.category-management {
  padding: 10px 0;
}

.category-form {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.danger {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .services-container {
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