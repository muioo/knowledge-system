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
import { h } from 'vue'
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
    await ElMessageBox({
      title: `确认${action}`,
      message: h('div', { class: 'dialog-confirm-content' }, [
        h('div', { class: 'dialog-icon warning' }, [
          h('svg', { viewBox: '0 0 24 24' }, [
            h('path', { d: 'M12 9v4m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
          ])
        ]),
        h('div', { class: 'dialog-text-wrapper' }, [
          h('p', `确定要${action}用户"${user.username}"吗？`)
        ])
      ]),
      customClass: 'dialog-unified',
      showCancelButton: true,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      confirmButtonClass: 'dialog-btn-secondary',
      cancelButtonClass: 'dialog-btn-secondary'
    })

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
    await ElMessageBox({
      title: '确认删除',
      message: h('div', { class: 'dialog-confirm-content' }, [
        h('div', { class: 'dialog-icon delete' }, [
          h('svg', { viewBox: '0 0 24 24' }, [
            h('path', { d: 'M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2' })
          ])
        ]),
        h('div', { class: 'dialog-text-wrapper' }, [
          h('p', `确定要删除用户"${user.username}"吗？`),
          h('p', { class: 'dialog-warning-text' }, '删除后该用户的所有文章也将被删除，此操作不可撤销。')
        ])
      ]),
      customClass: 'dialog-unified',
      showCancelButton: true,
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'dialog-btn-danger',
      cancelButtonClass: 'dialog-btn-secondary'
    })

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

/* 表格操作按钮样式 */
.user-table-container :deep(.el-button) {
  border-radius: 6px !important;
}

.user-table-container :deep(.el-button--text) {
  border-radius: 6px !important;
}

.user-table-container :deep(.el-button--text:hover) {
  background: rgba(116, 89, 217, 0.05) !important;
}
</style>
