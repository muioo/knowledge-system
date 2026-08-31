import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { ArticleProvider } from './contexts/ArticleContext';
import { BreadcrumbProvider } from './contexts/BreadcrumbContext';
import AppRouter from './router';

/**
 * App 应用根组件
 * 仅负责 Provider 包裹，路由统一收敛在 src/router 下。
 */
const App: React.FC = () => {
  return (
    <AuthProvider>
      <ArticleProvider>
        <BreadcrumbProvider>
          <AppRouter />
        </BreadcrumbProvider>
      </ArticleProvider>
    </AuthProvider>
  );
};

export default App;