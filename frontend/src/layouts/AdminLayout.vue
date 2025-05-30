<template>
  <el-container class="admin-layout">
    <el-header class="header">
      <div class="header-left">
        <h2>车辆维修管理系统 - 管理端</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" :src="userInfo?.avatar">
              <el-icon><UserFilled /></el-icon>
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
          active-text-color="#fff"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><Platform /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          
          <el-sub-menu index="user-management">
            <template #title>
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/admin/users">用户列表</el-menu-item>
            <el-menu-item index="/admin/system">管理员管理</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/admin/vehicles">
            <el-icon><Van /></el-icon>
            <span>车辆管理</span>
          </el-menu-item>

          <el-menu-item index="/admin/orders">
            <el-icon><List /></el-icon>
            <span>维修订单</span>
          </el-menu-item>

          <el-menu-item index="/admin/workers">
            <el-icon><Avatar /></el-icon>
            <span>维修工人</span>
          </el-menu-item>

          <el-sub-menu index="resource-management">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>资源管理</span>
            </template>
            <el-menu-item index="/admin/services">服务项目</el-menu-item>
            <el-menu-item index="/admin/materials">材料库存</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/admin/wages">
            <el-icon><Money /></el-icon>
            <span>工资管理</span>
          </el-menu-item>

          <el-menu-item index="/admin/feedback">
            <el-icon><ChatDotSquare /></el-icon>
            <span>用户反馈</span>
          </el-menu-item>

          <el-menu-item index="/admin/analytics">
            <el-icon><TrendCharts /></el-icon>
            <span>数据分析</span>
          </el-menu-item>

          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <span>系统日志</span>
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
      router.push('/admin/profile')
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
.admin-layout {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;

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
  flex-shrink: 0;

  .sidebar-menu {
    border: none;
    height: 100%;

    :deep(.el-menu-item) {
      height: 48px;
      line-height: 48px;
      border-radius: 0 !important;

      &:hover {
        background-color: #1890ff !important;
        color: #fff !important;
      }

      &.is-active {
        background-color: #1890ff !important;
        color: #fff !important;
      }

      .el-icon {
        margin-right: 8px;
      }

      span {
        color: inherit;
      }
    }

    :deep(.el-sub-menu) {
      .el-sub-menu__title {
        height: 48px;
        line-height: 48px;
        color: #fff;

        &:hover {
          background-color: #1890ff !important;
          color: #fff !important;
        }

        .el-icon {
          margin-right: 8px;
        }
      }

      .el-menu {
        background-color: #000c17;
      }

      .el-menu-item {
        background-color: #000c17;
        color: #fff;

        &:hover {
          background-color: #1890ff !important;
          color: #fff !important;
        }

        &.is-active {
          background-color: #1890ff !important;
          color: #fff !important;
        }
      }
    }
  }
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
  flex: 1;
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