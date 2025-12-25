'use client';

import './globals.css';
import { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { useStore } from '@/lib/store';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

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
    <html lang="en">
      <head>
        <title>ShopZone - Your One-Stop E-commerce Store</title>
        <meta name="description" content="Shop the best products at great prices" />
      </head>
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow">{children}</main>
        <Footer />
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}
