'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import toast from 'react-hot-toast';
import {
  Package,
  Truck,
  CheckCircle,
  XCircle,
  MapPin,
  Phone,
  RotateCcw,
  Copy,
} from 'lucide-react';

const statusSteps = [
  { key: 'confirmed', label: 'Confirmed', icon: CheckCircle },
  { key: 'processing', label: 'Processing', icon: Package },
  { key: 'shipped', label: 'Shipped', icon: Truck },
  { key: 'delivered', label: 'Delivered', icon: CheckCircle },
];

export default function OrderDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useStore();
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    async function loadOrder() {
      try {
        const data = await api.getOrder(id as string);
        setOrder(data);
      } catch (error) {
        console.error('Failed to load order:', error);
        toast.error('Order not found');
        router.push('/orders');
      } finally {
        setLoading(false);
      }
    }
    loadOrder();
  }, [id, isAuthenticated, router]);

  const handleCancelOrder = async () => {
    if (!confirm('Are you sure you want to cancel this order?')) return;

    setCancelling(true);
    try {
      const updated = await api.cancelOrder(order.id);
      setOrder(updated);
      toast.success('Order cancelled successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel order');
    } finally {
      setCancelling(false);
    }
  };

  const getCurrentStep = () => {
    const statusIndex = statusSteps.findIndex((s) => s.key === order?.status);
    return statusIndex >= 0 ? statusIndex : -1;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 w-1/3 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!order) return null;

  const currentStep = getCurrentStep();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Order #{order.order_number}</h1>
          <p className="text-gray-600">
            Placed on{' '}
            {new Date(order.created_at).toLocaleDateString('en-IN', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </p>
        </div>
        <button
          onClick={() => {
            navigator.clipboard.writeText(order.order_number);
            toast.success('Order number copied!');
          }}
          className="flex items-center gap-1 text-gray-600 hover:text-gray-800"
        >
          <Copy className="w-4 h-4" />
          Copy
        </button>
      </div>

      {/* Status tracker */}
      {order.status !== 'cancelled' && order.status !== 'returned' && (
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
                      className={`text-sm mt-2 ${
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

      {/* Cancelled status */}
      {order.status === 'cancelled' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-3">
          <XCircle className="w-6 h-6 text-red-600" />
          <div>
            <p className="font-medium text-red-800">Order Cancelled</p>
            <p className="text-sm text-red-600">
              This order was cancelled on{' '}
              {new Date(order.cancelled_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Order items */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b">
              <h2 className="font-bold">Order Items</h2>
            </div>
            <div className="divide-y">
              {order.items.map((item: any) => (
                <div key={item.id} className="p-4 flex gap-4">
                  <div className="relative w-20 h-20 bg-gray-100 rounded-lg flex-shrink-0">
                    {item.product_image && (
                      <Image
                        src={item.product_image}
                        alt={item.product_name}
                        fill
                        className="object-cover rounded-lg"
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <Link
                      href={`/products/${item.product_id}`}
                      className="font-medium hover:text-primary-600"
                    >
                      {item.product_name}
                    </Link>
                    <p className="text-sm text-gray-600">
                      Qty: {item.quantity} × Rs. {item.unit_price.toLocaleString()}
                    </p>
                    <p className="font-medium mt-1">
                      Rs. {item.total_price.toLocaleString()}
                    </p>

                    {/* Return button */}
                    {item.can_return && !item.is_returned && (
                      <Link
                        href={`/returns/new?order_id=${order.id}&item_id=${item.id}`}
                        className="inline-flex items-center gap-1 mt-2 text-sm text-primary-600 hover:text-primary-700"
                      >
                        <RotateCcw className="w-4 h-4" />
                        Return Item
                      </Link>
                    )}
                    {item.is_returned && (
                      <span className="inline-block mt-2 text-sm text-gray-500">
                        Returned
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Order summary and shipping */}
        <div className="space-y-6">
          {/* Payment summary */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3">Payment Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span>Rs. {order.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tax</span>
                <span>Rs. {order.tax.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span>
                  {order.shipping_fee === 0 ? 'FREE' : `Rs. ${order.shipping_fee}`}
                </span>
              </div>
              {order.discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount</span>
                  <span>-Rs. {order.discount.toLocaleString()}</span>
                </div>
              )}
              <hr className="my-2" />
              <div className="flex justify-between font-bold text-base">
                <span>Total</span>
                <span>Rs. {order.total.toLocaleString()}</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t text-sm">
              <p className="text-gray-600">Payment Method</p>
              <p className="font-medium capitalize">{order.payment_method}</p>
            </div>
          </div>

          {/* Shipping address */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-bold mb-3">Shipping Address</h3>
            <div className="text-sm space-y-1">
              <p className="font-medium">{order.shipping_name}</p>
              <p className="text-gray-600">{order.shipping_address}</p>
              <p className="text-gray-600">
                {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}
              </p>
              <p className="flex items-center gap-1 text-gray-600 mt-2">
                <Phone className="w-4 h-4" />
                {order.shipping_phone}
              </p>
            </div>
          </div>

          {/* Tracking */}
          {order.tracking_number && (
            <div className="bg-white rounded-lg border p-4">
              <h3 className="font-bold mb-3">Tracking</h3>
              <p className="text-sm text-gray-600">
                Carrier: <span className="font-medium">{order.carrier}</span>
              </p>
              <p className="text-sm text-gray-600">
                Tracking: <span className="font-medium">{order.tracking_number}</span>
              </p>
            </div>
          )}

          {/* Actions */}
          {order.can_cancel && (
            <button
              onClick={handleCancelOrder}
              disabled={cancelling}
              className="w-full py-3 border border-red-600 text-red-600 rounded-lg hover:bg-red-50 font-medium disabled:opacity-50"
            >
              {cancelling ? 'Cancelling...' : 'Cancel Order'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
