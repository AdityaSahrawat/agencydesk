import './globals.css';
import type { Metadata } from 'next';
import { Inter, Geist } from 'next/font/google';
import { Providers } from '@/providers';
import { Toaster } from 'sonner';
import { cn } from "@/lib/utils";

const geist = Geist({ subsets: ['latin'], variable: '--font-sans' });

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AgencyDesk — Agency Management Platform',
  description: 'Multi-tenant SaaS platform for agencies to manage clients, projects, and tasks.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={cn("font-sans", geist.variable)}>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster position="top-right" richColors />
        </Providers>
      </body>
    </html>
  );
}
