<template>
  <div class="profile-container">
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息和账户安全</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <div>
                <el-button v-if="!editingBasicInfo" type="primary" size="small" @click="editingBasicInfo = true">编辑</el-button>
                <div v-else>
                  <el-button size="small" @click="cancelEditBasicInfo">取消</el-button>
                  <el-button type="primary" size="small" @click="saveBasicInfo">保存</el-button>
                </div>
              </div>
            </div>
          </template>

          <el-form
            ref="basicInfoFormRef"
            :model="profileForm"
            :rules="basicInfoRules"
            label-width="100px"
            v-loading="loading"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="profileForm.name" :disabled="!editingBasicInfo" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工号">
                  <el-input :value="profileForm.employee_id" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="profileForm.phone" :disabled="!editingBasicInfo" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" :disabled="!editingBasicInfo" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="入职时间">
                  <el-input :value="profileForm.hire_date" disabled />
                </el-form-item>
              </el-col>
               <el-col :span="12">
                <el-form-item label="状态">
                    <el-tag>{{ profileForm.status }}</el-tag>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

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
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getMyProfile, updateMyProfile, changeMyPassword } from '@/api/worker';

const loading = ref(true);
const editingBasicInfo = ref(false);
const basicInfoFormRef = ref(null);
const passwordFormRef = ref(null);

const profileForm = ref({});
let originalProfileData = {};

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
});

const basicInfoRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur', type: 'email' }],
};

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur',
    },
  ],
};

const fetchProfile = async () => {
  loading.value = true;
  try {
    const response = await getMyProfile();
    profileForm.value = response;
    originalProfileData = JSON.parse(JSON.stringify(response));
  } catch (error) {
    ElMessage.error('获取个人信息失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const cancelEditBasicInfo = () => {
  profileForm.value = JSON.parse(JSON.stringify(originalProfileData));
  editingBasicInfo.value = false;
};

const saveBasicInfo = async () => {
  if (!basicInfoFormRef.value) return;
  await basicInfoFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const updateData = {
          name: profileForm.value.name,
          phone: profileForm.value.phone,
          email: profileForm.value.email,
        };
        await updateMyProfile(updateData);
        ElMessage.success('个人信息更新成功');
        editingBasicInfo.value = false;
        fetchProfile(); // Re-fetch to get the latest data
      } catch (error) {
        ElMessage.error('更新失败');
        console.error(error);
      }
    }
  });
};

const changePassword = async () => {
  if (!passwordFormRef.value) return;
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await changeMyPassword({
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password,
        });
        ElMessage.success('密码修改成功');
        passwordFormRef.value.resetFields();
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '密码修改失败');
        console.error(error);
      }
    }
  });
};

onMounted(() => {
  fetchProfile();
});
</script>

<style scoped>
.profile-container {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.info-card, .password-card {
  margin-bottom: 20px;
}
</style> 