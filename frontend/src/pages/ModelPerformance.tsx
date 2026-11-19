import React, { useEffect, useState } from 'react';
import { fetchModelBenchmarks, ModelBenchmark } from '../services/analyticsService';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Badge } from '../components/common/Badge';

export const ModelPerformance: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<ModelBenchmark[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModelBenchmarks()
      .then(setBenchmarks)
      .catch((err) => console.error('Benchmark load error:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Evaluating surveillance benchmark models..." />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Model Performance & Evaluation</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Empirical benchmark metrics evaluated against SEBI enforcement weak labels.
          </p>
        </div>
      </div>

      {/* Method Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {benchmarks.map((m, idx) => (
          <div key={idx} className="bg-surface border border-border rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-gray-200">{m.model_name}</h3>
              <Badge label={`T=${m.threshold}`} variant="neutral" />
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Precision:</span>
                <span className="font-semibold text-gray-100">{(m.precision * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Recall:</span>
                <span className="font-semibold text-gray-100">{(m.recall * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">F1-Score:</span>
                <span className="font-semibold text-accent">{(m.f1_score * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">ROC-AUC:</span>
                <span className="font-semibold text-bullGreen">{m.roc_auc.toFixed(3)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">False Positive Rate:</span>
                <span className="font-semibold text-bearRed">{(m.false_positive_rate * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* Confusion Matrix Mini-Pill */}
            <div className="pt-2 border-t border-border/50 text-[11px] text-gray-400">
              <span className="font-semibold text-gray-300">Confusion Matrix:</span>
              <div className="grid grid-cols-2 gap-1 mt-1 text-center font-mono">
                <div className="bg-background/60 p-1 rounded border border-border/40">
                  TP: {m.confusion_matrix.tp}
                </div>
                <div className="bg-background/60 p-1 rounded border border-border/40">
                  FP: {m.confusion_matrix.fp}
                </div>
                <div className="bg-background/60 p-1 rounded border border-border/40">
                  FN: {m.confusion_matrix.fn}
                </div>
                <div className="bg-background/60 p-1 rounded border border-border/40">
                  TN: {m.confusion_matrix.tn}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparative Evaluation Table */}
      <div className="bg-surface border border-border rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-200 mb-3">
          Surveillance Model Comparison Benchmark
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surfaceHover/80 text-gray-400 border-b border-border">
              <tr>
                <th className="py-2.5 px-3">Surveillance Model</th>
                <th className="py-2.5 px-3">Optimal Threshold</th>
                <th className="py-2.5 px-3">Precision</th>
                <th className="py-2.5 px-3">Recall</th>
                <th className="py-2.5 px-3">F1-Score</th>
                <th className="py-2.5 px-3">ROC-AUC</th>
                <th className="py-2.5 px-3">PR-AUC</th>
                <th className="py-2.5 px-3">FPR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {benchmarks.map((b, i) => (
                <tr key={i} className="hover:bg-surfaceHover/40">
                  <td className="py-2.5 px-3 font-semibold text-gray-100">{b.model_name}</td>
                  <td className="py-2.5 px-3 font-mono text-gray-300">{b.threshold}</td>
                  <td className="py-2.5 px-3 text-gray-200">{(b.precision * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-gray-200">{(b.recall * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 font-bold text-accent">{(b.f1_score * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 font-bold text-bullGreen">{b.roc_auc.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-gray-200">{b.pr_auc.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-bearRed">{(b.false_positive_rate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ModelPerformance;
