import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import './styles/global.scss'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)

// 在挂载应用前检查并恢复认证状态
const authStore = useAuthStore()
authStore.checkAuth()

app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app') 