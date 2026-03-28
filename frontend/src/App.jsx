import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ArticleProvider } from './contexts/ArticleContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ArticleList from './pages/ArticleList';
import ArticleCreate from './pages/ArticleCreate';

function App() {
  return (
    <AuthProvider>
      <ArticleProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="articles" element={<ArticleList />} />
              <Route path="articles/create" element={<ArticleCreate />} />
              <Route path="articles/:id" element={<div>文章详情页面（待实现）</div>} />
              <Route path="tags" element={<div>标签管理页面（待实现）</div>} />
              <Route path="reading/stats" element={<div>阅读统计页面（待实现）</div>} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ArticleProvider>
    </AuthProvider>
  );
}

export default App;
