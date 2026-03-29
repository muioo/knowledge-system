import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { articleApi } from '../api/article';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';
import { EyeIcon as CustomEyeIcon, TagIcon, ListIcon, ChevronDownIcon } from '../components/ui/Icons';
import { useBreadcrumb } from '../contexts/BreadcrumbContext';
import type { Article } from '../types/api';

// 创建简单的图标组件，避免SVG解析问题
const EyeIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7-10 7z" />
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

// 目录项接口
interface TocItem {
  id: string;
  title: string;
  level: number;
}

const ArticleDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumb();
  const [article, setArticle] = useState<Article | null>(null);
  const [htmlContent, setHtmlContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [showProgress, setShowProgress] = useState(false);
  const [tocItems, setTocItems] = useState<TocItem[]>([]);
  const [activeTocId, setActiveTocId] = useState<string>('');
  const [isTocCollapsed, setIsTocCollapsed] = useState(false);

  // 使用 ref 追踪当前文章ID，防止 StrictMode 重复调用
  const currentArticleIdRef = useRef<number | null>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const tocObserverRef = useRef<IntersectionObserver | null>(null);
  const readingStartTimeRef = useRef<number>(Date.now());
  const durationUpdateIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchArticle();

    // 只在文章ID变化时调用 startReading，防止 StrictMode 重复调用
    if (id) {
      const articleId = parseInt(id);
      if (currentArticleIdRef.current !== articleId) {
        currentArticleIdRef.current = articleId;
        readingApi.startReading(articleId).catch(console.error);
        setReadingProgress(0);
        readingStartTimeRef.current = Date.now();

        // 每30秒更新一次阅读时长
        durationUpdateIntervalRef.current = setInterval(async () => {
          const currentDuration = Math.floor((Date.now() - readingStartTimeRef.current) / 1000);

          try {
            await readingApi.updateProgress(articleId, {
              scroll_position: 0,
              total_content_length: 0,
              actual_progress: 0,
              reading_duration: currentDuration
            });
          } catch (error) {
            console.error('Failed to update reading duration:', error);
          }
        }, 30000); // 30秒更新一次
      }
    }

    // 清理定时器
    return () => {
      if (durationUpdateIntervalRef.current) {
        clearInterval(durationUpdateIntervalRef.current);
      }
    };
  }, [id]);

  // 设置自定义面包屑，显示文章标题
  useEffect(() => {
    if (article) {
      setBreadcrumbs([
        { label: '首页', path: '/dashboard' },
        { label: '文章管理', path: '/articles' },
        { label: article.title, path: undefined },
      ]);
    }
    return () => {
      setBreadcrumbs([]);
    };
  }, [article, setBreadcrumbs]);

  // 提取目录
  useEffect(() => {
    if (!htmlContent || !contentRef.current) return;

    // 解析HTML内容，提取标题
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');

    if (headings.length === 0) {
      setTocItems([]);
      return;
    }

    const toc: TocItem[] = [];
    headings.forEach((heading, index) => {
      const level = parseInt(heading.tagName[1]);
      const title = heading.textContent || `标题 ${index + 1}`;
      const id = `heading-${index}`;

      toc.push({ id, title, level });

      // 在实际渲染的内容中添加ID
      heading.id = id;
    });

    setTocItems(toc);

    // 更新HTML内容，添加ID到标题
    const updatedHtml = doc.body.innerHTML;
    setHtmlContent(updatedHtml);

    // 设置滚动监听来高亮当前目录项
    setupTocObserver();
  }, [htmlContent]);

  const setupTocObserver = () => {
    if (tocObserverRef.current) {
      tocObserverRef.current.disconnect();
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveTocId(entry.target.id);
          }
        });
      },
      {
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
      }
    );

    // 观察所有标题元素
    const headings = contentRef.current?.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings?.forEach((heading) => observer.observe(heading));

    tocObserverRef.current = observer;
  };

  // 监听滚动事件，更新阅读进度
  useEffect(() => {
    if (!contentRef.current || !htmlContent) return;

    const handleScroll = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      scrollTimeoutRef.current = setTimeout(async () => {
        if (!contentRef.current || !id) return;

        const scrollPosition = window.scrollY;
        const totalContentLength = document.documentElement.scrollHeight - window.innerHeight;
        const actualProgress = Math.min(100, Math.round((scrollPosition / totalContentLength) * 100));

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

    window.addEventListener('scroll', handleScroll, { passive: true });

    const handleBeforeUnload = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      if (durationUpdateIntervalRef.current) {
        clearInterval(durationUpdateIntervalRef.current);
      }

      // 计算总阅读时长
      const totalDuration = Math.floor((Date.now() - readingStartTimeRef.current) / 1000);

      const scrollPosition = window.scrollY;
      const totalContentLength = document.documentElement.scrollHeight - window.innerHeight;
      const actualProgress = Math.min(100, Math.round((scrollPosition / totalContentLength) * 100));

      if (totalDuration > 0 || actualProgress > 0) {
        navigator.sendBeacon('/api/v1/reading/articles/' + id + '/progress', JSON.stringify({
          scroll_position: Math.round(scrollPosition),
          total_content_length: Math.round(totalContentLength),
          actual_progress: actualProgress,
          reading_duration: totalDuration
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
      if (tocObserverRef.current) {
        tocObserverRef.current.disconnect();
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

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      const offset = 80; // 顶部偏移量
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  if (isLoading) return <div className="flex items-center justify-center min-h-[50vh]"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div>;
  if (error) return <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>;
  if (!article) return <div className="bg-red-50 text-red-600 p-4 rounded-lg">文章不存在</div>;

  return (
    <div className="w-full relative">
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

      <div className="flex gap-6">
        {/* 主内容区域 */}
        <div className="flex-1 min-w-0 space-y-6">
          <Card>
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

        {/* 右侧目录 */}
        {tocItems.length > 0 && (
          <div className="hidden lg:block w-72 flex-shrink-0">
            <div className="sticky top-6 space-y-6">
              {/* 目录卡片 */}
              <Card className="p-4">
                <button
                  onClick={() => setIsTocCollapsed(!isTocCollapsed)}
                  className="flex items-center justify-between w-full mb-3 text-left"
                >
                  <div className="flex items-center gap-2 font-semibold text-gray-900">
                    <ListIcon size={16} />
                    <span>目录</span>
                  </div>
                  <ChevronDownIcon
                    size={16}
                    className={`transition-transform duration-200 ${isTocCollapsed ? '-rotate-90' : ''}`}
                  />
                </button>

                {!isTocCollapsed && (
                  <nav className="space-y-1">
                    {tocItems.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => scrollToHeading(item.id)}
                        className={`block w-full text-left px-2 py-1.5 rounded-lg text-sm transition-colors ${
                          activeTocId === item.id
                            ? 'bg-blue-50 text-blue-600 font-medium'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                        style={{ paddingLeft: `${0.5 + item.level * 0.75}rem` }}
                      >
                        {item.title}
                      </button>
                    ))}
                  </nav>
                )}
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArticleDetail;
