<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息和工作技能</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧个人信息 -->
      <el-col :span="16">
        <!-- 基本信息 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button 
                v-if="!editingBasicInfo" 
                type="primary" 
                size="small" 
                @click="editBasicInfo"
              >
                编辑
              </el-button>
              <div v-else>
                <el-button size="small" @click="cancelEditBasicInfo">取消</el-button>
                <el-button type="primary" size="small" @click="saveBasicInfo">保存</el-button>
              </div>
            </div>
          </template>

          <el-form
            ref="basicInfoFormRef"
            :model="basicInfoForm"
            :rules="basicInfoRules"
            label-width="100px"
            :disabled="!editingBasicInfo"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="basicInfoForm.name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工号" prop="employeeId">
                  <el-input v-model="basicInfoForm.employeeId" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="basicInfoForm.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="basicInfoForm.email" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="身份证号" prop="idCard">
                  <el-input v-model="basicInfoForm.idCard" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="入职时间" prop="hireDate">
                  <el-date-picker
                    v-model="basicInfoForm.hireDate"
                    type="date"
                    placeholder="选择入职时间"
                    style="width: 100%"
                    disabled
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="地址" prop="address">
                  <el-input v-model="basicInfoForm.address" type="textarea" :rows="2" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 技能管理 -->
        <el-card class="skills-card">
          <template #header>
            <div class="card-header">
              <span>技能管理</span>
              <el-button type="primary" size="small" @click="showAddSkillDialog">
                添加技能
              </el-button>
            </div>
          </template>

          <div class="skills-list">
            <div v-for="skill in workerSkills" :key="skill.id" class="skill-item">
              <div class="skill-info">
                <div class="skill-name">{{ skill.name }}</div>
                <div class="skill-level">
                  <el-rate
                    v-model="skill.level"
                    disabled
                    show-score
                    text-color="#ff9900"
                    score-template="{value} 级"
                  />
                </div>
                <div class="skill-description">{{ skill.description }}</div>
              </div>
              <div class="skill-actions">
                <el-button type="text" size="small" @click="editSkill(skill)">
                  编辑
                </el-button>
                <el-button type="text" size="small" @click="removeSkill(skill.id)">
                  删除
                </el-button>
              </div>
            </div>
            <el-empty v-if="workerSkills.length === 0" description="暂无技能信息" />
          </div>
        </el-card>

        <!-- 工作经历 -->
        <el-card class="experience-card">
          <template #header>
            <div class="card-header">
              <span>工作经历</span>
              <el-button type="primary" size="small" @click="showAddExperienceDialog">
                添加经历
              </el-button>
            </div>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="exp in workExperience"
              :key="exp.id"
              :timestamp="formatDateRange(exp.startDate, exp.endDate)"
              placement="top"
            >
              <el-card>
                <div class="experience-content">
                  <h4>{{ exp.company }} - {{ exp.position }}</h4>
                  <p>{{ exp.description }}</p>
                  <div class="experience-actions">
                    <el-button type="text" size="small" @click="editExperience(exp)">
                      编辑
                    </el-button>
                    <el-button type="text" size="small" @click="removeExperience(exp.id)">
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="workExperience.length === 0" description="暂无工作经历" />
        </el-card>

        <!-- 密码修改 -->
        <el-card class="password-card">
          <template #header>
            <span>密码修改</span>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            style="max-width: 400px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧头像和统计 -->
      <el-col :span="8">
        <!-- 头像上传 -->
        <el-card class="avatar-card">
          <template #header>
            <span>头像</span>
          </template>

          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              action="#"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
            >
              <img v-if="avatarUrl" :src="avatarUrl" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <div class="avatar-tips">
              <p>点击上传头像</p>
              <p class="tips-text">支持 JPG、PNG 格式，文件大小不超过 2MB</p>
            </div>
          </div>
        </el-card>

        <!-- 工作统计 -->
        <el-card class="stats-card">
          <template #header>
            <span>工作统计</span>
          </template>

          <div class="stats-list">
            <div class="stat-item">
              <div class="stat-label">工作年限</div>
              <div class="stat-value">{{ workYears }}年</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">完成订单</div>
              <div class="stat-value">{{ totalOrders }}个</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">客户评分</div>
              <div class="stat-value">
                <el-rate v-model="averageRating" disabled show-score text-color="#ff9900" />
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">技能数量</div>
              <div class="stat-value">{{ workerSkills.length }}项</div>
            </div>
          </div>
        </el-card>

        <!-- 最近成就 -->
        <el-card class="achievements-card">
          <template #header>
            <span>最近成就</span>
          </template>

          <div class="achievements-list">
            <div v-for="achievement in recentAchievements" :key="achievement.id" class="achievement-item">
              <el-icon class="achievement-icon"><Trophy /></el-icon>
              <div class="achievement-content">
                <div class="achievement-title">{{ achievement.title }}</div>
                <div class="achievement-date">{{ formatDate(achievement.date) }}</div>
              </div>
            </div>
            <el-empty v-if="recentAchievements.length === 0" description="暂无成就" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑技能对话框 -->
    <el-dialog
      v-model="skillDialogVisible"
      :title="editingSkill ? '编辑技能' : '添加技能'"
      width="500px"
    >
      <el-form
        ref="skillFormRef"
        :model="skillForm"
        :rules="skillRules"
        label-width="80px"
      >
        <el-form-item label="技能名称" prop="name">
          <el-input v-model="skillForm.name" placeholder="请输入技能名称" />
        </el-form-item>
        <el-form-item label="技能等级" prop="level">
          <el-rate v-model="skillForm.level" show-text />
        </el-form-item>
        <el-form-item label="技能描述" prop="description">
          <el-input
            v-model="skillForm.description"
            type="textarea"
            :rows="3"
            placeholder="请描述您的技能水平和经验"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="skillDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSkill">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加/编辑工作经历对话框 -->
    <el-dialog
      v-model="experienceDialogVisible"
      :title="editingExperience ? '编辑工作经历' : '添加工作经历'"
      width="600px"
    >
      <el-form
        ref="experienceFormRef"
        :model="experienceForm"
        :rules="experienceRules"
        label-width="100px"
      >
        <el-form-item label="公司名称" prop="company">
          <el-input v-model="experienceForm.company" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="experienceForm.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="开始时间" prop="startDate">
          <el-date-picker
            v-model="experienceForm.startDate"
            type="date"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="endDate">
          <el-date-picker
            v-model="experienceForm.endDate"
            type="date"
            placeholder="选择结束时间（在职可不填）"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="工作描述" prop="description">
          <el-input
            v-model="experienceForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述您在该职位的工作内容和成就"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="experienceDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveExperience">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Trophy } from '@element-plus/icons-vue'

