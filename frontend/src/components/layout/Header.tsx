import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { MenuIcon } from '../ui/Icons';

/**
 * Header 组件 - 移动端顶部栏
 */
interface HeaderProps {
  onMenuToggle: () => void;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle, title = '仪表盘' }) => {
  const { user } = useAuth();

  return (
    <div className="p-4 bg-white border-b border-gray-200 md:hidden flex justify-between items-center shadow-sm">
      <div>
        <h1 className="text-xl font-bold text-gray-900">{title}</h1>
        <p className="text-sm text-gray-500">{user?.username || '用户'}</p>
      </div>
      <button
        onClick={onMenuToggle}
        aria-label="Toggle menu"
        className="focus:outline-none p-2 rounded-lg hover:bg-gray-100"
      >
        <MenuIcon size={24} />
      </button>
    </div>
  );
};
