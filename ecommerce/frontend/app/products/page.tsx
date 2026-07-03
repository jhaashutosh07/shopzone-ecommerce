'use client';

export const dynamic = 'force-dynamic';

import { useCallback, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import ProductCard, { ProductCardData, ProductCardSkeleton } from '@/components/ProductCard';
import { SlidersHorizontal, X, ChevronLeft, ChevronRight, Star, PackageSearch } from 'lucide-react';

const CATEGORIES = [
  { value: 'electronics', label: 'Electronics' },
  { value: 'clothing', label: 'Fashion' },
  { value: 'beauty', label: 'Beauty' },
  { value: 'home', label: 'Home & Living' },
  { value: 'jewelry', label: 'Jewelry & Watches' },
  { value: 'sports', label: 'Sports' },
  { value: 'grocery', label: 'Grocery' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'other', label: 'Other' },
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'popular', label: 'Most Popular' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'newest', label: 'Newest First' },
];

const PRICE_PRESETS = [
  { label: 'Under ₹500', min: '', max: '500' },
  { label: '₹500 – ₹2,000', min: '500', max: '2000' },
  { label: '₹2,000 – ₹10,000', min: '2000', max: '10000' },
  { label: '₹10,000 – ₹50,000', min: '10000', max: '50000' },
  { label: 'Over ₹50,000', min: '50000', max: '' },
];

const PER_PAGE = 24;

interface Filters {
  query: string;
  category: string;
  brand: string;
  min_price: string;
  max_price: string;
  min_rating: string;
  in_stock_only: boolean;
  sort_by: string;
  page: number;
}

