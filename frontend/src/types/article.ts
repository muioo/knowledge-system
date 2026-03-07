export interface TagInfo {
  id: number
  name: string
  color: string
}

export interface Article {
  id: number
  title: string
  source_url: string | null
  summary: string | null
  keywords: string | null
  author_id: number
  original_filename: string | null
  view_count: number
  created_at: string
  updated_at: string
  tags: TagInfo[]
  html_content: string | null
  html_path: string | null
  processing_status: string | null
  original_html_url: string | null
}

export interface CreateArticleRequest {
  title: string
  summary: string
  keywords: string
  tag_ids?: number[]
}

export interface UpdateArticleRequest {
  title?: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
}

export interface UploadArticleRequest extends CreateArticleRequest {
  file: File
}

export interface UrlImportRequest {
  url: string
  tag_ids?: number[]
  title?: string
}

export interface ArticleListParams {
  page?: number
  size?: number
  tag_id?: number
}
