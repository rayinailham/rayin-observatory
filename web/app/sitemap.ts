import type { MetadataRoute } from 'next';
import { caseFiles } from '@/lib/cases';
import { siteUrl } from '@/lib/site';

export default function sitemap(): MetadataRoute.Sitemap {
  return ['/', ...caseFiles.map(item => `/work/${item.id}`)].map(path => ({ url: new URL(path, siteUrl).href }));
}
