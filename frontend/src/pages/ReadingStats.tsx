import React, { useState, useEffect } from 'react';
import { readingApi } from '../api/reading';
import OverviewCards from '../components/reading/OverviewCards';
import ReadingHistoryList from '../components/reading/ReadingHistoryList';
import { useAuth } from '../contexts/AuthContext';

const ReadingStats: React.FC = () => {
  const { user } = useAuth();
  const [totalDuration, setTotalDuration] = useState(0);
  const [totalArticles, setTotalArticles] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [weeklyDuration, setWeeklyDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const fetchOverviewData = async () => {
    setIsLoading(true);
    try {
      // 获取阅读历史记录总数和总时长
      let historyItems: any[] = [];
      let historyPage = 1;
      const historyPageSize = 100;

      while (true) {
        const historyData = await readingApi.getHistory(historyPage, historyPageSize);
        historyItems = historyItems.concat(historyData.items);
        if (historyItems.length >= historyData.total) break;
        historyPage++;
      }

      // 计算总时长（从历史记录）
      const totalDur = historyItems.reduce((sum, item) => sum + (item.reading_duration || 0), 0);
      const totalRecs = historyItems.length;

      // 获取阅读统计（用于获取阅读过的文章数）
      let statsItems: any[] = [];
      let statsPage = 1;

      while (true) {
        const statsData = await readingApi.getStats(statsPage, historyPageSize);
        statsItems = statsItems.concat(statsData.items);
        if (statsItems.length >= statsData.total) break;
        statsPage++;
      }

      const totalArts = statsItems.length;

      // 计算本周阅读时长
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      const weeklyDur = historyItems
        .filter(item => item.started_at && new Date(item.started_at) >= weekAgo)
        .reduce((sum, item) => sum + (item.reading_duration || 0), 0);

      setTotalDuration(totalDur);
      setTotalArticles(totalArts);
      setTotalRecords(totalRecs);
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
        totalRecords={totalRecords}
        weeklyDuration={weeklyDuration}
      />

      {/* 阅读历史记录列表 */}
      {user && <ReadingHistoryList userId={user.id} />}
    </div>
  );
};

export default ReadingStats;
