import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { AnomalyTrendPoint } from '../../services/analyticsService';

interface AnomalyTrendChartProps {
  data: AnomalyTrendPoint[];
}

export const AnomalyTrendChart: React.FC<AnomalyTrendChartProps> = ({ data }) => {
  return (
    <div className="bg-surface border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-200">Surveillance Anomaly Velocity</h3>
        <div className="flex items-center space-x-4 text-xs text-gray-400">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-bearRed inline-block"></span>
            <span>High Risk</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-warningOrange inline-block"></span>
            <span>Medium Risk</span>
          </span>
        </div>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#23324E" vertical={false} />
            <XAxis dataKey="date" stroke="#6B7280" tick={{ fontSize: 11 }} />
            <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#151F32',
                borderColor: '#23324E',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Area
              type="monotone"
              dataKey="high_risk"
              stackId="1"
              stroke="#EF4444"
              fill="#EF4444"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="medium_risk"
              stackId="1"
              stroke="#F59E0B"
              fill="#F59E0B"
              fillOpacity={0.4}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
