import React, { useEffect, useState } from 'react';
import { ShieldAlert, AlertTriangle, Activity, Calendar, ArrowUpRight } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AnomalyTrendChart } from '../components/charts/AnomalyTrendChart';
import { fetchOverviewMetrics, fetchAnomalyTrends, OverviewMetrics, AnomalyTrendPoint } from '../services/analyticsService';
import { fetchAlerts } from '../services/alertService';
import { AnomalyAlert } from '../types';

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [trends, setTrends] = useState<AnomalyTrendPoint[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<AnomalyAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchOverviewMetrics(),
      fetchAnomalyTrends(30),
      fetchAlerts({ risk_level: 'HIGH' }),
    ])
      .then(([m, t, a]) => {
        setMetrics(m);
        setTrends(t);
        setRecentAlerts(a.slice(0, 5));
      })
      .catch((err) => console.error('Dashboard load error:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating surveillance metrics..." />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Market Surveillance Overview</h2>
          <p className="text-xs text-gray-400 mt-0.5">Real-time price & volume anomaly monitoring for small-cap equities.</p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-gray-400 bg-surface px-3 py-1.5 rounded-md border border-border">
          <Calendar className="w-3.5 h-3.5 text-accent" />
          <span>Latest Session: {metrics?.latest_detection_date || 'N/A'}</span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Equities"
          value={metrics?.total_stocks_monitored || 0}
          subtitle="NSE & BSE SmallCap universe"
          icon={<Activity className="w-5 h-5 text-accent" />}
        />
        <StatCard
          title="High Risk Alerts"
          value={metrics?.high_risk_alerts || 0}
          subtitle="Score >= 75 / 100"
          icon={<ShieldAlert className="w-5 h-5 text-bearRed" />}
        />
        <StatCard
          title="Medium Risk Watch"
          value={metrics?.medium_risk_alerts || 0}
          subtitle="Score 50 - 74 / 100"
          icon={<AlertTriangle className="w-5 h-5 text-warningOrange" />}
        />
        <StatCard
          title="Anomalies Flagged"
          value={metrics?.stocks_with_anomalies || 0}
          subtitle="Total multi-day deviations"
          icon={<ArrowUpRight className="w-5 h-5 text-purple-400" />}
        />
      </div>

      {/* Charts & Highest Anomaly Stocks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AnomalyTrendChart data={trends} />
        </div>

        <div className="bg-surface border border-border rounded-lg p-5">
          <h3 className="text-sm font-semibold text-gray-200 mb-4">Highest Anomaly Equities</h3>
          {metrics?.highest_anomaly_stocks && metrics.highest_anomaly_stocks.length > 0 ? (
            <div className="space-y-3">
              {metrics.highest_anomaly_stocks.map((item, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 bg-surfaceHover rounded border border-border/50">
                  <div>
                    <p className="text-sm font-semibold text-gray-200">{item.symbol}</p>
                    <p className="text-xs text-gray-400">Peak Surveillance Score</p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-bearRed">{item.score}/100</span>
                    <div>
                      <Badge label="HIGH RISK" variant="danger" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400">No anomaly scores recorded yet.</p>
          )}
        </div>
      </div>

      {/* Recent Alerts Feed */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-200 mb-3">Critical Surveillance Alerts</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surfaceHover/80 text-gray-400 border-b border-border">
              <tr>
                <th className="py-2.5 px-3">Symbol</th>
                <th className="py-2.5 px-3">Exchange</th>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Score</th>
                <th className="py-2.5 px-3">Risk</th>
                <th className="py-2.5 px-3">Key Reasons</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {recentAlerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-surfaceHover/40">
                  <td className="py-2.5 px-3 font-semibold text-gray-100">{alert.stock_symbol}</td>
                  <td className="py-2.5 px-3 text-gray-400">{alert.exchange}</td>
                  <td className="py-2.5 px-3 text-gray-300">{alert.detection_date}</td>
                  <td className="py-2.5 px-3 font-bold text-bearRed">{alert.anomaly_score.toFixed(1)}</td>
                  <td className="py-2.5 px-3">
                    <Badge label={alert.risk_level} variant={alert.risk_level === 'HIGH' ? 'danger' : 'warning'} />
                  </td>
                  <td className="py-2.5 px-3 text-gray-300 max-w-md truncate">
                    {alert.reasons.join('; ')}
                  </td>
                  <td className="py-2.5 px-3">
                    <Badge label={alert.status} variant="info" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
