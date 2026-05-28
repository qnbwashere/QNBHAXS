import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'FC 26 SBC Optimizer — AI-Powered Squad Building Challenges',
  description:
    'Find the best value FC 26 SBCs with AI-powered cost-benefit analysis. Never waste coins again.',
  icons: { icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-fc-dark antialiased">{children}</body>
    </html>
  );
}
