import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  ShieldAlert,
  Activity,
  Database,
  AlertTriangle,
  Cpu,
  Settings as SettingsIcon,
  LineChart,
  BarChart2,
} from 'lucide-react';
import { getHealthStatus } from './services/api';
import { SystemHealth } from './types';
import Dashboard from './pages/Dashboard';
import StockExplorer from './pages/StockExplorer';
import DetectionCenter from './pages/DetectionCenter';
import Alerts from './pages/Alerts';
import ModelPerformance from './pages/ModelPerformance';
import DataManagement from './pages/DataManagement';
import Settings from './pages/Settings';

const SidebarNav: React.FC<{ health: SystemHealth | null }> = ({ health }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <Activity className="w-4 h-4 text-blue-400" /> },
    { path: '/explorer', label: 'Stock Explorer', icon: <LineChart className="w-4 h-4 text-emerald-400" /> },
    { path: '/detection', label: 'AI Detection Center', icon: <Cpu className="w-4 h-4 text-purple-400" /> },
    { path: '/alerts', label: 'Alert Management', icon: <AlertTriangle className="w-4 h-4 text-amber-400" /> },
    { path: '/models', label: 'Model Performance', icon: <BarChart2 className="w-4 h-4 text-indigo-400" /> },
    { path: '/data', label: 'Data Management', icon: <Database className="w-4 h-4 text-cyan-400" /> },
    { path: '/settings', label: 'Settings', icon: <SettingsIcon className="w-4 h-4 text-gray-400" /> },
  ];

  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col justify-between shrink-0">
      <div>
        <div className="p-5 border-b border-border flex items-center space-x-3">
          <ShieldAlert className="w-7 h-7 text-bearRed" />
          <div>
            <h1 className="font-bold text-sm tracking-wide text-gray-100">SURVEILLANCE AI</h1>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">NSE/BSE Pump-Dump Detector</p>
          </div>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-accent/20 text-white border border-accent/40'
                    : 'text-gray-300 hover:bg-surfaceHover hover:text-white'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-border text-[11px] text-gray-400">
        <div className="flex items-center justify-between">
          <span>Backend API:</span>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
              health?.status === 'healthy'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}
          >
            {health?.status ? health.status.toUpperCase() : 'CONNECTING...'}
          </span>
        </div>
      </div>
    </aside>
  );
};

export const App: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    getHealthStatus()
      .then(setHealth)
      .catch((err) => console.error('Health check error:', err));
  }, []);

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-background text-gray-100 antialiased overflow-hidden">
        <SidebarNav health={health} />
        <main className="flex-1 overflow-y-auto p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/explorer" element={<StockExplorer />} />
            <Route path="/detection" element={<DetectionCenter />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/models" element={<ModelPerformance />} />
            <Route path="/data" element={<DataManagement />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
