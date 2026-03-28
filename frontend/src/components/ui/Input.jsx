import React from 'react';

/**
 * Input 组件
 * 提供统一的输入框样式
 */
const Input = ({ className = '', ...props }) => {
  const baseStyles =
    'flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm text-gray-800 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 border-gray-200 bg-gray-50 focus:border-blue-500';

  return <input className={`${baseStyles} ${className}`} {...props} />;
};

export default Input;
