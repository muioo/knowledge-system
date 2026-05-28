import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
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
