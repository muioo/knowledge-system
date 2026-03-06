/**
 * UI 状态管理 Store
 * UI state management store with Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // State
  const sidebarCollapsed = ref(false)
  const globalLoading = ref(false)
  const loadingText = ref<string>('')

  // Theme state
  const theme = ref<'light' | 'dark'>('light')

  // Modal state
  const modalVisible = ref(false)
  const modalTitle = ref('')
  const modalContent = ref('')

  // Toast notification state
  const toastVisible = ref(false)
  const toastMessage = ref('')
  const toastType = ref<'success' | 'error' | 'warning' | 'info'>('info')

  // Dialog state
  const dialogVisible = ref(false)
  const dialogTitle = ref('')
  const dialogMessage = ref<string | null>('')
  const dialogOnConfirm = ref<(() => void) | null>(null)
  const dialogOnCancel = ref<(() => void) | null>(null)

  // Getters
  const isDarkMode = computed(() => theme.value === 'dark')
  const isLoading = computed(() => globalLoading.value)
  const isSidebarOpen = computed(() => !sidebarCollapsed.value)

  // Actions

  /**
   * Toggle sidebar collapsed state
   */
  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
    // Persist to localStorage
    localStorage.setItem('sidebar_collapsed', String(sidebarCollapsed.value))
  }

  /**
   * Set sidebar collapsed state
   * @param collapsed - Whether sidebar should be collapsed
   */
  function setSidebarCollapsed(collapsed: boolean): void {
    sidebarCollapsed.value = collapsed
    localStorage.setItem('sidebar_collapsed', String(collapsed))
  }

  /**
   * Initialize sidebar state from localStorage
   */
  function initializeSidebar(): void {
    const stored = localStorage.getItem('sidebar_collapsed')
    if (stored !== null) {
      sidebarCollapsed.value = stored === 'true'
    }
  }

  /**
   * Set global loading state
   * @param loading - Loading state
   * @param text - Optional loading text
   */
  function setGlobalLoading(loading: boolean, text?: string): void {
    globalLoading.value = loading
    loadingText.value = text ?? ''
  }

  /**
   * Show global loading with text
   * @param text - Loading text
   */
  function showLoading(text?: string): void {
    globalLoading.value = true
    loadingText.value = text ?? 'Loading...'
  }

  /**
   * Hide global loading
   */
  function hideLoading(): void {
    globalLoading.value = false
    loadingText.value = ''
  }

  /**
   * Toggle theme between light and dark
   */
  function toggleTheme(): void {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  /**
   * Set theme
   * @param newTheme - Theme to set
   */
  function setTheme(newTheme: 'light' | 'dark'): void {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  /**
   * Initialize theme from localStorage or system preference
   */
  function initializeTheme(): void {
    // Check localStorage first
    const storedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null

    if (storedTheme) {
      theme.value = storedTheme
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }

    document.documentElement.setAttribute('data-theme', theme.value)
  }

  /**
   * Show modal
   * @param title - Modal title
   * @param content - Modal content
   */
  function showModal(title: string, content: string): void {
    modalTitle.value = title
    modalContent.value = content
    modalVisible.value = true
  }

  /**
   * Hide modal
   */
  function hideModal(): void {
    modalVisible.value = false
    modalTitle.value = ''
    modalContent.value = ''
  }

  /**
   * Show toast notification
   * @param message - Toast message
   * @param type - Toast type (default: 'info')
   * @param duration - Duration in milliseconds (default: 3000)
   */
  function showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration = 3000): void {
    toastMessage.value = message
    toastType.value = type
    toastVisible.value = true

    setTimeout(() => {
      hideToast()
    }, duration)
  }

  /**
   * Hide toast notification
   */
  function hideToast(): void {
    toastVisible.value = false
    toastMessage.value = ''
  }

  /**
   * Show success toast
   * @param message - Success message
   */
  function showSuccess(message: string): void {
    showToast(message, 'success')
  }

  /**
   * Show error toast
   * @param message - Error message
   */
  function showError(message: string): void {
    showToast(message, 'error')
  }

  /**
   * Show warning toast
   * @param message - Warning message
   */
  function showWarning(message: string): void {
    showToast(message, 'warning')
  }

  /**
   * Show info toast
   * @param message - Info message
   */
  function showInfo(message: string): void {
    showToast(message, 'info')
  }

  /**
   * Show dialog
   * @param title - Dialog title
   * @param message - Dialog message
   * @param onConfirm - Callback when confirmed
   * @param onCancel - Callback when cancelled (optional)
   */
  function showDialog(
    title: string,
    message: string,
    onConfirm: () => void,
    onCancel?: () => void
  ): void {
    dialogTitle.value = title
    dialogMessage.value = message
    dialogOnConfirm.value = onConfirm
    dialogOnCancel.value = onCancel ?? null
    dialogVisible.value = true
  }

  /**
   * Hide dialog
   */
  function hideDialog(): void {
    dialogVisible.value = false
    dialogTitle.value = ''
    dialogMessage.value = null
    dialogOnConfirm.value = null
    dialogOnCancel.value = null
  }

  /**
   * Confirm dialog
   */
  function confirmDialog(): void {
    if (dialogOnConfirm.value) {
      dialogOnConfirm.value()
    }
    hideDialog()
  }

  /**
   * Cancel dialog
   */
  function cancelDialog(): void {
    if (dialogOnCancel.value) {
      dialogOnCancel.value()
    }
    hideDialog()
  }

  /**
   * Reset UI state to defaults
   */
  function resetUiState(): void {
    sidebarCollapsed.value = false
    globalLoading.value = false
    loadingText.value = ''
    modalVisible.value = false
    toastVisible.value = false
    dialogVisible.value = false
  }

  return {
    // State
    sidebarCollapsed,
    globalLoading,
    loadingText,
    theme,
    modalVisible,
    modalTitle,
    modalContent,
    toastVisible,
    toastMessage,
    toastType,
    dialogVisible,
    dialogTitle,
    dialogMessage,

    // Getters
    isDarkMode,
    isLoading,
    isSidebarOpen,

    // Actions - Sidebar
    toggleSidebar,
    setSidebarCollapsed,
    initializeSidebar,

    // Actions - Loading
    setGlobalLoading,
    showLoading,
    hideLoading,

    // Actions - Theme
    toggleTheme,
    setTheme,
    initializeTheme,

    // Actions - Modal
    showModal,
    hideModal,

    // Actions - Toast
    showToast,
    hideToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // Actions - Dialog
    showDialog,
    hideDialog,
    confirmDialog,
    cancelDialog,

    // Actions - Reset
    resetUiState,
  }
})
