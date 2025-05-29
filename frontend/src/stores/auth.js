import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const userType = ref(localStorage.getItem('userType') || '') // 'user', 'admin', 'worker'

  const isLoggedIn = computed(() => !!token.value)
  const isUser = computed(() => userType.value === 'user')
  const isAdmin = computed(() => userType.value === 'admin')
  const isWorker = computed(() => userType.value === 'worker')

  // 用户登录
  const loginUser = async (credentials) => {
    try {
      const response = await request.post('/auth/login/user', credentials)
      setAuth(response.access_token, response.user_info, 'user')
      return response
    } catch (error) {
      throw error
    }
  }

  // 管理员登录
  const loginAdmin = async (credentials) => {
    try {
      const response = await request.post('/auth/login/admin', credentials)
      setAuth(response.access_token, response.admin_info, 'admin')
      return response
    } catch (error) {
      throw error
    }
  }

  // 维修工人登录
  const loginWorker = async (credentials) => {
    try {
      const response = await request.post('/auth/login/worker', credentials)
      setAuth(response.access_token, response.worker_info, 'worker')
      return response
    } catch (error) {
      throw error
    }
  }

  // 设置认证信息
  const setAuth = (authToken, user, type) => {
    token.value = authToken
    userInfo.value = user
    userType.value = type
    
    localStorage.setItem('token', authToken)
    localStorage.setItem('userInfo', JSON.stringify(user))
    localStorage.setItem('userType', type)
  }

  // 检查认证状态
  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUserInfo = localStorage.getItem('userInfo')
    const storedUserType = localStorage.getItem('userType')
    
    if (storedToken && storedUserInfo && storedUserType) {
      token.value = storedToken
      userInfo.value = JSON.parse(storedUserInfo)
      userType.value = storedUserType
    }
  }

  // 登出
  const logout = () => {
    token.value = null
    userInfo.value = null
    userType.value = ''
    
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('userType')
  }

  // 更新用户信息
  const updateUserInfo = (newUserInfo) => {
    userInfo.value = newUserInfo
    localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
  }

  return {
    token,
    userInfo,
    userType,
    isLoggedIn,
    isUser,
    isAdmin,
    isWorker,
    loginUser,
    loginAdmin,
    loginWorker,
    setAuth,
    checkAuth,
    logout,
    updateUserInfo
  }
}) 