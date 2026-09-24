// Phase 8: one place for the public URL and share-card copy used by metadata, robots and sitemap.
// On Vercel, VERCEL_PROJECT_PRODUCTION_URL is the project's production host (the owner's own domain
// once connected); locally the site falls back to the preview port. Only a production deploy is indexed.
import { caseFiles } from './cases';
import { instruments } from './instruments';

export const siteUrl = new URL(process.env.VERCEL_PROJECT_PRODUCTION_URL
  ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : 'http://localhost:8767');
export const indexable = process.env.VERCEL_ENV === 'production';

export const siteName = 'Rayin Observatory';
export const author = 'Rayina Ilham';
// Approved hero positioning line (app/page.tsx).
export const siteDescription = 'I’m an automation engineer. I build systems that test web apps, fill forms and monitor changing data.';

// Per-case share text: approved chapter pitch + reading + its limit (lib/instruments.ts), deck from lib/cases.ts.
export function caseShare(id: string) {
  const item = instruments.find(entry => entry.id === id);
  const file = caseFiles.find(entry => entry.id === id);
  if (!item || !file) return null;
  return {
    title: `${item.name} · ${item.category}`,
    description: item.pitch,
    social: `${file.deck.join(' ')} ${item.reading} ${item.unit} (${item.context}).`,
    image: { url: `/og/${id}.jpg`, width: 1200, height: 630, alt: `${item.name}: ${item.reading} ${item.unit}. ${item.context}.` },
  };
}
