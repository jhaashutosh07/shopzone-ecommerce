import Link from 'next/link';
import { Sparkles, ShieldCheck, Truck, RotateCcw, BadgeCheck } from 'lucide-react';

const TRUST = [
  { icon: ShieldCheck, title: 'AI-verified returns', text: 'Instant, explainable decisions' },
  { icon: Truck, title: 'Fast delivery', text: 'Free shipping over ₹999' },
  { icon: RotateCcw, title: 'Easy returns', text: 'Up to 30-day window' },
  { icon: BadgeCheck, title: 'Genuine products', text: 'Real brands, real reviews' },
];

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white">
      {/* Trust strip */}
      <div className="container-page grid grid-cols-2 gap-6 py-8 md:grid-cols-4">
        {TRUST.map((t) => (
          <div key={t.title} className="flex items-start gap-3">
            <span className="rounded-xl bg-primary-50 p-2.5 text-primary-600">
              <t.icon className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">{t.title}</p>
              <p className="text-xs text-slate-500">{t.text}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-100 bg-slate-50">
        <div className="container-page grid grid-cols-2 gap-8 py-10 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 text-white">
                <Sparkles className="h-4 w-4" />
              </span>
              <span className="font-display text-lg font-extrabold text-slate-900">
                Shop<span className="text-primary-600">Zone</span>
              </span>
            </Link>
            <p className="mt-3 max-w-xs text-sm text-slate-500">
              A full-stack commerce platform where every return decision is scored by an
              explainable ML engine — no black-box denials.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900">Shop</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-500">
              <li><Link href="/products" className="hover:text-primary-600">All products</Link></li>
              <li><Link href="/products?category=electronics" className="hover:text-primary-600">Electronics</Link></li>
              <li><Link href="/products?category=clothing" className="hover:text-primary-600">Fashion</Link></li>
              <li><Link href="/products?category=beauty" className="hover:text-primary-600">Beauty</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900">Support</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-500">
              <li><Link href="/help" className="hover:text-primary-600">Help Center</Link></li>
              <li><Link href="/shipping" className="hover:text-primary-600">Shipping</Link></li>
              <li><Link href="/return-policy" className="hover:text-primary-600">Return Policy</Link></li>
              <li><Link href="/contact" className="hover:text-primary-600">Contact Us</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900">Legal</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-500">
              <li><Link href="/terms" className="hover:text-primary-600">Terms of Service</Link></li>
              <li><Link href="/privacy" className="hover:text-primary-600">Privacy Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-200 py-4">
          <p className="container-page text-center text-xs text-slate-400">
            © {new Date().getFullYear()} ShopZone · Demo store with simulated payments ·
            Powered by an explainable ML Return Policy Engine
          </p>
        </div>
      </div>
    </footer>
  );
}
