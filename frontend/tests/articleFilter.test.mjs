import assert from 'node:assert/strict';
import test from 'node:test';

import { buildArticleListParams } from '../src/pages/articleFilter.js';

test('标签和搜索词会同时作为文章列表请求参数', () => {
  assert.deepEqual(
    buildArticleListParams('FastAPI', 12),
    { q: 'FastAPI', tag_id: 12 },
  );
});

test('取消标签筛选后不再提交 tag_id', () => {
  assert.deepEqual(buildArticleListParams('', null), {});
});
