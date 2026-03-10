<template>
  <div class="article-create-view content-wrapper">
    <div class="header-section">
      <h1 class="text-2xl font-bold text-gray-900">创建文章</h1>
    </div>

    <!-- 选项卡 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <!-- URL导入 -->
        <el-tab-pane label="URL导入" name="url">
          <el-form
            ref="urlFormRef"
            :model="urlForm"
            :rules="urlFormRules"
            label-width="100px"
          >
            <el-form-item label="文章URL" prop="url">
              <el-input
                v-model="urlForm.url"
                placeholder="请输入文章链接"
                clearable
              />
            </el-form-item>

            <el-form-item label="自定义标题" prop="title">
              <el-input
                v-model="urlForm.title"
                placeholder="留空则自动提取标题"
                clearable
              />
            </el-form-item>

            <el-form-item label="标签">
              <el-select
                v-model="urlForm.tag_ids"
                multiple
                placeholder="选择标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="AI提取">
              <el-switch
                v-model="urlForm.use_ai"
                active-text="使用AI提取关键词和摘要"
                inactive-text="手动输入"
              />
            </el-form-item>

            <el-form-item v-if="urlForm.use_ai" label="API Key">
              <el-input
                v-model="urlForm.api_key"
                type="password"
                placeholder="请输入火山引擎 ARK API Key"
                show-password
                clearable
              />
            </el-form-item>

            <template v-if="!urlForm.use_ai">
              <el-form-item label="摘要" prop="summary">
                <el-input
                  v-model="urlForm.summary"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入文章摘要"
                />
              </el-form-item>

              <el-form-item label="关键词" prop="keywords">
                <el-input
                  v-model="urlForm.keywords"
                  placeholder="请输入关键词，用逗号分隔"
                  clearable
                />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="handleUrlImport" :loading="urlImporting" class="btn-primary">
                导入文章
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 文件上传 -->
        <el-tab-pane label="文件上传" name="file">
          <el-form
            ref="fileFormRef"
            :model="fileForm"
            :rules="fileFormRules"
            label-width="100px"
          >
            <el-form-item label="上传文件" prop="file">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                accept=".html,.htm"
              >
                <el-button type="primary" class="btn-primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">仅支持 HTML 文件</div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item label="标题" prop="title">
              <el-input
                v-model="fileForm.title"
                placeholder="请输入文章标题"
                clearable
              />
            </el-form-item>

            <el-form-item label="摘要" prop="summary">
              <el-input
                v-model="fileForm.summary"
                type="textarea"
                :rows="3"
                placeholder="请输入文章摘要"
              />
            </el-form-item>

            <el-form-item label="关键词" prop="keywords">
              <el-input
                v-model="fileForm.keywords"
                placeholder="请输入关键词，用逗号分隔"
                clearable
              />
            </el-form-item>

            <el-form-item label="标签">
              <el-select
                v-model="fileForm.tag_ids"
                multiple
                placeholder="选择标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleFileUpload" :loading="fileUploading" class="btn-primary">
                上传文章
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules, type UploadInstance, type UploadFile } from 'element-plus'
import { articleApi } from '@/api/article'
import { tagApi } from '@/api/tag'
import type { Tag } from '@/types/tag'

const router = useRouter()

// 标签数据
const tags = ref<Tag[]>([])

// 当前激活的选项卡
const activeTab = ref('url')

// URL导入表单
const urlFormRef = ref<FormInstance>()
const urlImporting = ref(false)
const urlForm = ref({
  url: '',
  title: '',
  tag_ids: [] as number[],
  use_ai: true,
  summary: '',
  keywords: '',
  api_key: ''
})

const urlFormRules: FormRules = {
  url: [
    { required: true, message: '请输入文章链接', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
  ]
}

// 文件上传表单
const fileFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const fileUploading = ref(false)
const selectedFile = ref<File | null>(null)
const fileForm = ref({
  file: null as File | null,
  title: '',
  summary: '',
  keywords: '',
  tag_ids: [] as number[]
})

const fileFormRules: FormRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' }
  ],
  summary: [
    { required: true, message: '请输入文章摘要', trigger: 'blur' }
  ],
  keywords: [
    { required: true, message: '请输入关键词', trigger: 'blur' }
  ]
}

