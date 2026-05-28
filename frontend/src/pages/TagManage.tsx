import React, { useState, useEffect } from 'react';
import { tagApi } from '../api/tag';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import type { Tag } from '../types/api';

const TagManage: React.FC = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<{ name: string; color: string }>({ name: '', color: '#3b82f6' });
  const [message, setMessage] = useState('');

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];

  useEffect(() => { fetchTags(); }, []);

  const fetchTags = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tagApi.getTags();
      setTags(data);
    } catch (err: any) {
      setError(err.message || '获取标签失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      if (editingId) {
        await tagApi.updateTag(editingId, formData);
        setMessage('标签已更新');
      } else {
        await tagApi.createTag(formData);
        setMessage('标签已创建');
      }
      setIsCreating(false);
      setEditingId(null);
      setFormData({ name: '', color: '#3b82f6' });
      await fetchTags();
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setMessage(err.message || '操作失败');
    }
  };

  const handleEdit = (tag: Tag) => {
    setEditingId(tag.id);
    setFormData({ name: tag.name, color: tag.color });
    setIsCreating(false);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('确定要删除这个标签吗？')) return;
    try {
      await tagApi.deleteTag(id);
      setMessage('标签已删除');
      await fetchTags();
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setMessage(err.message || '删除失败');
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingId(null);
    setFormData({ name: '', color: '#3b82f6' });
  };

  return (
    <div className="w-full space-y-6">
      {message && <div className={`p-4 rounded-lg ${message.includes('失败') || message.includes('错误') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>{message}</div>}

      {(isCreating || editingId) && (
        <Card>
          <h2 className="text-lg font-semibold mb-4">{editingId ? '编辑标签' : '创建新标签'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="block text-sm font-medium text-gray-700 mb-2">标签名称</label><Input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="请输入标签名称" required /></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-2">标签颜色</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {colors.map(color => <button key={color} type="button" onClick={() => setFormData({ ...formData, color })} className={`w-8 h-8 rounded-full transition-transform ${formData.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''}`} style={{ backgroundColor: color }} />)}
              </div>
              <Input type="color" value={formData.color} onChange={(e) => setFormData({ ...formData, color: e.target.value })} className="w-20 h-10" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">{editingId ? '更新标签' : '创建标签'}</button>
              <button type="button" onClick={handleCancel} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">取消</button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">标签列表</h2>
          {!isCreating && !editingId && <button onClick={() => setIsCreating(true)} className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">新建标签</button>}
        </div>

        {isLoading ? <div className="text-center py-8"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div> : error ? <div className="text-red-500">{error}</div> : tags.length === 0 ? <div className="text-center py-8 text-gray-500">暂无标签</div> : (
          <div className="space-y-2">
            {tags.map(tag => (
              <div key={tag.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full" style={{ backgroundColor: tag.color }}></div>
                  <span className="font-medium">{tag.name}</span>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(tag)} className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">编辑</button>
                  <button onClick={() => handleDelete(tag.id)} className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">删除</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default TagManage;
