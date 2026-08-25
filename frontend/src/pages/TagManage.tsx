import React, { useEffect, useMemo, useState } from 'react';
import { tagApi } from '../api/tag';
import TagTree, { type TagTreeNode } from '../components/tag/TagTree';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import type { Tag } from '../types/api';
import { buildTagTree } from '../utils/tagTree';

interface TagFormData {
  name: string;
  color: string;
  parentId: number | null;
}

const EMPTY_FORM: TagFormData = { name: '', color: '#3b82f6', parentId: null };
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];

/** 从接口异常中提取可读错误信息。 */
const getErrorMessage = (error: any, fallback: string): string => (
  error?.response?.data?.detail || error?.message || fallback
);

/** 管理顶级标签和任意深度的子标签。 */
const TagManage: React.FC = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<TagFormData>(EMPTY_FORM);
  const [message, setMessage] = useState('');
  const tagTree = useMemo(() => buildTagTree(tags) as TagTreeNode[], [tags]);

  /** 重新加载完整标签集合，前端再构建顶级标签树。 */
  const fetchTags = async () => {
    setIsLoading(true);
    try {
      setTags(await tagApi.getTags());
    } catch (error) {
      setMessage(getErrorMessage(error, '获取标签失败'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { void fetchTags(); }, []);

  /** 打开新建顶级标签表单。 */
  const handleCreateRoot = () => {
    setEditingId(null);
    setFormData(EMPTY_FORM);
    setShowForm(true);
  };

  /** 打开新建子标签表单并固定当前父标签。 */
  const handleCreateChild = (parent: Tag) => {
    setEditingId(null);
    setFormData({ ...EMPTY_FORM, parentId: parent.id });
    setShowForm(true);
  };

  /** 打开标签编辑表单。 */
  const handleEdit = (tag: Tag) => {
    setEditingId(tag.id);
    setFormData({ name: tag.name, color: tag.color, parentId: tag.parent_id ?? null });
    setShowForm(true);
  };

  /** 创建或更新标签，然后刷新标签树。 */
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const payload = { name: formData.name, color: formData.color, parent_id: formData.parentId };
      if (editingId === null) await tagApi.createTag(payload);
      else await tagApi.updateTag(editingId, payload);
      setMessage(editingId === null ? '标签已创建' : '标签已更新');
      setShowForm(false);
      setEditingId(null);
      setFormData(EMPTY_FORM);
      await fetchTags();
    } catch (error) {
      setMessage(getErrorMessage(error, '标签操作失败'));
    }
  };

  /** 删除没有子标签的标签。 */
  const handleDelete = async (tagId: number) => {
    if (!window.confirm('确定要删除这个标签吗？')) return;
    try {
      await tagApi.deleteTag(tagId);
      setMessage('标签已删除');
      await fetchTags();
    } catch (error) {
      setMessage(getErrorMessage(error, '删除标签失败'));
    }
  };

  return (
    <div className="w-full space-y-6">
      {message && <div className="rounded-lg bg-blue-50 p-4 text-blue-700">{message}</div>}
      {showForm && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">{editingId === null ? '创建标签' : '编辑标签'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input value={formData.name} onChange={(event) => setFormData({ ...formData, name: event.target.value })} placeholder="标签名称" required />
            <select value={formData.parentId ?? ''} onChange={(event) => setFormData({ ...formData, parentId: event.target.value ? Number(event.target.value) : null })} className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
              <option value="">顶级标签</option>
              {tags.filter((tag) => tag.id !== editingId).map((tag) => <option key={tag.id} value={tag.id}>{tag.name}</option>)}
            </select>
            <div className="flex flex-wrap gap-2">
              {COLORS.map((color) => <button key={color} type="button" aria-label={`选择颜色 ${color}`} onClick={() => setFormData({ ...formData, color })} className="h-8 w-8 rounded-full" style={{ backgroundColor: color }} />)}
              <Input type="color" value={formData.color} onChange={(event) => setFormData({ ...formData, color: event.target.value })} className="h-10 w-20" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="rounded-lg bg-blue-500 px-4 py-2 text-white">保存</button>
              <button type="button" onClick={() => setShowForm(false)} className="rounded-lg border px-4 py-2">取消</button>
            </div>
          </form>
        </Card>
      )}
      <Card>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">顶级标签</h2>
          {!showForm && <button type="button" onClick={handleCreateRoot} className="rounded-lg bg-blue-500 px-4 py-2 text-white">新建顶级标签</button>}
        </div>
        {isLoading ? <div className="py-8 text-center">加载中...</div> : tagTree.length === 0 ? <div className="py-8 text-center text-gray-500">暂无标签</div> : <TagTree tags={tagTree} onCreateChild={handleCreateChild} onEdit={handleEdit} onDelete={handleDelete} />}
      </Card>
    </div>
  );
};

export default TagManage;
