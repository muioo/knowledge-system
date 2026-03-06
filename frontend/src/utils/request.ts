/**
 * 请求工具函数
 * Request utility functions for article content processing
 */

/**
 * 格式化文章内容
 * Format article content by converting markdown to HTML and sanitizing
 * @param content - Raw article content (markdown or plain text)
 * @param maxLength - Maximum length to truncate (optional)
 * @returns Formatted and sanitized HTML content
 */
export function formatArticleContent(content: string, maxLength?: number): string {
  if (!content) {
    return ''
  }

  // Truncate if maxLength is specified
  let formattedContent = content
  if (maxLength && content.length > maxLength) {
    formattedContent = content.substring(0, maxLength) + '...'
  }

  // Basic HTML escaping to prevent XSS
  formattedContent = formattedContent
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')

  // Convert line breaks to <br> tags
  formattedContent = formattedContent.replace(/\n/g, '<br>')

  return formattedContent
}

/**
 * 截断文本
 * Truncate text to a specified length with ellipsis
 * @param text - Text to truncate
 * @param length - Maximum length before truncation
 * @param suffix - Suffix to add (default: '...')
 * @returns Truncated text
 */
export function truncateText(text: string, length: number, suffix: string = '...'): string {
  if (!text) {
    return ''
  }

  if (text.length <= length) {
    return text
  }

  return text.substring(0, length) + suffix
}

/**
 * 从URL提取域名
 * Extract domain from URL
 * @param url - URL to extract domain from
 * @returns Domain name or empty string if invalid
 */
export function extractDomain(url: string): string {
  if (!url) {
    return ''
  }

  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return ''
  }
}

/**
 * 验证URL格式
 * Validate URL format
 * @param url - URL to validate
 * @returns True if valid URL
 */
export function isValidUrl(url: string): boolean {
  if (!url) {
    return false
  }

  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 生成随机颜色
 * Generate random hex color
 * @returns Random hex color string
 */
export function generateRandomColor(): string {
  return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
}

/**
 * 防抖函数
 * Debounce function to limit execution rate
 * @param func - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      func(...args)
    }, delay)
  }
}

/**
 * 节流函数
 * Throttle function to limit execution rate
 * @param func - Function to throttle
 * @param limit - Minimum time between executions in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}
