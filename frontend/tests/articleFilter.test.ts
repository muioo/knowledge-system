import { describe, expect, it } from 'vitest';

import { buildArticleListParams } from '../src/pages/articleFilter';

describe('buildArticleListParams', () => {
  it('标签和搜索词会同时作为文章列表请求参数', () => {
    expect(buildArticleListParams('FastAPI', 12)).toEqual({ q: 'FastAPI', tag_id: 12 });
  });

  it('取消标签筛选后不再提交 tag_id', () => {
    expect(buildArticleListParams('', null)).toEqual({});
  });
});