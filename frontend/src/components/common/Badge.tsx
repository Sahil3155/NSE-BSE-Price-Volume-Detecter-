import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'danger' | 'warning' | 'success' | 'info' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'neutral' }) => {
  const styles = {
    danger: 'bg-red-950/80 text-bearRed border-red-800/60',
    warning: 'bg-amber-950/80 text-warningOrange border-amber-800/60',
    success: 'bg-emerald-950/80 text-bullGreen border-emerald-800/60',
    info: 'bg-blue-950/80 text-blue-400 border-blue-800/60',
    neutral: 'bg-gray-800 text-gray-300 border-gray-700',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${styles[variant]}`}>
      {label}
    </span>
  );
};
