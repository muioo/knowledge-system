import React from 'react';

/**
 * Button 组件
 * 支持多种变体和自定义样式
 */
const Button = ({
  children,
  variant = 'default',
  className = '',
  isHovered = false,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';

  const variantStyles = {
    default:
      'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700',
    outline:
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className} ${isHovered ? 'shadow-lg shadow-blue-200' : ''}`;

  return (
    <button className={combinedClassName} {...props}>
      {children}
    </button>
  );
};

export default Button;
