<template>
  <div class="materials-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>材料管理</h1>
        <p class="page-description">管理维修材料库存、供应商和采购记录</p>
      </div>
      <div class="header-right">
        <el-button @click="showSupplierDialog = true">
          <el-icon><Shop /></el-icon>
          供应商管理
        </el-button>
        <el-button @click="showPurchaseDialog = true">
          <el-icon><ShoppingCart /></el-icon>
          采购入库
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加材料
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="5">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索材料名称或编号"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.category" placeholder="材料分类" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="发动机配件" value="engine" />
            <el-option label="制动系统" value="brake" />
            <el-option label="电气配件" value="electrical" />
            <el-option label="车身配件" value="body" />
            <el-option label="润滑油品" value="oil" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="searchForm.status" placeholder="库存状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="warning" />
            <el-option label="缺货" value="shortage" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.supplier" placeholder="供应商" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option
              v-for="supplier in suppliers"
              :key="supplier.id"
              :label="supplier.name"
              :value="supplier.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-switch
            v-model="searchForm.showLowStock"
            active-text="仅显示低库存"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="exportMaterials">导出</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总材料数</div>
          </div>
          <el-icon class="stat-icon"><Box /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.lowStock }}</div>
            <div class="stat-label">低库存预警</div>
          </div>
          <el-icon class="stat-icon warning"><Warning /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.totalValue.toFixed(0) }}</div>
            <div class="stat-label">库存总价值</div>
          </div>
          <el-icon class="stat-icon value"><Money /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.suppliers }}</div>
            <div class="stat-label">供应商数量</div>
          </div>
          <el-icon class="stat-icon supplier"><Shop /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 材料列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="materials"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :row-class-name="getRowClassName"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="材料编号" width="120" />
        <el-table-column prop="name" label="材料名称" width="200" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag>{{ getCategoryName(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格型号" width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="currentStock" label="当前库存" width="100">
          <template #default="{ row }">
            <span :class="getStockClass(row)">{{ row.currentStock }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="minStock" label="最低库存" width="100" />
        <el-table-column prop="unitPrice" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.unitPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="totalValue" label="库存价值" width="120">
          <template #default="{ row }">
            <span class="value-text">¥{{ (row.currentStock * row.unitPrice).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="150">
          <template #default="{ row }">
            {{ getSupplierName(row.supplierId) }}
          </template>
        </el-table-column>
        <el-table-column prop="lastPurchase" label="最后采购" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewMaterial(row)">详情</el-button>
            <el-button size="small" type="primary" @click="editMaterial(row)">编辑</el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`purchase-${row.id}`">采购入库</el-dropdown-item>
                  <el-dropdown-item :command="`adjust-${row.id}`">库存调整</el-dropdown-item>
                  <el-dropdown-item :command="`history-${row.id}`">出入库记录</el-dropdown-item>
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

    <!-- 添加/编辑材料对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingMaterial ? '编辑材料' : '添加材料'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="materialFormRef"
        :model="materialForm"
        :rules="materialFormRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料编号" prop="code">
              <el-input v-model="materialForm.code" placeholder="请输入材料编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料名称" prop="name">
              <el-input v-model="materialForm.name" placeholder="请输入材料名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料分类" prop="category">
              <el-select v-model="materialForm.category" placeholder="选择分类" style="width: 100%">
                <el-option label="发动机配件" value="engine" />
                <el-option label="制动系统" value="brake" />
                <el-option label="电气配件" value="electrical" />
                <el-option label="车身配件" value="body" />
                <el-option label="润滑油品" value="oil" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplierId">
              <el-select v-model="materialForm.supplierId" placeholder="选择供应商" style="width: 100%">
                <el-option
                  v-for="supplier in suppliers"
                  :key="supplier.id"
                  :label="supplier.name"
                  :value="supplier.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="materialForm.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="materialForm.unit" placeholder="选择单位" style="width: 100%">
                <el-option label="个" value="piece" />
                <el-option label="套" value="set" />
                <el-option label="升" value="liter" />
                <el-option label="千克" value="kg" />
                <el-option label="米" value="meter" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unitPrice">
              <el-input-number
                v-model="materialForm.unitPrice"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最低库存" prop="minStock">
              <el-input-number
                v-model="materialForm.minStock"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="材料描述">
          <el-input
            v-model="materialForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入材料描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMaterial" :loading="saving">
          {{ editingMaterial ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 材料详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="材料详情" width="800px">
      <div v-if="selectedMaterial" class="material-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="材料编号">{{ selectedMaterial.code }}</el-descriptions-item>
          <el-descriptions-item label="材料名称">{{ selectedMaterial.name }}</el-descriptions-item>
          <el-descriptions-item label="材料分类">
            <el-tag>{{ getCategoryName(selectedMaterial.category) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="规格型号">{{ selectedMaterial.specification }}</el-descriptions-item>
          <el-descriptions-item label="单位">{{ selectedMaterial.unit }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ selectedMaterial.unitPrice.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="当前库存">
            <span :class="getStockClass(selectedMaterial)">{{ selectedMaterial.currentStock }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="最低库存">{{ selectedMaterial.minStock }}</el-descriptions-item>
          <el-descriptions-item label="库存价值">
            <span class="value-text">¥{{ (selectedMaterial.currentStock * selectedMaterial.unitPrice).toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="供应商">{{ getSupplierName(selectedMaterial.supplierId) }}</el-descriptions-item>
          <el-descriptions-item label="最后采购">{{ selectedMaterial.lastPurchase }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedMaterial.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="材料描述" :span="2">
            {{ selectedMaterial.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>最近出入库记录</el-divider>
        <el-table :data="selectedMaterial.stockHistory" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.type === 'in' ? 'success' : 'warning'">
                {{ row.type === 'in' ? '入库' : '出库' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="reason" label="原因" />
          <el-table-column prop="operator" label="操作人" width="120" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 供应商管理对话框 -->
    <el-dialog v-model="showSupplierDialog" title="供应商管理" width="800px">
      <div class="supplier-management">
        <div class="supplier-form">
          <el-button type="primary" @click="showAddSupplierDialog = true">添加供应商</el-button>
        </div>
        <el-table :data="suppliers" style="width: 100%; margin-top: 20px">
          <el-table-column prop="name" label="供应商名称" />
          <el-table-column prop="contact" label="联系人" />
          <el-table-column prop="phone" label="联系电话" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="address" label="地址" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '合作中' : '已停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="editSupplier(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteSupplier(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 采购入库对话框 -->
    <el-dialog v-model="showPurchaseDialog" title="采购入库" width="600px">
      <el-form
        ref="purchaseFormRef"
        :model="purchaseForm"
        :rules="purchaseFormRules"
        label-width="100px"
      >
        <el-form-item label="选择材料" prop="materialId">
          <el-select v-model="purchaseForm.materialId" placeholder="选择材料" style="width: 100%">
            <el-option
              v-for="material in materials"
              :key="material.id"
              :label="`${material.name} (${material.code})`"
              :value="material.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购数量" prop="quantity">
              <el-input-number
                v-model="purchaseForm.quantity"
                :min="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="采购单价" prop="unitPrice">
              <el-input-number
                v-model="purchaseForm.unitPrice"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商" prop="supplierId">
          <el-select v-model="purchaseForm.supplierId" placeholder="选择供应商" style="width: 100%">
            <el-option
              v-for="supplier in suppliers"
              :key="supplier.id"
              :label="supplier.name"
              :value="supplier.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="采购备注">
          <el-input
            v-model="purchaseForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入采购备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPurchaseDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPurchase" :loading="saving">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Box, Warning, Money, Shop, ShoppingCart, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showSupplierDialog = ref(false)
const showAddSupplierDialog = ref(false)
const showPurchaseDialog = ref(false)
const editingMaterial = ref(null)
const selectedMaterial = ref(null)
const selectedMaterials = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
  supplier: '',
  showLowStock: false
})

// 材料表单
const materialForm = reactive({
  code: '',
  name: '',
  category: '',
  specification: '',
  unit: '',
  unitPrice: 0,
  minStock: 0,
  supplierId: '',
  description: ''
})

// 采购表单
const purchaseForm = reactive({
  materialId: '',
  quantity: 1,
  unitPrice: 0,
  supplierId: '',
  notes: ''
})

// 表单验证规则
const materialFormRules = {
  code: [{ required: true, message: '请输入材料编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入材料名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择材料分类', trigger: 'change' }],
  specification: [{ required: true, message: '请输入规格型号', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  minStock: [{ required: true, message: '请输入最低库存', trigger: 'blur' }],
  supplierId: [{ required: true, message: '请选择供应商', trigger: 'change' }]
}

const purchaseFormRules = {
  materialId: [{ required: true, message: '请选择材料', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入采购数量', trigger: 'blur' }],
  unitPrice: [{ required: true, message: '请输入采购单价', trigger: 'blur' }],
  supplierId: [{ required: true, message: '请选择供应商', trigger: 'change' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 数据
const materials = ref([])
const suppliers = ref([])

// 统计数据
const stats = reactive({
  total: 0,
  lowStock: 0,
  totalValue: 0,
  suppliers: 0
})

// 表单引用
const materialFormRef = ref()
const purchaseFormRef = ref()

// 方法
const fetchMaterials = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    materials.value = [
      {
        id: 1,
        code: 'MAT001',
        name: '机油滤清器',
        category: 'oil',
        specification: 'OEM-123456',
        unit: 'piece',
        currentStock: 25,
        minStock: 10,
        unitPrice: 35.50,
        supplierId: 1,
        lastPurchase: '2024-01-10',
        createdAt: '2023-12-01',
        description: '适用于多种车型的机油滤清器',
        stockHistory: [
          { date: '2024-01-10', type: 'in', quantity: 50, reason: '采购入库', operator: '张三' },
          { date: '2024-01-08', type: 'out', quantity: 5, reason: '维修使用', operator: '李四' }
        ]
      },
      {
        id: 2,
        code: 'MAT002',
        name: '刹车片',
        category: 'brake',
        specification: 'BP-789',
        unit: 'set',
        currentStock: 8,
        minStock: 15,
        unitPrice: 180.00,
        supplierId: 2,
        lastPurchase: '2024-01-05',
        createdAt: '2023-11-15',
        description: '高性能陶瓷刹车片',
        stockHistory: [
          { date: '2024-01-05', type: 'in', quantity: 20, reason: '采购入库', operator: '王五' }
        ]
      }
    ]
    
    // 更新统计数据
    stats.total = materials.value.length
    stats.lowStock = materials.value.filter(m => m.currentStock <= m.minStock).length
    stats.totalValue = materials.value.reduce((sum, m) => sum + (m.currentStock * m.unitPrice), 0)
    stats.suppliers = suppliers.value.length
    
    pagination.total = materials.value.length
  } catch (error) {
    ElMessage.error('获取材料列表失败')
  } finally {
    loading.value = false
  }
}

const fetchSuppliers = async () => {
  try {
    // 模拟数据
    suppliers.value = [
      {
        id: 1,
        name: '优质配件供应商',
        contact: '张经理',
        phone: '13800138001',
        email: 'zhang@supplier1.com',
        address: '北京市朝阳区工业园区1号',
        status: 'active'
      },
      {
        id: 2,
        name: '专业刹车系统公司',
        contact: '李经理',
        phone: '13800138002',
        email: 'li@supplier2.com',
        address: '上海市浦东新区制造基地2号',
        status: 'active'
      }
    ]
    
    stats.suppliers = suppliers.value.length
  } catch (error) {
    ElMessage.error('获取供应商列表失败')
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
    supplier: '',
    showLowStock: false
  })
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedMaterials.value = selection
}

const viewMaterial = (material) => {
  selectedMaterial.value = material
  showDetailDialog.value = true
}

const editMaterial = (material) => {
  editingMaterial.value = material
  Object.assign(materialForm, material)
  showAddDialog.value = true
}

const saveMaterial = async () => {
  if (!materialFormRef.value) return
  
  try {
    await materialFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingMaterial.value) {
      ElMessage.success('材料更新成功')
    } else {
      ElMessage.success('材料添加成功')
    }
    
    showAddDialog.value = false
    await fetchMaterials()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingMaterial.value = null
  Object.assign(materialForm, {
    code: '',
    name: '',
    category: '',
    specification: '',
    unit: '',
    unitPrice: 0,
    minStock: 0,
    supplierId: '',
    description: ''
  })
  if (materialFormRef.value) {
    materialFormRef.value.clearValidate()
  }
}

const submitPurchase = async () => {
  if (!purchaseFormRef.value) return
  
  try {
    await purchaseFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('采购入库成功')
    showPurchaseDialog.value = false
    
    // 重置表单
    Object.assign(purchaseForm, {
      materialId: '',
      quantity: 1,
      unitPrice: 0,
      supplierId: '',
      notes: ''
    })
    
    await fetchMaterials()
  } catch (error) {
    console.error('采购失败:', error)
  } finally {
    saving.value = false
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const material = materials.value.find(m => m.id === parseInt(id))
  
  switch (action) {
    case 'purchase':
      purchaseForm.materialId = material.id
      purchaseForm.unitPrice = material.unitPrice
      purchaseForm.supplierId = material.supplierId
      showPurchaseDialog.value = true
      break
    case 'adjust':
      try {
        const { value } = await ElMessageBox.prompt('请输入调整后的库存数量', '库存调整', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: material.currentStock.toString(),
          inputType: 'number'
        })
        
        ElMessage.success('库存调整成功')
        await fetchMaterials()
      } catch {
        // 用户取消
      }
      break
    case 'history':
      viewMaterial(material)
      break
    case 'delete':
      try {
        await ElMessageBox.confirm(
          `确定要删除材料 ${material.name} 吗？此操作不可恢复。`,
          '确认删除',
          { type: 'warning' }
        )
        ElMessage.success('删除成功')
        await fetchMaterials()
      } catch {
        // 用户取消
      }
      break
  }
}

const exportMaterials = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchMaterials()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchMaterials()
}

// 辅助方法
const getCategoryName = (category) => {
  const categoryMap = {
    engine: '发动机配件',
    brake: '制动系统',
    electrical: '电气配件',
    body: '车身配件',
    oil: '润滑油品'
  }
  return categoryMap[category] || category
}

const getSupplierName = (supplierId) => {
  const supplier = suppliers.value.find(s => s.id === supplierId)
  return supplier ? supplier.name : '未知供应商'
}

const getStockClass = (material) => {
  if (material.currentStock <= material.minStock) {
    return 'stock-warning'
  }
  return 'stock-normal'
}

const getRowClassName = ({ row }) => {
  if (row.currentStock <= row.minStock) {
    return 'warning-row'
  }
  return ''
}

// 生命周期
onMounted(() => {
  fetchSuppliers()
  fetchMaterials()
})
</script>

<style scoped>
.materials-container {
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

.stat-icon.warning {
  color: #e6a23c;
}

.stat-icon.value {
  color: #67c23a;
}

.stat-icon.supplier {
  color: #409eff;
}

.table-card {
  margin-bottom: 20px;
}

.stock-warning {
  color: #f56c6c;
  font-weight: bold;
}

.stock-normal {
  color: #67c23a;
}

.value-text {
  font-weight: bold;
  color: #409eff;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.material-detail {
  padding: 20px 0;
}

.supplier-management {
  padding: 10px 0;
}

.supplier-form {
  margin-bottom: 20px;
}

.danger {
  color: #f56c6c;
}

:deep(.warning-row) {
  background-color: #fef0f0;
}

:deep(.warning-row:hover) {
  background-color: #fde2e2 !important;
}

@media (max-width: 768px) {
  .materials-container {
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