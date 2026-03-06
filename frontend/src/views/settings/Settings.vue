<template>
  <div class="settings-page">
    <h1 class="page-title">设置</h1>

    <el-card class="settings-card">
      <template #header>
        <span>个人信息</span>
      </template>
      <el-form label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" disabled />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span>界面设置</span>
      </template>
      <el-form label-width="100px">
        <el-form-item label="主题">
          <el-switch
            v-model="isDarkMode"
            active-text="深色"
            inactive-text="浅色"
            @change="handleThemeChange"
          />
        </el-form-item>
        <el-form-item label="侧边栏">
          <el-switch
            v-model="sidebarCollapsed"
            active-text="收起"
            inactive-text="展开"
            @change="handleSidebarChange"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <span>账户操作</span>
      </template>
      <el-space direction="vertical" :size="16">
        <el-button type="primary" @click="handleChangePassword">
          修改密码
        </el-button>
        <el-button type="danger" @click="handleLogout">
          退出登录
        </el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { useUiStore } from '../../stores/ui'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const userInfo = computed(() => ({
  username: authStore.user?.username || '',
  email: authStore.user?.email || ''
}))

const isDarkMode = computed({
  get: () => uiStore.isDarkMode,
  set: (value: boolean) => {
    uiStore.setTheme(value ? 'dark' : 'light')
  }
})

const sidebarCollapsed = computed({
  get: () => uiStore.sidebarCollapsed,
  set: (value: boolean) => {
    uiStore.setSidebarCollapsed(value)
  }
})

function handleThemeChange(): void {
  ElMessage.success(`已切换到${isDarkMode.value ? '深色' : '浅色'}主题`)
}

function handleSidebarChange(): void {
  ElMessage.success(`侧边栏已${sidebarCollapsed.value ? '收起' : '展开'}`)
}

function handleChangePassword(): void {
  ElMessage.info('修改密码功能待实现')
}

async function handleLogout(): Promise<void> {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}
</script>

<style scoped lang="scss">
.settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 24px 0;
  color: #333;
}

.settings-card {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
}
</style>
