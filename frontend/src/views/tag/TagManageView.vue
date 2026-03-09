<template>
  <div class="tag-manage-view content-wrapper">
    <div class="header-section">
      <h1 class="text-2xl font-bold text-gray-900">标签管理</h1>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog" class="btn-primary">
        创建标签
      </el-button>
    </div>

    <!-- 标签网格 -->
    <div v-loading="loading" class="tag-grid">
      <div v-if="tags.length === 0 && !loading" class="empty-state">
        <el-icon :size="64" color="#9CA3AF"><PriceTag /></el-icon>
        <p class="text-gray-500 mt-4">暂无标签</p>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog" class="mt-4 btn-primary">
          创建第一个标签
        </el-button>
      </div>

      <div
        v-for="tag in tags"
        :key="tag.id"
        class="tag-card"
        :style="{ borderLeftColor: tag.color }"
      >
        <div class="tag-header">
          <div class="tag-name-wrapper">
            <div class="tag-color" :style="{ backgroundColor: tag.color }"></div>
            <h3 class="tag-name">{{ tag.name }}</h3>
          </div>
        </div>
        <p class="tag-info">创建于 {{ formatDate(tag.created_at) }}</p>
        <div class="tag-actions">
          <el-button text :icon="Edit" @click="openEditDialog(tag)" class="btn-ghost">编辑</el-button>
          <el-button text :icon="Delete" type="danger" @click="confirmDelete(tag)" class="btn-ghost btn-danger">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑标签' : '创建标签'"
      width="400px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="标签名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入标签名" maxlength="50" />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <div class="color-picker-wrapper">
            <el-color-picker v-model="formData.color" show-alpha />
            <el-input v-model="formData.color" placeholder="#3498db" class="color-input" />
          </div>
        </el-form-item>
        <div class="preset-colors">
          <span
            v-for="color in presetColors"
            :key="color"
            class="preset-color"
            :style="{ backgroundColor: color }"
            :class="{ active: formData.color === color }"
            @click="formData.color = color"
          ></span>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" class="btn-ghost">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting" class="btn-primary">
          {{ isEditMode ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PriceTag, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useTagStore } from '@/store/tag'
import { storeToRefs } from 'pinia'
import type { Tag } from '@/types/tag'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// Tag Store
const tagStore = useTagStore()
const { tags, loading } = storeToRefs(tagStore)

// 数据
const submitting = ref(false)

// 对话框
const dialogVisible = ref(false)
const isEditMode = ref(false)
const editingTag = ref<Tag | null>(null)

// 表单
const formRef = ref<FormInstance>()
const formData = ref({
  name: '',
  color: '#3498db'
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入标签名', trigger: 'blur' },
    { min: 1, max: 50, message: '标签名长度为1-50字符', trigger: 'blur' }
  ],
  color: [
    { required: true, message: '请选择颜色', trigger: 'blur' }
  ]
}

// 预设颜色
const presetColors = [
  '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
  '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#16a085'
]

// 加载标签列表
async function loadTags() {
  try {
    await tagStore.fetchTags()
  } catch (error) {
    console.error('加载标签列表失败:', error)
    ElMessage.error('加载标签列表失败')
  }
}

// 打开创建对话框
function openCreateDialog() {
  isEditMode.value = false
  editingTag.value = null
  formData.value = {
    name: '',
    color: '#3498db'
  }
  dialogVisible.value = true
}

// 打开编辑对话框
function openEditDialog(tag: Tag) {
  isEditMode.value = true
  editingTag.value = tag
  formData.value = {
    name: tag.name,
    color: tag.color
  }
  dialogVisible.value = true
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditMode.value && editingTag.value) {
        await tagStore.updateTag(editingTag.value.id, formData.value)
        ElMessage.success('标签更新成功')
      } else {
        await tagStore.createTag(formData.value)
        ElMessage.success('标签创建成功')
      }
      dialogVisible.value = false
    } catch (error: any) {
      console.error('保存标签失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

// 确认删除
function confirmDelete(tag: Tag) {
  ElMessageBox.confirm(
    `确定要删除标签"${tag.name}"吗？此操作不可撤销。`,
    '确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteTag(tag.id)
  }).catch(() => {
    // 用户取消
  })
}

// 删除标签
async function deleteTag(id: number) {
  try {
    await tagStore.deleteTag(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    console.error('删除标签失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-manage-view {
  width: 100%;
  padding: 12px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-section h1 {
  margin: 0;
  font-family: var(--font-dinpro);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-black);
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.tag-card {
  background: var(--bg-white);
  border: 1px solid var(--border-default);
  border-left-width: 4px;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.tag-card:hover {
  box-shadow: 0px 12px 24px 0px rgba(50, 50, 71, 0.1);
}

.tag-header {
  margin-bottom: 12px;
  width: 100%;
}

.tag-name-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.tag-color {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.tag-name {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-black);
  margin: 0;
  white-space: nowrap;
}

.tag-info {
  color: var(--text-grey-40);
  font-size: 13px;
  margin: 0 0 12px 0;
}

.tag-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--border-default);
}

.tag-actions .el-button {
  flex: 1;
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.color-input {
  flex: 1;
}

.preset-colors {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.preset-color {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.preset-color:hover {
  transform: scale(1.1);
}

.preset-color.active {
  border-color: var(--text-black);
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-state p {
  color: var(--text-grey-40);
  margin: 0;
}
</style>
