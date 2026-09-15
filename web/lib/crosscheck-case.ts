// DRAFT. Source: CAPABILITY_CROSSCHECK.md; section-level provenance in web/README.md.
export const components = [
  { id: 'matrix', node: 'Lens1', title: 'Browser matrix', label: 'Pages, screens & roles',
    body: 'I open the selected pages in Chromium, Firefox and WebKit, across screen sizes and user roles. Each visit checks for broken layouts, missing content and browser errors.' },
  { id: 'access', node: 'Lens2', title: 'Access checks', label: 'Who can see what',
    body: 'I check each page against the intended permissions for each role. Suspected access leaks are reopened in a real browser before they enter the report.' },
  { id: 'flows', node: 'Lens3', title: 'End-to-end flows', label: 'Check what was saved',
    body: 'I run tasks such as creating, searching and updating a record. After saving, I reload and check the stored data, so a success message cannot hide missing changes.' },
] as const;

export const readings = [
  { value: 1080, suffix: '', label: 'Test combinations', context: '40 pages × 3 browsers × 3 screen sizes × 3 roles.', source: '§3.1 / §7' },
  { value: 216, suffix: '', label: 'Permission checks', context: '72 pages × 3 roles. Suspected violations confirmed in Chromium desktop.', source: '§6 K5 / §9' },
  { value: 18, suffix: '', label: 'Unique issues from 881 signals', context: 'Duplicates merged and expected behavior removed by documented rules.', source: '§6 K7–K10 / §7 / §9' },
  { value: 12, suffix: '/12', label: 'Planted bugs caught', context: 'Controlled recall test on the owned target; not a guarantee for every app.', source: '§3.2 / §6 K10 / §7' },
] as const;

export const caseTools = ['Python', 'Playwright', 'Chromium / Firefox / WebKit', 'httpx', 'tenacity', 'SQLite', 'openpyxl', 'unittest', 'Docker / Docker Compose', 'GNU Make', 'uv', 'matplotlib', 'Pillow', 'ffmpeg', 'WordPress / PHP'];

export type CaseView = { mix: number; active: boolean };
