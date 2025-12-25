'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Star, Heart, ShoppingCart, Truck, RotateCcw, Shield, Minus, Plus, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function ProductDetailPage() {
  const { slug } = useParams();
  const [product, setProduct] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [reviewSummary, setReviewSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, title: '', content: '' });
  const [submittingReview, setSubmittingReview] = useState(false);
  const { addToCart, isAuthenticated } = useStore();

  useEffect(() => {
    async function loadProduct() {
      try {
        const data = await api.getProduct(slug as string);
        setProduct(data);

        // Load reviews
        const [reviewsData, summaryData] = await Promise.all([
          api.getProductReviews(data.id),
          api.getReviewSummary(data.id),
        ]);
        setReviews(reviewsData);
        setReviewSummary(summaryData);
      } catch (error) {
        console.error('Failed to load product:', error);
      } finally {
        setLoading(false);
      }
    }
    loadProduct();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }

    try {
      await addToCart(product.id, quantity);
      toast.success('Added to cart!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add to cart');
    }
  };

  const handleWishlist = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add to wishlist');
      return;
    }

    try {
      if (isWishlisted) {
        await api.removeFromWishlist(product.id);
        setIsWishlisted(false);
        toast.success('Removed from wishlist');
      } else {
        await api.addToWishlist(product.id);
        setIsWishlisted(true);
        toast.success('Added to wishlist!');
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to update wishlist');
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please login to submit a review');
      return;
    }

    setSubmittingReview(true);
    try {
      await api.createReview({
        product_id: product.id,
        rating: reviewForm.rating,
        title: reviewForm.title || undefined,
        content: reviewForm.content || undefined,
      });
      toast.success('Review submitted successfully!');
      setShowReviewForm(false);
      setReviewForm({ rating: 5, title: '', content: '' });

      // Reload reviews
      const [reviewsData, summaryData] = await Promise.all([
        api.getProductReviews(product.id),
        api.getReviewSummary(product.id),
      ]);
      setReviews(reviewsData);
      setReviewSummary(summaryData);
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit review');
    } finally {
      setSubmittingReview(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gray-200 aspect-square rounded-lg"></div>
            <div>
              <div className="bg-gray-200 h-8 w-2/3 rounded mb-4"></div>
              <div className="bg-gray-200 h-4 w-1/3 rounded mb-4"></div>
              <div className="bg-gray-200 h-6 w-1/4 rounded mb-4"></div>
              <div className="bg-gray-200 h-32 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold">Product not found</h1>
        <Link href="/products" className="text-primary-600 hover:underline mt-4 inline-block">
          Browse all products
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm mb-6">
        <Link href="/" className="text-gray-500 hover:text-gray-700">Home</Link>
        <span className="mx-2 text-gray-400">/</span>
        <Link href="/products" className="text-gray-500 hover:text-gray-700">Products</Link>
        <span className="mx-2 text-gray-400">/</span>
        <span className="text-gray-900">{product.name}</span>
      </nav>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Images */}
        <div>
          <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
            <Image
              src={product.images[selectedImage]?.url || product.primary_image}
              alt={product.name}
              fill
              className="object-cover"
            />
            {product.discount_percentage > 0 && (
              <span className="absolute top-4 left-4 bg-red-500 text-white text-sm font-semibold px-3 py-1 rounded">
                {product.discount_percentage}% OFF
              </span>
            )}
          </div>
          {product.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {product.images.map((img: any, idx: number) => (
                <button
                  key={img.id}
                  onClick={() => setSelectedImage(idx)}
                  className={`relative w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 border-2 ${
                    selectedImage === idx ? 'border-primary-600' : 'border-transparent'
                  }`}
                >
                  <Image src={img.url} alt="" fill className="object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <h1 className="text-2xl font-bold mb-2">{product.name}</h1>

          {/* Rating */}
          <div className="flex items-center gap-2 mb-4">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 ${
                    i < Math.round(product.avg_rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-gray-600">
              {product.avg_rating.toFixed(1)} ({product.review_count} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="mb-6">
            <div className="flex items-center gap-3">
              <span className="text-3xl font-bold">Rs. {product.price.toLocaleString()}</span>
              {product.compare_at_price && (
                <span className="text-xl text-gray-500 line-through">
                  Rs. {product.compare_at_price.toLocaleString()}
                </span>
              )}
            </div>
            {product.discount_percentage > 0 && (
              <p className="text-green-600 text-sm mt-1">
                You save Rs. {(product.compare_at_price - product.price).toLocaleString()}
              </p>
            )}
          </div>

          {/* Stock status */}
          <div className="mb-6">
            {product.in_stock ? (
              <span className="text-green-600 font-medium">In Stock</span>
            ) : (
              <span className="text-red-600 font-medium">Out of Stock</span>
            )}
          </div>

          {/* Quantity and Add to Cart */}
          {product.in_stock && (
            <div className="flex items-center gap-4 mb-6">
              <div className="flex items-center border rounded-lg">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-3 hover:bg-gray-100"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="px-4 font-medium">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                  className="p-3 hover:bg-gray-100"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={handleAddToCart}
                className="flex-1 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center justify-center gap-2 font-semibold"
              >
                <ShoppingCart className="w-5 h-5" />
                Add to Cart
              </button>

              <button
                onClick={handleWishlist}
                className={`p-3 border rounded-lg hover:bg-gray-100 ${isWishlisted ? 'border-red-500' : ''}`}
              >
                <Heart className={`w-5 h-5 ${isWishlisted ? 'fill-red-500 text-red-500' : ''}`} />
              </button>
            </div>
          )}

          {/* Features */}
          <div className="border-t pt-6 space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <Truck className="w-5 h-5 text-primary-600" />
              <span>Free delivery on orders over Rs. 999</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <RotateCcw className="w-5 h-5 text-primary-600" />
              <span>{product.return_window_days}-day easy returns</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <Shield className="w-5 h-5 text-primary-600" />
              <span>Secure checkout</span>
            </div>
          </div>

          {/* Description */}
          <div className="border-t mt-6 pt-6">
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-gray-600">{product.description || product.short_description}</p>
          </div>

          {/* Specs */}
          <div className="border-t mt-6 pt-6">
            <h3 className="font-semibold mb-2">Product Details</h3>
            <dl className="grid grid-cols-2 gap-2 text-sm">
              {product.brand && (
                <>
                  <dt className="text-gray-500">Brand</dt>
                  <dd>{product.brand}</dd>
                </>
              )}
              {product.material && (
                <>
                  <dt className="text-gray-500">Material</dt>
                  <dd>{product.material}</dd>
                </>
              )}
              {product.color && (
                <>
                  <dt className="text-gray-500">Color</dt>
                  <dd>{product.color}</dd>
                </>
              )}
              {product.size && (
                <>
                  <dt className="text-gray-500">Size</dt>
                  <dd>{product.size}</dd>
                </>
              )}
              <dt className="text-gray-500">SKU</dt>
              <dd>{product.sku}</dd>
            </dl>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mt-12 border-t pt-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Customer Reviews</h2>
          {isAuthenticated && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Write a Review
            </button>
          )}
        </div>

        {/* Review Form */}
        {showReviewForm && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-semibold mb-4">Write Your Review</h3>
            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Rating</label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setReviewForm({ ...reviewForm, rating: star })}
                      className="p-1"
                    >
                      <Star
                        className={`w-8 h-8 ${
                          star <= reviewForm.rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Title (optional)</label>
                <input
                  type="text"
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm({ ...reviewForm, title: e.target.value })}
                  placeholder="Summarize your review"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Review (optional)</label>
                <textarea
                  value={reviewForm.content}
                  onChange={(e) => setReviewForm({ ...reviewForm, content: e.target.value })}
                  placeholder="Share your experience with this product"
                  rows={4}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={submittingReview}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {submittingReview ? 'Submitting...' : 'Submit Review'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowReviewForm(false)}
                  className="px-6 py-2 border rounded-lg hover:bg-gray-100"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {reviewSummary && reviewSummary.total_reviews > 0 ? (
          <div className="grid md:grid-cols-3 gap-8">
            {/* Summary */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-center">
                <div className="text-4xl font-bold">{reviewSummary.avg_rating.toFixed(1)}</div>
                <div className="flex justify-center my-2">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 ${
                        i < Math.round(reviewSummary.avg_rating)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <div className="text-gray-600">{reviewSummary.total_reviews} reviews</div>
              </div>

              {/* Rating distribution */}
              <div className="mt-4 space-y-2">
                {[5, 4, 3, 2, 1].map((rating) => (
                  <div key={rating} className="flex items-center gap-2 text-sm">
                    <span className="w-3">{rating}</span>
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <div className="flex-1 h-2 bg-gray-200 rounded">
                      <div
                        className="h-full bg-yellow-400 rounded"
                        style={{
                          width: `${
                            (reviewSummary.rating_distribution[rating] / reviewSummary.total_reviews) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <span className="w-8 text-right text-gray-500">
                      {reviewSummary.rating_distribution[rating]}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Reviews list */}
            <div className="md:col-span-2 space-y-6">
              {reviews.map((review) => (
                <div key={review.id} className="border-b pb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < review.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    {review.is_verified_purchase && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                        Verified Purchase
                      </span>
                    )}
                  </div>
                  {review.title && <h4 className="font-medium">{review.title}</h4>}
                  {review.content && <p className="text-gray-600 mt-1">{review.content}</p>}
                  <div className="text-sm text-gray-500 mt-2">
                    By {review.user_name} on{' '}
                    {new Date(review.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">No reviews yet. Be the first to review this product!</p>
        )}
      </div>
    </div>
  );
}
