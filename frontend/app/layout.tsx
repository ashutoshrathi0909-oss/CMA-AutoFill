import type { Metadata } from 'next';
import { Inter, Geist_Mono } from 'next/font/google';
import { AuthProvider } from '@/lib/auth-context';
import { QueryProvider } from '@/lib/hooks/query-provider';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'CMA AutoFill — Automated CMA Documents for CA Firms',
  description:
    'Automate Credit Monitoring Arrangement document creation. Reduce manual work from 3-4 hours to under 5 minutes per client.',
  keywords: ['CMA', 'Credit Monitoring Arrangement', 'CA Firms', 'Bank Loan', 'Financial Statements'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${geistMono.variable} font-sans antialiased`}>
        <QueryProvider>
          <AuthProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                style: {
                  background: '#1A2A44',
                  border: '1px solid rgba(148, 163, 184, 0.15)',
                  color: '#F1F5F9',
                },
              }}
            />
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
