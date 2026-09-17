// Homepage copy approved at Phase 3; DriftWatch revision approved at gate 7C (2026-09-17).
// Exact dossier sections and proof context: web/README.md, Copy provenance.
export const instruments = [
  { id: 'crosscheck', name: 'CrossCheck', category: 'Web QA',
    pitch: 'I test your web app across browsers, screen sizes and user roles, then deliver a clear list of issues.',
    reading: '1,080', unit: 'test combinations', context: 'On an owned demo app' },
  { id: 'surgeline', name: 'SurgeLine', category: 'Form automation',
    pitch: 'I turn your spreadsheet into a resumable form-filling workflow, with a confirmation number for every success.',
    reading: '50,000', unit: 'records processed', context: 'Synthetic data · owned test form' },
  { id: 'driftwatch', name: 'DriftWatch', category: 'Data monitoring',
    pitch: 'I keep dated snapshots of your web data, show what changed and flag when collection can no longer be trusted.',
    reading: '11/11', unit: 'test scenarios handled', context: 'Includes normal-change controls' },
  { id: 'duewatch', name: 'DueWatch', category: 'Expiry & follow-up',
    pitch: 'I build daily expiry checks and follow-up workflows that hand sensitive messages to a person.',
    reading: '200', unit: 'contracts checked per run', context: 'Synthetic contracts · mock delivery' },
  { id: 'brandwall', name: 'BrandWall', category: 'Visual design QA',
    pitch: 'I test brand assets across your product surfaces and themes, then report where layouts break and which CSS rules fix them.',
    reading: '300', unit: 'screenshots per run', context: 'Generated brands · owned test app' },
] as const;

export type InstrumentId = typeof instruments[number]['id'];
// `from` is set only during a case-to-case chain: the outgoing instrument is then not index − 1.
export type ChapterState = { reveal: number; orbit: number; index: number; transition: number; outro: number; from?: number };
