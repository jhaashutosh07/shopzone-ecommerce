import Link from 'next/link';

export default function PrivacyPolicyPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg border p-8">
        <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
        <p className="text-gray-500 mb-8">Last updated: December 2024</p>

        <div className="prose prose-gray max-w-none space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-3">1. Information We Collect</h2>
            <p className="text-gray-600 mb-3">
              We collect information you provide directly to us, including:
            </p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Name, email address, phone number, and shipping address when you create an account or place an order</li>
              <li>Payment information (processed securely through our payment partners)</li>
              <li>Order history and preferences</li>
              <li>Communications you send to us</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">2. How We Use Your Information</h2>
            <p className="text-gray-600 mb-3">We use the information we collect to:</p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Process and fulfill your orders</li>
              <li>Send order confirmations and shipping updates</li>
              <li>Respond to your questions and requests</li>
              <li>Improve our services and user experience</li>
              <li>Send promotional communications (with your consent)</li>
              <li>Detect and prevent fraud</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">3. Information Sharing</h2>
            <p className="text-gray-600 mb-3">
              We do not sell your personal information. We may share your information with:
            </p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Service providers who assist in order fulfillment and delivery</li>
              <li>Payment processors for secure transaction handling</li>
              <li>Law enforcement when required by law</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">4. Data Security</h2>
            <p className="text-gray-600">
              We implement appropriate security measures to protect your personal information from unauthorized
              access, alteration, or destruction. All payment transactions are encrypted using SSL technology.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">5. Cookies</h2>
            <p className="text-gray-600">
              We use cookies to enhance your browsing experience, analyze site traffic, and personalize content.
              You can control cookie preferences through your browser settings.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">6. Your Rights</h2>
            <p className="text-gray-600 mb-3">You have the right to:</p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Access your personal information</li>
              <li>Correct inaccurate information</li>
              <li>Request deletion of your data</li>
              <li>Opt-out of marketing communications</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">7. Contact Us</h2>
            <p className="text-gray-600">
              If you have questions about this Privacy Policy, please contact us at{' '}
              <a href="mailto:privacy@shopzone.com" className="text-primary-600 hover:underline">
                privacy@shopzone.com
              </a>{' '}
              or visit our{' '}
              <Link href="/contact" className="text-primary-600 hover:underline">
                Contact Page
              </Link>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
