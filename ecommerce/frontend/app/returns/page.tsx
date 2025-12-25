'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { RotateCcw, ChevronRight, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  pickup_scheduled: 'bg-blue-100 text-blue-800',
  picked_up: 'bg-purple-100 text-purple-800',
  received: 'bg-indigo-100 text-indigo-800',
  refund_initiated: 'bg-teal-100 text-teal-800',
  refund_completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

const riskColors: Record<string, string> = {
  low: 'text-green-600',
  medium: 'text-yellow-600',
  high: 'text-red-600',
};

export default function ReturnsPage() {
  const router = useRouter();
  const { isAuthenticated } = useStore();
  const [returns, setReturns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/returns');
      return;
    }

    async function loadReturns() {
      try {
        const data = await api.getReturns();
        setReturns(data);
      } catch (error) {
        console.error('Failed to load returns:', error);
      } finally {
        setLoading(false);
      }
    }
    loadReturns();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-8">My Returns</h1>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (returns.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <RotateCcw className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">No returns yet</h1>
        <p className="text-gray-600 mb-4">
          You haven't made any return requests. You can return items from your orders.
        </p>
        <Link
          href="/orders"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          View Orders
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">My Returns</h1>

      {/* Info banner about return policy engine */}
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-primary-800">
              <strong>AI-Powered Returns:</strong> Our system uses machine learning to evaluate return
              requests. Customers with good history get faster approvals, while suspicious patterns
              are flagged for review.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {returns.map((ret) => (
          <Link
            key={ret.id}
            href={`/returns/${ret.id}`}
            className="block bg-white rounded-lg border hover:shadow-md transition-shadow"
          >
            <div className="p-4 flex items-center gap-4">
              {/* Product image */}
              <div className="relative w-20 h-20 flex-shrink-0 bg-gray-100 rounded-lg">
                {ret.product_image ? (
                  <Image
                    src={ret.product_image}
                    alt={ret.product_name}
                    fill
                    className="object-cover rounded-lg"
                  />
                ) : (
                  <RotateCcw className="w-8 h-8 absolute inset-0 m-auto text-gray-400" />
                )}
              </div>

              {/* Return details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Return #{ret.return_number}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${statusColors[ret.status]}`}>
                    {ret.status.replace(/_/g, ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-600 truncate">{ret.product_name}</p>
                <p className="text-sm text-gray-500">
                  Reason: {ret.reason.replace(/_/g, ' ')}
                </p>

                {/* Score indicator */}
                {ret.eligibility_score !== null && (
                  <div className="flex items-center gap-2 mt-1 text-sm">
                    <span className="text-gray-500">Score:</span>
                    <span className="font-medium">{ret.eligibility_score.toFixed(0)}/100</span>
                    {ret.risk_level && (
                      <span className={`${riskColors[ret.risk_level]}`}>
                        ({ret.risk_level} risk)
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Price and arrow */}
              <div className="text-right flex items-center gap-2">
                <div>
                  {ret.refund_amount && (
                    <p className="font-bold">Rs. {ret.refund_amount.toLocaleString()}</p>
                  )}
                  <p className="text-sm text-gray-500">
                    {new Date(ret.created_at).toLocaleDateString()}
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* Recommendation badge */}
            {ret.engine_recommendation && (
              <div className="px-4 pb-4">
                <div
                  className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${
                    ret.engine_recommendation === 'APPROVE'
                      ? 'bg-green-100 text-green-700'
                      : ret.engine_recommendation === 'DENY'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  {ret.engine_recommendation === 'APPROVE' && <CheckCircle className="w-3 h-3" />}
                  {ret.engine_recommendation === 'DENY' && <XCircle className="w-3 h-3" />}
                  {ret.engine_recommendation === 'REVIEW' && <Clock className="w-3 h-3" />}
                  AI Recommendation: {ret.engine_recommendation}
                </div>
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
