'use client';

import './globals.css';
import { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { Inter, Plus_Jakarta_Sans } from 'next/font/google';
import { useStore } from '@/lib/store';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });
const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-display' });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const checkAuth = useStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <html lang="en" className={`${inter.variable} ${jakarta.variable}`}>
      <head>
        <title>ShopZone — Shop Real Products, AI-Protected Returns</title>
        <meta
          name="description"
          content="ShopZone: real product catalog with transparent, AI-scored returns. Every return decision comes with an explanation."
        />
      </head>
      <body className="flex min-h-screen flex-col font-sans">
        <Header />
        <main className="flex-grow">{children}</main>
        <Footer />
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              borderRadius: '12px',
              background: '#0f172a',
              color: '#f8fafc',
              fontSize: '14px',
            },
          }}
        />
      </body>
    </html>
  );
}
