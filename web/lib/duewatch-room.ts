// Phase 7D, copy approved at gate 7D (2026-09-18). Local illustrations only; no classifier, clock, scheduler or delivery API.
// Policy: CAPABILITY_DUEWATCH §3.1/3.4, §6 K6. Limits: §7 and §11.
export const contractStops = [61, 60, 8, 7, 0, -1] as const;
export const contractCategories = [
  { id: 'active', title: 'Active', boundary: 'More than 60 days', action: 'Keep it on the daily check.' },
  { id: 'due', title: 'Due soon', boundary: '8–60 days', action: 'Plan the renewal conversation.' },
  { id: 'renew', title: 'Needs renewal', boundary: '0–7 days', action: 'Put renewal on the agenda, including today.' },
  { id: 'expired', title: 'Expired', boundary: 'Before today', action: 'Review the agreement with a person.' },
  { id: 'bad', title: 'Bad data', boundary: 'Unclear date or term', action: 'Ask a person to correct the row. Keep checking the others.' },
] as const;
export function contractCategory(days: number | null) {
  if (days === null || !Number.isFinite(days)) return contractCategories[4];
  return contractCategories[days > 60 ? 0 : days >= 8 ? 1 : days >= 0 ? 2 : 3];
}
export const messageSamples = [
  { id: 'price', title: 'Price question', route: 'reply', detail: 'A simple price question follows the approved-text path.' },
  { id: 'stock', title: 'Stock question', route: 'reply', detail: 'A simple stock question follows the approved-text path.' },
  { id: 'status', title: 'Status question', route: 'reply', detail: 'A simple status question follows the approved-text path.' },
  { id: 'complaint', title: 'Complaint', route: 'human', detail: 'A complaint stops here. A person takes over; no reply draft is attached.' },
  { id: 'payment', title: 'Payment problem', route: 'human', detail: 'A payment problem stops here. A person takes over; no reply draft is attached.' },
  { id: 'unknown', title: 'Unclear message', route: 'human', detail: 'An unclear message stops here. Uncertainty belongs with a person.' },
] as const;
export type ReminderState = { logged: boolean; replied: boolean; result: 'pending' | 'logged' | 'duplicate' | 'replied' };
export const initialReminder: ReminderState = { logged: false, replied: false, result: 'pending' };
export function checkReminder(state: ReminderState, hours: number): ReminderState {
  if (state.replied) return { ...state, result: 'replied' };
  if (state.logged) return { ...state, result: 'duplicate' };
  if (hours <= 24) return { ...state, result: 'pending' };
  return { ...state, logged: true, result: 'logged' };
}
export const reminderResults = {
  pending: 'Pending. At exactly 24 hours, no reminder is logged.',
  logged: 'One mock reminder saved to this illustrated ledger.',
  duplicate: 'Already recorded. This check adds no duplicate.',
  replied: 'Customer replied. No further reminder is logged.',
};
export const auditFindings = [
  ['High', 'Import can erase reminder history', 'Sequential checks preserve the saved ledger. Re-importing an inbox can overwrite it and allow another reminder.'],
  ['High', 'Message safeguards have gaps', 'Mixed price-and-complaint messages can take the reply path. Optional AI drafts can bypass the forbidden-term filter.'],
  ['High', 'Workflow validator is out of date', 'The workflow runs, but its older validation gate rejects the newer export.'],
  ['High', 'Simulated dates need an explicit label', 'The video’s seven-day segment uses simulated business dates, not seven autonomous daily runs.'],
  ['Medium', 'Demo figures can drift', 'A running timer changes the data. Previously recorded cards and video are not a frozen snapshot.'],
  ['Medium', 'History failure can leave a partial result', 'The master remains safe, but a new derived sheet may have no matching history or summary.'],
  ['Medium', 'Handoff remains unfinished', 'Packaging and acceptance A9/A10 remain open in the dossier.'],
] as const;
