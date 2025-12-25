'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import toast from 'react-hot-toast';
import {
  RotateCcw,
  CheckCircle,
  XCircle,
  Clock,
  Truck,
  Package,
  CreditCard,
  AlertTriangle,
} from 'lucide-react';

const statusSteps = [
  { key: 'approved', label: 'Approved', icon: CheckCircle },
  { key: 'pickup_scheduled', label: 'Pickup Scheduled', icon: Clock },
  { key: 'picked_up', label: 'Picked Up', icon: Truck },
  { key: 'received', label: 'Received', icon: Package },
  { key: 'refund_completed', label: 'Refunded', icon: CreditCard },
];

export default function ReturnDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useStore();
  const [returnRequest, setReturnRequest] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    async function loadReturn() {
      try {
        const data = await api.getReturn(id as string);
        setReturnRequest(data);
      } catch (error) {
        console.error('Failed to load return:', error);
        toast.error('Return not found');
        router.push('/returns');
      } finally {
        setLoading(false);
      }
    }
    loadReturn();
  }, [id, isAuthenticated, router]);

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this return request?')) return;

    try {
      const updated = await api.cancelReturn(returnRequest.id);
      setReturnRequest(updated);
      toast.success('Return cancelled');
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel return');
    }
  };

  const getCurrentStep = () => {
    const index = statusSteps.findIndex((s) => s.key === returnRequest?.status);
    return index >= 0 ? index : -1;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 w-1/3 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!returnRequest) return null;

  const currentStep = getCurrentStep();
  const riskFlags = returnRequest.risk_flags
    ? JSON.parse(returnRequest.risk_flags)
    : [];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-2">Return #{returnRequest.return_number}</h1>
      <p className="text-gray-600 mb-6">
        Created on{' '}
        {new Date(returnRequest.created_at).toLocaleDateString('en-IN', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })}
      </p>

      {/* Status tracker for approved returns */}
      {returnRequest.status !== 'pending' &&
        returnRequest.status !== 'rejected' &&
        returnRequest.status !== 'cancelled' && (
          <div className="bg-white rounded-lg border p-6 mb-6">
            <div className="flex justify-between">
              {statusSteps.map((step, index) => {
                const Icon = step.icon;
                const isCompleted = index <= currentStep;
                const isCurrent = index === currentStep;

                return (
                  <div key={step.key} className="flex-1 relative">
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          isCompleted
                            ? 'bg-green-500 text-white'
                            : 'bg-gray-200 text-gray-500'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <span
                        className={`text-xs mt-2 text-center ${
                          isCurrent ? 'font-medium text-green-600' : 'text-gray-600'
                        }`}
                      >
                        {step.label}
                      </span>
                    </div>
                    {index < statusSteps.length - 1 && (
                      <div
                        className={`absolute top-5 left-1/2 w-full h-0.5 ${
                          index < currentStep ? 'bg-green-500' : 'bg-gray-200'
                        }`}
                      ></div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

      {/* Pending status */}
      {returnRequest.status === 'pending' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 flex items-center gap-3">
          <Clock className="w-6 h-6 text-yellow-600" />
          <div>
            <p className="font-medium text-yellow-800">Under Review</p>
            <p className="text-sm text-yellow-600">
              Your return request is being reviewed. You'll be notified once a decision is made.
            </p>
          </div>
        </div>
      )}

      {/* Rejected status */}
      {returnRequest.status === 'rejected' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-3">
          <XCircle className="w-6 h-6 text-red-600" />
          <div>
            <p className="font-medium text-red-800">Return Denied</p>
            <p className="text-sm text-red-600">
              {returnRequest.decision_notes || 'Your return request was denied based on our policy.'}
            </p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Return details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Product */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="font-bold mb-4">Return Item</h2>
            <div className="flex gap-4">
              <div className="relative w-24 h-24 bg-gray-100 rounded-lg flex-shrink-0">
                {returnRequest.product_image && (
                  <Image
                    src={returnRequest.product_image}
                    alt=""
                    fill
                    className="object-cover rounded-lg"
                  />
                )}
              </div>
              <div>
                <p className="font-medium">{returnRequest.product_name}</p>
                <p className="text-gray-600">
                  Amount: Rs. {returnRequest.order_amount?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Reason: {returnRequest.reason.replace(/_/g, ' ')}
                </p>
                {returnRequest.reason_details && (
                  <p className="text-sm text-gray-500">{returnRequest.reason_details}</p>
                )}
              </div>
            </div>
          </div>

          {/* AI Scoring Details */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="font-bold mb-4">Return Policy Engine Analysis</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">
                  {returnRequest.eligibility_score?.toFixed(0) || 'N/A'}
                </p>
                <p className="text-xs text-gray-500">Score (0-100)</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p
                  className={`text-2xl font-bold capitalize ${
                    returnRequest.risk_level === 'low'
                      ? 'text-green-600'
                      : returnRequest.risk_level === 'medium'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}
                >
                  {returnRequest.risk_level || 'N/A'}
                </p>
                <p className="text-xs text-gray-500">Risk Level</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">
                  {returnRequest.engine_recommendation || 'N/A'}
                </p>
                <p className="text-xs text-gray-500">AI Recommendation</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">
                  {returnRequest.engine_confidence
                    ? `${(returnRequest.engine_confidence * 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
                <p className="text-xs text-gray-500">Confidence</p>
              </div>
            </div>

            {/* Risk Flags */}
            {riskFlags.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">Risk Flags Detected</h3>
                <div className="space-y-2">
                  {riskFlags.map((flag: any, index: number) => (
                    <div
                      key={index}
                      className={`flex items-start gap-2 p-3 rounded-lg ${
                        flag.severity === 'high'
                          ? 'bg-red-50'
                          : flag.severity === 'medium'
                          ? 'bg-yellow-50'
                          : 'bg-gray-50'
                      }`}
                    >
                      <AlertTriangle
                        className={`w-4 h-4 mt-0.5 ${
                          flag.severity === 'high'
                            ? 'text-red-500'
                            : flag.severity === 'medium'
                            ? 'text-yellow-500'
                            : 'text-gray-500'
                        }`}
                      />
                      <div>
                        <p className="text-sm font-medium">{flag.code.replace(/_/g, ' ')}</p>
                        <p className="text-xs text-gray-600">{flag.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {riskFlags.length === 0 && returnRequest.eligibility_score && (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                <p>No risk flags detected. You're a trusted customer!</p>
              </div>
            )}
          </div>
        </div>

        {/* Summary and actions */}
        <div className="space-y-6">
          {/* Refund summary */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="font-bold mb-4">Refund Summary</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Refund Amount</span>
                <span className="font-bold">
                  Rs. {returnRequest.refund_amount?.toLocaleString() || '—'}
                </span>
              </div>
              {returnRequest.refund_method && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Refund Method</span>
                  <span className="capitalize">{returnRequest.refund_method}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Status</span>
                <span className="capitalize">{returnRequest.status.replace(/_/g, ' ')}</span>
              </div>
            </div>

            {returnRequest.refunded_at && (
              <p className="text-sm text-green-600 mt-4">
                Refunded on{' '}
                {new Date(returnRequest.refunded_at).toLocaleDateString()}
              </p>
            )}
          </div>

          {/* Pickup info */}
          {returnRequest.pickup_date && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="font-bold mb-4">Pickup Details</h3>
              <p className="text-sm">
                <span className="text-gray-600">Date: </span>
                {new Date(returnRequest.pickup_date).toLocaleDateString()}
              </p>
              {returnRequest.pickup_slot && (
                <p className="text-sm">
                  <span className="text-gray-600">Slot: </span>
                  {returnRequest.pickup_slot}
                </p>
              )}
            </div>
          )}

          {/* Actions */}
          {(returnRequest.status === 'pending' || returnRequest.status === 'approved') && (
            <button
              onClick={handleCancel}
              className="w-full py-3 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 font-medium"
            >
              Cancel Return
            </button>
          )}

          <button
            onClick={() => router.push('/returns')}
            className="w-full py-3 border rounded-lg hover:bg-gray-50"
          >
            Back to Returns
          </button>
        </div>
      </div>
    </div>
  );
}
