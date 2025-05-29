<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">
        <h2>页面未找到</h2>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const goHome = () => {
  const homeRoutes = {
    'user': '/user/dashboard',
    'admin': '/admin/dashboard',
    'worker': '/worker/dashboard'
  }
  
  if (authStore.isLoggedIn) {
    router.push(homeRoutes[authStore.userType] || '/login')
  } else {
    router.push('/login')
  }
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  color: white;

  .error-code {
    font-size: 120px;
    font-weight: bold;
    line-height: 1;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  }

  .error-message {
    margin-bottom: 40px;

    h2 {
      font-size: 24px;
      margin-bottom: 12px;
      font-weight: 600;
    }

    p {
      font-size: 16px;
      opacity: 0.8;
      margin: 0;
    }
  }

  .error-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .not-found-content {
    .error-code {
      font-size: 80px;
    }

    .error-message h2 {
      font-size: 20px;
    }

    .error-actions {
      flex-direction: column;
      align-items: center;

      .el-button {
        width: 200px;
      }
    }
  }
}
</style> 