// 响应式数据
const basicInfoFormRef = ref()
const passwordFormRef = ref()
const skillFormRef = ref()
const experienceFormRef = ref()

const editingBasicInfo = ref(false)
const avatarUrl = ref('')

// 基本信息表单
const basicInfoForm = ref({
  name: '',
  employeeId: '',
  phone: '',
  email: '',
  idCard: '',
  hireDate: '',
  address: ''
})

const originalBasicInfo = ref({})

// 密码修改表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 技能相关
const workerSkills = ref([])
const skillDialogVisible = ref(false)
const editingSkill = ref(false)
const skillForm = ref({
  id: null,
  name: '',
  level: 0,
  description: ''
})

// 工作经历相关
const workExperience = ref([])
const experienceDialogVisible = ref(false)
const editingExperience = ref(false)
const experienceForm = ref({
  id: null,
  company: '',
  position: '',
  startDate: '',
  endDate: '',
  description: ''
})

// 统计数据
const workYears = ref(3)
const totalOrders = ref(156)
const averageRating = ref(4.8)
const recentAchievements = ref([])

// 表单验证规则
const basicInfoRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
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
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const skillRules = {
  name: [
    { required: true, message: '请输入技能名称', trigger: 'blur' }
  ],
  level: [
    { required: true, message: '请选择技能等级', trigger: 'change' }
  ]
}

const experienceRules = {
  company: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ],
  position: [
    { required: true, message: '请输入职位', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ]
}

// 方法
const fetchUserProfile = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    basicInfoForm.value = {
      name: '张师傅',
      employeeId: 'EMP001',
      phone: '13800138000',
      email: 'zhang@example.com',
      idCard: '110101199001011234',
      hireDate: '2021-03-15',
      address: '北京市朝阳区某某街道123号'
    }
    
    originalBasicInfo.value = { ...basicInfoForm.value }
    avatarUrl.value = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
    
    workerSkills.value = [
      { id: 1, name: '发动机维修', level: 5, description: '精通各类汽车发动机故障诊断与维修' },
      { id: 2, name: '刹车系统', level: 4, description: '熟练掌握刹车系统检修与更换' },
      { id: 3, name: '电路维修', level: 3, description: '具备基本的汽车电路故障排查能力' }
    ]
    
    workExperience.value = [
      {
        id: 1,
        company: '某某汽修厂',
        position: '高级技师',
        startDate: '2021-03-15',
        endDate: null,
        description: '负责高端车型的维修保养工作，具有丰富的故障诊断经验'
      },
      {
        id: 2,
        company: '4S店',
        position: '维修技师',
        startDate: '2018-06-01',
        endDate: '2021-02-28',
        description: '主要负责品牌车型的保养维修，熟悉标准化作业流程'
      }
    ]
    
    recentAchievements.value = [
      { id: 1, title: '月度优秀员工', date: '2024-03-01' },
      { id: 2, title: '客户满意度第一', date: '2024-02-15' },
      { id: 3, title: '技能考核优秀', date: '2024-01-20' }
    ]
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error('Error fetching user profile:', error)
  }
}

// 基本信息编辑
const editBasicInfo = () => {
  editingBasicInfo.value = true
}

const cancelEditBasicInfo = () => {
  basicInfoForm.value = { ...originalBasicInfo.value }
  editingBasicInfo.value = false
}

