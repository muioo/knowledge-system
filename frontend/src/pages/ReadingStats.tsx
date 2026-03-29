import React, { useState, useEffect } from 'react';
import { readingApi } from '../api/reading';
import OverviewCards from '../components/reading/OverviewCards';
import ReadingTrendsChart from '../components/reading/ReadingTrendsChart';
import TimeDistributionSection from '../components/reading/TimeDistributionSection';
import ArticleProgressList from '../components/reading/ArticleProgressList';
import { useAuth } from '../contexts/AuthContext';

const ReadingStats: React.FC = () => {
  const { user } = useAuth();
  const [totalDuration, setTotalDuration] = useState(0);
  const [totalArticles, setTotalArticles] = useState(0);
  const [weeklyDuration, setWeeklyDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const fetchOverviewData = async () => {
    setIsLoading(true);
    try {
      // 获取阅读进度统计
      const progressData = await readingApi.getProgress(1, 1000);

      // 计算总时长和文章数
      const totalDur = progressData.items.reduce((sum, item) => sum + item.total_duration, 0);
      const totalArts = progressData.items.length;

      // 获取本周阅读时长（通过阅读统计计算）
      const statsData = await readingApi.getStats(1, 1000);
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      const weeklyDur = statsData.items
        .filter(item => item.last_read_at && new Date(item.last_read_at) >= weekAgo)
        .reduce((sum, item) => sum + item.total_duration, 0);

      setTotalDuration(totalDur);
      setTotalArticles(totalArts);
      setWeeklyDuration(weeklyDur);
    } catch (error) {
      console.error('Failed to fetch overview data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
          <p className="text-gray-600">查看您的阅读历史和统计数据</p>
        </div>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
        <p className="text-gray-600">查看您的阅读历史和统计数据</p>
      </div>

      {/* 概览卡片 */}
      <OverviewCards
        totalDuration={totalDuration}
        totalArticles={totalArticles}
        weeklyDuration={weeklyDuration}
      />

      {/* 阅读趋势图表 */}
      {user && <ReadingTrendsChart userId={user.id} />}

      {/* 阅读时段分布 */}
      {user && <TimeDistributionSection userId={user.id} />}

      {/* 文章阅读进度 */}
      {user && <ArticleProgressList userId={user.id} />}
    </div>
  );
};

export default ReadingStats;
