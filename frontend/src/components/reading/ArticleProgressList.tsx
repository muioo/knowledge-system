import React, { useState, useEffect } from 'react';
import { readingApi } from '../../api/reading';
import type { ReadingProgress } from '../../types/api';
import { useNavigate } from 'react-router-dom';

interface ArticleProgressListProps {
  userId: number;
}

const ArticleProgressList: React.FC<ArticleProgressListProps> = ({ userId }) => {
  const [progress, setProgress] = useState<ReadingProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [userId]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getProgress(1, 50);
      setProgress(response.items);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}小时${minutes}分钟`;
    return `${minutes}分钟`;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '从未';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProgressColor = (prog: number): string => {
    if (prog >= 100) return 'bg-green-500';
    if (prog >= 50) return 'bg-blue-500';
    return 'bg-gray-400';
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  if (progress.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="text-center py-12 text-gray-500">暂无阅读记录</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">文章阅读进度</h2>
      <div className="space-y-4">
        {progress.map((item) => (
          <div
            key={item.article_id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
            onClick={() => navigate(`/articles/${item.article_id}`)}
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-medium text-gray-900 flex-1 pr-4 leading-snug">{item.article_title}</h3>
              <span className="text-xs text-gray-400 whitespace-nowrap">{formatDate(item.last_read_at)}</span>
            </div>

            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-500">阅读进度</span>
                <span className={`font-semibold ${item.reading_progress >= 100 ? 'text-green-600' : 'text-gray-900'}`}>
                  {item.reading_progress >= 100 ? '已读完' : `${item.reading_progress}%`}
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(item.reading_progress)}`}
                  style={{ width: `${Math.min(item.reading_progress, 100)}%` }}
                />
              </div>
            </div>

            <div className="flex items-center gap-6 text-sm text-gray-500">
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>阅读 {item.total_views} 次</span>
              </div>
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>累计 {formatDuration(item.total_duration)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArticleProgressList;
