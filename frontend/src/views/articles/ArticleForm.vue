<template>
  <div class="article-form-page">
    <!-- Loading State -->
    <div v-if="loading" class="form-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Form Container -->
    <div v-else class="form-container">
      <div class="form-header">
        <h1 class="form-title">{{ isEditMode ? '编辑文章' : '创建文章' }}</h1>
      </div>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <!-- Title -->
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入文章标题"
            maxlength="200"
            show-word-limit
            clearable
          />
        </el-form-item>

        <!-- Content -->
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            placeholder="请输入文章内容"
            :rows="10"
            show-word-limit
          />
        </el-form-item>

        <!-- Summary -->
        <el-form-item label="摘要" prop="summary">
          <el-input
            v-model="formData.summary"
            type="textarea"
            placeholder="请输入文章摘要（可选）"
            :rows="3"
            maxlength="500"
            show-word-limit
            clearable
          />
        </el-form-item>

        <!-- Tags -->
        <el-form-item label="标签" prop="tag_ids">
          <el-select
            v-model="formData.tag_ids"
            multiple
            placeholder="请选择标签"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="tag in tagStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>

        <!-- Source URL -->
        <el-form-item label="来源 URL" prop="source_url">
          <el-input
            v-model="formData.source_url"
            placeholder="请输入来源 URL（可选）"
            clearable
          />
        </el-form-item>

        <!-- Keywords -->
        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="formData.keywords"
            placeholder="请输入关键词，多个关键词用逗号分隔（可选）"
            clearable
          />
        </el-form-item>

        <!-- Form Actions -->
        <el-form-item class="form-actions">
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEditMode ? '保存' : '创建' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useArticleStore } from '../../stores/article'
import { useTagStore } from '../../stores/tag'
import type { ArticleCreate, ArticleUpdate } from '../../types'

// Stores
const articleStore = useArticleStore()
const tagStore = useTagStore()

// Router
const route = useRoute()
const router = useRouter()

// Form ref
const formRef = ref<FormInstance>()

// State
const loading = ref(false)
const submitting = ref(false)

// Check if edit mode
const isEditMode = computed(() => !!route.params.id)
const articleId = computed(() => Number(route.params.id))

// Form data
const formData = reactive<ArticleCreate & { id?: number }>({
  title: '',
  content: '',
  summary: '',
  tag_ids: [],
  source_url: '',
  keywords: '',
})

// URL validation function
const validateUrl = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }

  try {
    new URL(value)
    callback()
  } catch {
    callback(new Error('请输入有效的 URL 格式'))
  }
}

// Form validation rules
const formRules: FormRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度应在 1-200 个字符之间', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 10, message: '内容长度至少为 10 个字符', trigger: 'blur' },
  ],
  summary: [
    { max: 500, message: '摘要长度不能超过 500 个字符', trigger: 'blur' },
  ],
  source_url: [
    { validator: validateUrl, trigger: 'blur' },
  ],
}

// Load article data for edit mode
async function loadArticleData() {
  if (!isEditMode.value) return

  loading.value = true
  try {
    await articleStore.fetchArticle(articleId.value)

    if (articleStore.currentArticle) {
      const article = articleStore.currentArticle
      formData.title = article.title
      formData.content = article.content
      formData.summary = article.summary || ''
      formData.tag_ids = article.tags.map(tag => tag.id)
      formData.source_url = article.source_url || ''
      formData.keywords = article.keywords || ''
    }
  } catch (error) {
    ElMessage.error('加载文章数据失败')
    router.push('/articles')
  } finally {
    loading.value = false
  }
}

// Load tags
async function loadTags() {
  try {
    await tagStore.fetchTags()
  } catch (error) {
    ElMessage.error('加载标签列表失败')
  }
}

// Handle form submit
async function handleSubmit() {
  if (!formRef.value) return

  try {
    // Validate form
    await formRef.value.validate()

    submitting.value = true

    // Prepare data
    const submitData: ArticleCreate | ArticleUpdate = {
      title: formData.title,
      content: formData.content,
      summary: formData.summary || undefined,
      tag_ids: formData.tag_ids && formData.tag_ids.length > 0 ? formData.tag_ids : undefined,
      source_url: formData.source_url || undefined,
      keywords: formData.keywords || undefined,
    }

    let resultArticleId: number

    if (isEditMode.value) {
      // Update article
      await articleStore.updateArticle(articleId.value, submitData as ArticleUpdate)
      resultArticleId = articleId.value
      ElMessage.success('文章更新成功')
    } else {
      // Create article
      const result = await articleStore.createArticle(submitData as ArticleCreate)
      resultArticleId = result.id
      ElMessage.success('文章创建成功')
    }

    // Navigate to article detail page
    router.push(`/articles/${resultArticleId}`)
  } catch (error) {
    if (error instanceof Error && error.message !== 'Validation failed') {
      ElMessage.error(isEditMode.value ? '文章更新失败' : '文章创建失败')
    }
  } finally {
    submitting.value = false
  }
}

// Handle cancel
function handleCancel() {
  router.back()
}

// Initialize
onMounted(async () => {
  await loadTags()
  await loadArticleData()
})
</script>

<style scoped lang="scss">
.article-form-page {
  padding: 24px;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.form-loading {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background-color: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  box-shadow: var(--el-box-shadow-light);
}

.form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background-color: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  box-shadow: var(--el-box-shadow-light);
}

.form-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.form-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.el-form {
  :deep(.el-form-item__label) {
    font-weight: 500;
    color: var(--el-text-color-regular);
    margin-bottom: 8px;
  }

  :deep(.el-textarea__inner) {
    font-family: inherit;
    line-height: 1.6;
  }
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-lighter);

  :deep(.el-form-item__content) {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .article-form-page {
    padding: 16px;
  }

  .form-container {
    padding: 16px;
  }

  .form-title {
    font-size: 20px;
  }

  .el-form {
    :deep(.el-form-item) {
      margin-bottom: 18px;
    }
  }

  .form-actions {
    :deep(.el-form-item__content) {
      flex-direction: column-reverse;

      .el-button {
        width: 100%;
      }
    }
  }
}
</style>
