/**
 * 文章列表请求参数：可选搜索词与标签 ID。
 */
export interface ArticleListParams {
  q?: string;
  tag_id?: number;
}

/**
 * 构造文章列表请求的已应用筛选参数，确保翻页时仍保留搜索词和标签。
 *
 * @param searchQuery 已提交的搜索词。
 * @param selectedTagId 当前选中的标签 ID，null 表示未筛选。
 * @returns 后端文章列表接口所需的查询参数。
 */
export function buildArticleListParams(
  searchQuery: string,
  selectedTagId: number | null,
): ArticleListParams {
  const params: ArticleListParams = {};
  const normalizedSearchQuery = searchQuery.trim();

  if (normalizedSearchQuery) {
    params.q = normalizedSearchQuery;
  }
  if (selectedTagId !== null) {
    params.tag_id = selectedTagId;
  }

  return params;
}