import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import { useUiStore } from './stores/ui'
import App from './App.vue'
import './assets/styles/global.scss'

const app = createApp(App)
const pinia = createPinia()

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Install plugins
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// Initialize UI store
const uiStore = useUiStore()
uiStore.initializeSidebar()
uiStore.initializeTheme()

// Mount app
app.mount('#app')
