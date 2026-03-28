import React, { useState, useEffect } from 'react';
import { tagApi } from '../api/tag';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';

const TagManage = () => {
  const [tags, setTags] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: '', color: '#3b82f6' });
  const [message, setMessage] = useState('');

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];

  useEffect(() => { fetchTags(); }, []);

  const fetchTags = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tagApi.getTags();
      setTags(data);
    } catch (err) {
      setError(err.message || '获取标签失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    const result = editingId ? await tagApi.updateTag(editingId, formData) : await tagApi.createTag(formData);
    if (result.success || result) {
      setMessage(editingId ? '标签已更新' : '标签已创建');
      setIsCreating(false);
      setEditingId(null);
      setFormData({ name: '', color: '#3b82f6' });
      await fetchTags();
      setTimeout(() => setMessage(''), 3000);
    } else {
      setMessage(result.error || '操作失败');
    }
  };

  const handleEdit = (tag) => { setEditingId(tag.id); setFormData({ name: tag.name, color: tag.color }); setIsCreating(false); };
  const handleDelete = async (id) => {
    if (!window.confirm('确定要删除这个标签吗？')) return;
    try {
      await tagApi.deleteTag(id);
      setMessage('标签已删除');
      await fetchTags();
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(err.message || '删除失败');
    }
  };
  const handleCancel = () => { setIsCreating(false); setEditingId(null); setFormData({ name: '', color: '#3b82f6' }); };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">标签管理</h1>
        <p className="text-gray-600">管理和组织您的文章标签</p>
      </div>

      {message && <div className={`mb-4 p-4 rounded-lg ${message.includes('失败') || message.includes('错误') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>{message}</div>}

      {(isCreating || editingId) && (
        <Card className="mb-6">
          <h2 className="text-lg font-semibold mb-4">{editingId ? '编辑标签' : '创建新标签'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="block text-sm font-medium text-gray-700 mb-2">标签名称</label><Input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="请输入标签名称" required /></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-2">标签颜色</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {colors.map(color => <button key={color} type="button" onClick={() => setFormData({ ...formData, color })} className={`w-8 h-8 rounded-full transition-transform ${formData.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''}`} style={{ backgroundColor: color }} />)}
              </div>
              <Input type="color" value={formData.color} onChange={(e) => setFormData({ ...formData, color: e.target.value })} className="w-20 h-10" />
            </div>
            <div className="flex gap-4">
              <button type="submit" className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">{editingId ? '更新' : '创建'}</button>
              <button type="button" onClick={handleCancel} className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">取消</button>
            </div>
          </form>
        </Card>
      )}

      {!isCreating && !editingId && <button onClick={() => setIsCreating(true)} className="mb-6 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">+ 创建新标签</button>}

      {isLoading ? <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div> : error ? <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div> : tags.length === 0 ? <div className="text-center py-12 text-gray-500">暂无标签，点击上方按钮创建第一个标签</div> : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tags.map(tag => (
            <Card key={tag.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold" style={{ backgroundColor: tag.color }}>{tag.name.charAt(0).toUpperCase()}</div>
                <div><h3 className="font-semibold text-gray-900">{tag.name}</h3><p className="text-xs text-gray-500">{tag.color}</p></div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleEdit(tag)} className="p-2 text-gray-400 hover:text-blue-500 transition-colors"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" /></svg></button>
                <button onClick={() => handleDelete(tag.id)} className="p-2 text-gray-400 hover:text-red-500 transition-colors"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></svg></button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TagManage;
