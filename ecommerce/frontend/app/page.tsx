'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import ProductCard, { ProductCardData, ProductCardSkeleton } from '@/components/ProductCard';
import {
  ArrowRight,
  Flame,
  ShieldCheck,
  Laptop,
  Shirt,
  Sparkle,
  Home as HomeIcon,
  Watch,
  Dumbbell,
  Apple,
  Car,
  ScanSearch,
  BrainCircuit,
  BadgeCheck,
} from 'lucide-react';

const CATEGORY_TILES = [
  { label: 'Electronics', value: 'electronics', icon: Laptop, tint: 'from-sky-500 to-indigo-600' },
  { label: 'Fashion', value: 'clothing', icon: Shirt, tint: 'from-rose-500 to-pink-600' },
  { label: 'Beauty', value: 'beauty', icon: Sparkle, tint: 'from-fuchsia-500 to-purple-600' },
  { label: 'Home & Living', value: 'home', icon: HomeIcon, tint: 'from-emerald-500 to-teal-600' },
  { label: 'Jewelry & Watches', value: 'jewelry', icon: Watch, tint: 'from-amber-500 to-orange-600' },
  { label: 'Sports', value: 'sports', icon: Dumbbell, tint: 'from-lime-500 to-green-600' },
  { label: 'Grocery', value: 'grocery', icon: Apple, tint: 'from-red-500 to-rose-600' },
  { label: 'Automotive', value: 'automotive', icon: Car, tint: 'from-slate-600 to-slate-800' },
];

const AI_STEPS = [
  {
    icon: ScanSearch,
    title: 'Request a return',
    text: 'Pick any delivered item and tell us what went wrong — that’s it.',
  },
  {
    icon: BrainCircuit,
    title: 'ML engine scores it live',
    text: 'Your history, the product and the context are scored in milliseconds by our Return Policy Engine.',
  },
  {
    icon: BadgeCheck,
    title: 'Instant, explained decision',
    text: 'Approved or flagged — you see exactly which factors drove the decision. No black boxes.',
  },
];

function Row({ title, subtitle, href, products, loading, flame }: {
  title: string;
  subtitle: string;
  href: string;
  products: ProductCardData[];
  loading: boolean;
  flame?: boolean;
}) {
  return (
    <section className="container-page mt-14">
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="section-title flex items-center gap-2">
            {flame && <Flame className="h-6 w-6 text-rose-500" />}
            {title}
          </h2>
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
        </div>
        <Link href={href} className="hidden items-center gap-1 text-sm font-semibold text-primary-600 hover:text-primary-700 sm:flex">
          View all <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => <ProductCardSkeleton key={i} />)
          : products.slice(0, 5).map((p) => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  );
}

