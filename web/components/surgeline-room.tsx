'use client';

import { useLayoutEffect, useReducer, useRef } from 'react';
import { gsap } from 'gsap';
import {
  dispatchCopy, dispatchStage, exampleRecords, recordedOutcomes, recordLane, recordNote, recordSends, recordSlot, recordState,
  type DispatchStage, type ExampleRecord, type RecordState,
} from '@/lib/surgeline-room';
import { useReducedMotion } from './use-reduced-motion';

type Chip = HTMLElement;

// Phase 7B (approved at gate 2026-09-17). The board is an illustration driven by the guarded stage reducer: chips carry records
// A–F from the saved list through three browser lanes into outcome bins. Motion is transform-only (GSAP);
// the chip's colour and send count change when it arrives, not when the stage changes.
function laneStatus(lane: 1 | 2 | 3, stage: DispatchStage) {
  if (stage === 'ready') return 'idle';
  if (stage === 'complete') return 'done';
  if (lane !== 2) return 'working';
  return stage === 'crashed' ? 'offline' : stage === 'resuming' ? 'restarted' : 'holding B';
}

export function DispatchRoom() {
  const [stage, dispatch] = useReducer(dispatchStage, 'ready');
  const reducedMotion = useReducedMotion();
  const board = useRef<HTMLDivElement>(null);
  const shown = useRef<DispatchStage | null>(null);
  const motion = useRef<gsap.core.Timeline[]>([]);
  const resize = useRef<(() => void) | null>(null);
  const copy = dispatchCopy[stage];

  useLayoutEffect(() => {
    const el = board.current;
    if (!el) return;
    const chip = (id: ExampleRecord) => el.querySelector<Chip>(`[data-chip="${id}"]`)!;
    const at = (slot: string) => {
      const frame = el.getBoundingClientRect();
      const box = el.querySelector(`[data-slot="${slot}"]`)!.getBoundingClientRect();
      return { x: box.left - frame.left - el.clientLeft, y: box.top - frame.top - el.clientTop };
    };
    // Tween targets are read when each leg starts, so a leg always ends on its slot as laid out at that moment.
    const to = (slot: string) => ({ x: () => at(slot).x, y: () => at(slot).y });
    const mark = (id: ExampleRecord, state: RecordState, sends: number) => {
      const c = chip(id);
      c.dataset.state = state;
      c.dataset.sends = String(sends);
    };
    const stop = () => { motion.current.forEach(t => t.kill()); motion.current = []; };
    const settle = (target: DispatchStage) => {
      stop();
      exampleRecords.forEach(id => {
        gsap.set(chip(id), { ...at(recordSlot(id, target)), opacity: 1 });
        delete chip(id).dataset.kept;
        mark(id, recordState(id, target), recordSends(id, target));
      });
      shown.current = target;
    };
    const timeline = () => {
      const t = gsap.timeline({ onComplete: () => { motion.current = motion.current.filter(m => m !== t); } });
      motion.current.push(t);
      return t;
    };
    // A record's trip down its browser lane: claim → travel to the form → reach it once more.
    const trip = (t: gsap.core.Timeline, id: ExampleRecord, start: number, sends: number, state: RecordState = 'sending') => {
      const lane = recordLane[id];
      t.to(chip(id), { ...to(`lane-${lane}-start`), duration: .36, ease: 'power2.inOut', onStart: () => mark(id, state, sends - 1) }, start)
        .to(chip(id), { ...to(`lane-${lane}-end`), duration: .66, ease: 'power1.inOut', onComplete: () => mark(id, state, sends) }, start + .36);
      return start + 1.02;
    };
    const land = (t: gsap.core.Timeline, id: ExampleRecord, slot: string, state: RecordState, sends: number, start: number) =>
      t.to(chip(id), { ...to(slot), duration: .42, ease: 'power2.inOut', onComplete: () => mark(id, state, sends) }, start);

    resize.current = () => {
      settle(stage);
      if (stage === 'resuming') dispatch('finish');
    };

    const previous = shown.current;
    if (previous === null || reducedMotion) {
      settle(stage);
      if (stage === 'resuming') {
        // No choreography to wait for: keep the recovery message readable, then settle.
        const timer = window.setTimeout(() => dispatch('finish'), 900);
        return () => window.clearTimeout(timer);
      }
      return;
    }
    if (previous === stage) return;
    shown.current = stage;

    if (stage === 'ready') {
      // Replay is explicit: the old outcomes fade away, then the same six records return to the saved list.
      stop();
      const t = timeline();
      const chips = exampleRecords.map(chip);
      t.to(chips, { opacity: 0, duration: .2, ease: 'power1.out' })
        .add(() => exampleRecords.forEach(id => { gsap.set(chip(id), at(recordSlot(id, 'ready'))); mark(id, 'queued', 0); }))
        .to(chips, { opacity: 1, duration: .26, stagger: .05, ease: 'power1.out' });
    } else if (stage === 'sending') {
      const t = timeline();
      land(t, 'A', 'ok-0', 'confirmed', 1, trip(t, 'A', 0, 1));
      trip(t, 'B', .22, 1);
      const rejected = trip(t, 'C', .44, 1);
      t.to(chip('C'), { x: `+=4`, duration: .06, repeat: 3, yoyo: true, ease: 'none' }, rejected);
      land(t, 'C', 'rejected-0', 'rejected', 1, rejected + .26);
    } else if (stage === 'crashed') {
      // Cutting the browser freezes B wherever its claim is; A and C finish the trips they already started.
      gsap.killTweensOf(chip('B'));
      mark('B', 'stranded', Number(chip('B').dataset.sends) || 0);
    } else if (stage === 'resuming') {
      gsap.killTweensOf(chip('B'));
      const t = timeline().eventCallback('onComplete', () => {
        motion.current = motion.current.filter(m => m !== t);
        dispatch('finish');
      });
      const a = chip('A');
      a.dataset.kept = 'true';
      t.add(() => { delete a.dataset.kept; }, 1.6);
      // B: the claim expires (lane 2 shows it), B returns to the list, is claimed again and reaches the form a second time.
      t.to(chip('B'), { ...to('queue-1'), duration: .45, ease: 'power2.inOut', onStart: () => mark('B', 'recovering', 1) }, .9);
      land(t, 'B', 'ok-3', 'confirmed', 2, trip(t, 'B', 1.35, 2, 'recovering'));
      land(t, 'D', 'ok-1', 'confirmed', 1, trip(t, 'D', .1, 1));
      land(t, 'E', 'ok-2', 'confirmed', 1, trip(t, 'E', .3, 1));
      // F: the server keeps failing. Each retry is counted; after the fifth attempt F is parked with its last error.
      let retry = trip(t, 'F', 1.55, 1);
      for (let n = 2; n <= 5; n++) {
        t.to(chip('F'), { x: '-=12', duration: .09, yoyo: true, repeat: 1, ease: 'power1.inOut', onComplete: () => mark('F', 'sending', n) }, retry);
        retry += .2;
      }
      land(t, 'F', 'dead-0', 'dead-letter', 5, retry + .04);
    } else {
      settle(stage);
    }
  }, [stage, reducedMotion]);

  // Resizing moves every slot: rest the chips at the current stage's pose.
  useLayoutEffect(() => {
    const el = board.current;
    if (!el) return;
    let width = el.clientWidth;
    let height = el.clientHeight;
    const observer = new ResizeObserver(() => {
      if (el.clientWidth === width && el.clientHeight === height) return;
      const widthChanged = el.clientWidth !== width;
      width = el.clientWidth;
      height = el.clientHeight;
      // A late font or a height change while idle only re-rests the chips; a new width also cuts motion short.
      if (widthChanged || motion.current.length === 0) resize.current?.();
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useLayoutEffect(() => () => { motion.current.forEach(t => t.kill()); }, []);

  const confirmed = exampleRecords.filter(id => recordState(id, stage) === 'confirmed').length;
  return <section className="case-section dispatch-room" data-stage={stage} aria-labelledby="flow-heading">
    <div className="dispatch-intro"><p className="section-kicker">How it works / Dispatch room</p>
      <h2 id="flow-heading">Cut the browser.<br />Keep the progress.</h2>
      <p>I save the work list and every outcome before moving on. Try a crash at the awkward moment: the form has accepted a record, but its receipt is not saved yet.</p>
      <p className="dispatch-disclosure">Interactive illustration · fictional records and receipts · time compressed. No forms are submitted here.</p>
    </div>
    <div className="dispatch-console">
      <div className="dispatch-flow">
        <ol className="dispatch-steps" aria-label="Dispatch sequence">
          <li><span>01 / Import</span><h3>Spreadsheet → saved list</h3><p>Repeated rows stay out. Each record has one owner.</p></li>
          <li><span>02 / Dispatch</span><h3>Browsers share the work</h3><p>Submit the form, then save its receipt.</p></li>
          <li><span>03 / Recover</span><h3>Reclaim unfinished work</h3><p>An expired claim releases the stranded record.</p></li>
          <li><span>04 / Reconcile</span><h3>Keep every outcome</h3><p>Confirmed, rejected or parked with a reason.</p></li>
        </ol>
        <div className="dispatch-board" ref={board} aria-hidden="true">
          <div className="board-queue"><p className="board-label">Saved work list<span>on disk</span></p>
            <div className="board-slots">{exampleRecords.map((id, i) => <i key={id} data-slot={`queue-${i}`} />)}</div></div>
          <div className="board-lanes">{([1, 2, 3] as const).map(lane => <div key={lane} className="board-lane" data-lane={lane} data-status={laneStatus(lane, stage)}>
            <p className="board-label">Browser {lane}<span>{laneStatus(lane, stage)}</span></p>
            <div className="board-track"><i data-slot={`lane-${lane}-start`} /><b /><i data-slot={`lane-${lane}-end`} /><em>Form</em></div>
          </div>)}</div>
          <div className="board-bins">
            <div className="board-bin" data-bin="ok"><p className="board-label">Confirmed<span>receipt saved</span></p><div className="board-slots">{[0, 1, 2, 3].map(i => <i key={i} data-slot={`ok-${i}`} />)}</div></div>
            <div className="board-bin" data-bin="rejected"><p className="board-label">Rejected<span>reason kept</span></p><div className="board-slots"><i data-slot="rejected-0" /></div></div>
            <div className="board-bin" data-bin="dead"><p className="board-label">Dead-letter<span>5 attempts</span></p><div className="board-slots"><i data-slot="dead-0" /></div></div>
          </div>
          {exampleRecords.map(id => <span key={id} className="dispatch-chip" data-chip={id} data-state="queued" data-sends="0">{id}</span>)}
        </div>
        <p className="board-note">Amber: in flight · green: receipt saved · red: failed with a reason · ×2 = reached the form twice. The 120-second claim expiry is compressed.</p>
        <div className="dispatch-control">
          <div aria-live="polite" aria-atomic="true"><h3>{copy.title}</h3><p>{copy.body}</p></div>
          <button className="case-button" data-dispatch-action={copy.action} disabled={stage === 'resuming'} onClick={() => dispatch(copy.action)}>{copy.button}<span aria-hidden="true">{stage === 'sending' ? '✕' : '→'}</span></button>
        </div>
      </div>
      <div className="dispatch-ledger">
        <div className="dispatch-ledger-title"><h3>Saved outcomes</h3><span><b data-confirmed-count>{confirmed}</b> / 6 confirmed</span></div>
        <ul>{exampleRecords.map(id => {
          const state = recordState(id, stage);
          return <li key={id} data-record={id} data-status={state}><span className="dispatch-record-id">{id}</span><div><strong>{state}</strong><small>{recordNote(id, stage)}</small></div><span className="dispatch-status-mark" aria-hidden="true">{state === 'confirmed' ? '✓' : state === 'rejected' || state === 'dead-letter' || state === 'stranded' ? '!' : '·'}</span></li>;
        })}</ul>
        <p className="dispatch-rule">Already confirmed → stays confirmed.</p>
      </div>
    </div>
    <p className="dispatch-boundary">Why sending B again is safe here: the owned test form recognises the same record and returns the same confirmation. A real platform needs that guarantee checked first. This illustration cuts one browser; the recorded test below killed the entire worker group twice.</p>
  </section>;
}

export function DispatchEvidence() {
  return <section className="case-section dispatch-evidence" aria-labelledby="dispatch-evidence-heading">
    <p className="section-kicker">Recorded run / August 2026</p><h2 id="dispatch-evidence-heading">Finished processing.<br />Not all successful.</h2>
    <p>Snapshot from my owned local form, using synthetic data. These totals come from the recorded run, not the illustration above.</p>
    <div className="dispatch-intake"><span><strong>50,000</strong> input rows</span><span aria-hidden="true">→</span><span><strong>49,950</strong> unique records</span><small>50 duplicate input rows rejected at import</small></div>
    <div className="dispatch-proof-grid"><div className="dispatch-checkpoints"><h3>Confirmed progress survived both kills</h3><ol>
      <li><span>Before kill 1</span><strong>10,621</strong></li><li><span>Before kill 2</span><strong>21,508</strong></li><li><span>Final saved receipts</span><strong>48,273</strong></li>
    </ol><p><b>0 duplicate submissions.</b> All 7 stranded records recovered. Checked against the queue and target databases.</p></div>
    <div className="dispatch-outcomes">{recordedOutcomes.map(outcome => <article key={outcome.id} data-outcome={outcome.id}><strong>{outcome.value.toLocaleString('en-US')}</strong><div><h3>{outcome.label}</h3><p>{outcome.reason}</p></div></article>)}</div></div>
    <p className="dispatch-boundary"><b>6 million records were never run.</b> The estimate is about 3.0 days, or 4.1 days conservatively, on one machine against a local target with no network delay or rate limit. A real platform’s limits decide the actual duration.</p>
    <p className="dispatch-source">Source: SurgeLine capability dossier · §6 K1–K2, K7 · §7 · §9. Recorded snapshot, not live telemetry.</p>
  </section>;
}
