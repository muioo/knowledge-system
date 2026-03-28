import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { articleApi } from '../api/article';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';

const ArticleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [htmlContent, setHtmlContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchArticle();
    readingApi.startReading(parseInt(id)).catch(console.error);
  }, [id]);

  const fetchArticle = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [articleData, htmlData] = await Promise.all([
        articleApi.getArticle(parseInt(id)),
        articleApi.getArticleHtml(parseInt(id)),
      ]);
      setArticle(articleData);
      setHtmlContent(htmlData.html_content || '');
    } catch (err) {
      setError(err.message || '获取文章详情失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => new Date(dateString).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });

  if (isLoading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div>;
  if (error) return <div className="max-w-4xl mx-auto"><div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div><button onClick={() => navigate('/articles')} className="mt-4 px-4 py-2 text-blue-600 hover:underline">返回文章列表</button></div>;

  return (
    <div className="max-w-4xl mx-auto">
      <Link to="/articles" className="inline-flex items-center gap-2 text-blue-600 hover:underline mb-6"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>返回文章列表</Link>

      <Card className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-2"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-11 8-11 8-11z"/><circle cx="12" cy="12" r="3"/></svg><span>{article.view_count || 0} 次浏览</span></div>
          <div className="flex items-center gap-2"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><span>{formatDate(article.created_at)}</span></div>
        </div>
        {article.tags && article.tags.length > 0 && (
          <div className="flex items-center gap-2 mb-4">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><path d="M7 7h.01"/></svg>
            <div className="flex gap-2">{article.tags.map(tag => <span key={tag.id} className="px-3 py-1 rounded-full text-sm text-white" style={{ backgroundColor: tag.color }}>{tag.name}</span>)}</div>
          </div>
        )}
        {article.summary && <div className="border-t border-gray-200 pt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">摘要</h3><p className="text-gray-600">{article.summary}</p></div>}
        {article.keywords && <div className="border-t border-gray-200 pt-4 mt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">关键词</h3><p className="text-gray-600">{article.keywords}</p></div>}
        {article.source_url && <div className="border-t border-gray-200 pt-4 mt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">来源</h3><a href={article.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm break-all">{article.source_url}</a></div>}
      </Card>

      {htmlContent ? <Card><div className="prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: htmlContent }} /></Card> : <Card><div className="text-center py-12 text-gray-500">此文章没有可显示的内容</div></Card>}
    </div>
  );
};

export default ArticleDetail;
