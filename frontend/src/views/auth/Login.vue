<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="formRules"
    label-position="top"
    class="auth-form"
    @submit.prevent="handleSubmit"
  >
    <!-- Username field -->
    <el-form-item label="Username" prop="username">
      <el-input
        v-model="formData.username"
        placeholder="Enter your username"
        :prefix-icon="User"
        size="large"
        clearable
      />
    </el-form-item>

    <!-- Email field (only for registration) -->
    <el-form-item v-if="!isLoginMode" label="Email" prop="email">
      <el-input
        v-model="formData.email"
        type="email"
        placeholder="Enter your email"
        :prefix-icon="Message"
        size="large"
        clearable
      />
    </el-form-item>

    <!-- Password field -->
    <el-form-item label="Password" prop="password">
      <el-input
        v-model="formData.password"
        type="password"
        placeholder="Enter your password"
        :prefix-icon="Lock"
        size="large"
        show-password
      />
    </el-form-item>

    <!-- Confirm password field (only for registration) -->
    <el-form-item v-if="!isLoginMode" label="Confirm Password" prop="confirmPassword">
      <el-input
        v-model="formData.confirmPassword"
        type="password"
        placeholder="Confirm your password"
        :prefix-icon="Lock"
        size="large"
      />
    </el-form-item>

    <!-- Remember me & Forgot password (only for login) -->
    <div v-if="isLoginMode" class="auth-options">
      <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
      <el-link type="primary" :underline="false">Forgot password?</el-link>
    </div>

    <!-- Submit button -->
    <el-form-item class="auth-submit">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        native-type="submit"
        class="auth-button"
      >
        {{ loading ? 'Processing...' : (isLoginMode ? 'Sign In' : 'Create Account') }}
      </el-button>
    </el-form-item>
  </el-form>

  <!-- Toggle between login and register -->
  <div class="auth-footer">
    <span class="auth-text">
      {{ isLoginMode ? "Don't have an account?" : 'Already have an account?' }}
    </span>
    <el-link type="primary" :underline="false" @click="toggleMode">
      {{ isLoginMode ? 'Sign Up' : 'Sign In' }}
    </el-link>
  </div>

  <!-- Divider -->
  <el-divider>Or continue with</el-divider>

  <!-- Social login (placeholder for future) -->
  <div class="auth-social">
    <el-button class="social-button" disabled>
      <el-icon><Platform /></el-icon>
      WeChat
    </el-button>
    <el-button class="social-button" disabled>
      <el-icon><Platform /></el-icon>
      GitHub
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Message, Lock, Platform } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import type { UserLogin, UserCreate } from '../../types'

/**
 * Router and stores
 */
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

/**
 * Form state
 */
const isLoginMode = ref(true)
const loading = ref(false)
const rememberMe = ref(false)
const formRef = ref<FormInstance>()

/**
 * Form data
 */
const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

/**
 * Form validation rules
 */
const formRules = computed<FormRules>(() => ({
  username: [
    { required: true, message: 'Please enter your username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be 3-20 characters', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: 'Username can only contain letters, numbers, and underscores', trigger: 'blur' },
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' },
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, max: 50, message: 'Password must be 6-50 characters', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== formData.password) {
          callback(new Error('Passwords do not match'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}))

/**
 * Toggle between login and register mode
 */
function toggleMode(): void {
  isLoginMode.value = !isLoginMode.value
  formRef.value?.clearValidate()
  formRef.value?.resetFields()
}

/**
 * Handle form submission
 */
async function handleSubmit(): Promise<void> {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    if (isLoginMode.value) {
      await handleLogin()
    } else {
      await handleRegister()
    }
  } catch (error) {
    // Validation failed or API error
    console.error('Form validation or submission error:', error)
  } finally {
    loading.value = false
  }
}

/**
 * Handle login
 */
async function handleLogin(): Promise<void> {
  try {
    const credentials: UserLogin = {
      username: formData.username,
      password: formData.password,
    }

    await authStore.login(credentials)

    ElMessage.success('Login successful!')

    // Redirect to the page user was trying to access, or dashboard
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Login failed'
    ElMessage.error(errorMessage)
  }
}

/**
 * Handle registration
 */
async function handleRegister(): Promise<void> {
  try {
    const userData: UserCreate = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
    }

    await authStore.register(userData)

    ElMessage.success('Registration successful! Please log in.')

    // Switch to login mode and populate username
    isLoginMode.value = true
    formData.confirmPassword = ''
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Registration failed'
    ElMessage.error(errorMessage)
  }
}
</script>

<style scoped lang="scss">
.auth-form {
  margin-bottom: 24px;

  :deep(.el-form-item) {
    margin-bottom: 24px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #303133;
  }
}

.auth-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.auth-submit {
  margin-bottom: 0;

  :deep(.el-form-item__content) {
    width: 100%;
  }
}

.auth-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
}

.auth-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.auth-text {
  font-size: 14px;
  color: #909399;
}

.auth-social {
  display: flex;
  gap: 16px;
}

.social-button {
  flex: 1;
  height: 44px;
  font-weight: 500;
}

:deep(.el-divider__text) {
  background-color: transparent;
  font-size: 14px;
  color: #909399;
}

@media (max-width: 480px) {
  .auth-social {
    flex-direction: column;
  }
}
</style>
