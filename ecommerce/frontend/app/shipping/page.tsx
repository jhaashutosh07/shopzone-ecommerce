import { Truck, Clock, MapPin, Package, CheckCircle } from 'lucide-react';

export default function ShippingPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border p-8">
          <h1 className="text-3xl font-bold mb-6">Shipping Information</h1>

          {/* Shipping Highlights */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="bg-primary-50 rounded-lg p-4 text-center">
              <Truck className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-semibold">Free Shipping</p>
              <p className="text-sm text-gray-600">On orders above Rs. 999</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <Clock className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="font-semibold">5-7 Days</p>
              <p className="text-sm text-gray-600">Standard delivery</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <MapPin className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="font-semibold">Pan India</p>
              <p className="text-sm text-gray-600">We deliver everywhere</p>
            </div>
          </div>

          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-3">Delivery Options</h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border px-4 py-2 text-left">Shipping Method</th>
                      <th className="border px-4 py-2 text-left">Delivery Time</th>
                      <th className="border px-4 py-2 text-left">Cost</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-600">
                    <tr>
                      <td className="border px-4 py-2">
                        <div className="font-medium">Standard Delivery</div>
                        <div className="text-sm text-gray-500">Available for all locations</div>
                      </td>
                      <td className="border px-4 py-2">5-7 business days</td>
                      <td className="border px-4 py-2">
                        <div>Rs. 49</div>
                        <div className="text-sm text-green-600">Free above Rs. 999</div>
                      </td>
                    </tr>
                    <tr>
                      <td className="border px-4 py-2">
                        <div className="font-medium">Express Delivery</div>
                        <div className="text-sm text-gray-500">Metro cities only</div>
                      </td>
                      <td className="border px-4 py-2">2-3 business days</td>
                      <td className="border px-4 py-2">Rs. 99</td>
                    </tr>
                    <tr>
                      <td className="border px-4 py-2">
                        <div className="font-medium">Same Day Delivery</div>
                        <div className="text-sm text-gray-500">Select cities, order before 12 PM</div>
                      </td>
                      <td className="border px-4 py-2">Same day</td>
                      <td className="border px-4 py-2">Rs. 199</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Delivery Zones</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Zone A - Metro Cities</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Delhi NCR, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune
                  </p>
                  <ul className="text-sm text-gray-600">
                    <li>• Express & Same Day available</li>
                    <li>• Standard: 3-5 days</li>
                  </ul>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Zone B - Tier 2 Cities</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Jaipur, Lucknow, Ahmedabad, Surat, Nagpur, Indore, and more
                  </p>
                  <ul className="text-sm text-gray-600">
                    <li>• Express available</li>
                    <li>• Standard: 4-6 days</li>
                  </ul>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Zone C - Rest of India</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    All other serviceable pin codes
                  </p>
                  <ul className="text-sm text-gray-600">
                    <li>• Standard delivery only</li>
                    <li>• Standard: 5-7 days</li>
                  </ul>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Remote Areas</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Remote and difficult-to-reach areas
                  </p>
                  <ul className="text-sm text-gray-600">
                    <li>• Standard delivery only</li>
                    <li>• May take 7-10 days</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Order Tracking</h2>
              <div className="flex items-start gap-4">
                <Package className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
                <div className="text-gray-600">
                  <p className="mb-2">
                    Once your order is shipped, you will receive an email and SMS with tracking details.
                    You can track your order by:
                  </p>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Visiting the "My Orders" section in your account</li>
                    <li>Using the tracking link in your shipping confirmation email</li>
                    <li>Contacting our support team with your order ID</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Order Processing</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">1</div>
                  <div>
                    <p className="font-medium">Order Placed</p>
                    <p className="text-sm text-gray-500">Your order is confirmed</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">2</div>
                  <div>
                    <p className="font-medium">Processing</p>
                    <p className="text-sm text-gray-500">Order is being prepared (1-2 days)</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">3</div>
                  <div>
                    <p className="font-medium">Shipped</p>
                    <p className="text-sm text-gray-500">Package handed to courier partner</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center">
                    <CheckCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium">Delivered</p>
                    <p className="text-sm text-gray-500">Package delivered to your address</p>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Important Notes</h2>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>Delivery times are estimates and may vary due to unforeseen circumstances</li>
                <li>Orders placed on weekends/holidays are processed the next business day</li>
                <li>Large or heavy items may require additional shipping charges</li>
                <li>We will attempt delivery up to 3 times before returning the package</li>
                <li>Please ensure someone is available to receive the package</li>
                <li>Cash on Delivery (COD) is available for orders up to Rs. 10,000</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">Questions?</h2>
              <p className="text-gray-600">
                For shipping-related queries, please contact our support team at{' '}
                <a href="mailto:shipping@shopzone.com" className="text-primary-600 hover:underline">
                  shipping@shopzone.com
                </a>{' '}
                or call us at{' '}
                <a href="tel:1800123456" className="text-primary-600 hover:underline">
                  1800-123-456
                </a>.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
