'use client';

import Link from 'next/link';
import { useStore } from '@/lib/store';
import {
  ShoppingCart,
  User,
  Heart,
  Search,
  Package,
  RotateCcw,
  ShieldCheck,
  ChevronDown,
  LogOut,
  Sparkles,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

const CATEGORIES = [
  { label: 'Electronics', value: 'electronics' },
  { label: 'Fashion', value: 'clothing' },
  { label: 'Beauty', value: 'beauty' },
  { label: 'Home & Living', value: 'home' },
  { label: 'Jewelry & Watches', value: 'jewelry' },
  { label: 'Sports', value: 'sports' },
  { label: 'Grocery', value: 'grocery' },
  { label: 'Automotive', value: 'automotive' },
];

export default function Header() {
  const { user, cart, isAuthenticated, logout } = useStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const close = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/products?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="sticky top-0 z-50">
      {/* Announcement bar */}
      <div className="bg-slate-900 py-1.5 text-center text-xs font-medium text-slate-200">
        <span className="inline-flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          AI-verified returns — instant decisions, full transparency · Free shipping over ₹999
        </span>
      </div>

      {/* Main header */}
      <div className="border-b border-slate-200/70 bg-white/85 backdrop-blur-lg">
        <div className="container-page flex h-16 items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-glow">
              <Sparkles className="h-5 w-5" />
            </span>
            <span className="font-display text-xl font-extrabold tracking-tight text-slate-900">
              Shop<span className="text-primary-600">Zone</span>
            </span>
          </Link>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="hidden flex-1 max-w-xl sm:block">
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search products, brands…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-full border border-slate-200 bg-slate-50 py-2.5 pl-11 pr-24 text-sm outline-none transition focus:border-primary-400 focus:bg-white focus:ring-4 focus:ring-primary-100"
              />
              <button
                type="submit"
                className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full bg-primary-600 px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-primary-700"
              >
                Search
              </button>
            </div>
          </form>

          {/* Right section */}
          <div className="flex items-center gap-1">
            {isAuthenticated ? (
              <>
                <Link
                  href="/wishlist"
                  className="rounded-xl p-2.5 text-slate-600 transition hover:bg-slate-100 hover:text-primary-600"
                  aria-label="Wishlist"
                >
                  <Heart className="h-5 w-5" />
                </Link>

                <Link
                  href="/cart"
                  className="relative rounded-xl p-2.5 text-slate-600 transition hover:bg-slate-100 hover:text-primary-600"
                  aria-label="Cart"
                >
                  <ShoppingCart className="h-5 w-5" />
                  {cart && cart.total_items > 0 && (
                    <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow">
                      {cart.total_items}
                    </span>
                  )}
                </Link>

                <div className="relative" ref={menuRef}>
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center gap-1.5 rounded-xl p-2 pl-2.5 text-slate-700 transition hover:bg-slate-100"
                  >
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                      {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                    <span className="hidden max-w-[110px] truncate text-sm font-medium md:inline">
                      {user?.full_name?.split(' ')[0]}
                    </span>
                    <ChevronDown className="hidden h-4 w-4 text-slate-400 md:block" />
                  </button>

                  {showUserMenu && (
                    <div className="absolute right-0 mt-2 w-56 overflow-hidden rounded-2xl border border-slate-100 bg-white py-2 shadow-xl">
                      <div className="border-b border-slate-100 px-4 py-2.5">
                        <p className="truncate text-sm font-semibold text-slate-900">{user?.full_name}</p>
                        <p className="truncate text-xs text-slate-500">{user?.email}</p>
                      </div>
                      {[
                        { href: '/account', icon: User, label: 'My Account' },
                        { href: '/orders', icon: Package, label: 'My Orders' },
                        { href: '/returns', icon: RotateCcw, label: 'My Returns' },
                      ].map((item) => (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50 hover:text-primary-700"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <item.icon className="h-4 w-4 text-slate-400" />
                          {item.label}
                        </Link>
                      ))}
                      <button
                        onClick={() => {
                          logout();
                          setShowUserMenu(false);
                          router.push('/');
                        }}
                        className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-rose-600 transition hover:bg-rose-50"
                      >
                        <LogOut className="h-4 w-4" />
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
                  className="rounded-xl px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                >
                  Login
                </Link>
                <Link href="/register" className="btn-primary !py-2 text-sm">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Mobile search */}
        <form onSubmit={handleSearch} className="container-page pb-3 sm:hidden">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search products, brands…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-full border border-slate-200 bg-slate-50 py-2.5 pl-11 pr-4 text-sm outline-none focus:border-primary-400 focus:bg-white"
            />
          </div>
        </form>

        {/* Category nav */}
        <nav className="border-t border-slate-100">
          <div className="container-page">
            <ul className="no-scrollbar flex items-center gap-1 overflow-x-auto py-1.5 text-sm">
              {CATEGORIES.map((cat) => (
                <li key={cat.value}>
                  <Link
                    href={`/products?category=${cat.value}`}
                    className="whitespace-nowrap rounded-lg px-3 py-1.5 font-medium text-slate-600 transition hover:bg-primary-50 hover:text-primary-700"
                  >
                    {cat.label}
                  </Link>
                </li>
              ))}
              <li>
                <Link
                  href="/products"
                  className="whitespace-nowrap rounded-lg px-3 py-1.5 font-semibold text-primary-600 transition hover:bg-primary-50"
                >
                  All Products →
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </div>
    </header>
  );
}
