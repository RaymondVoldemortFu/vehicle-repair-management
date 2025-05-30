<template>
  <div class="page-container">
    <div class="page-header">
      <h1>服务反馈</h1>
      <p>您的意见和建议是我们改进服务的动力</p>
    </div>

    <el-row :gutter="20">
      <!-- 反馈表单 -->
      <el-col :span="12">
        <div class="card-container">
          <h3>提交反馈</h3>
          <el-form :model="feedbackForm" :rules="feedbackRules" ref="feedbackFormRef" label-width="100px">
            <el-form-item label="反馈类型" prop="type">
              <el-select v-model="feedbackForm.type" style="width: 100%" placeholder="请选择反馈类型">
                <el-option label="服务质量" value="service_quality" />
                <el-option label="系统问题" value="system_issue" />
                <el-option label="功能建议" value="feature_request" />
                <el-option label="投诉建议" value="complaint" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="相关订单" prop="order_id">
              <el-select 
                v-model="feedbackForm.order_id" 
                style="width: 100%" 
                placeholder="选择相关订单（可选）"
                clearable
                filterable
              >
                <el-option 
                  v-for="order in orders" 
                  :key="order.id" 
                  :label="`${order.order_number} - ${order.description.substring(0, 30)}...`"
                  :value="order.id" 
                />
              </el-select>
            </el-form-item>

            <el-form-item label="标题" prop="title">
              <el-input v-model="feedbackForm.title" placeholder="请输入反馈标题" />
            </el-form-item>

            <el-form-item label="详细内容" prop="content">
              <el-input 
                v-model="feedbackForm.content" 
                type="textarea" 
                :rows="6" 
                placeholder="请详细描述您的问题或建议..." 
              />
            </el-form-item>

            <el-form-item label="服务评分" prop="rating">
              <el-rate v-model="feedbackForm.rating" show-text />
            </el-form-item>

            <el-form-item label="联系方式" prop="contact_info">
              <el-input v-model="feedbackForm.contact_info" placeholder="请输入您的联系方式（可选）" />
            </el-form-item>

            <el-form-item label="附件上传">
              <el-upload
                action="#"
                :before-upload="handleFileUpload"
                :file-list="fileList"
                multiple
                :limit="5"
                accept="image/*,.pdf,.doc,.docx"
              >
                <el-button type="primary">
                  <el-icon><Upload /></el-icon>
                  上传附件
                </el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持jpg/png/pdf/doc格式，单个文件不超过10MB，最多5个文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleSubmit">
                提交反馈
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 历史反馈 -->
      <el-col :span="12">
        <div class="card-container">
          <div class="section-header">
            <h3>我的反馈</h3>
            <el-button size="small" @click="fetchMyFeedbacks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          
          <div class="feedback-list">
            <div v-if="myFeedbacks.length === 0" class="empty-state">
              <el-empty description="暂无反馈记录" />
            </div>
            
            <div 
              v-for="feedback in myFeedbacks" 
              :key="feedback.id" 
              class="feedback-item"
              @click="handleViewFeedback(feedback)"
            >
              <div class="feedback-header">
                <div class="feedback-title">{{ feedback.title }}</div>
                <el-tag :type="getStatusType(feedback.status)" size="small">
                  {{ getStatusText(feedback.status) }}
                </el-tag>
              </div>
              <div class="feedback-content">{{ feedback.content.substring(0, 100) }}...</div>
              <div class="feedback-meta">
                <span class="feedback-type">{{ getTypeText(feedback.type) }}</span>
                <span class="feedback-time">{{ formatDate(feedback.created_at) }}</span>
              </div>
              <div v-if="feedback.rating" class="feedback-rating">
                <el-rate v-model="feedback.rating" disabled size="small" />
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 反馈详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="反馈详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="反馈类型">{{ getTypeText(currentFeedback.type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentFeedback.status)">
            {{ getStatusText(currentFeedback.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="相关订单">
          {{ currentFeedback.order_number || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="服务评分">
          <el-rate v-if="currentFeedback.rating" v-model="currentFeedback.rating" disabled />
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatDate(currentFeedback.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="处理时间">
          {{ currentFeedback.handled_at ? formatDate(currentFeedback.handled_at) : '未处理' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <div style="margin-top: 20px;">
        <h4>标题</h4>
        <p>{{ currentFeedback.title }}</p>
      </div>

      <div style="margin-top: 20px;">
        <h4>详细内容</h4>
        <p style="white-space: pre-line;">{{ currentFeedback.content }}</p>
      </div>

      <div v-if="currentFeedback.reply" style="margin-top: 20px;">
        <h4>官方回复</h4>
        <div class="reply-content">
          <p style="white-space: pre-line;">{{ currentFeedback.reply }}</p>
          <div class="reply-meta">
            <span>回复时间：{{ formatDate(currentFeedback.replied_at) }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'

const submitting = ref(false)
const detailDialogVisible = ref(false)
const myFeedbacks = ref([])
const orders = ref([])
const fileList = ref([])
const currentFeedback = ref({})

const feedbackFormRef = ref()

const feedbackForm = reactive({
  type: '',
  order_id: '',
  title: '',
  content: '',
  rating: 5,
  contact_info: ''
})

const feedbackRules = {
  type: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入反馈标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度为5-100个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入详细内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度为10-1000个字符', trigger: 'blur' }
  ]
}

// 获取我的反馈
const fetchMyFeedbacks = async () => {
  try {
    const response = await request.get('/feedback/my-feedback')
    // 映射后端数据字段到前端期望的字段
    myFeedbacks.value = (response || []).map(item => ({
      id: item.id,
      type: item.feedback_type,
      title: item.title || '无标题', // 直接使用后端的title字段
      content: item.comment || '',
      rating: item.rating,
      status: item.status,
      created_at: item.created_at,
      order_number: item.order_id ? `订单ID: ${item.order_id}` : null,
      reply: item.response || null,
      replied_at: item.response_time || null
    }))
  } catch (error) {
    console.error('获取反馈列表失败:', error)
    // 使用模拟数据
    myFeedbacks.value = [
      {
        id: 1,
        type: 'service_quality',
        title: '服务很满意',
        content: '维修师傅很专业，服务态度很好，修理效果也很满意。',
        rating: 5,
        status: 'published',
        created_at: new Date().toISOString(),
        reply: null,
        replied_at: null
      }
    ]
  }
}

// 获取订单列表
const fetchOrders = async () => {
  try {
    const response = await request.get('/repair-orders/my-orders')
    orders.value = response.items || []
  } catch (error) {
    console.error('获取订单列表失败:', error)
  }
}

// 处理文件上传
const handleFileUpload = (file) => {
  const isValidType = ['image/jpeg', 'image/png', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 jpg/png/pdf/doc/docx 格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }

  // 这里应该上传到服务器
  ElMessage.success('文件上传功能开发中')
  return false
}

// 提交反馈
const handleSubmit = async () => {
  const valid = await feedbackFormRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    // 映射前端字段到后端期望的字段
    const submitData = {
      order_id: feedbackForm.order_id || null,
      title: feedbackForm.title,  // 添加title字段
      rating: feedbackForm.rating,
      comment: feedbackForm.content,  // 后端期望comment字段
      feedback_type: feedbackForm.type || 'service_rating',
      contact_info: feedbackForm.contact_info
    }
    
    await request.post('/feedback/', submitData)
    ElMessage.success('反馈提交成功，我们会尽快处理')
    resetForm()
    fetchMyFeedbacks()
  } catch (error) {
    console.error('提交反馈失败:', error)
    ElMessage.error('提交反馈失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(feedbackForm, {
    type: '',
    order_id: '',
    title: '',
    content: '',
    rating: 5,
    contact_info: ''
  })
  fileList.value = []
}

// 查看反馈详情
const handleViewFeedback = (feedback) => {
  currentFeedback.value = feedback
  detailDialogVisible.value = true
}

// 获取反馈类型文本
const getTypeText = (type) => {
  const typeMap = {
    'service_quality': '服务质量',
    'service_rating': '服务评价',
    'system_issue': '系统问题',
    'feature_request': '功能建议',
    'suggestion': '建议',
    'complaint': '投诉建议',
    'other': '其他'
  }
  return typeMap[type] || '未知'
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'processing': 'primary',
    'replied': 'success',
    'published': 'success',
    'closed': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'replied': '已回复',
    'published': '已发布',
    'closed': '已关闭'
  }
  return statusMap[status] || '未知'
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchMyFeedbacks()
  fetchOrders()
})
</script>

<style lang="scss" scoped>
.page-header {
  margin-bottom: 24px;

  h1 {
    margin: 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;
  }

  p {
    margin: 8px 0 0 0;
    color: #606266;
    font-size: 14px;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    color: #303133;
    font-size: 16px;
    font-weight: 600;
  }
}

.feedback-list {
  max-height: 600px;
  overflow-y: auto;
}

.feedback-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #c6e2ff;
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  }

  .feedback-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .feedback-title {
      font-weight: 600;
      color: #303133;
      font-size: 14px;
    }
  }

  .feedback-content {
    color: #606266;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 8px;
  }

  .feedback-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #909399;
    margin-bottom: 8px;
  }

  .feedback-rating {
    display: flex;
    align-items: center;
  }
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.reply-content {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 16px;
  
  .reply-meta {
    margin-top: 12px;
    font-size: 12px;
    color: #909399;
    text-align: right;
  }
}

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

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 20px;
  }

  .feedback-item {
    padding: 12px;

    .feedback-meta {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }
  }
}
</style> 