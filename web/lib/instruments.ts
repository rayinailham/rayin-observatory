// Homepage copy approved at Phase 3; DriftWatch revision approved at gate 7C (2026-09-17); DueWatch revision at gate 7D (2026-09-18).
// BrandWall chapter revision: Phase 7E, approved at gate 7E (2026-09-24).
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
    pitch: 'I make renewal dates visible and build message workflows with a human handoff — then test where their safeguards break.',
    reading: '200', unit: 'contracts checked per run', context: 'Synthetic contracts · mock delivery' },
  { id: 'brandwall', name: 'BrandWall', category: 'Visual design QA',
    pitch: 'I put extreme brand assets under light, measure where your layouts break and compare what changes after the fix.',
    reading: '300', unit: 'screenshots per run', context: '30 synthetic assets · 5 surfaces · 2 themes' },
] as const;

export type InstrumentId = typeof instruments[number]['id'];
// `from` is set only during a case-to-case chain: the outgoing instrument is then not index − 1.
// `orbit` is the visitor's own turn of the instrument (drag or tap), never scroll; `lead` is the camera
// angle the previous chapter was left at, so the hand-over to the next one starts where it stood.
export type ChapterState = { reveal: number; orbit: number; index: number; transition: number; outro: number; from?: number; lead?: number };
