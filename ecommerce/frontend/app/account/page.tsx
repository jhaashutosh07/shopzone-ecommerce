'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { User, Package, RotateCcw, MapPin, LogOut, Edit2, Save } from 'lucide-react';

export default function AccountPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, checkAuth } = useStore();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [addresses, setAddresses] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        phone: '',
      });
    }
    loadAddresses();
  }, [isAuthenticated, user, router]);

  const loadAddresses = async () => {
    try {
      const data = await api.getAddresses();
      setAddresses(data);
    } catch (error) {
      console.error('Failed to load addresses:', error);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
    toast.success('Logged out successfully');
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">My Account</h1>

      <div className="grid lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <p className="font-medium">{user.full_name}</p>
                <p className="text-sm text-gray-500">{user.email}</p>
              </div>
            </div>

            <nav className="space-y-2">
              <a href="/orders" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <Package className="w-5 h-5 text-gray-500" />
                <span>My Orders</span>
              </a>
              <a href="/returns" className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <RotateCcw className="w-5 h-5 text-gray-500" />
                <span>Returns</span>
              </a>
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-red-50 text-red-600 w-full"
              >
                <LogOut className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Profile Section */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Profile Information</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <p className="p-2 bg-gray-50 rounded">{user.full_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <p className="p-2 bg-gray-50 rounded">{user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                <p className="p-2 bg-gray-50 rounded capitalize">{user.role}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Member Since</label>
                <p className="p-2 bg-gray-50 rounded">2024</p>
              </div>
            </div>
          </div>

          {/* Stats Section */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">Account Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-primary-600">{user.total_orders || 0}</p>
                <p className="text-sm text-gray-500">Total Orders</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{user.total_returns || 0}</p>
                <p className="text-sm text-gray-500">Returns</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{((user.return_rate || 0) * 100).toFixed(1)}%</p>
                <p className="text-sm text-gray-500">Return Rate</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">Good</p>
                <p className="text-sm text-gray-500">Trust Score</p>
              </div>
            </div>
          </div>

          {/* Addresses Section */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Saved Addresses</h2>
            </div>

            {addresses.length === 0 ? (
              <p className="text-gray-500">No saved addresses. Add one during checkout.</p>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {addresses.map((addr: any) => (
                  <div key={addr.id} className="p-4 border rounded-lg">
                    <div className="flex items-start gap-2">
                      <MapPin className="w-5 h-5 text-gray-400 mt-1" />
                      <div>
                        <p className="font-medium">{addr.full_name}</p>
                        <p className="text-sm text-gray-600">{addr.address_line1}</p>
                        {addr.address_line2 && <p className="text-sm text-gray-600">{addr.address_line2}</p>}
                        <p className="text-sm text-gray-600">
                          {addr.city}, {addr.state} {addr.postal_code}
                        </p>
                        <p className="text-sm text-gray-600">{addr.phone}</p>
                        {addr.is_default && (
                          <span className="inline-block mt-2 text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                            Default
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
