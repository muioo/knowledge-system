/**
 * 将后端返回的平铺标签组装成仅以顶级标签为入口的树。
 * 缺失父节点的标签作为顶级标签展示，避免脏数据导致标签不可管理。
 */
export function buildTagTree(tags) {
  const nodesById = new Map(
    tags.map((tag) => [tag.id, { ...tag, children: [] }]),
  );
  const roots = [];

  for (const tag of tags) {
    const node = nodesById.get(tag.id);
    const parent = tag.parent_id == null ? null : nodesById.get(tag.parent_id);
    if (parent && parent.id !== node.id) {
      parent.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}
