'use client';

import Link from 'next/link';
import { useStore } from '@/lib/store';
import { ShoppingCart, User, Heart, Search, Menu, Package, RotateCcw } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Header() {
  const { user, cart, isAuthenticated, logout } = useStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/products?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      {/* Top bar */}
      <div className="bg-primary-600 text-white text-sm py-1">
        <div className="container mx-auto px-4 text-center">
          Free shipping on orders over Rs. 500 | Easy 30-day returns
        </div>
      </div>

      {/* Main header */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="text-2xl font-bold text-primary-600">
            ShopZone
          </Link>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-xl">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-4 pr-12 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-500 hover:text-primary-600"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
          </form>

          {/* Right section */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                {/* Wishlist */}
                <Link href="/wishlist" className="p-2 text-gray-600 hover:text-primary-600">
                  <Heart className="w-6 h-6" />
                </Link>

                {/* Cart */}
                <Link href="/cart" className="p-2 text-gray-600 hover:text-primary-600 relative">
                  <ShoppingCart className="w-6 h-6" />
                  {cart && cart.total_items > 0 && (
                    <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {cart.total_items}
                    </span>
                  )}
                </Link>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center gap-2 p-2 text-gray-600 hover:text-primary-600"
                  >
                    <User className="w-6 h-6" />
                    <span className="hidden md:inline text-sm">{user?.full_name}</span>
                  </button>

                  {showUserMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border py-2">
                      <Link
                        href="/account"
                        className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <User className="w-4 h-4 inline mr-2" />
                        My Account
                      </Link>
                      <Link
                        href="/orders"
                        className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <Package className="w-4 h-4 inline mr-2" />
                        My Orders
                      </Link>
                      <Link
                        href="/returns"
                        className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <RotateCcw className="w-4 h-4 inline mr-2" />
                        My Returns
                      </Link>
                      <hr className="my-2" />
                      <button
                        onClick={() => {
                          logout();
                          setShowUserMenu(false);
                          router.push('/');
                        }}
                        className="block w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100"
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-4 py-2 text-gray-600 hover:text-primary-600"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Category nav */}
      <nav className="border-t">
        <div className="container mx-auto px-4">
          <ul className="flex items-center gap-6 py-3 text-sm overflow-x-auto">
            <li>
              <Link href="/products?category=clothing" className="text-gray-600 hover:text-primary-600 whitespace-nowrap">
                Clothing
              </Link>
            </li>
            <li>
              <Link href="/products?category=electronics" className="text-gray-600 hover:text-primary-600 whitespace-nowrap">
                Electronics
              </Link>
            </li>
            <li>
              <Link href="/products?category=home" className="text-gray-600 hover:text-primary-600 whitespace-nowrap">
                Home & Living
              </Link>
            </li>
            <li>
              <Link href="/products?category=beauty" className="text-gray-600 hover:text-primary-600 whitespace-nowrap">
                Beauty
              </Link>
            </li>
            <li>
              <Link href="/products?category=sports" className="text-gray-600 hover:text-primary-600 whitespace-nowrap">
                Sports
              </Link>
            </li>
            <li>
              <Link href="/products/deals" className="text-red-600 font-medium whitespace-nowrap">
                Deals
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  );
}
