import type { Tag } from '../types/api';

/**
 * 标签树的节点类型：在 {@link Tag} 基础上增加子标签列表。
 */
export interface TagTreeNode extends Tag {
  children: TagTreeNode[];
}

/**
 * 将后端返回的平铺标签组装成仅以顶级标签为入口的树。
 * 缺失父节点的标签作为顶级标签展示，避免脏数据导致标签不可管理。
 *
 * @param tags 后端返回的平铺标签数组。
 * @returns 以顶级标签为入口的树。
 */
export function buildTagTree(tags: Tag[]): TagTreeNode[] {
  const nodesById = new Map<number, TagTreeNode>(
    tags.map((tag) => [tag.id, { ...tag, children: [] }]),
  );
  const roots: TagTreeNode[] = [];

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