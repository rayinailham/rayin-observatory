import { notFound } from 'next/navigation';
import CaseFile from '@/components/case-file';
import { caseFiles } from '@/lib/cases';

// Five static case routes; any other slug is a 404 at build time.
export const dynamicParams = false;
export function generateStaticParams() { return caseFiles.map(item => ({ slug: item.id })); }

export default async function CasePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const file = caseFiles.find(item => item.id === slug);
  if (!file) notFound();
  return <CaseFile key={file.id} id={file.id} />;
}
