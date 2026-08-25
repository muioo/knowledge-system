/**
 * 构造文章列表请求的已应用筛选参数，确保翻页时仍保留搜索词和标签。
 *
 * @param {string} searchQuery 已提交的搜索词。
 * @param {number | null} selectedTagId 当前选中的标签 ID。
 * @returns {{ q?: string, tag_id?: number }} 后端文章列表接口所需的查询参数。
 */
export function buildArticleListParams(searchQuery, selectedTagId) {
  const params = {};
  const normalizedSearchQuery = searchQuery.trim();

  if (normalizedSearchQuery) {
    params.q = normalizedSearchQuery;
  }
  if (selectedTagId !== null) {
    params.tag_id = selectedTagId;
  }

  return params;
}
