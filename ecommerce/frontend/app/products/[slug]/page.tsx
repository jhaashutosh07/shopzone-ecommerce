'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import ProductCard, { ProductCardData } from '@/components/ProductCard';
import Stars from '@/components/Stars';
import {
  Heart,
  ShoppingCart,
  Truck,
  RotateCcw,
  ShieldCheck,
  Minus,
  Plus,
  Send,
  BadgeCheck,
  Package,
  Ruler,
  Weight,
  Tag,
  ChevronRight,
  Zap,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProductDetailPage() {
  const { slug } = useParams();
  const [product, setProduct] = useState<any>(null);
  const [related, setRelated] = useState<ProductCardData[]>([]);
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
      setLoading(true);
      setSelectedImage(0);
      try {
        const data = await api.getProduct(slug as string);
        setProduct(data);

        const [reviewsData, summaryData, relatedData] = await Promise.all([
          api.getProductReviews(data.id),
          api.getReviewSummary(data.id),
          api.getProducts({ category: data.category, per_page: 6 }),
        ]);
        setReviews(reviewsData);
        setReviewSummary(summaryData);
        setRelated(relatedData.filter((p: any) => p.id !== data.id).slice(0, 5));
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
      toast.success('Added to cart');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add to cart');
    }
  };

  const handleWishlist = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to use wishlist');
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

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please login to write a review');
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
      toast.success('Review submitted');
      setShowReviewForm(false);
      setReviewForm({ rating: 5, title: '', content: '' });
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
      <div className="container-page py-8">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="skeleton aspect-square" />
          <div className="space-y-4">
            <div className="skeleton h-4 w-24" />
            <div className="skeleton h-8 w-3/4" />
            <div className="skeleton h-4 w-40" />
            <div className="skeleton h-10 w-48" />
            <div className="skeleton h-24 w-full" />
            <div className="skeleton h-12 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container-page py-24 text-center">
        <p className="font-semibold text-slate-900">Product not found</p>
        <Link href="/products" className="btn-primary mt-4 inline-flex">Browse catalog</Link>
      </div>
    );
  }

  const images: { url: string; alt_text?: string }[] =
    product.images?.length > 0 ? product.images : [{ url: product.primary_image }];
  const details = product.details || {};

  const specs: { icon: any; label: string; value: string }[] = [];
  if (product.brand) specs.push({ icon: BadgeCheck, label: 'Brand', value: product.brand });
  if (product.sku) specs.push({ icon: Tag, label: 'SKU', value: product.sku });
  if (product.weight) specs.push({ icon: Weight, label: 'Weight', value: `${product.weight} kg` });
  if (product.dimensions) specs.push({ icon: Ruler, label: 'Dimensions', value: product.dimensions });
  if (product.color) specs.push({ icon: Package, label: 'Color', value: product.color });
  if (product.material) specs.push({ icon: Package, label: 'Material', value: product.material });
  if (details.warranty) specs.push({ icon: ShieldCheck, label: 'Warranty', value: details.warranty });
  if (details.shipping) specs.push({ icon: Truck, label: 'Shipping', value: details.shipping });

  const distribution = reviewSummary?.rating_distribution || {};
  const totalReviews = reviewSummary?.total_reviews || 0;

  return (
    <div className="container-page py-6">
      {/* Breadcrumbs */}
      <nav className="mb-5 flex items-center gap-1.5 text-xs text-slate-500">
        <Link href="/" className="hover:text-primary-600">Home</Link>
        <ChevronRight className="h-3 w-3" />
        <Link href={`/products?category=${product.category}`} className="capitalize hover:text-primary-600">
          {product.category}
        </Link>
        <ChevronRight className="h-3 w-3" />
        <span className="max-w-[200px] truncate text-slate-700">{product.name}</span>
      </nav>

      <div className="grid gap-10 lg:grid-cols-2">
        {/* Gallery */}
        <div>
          <div className="card relative aspect-square overflow-hidden">
            <Image
              src={images[selectedImage]?.url || product.primary_image}
              alt={product.name}
              fill
              priority
              sizes="(max-width: 1024px) 100vw, 50vw"
              className="object-contain p-6"
            />
            {product.discount_percentage > 0 && (
              <span className="chip absolute left-4 top-4 bg-rose-500 text-white shadow">
                −{product.discount_percentage}% OFF
              </span>
            )}
            {product.total_sold > 500 && (
              <span className="chip absolute right-4 top-4 bg-accent-100 text-accent-700">
                <Zap className="h-3 w-3" /> Bestseller
              </span>
            )}
          </div>
          {images.length > 1 && (
            <div className="no-scrollbar mt-3 flex gap-2 overflow-x-auto">
              {images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedImage(i)}
                  className={`relative h-20 w-20 shrink-0 overflow-hidden rounded-xl border-2 bg-white transition ${
                    selectedImage === i ? 'border-primary-500 shadow-card-hover' : 'border-slate-200 hover:border-primary-300'
                  }`}
                >
                  <Image src={img.url} alt="" fill sizes="80px" className="object-contain p-1.5" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          {product.brand && (
            <Link
              href={`/products?brand=${encodeURIComponent(product.brand)}`}
              className="text-xs font-bold uppercase tracking-widest text-primary-600 hover:underline"
            >
              {product.brand}
            </Link>
          )}
          <h1 className="mt-1 font-display text-2xl font-bold text-slate-900 sm:text-3xl">
            {product.name}
          </h1>

          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
            <span className="flex items-center gap-1.5">
              <Stars rating={product.avg_rating} size={16} />
              <span className="font-semibold text-slate-800">
                {product.avg_rating > 0 ? product.avg_rating.toFixed(1) : 'New'}
              </span>
            </span>
            <a href="#reviews" className="text-slate-500 hover:text-primary-600">
              {product.review_count} review{product.review_count === 1 ? '' : 's'}
            </a>
            <span className="text-slate-300">·</span>
            <span className="text-slate-500">{product.total_sold?.toLocaleString('en-IN')} sold</span>
          </div>

          {/* Price */}
          <div className="mt-5 flex items-end gap-3">
            <span className="font-display text-4xl font-extrabold text-slate-900">
              ₹{product.price.toLocaleString('en-IN')}
            </span>
            {product.compare_at_price && product.compare_at_price > product.price && (
              <>
                <span className="pb-1 text-lg text-slate-400 line-through">
                  ₹{product.compare_at_price.toLocaleString('en-IN')}
                </span>
                <span className="chip mb-1.5 bg-emerald-100 font-bold text-emerald-700">
                  Save ₹{(product.compare_at_price - product.price).toLocaleString('en-IN')}
                </span>
              </>
            )}
          </div>
          <p className="mt-1 text-xs text-slate-500">Inclusive of all taxes</p>

          {/* Stock */}
          <div className="mt-4">
            {product.in_stock ? (
              product.stock_quantity <= 10 ? (
                <span className="chip bg-amber-100 font-semibold text-amber-700">
                  Only {product.stock_quantity} left — order soon
                </span>
              ) : (
                <span className="chip bg-emerald-100 font-semibold text-emerald-700">In stock</span>
              )
            ) : (
              <span className="chip bg-rose-100 font-semibold text-rose-700">Out of stock</span>
            )}
          </div>

          {/* Description */}
          <p className="mt-5 leading-relaxed text-slate-600">{product.description}</p>

          {details.tags?.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {details.tags.map((tag: string) => (
                <span key={tag} className="chip bg-slate-100 capitalize text-slate-600">{tag}</span>
              ))}
            </div>
          )}

          {/* Quantity + CTA */}
          {product.in_stock && (
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <div className="flex items-center rounded-xl border border-slate-200 bg-white">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-3 text-slate-500 transition hover:text-primary-600"
                  aria-label="Decrease quantity"
                >
                  <Minus className="h-4 w-4" />
                </button>
                <span className="w-10 text-center font-semibold">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                  className="p-3 text-slate-500 transition hover:text-primary-600"
                  aria-label="Increase quantity"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
              <button onClick={handleAddToCart} className="btn-primary flex-1 !py-3 sm:flex-none sm:!px-10">
                <ShoppingCart className="h-4 w-4" /> Add to cart
              </button>
              <button
                onClick={handleWishlist}
                className={`rounded-xl border p-3 transition ${
                  isWishlisted
                    ? 'border-rose-200 bg-rose-50 text-rose-500'
                    : 'border-slate-200 bg-white text-slate-500 hover:border-rose-200 hover:text-rose-500'
                }`}
                aria-label="Wishlist"
              >
                <Heart className={`h-5 w-5 ${isWishlisted ? 'fill-rose-500' : ''}`} />
              </button>
            </div>
          )}

          {/* Policies */}
          <div className="mt-7 grid grid-cols-3 gap-3">
            <div className="card flex flex-col items-center gap-1.5 p-3 text-center">
              <Truck className="h-5 w-5 text-primary-600" />
              <span className="text-xs font-medium text-slate-700">
                {details.shipping || 'Fast delivery'}
              </span>
            </div>
            <div className="card flex flex-col items-center gap-1.5 p-3 text-center">
              <RotateCcw className="h-5 w-5 text-primary-600" />
              <span className="text-xs font-medium text-slate-700">
                {product.is_returnable ? `${product.return_window_days}-day returns` : 'Non-returnable'}
              </span>
            </div>
            <div className="card flex flex-col items-center gap-1.5 p-3 text-center">
              <ShieldCheck className="h-5 w-5 text-primary-600" />
              <span className="text-xs font-medium text-slate-700">AI-verified returns</span>
            </div>
          </div>
        </div>
      </div>

      {/* Specifications */}
      {specs.length > 0 && (
        <section className="mt-12">
          <h2 className="section-title">Specifications</h2>
          <div className="card mt-4 grid gap-x-8 gap-y-1 p-2 sm:grid-cols-2">
            {specs.map((s) => (
              <div key={s.label} className="flex items-center gap-3 rounded-xl px-4 py-3 odd:bg-slate-50/70">
                <s.icon className="h-4 w-4 shrink-0 text-slate-400" />
                <span className="w-28 shrink-0 text-sm text-slate-500">{s.label}</span>
                <span className="text-sm font-medium text-slate-800">{s.value}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Reviews */}
      <section id="reviews" className="mt-12">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="section-title">Customer reviews</h2>
          {isAuthenticated && (
            <button onClick={() => setShowReviewForm(!showReviewForm)} className="btn-secondary !py-2">
              Write a review
            </button>
          )}
        </div>

        <div className="mt-5 grid gap-6 lg:grid-cols-3">
          {/* Summary */}
          <div className="card h-fit p-6">
            <div className="flex items-end gap-3">
              <span className="font-display text-5xl font-extrabold text-slate-900">
                {(reviewSummary?.avg_rating || 0).toFixed(1)}
              </span>
              <div className="pb-1.5">
                <Stars rating={reviewSummary?.avg_rating || 0} size={16} />
                <p className="mt-0.5 text-xs text-slate-500">{totalReviews} reviews</p>
              </div>
            </div>
            <div className="mt-4 space-y-1.5">
              {[5, 4, 3, 2, 1].map((star) => {
                const count = distribution[star] || 0;
                const pct = totalReviews > 0 ? (count / totalReviews) * 100 : 0;
                return (
                  <div key={star} className="flex items-center gap-2 text-xs">
                    <span className="w-6 text-slate-600">{star}★</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-accent-400" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="w-6 text-right text-slate-400">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* List + form */}
          <div className="lg:col-span-2">
            {showReviewForm && (
              <form onSubmit={handleSubmitReview} className="card mb-5 space-y-3 p-5">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-700">Your rating:</span>
                  {[1, 2, 3, 4, 5].map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setReviewForm({ ...reviewForm, rating: r })}
                      className={`text-xl transition ${r <= reviewForm.rating ? 'text-accent-400' : 'text-slate-300'}`}
                    >
                      ★
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  placeholder="Title (optional)"
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm({ ...reviewForm, title: e.target.value })}
                  className="input"
                />
                <textarea
                  placeholder="Share your experience…"
                  rows={3}
                  value={reviewForm.content}
                  onChange={(e) => setReviewForm({ ...reviewForm, content: e.target.value })}
                  className="input resize-none"
                />
                <button type="submit" disabled={submittingReview} className="btn-primary">
                  <Send className="h-4 w-4" />
                  {submittingReview ? 'Submitting…' : 'Submit review'}
                </button>
              </form>
            )}

            {reviews.length === 0 ? (
              <div className="card p-10 text-center text-sm text-slate-500">
                No reviews yet — be the first to review this product.
              </div>
            ) : (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.id} className="card p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-700">
                          {review.user_name?.charAt(0)?.toUpperCase() || 'U'}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{review.user_name}</p>
                          <div className="flex items-center gap-2">
                            <Stars rating={review.rating} size={12} />
                            {review.is_verified_purchase && (
                              <span className="chip bg-emerald-50 !px-2 !py-0.5 text-[10px] text-emerald-700">
                                <BadgeCheck className="h-3 w-3" /> Verified
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <span className="text-xs text-slate-400">
                        {new Date(review.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric', month: 'short', year: 'numeric',
                        })}
                      </span>
                    </div>
                    {review.title && <p className="mt-3 text-sm font-semibold text-slate-900">{review.title}</p>}
                    {review.content && <p className="mt-1 text-sm leading-relaxed text-slate-600">{review.content}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Related */}
      {related.length > 0 && (
        <section className="mt-14">
          <h2 className="section-title">You may also like</h2>
          <div className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {related.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}
    </div>
  );
}
