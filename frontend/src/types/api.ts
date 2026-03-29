// 通用响应格式
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 分页响应
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  size: number;
  items: T[];
}

// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}

// 登录请求
export interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// 标签类型
export interface Tag {
  id: number;
  name: string;
  color: string;
  created_at?: string;
}

// 文章类型
export interface Article {
  id: number;
  title: string;
  source_url: string | null;
  summary: string | null;
  keywords: string | null;
  author_id: number;
  original_filename: string | null;
  view_count: number;
  created_at: string;
  updated_at: string;
  tags: Tag[];
  html_content: string | null;
  html_path: string | null;
  processing_status: string | null;
  original_html_url: string | null;
  // 阅读状态
  is_read?: boolean | null;
  reading_progress?: number | null;
}

// 文章创建数据
export interface ArticleCreateData {
  title?: string;
  summary?: string;
  keywords?: string;
  tagIds?: number[];
}

// URL导入数据
export interface UrlImportData {
  url: string;
  tagIds?: number[];
  title?: string;
  use_ai?: boolean;
  summary?: string;
  keywords?: string;
  api_key?: string;
}

// 阅读统计类型
export interface ReadingStats {
  article_id: number;
  article_title: string;
  total_views: number;
  total_duration: number;
  last_read_at: string | null;
}

// 阅读历史类型
export interface ReadingHistory {
  id: number;
  article_id: number;
  article_title: string;
  started_at: string;
  ended_at: string | null;
  reading_duration: number;
  reading_progress: number;
}

// 阅读趋势
export interface ReadingTrend {
  date: string;
  minutes: number;
  articles: number;
}

// 时段统计
export interface TimePeriod {
  name: string;
  count: number;
  duration: number;
  percentage: number;
}

// 热力图数据
export interface HeatmapData {
  hour: number;
  day: number;
  count: number;
}

// 时间分布
export interface TimeDistribution {
  periods: TimePeriod[];
  heatmap: HeatmapData[];
}

// 阅读进度
export interface ReadingProgress {
  article_id: number;
  article_title: string;
  total_views: number;
  total_duration: number;
  reading_progress: number;
  last_read_at: string | null;
}
