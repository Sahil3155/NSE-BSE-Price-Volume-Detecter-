import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface ChartDataPoint {
  trading_date: string;
  close: number;
  volume: number;
  daily_return?: number;
  consecutive_upper_circuits?: number;
}

interface PriceVolumeChartProps {
  data: ChartDataPoint[];
  symbol: string;
}

export const PriceVolumeChart: React.FC<PriceVolumeChartProps> = ({ data, symbol }) => {
  return (
    <div className="bg-surface border border-border rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-200">
          Price & Volume Trajectory — {symbol}
        </h3>
        <div className="flex items-center space-x-4 text-xs text-gray-400">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-accent inline-block"></span>
            <span>Close (₹)</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-600 inline-block"></span>
            <span>Volume</span>
          </span>
        </div>
      </div>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#23324E" vertical={false} />
            <XAxis dataKey="trading_date" stroke="#6B7280" tick={{ fontSize: 11 }} />
            <YAxis
              yAxisId="price"
              domain={['auto', 'auto']}
              stroke="#6B7280"
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => `₹${v}`}
            />
            <YAxis
              yAxisId="volume"
              orientation="right"
              stroke="#6B7280"
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#151F32',
                borderColor: '#23324E',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill="#0E7490"
              opacity={0.4}
              radius={[2, 2, 0, 0]}
            />
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
