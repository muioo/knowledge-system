import type { Tag } from './tag'

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed'

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
  tags: Tag[]
  html_content: string | null
  html_path: string | null
  processing_status: ProcessingStatus | null
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
  use_ai?: boolean
  summary?: string
  keywords?: string
}

export interface ArticleListParams {
  page?: number
  size?: number
  tag_id?: number
}
