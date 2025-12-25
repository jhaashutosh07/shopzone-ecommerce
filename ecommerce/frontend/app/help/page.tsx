'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChevronDown, ChevronUp, Search, Package, RotateCcw, CreditCard, Truck, User, ShieldCheck } from 'lucide-react';

const faqs = [
  {
    category: 'Orders',
    icon: Package,
    questions: [
      {
        q: 'How do I track my order?',
        a: 'Once your order is shipped, you will receive an email with tracking information. You can also track your order by visiting the "My Orders" section in your account.'
      },
      {
        q: 'Can I modify or cancel my order?',
        a: 'You can modify or cancel your order within 1 hour of placing it. After that, the order enters processing and cannot be changed. Please contact support for assistance.'
      },
      {
        q: 'What payment methods do you accept?',
        a: 'We accept all major credit/debit cards, UPI, net banking, and cash on delivery (COD) for eligible orders.'
      }
    ]
  },
  {
    category: 'Returns & Refunds',
    icon: RotateCcw,
    questions: [
      {
        q: 'What is your return policy?',
        a: 'We offer a 7-day return policy for most items. Products must be unused, in original packaging, and with all tags attached. Some items like undergarments and personalized products are non-returnable.'
      },
      {
        q: 'How do I initiate a return?',
        a: 'Go to "My Orders", select the order you want to return, and click "Request Return". Select a reason and our team will review your request within 24-48 hours.'
      },
      {
        q: 'When will I receive my refund?',
        a: 'Refunds are processed within 5-7 business days after we receive and verify the returned item. The amount will be credited to your original payment method.'
      }
    ]
  },
  {
    category: 'Shipping',
    icon: Truck,
    questions: [
      {
        q: 'How long does delivery take?',
        a: 'Standard delivery takes 5-7 business days. Express delivery (where available) takes 2-3 business days. Delivery times may vary based on your location.'
      },
      {
        q: 'Do you offer free shipping?',
        a: 'Yes! We offer free standard shipping on orders above Rs. 999. For orders below this amount, a flat shipping fee of Rs. 49 applies.'
      },
      {
        q: 'Do you ship internationally?',
        a: 'Currently, we only ship within India. We are working on expanding our shipping to other countries soon.'
      }
    ]
  },
  {
    category: 'Account',
    icon: User,
    questions: [
      {
        q: 'How do I create an account?',
        a: 'Click on "Sign Up" at the top of the page, enter your email and create a password. You can also sign up using your Google account for faster registration.'
      },
      {
        q: 'I forgot my password. What should I do?',
        a: 'Click on "Login" and then "Forgot Password". Enter your registered email address and we will send you a link to reset your password.'
      },
      {
        q: 'How do I update my profile information?',
        a: 'Go to "My Account" and click on "Edit Profile". You can update your name, phone number, and manage your saved addresses.'
      }
    ]
  }
];

export default function HelpPage() {
  const [openCategory, setOpenCategory] = useState<string | null>('Orders');
  const [openQuestion, setOpenQuestion] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFaqs = faqs.map(category => ({
    ...category,
    questions: category.questions.filter(
      q => q.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
           q.a.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.questions.length > 0);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-2">How can we help you?</h1>
        <p className="text-gray-600 text-center mb-8">Find answers to frequently asked questions</p>

        {/* Search */}
        <div className="relative mb-8">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search for answers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Link href="/orders" className="flex flex-col items-center p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
            <Package className="w-8 h-8 text-primary-600 mb-2" />
            <span className="text-sm font-medium">Track Order</span>
          </Link>
          <Link href="/returns" className="flex flex-col items-center p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
            <RotateCcw className="w-8 h-8 text-primary-600 mb-2" />
            <span className="text-sm font-medium">Returns</span>
          </Link>
          <Link href="/account" className="flex flex-col items-center p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
            <User className="w-8 h-8 text-primary-600 mb-2" />
            <span className="text-sm font-medium">My Account</span>
          </Link>
          <Link href="/contact" className="flex flex-col items-center p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
            <ShieldCheck className="w-8 h-8 text-primary-600 mb-2" />
            <span className="text-sm font-medium">Contact Us</span>
          </Link>
        </div>

        {/* FAQs */}
        <div className="space-y-4">
          {filteredFaqs.map((category) => (
            <div key={category.category} className="bg-white border rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenCategory(openCategory === category.category ? null : category.category)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <category.icon className="w-5 h-5 text-primary-600" />
                  <span className="font-semibold">{category.category}</span>
                  <span className="text-sm text-gray-500">({category.questions.length} questions)</span>
                </div>
                {openCategory === category.category ? (
                  <ChevronUp className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                )}
              </button>

              {openCategory === category.category && (
                <div className="border-t">
                  {category.questions.map((item, idx) => (
                    <div key={idx} className="border-b last:border-b-0">
                      <button
                        onClick={() => setOpenQuestion(openQuestion === `${category.category}-${idx}` ? null : `${category.category}-${idx}`)}
                        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
                      >
                        <span className="font-medium pr-4">{item.q}</span>
                        {openQuestion === `${category.category}-${idx}` ? (
                          <ChevronUp className="w-4 h-4 text-gray-500 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" />
                        )}
                      </button>
                      {openQuestion === `${category.category}-${idx}` && (
                        <div className="px-4 pb-4 text-gray-600">
                          {item.a}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Contact CTA */}
        <div className="mt-8 bg-primary-50 rounded-lg p-6 text-center">
          <h2 className="text-lg font-semibold mb-2">Still need help?</h2>
          <p className="text-gray-600 mb-4">Our support team is here to assist you</p>
          <Link
            href="/contact"
            className="inline-block px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Contact Support
          </Link>
        </div>
      </div>
    </div>
  );
}
