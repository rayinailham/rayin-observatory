import type { MetadataRoute } from 'next';
import { indexable, siteUrl } from '@/lib/site';

// Preview and local builds stay out of search; the production deploy is open and lists its sitemap.
export default function robots(): MetadataRoute.Robots {
  return indexable
    ? { rules: { userAgent: '*', allow: '/' }, sitemap: new URL('/sitemap.xml', siteUrl).href }
    : { rules: { userAgent: '*', disallow: '/' } };
}
