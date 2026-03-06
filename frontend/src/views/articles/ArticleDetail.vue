<template>
  <div class="article-detail-page">
    <!-- Loading State -->
    <div v-if="articleStore.loading" class="article-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Error State -->
    <el-alert
      v-else-if="articleStore.error"
      type="error"
      :title="articleStore.error"
      :closable="false"
      show-icon
    />

    <!-- Article Content -->
    <div v-else-if="article" class="article-container">
      <!-- Article Header -->
      <div class="article-header">
        <div class="article-header-main">
          <el-button
            class="back-button"
            :icon="ArrowLeft"
            circle
            @click="handleBack"
          />
          <h1 class="article-title">{{ article.title }}</h1>
        </div>

        <div class="article-meta">
          <div class="article-tags">
            <el-tag
              v-for="tag in article.tags"
              :key="tag.id"
              :color="tag.color"
              size="small"
            >
              {{ tag.name }}
            </el-tag>
          </div>

          <div class="article-actions">
            <el-button
              v-if="canEdit"
              type="warning"
              :icon="Edit"
              @click="handleEdit"
            >
              Edit
            </el-button>
            <el-button
              v-if="canDelete"
              type="danger"
              :icon="Delete"
              @click="handleDelete"
            >
              Delete
            </el-button>
          </div>
        </div>

        <div class="article-info">
          <div class="article-info-item">
            <el-icon><User /></el-icon>
            <span>Author ID: {{ article.author_id }}</span>
          </div>
          <div class="article-info-item">
            <el-icon><View /></el-icon>
            <span>{{ article.view_count }} views</span>
          </div>
          <div class="article-info-item">
            <el-icon><Clock /></el-icon>
            <span>{{ formatDate(article.created_at) }}</span>
          </div>
          <div v-if="article.source_url" class="article-info-item">
            <el-icon><Link /></el-icon>
            <el-link :href="article.source_url" target="_blank" :underline="false" type="primary">
              Source URL
            </el-link>
          </div>
        </div>

        <el-divider />
      </div>

      <!-- Article Summary (if exists) -->
      <div v-if="article.summary" class="article-summary">
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <strong>Summary:</strong> {{ article.summary }}
          </template>
        </el-alert>
      </div>

      <!-- Article HTML Content -->
      <div class="article-content">
        <div v-if="loadingHtml" class="html-loading">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="htmlError" class="html-error">
          <el-alert
            type="error"
            :title="htmlError"
            :closable="false"
            show-icon
          />
          <el-divider>Original Content</el-divider>
          <div class="original-content">
            {{ article.content }}
          </div>
        </div>
        <div
          v-else-if="htmlContent"
          class="html-content"
          v-html="htmlContent"
        />
        <div v-else class="no-html-content">
          <el-empty description="No HTML content available">
            <div class="original-content">
              {{ article.content }}
            </div>
          </el-empty>
        </div>
      </div>

      <!-- Article Keywords (if exists) -->
      <div v-if="article.keywords" class="article-keywords">
        <el-divider>Keywords</el-divider>
        <div class="keywords-list">
          <el-tag
            v-for="(keyword, index) in keywordList"
            :key="index"
            type="info"
            size="small"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- Not Found State -->
    <el-empty
      v-else
      description="Article not found"
      :image-size="120"
    >
      <el-button type="primary" @click="handleBack">
        Back to Articles
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  Delete,
  User,
  View,
  Clock,
  Link,
} from '@element-plus/icons-vue'
import { useArticleStore } from '../../stores/article'
import { useAuthStore } from '../../stores/auth'
import { formatDate } from '../../utils/date'

/**
 * Router and stores
 */
const router = useRouter()
const route = useRoute()
const articleStore = useArticleStore()
const authStore = useAuthStore()

/**
 * State
 */
const htmlContent = ref('')
const loadingHtml = ref(false)
const htmlError = ref('')

/**
 * Computed
 */
const article = computed(() => articleStore.currentArticle)
const articleId = computed(() => Number(route.params.id))

const canEdit = computed(() => {
  return article.value && authStore.canEditArticle(article.value.author_id)
})

const canDelete = computed(() => {
  return article.value && authStore.canDeleteArticle(article.value.author_id)
})

const keywordList = computed(() => {
  if (!article.value?.keywords) return []
  return article.value.keywords.split(',').map(k => k.trim()).filter(k => k)
})

/**
 * Load article on mount
 */
onMounted(async () => {
  await loadArticle()
  await loadHtmlContent()
})

/**
 * Load article data
 */
async function loadArticle(): Promise<void> {
  try {
    await articleStore.fetchArticle(articleId.value)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to load article'
    ElMessage.error(errorMessage)
  }
}

/**
 * Load HTML content
 */
