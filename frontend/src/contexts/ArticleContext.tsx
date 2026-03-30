import React, { createContext, useContext, useState, useEffect } from 'react';
import { articleApi } from '../api/article';
import { tagApi } from '../api/tag';
import type { Article, Tag, ArticleCreateData, UrlImportData } from '../types/api';

const getErrorMessage = (err: any, fallback: string): string => {
  if (err?.response?.data?.detail) return err.response.data.detail;
  if (err?.response?.data?.message) return err.response.data.message;
  return err?.message || fallback;
};

interface ArticleContextType {
  articles: Article[];
  tags: Tag[];
  total: number;
  currentPage: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  fetchArticles: (params?: any) => Promise<void>;
  createArticle: (data: { file: File; title?: string; summary?: string; keywords?: string; tagIds?: number[]; images?: File[] }) => Promise<{ success: boolean; error?: string }>;
  importFromUrl: (data: UrlImportData) => Promise<{ success: boolean; error?: string }>;
  deleteArticle: (id: number) => Promise<{ success: boolean; error?: string }>;
  setCurrentPage: (page: number) => void;
}

const ArticleContext = createContext<ArticleContextType | undefined>(undefined);

export const useArticles = (): ArticleContextType => {
  const context = useContext(ArticleContext);
  if (!context) {
    throw new Error('useArticles must be used within an ArticleProvider');
  }
  return context;
};

interface ArticleProviderProps {
  children: React.ReactNode;
}

export const ArticleProvider: React.FC<ArticleProviderProps> = ({ children }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await tagApi.getTags();
        setTags(data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
      }
    };
    fetchTags();
  }, []);

  const fetchArticles = async (params: any = {}) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await articleApi.getArticles({
        page: currentPage,
        size: pageSize,
        ...params,
      });
      setArticles(response.items);
      setTotal(response.total);
    } catch (err: any) {
      setError(getErrorMessage(err, '获取文章列表失败'));
    } finally {
      setIsLoading(false);
    }
  };

  const createArticle = async (data: { file: File; title?: string; summary?: string; keywords?: string; tagIds?: number[]; images?: File[] }): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      await articleApi.uploadArticle(data.file, data);
      await fetchArticles();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: getErrorMessage(err, '创建文章失败') };
    } finally {
      setIsLoading(false);
    }
  };

  const importFromUrl = async (data: UrlImportData): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      await articleApi.importFromUrl(data);
      await fetchArticles();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: getErrorMessage(err, '导入文章失败') };
    } finally {
      setIsLoading(false);
    }
  };

  const deleteArticle = async (id: number): Promise<{ success: boolean; error?: string }> => {
    try {
      await articleApi.deleteArticle(id);
      setArticles(articles.filter(a => a.id !== id));
      setTotal(prev => prev - 1);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: getErrorMessage(err, '删除文章失败') };
    }
  };

  const value: ArticleContextType = {
    articles,
    tags,
    total,
    currentPage,
    pageSize,
    isLoading,
    error,
    fetchArticles,
    createArticle,
    importFromUrl,
    deleteArticle,
    setCurrentPage,
  };

  return <ArticleContext.Provider value={value}>{children}</ArticleContext.Provider>;
};
