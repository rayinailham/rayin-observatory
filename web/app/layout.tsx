import type { Metadata, Viewport } from 'next';
import ObservatoryShell from '@/components/observatory-shell';
import 'lenis/dist/lenis.css';
import './globals.css';

export const metadata: Metadata = {
  title: 'Rayin Observatory | Rayina Ilham',
  description: 'First light. A portfolio by Rayina Ilham.',
  robots: { index: false, follow: false },
};
export const viewport: Viewport = { themeColor: '#0B1020', width: 'device-width', initialScale: 1 };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><ObservatoryShell>{children}</ObservatoryShell><noscript><p className="noscript-note">Rayin Observatory requires JavaScript for its interactive entrance.</p></noscript></body></html>;
}
