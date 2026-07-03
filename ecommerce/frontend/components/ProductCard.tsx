'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Heart, ShoppingCart, Zap } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { useState } from 'react';
import Stars from '@/components/Stars';

export interface ProductCardData {
  id: string;
  name: string;
  slug: string;
  brand?: string | null;
  category?: string;
  price: number;
  compare_at_price?: number | null;
  discount_percentage: number;
  avg_rating: number;
  review_count: number;
  in_stock: boolean;
  primary_image: string;
  hover_image?: string | null;
  total_sold?: number;
}

export function ProductCardSkeleton() {
  return (
    <div className="card overflow-hidden">
      <div className="skeleton aspect-square rounded-none" />
      <div className="space-y-2 p-4">
        <div className="skeleton h-3 w-1/3" />
        <div className="skeleton h-4 w-full" />
        <div className="skeleton h-4 w-2/3" />
        <div className="skeleton h-6 w-1/2" />
      </div>
    </div>
  );
}

export default function ProductCard({ product }: { product: ProductCardData }) {
  const { addToCart, isAuthenticated } = useStore();
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [adding, setAdding] = useState(false);

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }
    setAdding(true);
    try {
      await addToCart(product.id);
      toast.success('Added to cart');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add to cart');
    } finally {
      setAdding(false);
    }
  };

  const handleWishlist = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      toast.error('Please login to add to wishlist');
      return;
    }
    try {
      if (isWishlisted) {
        await api.removeFromWishlist(product.id);
        setIsWishlisted(false);
      } else {
        await api.addToWishlist(product.id);
        setIsWishlisted(true);
        toast.success('Added to wishlist');
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to update wishlist');
    }
  };

  return (
    <Link href={`/products/${product.slug}`} className="group block">
      <div className="card overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-card-hover">
        {/* Image */}
        <div className="relative aspect-square overflow-hidden bg-slate-50">
          <Image
            src={product.primary_image}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className={`object-contain p-2 transition-all duration-500 ${
              product.hover_image ? 'group-hover:opacity-0' : 'group-hover:scale-105'
            }`}
          />
          {product.hover_image && (
            <Image
              src={product.hover_image}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
              className="object-contain p-2 opacity-0 transition-all duration-500 group-hover:scale-105 group-hover:opacity-100"
            />
          )}

          {/* Badges */}
          <div className="absolute left-3 top-3 flex flex-col gap-1.5">
            {product.discount_percentage > 0 && (
              <span className="chip bg-rose-500 text-white shadow-sm">
                −{product.discount_percentage}%
              </span>
            )}
            {(product.total_sold ?? 0) > 500 && (
              <span className="chip bg-accent-100 text-accent-700">
                <Zap className="h-3 w-3" /> Bestseller
              </span>
            )}
          </div>

          {!product.in_stock && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-[2px]">
              <span className="chip bg-white font-semibold text-slate-900">Out of stock</span>
            </div>
          )}

          <button
            aria-label="Add to wishlist"
            className={`absolute right-3 top-3 rounded-full bg-white/90 p-2 shadow-sm backdrop-blur transition-all hover:scale-110 ${
              isWishlisted ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
            }`}
            onClick={handleWishlist}
          >
            <Heart className={`h-4 w-4 ${isWishlisted ? 'fill-rose-500 text-rose-500' : 'text-slate-600'}`} />
          </button>

          {/* Quick add */}
          {product.in_stock && (
            <button
              onClick={handleAddToCart}
              disabled={adding}
              className="absolute inset-x-3 bottom-3 flex translate-y-2 items-center justify-center gap-2 rounded-xl bg-slate-900/90 py-2.5 text-sm font-semibold text-white opacity-0 backdrop-blur transition-all duration-300 hover:bg-primary-600 group-hover:translate-y-0 group-hover:opacity-100"
            >
              <ShoppingCart className="h-4 w-4" />
              {adding ? 'Adding…' : 'Add to cart'}
            </button>
          )}
        </div>

        {/* Details */}
        <div className="p-4">
          {product.brand && (
            <p className="text-[11px] font-semibold uppercase tracking-wider text-primary-600">
              {product.brand}
            </p>
          )}
          <h3 className="mt-0.5 line-clamp-2 min-h-[2.5rem] text-sm font-medium text-slate-800 group-hover:text-primary-700">
            {product.name}
          </h3>

          <div className="mt-1.5 flex items-center gap-1.5">
            <Stars rating={product.avg_rating} />
            <span className="text-xs text-slate-500">
              {product.avg_rating > 0 ? product.avg_rating.toFixed(1) : 'New'}
              {product.review_count > 0 && ` (${product.review_count})`}
            </span>
          </div>

          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-lg font-bold text-slate-900">
              ₹{product.price.toLocaleString('en-IN')}
            </span>
            {product.compare_at_price && product.compare_at_price > product.price && (
              <span className="text-xs text-slate-400 line-through">
                ₹{product.compare_at_price.toLocaleString('en-IN')}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
