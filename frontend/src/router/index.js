import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresGuest: true }
  },
  // 用户端路由
  {
    path: '/user',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true, role: 'user' },
    children: [
      {
        path: '',
        redirect: '/user/dashboard'
      },
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: () => import('@/views/user/Dashboard.vue')
      },
      {
        path: 'vehicles',
        name: 'UserVehicles',
        component: () => import('@/views/user/Vehicles.vue')
      },
      {
        path: 'orders',
        name: 'UserOrders',
        component: () => import('@/views/user/Orders.vue')
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/user/Profile.vue')
      },
      {
        path: 'feedback',
        name: 'UserFeedback',
        component: () => import('@/views/user/Feedback.vue')
      }
    ]
  },
  // 管理员端路由
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue')
      },
      {
        path: 'vehicles',
        name: 'AdminVehicles',
        component: () => import('@/views/admin/Vehicles.vue')
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: () => import('@/views/admin/Orders.vue')
      },
      {
        path: 'workers',
        name: 'AdminWorkers',
        component: () => import('@/views/admin/Workers.vue')
      },
      {
        path: 'services',
        name: 'AdminServices',
        component: () => import('@/views/admin/Services.vue')
      },
      {
        path: 'materials',
        name: 'AdminMaterials',
        component: () => import('@/views/admin/Materials.vue')
      },
      {
        path: 'feedback',
        name: 'AdminFeedback',
        component: () => import('@/views/admin/Feedback.vue')
      },
      {
        path: 'wages',
        name: 'AdminWages',
        component: () => import('@/views/admin/Wages.vue')
      },
      {
        path: 'analytics',
        name: 'AdminAnalytics',
        component: () => import('@/views/admin/Analytics.vue')
      },
      {
        path: 'logs',
        name: 'AdminLogs',
        component: () => import('@/views/admin/Logs.vue')
      },
      {
        path: 'system',
        name: 'AdminSystem',
        component: () => import('@/views/admin/System.vue')
      }
    ]
  },
  // 维修工人端路由
  {
    path: '/worker',
    component: () => import('@/layouts/WorkerLayout.vue'),
    meta: { requiresAuth: true, role: 'worker' },
    children: [
      {
        path: '',
        redirect: '/worker/dashboard'
      },
      {
        path: 'dashboard',
        name: 'WorkerDashboard',
        component: () => import('@/views/worker/Dashboard.vue')
      },
      {
        path: 'orders',
        name: 'WorkerOrders',
        component: () => import('@/views/worker/Orders.vue')
      },
      {
        path: 'wages',
        name: 'WorkerWages',
        component: () => import('@/views/worker/Wages.vue')
      },
      {
        path: 'profile',
        name: 'WorkerProfile',
        component: () => import('@/views/worker/Profile.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 需要登录的页面
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isLoggedIn) {
      next('/login')
      return
    }
    
    // 检查角色权限
    const requiredRole = to.meta.role
    if (requiredRole && authStore.userType !== requiredRole) {
      // 重定向到对应的角色首页
      const redirectMap = {
        'user': '/user/dashboard',
        'admin': '/admin/dashboard',
        'worker': '/worker/dashboard'
      }
      next(redirectMap[authStore.userType] || '/login')
      return
    }
  }
  
  // 只允许未登录用户访问的页面
  if (to.matched.some(record => record.meta.requiresGuest)) {
    if (authStore.isLoggedIn) {
      const redirectMap = {
        'user': '/user/dashboard',
        'admin': '/admin/dashboard',
        'worker': '/worker/dashboard'
      }
      next(redirectMap[authStore.userType] || '/')
      return
    }
  }
  
  next()
})

export default router 