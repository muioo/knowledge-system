import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import { MainLayout } from '../components/layout/MainLayout';
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import ArticleList from '../pages/ArticleList';
import ArticleCreate from '../pages/ArticleCreate';
import ArticleDetail from '../pages/ArticleDetail';
import TagManage from '../pages/TagManage';
import ReadingStats from '../pages/ReadingStats';
import AiSetting from '../pages/AiSetting';

/**
 * AppRouter 路由定义
 * 集中维护所有页面路由：根路径登录、受保护的主布局及其子页面。
 */
const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* 登录页 */}
        <Route path="/" element={<Login />} />

        {/* 受保护的主布局（需登录，含侧边栏/顶栏/面包屑） */}
        <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="articles" element={<ArticleList />} />
          <Route path="articles/create" element={<ArticleCreate />} />
          <Route path="articles/:id" element={<ArticleDetail />} />
          <Route path="tags" element={<TagManage />} />
          <Route path="reading/stats" element={<ReadingStats />} />
          <Route path="ai-settings" element={<AiSetting />} />

          {/* 未知路径兜底到仪表盘 */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>

        {/* 未定义根路径兜底到登录 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;