'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import ProductCard from '@/components/ProductCard';
import Link from 'next/link';
import { ArrowRight, Truck, Shield, RotateCcw, Headphones } from 'lucide-react';

export default function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState<any[]>([]);
  const [deals, setDeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [featured, dealsData] = await Promise.all([
          api.getFeaturedProducts(),
          api.getDeals(),
        ]);
        setFeaturedProducts(featured);
        setDeals(dealsData);
      } catch (error) {
        console.error('Failed to load products:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div>
      {/* Hero Banner */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Shop Smart with Intelligent Returns
            </h1>
            <p className="text-xl mb-8 text-primary-100">
              Experience hassle-free shopping with our AI-powered return policy engine.
              Get instant return decisions based on your shopping history.
            </p>
            <div className="flex gap-4">
              <Link
                href="/products"
                className="px-6 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Shop Now
              </Link>
              <Link
                href="/return-policy"
                className="px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-colors"
              >
                Learn About Returns
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-8 border-b">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="flex items-center gap-3">
              <Truck className="w-10 h-10 text-primary-600" />
              <div>
                <h3 className="font-semibold">Free Shipping</h3>
                <p className="text-sm text-gray-600">On orders over Rs. 500</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <RotateCcw className="w-10 h-10 text-primary-600" />
              <div>
                <h3 className="font-semibold">Easy Returns</h3>
                <p className="text-sm text-gray-600">30-day return policy</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Shield className="w-10 h-10 text-primary-600" />
              <div>
                <h3 className="font-semibold">Secure Payment</h3>
                <p className="text-sm text-gray-600">100% secure checkout</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Headphones className="w-10 h-10 text-primary-600" />
              <div>
                <h3 className="font-semibold">24/7 Support</h3>
                <p className="text-sm text-gray-600">Dedicated support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold">Featured Products</h2>
            <Link
              href="/products"
              className="text-primary-600 hover:text-primary-700 flex items-center gap-1"
            >
              View All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 aspect-square rounded-lg mb-4"></div>
                  <div className="bg-gray-200 h-4 rounded mb-2"></div>
                  <div className="bg-gray-200 h-4 w-2/3 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {featuredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Deals Section */}
      {deals.length > 0 && (
        <section className="py-12 bg-red-50">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-red-600">Today's Deals</h2>
                <p className="text-gray-600">Limited time offers</p>
              </div>
              <Link
                href="/products/deals"
                className="text-red-600 hover:text-red-700 flex items-center gap-1"
              >
                View All Deals <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {deals.slice(0, 5).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Categories */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-8">Shop by Category</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: 'Clothing', icon: '👕', slug: 'clothing' },
              { name: 'Electronics', icon: '📱', slug: 'electronics' },
              { name: 'Home', icon: '🏠', slug: 'home' },
              { name: 'Beauty', icon: '💄', slug: 'beauty' },
              { name: 'Sports', icon: '⚽', slug: 'sports' },
              { name: 'Toys', icon: '🎮', slug: 'toys' },
            ].map((category) => (
              <Link
                key={category.slug}
                href={`/products?category=${category.slug}`}
                className="bg-white rounded-lg p-6 text-center border hover:shadow-md transition-shadow"
              >
                <span className="text-4xl mb-2 block">{category.icon}</span>
                <span className="font-medium">{category.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Return Policy Highlight */}
      <section className="py-12 bg-primary-50">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl font-bold mb-4">
              AI-Powered Return Policy Engine
            </h2>
            <p className="text-gray-600 mb-6">
              Our intelligent return system uses machine learning to provide instant return decisions.
              Good customers get auto-approved returns, while suspicious patterns are flagged for review.
              This helps us offer better prices while protecting against fraud.
            </p>
            <div className="flex justify-center gap-8 text-sm">
              <div>
                <div className="text-3xl font-bold text-primary-600">30</div>
                <div className="text-gray-600">Day Return Window</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary-600">Instant</div>
                <div className="text-gray-600">Return Decisions</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary-600">Free</div>
                <div className="text-gray-600">Return Pickup</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