export default function HomePage() {
  const [deals, setDeals] = useState<ProductCardData[]>([]);
  const [featured, setFeatured] = useState<ProductCardData[]>([]);
  const [newest, setNewest] = useState<ProductCardData[]>([]);
  const [brands, setBrands] = useState<{ name: string; product_count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      api.getDeals(),
      api.getFeaturedProducts(),
      api.getProducts({ sort_by: 'newest', per_page: 10 }),
      api.getBrands(),
    ]).then(([d, f, n, b]) => {
      if (d.status === 'fulfilled') setDeals(d.value);
      if (f.status === 'fulfilled') setFeatured(f.value);
      if (n.status === 'fulfilled') setNewest(n.value);
      if (b.status === 'fulfilled') setBrands(b.value);
      setLoading(false);
    });
  }, []);

  return (
    <div className="pb-8">
      {/* Hero */}
      <section className="relative overflow-hidden bg-slate-950">
        <div className="absolute inset-0">
          <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary-600/30 blur-3xl" />
          <div className="absolute -bottom-40 right-0 h-[28rem] w-[28rem] rounded-full bg-fuchsia-600/20 blur-3xl" />
          <div className="absolute left-1/2 top-0 h-64 w-64 -translate-x-1/2 rounded-full bg-accent-500/10 blur-3xl" />
        </div>

        <div className="container-page relative py-16 sm:py-24">
          <div className="max-w-2xl animate-fade-up">
            <span className="chip border border-primary-400/30 bg-primary-500/10 text-primary-300">
              <ShieldCheck className="h-3.5 w-3.5" />
              Every return decision is AI-scored &amp; explained
            </span>
            <h1 className="mt-5 font-display text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-6xl">
              Real products.
              <br />
              <span className="bg-gradient-to-r from-primary-400 via-fuchsia-400 to-accent-400 bg-clip-text text-transparent">
                Radically fair returns.
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-base text-slate-300 sm:text-lg">
              Shop {brands.length > 0 ? `${brands.length}+ brands` : 'hundreds of products'} with
              live inventory, genuine reviews and an ML engine that approves honest returns in
              milliseconds — and shows its reasoning.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/products" className="btn-primary !px-7 !py-3 !text-base shadow-glow">
                Shop the catalog <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/products?sort_by=popular" className="btn-secondary !border-slate-700 !bg-slate-900/60 !px-7 !py-3 !text-base !text-slate-200 hover:!border-primary-500">
                <Flame className="h-4 w-4 text-rose-400" /> Bestsellers
              </Link>
            </div>

            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-sm text-slate-400">
              <span><strong className="text-white">200+</strong> real listings</span>
              <span><strong className="text-white">590+</strong> verified reviews</span>
              <span><strong className="text-white">&lt;1s</strong> return decisions</span>
            </div>
          </div>
        </div>

        {/* Brand marquee */}
        {brands.length > 6 && (
          <div className="relative border-t border-white/5 bg-white/[0.03] py-3">
            <div className="flex w-max animate-marquee gap-10 whitespace-nowrap px-4 text-sm font-semibold uppercase tracking-widest text-slate-500">
              {[...brands, ...brands].map((b, i) => (
                <Link key={i} href={`/products?brand=${encodeURIComponent(b.name)}`} className="transition hover:text-slate-200">
                  {b.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Categories */}
      <section className="container-page mt-12">
        <h2 className="section-title">Shop by category</h2>
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
          {CATEGORY_TILES.map((cat) => (
            <Link
              key={cat.value}
              href={`/products?category=${cat.value}`}
              className="group card flex flex-col items-center gap-3 p-4 text-center transition-all hover:-translate-y-1 hover:shadow-card-hover"
            >
              <span className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${cat.tint} text-white shadow-sm transition-transform group-hover:scale-110`}>
                <cat.icon className="h-6 w-6" />
              </span>
              <span className="text-xs font-semibold text-slate-700 group-hover:text-primary-700">
                {cat.label}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <Row
        title="Deals of the day"
        subtitle="Biggest live discounts across the catalog"
        href="/products?sort_by=price_low"
        products={deals}
        loading={loading}
        flame
      />

      {/* AI returns explainer */}
      <section className="container-page mt-16">
        <div className="card overflow-hidden !border-slate-800 bg-slate-950">
          <div className="relative px-6 py-10 sm:px-10">
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary-600/20 blur-3xl" />
            <div className="relative">
              <span className="chip border border-emerald-400/30 bg-emerald-500/10 text-emerald-300">
                <ShieldCheck className="h-3.5 w-3.5" /> The ShopZone difference
              </span>
              <h2 className="mt-4 font-display text-2xl font-bold text-white sm:text-3xl">
                Returns without the black box
              </h2>
              <p className="mt-2 max-w-2xl text-sm text-slate-400">
                Behind every return is a live ML risk engine with per-decision explanations,
                merchant feedback retraining and drift monitoring.
              </p>
              <div className="mt-8 grid gap-6 sm:grid-cols-3">
                {AI_STEPS.map((step, i) => (
                  <div key={step.title} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-500/15 text-primary-300">
                        <step.icon className="h-5 w-5" />
                      </span>
                      <span className="text-xs font-bold text-slate-500">STEP {i + 1}</span>
                    </div>
                    <h3 className="mt-3 font-semibold text-white">{step.title}</h3>
                    <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{step.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Row
        title="Featured picks"
        subtitle="Top-rated products our shoppers love"
        href="/products?sort_by=popular"
        products={featured}
        loading={loading}
      />

      <Row
        title="New arrivals"
        subtitle="Fresh in the catalog this week"
        href="/products?sort_by=newest"
        products={newest}
        loading={loading}
      />
    </div>
  );
}
