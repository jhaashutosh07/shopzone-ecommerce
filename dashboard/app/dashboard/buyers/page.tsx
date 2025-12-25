'use client';

import { useEffect, useState } from 'react';
import { api, Buyer } from '@/lib/api';
import { AlertTriangle, User, ShoppingBag, Star, ChevronLeft, ChevronRight } from 'lucide-react';

function RiskBadge({ returnRate }: { returnRate: number }) {
  if (returnRate >= 0.3) {
    return (
      <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium flex items-center">
        <AlertTriangle className="h-3 w-3 mr-1" />
        High Risk
      </span>
    );
  }
  if (returnRate >= 0.15) {
    return (
      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
        Medium Risk
      </span>
    );
  }
  return (
    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
      Low Risk
    </span>
  );
}

export default function BuyersPage() {
  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [showHighRisk, setShowHighRisk] = useState(false);

  const perPage = 20;

  useEffect(() => {
    setLoading(true);
    api.getBuyers(page, perPage)
      .then((data) => {
        if (showHighRisk) {
          setBuyers(data.filter(b => b.return_rate >= 0.3));
        } else {
          setBuyers(data);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, showHighRisk]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Buyers</h1>
        <p className="text-gray-500 mt-1">Monitor buyer behavior and risk levels</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div className="flex items-center space-x-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={showHighRisk}
              onChange={(e) => { setShowHighRisk(e.target.checked); setPage(1); }}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-gray-600">Show high-risk buyers only</span>
          </label>
        </div>
      </div>

      {/* Buyers Grid */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : buyers.length === 0 ? (
          <div className="text-center py-12">
            <User className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No buyers found</p>
            <p className="text-sm text-gray-400 mt-1">Buyers will appear here as return requests are processed</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Buyer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Orders</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Returns</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Return Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Review</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {buyers.map((buyer) => (
                  <tr key={buyer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-gray-500" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{buyer.external_buyer_id}</div>
                          <div className="text-sm text-gray-500">ID: {buyer.id.slice(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        <ShoppingBag className="h-4 w-4 text-gray-400 mr-2" />
                        {buyer.total_orders}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {buyer.total_returns}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className={`h-2 rounded-full ${
                              buyer.return_rate >= 0.3 ? 'bg-red-500' :
                              buyer.return_rate >= 0.15 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(buyer.return_rate * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-900">{(buyer.return_rate * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        <Star className="h-4 w-4 text-yellow-400 mr-1" />
                        {buyer.avg_review_score > 0 ? buyer.avg_review_score.toFixed(1) : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <RiskBadge returnRate={buyer.return_rate} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {buyers.length > 0 && (
          <div className="px-6 py-4 border-t flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Page {page}
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
                onClick={() => setPage(p => p + 1)}
                disabled={buyers.length < perPage}
                className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
