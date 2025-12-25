import Link from 'next/link';
import { CheckCircle, XCircle, Clock, Package, RotateCcw, CreditCard } from 'lucide-react';

export default function ReturnPolicyPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border p-8">
          <h1 className="text-3xl font-bold mb-6">Return & Refund Policy</h1>
          <p className="text-gray-500 mb-8">Last updated: December 2024</p>

          {/* Quick Overview */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="bg-primary-50 rounded-lg p-4 text-center">
              <Clock className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-semibold">7-Day Returns</p>
              <p className="text-sm text-gray-600">From delivery date</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <CreditCard className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="font-semibold">Full Refund</p>
              <p className="text-sm text-gray-600">Original payment method</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <Package className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="font-semibold">Free Pickup</p>
              <p className="text-sm text-gray-600">For eligible returns</p>
            </div>
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <RotateCcw className="w-5 h-5 text-primary-600" />
                Return Eligibility
              </h2>
              <p className="text-gray-600 mb-4">
                We want you to be completely satisfied with your purchase. You may return most items
                within 7 days of delivery for a full refund.
              </p>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-medium text-green-800 mb-2 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Eligible for Return
                  </h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Unused items in original packaging</li>
                    <li>• Items with all tags attached</li>
                    <li>• Defective or damaged products</li>
                    <li>• Wrong item received</li>
                    <li>• Items significantly different from description</li>
                  </ul>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <h3 className="font-medium text-red-800 mb-2 flex items-center gap-2">
                    <XCircle className="w-5 h-5" />
                    Not Eligible for Return
                  </h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Undergarments and innerwear</li>
                    <li>• Personalized/customized items</li>
                    <li>• Perishable goods</li>
                    <li>• Items marked as "Non-Returnable"</li>
                    <li>• Items without original packaging</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">How to Initiate a Return</h2>
              <ol className="list-decimal pl-6 text-gray-600 space-y-3">
                <li>
                  <strong>Login to your account</strong> and go to{' '}
                  <Link href="/orders" className="text-primary-600 hover:underline">My Orders</Link>
                </li>
                <li>
                  <strong>Select the order</strong> containing the item you wish to return
                </li>
                <li>
                  <strong>Click "Request Return"</strong> and select the item(s) and reason for return
                </li>
                <li>
                  <strong>Choose your preferred pickup date</strong> (free pickup for eligible orders)
                </li>
                <li>
                  <strong>Pack the item</strong> securely in its original packaging
                </li>
                <li>
                  <strong>Hand over the package</strong> to our pickup agent
                </li>
              </ol>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Refund Process</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Payment Method</th>
                      <th className="text-left py-2">Refund Timeline</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-600">
                    <tr className="border-b">
                      <td className="py-2">Credit/Debit Card</td>
                      <td className="py-2">5-7 business days</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">UPI</td>
                      <td className="py-2">2-3 business days</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Net Banking</td>
                      <td className="py-2">5-7 business days</td>
                    </tr>
                    <tr>
                      <td className="py-2">Cash on Delivery</td>
                      <td className="py-2">Bank transfer within 7-10 business days</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                * Refund timeline begins after the returned item is received and verified at our facility.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Exchange Policy</h2>
              <p className="text-gray-600">
                We currently do not offer direct exchanges. If you need a different size, color, or product,
                please return the original item for a refund and place a new order for the desired item.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Damaged or Defective Items</h2>
              <p className="text-gray-600">
                If you receive a damaged or defective item, please report it within 48 hours of delivery.
                Take photos of the damage and contact our support team. We will arrange for a priority
                pickup and provide a full refund or replacement at no additional cost.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">ML-Powered Return Assessment</h2>
              <p className="text-gray-600">
                Our platform uses machine learning to assess return requests. This helps us process legitimate
                returns faster while preventing fraudulent claims. Factors considered include order history,
                return patterns, and product condition. All decisions are subject to manual review upon request.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Need Help?</h2>
              <p className="text-gray-600">
                If you have questions about returns or need assistance, please visit our{' '}
                <Link href="/help" className="text-primary-600 hover:underline">Help Center</Link>{' '}
                or{' '}
                <Link href="/contact" className="text-primary-600 hover:underline">Contact Us</Link>.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
