import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticles } from '../contexts/ArticleContext';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';

interface FileData {
  file: File | null;
  images: File[];
  title: string;
  summary: string;
  keywords: string;
  tagIds: number[];
}

interface UrlData {
  url: string;
  tagIds: number[];
  title: string;
  useAi: boolean;
  summary: string;
  keywords: string;
  apiKey: string;
}

const ArticleCreate: React.FC = () => {
  const navigate = useNavigate();
  const { tags, createArticle, importFromUrl, isLoading } = useArticles();

  const [mode, setMode] = useState<'file' | 'url'>('file');
  const [fileData, setFileData] = useState<FileData>({ file: null, images: [], title: '', summary: '', keywords: '', tagIds: [] });
  const [urlData, setUrlData] = useState<UrlData>({ url: '', tagIds: [], title: '', useAi: false, summary: '', keywords: '', apiKey: '' });
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileData({ ...fileData, file: e.target.files[0] });
    }
  };

  const handleImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setFileData({ ...fileData, images: filesArray });
    }
  };

  const handleTagToggle = (tagId: number) => {
    const currentData = mode === 'file' ? fileData : urlData;
    const newTagIds = currentData.tagIds.includes(tagId)
      ? currentData.tagIds.filter(id => id !== tagId)
      : [...currentData.tagIds, tagId];
    if (mode === 'file') setFileData({ ...fileData, tagIds: newTagIds });
    else setUrlData({ ...urlData, tagIds: newTagIds });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (mode === 'file') {
      if (!fileData.file || !fileData.title || !fileData.summary || !fileData.keywords) {
        setError('请填写所有必填字段');
        return;
      }
      const result = await createArticle({
        file: fileData.file,
        images: fileData.images,
        title: fileData.title,
        summary: fileData.summary,
        keywords: fileData.keywords,
        tagIds: fileData.tagIds
      });
      if (result.success) navigate('/articles');
      else setError(result.error || '创建文章失败');
    } else {
      if (!urlData.url) { setError('请输入文章 URL'); return; }
      if (!urlData.useAi && (!urlData.summary || !urlData.keywords)) {
        setError('未开启 AI 提取时，摘要和关键词为必填');
        return;
      }
      const result = await importFromUrl({
        url: urlData.url,
        tagIds: urlData.tagIds,
        title: urlData.title || undefined,
        use_ai: urlData.useAi,
        summary: !urlData.useAi ? urlData.summary : undefined,
        keywords: !urlData.useAi ? urlData.keywords : undefined,
        api_key: urlData.useAi && urlData.apiKey ? urlData.apiKey : undefined,
      });
      if (result.success) navigate('/articles');
      else setError(result.error || '导入文章失败');
    }
  };

  return (
    <div className="w-full space-y-6">
      <div className="flex gap-2">
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">图片文件（可选）</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImagesChange}
                  className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-green-50 file:text-green-600 hover:file:bg-green-100"
                />
                {fileData.images.length > 0 && (
                  <p className="mt-2 text-sm text-gray-600">
                    已选择 {fileData.images.length} 个图片文件
                  </p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  如果 HTML 文件包含本地图片（如从浏览器保存的网页），请同时选择对应的图片文件
                </p>
              </div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">标题 <span className="text-blue-500">*</span></label><Input type="text" value={fileData.title} onChange={(e) => setFileData({ ...fileData, title: e.target.value })} placeholder="请输入文章标题" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">摘要 <span className="text-blue-500">*</span></label><textarea value={fileData.summary} onChange={(e) => setFileData({ ...fileData, summary: e.target.value })} placeholder="请输入文章摘要" rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-2">关键词 <span className="text-blue-500">*</span></label><Input type="text" value={fileData.keywords} onChange={(e) => setFileData({ ...fileData, keywords: e.target.value })} placeholder="请输入关键词，用逗号分隔" required /></div>
            </>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">文章 URL <span className="text-blue-500">*</span></label>
                <Input type="url" value={urlData.url} onChange={(e) => setUrlData({ ...urlData, url: e.target.value })} placeholder="https://example.com/article" required />
                <p className="mt-1 text-xs text-gray-500">系统将自动抓取网页内容</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">标题（可选）</label>
                <Input type="text" value={urlData.title} onChange={(e) => setUrlData({ ...urlData, title: e.target.value })} placeholder="留空则使用网页标题" />
              </div>

              <div className="border-t border-gray-100 pt-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={urlData.useAi}
                    onChange={(e) => setUrlData({ ...urlData, useAi: e.target.checked })}
                    className="w-4 h-4 text-blue-500 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">使用 AI 提取摘要和关键词</span>
                </label>
                <p className="mt-1 ml-6 text-xs text-gray-500">需要提供 API Key，AI 将自动生成摘要和关键词</p>
              </div>

              {urlData.useAi ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                  <Input type="password" value={urlData.apiKey} onChange={(e) => setUrlData({ ...urlData, apiKey: e.target.value })} placeholder="输入火山引擎 ARK API Key" />
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">摘要 <span className="text-blue-500">*</span></label>
                    <textarea value={urlData.summary} onChange={(e) => setUrlData({ ...urlData, summary: e.target.value })} placeholder="请输入文章摘要" rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">关键词 <span className="text-blue-500">*</span></label>
                    <Input type="text" value={urlData.keywords} onChange={(e) => setUrlData({ ...urlData, keywords: e.target.value })} placeholder="请输入关键词，用逗号分隔" required />
                  </div>
                </>
              )}
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">标签</label>
            <div className="flex flex-wrap gap-2">
              {tags.map(tag => (
                <button
                  key={tag.id}
                  type="button"
                  onClick={() => handleTagToggle(tag.id)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${(mode === 'file' ? fileData.tagIds : urlData.tagIds).includes(tag.id) ? 'text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                  style={(mode === 'file' ? fileData.tagIds : urlData.tagIds).includes(tag.id) ? { backgroundColor: tag.color } : {}}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button type="submit" disabled={isLoading} className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              {isLoading ? '处理中...' : mode === 'file' ? '上传文章' : '导入文章'}
            </button>
            <button type="button" onClick={() => navigate('/articles')} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              取消
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default ArticleCreate;
