// 验证用户名
export function validateUsername(username: string): boolean {
  return username.length >= 3 && username.length <= 50
}

// 验证邮箱
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 验证密码
export function validatePassword(password: string): boolean {
  return password.length >= 6 && password.length <= 50
}

// 验证文章标题
export function validateTitle(title: string): boolean {
  return title.length >= 1 && title.length <= 255
}
