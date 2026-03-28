import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticles } from '../contexts/ArticleContext';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';

const ArticleCreate = () => {
  const navigate = useNavigate();
  const { tags, createArticle, importFromUrl, isLoading } = useArticles();

  const [mode, setMode] = useState('file');
  const [fileData, setFileData] = useState({ file: null, title: '', summary: '', keywords: '', tagIds: [] });
  const [urlData, setUrlData] = useState({ url: '', tagIds: [], title: '' });
  const [error, setError] = useState('');

  const handleFileChange = (e) => { setFileData({ ...fileData, file: e.target.files[0] }); };

  const handleTagToggle = (tagId) => {
    const currentData = mode === 'file' ? fileData : urlData;
    const newTagIds = currentData.tagIds.includes(tagId)
      ? currentData.tagIds.filter(id => id !== tagId)
      : [...currentData.tagIds, tagId];
    if (mode === 'file') setFileData({ ...fileData, tagIds: newTagIds });
    else setUrlData({ ...urlData, tagIds: newTagIds });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (mode === 'file') {
      if (!fileData.file || !fileData.title || !fileData.summary || !fileData.keywords) {
        setError('请填写所有必填字段');
        return;
      }
      const result = await createArticle(fileData);
      if (result.success) navigate('/articles');
      else setError(result.error);
    } else {
      if (!urlData.url) { setError('请输入文章 URL'); return; }
      const result = await importFromUrl(urlData);
      if (result.success) navigate('/articles');
      else setError(result.error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">创建文章</h1>
        <p className="text-gray-600">通过文件上传或 URL 导入创建新文章</p>
      </div>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setMode('file')} className={`px-4 py-2 rounded-lg transition-colors ${mode === 'file' ? 'bg-blue-500 text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
          文件上传
        </button>
        <button onClick={() => setMode('url')} className={`px-4 py-2 rounded-lg transition-colors ${mode === 'url' ? 'bg-blue-500 text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
          URL 导入
        </button>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>}

          {mode === 'file' ? (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">HTML 文件 <span className="text-blue-500">*</span></label>
                <input type="file" accept=".html,.htm" onChange={handleFileChange} className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100" />
                {fileData.file && <p className="mt-2 text-sm text-gray-600">已选择: {fileData.file.name}</p>}
              </div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">标题 <span className="text-blue-500">*</span></label><Input type="text" value={fileData.title} onChange={(e) => setFileData({ ...fileData, title: e.target.value })} placeholder="请输入文章标题" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">摘要 <span className="text-blue-500">*</span></label><textarea value={fileData.summary} onChange={(e) => setFileData({ ...fileData, summary: e.target.value })} placeholder="请输入文章摘要" rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">关键词 <span className="text-blue-500">*</span></label><Input type="text" value={fileData.keywords} onChange={(e) => setFileData({ ...fileData, keywords: e.target.value })} placeholder="请输入关键词，用逗号分隔" required /></div>
            </>
          ) : (
            <>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">文章 URL <span className="text-blue-500">*</span></label><Input type="url" value={urlData.url} onChange={(e) => setUrlData({ ...urlData, url: e.target.value })} placeholder="https://example.com/article" required /><p className="mt-1 text-xs text-gray-500">系统将自动抓取内容并使用 AI 提取标题、摘要和关键词</p></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">自定义标题（可选）</label><Input type="text" value={urlData.title} onChange={(e) => setUrlData({ ...urlData, title: e.target.value })} placeholder="留空则由 AI 自动提取" /></div>
            </>
          )}

          {tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">选择标签</label>
              <div className="flex flex-wrap gap-2">
                {tags.map(tag => {
                  const isSelected = (mode === 'file' ? fileData.tagIds : urlData.tagIds).includes(tag.id);
                  return <button key={tag.id} type="button" onClick={() => handleTagToggle(tag.id)} className={`px-3 py-1 rounded-full text-sm transition-colors ${isSelected ? 'text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`} style={isSelected ? { backgroundColor: tag.color } : {}}>{tag.name}</button>;
                })}
              </div>
            </div>
          )}

          <div className="flex gap-4 pt-4">
            <button type="submit" disabled={isLoading} className="flex-1 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-colors disabled:opacity-50">
              {isLoading ? '处理中...' : mode === 'file' ? '上传文章' : '导入文章'}
            </button>
            <button type="button" onClick={() => navigate('/articles')} className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">取消</button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default ArticleCreate;