export default function ProductsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [filters, setFilters] = useState<Filters>({
    query: searchParams.get('query') || '',
    category: searchParams.get('category') || '',
    brand: searchParams.get('brand') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    min_rating: searchParams.get('min_rating') || '',
    in_stock_only: searchParams.get('in_stock_only') === 'true',
    sort_by: searchParams.get('sort_by') || 'relevance',
    page: 1,
  });
  const [products, setProducts] = useState<ProductCardData[]>([]);
  const [brands, setBrands] = useState<{ name: string; product_count: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [hasMore, setHasMore] = useState(false);

  // Keep in sync when header search / category nav changes the URL
  useEffect(() => {
    setFilters((f) => ({
      ...f,
      query: searchParams.get('query') || '',
      category: searchParams.get('category') || '',
      brand: searchParams.get('brand') || f.brand,
      sort_by: searchParams.get('sort_by') || f.sort_by,
      page: 1,
    }));
  }, [searchParams]);

  useEffect(() => {
    api.getBrands().then(setBrands).catch(() => {});
  }, []);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        sort_by: filters.sort_by,
        page: filters.page,
        per_page: PER_PAGE,
      };
      if (filters.query) params.query = filters.query;
      if (filters.category) params.category = filters.category;
      if (filters.brand) params.brand = filters.brand;
      if (filters.min_price) params.min_price = filters.min_price;
      if (filters.max_price) params.max_price = filters.max_price;
      if (filters.min_rating) params.min_rating = filters.min_rating;
      if (filters.in_stock_only) params.in_stock_only = 'true';

      const data = await api.getProducts(params);
      setProducts(data);
      setHasMore(data.length === PER_PAGE);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const update = (patch: Partial<Filters>) => {
    setFilters((f) => ({ ...f, ...patch, page: patch.page ?? 1 }));
  };

  const clearAll = () => {
    update({
      query: '', category: '', brand: '', min_price: '', max_price: '',
      min_rating: '', in_stock_only: false, sort_by: 'relevance', page: 1,
    });
    router.push('/products');
  };

  const activeChips: { label: string; clear: () => void }[] = [];
  if (filters.query) activeChips.push({ label: `“${filters.query}”`, clear: () => update({ query: '' }) });
  if (filters.category) {
    const cat = CATEGORIES.find((c) => c.value === filters.category);
    activeChips.push({ label: cat?.label || filters.category, clear: () => update({ category: '' }) });
  }
  if (filters.brand) activeChips.push({ label: filters.brand, clear: () => update({ brand: '' }) });
  if (filters.min_price || filters.max_price) {
    activeChips.push({
      label: `₹${filters.min_price || '0'} – ${filters.max_price ? `₹${filters.max_price}` : 'any'}`,
      clear: () => update({ min_price: '', max_price: '' }),
    });
  }
  if (filters.min_rating) activeChips.push({ label: `${filters.min_rating}★ & up`, clear: () => update({ min_rating: '' }) });
  if (filters.in_stock_only) activeChips.push({ label: 'In stock', clear: () => update({ in_stock_only: false }) });

  const FilterPanel = (
    <div className="space-y-6">
      {/* Category */}
      <div>
        <h4 className="mb-2 text-sm font-semibold text-slate-900">Category</h4>
        <div className="space-y-1">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => update({ category: filters.category === cat.value ? '' : cat.value })}
              className={`block w-full rounded-lg px-3 py-1.5 text-left text-sm transition ${
                filters.category === cat.value
                  ? 'bg-primary-50 font-semibold text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Price */}
      <div>
        <h4 className="mb-2 text-sm font-semibold text-slate-900">Price</h4>
        <div className="space-y-1">
          {PRICE_PRESETS.map((p) => {
            const active = filters.min_price === p.min && filters.max_price === p.max;
            return (
              <button
                key={p.label}
                onClick={() => update(active ? { min_price: '', max_price: '' } : { min_price: p.min, max_price: p.max })}
                className={`block w-full rounded-lg px-3 py-1.5 text-left text-sm transition ${
                  active ? 'bg-primary-50 font-semibold text-primary-700' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {p.label}
              </button>
            );
          })}
        </div>
        <div className="mt-2 flex items-center gap-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.min_price}
            onChange={(e) => update({ min_price: e.target.value })}
            className="input !px-3 !py-1.5 text-xs"
          />
          <span className="text-slate-400">–</span>
          <input
            type="number"
            placeholder="Max"
            value={filters.max_price}
            onChange={(e) => update({ max_price: e.target.value })}
            className="input !px-3 !py-1.5 text-xs"
          />
        </div>
      </div>

      {/* Rating */}
      <div>
        <h4 className="mb-2 text-sm font-semibold text-slate-900">Rating</h4>
        <div className="space-y-1">
          {[4, 3, 2].map((r) => (
            <button
              key={r}
              onClick={() => update({ min_rating: filters.min_rating === String(r) ? '' : String(r) })}
              className={`flex w-full items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition ${
                filters.min_rating === String(r)
                  ? 'bg-primary-50 font-semibold text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Star className="h-3.5 w-3.5 fill-accent-400 text-accent-400" />
              {r}★ &amp; up
            </button>
          ))}
        </div>
      </div>

      {/* Availability */}
      <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          checked={filters.in_stock_only}
          onChange={(e) => update({ in_stock_only: e.target.checked })}
          className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
        />
        In stock only
      </label>

      {/* Brands */}
      {brands.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-semibold text-slate-900">Brand</h4>
          <div className="max-h-64 space-y-1 overflow-y-auto pr-1">
            {brands.map((b) => (
              <button
                key={b.name}
                onClick={() => update({ brand: filters.brand === b.name ? '' : b.name })}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-1.5 text-left text-sm transition ${
                  filters.brand === b.name
                    ? 'bg-primary-50 font-semibold text-primary-700'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <span className="truncate">{b.name}</span>
                <span className="ml-2 text-xs text-slate-400">{b.product_count}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="container-page py-6">
      {/* Heading + sort */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-900">
            {filters.query
              ? `Results for “${filters.query}”`
              : CATEGORIES.find((c) => c.value === filters.category)?.label || 'All Products'}
          </h1>
          {!loading && (
            <p className="mt-0.5 text-sm text-slate-500">
              {products.length}{hasMore ? '+' : ''} products
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMobileFilters(true)}
            className="btn-secondary !px-4 !py-2 lg:hidden"
          >
            <SlidersHorizontal className="h-4 w-4" /> Filters
          </button>
          <select
            value={filters.sort_by}
            onChange={(e) => update({ sort_by: e.target.value })}
            className="input w-auto !py-2 text-sm"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Active filter chips */}
      {activeChips.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          {activeChips.map((chip, i) => (
            <button
              key={i}
              onClick={chip.clear}
              className="chip border border-primary-200 bg-primary-50 text-primary-700 transition hover:bg-primary-100"
            >
              {chip.label} <X className="h-3 w-3" />
            </button>
          ))}
          <button onClick={clearAll} className="text-xs font-semibold text-slate-500 hover:text-rose-600">
            Clear all
          </button>
        </div>
      )}

      <div className="flex gap-6">
        {/* Desktop sidebar */}
        <aside className="hidden w-60 shrink-0 lg:block">
          <div className="card sticky top-36 max-h-[calc(100vh-10rem)] overflow-y-auto p-5">
            {FilterPanel}
          </div>
        </aside>

        {/* Grid */}
        <div className="min-w-0 flex-1">
          {loading ? (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 12 }).map((_, i) => <ProductCardSkeleton key={i} />)}
            </div>
          ) : products.length === 0 ? (
            <div className="card flex flex-col items-center justify-center py-20 text-center">
              <PackageSearch className="h-12 w-12 text-slate-300" />
              <p className="mt-4 font-semibold text-slate-900">No products found</p>
              <p className="mt-1 text-sm text-slate-500">Try removing some filters</p>
              <button onClick={clearAll} className="btn-primary mt-5">Clear filters</button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
                {products.map((p) => <ProductCard key={p.id} product={p} />)}
              </div>

              {/* Pagination */}
              {(filters.page > 1 || hasMore) && (
                <div className="mt-8 flex items-center justify-center gap-3">
                  <button
                    onClick={() => { update({ page: filters.page - 1 }); window.scrollTo({ top: 0 }); }}
                    disabled={filters.page === 1}
                    className="btn-secondary !px-4 !py-2 disabled:opacity-40"
                  >
                    <ChevronLeft className="h-4 w-4" /> Previous
                  </button>
                  <span className="text-sm font-medium text-slate-600">Page {filters.page}</span>
                  <button
                    onClick={() => { update({ page: filters.page + 1 }); window.scrollTo({ top: 0 }); }}
                    disabled={!hasMore}
                    className="btn-secondary !px-4 !py-2 disabled:opacity-40"
                  >
                    Next <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Mobile filter drawer */}
      {showMobileFilters && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/50" onClick={() => setShowMobileFilters(false)} />
          <div className="absolute inset-y-0 left-0 w-80 max-w-[85vw] overflow-y-auto bg-white p-5 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-lg font-bold">Filters</h3>
              <button onClick={() => setShowMobileFilters(false)} className="rounded-lg p-2 hover:bg-slate-100">
                <X className="h-5 w-5" />
              </button>
            </div>
            {FilterPanel}
            <button onClick={() => setShowMobileFilters(false)} className="btn-primary mt-6 w-full">
              Show results
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
