import { describe, expect, it } from 'vitest';

import { buildTagTree } from '../src/utils/tagTree';

describe('buildTagTree', () => {
  it('标签树仅返回顶级入口并保留任意深度子标签', () => {
    const tree = buildTagTree([
      { id: 1, name: '技术', parent_id: null },
      { id: 2, name: '后端', parent_id: 1 },
      { id: 3, name: 'FastAPI', parent_id: 2 },
      { id: 4, name: '生活', parent_id: null },
    ]);

    expect(tree.map((tag) => tag.id)).toEqual([1, 4]);
    expect(tree[0].children[0].id).toBe(2);
    expect(tree[0].children[0].children[0].id).toBe(3);
  });
});