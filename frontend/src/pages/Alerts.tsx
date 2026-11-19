import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { fetchAlerts, updateAlertStatus } from '../services/alertService';
import { AnomalyAlert, RiskLevel } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AnomalyAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [symbolSearch, setSymbolSearch] = useState<string>('');
  const [activeAlert, setActiveAlert] = useState<AnomalyAlert | null>(null);
  const [newStatus, setNewStatus] = useState<string>('INVESTIGATING');
  const [notes, setNotes] = useState<string>('');

  const loadAlerts = () => {
    setLoading(true);
    fetchAlerts({
      risk_level: (riskFilter as RiskLevel) || undefined,
      status: statusFilter || undefined,
      symbol: symbolSearch.trim() || undefined,
    })
      .then(setAlerts)
      .catch((err) => console.error('Alerts load error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, [riskFilter, statusFilter]);

  const handleUpdateStatus = async () => {
    if (!activeAlert) return;
    try {
      await updateAlertStatus(activeAlert.id, newStatus, notes);
      setActiveAlert(null);
      loadAlerts();
    } catch (err) {
      console.error('Update status error:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Surveillance Alert Management</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Audit, investigate, and triage flagged pump-and-dump market anomalies.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter by symbol..."
              value={symbolSearch}
              onChange={(e) => setSymbolSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadAlerts()}
              className="bg-surface border border-border rounded-md pl-9 pr-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-accent"
            />
          </div>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-surface border border-border rounded-md px-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-accent"
          >
            <option value="">All Risk Levels</option>
            <option value="HIGH">High Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="LOW">Low Risk</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-surface border border-border rounded-md px-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-accent"
          >
            <option value="">All Review Statuses</option>
            <option value="PENDING_REVIEW">Pending Review</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CONFIRMED_ANOMALY">Confirmed Anomaly</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      {loading ? (
        <LoadingSpinner message="Fetching alerts database..." />
      ) : alerts.length > 0 ? (
        <div className="bg-surface border border-border rounded-lg overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-surfaceHover/80 text-gray-400 border-b border-border">
              <tr>
                <th className="py-3 px-4">Alert ID</th>
                <th className="py-3 px-4">Symbol</th>
                <th className="py-3 px-4">Exchange</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4">Risk</th>
                <th className="py-3 px-4">Reasons</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {alerts.map((a) => (
                <tr key={a.id} className="hover:bg-surfaceHover/40">
                  <td className="py-3 px-4 font-mono text-gray-400">#{a.id}</td>
                  <td className="py-3 px-4 font-bold text-gray-100">{a.stock_symbol}</td>
                  <td className="py-3 px-4 text-gray-400">{a.exchange}</td>
                  <td className="py-3 px-4 text-gray-300">{a.detection_date}</td>
                  <td className="py-3 px-4 font-bold text-bearRed">{a.anomaly_score.toFixed(1)}</td>
                  <td className="py-3 px-4">
                    <Badge
                      label={a.risk_level}
                      variant={a.risk_level === 'HIGH' ? 'danger' : 'warning'}
                    />
                  </td>
                  <td className="py-3 px-4 text-gray-300 max-w-xs truncate">
                    {a.reasons.join(', ')}
                  </td>
                  <td className="py-3 px-4">
                    <Badge label={a.status} variant="info" />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => {
                        setActiveAlert(a);
                        setNewStatus(a.status);
                        setNotes('');
                      }}
                      className="px-2.5 py-1 bg-surfaceHover hover:bg-border text-gray-200 rounded border border-border text-[11px]"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-lg p-8 text-center text-gray-400">
          No alerts matching the selected filters.
        </div>
      )}

      {/* Review Modal / Drawer */}
      {activeAlert && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
          <div className="bg-surface border border-border rounded-lg max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-base font-bold text-gray-100">
                  Audit Alert #{activeAlert.id} — {activeAlert.stock_symbol}
                </h3>
                <p className="text-xs text-gray-400">Date: {activeAlert.detection_date}</p>
              </div>
              <Badge label={activeAlert.risk_level} variant="danger" />
            </div>

            <div>
              <p className="text-xs font-semibold text-gray-400 mb-1">Triggered Indicators:</p>
              <ul className="list-disc list-inside space-y-1 text-xs text-gray-300 bg-background/60 p-3 rounded border border-border">
                {activeAlert.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Update Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-xs text-gray-100"
              >
                <option value="PENDING_REVIEW">PENDING REVIEW</option>
                <option value="INVESTIGATING">INVESTIGATING</option>
                <option value="CONFIRMED_ANOMALY">CONFIRMED ANOMALY</option>
                <option value="DISMISSED">DISMISSED</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Surveillance Desk Notes</label>
              <textarea
                rows={3}
                placeholder="Enter audit notes or escalation details..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full bg-background border border-border rounded-md p-3 text-xs text-gray-100"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-border">
              <button
                onClick={() => setActiveAlert(null)}
                className="px-4 py-2 text-xs text-gray-400 hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateStatus}
                className="px-4 py-2 bg-accent hover:bg-blue-600 text-white rounded text-xs font-semibold"
              >
                Save Decision
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;
