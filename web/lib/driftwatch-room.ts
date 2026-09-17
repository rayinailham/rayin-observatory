// Phase 7C (approved at gate 2026-09-17). Facts: portfolio/CAPABILITY_DRIFTWATCH.md §4, §6 K1–3/K5, §7/9.
// The small snapshots below are invented teaching examples, never harvested evidence.
// Days are numbered, not dated: real calendar dates would collide with the recorded soak (01–03 Sep, no alarms).
export const sampleBaseline = [
  { id: '/guide', title: 'Getting started' },
  { id: '/notes', title: 'Release notes' },
  { id: '/help', title: 'Help centre' },
] as const;
export const sampleChanged = [
  { id: '/guide', title: 'Getting started with the API' },
  { id: '/help', title: 'Help centre' },
  { id: '/start', title: 'Quick start' },
] as const;
export const emptyCodes = ['ZERO_RECORDS', 'RECORD_COUNT_DROP', 'FIELD_COMPLETENESS_DROP', 'RUN_FAILED', 'CHURN_SPIKE'] as const;
export const monitoringScenarios = [
  { id: 'change', label: 'Source changes', kind: 'source', alarm: false, day: 2,
    heading: 'Changed data. Healthy collection.', summary: 'A title changed, a page appeared and another disappeared. These are ordinary source changes. Record them without raising a false alarm.',
    cause: 'Normal content edits', action: 'Review the field diff. Keep the snapshot as the next good baseline.', codes: [], source: '§6 K1 DO-01–03; §4' },
  { id: 'layout', label: 'Layout breaks', kind: 'source', alarm: true, day: 2,
    heading: 'Empty is an alarm.', summary: 'In this planted example, the source layout changed and the collector found no records. An empty collection does not prove that every page was deleted.',
    cause: 'Source structure changed · planted example', action: 'Check the page structure and extraction rules. Keep the last good baseline until collection succeeds.', codes: emptyCodes, source: '§6 K1 DO-04' },
  { id: 'pipeline', label: 'Collector fails', kind: 'pipeline', alarm: true, day: 2,
    heading: 'Same symptom. Different cause.', summary: 'The collector cannot reach its test source. In the recorded project failure, the daily runner had not started the local fixture. The source content had not disappeared.',
    cause: 'Pipeline setup failed · illustrated from a recorded incident', action: 'Check the runner and source availability before changing extraction rules. Zero rows alone cannot identify the cause.', codes: emptyCodes, source: '§6 K2' },
  { id: 'missing', label: 'Run never starts', kind: 'pipeline', alarm: true, day: 2,
    heading: 'No run. No healthy verdict.', summary: 'There is no current snapshot to compare. A separate watchdog catches the missing run even when the collection job never starts.',
    cause: 'Scheduled run missing', action: 'Check the timer and machine availability. Retain the last good snapshot; do not turn a missing run into an empty dataset.', codes: ['RUN_MISSING'], source: '§6 K1 DO-09; §6 K5' },
  { id: 'recovery', label: 'Recover next day', kind: 'recovery', alarm: false, day: 3,
    heading: 'Recovered. History kept.', summary: 'After a failed day, comparison still uses the last successful snapshot. The successful re-run resolves the evaluated alarms; their history stays on record.',
    cause: 'Collection restored after an empty run', action: 'Compare against Day 1, not the failed Day 2. Keep the failure and its resolution visible.', codes: [], source: '§4; §6 K2' },
] as const;
export type MonitoringScenario = typeof monitoringScenarios[number];
export const sourceLedger = [
  { name: 'Books', count: '1,000', role: 'Scraping sandbox · volume' },
  { name: 'Quotes', count: '100', role: 'Scraping sandbox · direct data endpoint' },
  { name: 'SEO metadata', count: '23', role: 'Public documentation pages · small, checked scope' },
  { name: 'Drift lab', count: '200', role: 'Owned fixture · planted failures' },
] as const;
export const monitoringSteps = [
  { title: 'Check the source', body: 'Review access rules and the sitemap before collecting metadata.' },
  { title: 'Keep each snapshot', body: 'Collect on schedule; retain a dated copy and saved progress.' },
  { title: 'Compare to the last good run', body: 'Match stable record IDs, then compare fields without volatile timestamps.' },
  { title: 'Explain the verdict', body: 'Report changes, judge alarm thresholds and flag missed runs independently.' },
] as const;