// 加载标签列表
async function loadTags() {
  try {
    const res = await tagApi.getList()
    tags.value = res.data
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// URL导入
async function handleUrlImport() {
  if (!urlFormRef.value) return

  await urlFormRef.value.validate(async (valid) => {
    if (!valid) return

    urlImporting.value = true
    try {
      await articleApi.importFromUrl({
        url: urlForm.value.url,
        title: urlForm.value.title || undefined,
        tag_ids: urlForm.value.tag_ids,
        use_ai: urlForm.value.use_ai,
        summary: urlForm.value.use_ai ? undefined : urlForm.value.summary,
        keywords: urlForm.value.use_ai ? undefined : urlForm.value.keywords,
        api_key: urlForm.value.use_ai ? urlForm.value.api_key || undefined : undefined
      })
      ElMessage.success('文章导入成功')
      router.push('/articles')
    } catch (error: any) {
      console.error('导入文章失败:', error)
      ElMessage.error(error.response?.data?.detail || '导入失败')
    } finally {
      urlImporting.value = false
    }
  })
}

// 文件选择
function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
    fileForm.value.file = file.raw
  }
}

// 文件超出限制
function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

// 文件上传
async function handleFileUpload() {
  if (!fileFormRef.value) return
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  await fileFormRef.value.validate(async (valid) => {
    if (!valid) return

    fileUploading.value = true
    try {
      const formData = new FormData()
      if (selectedFile.value) {
        formData.append('file', selectedFile.value)
      }
      formData.append('title', fileForm.value.title)
      formData.append('summary', fileForm.value.summary)
      formData.append('keywords', fileForm.value.keywords)
      if (fileForm.value.tag_ids.length > 0) {
        formData.append('tag_ids', fileForm.value.tag_ids.join(','))
      }

      await articleApi.upload(formData)
      ElMessage.success('文章上传成功')
      router.push('/articles')
    } catch (error: any) {
      console.error('上传文章失败:', error)
      ElMessage.error(error.response?.data?.detail || '上传失败')
    } finally {
      fileUploading.value = false
    }
  })
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.article-create-view {
  width: 100%;
  height: 100%;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.header-section {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.header-section h1 {
  font-family: var(--font-dinpro);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-black);
  margin: 0;
}

/* 卡片容器 */
.article-create-view :deep(.el-card) {
  background: var(--bg-white);
  border-radius: 12px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-create-view :deep(.el-card__body) {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.article-create-view :deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.article-create-view :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.article-create-view :deep(.el-tab-pane) {
  height: 100%;
  overflow: auto;
}

/* 选项卡样式 */
.article-create-view :deep(.el-tabs__header) {
  margin: 0 0 24px 0;
  border-bottom: 2px solid var(--border-default);
}

.article-create-view :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.article-create-view :deep(.el-tabs__item) {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-grey-50);
  padding: 0 20px;
  height: 44px;
  line-height: 44px;
  border: none;
  transition: all 0.2s ease;
}

.article-create-view :deep(.el-tabs__item:hover) {
  color: var(--text-black);
}

.article-create-view :deep(.el-tabs__item.is-active) {
  color: var(--color-indigo);
}

.article-create-view :deep(.el-tabs__active-bar) {
  height: 3px;
  background: var(--color-indigo);
  border-radius: 2px;
}

/* 表单样式 */
.article-create-view :deep(.el-form-item__label) {
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-black);
  padding-right: 16px;
}

.article-create-view :deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  box-shadow: none;
  border: 1px solid var(--border-default);
  padding: 8px 16px;
  transition: all 0.2s ease;
}

.article-create-view :deep(.el-input__wrapper:hover) {
  border-color: var(--color-indigo);
}

.article-create-view :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-indigo);
  box-shadow: 0 0 0 2px rgba(116, 89, 217, 0.1);
}

.article-create-view :deep(.el-input__inner) {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: var(--text-black);
}

