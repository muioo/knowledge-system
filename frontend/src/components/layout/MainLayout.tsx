import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

/**
 * MainLayout 组件 - 主布局容器
 * 包含 Sidebar、Header 和内容区域
 */
export const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleMenuToggle = () => {
    setSidebarOpen((prev) => !prev);
  };

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar - 单一实例，支持 mobile 和 desktop */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={handleSidebarClose}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-0 md:ml-64 transition-all duration-300">
        {/* Mobile Header */}
        <Header onMenuToggle={handleMenuToggle} />

        {/* Main Content */}
        <div className="p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
};
