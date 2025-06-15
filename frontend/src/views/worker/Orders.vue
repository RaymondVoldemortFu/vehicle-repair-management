<template>
  <div class="page-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>我的维修订单</h1>
      <p>查看和管理分配给您的维修任务</p>
    </div>
    <div class="page-actions">
      <el-button type="primary" @click="openAvailableOrdersDialog">
        <el-icon><Plus /></el-icon>
        接单中心
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
       <el-form :model="searchForm" layout="inline" @submit.prevent="fetchData">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="关键词">
              <el-input
                v-model="searchForm.keyword"
                placeholder="搜索订单号或车辆信息"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
             <el-form-item label="状态">
                <el-select v-model="searchForm.status" placeholder="订单状态" clearable @change="handleSearch">
                  <el-option label="待处理" value="pending" />
                  <el-option label="已派单" value="assigned" />
                  <el-option label="维修中" value="in_progress" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已取消" value="cancelled" />
                </el-select>
             </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="table-card">
      <el-table v-loading="loading" :data="orders" style="width: 100%">
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column label="车牌号" width="150">
          <template #default="scope">
            {{ scope.row.vehicle?.license_plate }}
          </template>
        </el-table-column>
        <el-table-column label="车型" width="180">
          <template #default="scope">
            {{ scope.row.vehicle?.manufacturer }} {{ scope.row.vehicle?.model }}
          </template>
        </el-table-column>
        <el-table-column label="客户姓名" width="120">
          <template #default="scope">
            {{ scope.row.user?.name }}
          </template>
        </el-table-column>
        <el-table-column label="联系电话" width="150">
          <template #default="scope">
            {{ scope.row.user?.phone || 'N/A' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="问题描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrder(row)">详情</el-button>
            <el-button 
              v-if="row.status === 'assigned'" 
              size="small" 
              type="primary" 
              @click="updateStatus(row.id, 'in_progress')"
            >
              开始维修
            </el-button>
            <el-button 
              v-if="row.status === 'in_progress'" 
              size="small" 
              type="success" 
              @click="openCompletionDialog(row)"
            >
              完成维修
            </el-button>
            <el-button 
              v-if="row.status === 'in_progress'"
              type="danger"
              size="small"
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="订单详情" width="700px">
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ selectedOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedOrder.status)">{{ getStatusName(selectedOrder.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="车主">{{ selectedOrder.user.name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedOrder.user.phone }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">{{ selectedOrder.vehicle.license_plate_number }}</el-descriptions-item>
          <el-descriptions-item label="车型">{{ selectedOrder.vehicle.model }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedOrder.create_time }}</el-descriptions-item>
          <el-descriptions-item label="预计完成时间">{{ selectedOrder.estimated_completion_time }}</el-descriptions-item>
          <el-descriptions-item label="问题描述" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedOrder.internal_notes }}</el-descriptions-item>
        </el-descriptions>
      </div>
       <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 完成维修对话框 -->
    <el-dialog v-model="completionDialogVisible" title="完成维修与材料登记" width="600px" @close="resetCompletionForm">
      <el-form ref="completionFormRef" :model="completionForm" :rules="completionFormRules" label-width="100px">
        <el-form-item label="总工时" prop="work_hours">
          <el-input-number v-model="completionForm.work_hours" :min="0.5" :precision="2" :step="0.5" controls-position="right" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="工作描述" prop="work_description">
          <el-input v-model="completionForm.work_description" type="textarea" :rows="3" placeholder="请输入本次维修工作的详细内容" />
        </el-form-item>
        
        <el-divider>使用材料</el-divider>

        <div v-for="(item, index) in completionForm.used_materials" :key="index" class="material-item">
          <el-form-item 
            :label="'材料 ' + (index + 1)"
            :prop="'used_materials.' + index + '.material_id'"
            :rules="{ required: true, message: '请选择材料', trigger: 'change' }"
          >
            <el-select
              v-model="item.material_id"
              placeholder="选择或搜索材料"
              filterable
              style="width: 100%;"
            >
              <el-option
                v-for="material in allMaterials"
                :key="material.id"
                :label="`${material.name} (库存: ${material.stock})`"
                :value="material.id"
              />
            </el-select>
          </el-form-item>
           <el-form-item 
            label-width="100px"
            :prop="'used_materials.' + index + '.quantity'"
            :rules="{ required: true, type: 'number', min: 1, message: '请输入有效数量', trigger: 'blur' }"
          >
             <el-input-number v-model="item.quantity" :min="1" placeholder="数量" style="width: 100%;"/>
          </el-form-item>
          <el-button type="danger" plain size="small" @click="removeMaterial(index)" class="remove-material-btn">移除</el-button>
        </div>

        <el-button type="primary" plain @click="addMaterial">
          <el-icon><Plus /></el-icon>
          添加材料
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="completionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCompletionForm">提交</el-button>
      </template>
    </el-dialog>

    <!-- 可接订单对话框 -->
    <el-dialog v-model="availableOrdersDialogVisible" title="接单中心" width="80%">
      <el-table v-loading="availableLoading" :data="availableOrders" style="width: 100%">
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column prop="vehicle.license_plate_number" label="车牌号" width="120" />
        <el-table-column prop="description" label="问题描述" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleAcceptOrder(row.id)">
              接单
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="availablePagination.page"
          v-model:page-size="availablePagination.size"
          :page-sizes="[5, 10, 20]"
          :total="availablePagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchAvailableOrders"
          @current-change="fetchAvailableOrders"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getWorkerOrders, updateWorkerOrderStatus, getAvailableOrders, acceptOrder, rejectOrder, completeOrder } from '@/api/repairOrder';