const saveBasicInfo = async () => {
  try {
    await basicInfoFormRef.value.validate()
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    originalBasicInfo.value = { ...basicInfoForm.value }
    editingBasicInfo.value = false
    ElMessage.success('基本信息更新成功')
  } catch (error) {
    console.error('Error saving basic info:', error)
  }
}

// 头像上传
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('头像图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

const handleAvatarUpload = (options) => {
  // 模拟上传
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarUrl.value = e.target.result
    ElMessage.success('头像上传成功')
  }
  reader.readAsDataURL(options.file)
}

// 密码修改
const changePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('密码修改成功')
    resetPasswordForm()
  } catch (error) {
    console.error('Error changing password:', error)
  }
}

const resetPasswordForm = () => {
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  passwordFormRef.value?.clearValidate()
}

// 技能管理
const showAddSkillDialog = () => {
  editingSkill.value = false
  skillForm.value = {
    id: null,
    name: '',
    level: 0,
    description: ''
  }
  skillDialogVisible.value = true
}

const editSkill = (skill) => {
  editingSkill.value = true
  skillForm.value = { ...skill }
  skillDialogVisible.value = true
}

const saveSkill = async () => {
  try {
    await skillFormRef.value.validate()
    
    if (editingSkill.value) {
      // 编辑技能
      const index = workerSkills.value.findIndex(s => s.id === skillForm.value.id)
      if (index !== -1) {
        workerSkills.value[index] = { ...skillForm.value }
      }
      ElMessage.success('技能更新成功')
    } else {
      // 添加技能
      const newSkill = {
        ...skillForm.value,
        id: Date.now()
      }
      workerSkills.value.push(newSkill)
      ElMessage.success('技能添加成功')
    }
    
    skillDialogVisible.value = false
  } catch (error) {
    console.error('Error saving skill:', error)
  }
}

const removeSkill = async (skillId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个技能吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    workerSkills.value = workerSkills.value.filter(s => s.id !== skillId)
    ElMessage.success('技能删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

// 工作经历管理
const showAddExperienceDialog = () => {
  editingExperience.value = false
  experienceForm.value = {
    id: null,
    company: '',
    position: '',
    startDate: '',
    endDate: '',
    description: ''
  }
  experienceDialogVisible.value = true
}

const editExperience = (experience) => {
  editingExperience.value = true
  experienceForm.value = { ...experience }
  experienceDialogVisible.value = true
}

const saveExperience = async () => {
  try {
    await experienceFormRef.value.validate()
    
    if (editingExperience.value) {
      // 编辑经历
      const index = workExperience.value.findIndex(e => e.id === experienceForm.value.id)
      if (index !== -1) {
        workExperience.value[index] = { ...experienceForm.value }
      }
      ElMessage.success('工作经历更新成功')
    } else {
      // 添加经历
      const newExperience = {
        ...experienceForm.value,
        id: Date.now()
      }
      workExperience.value.push(newExperience)
      ElMessage.success('工作经历添加成功')
    }
    
    experienceDialogVisible.value = false
  } catch (error) {
    console.error('Error saving experience:', error)
  }
}

const removeExperience = async (experienceId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条工作经历吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    workExperience.value = workExperience.value.filter(e => e.id !== experienceId)
    ElMessage.success('工作经历删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

// 工具方法
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateRange = (startDate, endDate) => {
  const start = formatDate(startDate)
  const end = endDate ? formatDate(endDate) : '至今'
  return `${start} - ${end}`
}

// 生命周期
onMounted(() => {
  fetchUserProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.info-card,
.skills-card,
.experience-card,
.password-card,
.avatar-card,
.stats-card,
.achievements-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 头像上传样式 */
.avatar-section {
  text-align: center;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: block;
  margin: 0 auto;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: 0.2s;
  width: 120px;
  height: 120px;
  margin: 0 auto;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
}

.avatar-tips {
  margin-top: 16px;
}

.avatar-tips p {
  margin: 4px 0;
  color: #606266;
}

.tips-text {
  font-size: 12px;
  color: #909399;
}

/* 技能列表样式 */
.skills-list {
  max-height: 400px;
  overflow-y: auto;
}

.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 12px;
}

.skill-info {
  flex: 1;
}

.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.skill-level {
  margin-bottom: 8px;
}

.skill-description {
  color: #606266;
  font-size: 14px;
}

.skill-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 工作经历样式 */
.experience-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.experience-content p {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.6;
}

.experience-actions {
  display: flex;
  gap: 8px;
}

/* 统计卡片样式 */
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  color: #303133;
  font-weight: 600;
  font-size: 16px;
}

/* 成就列表样式 */
.achievements-list {
  max-height: 300px;
  overflow-y: auto;
}

.achievement-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.achievement-item:last-child {
  border-bottom: none;
}

.achievement-icon {
  font-size: 20px;
  color: #f39c12;
  margin-right: 12px;
}

.achievement-content {
  flex: 1;
}

.achievement-title {
  color: #303133;
  font-weight: 500;
  margin-bottom: 4px;
}

.achievement-date {
  color: #909399;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 