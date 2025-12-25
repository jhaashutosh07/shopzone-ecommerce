'use client';

import { useStore } from '@/lib/store';
import Image from 'next/image';
import Link from 'next/link';
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CartPage() {
  const { cart, updateCartItem, removeFromCart, isAuthenticated } = useStore();

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <ShoppingBag className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Your cart is empty</h1>
        <p className="text-gray-600 mb-4">Please login to view your cart</p>
        <Link
          href="/login"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Login
        </Link>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <ShoppingBag className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Your cart is empty</h1>
        <p className="text-gray-600 mb-4">Add some products to get started</p>
        <Link
          href="/products"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  const handleUpdateQuantity = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      await updateCartItem(itemId, newQuantity);
    } catch (error: any) {
      toast.error(error.message || 'Failed to update quantity');
    }
  };

  const handleRemove = async (itemId: string) => {
    try {
      await removeFromCart(itemId);
      toast.success('Item removed from cart');
    } catch (error: any) {
      toast.error(error.message || 'Failed to remove item');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">Shopping Cart ({cart.total_items} items)</h1>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Cart items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.items.map((item) => (
            <div key={item.id} className="bg-white rounded-lg border p-4 flex gap-4">
              <div className="relative w-24 h-24 flex-shrink-0">
                <Image
                  src={item.product_image}
                  alt={item.product_name}
                  fill
                  className="object-cover rounded-lg"
                />
              </div>

              <div className="flex-1">
                <h3 className="font-medium">{item.product_name}</h3>
                <p className="text-lg font-bold mt-1">Rs. {item.unit_price.toLocaleString()}</p>

                {!item.product_in_stock && (
                  <p className="text-red-600 text-sm">Out of stock</p>
                )}

                <div className="flex items-center justify-between mt-3">
                  <div className="flex items-center border rounded-lg">
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                      className="p-2 hover:bg-gray-100"
                      disabled={item.quantity <= 1}
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="px-3">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                      className="p-2 hover:bg-gray-100"
                      disabled={item.quantity >= item.product_stock_quantity}
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-red-600 hover:text-red-700 p-2"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="text-right">
                <p className="font-bold">Rs. {item.total_price.toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Order summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border p-6 sticky top-24">
            <h2 className="text-lg font-bold mb-4">Order Summary</h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span>Rs. {cart.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tax (18% GST)</span>
                <span>Rs. {cart.tax.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className={cart.subtotal >= 999 ? 'text-green-600' : ''}>
                  {cart.subtotal >= 999 ? 'FREE' : 'Rs. 49'}
                </span>
              </div>
              <hr />
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>Rs. {(cart.total + (cart.subtotal < 999 ? 49 : 0)).toLocaleString()}</span>
              </div>
            </div>

            <Link
              href="/checkout"
              className="block w-full mt-6 py-3 bg-primary-600 text-white text-center rounded-lg hover:bg-primary-700 font-semibold"
            >
              Proceed to Checkout
            </Link>

            <Link
              href="/products"
              className="block w-full mt-3 py-3 border text-center rounded-lg hover:bg-gray-50"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