import request from '@/utils/request';

const loading = ref(true);
const showDetailDialog = ref(false);
const selectedOrder = ref(null);
const orders = ref([]);

const availableOrdersDialogVisible = ref(false);
const availableLoading = ref(false);
const availableOrders = ref([]);
const availablePagination = reactive({
  page: 1,
  size: 5,
  total: 0,
});

const searchForm = reactive({
  keyword: '',
  status: '',
});

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
});

const completionDialogVisible = ref(false);
const completionFormRef = ref(null);
const activeOrder = ref(null);
const allMaterials = ref([]);

const getInitialCompletionForm = () => ({
  work_hours: 1,
  work_description: '',
  used_materials: [],
});

const completionForm = reactive(getInitialCompletionForm());

const completionFormRules = {
  work_hours: [{ required: true, message: '请输入总工时', trigger: 'blur' }],
  work_description: [{ required: true, message: '请输入工作描述', trigger: 'blur' }],
};

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      status: searchForm.status,
    };
    const filteredParams = Object.fromEntries(Object.entries(params).filter(([_, v]) => v !== null && v !== ''));
    const response = await request.get('/repair-orders/worker-orders', { params: filteredParams });
    orders.value = response.items;
    pagination.total = response.total;
  } catch (error) {
    console.error('获取订单列表失败:', error);
    ElMessage.error('获取订单列表失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  fetchData();
};

const resetSearch = () => {
  searchForm.keyword = '';
  searchForm.status = '';
  handleSearch();
};

const viewOrder = (order) => {
  selectedOrder.value = order;
  showDetailDialog.value = true;
};

const updateStatus = async (orderId, newStatus) => {
  try {
    const actionText = newStatus === 'in_progress' ? '开始维修' : '完成维修';
    await ElMessageBox.confirm(`确定要将此订单状态更新为"${getStatusName(newStatus)}"吗？`, `确认${actionText}`, {
      type: 'warning',
    });
    
    await updateWorkerOrderStatus(orderId, { status: newStatus });
    ElMessage.success('状态更新成功');
    fetchData();
  } catch (error) {
     if (error !== 'cancel') {
        console.error('状态更新失败:', error);
        ElMessage.error(error.response?.data?.detail || '状态更新失败');
     }
  }
};

const getStatusName = (status) => {
  const map = {
    pending: '待处理',
    assigned: '已派单',
    in_progress: '维修中',
    completed: '已完成',
    cancelled: '已取消'
  };
  return map[status] || status;
};

const getStatusTagType = (status) => {
  const map = {
    pending: 'info',
    assigned: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  };
  return map[status] || 'info';
};

const openAvailableOrdersDialog = () => {
  availableOrdersDialogVisible.value = true;
  fetchAvailableOrders();
};

const fetchAvailableOrders = async () => {
  availableLoading.value = true;
  try {
    const params = { page: availablePagination.page, size: availablePagination.size };
    const response = await request.get('/repair-orders/available', { params });
    availableOrders.value = response.items;
    availablePagination.total = response.total;
  } catch (error) {
    console.error('获取可接订单失败:', error);
    ElMessage.error('获取可接订单失败');
  } finally {
    availableLoading.value = false;
  }
};

const handleAcceptOrder = async (orderId) => {
  try {
    await request.post(`/repair-orders/${orderId}/accept`);
    ElMessage.success('接单成功');
    fetchAvailableOrders(); // 刷新可接订单列表
    fetchData(); // 刷新我的订单列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '接单失败');
  }
};

const handleReject = (order) => {
  ElMessageBox.confirm(`确定要拒绝订单 ${order.order_number} 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await request.put(`/repair-orders/${order.id}/reject`);
      ElMessage.success('订单已拒绝');
      fetchData();
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败');
    }
  });
};

const fetchAllMaterials = async () => {
  try {
    const response = await request.get('/materials/');
    allMaterials.value = response.items;
  } catch (error) {
    ElMessage.error('获取材料列表失败');
    console.error(error);
  }
};

const addMaterial = () => {
  completionForm.used_materials.push({
    material_id: null,
    quantity: 1,
  });
};

const removeMaterial = (index) => {
  completionForm.used_materials.splice(index, 1);
};

const resetCompletionForm = () => {
  Object.assign(completionForm, getInitialCompletionForm());
  completionFormRef.value?.resetFields();
};

const openCompletionDialog = (order) => {
  resetCompletionForm();
  activeOrder.value = order;
  if (allMaterials.value.length === 0) {
    fetchAllMaterials();
  }
  completionDialogVisible.value = true;
};

const submitCompletionForm = async () => {
  if (!completionFormRef.value) return;
  await completionFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const payload = {
          work_hours: completionForm.work_hours,
          work_description: completionForm.work_description,
          used_materials: completionForm.used_materials.map(item => ({
            material_id: item.material_id,
            quantity: item.quantity
          }))
        };
        await request.post(`/repair-orders/worker-orders/${activeOrder.value.id}/complete`, payload);
        ElMessage.success('订单已成功完成');
        completionDialogVisible.value = false;
        fetchData();
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败');
        console.error(error);
      }
    }
  });
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.page-actions {
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