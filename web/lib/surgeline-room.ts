// Phase 7B (approved at gate 2026-09-17). Recorded facts: portfolio/CAPABILITY_SURGELINE.md §3–4, §6 K1/K2/K3/K5/K7, §7, §9.
// Records A–F and DEMO-* receipts are a deliberately fictional illustration, not samples from the recorded run.
export type DispatchStage = 'ready' | 'sending' | 'crashed' | 'resuming' | 'complete';
export type DispatchAction = 'start' | 'crash' | 'resume' | 'finish' | 'reset';
export type RecordState = 'queued' | 'sending' | 'stranded' | 'recovering' | 'confirmed' | 'rejected' | 'dead-letter';

// Guarded transitions: a repeated or out-of-order action leaves the stage unchanged (rapid taps never queue).
export function dispatchStage(stage: DispatchStage, action: DispatchAction): DispatchStage {
  if (action === 'reset') return 'ready';
  if (stage === 'ready' && action === 'start') return 'sending';
  if (stage === 'sending' && action === 'crash') return 'crashed';
  if (stage === 'crashed' && action === 'resume') return 'resuming';
  if (stage === 'resuming' && action === 'finish') return 'complete';
  return stage;
}

export const dispatchCopy: Record<DispatchStage, { title: string; body: string; button: string; action: DispatchAction }> = {
  ready: { title: 'Six records, saved before anything is sent.', body: 'The spreadsheet is already a work list on disk. Start the dispatch: three browsers each claim one record.', button: 'Start dispatch', action: 'start' },
  sending: { title: 'B reached the form. Its receipt is not saved.', body: 'A is confirmed. C was rejected, with its reason kept. Browser 2 still holds B. Cut that browser now.', button: 'Cut browser 2', action: 'crash' },
  crashed: { title: 'The browser stopped. The work list stayed.', body: 'B is stranded: claimed on disk, no receipt. A keeps its receipt and C its reason. Neither goes back in line.', button: 'Resume from the saved list', action: 'resume' },
  resuming: { title: 'The claim expires. B goes back in line.', body: 'B is sent again. The owned test form recognises B and returns the same receipt, so nothing is recorded twice. A is not sent again.', button: 'Recovering…', action: 'finish' },
  complete: { title: 'Every record has an outcome.', body: 'Four receipts, one rejection with its reason, one record parked after five attempts. B was sent twice and recorded once.', button: 'Replay demonstration', action: 'reset' },
};

export const exampleRecords = ['A', 'B', 'C', 'D', 'E', 'F'] as const;
export type ExampleRecord = typeof exampleRecords[number];
// Browser (lane) that claims each record in the illustration.
export const recordLane: Record<ExampleRecord, 1 | 2 | 3> = { A: 1, B: 2, C: 3, D: 1, E: 3, F: 1 };

export function recordState(id: ExampleRecord, stage: DispatchStage): RecordState {
  if (stage === 'ready') return 'queued';
  if (id === 'A') return 'confirmed';
  if (id === 'C') return 'rejected';
  if (stage === 'complete') return id === 'F' ? 'dead-letter' : 'confirmed';
  if (id === 'B') return stage === 'crashed' ? 'stranded' : stage === 'resuming' ? 'recovering' : 'sending';
  return stage === 'resuming' ? 'sending' : 'queued';
}

// Times each record reached the form once the stage has settled. B: twice, one receipt. F: five attempts.
export function recordSends(id: ExampleRecord, stage: DispatchStage) {
  const state = recordState(id, stage);
  if (state === 'queued') return 0;
  if (id === 'B') return stage === 'resuming' || stage === 'complete' ? 2 : 1;
  if (id === 'F') return stage === 'complete' ? 5 : 0;
  return state === 'sending' ? 0 : 1;
}

// Where a record rests on the board when a stage has settled. Slot names match `data-slot` in DispatchBoard.
export function recordSlot(id: ExampleRecord, stage: DispatchStage) {
  const queue = `queue-${exampleRecords.indexOf(id)}`;
  if (stage === 'ready') return queue;
  if (id === 'C') return 'rejected-0';
  if (stage === 'sending' || stage === 'crashed') return id === 'A' ? 'ok-0' : id === 'B' ? 'lane-2-end' : queue;
  return { A: 'ok-0', D: 'ok-1', E: 'ok-2', B: 'ok-3', F: 'dead-0' }[id];
}

export function recordNote(id: ExampleRecord, stage: DispatchStage) {
  const state = recordState(id, stage);
  const sends = recordSends(id, stage);
  switch (state) {
    case 'confirmed': return `Receipt DEMO-${id} saved · sent ${sends}×${id === 'B' ? ', same receipt' : ''}`;
    case 'rejected': return 'Validation rejected · reason kept · not retried';
    case 'dead-letter': return 'Server error on all 5 attempts · last error kept';
    case 'stranded': return 'Claimed on disk · browser offline · no receipt';
    case 'recovering': return 'Claim expired · sent again';
    case 'sending': return `Claimed by browser ${recordLane[id]} · awaiting receipt`;
    default: return 'Waiting in the saved work list';
  }
}

export const recordedOutcomes = [
  { id: 'confirmed', value: 48273, label: 'Confirmed', reason: 'A confirmation number saved for every success. None empty; none repeated.' },
  { id: 'rejected', value: 844, label: 'Rejected', reason: 'Permanent validation failure. Recorded with a reason, without retrying.' },
  { id: 'dead-letter', value: 833, label: 'Dead-letter', reason: 'Still failing after five attempts. Parked with the last error for review.' },
] as const;
