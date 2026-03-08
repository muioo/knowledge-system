<template>
  <div class="user-manage-view">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="text-2xl font-bold text-gray-900">用户管理</h1>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名或邮箱"
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch" />
        </template>
      </el-input>
    </div>

    <!-- 用户表格 -->
    <UserTable
      :users="filteredUsers"
      :loading="loading"
      :total="total"
      :page="page"
      :size="size"
      :current-user-id="currentUserId"
      @refresh="loadUsers"
      @update:page="page = $event"
      @update:size="size = $event"
      @edit="handleEditUser"
    />

    <!-- 编辑对话框 -->
    <UserEditDialog
      v-model="editDialogVisible"
      :user="editingUser"
      :current-user-id="currentUserId"
      @success="loadUsers"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import type { User } from '@/types/user'
import UserTable from './components/UserTable.vue'
import UserEditDialog from './components/UserEditDialog.vue'

// 用户状态
const authStore = useAuthStore()
const { user: currentUser } = storeToRefs(authStore)

// 数据
const loading = ref(false)
const users = ref<User[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const searchKeyword = ref('')

// 编辑对话框
const editDialogVisible = ref(false)
const editingUser = ref<User | null>(null)

// 当前用户ID
const currentUserId = computed(() => currentUser.value?.id || 0)

// 过滤后的用户列表（前端搜索）
const filteredUsers = computed(() => {
  if (!searchKeyword.value) {
    return users.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return users.value.filter(
    (user) =>
      user.username.toLowerCase().includes(keyword) ||
      user.email.toLowerCase().includes(keyword)
  )
})

// 加载用户列表
async function loadUsers() {
  loading.value = true
  try {
    const res = await userApi.getList({ page: page.value, size: size.value })
    users.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索用户
function handleSearch() {
  // 重置到第一页
  page.value = 1
  // 前端搜索，不需要重新加载
  // 如果需要后端搜索，可以在这里调用 API
}

// 编辑用户
function handleEditUser(user: User) {
  editingUser.value = user
  editDialogVisible.value = true
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-manage-view {
  width: 100%;
  padding: 16px;
}

.header-section {
  margin-bottom: 16px;
}

.search-section {
  margin-bottom: 16px;
}
</style>
