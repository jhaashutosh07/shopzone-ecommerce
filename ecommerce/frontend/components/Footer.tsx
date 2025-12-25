import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white text-lg font-semibold mb-4">ShopZone</h3>
            <p className="text-sm">
              Your one-stop destination for quality products at great prices.
              Shop with confidence with our easy returns policy.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/products" className="hover:text-white">All Products</Link></li>
              <li><Link href="/products/deals" className="hover:text-white">Today's Deals</Link></li>
              <li><Link href="/products?category=clothing" className="hover:text-white">Clothing</Link></li>
              <li><Link href="/products?category=electronics" className="hover:text-white">Electronics</Link></li>
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h4 className="text-white font-semibold mb-4">Customer Service</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/help" className="hover:text-white">Help Center</Link></li>
              <li><Link href="/orders" className="hover:text-white">Track Order</Link></li>
              <li><Link href="/returns" className="hover:text-white">Returns & Refunds</Link></li>
              <li><Link href="/contact" className="hover:text-white">Contact Us</Link></li>
            </ul>
          </div>

          {/* Policies */}
          <div>
            <h4 className="text-white font-semibold mb-4">Policies</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/privacy" className="hover:text-white">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-white">Terms of Service</Link></li>
              <li><Link href="/return-policy" className="hover:text-white">Return Policy</Link></li>
              <li><Link href="/shipping" className="hover:text-white">Shipping Info</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
          <p>&copy; 2024 ShopZone. All rights reserved.</p>
          <p className="mt-2 text-gray-500">
            Powered by Return Policy Engine for intelligent return management
          </p>
        </div>
      </div>
    </footer>
  );
}
