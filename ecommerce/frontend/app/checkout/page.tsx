'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { CreditCard, Wallet, Building, Plus } from 'lucide-react';

export default function CheckoutPage() {
  const router = useRouter();
  const { cart, isAuthenticated, clearCart } = useStore();
  const [addresses, setAddresses] = useState<any[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<string>('');
  const [paymentMethod, setPaymentMethod] = useState('cod');
  const [loading, setLoading] = useState(true);
  const [placing, setPlacing] = useState(false);
  const [showAddAddress, setShowAddAddress] = useState(false);
  const [newAddress, setNewAddress] = useState({
    full_name: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    address_type: 'home',
    is_default: false,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/checkout');
      return;
    }

    async function loadAddresses() {
      try {
        const data = await api.getAddresses();
        setAddresses(data);
        if (data.length > 0) {
          const defaultAddr = data.find((a: any) => a.is_default) || data[0];
          setSelectedAddress(defaultAddr.id);
        }
      } catch (error) {
        console.error('Failed to load addresses:', error);
      } finally {
        setLoading(false);
      }
    }
    loadAddresses();
  }, [isAuthenticated, router]);

  const handleAddAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const addr = await api.addAddress(newAddress);
      setAddresses([...addresses, addr]);
      setSelectedAddress(addr.id);
      setShowAddAddress(false);
      toast.success('Address added');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add address');
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddress) {
      toast.error('Please select a delivery address');
      return;
    }

    setPlacing(true);
    try {
      const order = await api.createOrder(selectedAddress, paymentMethod);
      toast.success('Order placed successfully!');
      router.push(`/orders/${order.id}`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to place order');
    } finally {
      setPlacing(false);
    }
  };

  if (!isAuthenticated || !cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Your cart is empty</h1>
        <button
          onClick={() => router.push('/products')}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg"
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  const shipping = cart.subtotal >= 500 ? 0 : 40;
  const total = cart.total + shipping;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">Checkout</h1>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Delivery Address */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-bold mb-4">Delivery Address</h2>

            {loading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-20 bg-gray-200 rounded"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            ) : addresses.length === 0 ? (
              <p className="text-gray-600 mb-4">No addresses saved. Add one to continue.</p>
            ) : (
              <div className="space-y-3">
                {addresses.map((addr) => (
                  <label
                    key={addr.id}
                    className={`block p-4 border rounded-lg cursor-pointer ${
                      selectedAddress === addr.id
                        ? 'border-primary-600 bg-primary-50'
                        : 'hover:border-gray-400'
                    }`}
                  >
                    <input
                      type="radio"
                      name="address"
                      value={addr.id}
                      checked={selectedAddress === addr.id}
                      onChange={() => setSelectedAddress(addr.id)}
                      className="sr-only"
                    />
                    <div className="flex justify-between">
                      <div>
                        <p className="font-medium">{addr.full_name}</p>
                        <p className="text-sm text-gray-600">{addr.full_address}</p>
                        <p className="text-sm text-gray-600">{addr.phone}</p>
                      </div>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded h-fit">
                        {addr.address_type}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            )}

            <button
              onClick={() => setShowAddAddress(!showAddAddress)}
              className="mt-4 flex items-center gap-2 text-primary-600 hover:text-primary-700"
            >
              <Plus className="w-4 h-4" />
              Add New Address
            </button>

            {showAddAddress && (
              <form onSubmit={handleAddAddress} className="mt-4 border-t pt-4 space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Full Name"
                    value={newAddress.full_name}
                    onChange={(e) => setNewAddress({ ...newAddress, full_name: e.target.value })}
                    className="border rounded-lg px-4 py-2"
                    required
                  />
                  <input
                    type="tel"
                    placeholder="Phone Number"
                    value={newAddress.phone}
                    onChange={(e) => setNewAddress({ ...newAddress, phone: e.target.value })}
                    className="border rounded-lg px-4 py-2"
                    required
                  />
                </div>
                <input
                  type="text"
                  placeholder="Address Line 1"
                  value={newAddress.address_line1}
                  onChange={(e) => setNewAddress({ ...newAddress, address_line1: e.target.value })}
                  className="w-full border rounded-lg px-4 py-2"
                  required
                />
                <input
                  type="text"
                  placeholder="Address Line 2 (Optional)"
                  value={newAddress.address_line2}
                  onChange={(e) => setNewAddress({ ...newAddress, address_line2: e.target.value })}
                  className="w-full border rounded-lg px-4 py-2"
                />
                <div className="grid md:grid-cols-3 gap-4">
                  <input
                    type="text"
                    placeholder="City"
                    value={newAddress.city}
                    onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
                    className="border rounded-lg px-4 py-2"
                    required
                  />
                  <input
                    type="text"
                    placeholder="State"
                    value={newAddress.state}
                    onChange={(e) => setNewAddress({ ...newAddress, state: e.target.value })}
                    className="border rounded-lg px-4 py-2"
                    required
                  />
                  <input
                    type="text"
                    placeholder="PIN Code"
                    value={newAddress.postal_code}
                    onChange={(e) => setNewAddress({ ...newAddress, postal_code: e.target.value })}
                    className="border rounded-lg px-4 py-2"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save Address
                </button>
              </form>
            )}
          </div>

          {/* Payment Method */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-bold mb-4">Payment Method</h2>
            <div className="space-y-3">
              <label
                className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer ${
                  paymentMethod === 'cod' ? 'border-primary-600 bg-primary-50' : 'hover:border-gray-400'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  value="cod"
                  checked={paymentMethod === 'cod'}
                  onChange={() => setPaymentMethod('cod')}
                />
                <Wallet className="w-5 h-5" />
                <div>
                  <p className="font-medium">Cash on Delivery</p>
                  <p className="text-sm text-gray-600">Pay when you receive</p>
                </div>
              </label>

              <label
                className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer ${
                  paymentMethod === 'card' ? 'border-primary-600 bg-primary-50' : 'hover:border-gray-400'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={() => setPaymentMethod('card')}
                />
                <CreditCard className="w-5 h-5" />
                <div>
                  <p className="font-medium">Credit/Debit Card</p>
                  <p className="text-sm text-gray-600">Visa, Mastercard, Rupay</p>
                </div>
              </label>

              <label
                className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer ${
                  paymentMethod === 'upi' ? 'border-primary-600 bg-primary-50' : 'hover:border-gray-400'
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  value="upi"
                  checked={paymentMethod === 'upi'}
                  onChange={() => setPaymentMethod('upi')}
                />
                <Building className="w-5 h-5" />
                <div>
                  <p className="font-medium">UPI</p>
                  <p className="text-sm text-gray-600">GPay, PhonePe, Paytm</p>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border p-6 sticky top-24">
            <h2 className="text-lg font-bold mb-4">Order Summary</h2>

            <div className="space-y-3 mb-4">
              {cart.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-600">
                    {item.product_name} x {item.quantity}
                  </span>
                  <span>Rs. {item.total_price.toLocaleString()}</span>
                </div>
              ))}
            </div>

            <hr className="my-4" />

            <div className="space-y-2 text-sm">
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
                <span className={shipping === 0 ? 'text-green-600' : ''}>
                  {shipping === 0 ? 'FREE' : `Rs. ${shipping}`}
                </span>
              </div>
            </div>

            <hr className="my-4" />

            <div className="flex justify-between text-lg font-bold">
              <span>Total</span>
              <span>Rs. {total.toLocaleString()}</span>
            </div>

            <button
              onClick={handlePlaceOrder}
              disabled={placing || !selectedAddress}
              className="w-full mt-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {placing ? 'Placing Order...' : 'Place Order'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
