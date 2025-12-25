'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import Image from 'next/image';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { Heart, ShoppingCart, Trash2 } from 'lucide-react';

export default function WishlistPage() {
  const router = useRouter();
  const { isAuthenticated, addToCart } = useStore();
  const [wishlist, setWishlist] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    loadWishlist();
  }, [isAuthenticated, router]);

  const loadWishlist = async () => {
    try {
      const data = await api.getWishlist();
      setWishlist(data);
    } catch (error) {
      console.error('Failed to load wishlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (productId: string) => {
    try {
      await api.removeFromWishlist(productId);
      setWishlist(wishlist.filter((item) => item.product_id !== productId));
      toast.success('Removed from wishlist');
    } catch (error) {
      toast.error('Failed to remove item');
    }
  };

  const handleAddToCart = async (productId: string) => {
    try {
      await addToCart(productId, 1);
      toast.success('Added to cart');
    } catch (error) {
      toast.error('Failed to add to cart');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p>Loading wishlist...</p>
      </div>
    );
  }

  if (wishlist.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <Heart className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Your wishlist is empty</h1>
        <p className="text-gray-600 mb-4">Save items you love for later</p>
        <Link
          href="/products"
          className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">My Wishlist ({wishlist.length} items)</h1>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {wishlist.map((item) => (
          <div key={item.id} className="bg-white rounded-lg border overflow-hidden group">
            <div className="relative aspect-square">
              <Image
                src={item.product_image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'}
                alt={item.product_name}
                fill
                className="object-cover"
              />
              <button
                onClick={() => handleRemove(item.product_id)}
                className="absolute top-2 right-2 p-2 bg-white rounded-full shadow hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 text-red-500" />
              </button>
            </div>

            <div className="p-4">
              <Link href={`/products/${item.product_slug}`}>
                <h3 className="font-medium hover:text-primary-600 line-clamp-2">
                  {item.product_name}
                </h3>
              </Link>
              <p className="text-lg font-bold mt-2">Rs. {item.product_price?.toLocaleString()}</p>

              <button
                onClick={() => handleAddToCart(item.product_id)}
                className="w-full mt-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center justify-center gap-2"
              >
                <ShoppingCart className="w-4 h-4" />
                Add to Cart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
