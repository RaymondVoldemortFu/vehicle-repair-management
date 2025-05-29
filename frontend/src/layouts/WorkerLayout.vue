<template>
  <el-container class="worker-layout">
    <el-header class="header">
      <div class="header-left">
        <h2>车辆维修管理系统 - 工人端</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" :src="userInfo?.avatar">
              <el-icon><Tools /></el-icon>
            </el-avatar>
            <span class="username">{{ userInfo?.name }}</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>个人资料
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-aside width="240px" class="sidebar">
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#1890ff"
        >
          <el-menu-item index="/worker/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          
          <el-menu-item index="/worker/orders">
            <el-icon><List /></el-icon>
            <span>我的订单</span>
          </el-menu-item>

          <el-menu-item index="/worker/wages">
            <el-icon><Money /></el-icon>
            <span>工资查询</span>
          </el-menu-item>

          <el-menu-item index="/worker/profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const userInfo = computed(() => authStore.userInfo)

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/worker/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          type: 'warning'
        })
        authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消操作
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.worker-layout {
  height: 100vh;
  width: 100%;
}

.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .header-left {
    h2 {
      margin: 0;
      color: #1890ff;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      .username {
        margin: 0 8px;
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.sidebar {
  background: #001529;
  overflow: hidden;

  .sidebar-menu {
    border: none;
    height: 100%;

    :deep(.el-menu-item) {
      height: 48px;
      line-height: 48px;
      border-radius: 0 !important;

      &:hover {
        background-color: #1890ff !important;
      }

      &.is-active {
        background-color: #1890ff !important;
      }

      .el-icon {
        margin-right: 8px;
      }
    }
  }
}

.main-content {
  background: #f5f7fa;
  padding: 0;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .header {
    .header-left h2 {
      font-size: 16px;
    }
  }
}
</style> 