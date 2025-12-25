'use client';

import { useEffect, useState } from 'react';
import { api, ReturnRequest } from '@/lib/api';
import { CheckCircle, XCircle, Clock, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';

const reasonLabels: Record<string, string> = {
  size_issue: 'Size Issue',
  defective: 'Defective',
  not_as_described: 'Not as Described',
  changed_mind: 'Changed Mind',
  arrived_late: 'Arrived Late',
  damaged_in_shipping: 'Damaged in Shipping',
  wrong_item: 'Wrong Item',
  other: 'Other',
};

const decisionColors: Record<string, string> = {
  approved: 'bg-green-100 text-green-800',
  denied: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  review: 'bg-orange-100 text-orange-800',
};

const riskColors: Record<string, string> = {
  low: 'text-green-600',
  medium: 'text-yellow-600',
  high: 'text-red-600',
};

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-gray-400">-</span>;

  const color = score >= 70 ? 'bg-green-100 text-green-800' :
                score >= 40 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800';

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      {score.toFixed(0)}
    </span>
  );
}

export default function ReturnsPage() {
  const [returns, setReturns] = useState<ReturnRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<string>('');
  const [selectedReturn, setSelectedReturn] = useState<ReturnRequest | null>(null);

  const perPage = 10;

  const fetchReturns = async () => {
    setLoading(true);
    try {
      const data = await api.getReturns(page, perPage, filter || undefined);
      setReturns(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch returns:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReturns();
  }, [page, filter]);

  const handleDecision = async (returnId: string, decision: string) => {
    try {
      await api.updateReturnDecision(returnId, decision);
      fetchReturns();
      setSelectedReturn(null);
    } catch (error) {
      console.error('Failed to update decision:', error);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Return Requests</h1>
        <p className="text-gray-500 mt-1">Manage and review return requests</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => { setFilter(''); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === '' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => { setFilter('review'); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'review' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Needs Review
          </button>
          <button
            onClick={() => { setFilter('approved'); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'approved' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Approved
          </button>
          <button
            onClick={() => { setFilter('denied'); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'denied' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Denied
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : returns.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No return requests found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Days</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {returns.map((ret) => (
                  <tr key={ret.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{ret.order_id}</div>
                      <div className="text-sm text-gray-500">${ret.order_amount.toFixed(2)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{reasonLabels[ret.reason] || ret.reason}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <ScoreBadge score={ret.eligibility_score} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {ret.risk_level && (
                        <span className={`text-sm font-medium ${riskColors[ret.risk_level]}`}>
                          {ret.risk_level.charAt(0).toUpperCase() + ret.risk_level.slice(1)}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${decisionColors[ret.decision]}`}>
                        {ret.decision.charAt(0).toUpperCase() + ret.decision.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {ret.days_since_order}d
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {(ret.decision === 'pending' || ret.decision === 'review') && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleDecision(ret.id, 'approved')}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Approve"
                          >
                            <CheckCircle className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDecision(ret.id, 'denied')}
                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                            title="Deny"
                          >
                            <XCircle className="h-5 w-5" />
                          </button>
                        </div>
                      )}
                      <button
                        onClick={() => setSelectedReturn(ret)}
                        className="text-sm text-primary-600 hover:text-primary-800"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing {(page - 1) * perPage + 1} to {Math.min(page * perPage, total)} of {total}
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {selectedReturn && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Return Request Details</h3>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Order ID</p>
                    <p className="font-medium">{selectedReturn.order_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Amount</p>
                    <p className="font-medium">${selectedReturn.order_amount.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Reason</p>
                    <p className="font-medium">{reasonLabels[selectedReturn.reason]}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Days Since Order</p>
                    <p className="font-medium">{selectedReturn.days_since_order} days</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Eligibility Score</p>
                    <ScoreBadge score={selectedReturn.eligibility_score} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Risk Level</p>
                    <p className={`font-medium ${riskColors[selectedReturn.risk_level || 'low']}`}>
                      {selectedReturn.risk_level ? selectedReturn.risk_level.charAt(0).toUpperCase() + selectedReturn.risk_level.slice(1) : 'N/A'}
                    </p>
                  </div>
                </div>

                {selectedReturn.risk_flags && selectedReturn.risk_flags.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Risk Flags</p>
                    <div className="space-y-2">
                      {selectedReturn.risk_flags.map((flag, i) => (
                        <div key={i} className="flex items-start p-3 bg-red-50 rounded-lg">
                          <AlertTriangle className={`h-5 w-5 mr-2 flex-shrink-0 ${
                            flag.severity === 'high' ? 'text-red-600' :
                            flag.severity === 'medium' ? 'text-yellow-600' : 'text-gray-600'
                          }`} />
                          <div>
                            <p className="font-medium text-sm">{flag.code.replace(/_/g, ' ')}</p>
                            <p className="text-sm text-gray-600">{flag.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setSelectedReturn(null)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Close
                </button>
                {(selectedReturn.decision === 'pending' || selectedReturn.decision === 'review') && (
                  <>
                    <button
                      onClick={() => handleDecision(selectedReturn.id, 'denied')}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      Deny
                    </button>
                    <button
                      onClick={() => handleDecision(selectedReturn.id, 'approved')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Approve
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
