import type { Metadata, Viewport } from 'next';
import { preload } from 'react-dom';
import ObservatoryShell from '@/components/observatory-shell';
import { author, indexable, siteDescription, siteName, siteUrl } from '@/lib/site';
import 'lenis/dist/lenis.css';
import './globals.css';

const homeImage = { url: '/og/home.jpg', width: 1200, height: 630, alt: `${siteName}: ${author}, automation engineer. I automate. I test.` };
export const metadata: Metadata = {
  metadataBase: siteUrl,
  title: { default: `${siteName} | ${author}`, template: `%s | ${author}` },
  description: siteDescription,
  applicationName: siteName,
  authors: [{ name: author }],
  creator: author,
  alternates: { canonical: '/' },
  robots: indexable ? { index: true, follow: true } : { index: false, follow: false },
  openGraph: {
    type: 'website', siteName, locale: 'en_US', url: '/',
    title: `${siteName} | ${author}`, description: siteDescription, images: [homeImage],
  },
  twitter: { card: 'summary_large_image', title: `${siteName} | ${author}`, description: siteDescription, images: [homeImage] },
};
export const viewport: Viewport = { themeColor: '#0B1020', width: 'device-width', initialScale: 1 };

// Enter waits for the hero. Start Saturn and the Draco decoder with the HTML instead of after
// the 3D chunk runs; `fetch` + anonymous CORS matches three's FileLoader, so the preloads are reused.
const HERO_ASSETS = ['/models/ambient.glb', '/draco/draco_wasm_wrapper.js', '/draco/draco_decoder.wasm'];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  HERO_ASSETS.forEach(href => preload(href, { as: 'fetch', crossOrigin: 'anonymous' }));
  return <html lang="en"><body><ObservatoryShell>{children}</ObservatoryShell><noscript><p className="noscript-note">Rayin Observatory requires JavaScript for its interactive entrance.</p></noscript></body></html>;
}
