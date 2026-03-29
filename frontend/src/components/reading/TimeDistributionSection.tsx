import React, { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { readingApi } from '../../api/reading';
import type { TimeDistribution, TimePeriod, HeatmapData } from '../../types/api';

interface TimeDistributionSectionProps {
  userId: number;
}

const COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#6b7280'];

const WEEK_LABELS = ['一', '二', '三', '四', '五', '六', '日'];

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

interface HeatmapProps {
  heatmap: HeatmapData[];
}

const ReadingHeatmap: React.FC<HeatmapProps> = ({ heatmap }) => (
  <div>
    <h3 className="text-sm font-medium text-gray-700 mb-4">阅读热力图</h3>
    <p className="text-sm text-gray-500 mb-3">一周内各时段的阅读活跃度</p>
    <div className="overflow-x-auto">
      <div style={{ minWidth: '200px' }}>
        {/* Day-of-week header */}
        <div className="grid grid-cols-7 gap-1 mb-1">
          {WEEK_LABELS.map(day => (
            <div key={day} className="text-center text-xs text-gray-500">
              {day}
            </div>
          ))}
        </div>

        {/* 24 hour rows × 7 day columns */}
        {Array.from({ length: 24 }).map((_, hour) => (
          <div key={hour} className="grid grid-cols-7 gap-1 mb-1">
            {Array.from({ length: 7 }).map((_, day) => {
              const cell = heatmap.find(h => h.hour === hour && h.day === day);
              const count = cell?.count ?? 0;
              const intensity = count > 0 ? Math.min(count * 20, 100) : 0;

              return (
                <div
                  key={`${hour}-${day}`}
                  className="aspect-square rounded-sm"
                  style={{
                    backgroundColor:
                      intensity > 0
                        ? `rgba(59, 130, 246, ${intensity / 100})`
                        : '#f3f4f6',
                  }}
                  title={`周${WEEK_LABELS[day]} ${hour}:00 - ${count}次`}
                />
              );
            })}
          </div>
        ))}
      </div>
    </div>

    {/* Intensity legend */}
    <div className="flex items-center justify-end gap-2 mt-3 text-xs text-gray-500">
      <span>低</span>
      <div className="flex gap-1">
        {[0.1, 0.3, 0.5, 0.7, 1.0].map(opacity => (
          <div
            key={opacity}
            className="w-3 h-3 rounded-sm"
            style={{ backgroundColor: `rgba(59, 130, 246, ${opacity})` }}
          />
        ))}
      </div>
      <span>高</span>
    </div>
  </div>
);

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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <TimePeriodPieChart data={data.periods} />
        <ReadingHeatmap heatmap={data.heatmap} />
      </div>
    </div>
  );
};

export default TimeDistributionSection;
