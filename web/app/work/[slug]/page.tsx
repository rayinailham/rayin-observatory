import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import CaseFile from '@/components/case-file';
import { caseFiles } from '@/lib/cases';
import { caseShare, siteName } from '@/lib/site';

// Five static case routes; any other slug is a 404 at build time.
export const dynamicParams = false;
export function generateStaticParams() { return caseFiles.map(item => ({ slug: item.id })); }

type Props = { params: Promise<{ slug: string }> };

// Each case shares its own card: title, approved pitch, headline reading with its limit (lib/site.ts).
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const share = caseShare(slug);
  if (!share) return {};
  const url = `/work/${slug}`;
  return {
    title: share.title,
    description: share.description,
    alternates: { canonical: url },
    openGraph: { type: 'article', siteName, locale: 'en_US', url, title: share.title, description: share.social, images: [share.image] },
    twitter: { card: 'summary_large_image', title: share.title, description: share.social, images: [share.image] },
  };
}

export default async function CasePage({ params }: Props) {
  const { slug } = await params;
  const file = caseFiles.find(item => item.id === slug);
  if (!file) notFound();
  return <CaseFile key={file.id} id={file.id} />;
}
