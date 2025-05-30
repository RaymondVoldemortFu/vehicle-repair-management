<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索操作内容或用户"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchForm.action_type" placeholder="操作类型" style="width: 150px" clearable>
          <el-option label="登录" value="login" />
          <el-option label="创建" value="create" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="查看" value="view" />
          <el-option label="导出" value="export" />
          <el-option label="系统" value="system" />
        </el-select>
        <el-select v-model="searchForm.user_type" placeholder="用户类型" style="width: 120px" clearable>
          <el-option label="用户" value="user" />
          <el-option label="管理员" value="admin" />
          <el-option label="工人" value="worker" />
        </el-select>
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 240px"
        />
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      <div>
        <el-button type="warning" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出日志
        </el-button>
        <el-button type="danger" @click="handleClear">
          <el-icon><Delete /></el-icon>
          清理日志
        </el-button>
      </div>
    </div>

    <div class="card-container">
      <el-table v-loading="loading" :data="tableData" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="action_type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action_type)" size="small">
              {{ getActionText(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_type" label="用户类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getUserTypeColor(row.user_type)" size="small">
              {{ getUserTypeText(row.user_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="操作用户" width="120" />
        <el-table-column prop="target_type" label="目标类型" width="100" />
        <el-table-column prop="target_id" label="目标ID" width="80" />
        <el-table-column prop="action_description" label="操作描述" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="120" />
        <el-table-column prop="user_agent" label="用户代理" width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="操作时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              详情
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

    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="操作ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionType(currentLog.action_type)">
            {{ getActionText(currentLog.action_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户类型">
          <el-tag :type="getUserTypeColor(currentLog.user_type)">
            {{ getUserTypeText(currentLog.user_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ currentLog.username }}</el-descriptions-item>
        <el-descriptions-item label="目标类型">{{ currentLog.target_type }}</el-descriptions-item>
        <el-descriptions-item label="目标ID">{{ currentLog.target_id }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ formatDate(currentLog.created_at) }}</el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>操作描述</h4>
        <p>{{ currentLog.action_description }}</p>
      </div>

      <div style="margin-top: 20px;">
        <h4>用户代理</h4>
        <p style="word-break: break-all;">{{ currentLog.user_agent }}</p>
      </div>

      <div v-if="currentLog.additional_data" style="margin-top: 20px;">
        <h4>附加数据</h4>
        <el-input
          type="textarea"
          :rows="8"
          :value="formatJson(currentLog.additional_data)"
          readonly
        />
      </div>
    </el-dialog>

    <!-- 清理日志对话框 -->
    <el-dialog v-model="clearVisible" title="清理日志" width="500px">
      <el-form :model="clearForm" label-width="120px">
        <el-form-item label="清理策略">
          <el-radio-group v-model="clearForm.strategy">
            <el-radio label="days">保留最近天数</el-radio>
            <el-radio label="count">保留最新条数</el-radio>
            <el-radio label="all">清空全部</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="clearForm.strategy === 'days'" label="保留天数">
          <el-input-number v-model="clearForm.days" :min="1" :max="365" />
          <span style="margin-left: 8px; color: #909399;">天</span>
        </el-form-item>
        <el-form-item v-if="clearForm.strategy === 'count'" label="保留条数">
          <el-input-number v-model="clearForm.count" :min="100" :max="100000" />
          <span style="margin-left: 8px; color: #909399;">条</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="clearVisible = false">取消</el-button>
        <el-button type="danger" :loading="clearing" @click="confirmClear">
          确认清理
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
const clearing = ref(false)
const detailVisible = ref(false)
const clearVisible = ref(false)
const tableData = ref([])
const currentLog = ref({})

const searchForm = reactive({
  keyword: '',
  action_type: '',
  user_type: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const clearForm = reactive({
  strategy: 'days',
  days: 30,
  count: 10000
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword,
      action_type: searchForm.action_type,
      user_type: searchForm.user_type
    }

    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }

    const response = await request.get('/system/logs', { params })
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取日志失败:', error)
    // 使用模拟数据
    loadMockData()
  } finally {
    loading.value = false
  }
}

// 加载模拟数据
const loadMockData = () => {
  const mockData = Array.from({ length: 20 }, (_, i) => ({
    id: i + 1,
    action_type: ['login', 'create', 'update', 'delete', 'view'][Math.floor(Math.random() * 5)],
    user_type: ['user', 'admin', 'worker'][Math.floor(Math.random() * 3)],
    username: ['张三', '李四', '王五', '赵六', '钱七'][Math.floor(Math.random() * 5)],
    target_type: ['user', 'vehicle', 'order', 'worker'][Math.floor(Math.random() * 4)],
    target_id: Math.floor(Math.random() * 1000) + 1,
    action_description: '用户执行了相关操作',
    ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    created_at: dayjs().subtract(Math.floor(Math.random() * 30), 'day').toISOString(),
    additional_data: '{"details": "操作详细信息"}'
  }))
  
  tableData.value = mockData.slice((pagination.page - 1) * pagination.size, pagination.page * pagination.size)
  pagination.total = mockData.length
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
    action_type: '',
    user_type: '',
    dateRange: []
  })
  handleSearch()
}

// 查看详情
const handleView = (row) => {
  currentLog.value = row
  detailVisible.value = true
}

// 导出日志
const handleExport = async () => {
  try {
    ElMessage.success('导出功能开发中')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 清理日志
const handleClear = () => {
  clearVisible.value = true
}

// 确认清理
const confirmClear = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清理日志吗？此操作不可恢复！',
      '警告',
      { type: 'warning' }
    )

    clearing.value = true
    
    const params = {
      strategy: clearForm.strategy
    }
    
    if (clearForm.strategy === 'days') {
      params.days = clearForm.days
    } else if (clearForm.strategy === 'count') {
      params.count = clearForm.count
    }

    await request.post('/system/logs/clear', params)
    ElMessage.success('日志清理成功')
    clearVisible.value = false
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清理失败:', error)
    }
  } finally {
    clearing.value = false
  }
}

// 获取操作类型
const getActionType = (type) => {
  const typeMap = {
    'login': 'primary',
    'create': 'success',
    'update': 'warning',
    'delete': 'danger',
    'view': 'info',
    'export': 'warning',
    'system': 'info'
  }
  return typeMap[type] || 'info'
}

// 获取操作类型文本
const getActionText = (type) => {
  const textMap = {
    'login': '登录',
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'view': '查看',
    'export': '导出',
    'system': '系统'
  }
  return textMap[type] || '未知'
}

// 获取用户类型颜色
const getUserTypeColor = (type) => {
  const colorMap = {
    'user': 'primary',
    'admin': 'danger',
    'worker': 'success'
  }
  return colorMap[type] || 'info'
}

// 获取用户类型文本
const getUserTypeText = (type) => {
  const textMap = {
    'user': '用户',
    'admin': '管理员',
    'worker': '工人'
  }
  return textMap[type] || '未知'
}

// 格式化JSON
const formatJson = (jsonStr) => {
  try {
    return JSON.stringify(JSON.parse(jsonStr), null, 2)
  } catch {
    return jsonStr
  }
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}
</style> 