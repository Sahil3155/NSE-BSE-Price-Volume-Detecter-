import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { PriceVolumeChart } from '../components/charts/PriceVolumeChart';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { fetchStocks, fetchStockHistory, StockHistoryResponse } from '../services/stockService';
import { Stock } from '../types';

export const StockExplorer: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [exchangeFilter, setExchangeFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [historyData, setHistoryData] = useState<StockHistoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [chartLoading, setChartLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchStocks(exchangeFilter)
      .then((data) => {
        setStocks(data);
        if (data.length > 0 && !selectedSymbol) {
          setSelectedSymbol(data[0].symbol);
        }
      })
      .catch((err) => console.error('Stocks fetch error:', err))
      .finally(() => setLoading(false));
  }, [exchangeFilter]);

  useEffect(() => {
    if (!selectedSymbol) return;
    setChartLoading(true);
    fetchStockHistory(selectedSymbol)
      .then(setHistoryData)
      .catch((err) => console.error('History fetch error:', err))
      .finally(() => setChartLoading(false));
  }, [selectedSymbol]);

  const filteredStocks = stocks.filter((s) =>
    s.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) return <LoadingSpinner message="Loading stock listings..." />;

  const latestPoint = historyData?.history[historyData.history.length - 1];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Stock Surveillance Explorer</h2>
          <p className="text-xs text-gray-400 mt-0.5">Inspect price, volume, and circuit-limit trajectory for listed equities.</p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search symbol..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-surface border border-border rounded-md pl-9 pr-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-accent"
            />
          </div>

          <select
            value={exchangeFilter}
            onChange={(e) => setExchangeFilter(e.target.value)}
            className="bg-surface border border-border rounded-md px-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-accent"
          >
            <option value="">All Exchanges</option>
            <option value="NSE">NSE</option>
            <option value="BSE">BSE</option>
          </select>
        </div>
      </div>

      {/* Stock Selection Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {filteredStocks.slice(0, 15).map((stock) => (
          <button
            key={stock.symbol}
            onClick={() => setSelectedSymbol(stock.symbol)}
            className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap transition-colors ${
              selectedSymbol === stock.symbol
                ? 'bg-accent text-white'
                : 'bg-surface hover:bg-surfaceHover text-gray-300 border border-border'
            }`}
          >
            {stock.symbol} ({stock.exchange_code || 'NSE'})
          </button>
        ))}
      </div>

      {/* Active Stock Key Stats */}
      {latestPoint && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Latest Close</p>
            <p className="text-xl font-bold text-gray-100 mt-1">₹{latestPoint.close.toFixed(2)}</p>
            <p className={`text-xs mt-1 ${latestPoint.daily_return && latestPoint.daily_return >= 0 ? 'text-bullGreen' : 'text-bearRed'}`}>
              {latestPoint.daily_return ? `${latestPoint.daily_return >= 0 ? '+' : ''}${latestPoint.daily_return.toFixed(2)}%` : '0.0%'}
            </p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Trading Volume</p>
            <p className="text-xl font-bold text-cyan-400 mt-1">{latestPoint.volume.toLocaleString()}</p>
            <p className="text-xs text-gray-400 mt-1">Shares traded</p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Consecutive Upper Circuits</p>
            <p className="text-xl font-bold text-warningOrange mt-1">{latestPoint.consecutive_upper_circuits || 0}</p>
            <p className="text-xs text-gray-400 mt-1">Sessions locked</p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Observations</p>
            <p className="text-xl font-bold text-gray-100 mt-1">{historyData?.total_records || 0}</p>
            <p className="text-xs text-gray-400 mt-1">Historical sessions</p>
          </div>
        </div>
      )}

      {/* Interactive Chart */}
      {chartLoading ? (
        <LoadingSpinner message={`Rendering trajectory for ${selectedSymbol}...`} />
      ) : historyData && historyData.history.length > 0 ? (
        <PriceVolumeChart data={historyData.history} symbol={selectedSymbol} />
      ) : (
        <div className="bg-surface border border-border rounded-lg p-8 text-center text-gray-400">
          No historical price/volume data found for {selectedSymbol}.
        </div>
      )}
    </div>
  );
};

export default StockExplorer;
