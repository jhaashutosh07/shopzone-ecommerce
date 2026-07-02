'use client';

import { useEffect, useState } from 'react';
import { api, ModelVersion, DriftReport, RetrainResult } from '@/lib/api';
import { Brain, RefreshCw, CheckCircle2, Activity, AlertTriangle } from 'lucide-react';

const driftColors: Record<string, string> = {
  stable: 'bg-green-100 text-green-800',
  moderate: 'bg-yellow-100 text-yellow-800',
  drifted: 'bg-red-100 text-red-800',
  insufficient_data: 'bg-gray-100 text-gray-600',
};

function Metric({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="text-center">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-900">
        {value !== null && value !== undefined ? (value * 100).toFixed(1) + '%' : '-'}
      </p>
    </div>
  );
}

export default function ModelsPage() {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [drift, setDrift] = useState<DriftReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [retrainResult, setRetrainResult] = useState<RetrainResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [modelsData, driftData] = await Promise.all([
        api.getModels(),
        api.getDriftReport().catch(() => null),
      ]);
      setModels(modelsData);
      setDrift(driftData);
    } catch (e: any) {
      setError(e.message || 'Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRetrain = async () => {
    setRetraining(true);
    setError(null);
    setRetrainResult(null);
    try {
      const result = await api.retrainModel();
      setRetrainResult(result);
      await fetchData();
    } catch (e: any) {
      setError(e.message || 'Retraining failed');
    } finally {
      setRetraining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Model Registry</h1>
          <p className="text-gray-500 mt-1">
            Scoring model versions, feedback retraining, and drift monitoring
          </p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={retraining}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${retraining ? 'animate-spin' : ''}`} />
          {retraining ? 'Training…' : 'Retrain from feedback'}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
      )}

      {retrainResult && (
        <div className="mb-6 p-4 bg-green-50 text-green-800 rounded-lg text-sm flex items-start">
          <CheckCircle2 className="h-5 w-5 mr-2 flex-shrink-0" />
          <div>
            <p className="font-medium">{retrainResult.message}</p>
            <p className="mt-1 text-green-700">
              Your manual approve/deny overrides were used as ground-truth labels
              ({retrainResult.feedback_samples} samples).
            </p>
          </div>
        </div>
      )}

      {/* Drift monitoring */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Activity className="h-5 w-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">Data Drift</h2>
          </div>
          {drift && (
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${driftColors[drift.overall_status]}`}>
              {drift.overall_status.replace('_', ' ')}
            </span>
          )}
        </div>
        {!drift || drift.overall_status === 'insufficient_data' ? (
          <p className="text-sm text-gray-500">
            Not enough scored traffic yet ({drift?.samples_analyzed ?? 0} samples).
            Drift is computed once at least 30 requests have been scored.
          </p>
        ) : (
          <>
            <p className="text-sm text-gray-500 mb-4">
              Population Stability Index of live traffic vs. the training distribution
              ({drift.samples_analyzed} recent requests, model v{drift.model_version}).
              PSI &gt; 0.25 means the model sees data it was not trained on.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {drift.features.slice(0, 8).map((f) => (
                <div key={f.feature} className="flex items-center justify-between p-2 rounded-lg bg-gray-50">
                  <span className="text-sm text-gray-700">{f.label}</span>
                  <span className="flex items-center text-sm">
                    {f.status !== 'stable' && (
                      <AlertTriangle className={`h-4 w-4 mr-1 ${f.status === 'drifted' ? 'text-red-500' : 'text-yellow-500'}`} />
                    )}
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${driftColors[f.status]}`}>
                      PSI {f.psi.toFixed(3)}
                    </span>
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Version history */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 pb-2 flex items-center">
          <Brain className="h-5 w-5 text-primary-600 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Version History</h2>
        </div>
        {models.length === 0 ? (
          <p className="p-6 text-sm text-gray-500">No models registered yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Samples</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Feedback</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Precision</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Recall</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">ROC-AUC</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trained</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {models.map((m) => (
                  <tr key={m.id} className={m.is_active ? 'bg-primary-50/50' : 'hover:bg-gray-50'}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">v{m.version}</td>
                    <td className="px-6 py-4">
                      {m.is_active ? (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          Archived
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{m.training_samples.toLocaleString()}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{m.feedback_samples}</td>
                    <td className="px-6 py-4"><Metric label="" value={m.accuracy} /></td>
                    <td className="px-6 py-4"><Metric label="" value={m.precision_score} /></td>
                    <td className="px-6 py-4"><Metric label="" value={m.recall_score} /></td>
                    <td className="px-6 py-4"><Metric label="" value={m.roc_auc} /></td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {m.trained_at ? new Date(m.trained_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
