// Case file content for all five instruments, in homepage order (PLAN §5 / §7).
// All five case files owner-approved at the Phase 5 gate (2026-09-15).
// Every reading traces to its dossier section (`source`);
// /home/rayin/Projects/Testing/portfolio/CAPABILITY_<NAME>.md. Full table: web/README.md.
import type { InstrumentId } from './instruments';

export type CaseComponent = {
  id: string; title: string; label: string; body: string;
  // Named GLB node; `part` picks the child mesh by material name and anchors at its centre.
  node: string; part?: string;
  // Marker position inside the instrument stage, in percent (x, y).
  marker: readonly [number, number];
};
export type CaseReading = { value: number; suffix: string; label: string; context: string; source: string };
export type CaseFile = {
  id: InstrumentId; draft: boolean; deck: readonly string[]; brief: readonly string[]; context: string;
  instrumentHeading: readonly string[]; components: readonly CaseComponent[];
  flowHeading: readonly string[]; flow: readonly { title: string; body: string }[];
  readingsHeading: readonly string[]; readingsIntro: string; readings: readonly CaseReading[]; limits: readonly string[];
  tools: readonly string[];
  video: { duration: number; label: string; intro: string };
};

export const caseFiles: readonly CaseFile[] = [
  {
    id: 'crosscheck', draft: false,
    deck: ['Find the gaps.', 'Bring back proof.'],
    brief: [
      'Your app can work in one browser and fail in another. Different screens and user permissions make the gaps harder to spot.',
      'I build repeatable checks, then turn the results into a short list of issues with steps, screenshots and priorities.',
    ],
    context: 'Owned WordPress + CRM demo. Results shown here come from a test app with deliberately planted bugs.',
    instrumentHeading: ['Three lenses.', 'One target.'],
    // Revision 3: 01 → Lens3 (upper tube), 03 → Lens1, so left leaders never cross another lens.
    components: [
      { id: 'matrix', node: 'Lens3', marker: [12, 32], title: 'Browser matrix', label: 'Pages, screens & roles',
        body: 'I open the selected pages in Chromium, Firefox and WebKit, across screen sizes and user roles. Each visit checks for broken layouts, missing content and browser errors.' },
      { id: 'access', node: 'Lens2', marker: [88, 44], title: 'Access checks', label: 'Who can see what',
        body: 'I check each page against the intended permissions for each role. Suspected access leaks are reopened in a real browser before they enter the report.' },
      { id: 'flows', node: 'Lens1', marker: [12, 57], title: 'End-to-end flows', label: 'Check what was saved',
        body: 'I run tasks such as creating, searching and updating a record. After saving, I reload and check the stored data, so a success message cannot hide missing changes.' },
    ],
    flowHeading: ['From page visits', 'to a clear report.'],
    flow: [
      { title: 'Map the app', body: 'I discover pages and define who should be allowed to open each one.' },
      { title: 'Run the checks', body: 'Browser checks, permission checks and full user tasks collect results and screenshots.' },
      { title: 'Verify & sort', body: 'I confirm suspected access leaks, merge duplicates and remove expected behavior using documented rules.' },
      { title: 'Hand over the evidence', body: 'A spreadsheet and screenshot gallery show what failed, how to reproduce it and what needs attention first.' },
    ],
    readingsHeading: ['Measured on', 'the demo.'],
    readingsIntro: 'These are recorded results from the owned test app, not live counters or client production results.',
    readings: [
      { value: 1080, suffix: '', label: 'Test combinations', context: '40 pages × 3 browsers × 3 screen sizes × 3 roles.', source: '§3.1 / §7' },
      { value: 216, suffix: '', label: 'Permission checks', context: '72 pages × 3 roles. Suspected violations confirmed in Chromium desktop.', source: '§6 K5 / §9' },
      { value: 18, suffix: '', label: 'Unique issues from 881 signals', context: 'Duplicates merged and expected behavior removed by documented rules.', source: '§6 K7–K10 / §7 / §9' },
      { value: 12, suffix: '/12', label: 'Planted bugs caught', context: 'Controlled recall test on the owned target; not a guarantee for every app.', source: '§3.2 / §6 K10 / §7' },
    ],
    limits: [
      'The 881 signals include browser findings, permission violations and a failed user flow. They became 18 unique issues. A later clean-copy run changed the raw finding count while retaining the same 18 issues.',
      'Screen sizes are emulated. Permission violations were confirmed in Chromium desktop. This work checks web behavior and access rules; penetration testing, load testing and human judgment about business rules sit outside its scope.',
    ],
    tools: ['Python', 'Playwright', 'Chromium / Firefox / WebKit', 'httpx', 'tenacity', 'SQLite', 'openpyxl', 'unittest', 'Docker / Docker Compose', 'GNU Make', 'uv', 'matplotlib', 'Pillow', 'ffmpeg', 'WordPress / PHP'],
    video: { duration: 126.866667, label: 'CrossCheck demo with burned-in English captions',
      intro: 'English captions. No audio. Original demo footage, with its progress replay clearly labeled.' },
  },
  {
    id: 'surgeline', draft: false,
    deck: ['Every row sent once.', 'Every success proven.'],
    brief: [
      'Your platform only accepts data through a web form, and your spreadsheet has thousands of rows. A simple script can stop halfway, and after a restart nobody knows what was sent.',
      'I build a form-filling system that keeps its progress on disk, saves the confirmation number for every success and continues after a crash without sending anything twice.',
    ],
    context: 'Owned test form with synthetic records. The form fails 5% of submissions on purpose, so failures are part of the test.',
    instrumentHeading: ['Four dishes.', 'One work list.'],
    components: [
      { id: 'queue', node: 'DishPivot1', part: 'signal', marker: [12, 33], title: 'Work list', label: 'Loaded once, kept on disk',
        body: 'I load the spreadsheet into one work list stored on disk. Repeated rows are rejected on arrival, and loading the same file again adds nothing.' },
      { id: 'workers', node: 'DishPivot2', part: 'signal', marker: [88, 45], title: 'Parallel workers', label: 'Real browsers, one record each',
        body: 'Several headless browsers fill the form at the same time. Each record is held by one worker only, so two workers never submit the same row.' },
      { id: 'proof', node: 'DishPivot3', part: 'signal', marker: [12, 57], title: 'Confirmation proof', label: 'No number, no success',
        body: 'A submission only counts as successful when the confirmation number from the result page is saved. Rejected records keep a plain reason instead of disappearing.' },
    ],
    flowHeading: ['From spreadsheet', 'to confirmed rows.'],
    flow: [
      { title: 'Load the file', body: 'I stream the Excel or CSV file into the work list, and the database rejects repeated rows.' },
      { title: 'Fill the forms', body: 'Parallel browsers submit each record and read the confirmation number from the page.' },
      { title: 'Retry or set aside', body: 'Temporary errors are retried with growing waits. Permanent rejections stop at once and keep their reason.' },
      { title: 'Resume and report', body: 'After a crash, the run continues from the saved list. A live dashboard and a plain-language report show every outcome.' },
    ],
    readingsHeading: ['Measured on', 'the test form.'],
    readingsIntro: 'Recorded from a 50,000-row run on synthetic data against the owned test form, not a client platform.',
    readings: [
      { value: 48273, suffix: '', label: 'Submitted with a confirmation number', context: 'Of 49,950 unique records. The other 1,677 were recorded with a reason: rejected by validation or still failing after five attempts.', source: '§6 K2 / §7' },
      { value: 0, suffix: '', label: 'Duplicate submissions', context: 'After the run was force-stopped twice mid-way and restarted. Checked by database query.', source: '§6 K1 / K3 / §7' },
      { value: 7, suffix: '/7', label: 'Interrupted records recovered', context: 'Records held by a worker at the moment of shutdown returned to the list and were submitted once.', source: '§6 K1 / §7' },
      { value: 81915, suffix: '', label: 'Records per hour with 8 workers', context: 'Measured on one machine against the local test form, with no network delay or rate limit.', source: '§6 K7 / §7 / §9' },
    ],
    limits: [
      'The run used 50,000 synthetic rows; 50 deliberate duplicates were rejected, leaving 49,950 records. Larger volumes were not run, so any estimate beyond that is an extrapolation.',
      'Speed was measured against a local form with no network delay; a real platform’s own rate limit decides the real duration. Only authorized platforms are in scope, and captchas or anti-bot protections are never bypassed.',
    ],
    tools: ['Python', 'Playwright', 'SQLite', 'FastAPI', 'HTMX', 'Docker / Docker Compose', 'openpyxl', 'Faker', 'GNU Make', 'uv', 'unittest', 'ffmpeg'],
    video: { duration: 115.233333, label: 'SurgeLine demo with burned-in English captions',
      intro: 'English captions. No audio. Live footage comes from a separate 3,000-record demonstration run, labeled on screen.' },
  },
  {
    id: 'driftwatch', draft: false,
    deck: ['Collect every day.', 'Speak up when it changes.'],
    brief: [
      'Scrapers rarely break loudly. A page layout changes, a column goes empty, and the data keeps flowing until someone finds weeks of wrong reports.',
      'I build collection pipelines that run on a schedule, compare each day with the last good run and raise an alarm the same day a source changes.',
    ],
    context: 'Two public scraping sandboxes, one documentation site that passed a robots.txt check, and an owned test site where failures were planted.',
    instrumentHeading: ['One needle.', 'A daily trace.'],
    // Numbered top-down on the instrument; the needle leader meets its pivot so it clears the frame.
    components: [
      { id: 'alarms', node: 'NeedlePivot', marker: [12, 33], title: 'Alarms', label: 'Ten rules, written first',
        body: 'Ten alarm rules, with thresholds written before testing, flag empty runs, missing fields, error spikes and missed schedules. Normal changes stay quiet.' },
      { id: 'compare', node: 'driftwatchMount', part: 'ceramic', marker: [88, 45], title: 'Change detection', label: 'New, changed, removed',
        body: 'Every day is saved as a dated snapshot and compared with the last successful run, field by field. Timestamps are ignored, so a stable source shows no phantom changes.' },
      { id: 'collect', node: 'RollerPivot0', part: 'ceramic', marker: [12, 57], title: 'Daily collection', label: 'Polite, scheduled, resumable',
        body: 'A scheduled job collects each source at one request per second with an honest User-Agent. If it stops, it resumes from saved progress instead of starting over.' },
    ],
    flowHeading: ['From a source page', 'to a daily verdict.'],
    flow: [
      { title: 'Check the source first', body: 'I review robots.txt, terms and the sitemap before collecting, and look for a direct data endpoint before using a browser.' },
      { title: 'Collect on schedule', body: 'A daily timer runs the collection, and a separate watchdog reports a run that never happened.' },
      { title: 'Compare and judge', body: 'The pipeline validates required fields, compares today with the last good run and checks every alarm rule.' },
      { title: 'Report plainly', body: 'A short daily summary, a weekly Excel workbook and a four-line alert explain what changed and what needs attention.' },
    ],
    readingsHeading: ['Measured on', 'the test sources.'],
    readingsIntro: 'Recorded from the project’s own runs on sandboxes, a small documentation site and an owned test site, not client data.',
    readings: [
      { value: 11, suffix: '/11', label: 'Planted failures caught', context: 'Planted one at a time in the owned test site, with 0 false alarms. Three were normal changes that correctly stayed quiet.', source: '§1 / §6 K1 / §7' },
      { value: 1323, suffix: '', label: 'Records collected per day', context: 'Across four sources, with 0 duplicates and every required field filled.', source: '§6 K9 / §7' },
      { value: 12, suffix: '/12', label: 'Unattended runs finished cleanly', context: 'Three consecutive days, four sources a day, started by the scheduler with no manual step.', source: '§6 K5 / §7 / §9' },
      { value: 1, suffix: '', label: 'Request where a browser needed 8', context: 'A direct data endpoint found during setup replaced the browser for the same 10 quotes.', source: '§6 K8 / §7' },
    ],
    limits: [
      'The public sources did not change during the eight recorded days. Change detection was proven on the planted test site, and on one real, unplanned failure in the pipeline itself that the alarms caught.',
      'The real public source is a 23-page documentation site, chosen as the lowest-load option that passed the robots.txt check. Logins, captchas, protected sites and personal data are out of scope.',
    ],
    tools: ['Python', 'httpx', 'selectolax', 'tenacity', 'pydantic', 'SQLite', 'systemd timers', 'GNU Make', 'openpyxl', 'Anthropic Claude API', 'uv', 'unittest', 'ffmpeg'],
    video: { duration: 118.166667, label: 'DriftWatch demo with burned-in English captions',
      intro: 'English captions. No audio. Terminal footage was recorded in a disposable copy of the project.' },
  },
  {
    id: 'duewatch', draft: false,
    deck: ['Checked every morning.', 'Hard messages go to a person.'],
    brief: [
      'A contract sheet is only checked when someone remembers, and a busy inbox invites rushed automatic replies. One missed renewal or one wrong answer to an angry customer costs more than the time saved.',
      'I build daily expiry checks and message workflows that back up the sheet before writing, answer only simple questions and hand complaints and payment issues to a person.',
    ],
    context: 'Synthetic contracts and test messages. Every message “sent” here is a local mock log; live sending is not demonstrated.',
    instrumentHeading: ['Three orbits.', 'One daily clock.'],
    components: [
      { id: 'expiry', node: 'OrbitPivot0', part: 'ceramic', marker: [12, 33], title: 'Daily expiry check', label: 'Calendar-correct dates',
        body: 'Every morning each contract’s expiry is recomputed from its start date and term, with correct month and leap-year math. Unclear dates are flagged for a person instead of guessed.' },
      { id: 'triage', node: 'OrbitPivot1', part: 'alarm', marker: [88, 45], title: 'Safe message triage', label: 'Hand off when unsure',
        body: 'Simple price, stock and status questions get approved replies. Complaints, payment problems and anything unclear go to a person, with no draft attached.' },
      { id: 'followup', node: 'OrbitPivot2', part: 'ceramic', marker: [12, 57], title: '24-hour follow-up', label: 'One reminder, never two',
        body: 'If a customer has not replied within 24 hours, one reminder is logged. A customer who replied is skipped, and running the check again adds nothing.' },
    ],
    flowHeading: ['From a sheet and an inbox', 'to a safe routine.'],
    flow: [
      { title: 'Back up first', body: 'Before anything is written, the contract sheet is copied to a dated backup, and the original file stays untouched.' },
      { title: 'Recompute the dates', body: 'Each row gets its expiry date, days left and a status. A bad row is flagged without stopping the others.' },
      { title: 'Sort the messages', body: 'An n8n workflow sends each message to one set of rules that decides: approved reply or hand-off to a person.' },
      { title: 'Follow up once', body: 'A ledger records every reminder, so a follow-up is logged once and never repeated.' },
    ],
    readingsHeading: ['Measured on', 'synthetic data.'],
    readingsIntro: 'Recorded from the project’s own runs on synthetic contracts and 18 test messages, with mock delivery only.',
    readings: [
      { value: 200, suffix: '', label: 'Contracts checked per run', context: 'Including 45 deliberately difficult date rows, such as leap days and ambiguous formats.', source: '§3.1 / §3.3 / §8' },
      { value: 7, suffix: '/7', label: 'Renewals matched a manual audit', context: 'On the reference date, the engine and a hand check of all 200 rows found the same seven contracts.', source: '§6 K2 / §8' },
      { value: 6, suffix: '/6', label: 'Sensitive test messages sent to a person', context: 'Complaint, payment and unclear messages among 18 fixtures; none received an automatic draft.', source: '§6 K5 / §8' },
      { value: 12, suffix: '', label: 'Reminders, unchanged after six replays', context: 'The follow-up check ran six times in a row and still logged exactly 12 mock reminders.', source: '§6 K6 / §8' },
    ],
    limits: [
      'A later self-review attacked this project and found real gaps: a message mixing a price question with a complaint could still get an automatic reply, and repeating an inbox import can overwrite follow-up history. Both are documented findings, not fixed claims.',
      'The 18 test messages were written alongside the rules, so they are a baseline, not an accuracy guarantee. The daily timer fired on its own 8 times across 9 real days; a day the computer was off was not backfilled.',
    ],
    tools: ['Python', 'python-dateutil', 'SQLite', 'systemd timers', 'cron', 'n8n', 'Docker / Docker Compose', 'pytest', 'uv', 'GNU Make', 'ffmpeg'],
    video: { duration: 102.5, label: 'DueWatch demo with burned-in English captions',
      intro: 'English captions. No audio. Its seven-day segment replays simulated business dates; the real timer record is in the notes under Readings.' },
  },
  {
    id: 'brandwall', draft: false,
    deck: ['Find where brands break.', 'Close it with one rule.'],
    brief: [
      'A white-label product looks tidy with one demo logo. Then real brands arrive: very wide wordmarks, white logos on light themes, long names in other scripts and files that fail to load.',
      'I test every brand asset on every product surface and theme, measure where the layout breaks and deliver CSS rules that close each type of break.',
    ],
    context: 'Owned test app with 30 generated brand assets. No real logos are used, and no brand affiliation is claimed.',
    instrumentHeading: ['Light in.', 'Measured bands out.'],
    components: [
      { id: 'matrix', node: 'brandwallMount', part: 'ceramic', marker: [12, 33], title: 'Test matrix', label: '30 assets · 5 surfaces · 2 themes',
        body: 'Every generated brand asset is placed on five product surfaces in light and dark themes, then captured automatically. A plain control asset must produce no findings.' },
      { id: 'measure', node: 'PrismPivot', part: 'Prism', marker: [12, 57], title: 'Measurement', label: 'Numbers, not opinions',
        body: 'Each finding carries a measured value, its threshold and a screenshot: clipping in pixels, contrast ratios against WCAG 2.1 and name length per script.' },
      { id: 'fixes', node: 'SpectrumPivot', part: 'Spectrum0', marker: [88, 58], title: 'Fix rules', label: 'One rule per class',
        body: 'Findings are grouped into seven classes of break. Each class gets one CSS rule, then the same 300 combinations are tested again.' },
    ],
    flowHeading: ['From thirty assets', 'to seven rules.'],
    flow: [
      { title: 'Build the matrix', body: 'Generated assets reproduce hard cases: extreme ratios, white or black logos, non-Latin names and a missing file.' },
      { title: 'Capture every combination', body: 'Headless browsers capture 300 screenshots per run with no manual clicks.' },
      { title: 'Measure and find limits', body: 'Each capture is checked against locked thresholds, and sweeps find the exact ratio, brightness or name length where a design starts to fail.' },
      { title: 'Fix and prove it', body: 'Class-closing CSS is applied and the full matrix runs again, with a gallery, a workbook and before/after evidence.' },
    ],
    readingsHeading: ['Measured on', 'the test app.'],
    readingsIntro: 'Recorded from the project’s own runs on an owned test app with generated brand assets, not a client product.',
    readings: [
      { value: 300, suffix: '', label: 'Screenshots per run', context: '30 assets × 5 surfaces × 2 themes, captured in five consecutive runs with 0 failed cells.', source: '§3.1 / §6 K1 / §7' },
      { value: 18, suffix: '', label: 'Findings left after the fixes', context: 'Down from 186, with 0 new findings. The 18 are a missing file and a hairline logo, rejected at the asset check rather than hidden.', source: '§6 K7 / §7' },
      { value: 11, suffix: '', label: 'Breakpoints found by sweeps', context: 'Exact limits where a design starts to fail, from 716 measured observations.', source: '§6 K5 / §7' },
      { value: 0, suffix: '/300', label: 'False changes between identical runs', context: 'Baseline comparison proven twice; swapping one asset was flagged on its own.', source: '§6 K8 / §7' },
    ],
    limits: [
      'Captures ran at desktop sizes (1440×900, and 1200×630 for share cards) in Chromium. Other viewports and browsers belong to a separate QA sweep.',
      'The English evidence run used for the video recorded 182 findings instead of 186, because English names have different text widths. Both runs are kept separate rather than made to agree.',
    ],
    tools: ['Python', 'Playwright', 'Pillow', 'NumPy', 'FastAPI', 'Jinja2', 'Docker / Docker Compose', 'matplotlib', 'openpyxl', 'GNU Make', 'uv', 'unittest', 'ffmpeg'],
    video: { duration: 124.966667, label: 'BrandWall demo with burned-in English captions',
      intro: 'English captions. No audio. Filmed on the English evidence run described above, using generated brand assets only.' },
  },
];

export const caseIndex = (id: string | null | undefined) => caseFiles.findIndex(item => item.id === id);

// Persistent camera state shared by shell and scene: `index` is the instrument in view.
export type CaseView = { mix: number; active: boolean; index: number };