.article-create-view :deep(.el-textarea__inner) {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  padding: 12px 16px;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: var(--text-black);
  transition: all 0.2s ease;
}

.article-create-view :deep(.el-textarea__inner:hover) {
  border-color: var(--color-indigo);
}

.article-create-view :deep(.el-textarea__inner:focus) {
  border-color: var(--color-indigo);
  box-shadow: 0 0 0 2px rgba(116, 89, 217, 0.1);
}

/* 选择器样式 */
.article-create-view :deep(.el-select .el-input__wrapper) {
  border-radius: var(--radius-md);
}

.article-create-view :deep(.el-select__placeholder) {
  color: var(--text-grey-40);
}

.article-create-view :deep(.el-select-dropdown__item) {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
}

.article-create-view :deep(.el-tag) {
  border-radius: var(--radius-md);
  font-family: var(--font-dinpro);
  font-size: 13px;
  font-weight: 500;
  padding: 4px 10px;
  border: none;
  background-color: var(--tag-color) !important;
}

.article-create-view :deep(.el-tag.el-tag--light) {
  border: none !important;
  background-color: var(--tag-color) !important;
}

.article-create-view :deep(.el-select__tag) {
  background-color: var(--tag-color) !important;
  border: none !important;
  color: white !important;
}

.article-create-view :deep(.el-select__tag .el-tag__close) {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-radius: 50%;
}

.article-create-view :deep(.el-select__tag .el-tag__close:hover) {
  background-color: rgba(255, 255, 255, 0.3) !important;
}

/* 开关样式 */
.article-create-view :deep(.el-switch) {
  height: 24px;
}

.article-create-view :deep(.el-switch__core) {
  border-radius: 12px;
  height: 24px;
  min-width: 48px;
  border: 2px solid var(--border-default);
}

.article-create-view :deep(.el-switch.is-checked .el-switch__core) {
  background: var(--color-indigo);
  border-color: var(--color-indigo);
}

.article-create-view :deep(.el-switch__action) {
  border-radius: 50%;
  width: 18px;
  height: 18px;
  top: 1px;
  left: 1px;
}

.article-create-view :deep(.el-switch.is-checked .el-switch__action) {
  left: calc(100% - 19px);
}

.article-create-view :deep(.el-switch__label) {
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-black);
}

.article-create-view :deep(.el-switch__label.is-active) {
  color: var(--color-indigo);
}

/* 按钮样式 */
.article-create-view :deep(.el-button) {
  border-radius: var(--radius-md);
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  border: none;
  transition: all 0.2s ease;
}

.article-create-view :deep(.el-button--primary) {
  background: var(--color-indigo);
  color: white;
}

.article-create-view :deep(.el-button--primary:hover) {
  background: var(--color-indigo-50);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(116, 89, 217, 0.3);
}

.article-create-view :deep(.el-button--primary:active) {
  transform: translateY(0);
}

/* 上传组件样式 */
.article-create-view :deep(.el-upload) {
  width: 100%;
}

.article-create-view :deep(.el-upload-dragger) {
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-default);
  background: var(--bg-tertiary);
  padding: 32px;
  transition: all 0.2s ease;
}

.article-create-view :deep(.el-upload-dragger:hover) {
  border-color: var(--color-indigo);
  background: rgba(116, 89, 217, 0.05);
}

.article-create-view :deep(.el-upload__tip) {
  font-family: 'Poppins', sans-serif;
  font-size: 12px;
  color: var(--text-grey-40);
  margin-top: 8px;
}

/* 表单项间距 */
.article-create-view :deep(.el-form-item) {
  margin-bottom: 20px;
}

.article-create-view :deep(.el-form-item:last-child) {
  margin-bottom: 0;
  margin-top: 8px;
}

/* 必填星号 */
.article-create-view :deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label::before) {
  color: var(--color-red);
  margin-right: 4px;
}

/* 错误提示 */
.article-create-view :deep(.el-form-item__error) {
  font-family: 'Poppins', sans-serif;
  font-size: 12px;
  color: var(--color-red);
  margin-top: 4px;
}
</style>
