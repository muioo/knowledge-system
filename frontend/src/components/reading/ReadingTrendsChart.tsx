import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { readingApi } from '../../api/reading';
import type { ReadingTrend } from '../../types/api';

interface ReadingTrendsChartProps {
  userId: number;
}

const ReadingTrendsChart: React.FC<ReadingTrendsChartProps> = ({ userId }) => {
  const [days, setDays] = useState(7);
  const [data, setData] = useState<ReadingTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getTrends(days);
      setData(response.items);
    } catch (error) {
      console.error('Failed to fetch trends:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">阅读趋势</h2>
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                days === d
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {d}天
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })}
          />
          <YAxis yAxisId="left" orientation="left" stroke="#3b82f6" />
          <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
          <Tooltip
            labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
            formatter={(value: number, name: string) => [
              value,
              name === 'minutes' ? '分钟' : '篇'
            ]}
          />
          <Legend />
          <Bar yAxisId="left" dataKey="minutes" fill="#3b82f6" name="阅读时长(分钟)" />
          <Bar yAxisId="right" dataKey="articles" fill="#10b981" name="阅读文章数" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ReadingTrendsChart;
