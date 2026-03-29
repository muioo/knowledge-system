import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { HomeIcon, ChevronRightIcon } from '../ui/Icons';
import { useBreadcrumb as useCustomBreadcrumb } from '../../contexts/BreadcrumbContext';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

/**
 * Breadcrumb 组件 - 面包屑导航
 * 自动根据当前路由生成面包屑，支持自定义覆盖
 */
export const Breadcrumb: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [autoBreadcrumbs, setAutoBreadcrumbs] = useState<BreadcrumbItem[]>([]);
  const { breadcrumbs: customBreadcrumbs } = useCustomBreadcrumb();

  // 路由到中文标签的映射
  const routeLabels: Record<string, string> = {
    dashboard: '仪表盘',
    articles: '文章管理',
    create: '添加文章',
    tags: '标签管理',
    reading: '阅读',
    stats: '阅读统计',
  };

  useEffect(() => {
    const pathnames = location.pathname.split('/').filter((x) => x);

    const items: BreadcrumbItem[] = [];

    // 添加首页
    items.push({ label: '首页', path: '/dashboard' });

    // 构建面包屑路径
    let currentPath = '';
    pathnames.forEach((path) => {
      currentPath += `/${path}`;

      // 处理动态路由（如文章ID）
      if (/^\d+$/.test(path)) {
        // 获取上一级的标签
        const prevLabel = items[items.length - 1]?.label || '详情';
        items.push({ label: `${prevLabel}详情`, path: currentPath });
      } else {
        // 使用映射或原始路径
        const label = routeLabels[path] || path;
        items.push({ label, path: currentPath });
      }
    });

    setAutoBreadcrumbs(items);
  }, [location.pathname]);

  // 使用自定义面包屑（如果有），否则使用自动生成的
  const displayBreadcrumbs = customBreadcrumbs.length > 0 ? customBreadcrumbs : autoBreadcrumbs;

  const handleNavigate = (item: BreadcrumbItem, index: number) => {
    // 如果是最后一项或没有路径，不跳转
    if (index === displayBreadcrumbs.length - 1 || !item.path) return;
    navigate(item.path);
  };

  if (displayBreadcrumbs.length <= 1) return null;

  return (
    <nav className="mb-6" aria-label="面包屑导航">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 px-4 py-3">
        <ol className="flex items-center flex-wrap gap-1 text-sm">
          {displayBreadcrumbs.map((item, index) => (
            <li key={`${item.path}-${index}`} className="flex items-center">
              {index > 0 && (
                <ChevronRightIcon size={14} className="mx-1 text-gray-300" />
              )}
              <button
                onClick={() => handleNavigate(item, index)}
                className={`flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all duration-200 ${
                  index === displayBreadcrumbs.length - 1
                    ? 'text-blue-600 font-medium bg-blue-50 cursor-default'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                }`}
                disabled={index === displayBreadcrumbs.length - 1}
              >
                {index === 0 && <HomeIcon size={14} />}
                <span className="max-w-[200px] truncate">{item.label}</span>
              </button>
            </li>
          ))}
        </ol>
      </div>
    </nav>
  );
};
