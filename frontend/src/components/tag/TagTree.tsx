import React, { useState } from 'react';
import type { Tag } from '../../types/api';
import type { TagTreeNode } from '../../utils/tagTree';

export type { TagTreeNode };

interface TagTreeProps {
  tags: TagTreeNode[];
  onCreateChild: (tag: Tag) => void;
  onEdit: (tag: Tag) => void;
  onDelete: (tagId: number) => void;
}

interface TagTreeItemProps extends Omit<TagTreeProps, 'tags'> {
  tag: TagTreeNode;
  depth: number;
}

/** 渲染单个标签节点，并按需展开其子标签。 */
const TagTreeItem: React.FC<TagTreeItemProps> = ({ tag, depth, onCreateChild, onEdit, onDelete }) => {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = tag.children.length > 0;

  return (
    <div>
      <div
        className="flex items-center justify-between gap-3 rounded-lg bg-gray-50 p-3 hover:bg-gray-100"
        style={{ marginLeft: `${depth * 24}px` }}
      >
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={() => setExpanded((value) => !value)}
            disabled={!hasChildren}
            className="w-6 text-gray-500 disabled:invisible"
            aria-label={expanded ? '收起子标签' : '展开子标签'}
          >
            {expanded ? '▾' : '▸'}
          </button>
          <div className="h-5 w-5 shrink-0 rounded-full" style={{ backgroundColor: tag.color }} />
          <span className="truncate font-medium">{tag.name}</span>
          <span className="text-xs text-gray-500">{tag.article_count ?? 0} 篇</span>
        </div>
        <div className="flex shrink-0 gap-2 text-sm">
          <button type="button" onClick={() => onCreateChild(tag)} className="text-green-600">新建子标签</button>
          <button type="button" onClick={() => onEdit(tag)} className="text-blue-600">编辑</button>
          <button type="button" onClick={() => onDelete(tag.id)} className="text-red-600">删除</button>
        </div>
      </div>
      {expanded && tag.children.map((child) => (
        <TagTreeItem
          key={child.id}
          tag={child}
          depth={depth + 1}
          onCreateChild={onCreateChild}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

/** 渲染顶级标签列表；子标签只在用户展开父节点后显示。 */
const TagTree: React.FC<TagTreeProps> = ({ tags, onCreateChild, onEdit, onDelete }) => (
  <div className="space-y-2">
    {tags.map((tag) => (
      <TagTreeItem
        key={tag.id}
        tag={tag}
        depth={0}
        onCreateChild={onCreateChild}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    ))}
  </div>
);

export default TagTree;
