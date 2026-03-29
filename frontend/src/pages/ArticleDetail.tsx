import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { articleApi } from '../api/article';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';
import { ArrowRightIcon, EyeIcon as CustomEyeIcon, TagIcon } from '../components/ui/Icons';
import type { Article } from '../types/api';

// 创建简单的图标组件，避免SVG解析问题
const EyeIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const CalendarIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

const ArticleDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<Article | null>(null);
  const [htmlContent, setHtmlContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [showProgress, setShowProgress] = useState(false);

  // 使用 ref 追踪当前文章ID，防止 StrictMode 重复调用
  const currentArticleIdRef = useRef<number | null>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchArticle();

    // 只在文章ID变化时调用 startReading，防止 StrictMode 重复调用
    if (id) {
      const articleId = parseInt(id);
      if (currentArticleIdRef.current !== articleId) {
        currentArticleIdRef.current = articleId;
        readingApi.startReading(articleId).catch(console.error);
        setReadingProgress(0);
      }
    }
  }, [id]);

  // 监听滚动事件，更新阅读进度
  useEffect(() => {
    if (!contentRef.current || !htmlContent) return;

    const handleScroll = () => {
      // 清除之前的定时器
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      // 防抖：停止滚动500ms后才发送请求
      scrollTimeoutRef.current = setTimeout(async () => {
        if (!contentRef.current || !id) return;

        const scrollPosition = window.scrollY;
        const totalContentLength = document.documentElement.scrollHeight - window.innerHeight;
        const actualProgress = Math.min(100, Math.round((scrollPosition / totalContentLength) * 100));

        // 只在有实际滚动时才更新
        if (actualProgress > 0) {
          setReadingProgress(actualProgress);
          setShowProgress(true);

          try {
            await readingApi.updateProgress(parseInt(id), {
              scroll_position: Math.round(scrollPosition),
              total_content_length: Math.round(totalContentLength),
              actual_progress: actualProgress
            });
          } catch (error) {
            console.error('Failed to update reading progress:', error);
          }
        }
      }, 500);
    };

    // 添加滚动监听，使用 passive 提升性能
    window.addEventListener('scroll', handleScroll, { passive: true });

    // 页面离开时保存最终进度
    const handleBeforeUnload = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      // 立即保存进度
      const scrollPosition = window.scrollY;
      const totalContentLength = document.documentElement.scrollHeight - window.innerHeight;
      const actualProgress = Math.min(100, Math.round((scrollPosition / totalContentLength) * 100));

      if (actualProgress > 0) {
        navigator.sendBeacon('/api/v1/reading/articles/' + id + '/progress', JSON.stringify({
          scroll_position: Math.round(scrollPosition),
          total_content_length: Math.round(totalContentLength),
          actual_progress: actualProgress
        }));
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [id, htmlContent]);

  const fetchArticle = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const [articleData, htmlData] = await Promise.all([
        articleApi.getArticle(parseInt(id)),
        articleApi.getArticleHtml(parseInt(id)),
      ]);
      setArticle(articleData);
      // 替换图片路径为完整的后端URL，避免代理问题
      let htmlContent = htmlData.html_content || '';
      htmlContent = htmlContent.replace(/src="\/api\/v1\/media\//g, 'src="http://localhost:8022/api/v1/media/');
      setHtmlContent(htmlContent);
    } catch (err: any) {
      setError(err.message || '获取文章详情失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string): string => new Date(dateString).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });

  if (isLoading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div>;
  if (error) return <div className="max-w-4xl mx-auto"><div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div><button onClick={() => navigate('/articles')} className="mt-4 px-4 py-2 text-blue-600 hover:underline">返回文章列表</button></div>;
  if (!article) return <div className="max-w-4xl mx-auto"><div className="bg-red-50 text-red-600 p-4 rounded-lg">文章不存在</div></div>;

  return (
    <div className="max-w-4xl mx-auto relative">
      {/* 阅读进度浮标 */}
      {showProgress && readingProgress > 0 && (
        <div className="fixed bottom-6 right-6 z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-4 min-w-[200px]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">阅读进度</span>
            <span className="text-sm font-bold text-blue-600">{readingProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 rounded-full h-2 transition-all duration-300"
              style={{ width: `${readingProgress}%` }}
            />
          </div>
        </div>
      )}

      <Link to="/articles" className="inline-flex items-center gap-2 text-blue-600 hover:underline mb-6">
        <ArrowRightIcon size={16} className="rotate-180" />
        返回文章列表
      </Link>

      <Card className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-2">
            <EyeIcon size={16} />
            <span>{article.view_count || 0} 次浏览</span>
          </div>
          <div className="flex items-center gap-2">
            <CalendarIcon size={16} />
            <span>{formatDate(article.created_at)}</span>
          </div>
        </div>
        {article.tags && article.tags.length > 0 && (
          <div className="flex items-center gap-2 mb-4">
            <TagIcon size={16} />
            <div className="flex gap-2">{article.tags.map(tag => <span key={tag.id} className="px-3 py-1 rounded-full text-sm text-white" style={{ backgroundColor: tag.color }}>{tag.name}</span>)}</div>
          </div>
        )}
        {article.summary && <div className="border-t border-gray-200 pt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">摘要</h3><p className="text-gray-600">{article.summary}</p></div>}
        {article.keywords && <div className="border-t border-gray-200 pt-4 mt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">关键词</h3><p className="text-gray-600">{article.keywords}</p></div>}
        {article.source_url && <div className="border-t border-gray-200 pt-4 mt-4"><h3 className="text-sm font-medium text-gray-700 mb-2">来源</h3><a href={article.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm break-all">{article.source_url}</a></div>}
      </Card>

      {htmlContent ? (
        <Card>
          <div ref={contentRef} className="prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: htmlContent }} />
        </Card>
      ) : (
        <Card>
          <div className="text-center py-12 text-gray-500">此文章没有可显示的内容</div>
        </Card>
      )}
    </div>
  );
};

export default ArticleDetail;
