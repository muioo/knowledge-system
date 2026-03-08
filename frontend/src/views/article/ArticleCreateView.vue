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
  keywords: ''
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
        keywords: urlForm.value.use_ai ? undefined : urlForm.value.keywords
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
      formData.append('file', selectedFile.value)
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
  padding: 20px;
}

.header-section {
  margin-bottom: 20px;
}
</style>
