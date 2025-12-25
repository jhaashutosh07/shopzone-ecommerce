'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Star, Heart, ShoppingCart } from 'lucide-react';
import { useStore } from '@/lib/store';
import toast from 'react-hot-toast';

interface Product {
  id: string;
  name: string;
  slug: string;
  price: number;
  compare_at_price?: number;
  discount_percentage: number;
  avg_rating: number;
  review_count: number;
  in_stock: boolean;
  primary_image: string;
}

export default function ProductCard({ product }: { product: Product }) {
  const { addToCart, isAuthenticated } = useStore();

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }

    try {
      await addToCart(product.id);
      toast.success('Added to cart!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add to cart');
    }
  };

  return (
    <Link href={`/products/${product.slug}`} className="group">
      <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow overflow-hidden">
        {/* Image */}
        <div className="relative aspect-square bg-gray-100">
          <Image
            src={product.primary_image}
            alt={product.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
          {product.discount_percentage > 0 && (
            <span className="absolute top-2 left-2 bg-red-500 text-white text-xs font-semibold px-2 py-1 rounded">
              {product.discount_percentage}% OFF
            </span>
          )}
          {!product.in_stock && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
              <span className="text-white font-semibold">Out of Stock</span>
            </div>
          )}
          <button
            className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toast('Added to wishlist!');
            }}
          >
            <Heart className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* Details */}
        <div className="p-4">
          <h3 className="font-medium text-gray-900 truncate group-hover:text-primary-600">
            {product.name}
          </h3>

          {/* Rating */}
          <div className="flex items-center gap-1 mt-1">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm text-gray-600">
              {product.avg_rating.toFixed(1)} ({product.review_count})
            </span>
          </div>

          {/* Price */}
          <div className="mt-2 flex items-center gap-2">
            <span className="text-lg font-bold text-gray-900">
              Rs. {product.price.toLocaleString()}
            </span>
            {product.compare_at_price && (
              <span className="text-sm text-gray-500 line-through">
                Rs. {product.compare_at_price.toLocaleString()}
              </span>
            )}
          </div>

          {/* Add to cart */}
          {product.in_stock && (
            <button
              onClick={handleAddToCart}
              className="mt-3 w-full py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center justify-center gap-2 transition-colors"
            >
              <ShoppingCart className="w-4 h-4" />
              Add to Cart
            </button>
          )}
        </div>
      </div>
    </Link>
  );
}
