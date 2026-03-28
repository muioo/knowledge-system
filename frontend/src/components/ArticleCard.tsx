import React from 'react';
import { Link } from 'react-router-dom';
import Card from './ui/Card';
import { FileTextIcon, EyeIcon } from './ui/Icons';
import type { Article } from '../types/api';

interface ArticleCardProps {
  article: Article;
  onDelete: (id: number) => void;
}

const ArticleCard: React.FC<ArticleCardProps> = ({ article, onDelete }) => {
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <Link
            to={`/articles/${article.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors"
          >
            {article.title}
          </Link>
        </div>
        <button
          onClick={() => onDelete(article.id)}
          className="text-gray-400 hover:text-red-500 transition-colors ml-2"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      </div>

      {article.summary && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{article.summary}</p>
      )}

      {article.keywords && (
        <p className="text-xs text-gray-500 mb-3">关键词: {article.keywords}</p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <EyeIcon size={14} />
            {article.view_count || 0}
          </span>
          <span>{formatDate(article.created_at)}</span>
        </div>

        {article.tags && article.tags.length > 0 && (
          <div className="flex gap-1">
            {article.tags.map(tag => (
              <span
                key={tag.id}
                className="px-2 py-0.5 rounded text-xs text-white"
                style={{ backgroundColor: tag.color }}
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default ArticleCard;
