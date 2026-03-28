import React from 'react';
import Card from '../components/ui/Card';
import { useAuth } from '../contexts/AuthContext';
import { HomeIcon, FileTextIcon, TagIcon, BarChartIcon } from '../components/ui/Icons';

interface StatItem {
  title: string;
  value: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  color: string;
  path: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const stats: StatItem[] = [
    { title: '总文章数', value: '0', icon: FileTextIcon, color: 'bg-blue-500', path: '/articles' },
    { title: '标签数量', value: '0', icon: TagIcon, color: 'bg-green-500', path: '/tags' },
    { title: '阅读统计', value: '查看', icon: BarChartIcon, color: 'bg-purple-500', path: '/reading/stats' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          欢迎回来，{user?.username || '用户'}
        </h1>
        <p className="text-gray-600">
          这是您的知识管理仪表盘
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <a
              key={index}
              href={stat.path}
              className="card-animate bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer block"
            >
              <div className={`w-12 h-12 ${stat.color} rounded-lg mb-4 flex items-center justify-center`}>
                <Icon className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-1">{stat.title}</h3>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </a>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-100">
        <h2 className="font-semibold text-lg mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/articles/create"
            className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <FileTextIcon className="text-blue-500" size={20} />
            <span>创建新文章</span>
          </a>
          <a
            href="/tags"
            className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <TagIcon className="text-green-500" size={20} />
            <span>管理标签</span>
          </a>
        </div>
      </Card>

      {/* Info Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
        <h2 className="font-semibold text-lg mb-4">系统功能</h2>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            文章管理：上传文件或从 URL 导入
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            标签系统：组织和管理您的知识
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
            阅读统计：追踪您的阅读进度
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
            搜索功能：快速找到您需要的内容
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
