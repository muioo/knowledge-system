import React from 'react';

interface OverviewCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  color: string;
}

const OverviewCard: React.FC<OverviewCardProps> = ({ icon, title, value, unit, change, color }) => {
  const gradientColors: Record<string, string> = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg bg-gradient-to-br ${gradientColors[color] || gradientColors.blue}`}>
          {icon}
        </div>
        {change !== undefined && (
          <span className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900 tabular-nums">
          {value}
          {unit && <span className="text-sm font-normal text-gray-600 ml-1">{unit}</span>}
        </p>
      </div>
    </div>
  );
};

interface OverviewCardsProps {
  totalDuration: number;
  totalArticles: number;
  weeklyDuration: number;
}

const OverviewCards: React.FC<OverviewCardsProps> = ({
  totalDuration,
  totalArticles,
  weeklyDuration
}) => {
  const formatHours = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    return hours.toString();
  };

  const formatMinutes = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    return minutes.toString();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
        title="总阅读时长"
        value={formatHours(totalDuration)}
        unit="小时"
        color="blue"
      />
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
        title="已读文章数"
        value={totalArticles}
        unit="篇"
        color="purple"
      />
      <OverviewCard
        icon={<svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" /></svg>}
        title="本周阅读"
        value={formatMinutes(weeklyDuration)}
        unit="分钟"
        color="orange"
      />
    </div>
  );
};

export default OverviewCards;
