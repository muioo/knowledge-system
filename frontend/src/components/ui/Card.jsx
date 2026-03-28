import React from 'react';

/**
 * Card 组件
 * 提供卡片容器样式
 */
const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
