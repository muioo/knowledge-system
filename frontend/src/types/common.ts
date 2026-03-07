export interface PaginationInfo {
  total: number
  page: number
  size: number
}

export interface SelectOption {
  label: string
  value: string | number
}

export interface MenuItem {
  path: string
  name: string
  icon?: string
  children?: MenuItem[]
}
