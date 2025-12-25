import Link from 'next/link';

export default function TermsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg border p-8">
        <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
        <p className="text-gray-500 mb-8">Last updated: December 2024</p>

        <div className="prose prose-gray max-w-none space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-3">1. Acceptance of Terms</h2>
            <p className="text-gray-600">
              By accessing and using ShopZone, you agree to be bound by these Terms of Service.
              If you do not agree to these terms, please do not use our services.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">2. Account Registration</h2>
            <p className="text-gray-600 mb-3">When creating an account, you agree to:</p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Provide accurate and complete information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Notify us immediately of any unauthorized access</li>
              <li>Be responsible for all activities under your account</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">3. Orders and Payments</h2>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>All prices are listed in Indian Rupees (INR) and include applicable taxes</li>
              <li>We reserve the right to refuse or cancel orders at our discretion</li>
              <li>Payment must be received before order processing</li>
              <li>For COD orders, payment is collected upon delivery</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">4. Shipping and Delivery</h2>
            <p className="text-gray-600">
              Delivery times are estimates and may vary. We are not liable for delays caused by
              courier services or circumstances beyond our control. Risk of loss passes to you
              upon delivery.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">5. Returns and Refunds</h2>
            <p className="text-gray-600">
              Returns are subject to our{' '}
              <Link href="/return-policy" className="text-primary-600 hover:underline">
                Return Policy
              </Link>.
              Refunds will be processed to the original payment method within 5-7 business days
              after the returned item is received and verified.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">6. Product Information</h2>
            <p className="text-gray-600">
              We strive to display accurate product information, including descriptions, images, and prices.
              However, we do not guarantee that all information is error-free. Colors may appear differently
              on various screens.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">7. Intellectual Property</h2>
            <p className="text-gray-600">
              All content on ShopZone, including logos, images, and text, is our property or licensed to us.
              You may not use, reproduce, or distribute any content without our written permission.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">8. Prohibited Activities</h2>
            <p className="text-gray-600 mb-3">You agree not to:</p>
            <ul className="list-disc pl-6 text-gray-600 space-y-2">
              <li>Use the site for any unlawful purpose</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Submit false or misleading information</li>
              <li>Interfere with the proper functioning of the site</li>
              <li>Abuse the return policy or engage in fraudulent returns</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">9. Limitation of Liability</h2>
            <p className="text-gray-600">
              ShopZone shall not be liable for any indirect, incidental, special, or consequential damages
              arising from your use of our services. Our total liability shall not exceed the amount paid
              for the specific product or service in question.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">10. Changes to Terms</h2>
            <p className="text-gray-600">
              We reserve the right to modify these terms at any time. Changes will be effective immediately
              upon posting. Your continued use of the site constitutes acceptance of the modified terms.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">11. Contact</h2>
            <p className="text-gray-600">
              For questions about these Terms of Service, please{' '}
              <Link href="/contact" className="text-primary-600 hover:underline">
                contact us
              </Link>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
