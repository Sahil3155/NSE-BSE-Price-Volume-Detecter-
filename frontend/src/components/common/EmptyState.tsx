import React, { ReactNode } from 'react';
import { Database } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, action }) => {
  return (
    <div className="bg-surface/50 border border-border border-dashed rounded-lg p-12 text-center flex flex-col items-center justify-center">
      <div className="p-3 bg-surfaceHover rounded-full text-gray-400 mb-3">
        <Database className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-gray-200">{title}</h3>
      <p className="text-sm text-gray-400 max-w-sm mt-1 mb-4">{description}</p>
      {action}
    </div>
  );
};
