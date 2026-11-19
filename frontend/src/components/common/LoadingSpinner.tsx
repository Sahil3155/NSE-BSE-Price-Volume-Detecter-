import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Loading surveillance data...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-gray-400">
      <Loader2 className="w-8 h-8 animate-spin text-accent mb-3" />
      <p className="text-sm">{message}</p>
    </div>
  );
};
