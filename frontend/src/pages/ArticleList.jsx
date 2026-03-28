import React, { useEffect, useState } from 'react';
import { useArticles } from '../contexts/ArticleContext';
import ArticleCard from '../components/ArticleCard';
import Input from '../components/ui/Input';

const ArticleList = () => {
  const {
    articles,
    tags,
    total,
    currentPage,
    pageSize,
    isLoading,
    error,
    fetchArticles,
    deleteArticle,
    setCurrentPage,
  } = useArticles();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState(null);

  useEffect(() => {
    fetchArticles();
  }, [currentPage]);

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchArticles({
      ...(searchQuery && { q: searchQuery }),
      ...(selectedTag && { tag_id: selectedTag }),
    });
  };

  const handleTagFilter = (tagId) => {
    setSelectedTag(tagId === selectedTag ? null : tagId);
    setCurrentPage(1);
    fetchArticles({
      q: searchQuery,
      ...(tagId !== selectedTag && { tag_id: tagId }),
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这篇文章吗？')) {
      const result = await deleteArticle(id);
      if (!result.success) {
        alert(result.error);
      }
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">文章管理</h1>
        <p className="text-gray-600">管理和查看您的文章</p>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100 mb-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索文章..."
            className="flex-1"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            搜索
          </button>
        </form>

        {tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-gray-600 mr-2">标签筛选:</span>
            {tags.map(tag => (
              <button
                key={tag.id}
                onClick={() => handleTagFilter(tag.id)}
                className={`
                  px-3 py-1 rounded-full text-sm transition-colors
                  ${selectedTag === tag.id ? 'text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
                `}
                style={selectedTag === tag.id ? { backgroundColor: tag.color } : {}}
              >
                {tag.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Articles List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无文章，<a href="/articles/create" className="text-blue-600 hover:underline">创建第一篇文章</a>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {articles.map(article => (
              <ArticleCard key={article.id} article={article} onDelete={handleDelete} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <span className="text-sm text-gray-600">
                第 {currentPage} / {totalPages} 页，共 {total} 篇
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ArticleList;