async function loadHtmlContent(): Promise<void> {
  if (!article.value) return

  loadingHtml.value = true
  htmlError.value = ''

  try {
    const response = await articleStore.fetchArticleHtml(articleId.value)
    htmlContent.value = response.html
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to load HTML content'
    htmlError.value = errorMessage
  } finally {
    loadingHtml.value = false
  }
}

/**
 * Handle back button
 */
function handleBack(): void {
  router.push({ name: 'ArticleList' })
}

/**
 * Handle edit button
 */
function handleEdit(): void {
  if (!article.value) return
  router.push({ name: 'ArticleEdit', params: { id: article.value.id } })
}

/**
 * Handle delete button
 */
async function handleDelete(): Promise<void> {
  if (!article.value) return

  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${article.value.title}"?`,
      'Delete Article',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )

    await articleStore.deleteArticle(article.value.id)
    ElMessage.success('Article deleted successfully')
    router.push({ name: 'ArticleList' })
  } catch (error) {
    if (error !== 'cancel') {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete article'
      ElMessage.error(errorMessage)
    }
  }
}
</script>

<style scoped lang="scss">
.article-detail-page {
  padding: var(--spacing-lg);
  max-width: 900px;
  margin: 0 auto;
}

.article-loading {
  padding: var(--spacing-lg);
}

.article-container {
  background: var(--color-white);
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-card);
  padding: var(--spacing-xl);
}

.article-header {
  margin-bottom: var(--spacing-lg);
}

.article-header-main {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.back-button {
  flex-shrink: 0;
  margin-top: var(--spacing-xs);
}

.article-title {
  font-size: var(--font-size-xxl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: var(--line-height-small);
  margin: 0;
  flex: 1;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.article-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.article-info {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.article-info-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.article-summary {
  margin-bottom: var(--spacing-lg);
}

.article-content {
  margin-bottom: var(--spacing-lg);
}

.html-loading,
.html-error {
  padding: var(--spacing-lg);
}

.original-content {
  padding: var(--spacing-md);
  background: var(--color-bg-base);
  border-radius: var(--radius-base);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-family-code);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-large);
  max-height: 400px;
  overflow-y: auto;
}

.no-html-content {
  padding: var(--spacing-lg);
}

.html-content {
  line-height: var(--line-height-large);
  color: var(--color-text-primary);

  // Style HTML content
  :deep(h1),
  :deep(h2),
  :deep(h3),
  :deep(h4),
  :deep(h5),
  :deep(h6) {
    font-weight: 600;
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-sm);
    color: var(--color-text-primary);
  }

  :deep(h1) { font-size: var(--font-size-xxl); }
  :deep(h2) { font-size: var(--font-size-xl); }
  :deep(h3) { font-size: var(--font-size-lg); }
  :deep(h4) { font-size: var(--font-size-md); }
  :deep(h5) { font-size: var(--font-size-base); }
  :deep(h6) { font-size: var(--font-size-sm); }

  :deep(p) {
    margin-bottom: var(--spacing-md);
  }

  :deep(a) {
    color: var(--color-primary);
    text-decoration: none;
    transition: var(--transition-fast);

    &:hover {
      color: var(--color-primary-dark);
      text-decoration: underline;
    }
  }

  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: var(--radius-base);
    margin: var(--spacing-md) 0;
  }

  :deep(code) {
    background: var(--color-bg-base);
    padding: 2px 6px;
    border-radius: var(--radius-base);
    font-family: var(--font-family-code);
    font-size: 0.9em;
  }

  :deep(pre) {
    background: var(--color-bg-base);
    padding: var(--spacing-md);
    border-radius: var(--radius-base);
    overflow-x: auto;
    margin: var(--spacing-md) 0;

    code {
      background: transparent;
      padding: 0;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid var(--color-primary);
    padding-left: var(--spacing-md);
    margin: var(--spacing-md) 0;
    color: var(--color-text-secondary);
    font-style: italic;
  }

  :deep(ul),
  :deep(ol) {
    padding-left: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
  }

  :deep(li) {
    margin-bottom: var(--spacing-xs);
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin: var(--spacing-md) 0;
  }

  :deep(th),
  :deep(td) {
    border: 1px solid var(--color-border-base);
    padding: var(--spacing-sm);
    text-align: left;
  }

  :deep(th) {
    background: var(--color-bg-base);
    font-weight: 600;
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid var(--color-border-light);
    margin: var(--spacing-lg) 0;
  }
}

.article-keywords {
  margin-top: var(--spacing-lg);
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.keyword-tag {
  margin: 0;
}

@media (max-width: 768px) {
  .article-detail-page {
    padding: var(--spacing-md);
  }

  .article-container {
    padding: var(--spacing-lg);
  }

  .article-header-main {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .back-button {
    align-self: flex-start;
  }

  .article-title {
    font-size: var(--font-size-xl);
  }

  .article-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .article-info {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}
</style>
