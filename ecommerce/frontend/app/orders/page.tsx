'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Package, ChevronRight } from 'lucide-react';

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  processing: 'bg-blue-100 text-blue-800',
  shipped: 'bg-purple-100 text-purple-800',
  out_for_delivery: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  returned: 'bg-gray-100 text-gray-800',
};

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated } = useStore();
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/orders');
      return;
    }

    async function loadOrders() {
      try {
        const data = await api.getOrders();
        setOrders(data);
      } catch (error) {
        console.error('Failed to load orders:', error);
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-8">My Orders</h1>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">No orders yet</h1>
        <p className="text-gray-600 mb-4">Start shopping to see your orders here</p>
        <Link
          href="/products"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Shop Now
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">My Orders</h1>

      <div className="space-y-4">
        {orders.map((order) => (
          <Link
            key={order.id}
            href={`/orders/${order.id}`}
            className="block bg-white rounded-lg border hover:shadow-md transition-shadow"
          >
            <div className="p-4 flex items-center gap-4">
              {/* Order image */}
              <div className="relative w-20 h-20 flex-shrink-0 bg-gray-100 rounded-lg">
                {order.first_item_image ? (
                  <Image
                    src={order.first_item_image}
                    alt=""
                    fill
                    className="object-cover rounded-lg"
                  />
                ) : (
                  <Package className="w-8 h-8 absolute inset-0 m-auto text-gray-400" />
                )}
              </div>

              {/* Order details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Order #{order.order_number}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${statusColors[order.status]}`}>
                    {order.status.replace(/_/g, ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-600 truncate">
                  {order.first_item_name}
                  {order.item_count > 1 && ` +${order.item_count - 1} more`}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(order.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </p>
              </div>

              {/* Price and arrow */}
              <div className="text-right flex items-center gap-2">
                <div>
                  <p className="font-bold">Rs. {order.total.toLocaleString()}</p>
                  <p className="text-sm text-gray-500">{order.item_count} items</p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
