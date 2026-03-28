import React, { createContext, useContext, useState, useEffect } from 'react';
import { articleApi } from '../api/article';
import { tagApi } from '../api/tag';

const ArticleContext = createContext(undefined);

export const useArticles = () => {
  const context = useContext(ArticleContext);
  if (!context) {
    throw new Error('useArticles must be used within an ArticleProvider');
  }
  return context;
};

export const ArticleProvider = ({ children }) => {
  const [articles, setArticles] = useState([]);
  const [tags, setTags] = useState([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const fetchArticles = async (params = {}) => {
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
    } catch (err) {
      setError(err.message || '获取文章列表失败');
    } finally {
      setIsLoading(false);
    }
  };

  const createArticle = async (data) => {
    setIsLoading(true);
    try {
      await articleApi.uploadArticle(data.file, data);
      await fetchArticles();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '创建文章失败' };
    } finally {
      setIsLoading(false);
    }
  };

  const importFromUrl = async (data) => {
    setIsLoading(true);
    try {
      await articleApi.importFromUrl(data);
      await fetchArticles();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '导入文章失败' };
    } finally {
      setIsLoading(false);
    }
  };

  const deleteArticle = async (id) => {
    try {
      await articleApi.deleteArticle(id);
      setArticles(articles.filter(a => a.id !== id));
      setTotal(prev => prev - 1);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '删除文章失败' };
    }
  };

  const value = {
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
