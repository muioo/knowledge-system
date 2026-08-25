import assert from 'node:assert/strict';
import test from 'node:test';

import { buildTagTree } from '../src/utils/tagTree.js';

test('标签树仅返回顶级入口并保留任意深度子标签', () => {
  const tree = buildTagTree([
    { id: 1, name: '技术', parent_id: null },
    { id: 2, name: '后端', parent_id: 1 },
    { id: 3, name: 'FastAPI', parent_id: 2 },
    { id: 4, name: '生活', parent_id: null },
  ]);

  assert.deepEqual(tree.map((tag) => tag.id), [1, 4]);
  assert.equal(tree[0].children[0].id, 2);
  assert.equal(tree[0].children[0].children[0].id, 3);
});
