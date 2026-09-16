import type { Metadata, Viewport } from 'next';
import { preload } from 'react-dom';
import ObservatoryShell from '@/components/observatory-shell';
import 'lenis/dist/lenis.css';
import './globals.css';

export const metadata: Metadata = {
  title: 'Rayin Observatory | Rayina Ilham',
  description: 'First light. A portfolio by Rayina Ilham.',
  robots: { index: false, follow: false },
};
export const viewport: Viewport = { themeColor: '#0B1020', width: 'device-width', initialScale: 1 };

// Enter waits for the hero. Start Saturn and the Draco decoder with the HTML instead of after
// the 3D chunk runs; `fetch` + anonymous CORS matches three's FileLoader, so the preloads are reused.
const HERO_ASSETS = ['/models/ambient.glb', '/draco/draco_wasm_wrapper.js', '/draco/draco_decoder.wasm'];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  HERO_ASSETS.forEach(href => preload(href, { as: 'fetch', crossOrigin: 'anonymous' }));
  return <html lang="en"><body><ObservatoryShell>{children}</ObservatoryShell><noscript><p className="noscript-note">Rayin Observatory requires JavaScript for its interactive entrance.</p></noscript></body></html>;
}
