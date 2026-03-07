// 统一API响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页数据格式
export interface PaginatedData<T> {
  total: number
  page: number
  size: number
  items: T[]
}

// 分页响应格式（匹配后端实际响应结构）
export interface ApiPaginatedResponse<T> {
  code: number
  message: string
  data: PaginatedData<T>
}

// 分页参数
export interface PaginationParams {
  page?: number
  size?: number
}

// 错误响应
export interface ApiError {
  detail: string | Array<{
    loc: string[]
    msg: string
    type: string
  }>
}
