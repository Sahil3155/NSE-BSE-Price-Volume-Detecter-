import React, { useEffect, useState } from 'react';
import { Database, Sliders, Info } from 'lucide-react';
import { getHealthStatus } from '../services/api';
import { SystemHealth } from '../types';
import { Badge } from '../components/common/Badge';

export const Settings: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    getHealthStatus()
      .then(setHealth)
      .catch((err) => console.error('Health fetch error:', err));
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-gray-100">System Configuration & Thresholds</h2>
        <p className="text-xs text-gray-400 mt-0.5">
          Surveillance risk parameters, neural network lookback windows, and environment settings.
        </p>
      </div>

      {/* Database & Runtime Info */}
      <div className="bg-surface border border-border rounded-lg p-5 space-y-4">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center space-x-2">
          <Database className="w-4 h-4 text-accent" />
          <span>Database & Environment Health</span>
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div>
            <p className="text-gray-400">Database Connectivity</p>
            <div className="mt-1">
              <Badge
                label={health?.database_connected ? 'CONNECTED (ONLINE)' : 'DISCONNECTED'}
                variant={health?.database_connected ? 'success' : 'danger'}
              />
            </div>
          </div>
          <div>
            <p className="text-gray-400">Environment</p>
            <p className="text-sm font-semibold text-gray-200 mt-1 uppercase">{health?.environment || 'development'}</p>
          </div>
          <div>
            <p className="text-gray-400">Application Version</p>
            <p className="text-sm font-semibold text-gray-200 mt-1">{health?.version || '1.0.0'}</p>
          </div>
          <div>
            <p className="text-gray-400">Overall Status</p>
            <div className="mt-1">
              <Badge label={health?.status?.toUpperCase() || 'UNKNOWN'} variant={health?.status === 'healthy' ? 'success' : 'warning'} />
            </div>
          </div>
        </div>
      </div>

      {/* Detection Thresholds Form */}
      <div className="bg-surface border border-border rounded-lg p-5 space-y-4">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-accent" />
          <span>Active Surveillance Sensitivity Thresholds</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">Volume Surge Multiplier Trigger</label>
            <p className="text-gray-400 mt-0.5">Multiple of 20-day moving average volume to trigger alert.</p>
            <div className="mt-2 text-sm font-bold text-accent">4.0x average volume</div>
          </div>

          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">Single-Day Price Jump Threshold</label>
            <p className="text-gray-400 mt-0.5">Single-day percentage increase to raise alert indicator.</p>
            <div className="mt-2 text-sm font-bold text-accent">+10.0% gain</div>
          </div>

          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">Consecutive Upper Circuit Limit</label>
            <p className="text-gray-400 mt-0.5">Number of consecutive sessions closed at upper band.</p>
            <div className="mt-2 text-sm font-bold text-accent">3 sessions</div>
          </div>

          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">LSTM Lookback Sequence Window</label>
            <p className="text-gray-400 mt-0.5">Time-series sliding window for sequence reconstruction.</p>
            <div className="mt-2 text-sm font-bold text-accent">10 trading days</div>
          </div>

          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">High Risk Composite Cutoff</label>
            <p className="text-gray-400 mt-0.5">Minimum score (0-100) classified as High Risk.</p>
            <div className="mt-2 text-sm font-bold text-bearRed">&gt;= 75.0 / 100</div>
          </div>

          <div className="bg-background/60 p-3.5 rounded border border-border">
            <label className="block font-semibold text-gray-300">Hybrid Ensemble Model Weights</label>
            <p className="text-gray-400 mt-0.5">Isolation Forest / LSTM Autoencoder / Deterministic Rules.</p>
            <div className="mt-2 text-sm font-bold text-gray-200">40% IF / 35% LSTM / 25% Rules</div>
          </div>
        </div>
      </div>

      {/* Academic Project Info */}
      <div className="bg-surface border border-border rounded-lg p-5 space-y-2">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center space-x-2">
          <Info className="w-4 h-4 text-cyan-400" />
          <span>Research & Methodology Scope</span>
        </h3>
        <p className="text-xs text-gray-300 leading-relaxed">
          <strong>NSE/BSE Small-Cap Pump-and-Dump Early Detector</strong> is designed as a research-grade surveillance system for identifying micro-cap price-volume manipulation signatures. Operating strictly on price and volume without external sentiment, it addresses the active enforcement gap documented in recent SEBI regulatory orders.
        </p>
      </div>
    </div>
  );
};

export default Settings;
