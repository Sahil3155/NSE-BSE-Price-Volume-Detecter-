import React, { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon }) => {
  return (
    <div className="bg-surface border border-border rounded-lg p-5 flex items-center justify-between">
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-gray-400">{title}</p>
        <p className="text-2xl font-bold mt-1 text-gray-100">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      {icon && (
        <div className="p-3 bg-surfaceHover rounded-lg border border-border/50 text-gray-300">
          {icon}
        </div>
      )}
    </div>
  );
};
