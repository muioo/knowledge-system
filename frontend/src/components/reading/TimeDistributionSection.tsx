import React, { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { readingApi } from '../../api/reading';
import type { TimeDistribution, TimePeriod } from '../../types/api';

interface TimeDistributionSectionProps {
  userId: number;
}

const COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#6b7280'];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const TimePeriodPieChart: React.FC<{ data: TimePeriod[] }> = ({ data }) => {
  const chartData = data.map(item => ({
    name: item.name,
    value: item.duration,
  }));

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-4">时段分布</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }: { name: string; percent: number }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`${value}分钟`, '阅读时长']}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend list */}
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div
            key={item.name}
            className="flex items-center justify-between text-sm"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-gray-600">{item.name}</span>
            </div>
            <span className="text-gray-900 font-medium">
              {item.duration}分钟 ({item.percentage}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const TimeDistributionSection: React.FC<TimeDistributionSectionProps> = ({
  userId,
}) => {
  const [data, setData] = useState<TimeDistribution | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
    // userId is passed as a prop but the current API does not accept it;
    // listed here to suppress exhaustive-deps warnings.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await readingApi.getTimeDistribution();
      setData(response);
    } catch (error) {
      console.error('Failed to fetch time distribution:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        阅读时段分布
      </h2>
      <div className="max-w-md mx-auto">
        <TimePeriodPieChart data={data.periods} />
      </div>
    </div>
  );
};

export default TimeDistributionSection;
