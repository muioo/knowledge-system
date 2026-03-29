import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ArticleProvider } from './contexts/ArticleContext';
import { BreadcrumbProvider } from './contexts/BreadcrumbContext';
import ProtectedRoute from './components/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ArticleList from './pages/ArticleList';
import ArticleCreate from './pages/ArticleCreate';
import ArticleDetail from './pages/ArticleDetail';
import TagManage from './pages/TagManage';
import ReadingStats from './pages/ReadingStats';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ArticleProvider>
        <BreadcrumbProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="articles" element={<ArticleList />} />
                <Route path="articles/create" element={<ArticleCreate />} />
                <Route path="articles/:id" element={<ArticleDetail />} />
                <Route path="tags" element={<TagManage />} />
                <Route path="reading/stats" element={<ReadingStats />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </BreadcrumbProvider>
      </ArticleProvider>
    </AuthProvider>
  );
};

export default App;
