import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  FileTextIcon,
  TagIcon,
  BarChartIcon,
  UserIcon,
  ChevronDownIcon,
  PlusIcon,
} from '../ui/Icons';

/**
 * Sidebar 组件 - 侧边栏导航
 * 完全还原 home.html 的样式
 */
interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

interface MenuItem {
  path: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // 折叠状态
  const [extraOptionsOpen, setExtraOptionsOpen] = useState(false);
  const [moreInfoOpen, setMoreInfoOpen] = useState(false);

  const menuItems = useMemo<MenuItem[]>(
    () => [
      { path: '/dashboard', icon: HomeIcon, label: '仪表盘' },
      { path: '/articles', icon: FileTextIcon, label: '文章管理' },
      { path: '/articles/create', icon: PlusIcon, label: '添加文章' },
      { path: '/tags', icon: TagIcon, label: '标签管理' },
      { path: '/reading/stats', icon: BarChartIcon, label: '阅读统计' },
    ],
    []
  );

  const handleNavigate = (path: string) => {
    navigate(path);
    // Mobile 关闭侧边栏
    if (window.innerWidth < 768 && onClose) {
      onClose();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 响应式：mobile 时是抽屉，desktop 时是固定侧边栏
  const isMobile = window.innerWidth < 768;
  const sidebarClasses = `
    ${isMobile ? 'fixed inset-0 z-[9999]' : 'hidden md:flex flex-col fixed top-0 left-0'}
    bg-white text-black
    ${isMobile && !isOpen ? 'transform -translate-x-full' : 'transform translate-x-0'}
    transition-transform duration-300 ease-in-out
    ${isMobile ? 'w-full' : 'w-64'}
    h-full shadow-lg
  `;

  return (
    <>
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-[9998] md:hidden"
          onClick={onClose}
        />
      )}
      <div className={sidebarClasses}>
        {/* Profile Section */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <UserIcon size={24} className="text-white" />
            </div>
            <div>
              <p className="font-semibold">{user?.username || '用户'}</p>
              <p className="text-sm text-gray-500">{user?.email || 'user@example.com'}</p>
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul>
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path} className="mb-2">
                  <button
                    onClick={() => handleNavigate(item.path)}
                    className="flex gap-2 font-medium text-sm items-center w-full py-2 px-4 rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    <Icon size={20} />
                    {item.label}
                  </button>
                </li>
              );
            })}
          </ul>

          {/* Collapsible Sections */}
          <div className="mt-4">
            {/* Extra Options */}
            <div className="mb-4">
              <button
                onClick={() => setExtraOptionsOpen(!extraOptionsOpen)}
                className="w-full flex items-center justify-between py-2 px-4 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <span className="font-semibold text-sm">Extra Options</span>
                <ChevronDownIcon
                  size={16}
                  className={`transform transition-transform duration-200 ${extraOptionsOpen ? 'rotate-180' : ''}`}
                />
              </button>
              {extraOptionsOpen && (
                <div className="ml-4 mt-2 space-y-2">
                  <p className="text-sm text-gray-600 py-1 px-2">选项 1</p>
                  <p className="text-sm text-gray-600 py-1 px-2">选项 2</p>
                </div>
              )}
            </div>

            {/* More Info */}
            <div className="mb-4">
              <button
                onClick={() => setMoreInfoOpen(!moreInfoOpen)}
                className="w-full flex items-center justify-between py-2 px-4 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <span className="font-semibold text-sm">More Info</span>
                <ChevronDownIcon
                  size={16}
                  className={`transform transition-transform duration-200 ${moreInfoOpen ? 'rotate-180' : ''}`}
                />
              </button>
              {moreInfoOpen && (
                <div className="ml-4 mt-2 space-y-2">
                  <p className="text-sm text-gray-600 py-1 px-2">信息 1</p>
                  <p className="text-sm text-gray-600 py-1 px-2">信息 2</p>
                </div>
              )}
            </div>
          </div>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full font-medium text-sm p-3 text-center bg-blue-100 rounded-xl hover:bg-blue-200 transition-colors"
          >
            退出登录
          </button>
        </div>
      </div>
    </>
  );
};
