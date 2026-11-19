import React, { useState } from 'react';
import { Cpu, Play } from 'lucide-react';
import { runDetection, DetectionResult } from '../services/detectionService';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DetectionCenter: React.FC = () => {
  const [exchange, setExchange] = useState('NSE');
  const [symbol, setSymbol] = useState('');
  const [modelName, setModelName] = useState('HYBRID');
  const [results, setResults] = useState<DetectionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const handleRunDetection = async () => {
    setLoading(true);
    setHasRun(true);
    try {
      const resp = await runDetection({
        exchange,
        symbol: symbol.trim() || undefined,
        model_name: modelName,
      });
      setResults(resp.results);
    } catch (err) {
      console.error('Detection trigger error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">AI Anomaly Detection Center</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Execute tri-modal surveillance models (Isolation Forest + LSTM Autoencoder + Microstructure Rules).
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-200 mb-4 flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-accent" />
          <span>Surveillance Engine Parameters</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Exchange</label>
            <select
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-xs text-gray-100 focus:outline-none focus:border-accent"
            >
              <option value="NSE">National Stock Exchange (NSE)</option>
              <option value="BSE">Bombay Stock Exchange (BSE)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Target Stock (Optional)</label>
            <input
              type="text"
              placeholder="e.g. PUMPDUMP_SUSPECT (leave blank for all)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-xs text-gray-100 focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Detection Model</label>
            <select
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-xs text-gray-100 focus:outline-none focus:border-accent"
            >
              <option value="HYBRID">Hybrid Ensemble (40% IF + 35% LSTM + 25% Rules)</option>
              <option value="ISOLATION_FOREST">Isolation Forest Only</option>
              <option value="LSTM">PyTorch LSTM Autoencoder Only</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRunDetection}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 bg-accent hover:bg-blue-600 disabled:opacity-50 text-white font-semibold text-xs py-2 px-4 rounded-md transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? 'Analyzing Market...' : 'Run Surveillance'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Detection Results */}
      {loading ? (
        <LoadingSpinner message="Executing PyTorch LSTM reconstruction and Isolation Forest scoring..." />
      ) : hasRun && results.length > 0 ? (
        <div className="bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-200">
              Ranked Anomaly Alerts ({results.length} flagged records)
            </h3>
            <span className="text-xs text-gray-400">Sorted by Anomaly Score Descending</span>
          </div>

          <div className="space-y-4">
            {results.map((res, i) => (
              <div
                key={i}
                className="p-4 bg-surfaceHover/60 rounded-lg border border-border hover:border-border/80 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-bold text-gray-100">{res.symbol}</span>
                    <span className="text-xs text-gray-400">({res.exchange})</span>
                    <span className="text-xs text-gray-300">Date: {res.trading_date}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-gray-400">
                      Score: <strong className="text-sm text-gray-100">{res.anomaly_score.toFixed(1)}/100</strong>
                    </span>
                    <Badge
                      label={res.risk_level}
                      variant={
                        res.risk_level === 'HIGH'
                          ? 'danger'
                          : res.risk_level === 'MEDIUM'
                          ? 'warning'
                          : 'neutral'
                      }
                    />
                  </div>
                </div>

                {/* Plain-Language Explanations */}
                <div className="mt-3 pt-3 border-t border-border/50">
                  <p className="text-xs font-semibold text-gray-400 mb-1">Evidence & Triggers:</p>
                  <ul className="list-disc list-inside space-y-1 text-xs text-gray-300">
                    {res.reasons.map((r, ri) => (
                      <li key={ri}>{r}</li>
                    ))}
                  </ul>
                </div>

                {/* Model Breakdown */}
                <div className="mt-3 grid grid-cols-3 gap-2 text-[11px] bg-background/50 p-2 rounded border border-border/40 text-gray-400">
                  <div>
                    Isolation Forest: <strong className="text-gray-200">{(res.model_breakdown.isolation_forest_score * 100).toFixed(1)}%</strong>
                  </div>
                  <div>
                    LSTM Reconstruction: <strong className="text-gray-200">{(res.model_breakdown.lstm_reconstruction_score * 100).toFixed(1)}%</strong>
                  </div>
                  <div>
                    Microstructure Rules: <strong className="text-gray-200">{(res.model_breakdown.rule_score * 100).toFixed(1)}%</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : hasRun ? (
        <div className="bg-surface border border-border rounded-lg p-8 text-center text-gray-400">
          No anomalies matched the selected filters.
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-lg p-8 text-center text-gray-400">
          Click <strong>"Run Surveillance"</strong> to scan loaded market data for price-volume manipulation signatures.
        </div>
      )}
    </div>
  );
};

export default DetectionCenter;
