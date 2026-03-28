import React, { useState, useEffect } from 'react';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';

const ReadingStats = () => {
  const [stats, setStats] = useState([]);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('stats');

  useEffect(() => { fetchData(); }, [activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (activeTab === 'stats') {
        const data = await readingApi.getStats();
        setStats(data.items || []);
      } else {
        const data = await readingApi.getHistory();
        setHistory(data.items || []);
      }
    } catch (err) {
      setError(err.message || '获取数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`;
  };

  const formatDate = (dateString) => new Date(dateString).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
        <p className="text-gray-600">查看您的阅读历史和统计数据</p>
      </div>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setActiveTab('stats')} className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'stats' ? 'bg-blue-500 text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>文章统计</button>
        <button onClick={() => setActiveTab('history')} className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'history' ? 'bg-blue-500 text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>阅读历史</button>
      </div>

      {error && <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">{error}</div>}

      {isLoading ? <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div> : activeTab === 'stats' ? (
        stats.length === 0 ? <div className="text-center py-12 text-gray-500">暂无阅读统计数据</div> : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stats.map(stat => (
              <Card key={stat.article_id}>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="text-purple-500" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{stat.article_title}</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <div className="flex items-center gap-2"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-11 11-8 11 8-11 8-11z"/><circle cx="12" cy="12" r="3"/></svg><span>阅读 {stat.total_views} 次</span></div>
                      <div className="flex items-center gap-2"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg><span>累计 {formatDuration(stat.total_duration)}</span></div>
                      {stat.last_read_at && <div className="text-xs text-gray-500">最后阅读: {formatDate(stat.last_read_at)}</div>}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )
      ) : (
        history.length === 0 ? <div className="text-center py-12 text-gray-500">暂无阅读历史记录</div> : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">文章</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">开始时间</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时长</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">进度</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.map(record => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4"><a href={`/articles/${record.article_id}`} className="text-blue-600 hover:underline">{record.article_title}</a></td>
                    <td className="px-6 py-4 text-sm text-gray-600">{formatDate(record.started_at)}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{record.reading_duration > 0 ? formatDuration(record.reading_duration) : '-'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 w-24"><div className="bg-blue-500 h-2 rounded-full" style={{ width: `${record.reading_progress}%` }} /></div>
                        <span className="text-sm text-gray-600">{record.reading_progress}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
};

export default ReadingStats;
