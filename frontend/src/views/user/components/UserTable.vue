<template>
  <div class="user-table-container">
    <el-table
      v-loading="loading"
      :data="users"
      stripe
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button
            text
            type="primary"
            size="small"
            :icon="Edit"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            text
            :type="row.is_active ? 'warning' : 'success'"
            size="small"
            @click="handleToggleStatus(row)"
          >
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button
            text
            type="danger"
            size="small"
            :icon="Delete"
            :disabled="row.id === currentUserId"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api/user'
import type { User } from '@/types/user'

interface Props {
  users: User[]
  loading: boolean
  currentUserId: number
}

interface Emits {
  (e: 'edit', user: User): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

function handleSortChange() {
  // 如果需要排序功能可以在这里实现
}

function handleEdit(user: User) {
  emit('edit', user)
}

async function handleToggleStatus(user: User) {
  const action = user.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户"${user.username}"吗？`,
      `确认${action}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await userApi.updateUserStatus(user.id, !user.is_active)
    ElMessage.success(`用户${action}成功`)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

async function handleDelete(user: User) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${user.username}"吗？删除后该用户的所有文章也将被删除，此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await userApi.deleteUser(user.id)
    ElMessage.success('用户删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.user-table-container {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
}
</style>

<style>
/* 确认对话框样式 */
.el-message-box {
  border-radius: 20px !important;
  border: 2px solid var(--border-default, #e5e7eb) !important;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2) !important;
  padding: 32px !important;
  min-width: 480px !important;
  max-width: 520px !important;
}

.el-message-box__header {
  padding: 0 0 20px 0 !important;
  margin-bottom: 20px !important;
  border-bottom: 2px solid var(--border-default, #e5e7eb) !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
}

.el-message-box__title {
  font-family: var(--font-dinpro, 'DIN Pro', sans-serif) !important;
  font-size: 20px !important;
  font-weight: 700 !important;
  color: var(--text-black, #111827) !important;
  letter-spacing: -0.01em !important;
}

.el-message-box__headerbtn {
  top: -4px !important;
  right: -8px !important;
  width: 36px !important;
  height: 36px !important;
  border-radius: 50% !important;
  transition: all 0.2s ease !important;
}

.el-message-box__headerbtn:hover {
  background: var(--bg-tertiary, #f9fafb) !important;
}

.el-message-box__headerbtn .el-message-box__close {
  color: var(--text-grey-40, #9ca3af) !important;
  font-size: 20px !important;
  font-weight: bold !important;
}

.el-message-box__headerbtn:hover .el-message-box__close {
  color: var(--text-black, #111827) !important;
}

.el-message-box__content {
  padding: 8px 0 24px 0 !important;
  font-family: 'Poppins', sans-serif !important;
}

.el-message-box__message {
  font-size: 16px !important;
  color: var(--text-black, #111827) !important;
  line-height: 1.7 !important;
  font-weight: 400 !important;
}

.el-message-box__btns {
  padding: 20px 0 0 0 !important;
  display: flex !important;
  gap: 16px !important;
  justify-content: flex-end !important;
}

.el-message-box__btns button {
  border-radius: 12px !important;
  font-family: var(--font-dinpro, 'DIN Pro', sans-serif) !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  padding: 12px 28px !important;
  border: none !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  min-width: 100px !important;
}

.el-message-box__btns .el-button--default {
  background: var(--bg-tertiary, #f9fafb) !important;
  color: var(--text-black, #111827) !important;
  border: 2px solid var(--border-default, #e5e7eb) !important;
}

.el-message-box__btns .el-button--default:hover {
  background: var(--bg-secondary, #f3f4f6) !important;
  border-color: var(--color-indigo, #7459d9) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.el-message-box__btns .el-button--primary {
  background: linear-gradient(135deg, #7459d9 0%, #6b4fc4 100%) !important;
  color: white !important;
  border: 2px solid transparent !important;
}

.el-message-box__btns .el-button--primary:hover {
  background: linear-gradient(135deg, #6b4fc4 0%, #5e47b8 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 20px rgba(116, 89, 217, 0.35) !important;
}

.el-message-box__btns .el-button--primary:active {
  transform: translateY(0) !important;
}
</style>
