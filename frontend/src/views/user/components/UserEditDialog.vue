<template>
  <el-dialog
    v-model="visible"
    :title="isEditMode ? '编辑用户' : '新建用户'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="80px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          placeholder="请输入用户名"
          :disabled="isEditMode"
          maxlength="50"
        />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="formData.email"
          placeholder="请输入邮箱"
          type="email"
          maxlength="100"
        />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="formData.password"
          :placeholder="isEditMode ? '留空则不修改密码' : '请输入密码'"
          type="password"
          show-password
          maxlength="50"
        />
      </el-form-item>

      <el-form-item v-if="isEditMode && !isCurrentUser" label="角色" prop="role">
        <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="isEditMode && !isCurrentUser" label="状态" prop="is_active">
        <el-switch
          v-model="formData.is_active"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ isEditMode ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { userApi } from '@/api/user'
import type { User } from '@/types/user'

interface Props {
  modelValue: boolean
  user?: User | null
  currentUserId?: number
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<Props>(), {
  user: null,
  currentUserId: 0,
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const isEditMode = computed(() => !!props.user)
const isCurrentUser = computed(() => props.user?.id === props.currentUserId)

const formData = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user' as 'admin' | 'user',
  is_active: true,
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    {
      required: !isEditMode.value,
      message: '请输入密码',
      trigger: 'blur',
    },
    { min: 6, max: 50, message: '密码长度为6-50字符', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

// 监听用户数据变化，填充表单
watch(
  () => props.user,
  (user) => {
    if (user) {
      formData.username = user.username
      formData.email = user.email
      formData.password = ''
      formData.role = user.role as 'admin' | 'user'
      formData.is_active = user.is_active
    } else {
      formData.username = ''
      formData.email = ''
      formData.password = ''
      formData.role = 'user'
      formData.is_active = true
    }
  },
  { immediate: true }
)

// 重置表单验证规则中的密码必填
watch(
  () => isEditMode.value,
  (isEdit) => {
    if (formRef.value) {
      const passwordRule = formRef.value.rules?.password
      if (passwordRule && Array.isArray(passwordRule)) {
        passwordRule[0].required = !isEdit
      }
    }
  }
)

function handleClose() {
  formRef.value?.resetFields()
  emit('update:modelValue', false)
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const data = {
        email: formData.email,
        ...(formData.password ? { password: formData.password } : {}),
      }

      if (isEditMode.value && props.user) {
        await userApi.updateUser(props.user.id, data)

        // 如果修改了角色或状态，需要额外调用接口
        if (formData.role !== props.user.role) {
          await userApi.updateUserRole(props.user.id, formData.role)
        }

        if (formData.is_active !== props.user.is_active && !isCurrentUser.value) {
          await userApi.updateUserStatus(props.user.id, formData.is_active)
        }

        ElMessage.success('用户更新成功')
      } else {
        // 新建用户需要调用注册接口，但这里暂不实现
        ElMessage.warning('新建用户功能暂未实现，请联系管理员')
      }

      emit('success')
      handleClose()
    } catch (error: any) {
      console.error('保存用户失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
/* 添加必要的样式 */
</style>
