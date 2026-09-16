// Phase 7A — CrossCheck inspection room. Copy approved by the owner at the 7A gate (2026-09-16).
// Every fact traces to portfolio/CAPABILITY_CROSSCHECK.md (section in `source`) or to one of the
// project's own evidence images copied by web/scripts/build_crosscheck_run.py. Table: web/README.md.

export type Priority = 'High' | 'Medium' | 'Low';
export type FindingLayer = 'matrix' | 'access' | 'flow';

export type Finding = {
  id: string; priority: Priority; kind: string; lens: string; title: string; where: string;
  steps: readonly string[]; expected: string; actual: string; layer: FindingLayer;
  // Real screenshots: `before` is what the tester saw, `expected` the reference view when one exists.
  images: { before: { src: string; alt: string; label: string }; expected?: { src: string; alt: string; label: string } };
  caption: string; source: string;
};

// The chapter strip names the three lanes the lenses sweep; each lane holds 3 screen sizes × 3 roles.
export const scanLanes = ['Chromium', 'Firefox', 'WebKit'] as const;

// "How it works" keeps the four approved step titles and bodies (Phase 5 gate); only `readout` is new.
export const inspectionSteps = [
  { title: 'Map the app', body: 'I discover pages and define who should be allowed to open each one.',
    readout: '72 pages found · 40 in the matrix', source: '§3.1 / §6 K1' },
  { title: 'Run the checks', body: 'Browser checks, permission checks and full user tasks collect results and screenshots.',
    readout: '1,080 visits · 422 flagged · 216 access checks · 5 flows', source: '§6 K2 / K5 / K6' },
  { title: 'Verify & sort', body: 'I confirm suspected access leaks, merge duplicates and remove expected behavior using documented rules.',
    readout: '881 raw signals · 562 removed by declared rules', source: '§6 K7' },
  { title: 'Hand over the evidence', body: 'A spreadsheet and screenshot gallery show what failed, how to reproduce it and what needs attention first.',
    readout: '18 unique issues · 3 High · 14 Medium · 1 Low', source: '§6 K7 / §7' },
] as const;

export const inspectionNote = 'Cells come from the recorded demo run’s result files; the sorting step is simplified to whole page rows. A replay, not a live run.';

export const findings: readonly Finding[] = [
  {
    id: 'CC-003', priority: 'High', kind: 'Data loss', lens: 'End-to-end flows', layer: 'flow',
    title: 'CRM Owner changes disappear after saving',
    where: 'Chromium · Desktop · Editor',
    steps: ['Sign in as Editor.', 'Open /wp-admin/.', 'Edit both fields, save, reload, and compare both values.'],
    expected: 'The title and CRM Owner remain saved after reloading.',
    actual: 'CRM Owner disappears and is appended to the title after reloading.',
    images: { before: { src: '/images/crosscheck/cc-003-actual.png', label: 'After reload',
      alt: 'WordPress editor after reloading: the post title now ends with the CRM Owner value that should have been saved in its own field' } },
    caption: 'WordPress said “Post updated”. Only the check after reloading shows the owner value landed in the title.',
    source: '§6 K6 / K8 · flow screenshot at the failed step',
  },
  {
    id: 'CC-001', priority: 'High', kind: 'Access leak', lens: 'Access checks', layer: 'access',
    title: 'Viewer can open the internal user directory',
    where: 'Chromium · Desktop · Editor and Viewer',
    steps: ['Sign in as Viewer.', 'Open /admin/users/.', 'Compare with /admin/settings/, which refuses Viewer.'],
    expected: 'Access is denied with 403.',
    actual: 'The user directory is visible to Viewer (HTTP 200).',
    images: {
      before: { src: '/images/crosscheck/cc-001-before.png', label: 'What the user sees',
        alt: 'User Administration page listing the internal user directory while signed in as Viewer, outlined in red' },
      expected: { src: '/images/crosscheck/cc-001-expected.png', label: 'Expected',
        alt: 'A plain forbidden notice, outlined in green: settings require administrator privileges' },
    },
    caption: 'Another admin page denies Viewer, but this directory exposes its users. Reopened in a real browser before it was reported.',
    source: '§6 K5 · V4 before/after 3',
  },
  {
    id: 'CC-017', priority: 'Medium', kind: 'Layout', lens: 'Browser matrix', layer: 'matrix',
    title: 'Wide report forces horizontal scrolling on mobile',
    where: 'Mobile 390 px · Chromium, Firefox and WebKit',
    steps: ['Open /wide-report/ on a 390 px wide screen.', 'Open the same page at 768 px and compare.'],
    expected: 'The table fits the screen, as it does at 768 px.',
    actual: 'At 390 px the content extends beyond the screen and the page scrolls sideways.',
    images: {
      before: { src: '/images/crosscheck/cc-017-before.png', label: 'What the user sees · 390 px',
        alt: 'Quarterly Report page on a phone-sized screen, its report banner cut off at the right edge, outlined in red' },
      expected: { src: '/images/crosscheck/cc-017-expected.png', label: 'Expected · 768 px',
        alt: 'The same Quarterly Report page on a tablet-sized screen, the banner fully visible, outlined in green' },
    },
    caption: 'Flagged in every phone-sized visit and none of the wider ones, so the report names the device instead of nine duplicates.',
    source: '§3.2 PB-04 / §6 K7 · V1 heatmap · V4 before/after 1',
  },
  {
    id: 'CC-015', priority: 'Medium', kind: 'Overlap', lens: 'Browser matrix', layer: 'matrix',
    title: 'Toolbar buttons overlap',
    where: 'Every browser, screen size and role',
    steps: ['Open /overlap-toolbar/.', 'Try to press Save view.'],
    expected: 'The controls stack without overlapping.',
    actual: 'The Export button covers part of Save; the controls overlap by 37%.',
    images: {
      before: { src: '/images/crosscheck/cc-015-before.png', label: 'What the user sees',
        alt: 'Action Toolbar page where the Export view button sits on top of the Save view button, outlined in red' },
      expected: { src: '/images/crosscheck/cc-015-expected.png', label: 'Fix preview',
        alt: 'The same page with Save view and Export view stacked one above the other, outlined in green' },
    },
    caption: 'Twenty-seven visits raised the same overlap. Triage merged them into one row with one screenshot.',
    source: '§3.2 PB-10 / §3.3 / §6 K7 · V1 heatmap · V4 before/after 2',
  },
];

export const findingsIntro = 'Pick a finding. Each one carries the steps to reproduce it, what should happen, what happened, and the screenshot it was checked against.';
