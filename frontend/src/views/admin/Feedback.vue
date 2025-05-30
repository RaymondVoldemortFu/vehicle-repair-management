<template>
  <div class="feedback-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>反馈管理</h1>
        <p class="page-description">管理用户反馈、投诉建议和满意度调查</p>
      </div>
      <div class="header-right">
        <el-button @click="exportFeedback">
          <el-icon><Download /></el-icon>
          导出反馈
        </el-button>
        <el-button type="primary" @click="showStatsDialog = true">
          <el-icon><DataAnalysis /></el-icon>
          统计分析
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="5">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户名或反馈内容"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="3">
          <el-select v-model="searchForm.type" placeholder="反馈类型" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="服务评价" value="rating" />
            <el-option label="投诉建议" value="complaint" />
            <el-option label="系统问题" value="system" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="searchForm.status" placeholder="处理状态" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="searchForm.rating" placeholder="评分" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="5星" value="5" />
            <el-option label="4星" value="4" />
            <el-option label="3星" value="3" />
            <el-option label="2星" value="2" />
            <el-option label="1星" value="1" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="5">
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总反馈数</div>
          </div>
          <el-icon class="stat-icon"><ChatDotRound /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.pending }}</div>
            <div class="stat-label">待处理</div>
          </div>
          <el-icon class="stat-icon pending"><Clock /></el-icon>
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
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.satisfaction }}%</div>
            <div class="stat-label">满意度</div>
          </div>
          <el-icon class="stat-icon satisfaction"><TrendCharts /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 反馈列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="feedbacks"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :row-class-name="getRowClassName"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="反馈ID" width="100" />
        <el-table-column prop="user" label="用户" width="120">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="30" :src="row.user.avatar">
                {{ row.user.name.charAt(0) }}
              </el-avatar>
              <span class="user-name">{{ row.user.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" width="200" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" min-width="250" show-overflow-tooltip />
        <el-table-column prop="rating" label="评分" width="120">
          <template #default="{ row }">
            <el-rate
              v-if="row.rating"
              v-model="row.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="150" />
        <el-table-column prop="assignee" label="处理人" width="100">
          <template #default="{ row }">
            {{ row.assignee || '未分配' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewFeedback(row)">详情</el-button>
            <el-button size="small" type="primary" @click="handleFeedback(row)">处理</el-button>
            <el-dropdown @command="handleCommand">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`assign-${row.id}`">分配处理人</el-dropdown-item>
                  <el-dropdown-item :command="`reply-${row.id}`">回复</el-dropdown-item>
                  <el-dropdown-item :command="`close-${row.id}`" divided>关闭</el-dropdown-item>
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

    <!-- 反馈详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="反馈详情" width="800px">
      <div v-if="selectedFeedback" class="feedback-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="反馈ID">{{ selectedFeedback.id }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ selectedFeedback.user.name }}</el-descriptions-item>
          <el-descriptions-item label="反馈类型">
            <el-tag :type="getTypeTagType(selectedFeedback.type)">
              {{ getTypeName(selectedFeedback.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="getStatusTagType(selectedFeedback.status)">
              {{ getStatusName(selectedFeedback.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="评分">
            <el-rate
              v-if="selectedFeedback.rating"
              v-model="selectedFeedback.rating"
              disabled
              show-score
            />
            <span v-else>无评分</span>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ selectedFeedback.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="处理人">{{ selectedFeedback.assignee || '未分配' }}</el-descriptions-item>
          <el-descriptions-item label="关联订单">{{ selectedFeedback.orderId || '无' }}</el-descriptions-item>
          <el-descriptions-item label="反馈标题" :span="2">{{ selectedFeedback.title }}</el-descriptions-item>
          <el-descriptions-item label="反馈内容" :span="2">
            <div class="feedback-content">{{ selectedFeedback.content }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 附件 -->
        <div v-if="selectedFeedback.attachments && selectedFeedback.attachments.length" class="attachments">
          <el-divider>附件</el-divider>
          <div class="attachment-list">
            <div
              v-for="(attachment, index) in selectedFeedback.attachments"
              :key="index"
              class="attachment-item"
            >
              <el-image
                v-if="attachment.type === 'image'"
                :src="attachment.url"
                :preview-src-list="[attachment.url]"
                fit="cover"
                style="width: 100px; height: 100px"
              />
              <div v-else class="file-attachment">
                <el-icon><Document /></el-icon>
                <span>{{ attachment.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 处理记录 -->
        <el-divider>处理记录</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="(record, index) in selectedFeedback.processHistory"
            :key="index"
            :timestamp="record.timestamp"
            :type="getTimelineType(record.action)"
          >
            <div class="timeline-content">
              <div class="timeline-title">{{ record.action }}</div>
              <div class="timeline-operator">操作人：{{ record.operator }}</div>
              <div v-if="record.content" class="timeline-detail">{{ record.content }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>

    <!-- 处理反馈对话框 -->
    <el-dialog v-model="showHandleDialog" title="处理反馈" width="600px">
      <el-form
        ref="handleFormRef"
        :model="handleForm"
        :rules="handleFormRules"
        label-width="100px"
      >
        <el-form-item label="处理状态" prop="status">
          <el-select v-model="handleForm.status" placeholder="选择状态" style="width: 100%">
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理结果" prop="result">
          <el-input
            v-model="handleForm.result"
            type="textarea"
            :rows="4"
            placeholder="请输入处理结果"
          />
        </el-form-item>
        <el-form-item label="回复内容">
          <el-input
            v-model="handleForm.reply"
            type="textarea"
            :rows="3"
            placeholder="回复给用户的内容（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHandleDialog = false">取消</el-button>
        <el-button type="primary" @click="submitHandle" :loading="saving">提交</el-button>
      </template>
    </el-dialog>

    <!-- 统计分析对话框 -->
    <el-dialog v-model="showStatsDialog" title="反馈统计分析" width="1000px">
      <div class="stats-analysis">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card title="反馈类型分布">
              <div ref="typeChartRef" style="height: 300px"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card title="满意度趋势">
              <div ref="ratingChartRef" style="height: 300px"></div>
            </el-card>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="24">
            <el-card title="月度反馈统计">
              <div ref="monthlyChartRef" style="height: 300px"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Download, DataAnalysis, ChatDotRound, Clock, Star, TrendCharts, 
  ArrowDown, Document 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showDetailDialog = ref(false)
const showHandleDialog = ref(false)
const showStatsDialog = ref(false)
const selectedFeedback = ref(null)
const selectedFeedbacks = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  status: '',
  rating: '',
  dateRange: null
})

// 处理表单
const handleForm = reactive({
  status: '',
  result: '',
  reply: ''
})

// 表单验证规则
const handleFormRules = {
  status: [{ required: true, message: '请选择处理状态', trigger: 'change' }],
  result: [{ required: true, message: '请输入处理结果', trigger: 'blur' }]
}

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 数据
const feedbacks = ref([])

// 统计数据
const stats = reactive({
  total: 0,
  pending: 0,
  avgRating: 0,
  satisfaction: 0
})

// 表单引用
const handleFormRef = ref()
const typeChartRef = ref()
const ratingChartRef = ref()
const monthlyChartRef = ref()

// 方法
const fetchFeedbacks = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    feedbacks.value = [
      {
        id: 'FB001',
        user: {
          name: '张三',
          avatar: '',
          phone: '13800138001'
        },
        type: 'rating',
        title: '服务很满意',
        content: '维修师傅很专业，服务态度很好，修车质量也不错，下次还会来的。',
        rating: 5,
        status: 'completed',
        createdAt: '2024-01-15 14:30:00',
        assignee: '客服小王',
        orderId: 'ORD001',
        attachments: [
          { type: 'image', url: '/images/feedback1.jpg', name: '维修后照片' }
        ],
        processHistory: [
          {
            timestamp: '2024-01-15 14:30:00',
            action: '用户提交反馈',
            operator: '张三',
            content: '用户对服务表示满意'
          },
          {
            timestamp: '2024-01-15 15:00:00',
            action: '客服回复',
            operator: '客服小王',
            content: '感谢您的好评，我们会继续努力提供优质服务'
          }
        ]
      },
      {
        id: 'FB002',
        user: {
          name: '李四',
          avatar: '',
          phone: '13800138002'
        },
        type: 'complaint',
        title: '等待时间过长',
        content: '预约的时间是上午9点，但是等到10点半才开始维修，希望能改善时间管理。',
        rating: 2,
        status: 'processing',
        createdAt: '2024-01-14 16:45:00',
        assignee: '主管张经理',
        orderId: 'ORD002',
        attachments: [],
        processHistory: [
          {
            timestamp: '2024-01-14 16:45:00',
            action: '用户提交投诉',
            operator: '李四',
            content: '对等待时间过长表示不满'
          },
          {
            timestamp: '2024-01-14 17:00:00',
            action: '分配处理人',
            operator: '系统',
            content: '已分配给主管张经理处理'
          }
        ]
      }
    ]
    
    // 更新统计数据
    stats.total = feedbacks.value.length
    stats.pending = feedbacks.value.filter(f => f.status === 'pending').length
    const ratedFeedbacks = feedbacks.value.filter(f => f.rating)
    stats.avgRating = ratedFeedbacks.length > 0 
      ? ratedFeedbacks.reduce((sum, f) => sum + f.rating, 0) / ratedFeedbacks.length 
      : 0
    stats.satisfaction = ratedFeedbacks.length > 0 
      ? Math.round(ratedFeedbacks.filter(f => f.rating >= 4).length / ratedFeedbacks.length * 100)
      : 0
    
    pagination.total = feedbacks.value.length
  } catch (error) {
    ElMessage.error('获取反馈列表失败')
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
    type: '',
    status: '',
    rating: '',
    dateRange: null
  })
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedFeedbacks.value = selection
}

const viewFeedback = (feedback) => {
  selectedFeedback.value = feedback
  showDetailDialog.value = true
}

const handleFeedback = (feedback) => {
  selectedFeedback.value = feedback
  Object.assign(handleForm, {
    status: feedback.status === 'pending' ? 'processing' : feedback.status,
    result: '',
    reply: ''
  })
  showHandleDialog.value = true
}

const submitHandle = async () => {
  if (!handleFormRef.value) return
  
  try {
    await handleFormRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('处理成功')
    showHandleDialog.value = false
    await fetchFeedbacks()
  } catch (error) {
    console.error('处理失败:', error)
  } finally {
    saving.value = false
  }
}

const handleCommand = async (command) => {
  const [action, id] = command.split('-')
  const feedback = feedbacks.value.find(f => f.id === id)
  
  switch (action) {
    case 'assign':
      try {
        const { value } = await ElMessageBox.prompt('请输入处理人姓名', '分配处理人', {
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })
        
        ElMessage.success('分配成功')
        await fetchFeedbacks()
      } catch {
        // 用户取消
      }
      break
    case 'reply':
      try {
        const { value } = await ElMessageBox.prompt('请输入回复内容', '回复用户', {
          confirmButtonText: '发送',
          cancelButtonText: '取消',
          inputType: 'textarea'
        })
        
        ElMessage.success('回复成功')
        await fetchFeedbacks()
      } catch {
        // 用户取消
      }
      break
    case 'close':
      try {
        await ElMessageBox.confirm(
          `确定要关闭反馈 ${feedback.id} 吗？`,
          '确认关闭',
          { type: 'warning' }
        )
        
        ElMessage.success('关闭成功')
        await fetchFeedbacks()
      } catch {
        // 用户取消
      }
      break
  }
}

const exportFeedback = () => {
  ElMessage.success('导出功能开发中')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchFeedbacks()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchFeedbacks()
}

// 辅助方法
const getTypeName = (type) => {
  const typeMap = {
    rating: '服务评价',
    complaint: '投诉建议',
    system: '系统问题',
    other: '其他'
  }
  return typeMap[type] || type
}

const getTypeTagType = (type) => {
  const typeMap = {
    rating: 'success',
    complaint: 'warning',
    system: 'danger',
    other: 'info'
  }
  return typeMap[type] || ''
}

const getStatusName = (status) => {
  const statusMap = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    closed: 'info'
  }
  return typeMap[status] || ''
}

const getTimelineType = (action) => {
  if (action.includes('提交')) return 'primary'
  if (action.includes('完成')) return 'success'
  if (action.includes('关闭')) return 'info'
  return 'primary'
}

const getRowClassName = ({ row }) => {
  if (row.status === 'pending') {
    return 'pending-row'
  }
  return ''
}

// 生命周期
onMounted(() => {
  fetchFeedbacks()
})
</script>

<style scoped>
.feedback-container {
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

.stat-icon.pending {
  color: #e6a23c;
}

.stat-icon.rating {
  color: #f56c6c;
}

.stat-icon.satisfaction {
  color: #67c23a;
}

.table-card {
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.feedback-detail {
  padding: 20px 0;
}

.feedback-content {
  line-height: 1.6;
  color: #606266;
}

.attachments {
  margin: 20px 0;
}

.attachment-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.attachment-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.file-attachment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #f5f7fa;
}

.timeline-content {
  padding: 10px 0;
}

.timeline-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.timeline-operator {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.timeline-detail {
  color: #606266;
  line-height: 1.5;
}

.stats-analysis {
  padding: 20px 0;
}

:deep(.pending-row) {
  background-color: #fdf6ec;
}

:deep(.pending-row:hover) {
  background-color: #faecd8 !important;
}

@media (max-width: 768px) {
  .feedback-container {
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