import React from 'react';

/**
 * DotMap 组件 - 创建点阵背景效果
 */
const DotMap: React.FC = () => {
  // 创建点阵网格
  const dots = Array.from({ length: 100 }, (_, i) => i);

  return (
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: `radial-gradient(circle, #cbd5e1 1px, transparent 1px)`,
        backgroundSize: '20px 20px',
      }}
    >
      {dots.map((i) => (
        <div
          key={i}
          className="absolute w-1 h-1 bg-blue-200 rounded-full opacity-40"
          style={{
            left: `${(i % 10) * 10 + 5}%`,
            top: `${Math.floor(i / 10) * 10 + 5}%`,
          }}
        />
      ))}
    </div>
  );
};

export default DotMap;
