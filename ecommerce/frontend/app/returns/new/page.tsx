'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import toast from 'react-hot-toast';
import { RotateCcw, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';

const returnReasons = [
  { value: 'size_issue', label: 'Size/Fit Issue' },
  { value: 'defective', label: 'Defective/Damaged Product' },
  { value: 'not_as_described', label: 'Not as Described' },
  { value: 'changed_mind', label: 'Changed Mind' },
  { value: 'arrived_late', label: 'Arrived Late' },
  { value: 'damaged_in_shipping', label: 'Damaged in Shipping' },
  { value: 'wrong_item', label: 'Wrong Item Received' },
  { value: 'better_price_elsewhere', label: 'Better Price Elsewhere' },
  { value: 'other', label: 'Other' },
];

export default function NewReturnPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useStore();

  const orderId = searchParams.get('order_id');
  const itemId = searchParams.get('item_id');

  const [order, setOrder] = useState<any>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [reason, setReason] = useState('');
  const [reasonDetails, setReasonDetails] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!orderId) {
      router.push('/orders');
      return;
    }

    async function loadOrder() {
      try {
        const data = await api.getOrder(orderId);
        setOrder(data);

        if (itemId) {
          const item = data.items.find((i: any) => i.id === itemId);
          if (item) {
            setSelectedItem(item);
          }
        }
      } catch (error) {
        console.error('Failed to load order:', error);
        toast.error('Order not found');
        router.push('/orders');
      } finally {
        setLoading(false);
      }
    }
    loadOrder();
  }, [orderId, itemId, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedItem) {
      toast.error('Please select an item to return');
      return;
    }

    if (!reason) {
      toast.error('Please select a reason for return');
      return;
    }

    setSubmitting(true);
    try {
      const returnRequest = await api.createReturn({
        order_id: order.id,
        order_item_id: selectedItem.id,
        reason,
        reason_details: reasonDetails || undefined,
      });

      setResult(returnRequest);
      toast.success('Return request submitted!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit return request');
    } finally {
      setSubmitting(false);
    }
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

  // Show result after submission
  if (result) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="bg-white rounded-lg border p-8 text-center">
          {result.status === 'approved' ? (
            <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
          ) : result.status === 'rejected' ? (
            <XCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
          ) : (
            <Clock className="w-16 h-16 mx-auto text-yellow-500 mb-4" />
          )}

          <h1 className="text-2xl font-bold mb-2">
            {result.status === 'approved'
              ? 'Return Approved!'
              : result.status === 'rejected'
              ? 'Return Denied'
              : 'Return Under Review'}
          </h1>

          <p className="text-gray-600 mb-6">
            Return #{result.return_number}
          </p>

          {/* Score details */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
            <h3 className="font-semibold mb-4">Return Policy Engine Analysis</h3>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Eligibility Score</p>
                <p className="text-2xl font-bold">
                  {result.eligibility_score?.toFixed(0) || 'N/A'}/100
                </p>
              </div>
              <div>
                <p className="text-gray-500">Risk Level</p>
                <p
                  className={`text-2xl font-bold capitalize ${
                    result.risk_level === 'low'
                      ? 'text-green-600'
                      : result.risk_level === 'medium'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}
                >
                  {result.risk_level || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-gray-500">AI Recommendation</p>
                <p className="font-medium">{result.engine_recommendation || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-500">Confidence</p>
                <p className="font-medium">
                  {result.engine_confidence
                    ? `${(result.engine_confidence * 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
              </div>
            </div>

            {result.decision_notes && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-gray-500 text-sm">Decision Notes</p>
                <p>{result.decision_notes}</p>
              </div>
            )}
          </div>

          {/* Next steps */}
          <div className="text-left mb-6">
            <h3 className="font-semibold mb-2">What's Next?</h3>
            {result.status === 'approved' ? (
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• We'll schedule a pickup for your item</li>
                <li>• Refund will be processed after item inspection</li>
                <li>• Expected refund: Rs. {result.refund_amount?.toLocaleString()}</li>
              </ul>
            ) : result.status === 'rejected' ? (
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Your return request was denied based on our policy</li>
                <li>• Contact customer support if you believe this is an error</li>
              </ul>
            ) : (
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Your request is being reviewed by our team</li>
                <li>• You'll receive an update within 24-48 hours</li>
                <li>• Check your email for status updates</li>
              </ul>
            )}
          </div>

          <div className="flex gap-4 justify-center">
            <button
              onClick={() => router.push(`/returns/${result.id}`)}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              View Return Details
            </button>
            <button
              onClick={() => router.push('/orders')}
              className="px-6 py-3 border rounded-lg hover:bg-gray-50"
            >
              Back to Orders
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">Request a Return</h1>

      {/* Info about AI scoring */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">AI-Powered Return Processing</p>
            <p>
              Your return request will be evaluated by our intelligent system based on your
              shopping history, product details, and return reason. Good customers typically
              get instant approvals!
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Select item */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="font-bold mb-4">Select Item to Return</h2>

          <div className="space-y-3">
            {order?.items
              .filter((item: any) => item.can_return && !item.is_returned)
              .map((item: any) => (
                <label
                  key={item.id}
                  className={`flex items-center gap-4 p-4 border rounded-lg cursor-pointer ${
                    selectedItem?.id === item.id
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-gray-400'
                  }`}
                >
                  <input
                    type="radio"
                    name="item"
                    checked={selectedItem?.id === item.id}
                    onChange={() => setSelectedItem(item)}
                    className="sr-only"
                  />
                  <div className="relative w-16 h-16 bg-gray-100 rounded flex-shrink-0">
                    {item.product_image && (
                      <Image
                        src={item.product_image}
                        alt=""
                        fill
                        className="object-cover rounded"
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{item.product_name}</p>
                    <p className="text-sm text-gray-600">
                      Qty: {item.quantity} × Rs. {item.unit_price.toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">Rs. {item.total_price.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">
                      Return by {new Date(
                        new Date(order.delivered_at).getTime() +
                          item.return_window_days * 24 * 60 * 60 * 1000
                      ).toLocaleDateString()}
                    </p>
                  </div>
                </label>
              ))}
          </div>

          {order?.items.filter((i: any) => i.can_return && !i.is_returned).length === 0 && (
            <p className="text-gray-500">No items eligible for return</p>
          )}
        </div>

        {/* Return reason */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="font-bold mb-4">Reason for Return</h2>

          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 mb-4"
            required
          >
            <option value="">Select a reason</option>
            {returnReasons.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>

          <textarea
            placeholder="Additional details (optional)"
            value={reasonDetails}
            onChange={(e) => setReasonDetails(e.target.value)}
            rows={3}
            className="w-full border rounded-lg px-4 py-2"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={submitting || !selectedItem || !reason}
          className="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-5 h-5" />
          {submitting ? 'Processing...' : 'Submit Return Request'}
        </button>
      </form>
    </div>
  );
}
