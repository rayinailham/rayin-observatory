'use client';

import { useRef, useState, useEffect, type MouseEvent } from 'react';
import { contractStops, contractCategories, contractCategory, messageSamples, initialReminder, checkReminder, reminderResults, auditFindings } from '@/lib/duewatch-room';

// Phase 7D (approved at gate 7D): two independent explanatory modules, never a live inbox.
export function TimeControlRoom() {
  const [module, setModule] = useState('agenda');
  const [stop, setStop] = useState(0);
  const [badDate, setBadDate] = useState(false);
  const [message, setMessage] = useState(3);
  const [reminder, setReminder] = useState(initialReminder);
  const [hours, setHours] = useState(24);
  const [motion, setMotion] = useState(false);
  const hand = useRef<SVGLineElement>(null);
  const card = useRef<HTMLDivElement>(null);
  const handMotion = useRef<Animation | null>(null);
  const cardMotion = useRef<Animation | null>(null);
  const previousStop = useRef(0);
  const handoffDot = useRef<HTMLElement>(null);
  const handoffMotion = useRef<Animation | null>(null);
  useEffect(() => () => handoffMotion.current?.cancel(), []);
  const category = contractCategory(badDate ? null : contractStops[stop]);
  const sample = messageSamples[message];
  useEffect(() => {
    handMotion.current?.cancel();
    cardMotion.current?.cancel();
    if (motion && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      handMotion.current = hand.current?.animate([
        { transform: `rotate(${previousStop.current * 42 - 105}deg)` },
        { transform: `rotate(${stop * 42 - 105}deg)` },
      ], { duration: 650, easing: 'cubic-bezier(.77,0,.175,1)' }) ?? null;
      cardMotion.current = card.current?.animate([
        { transform: 'translateY(8px)', opacity: .5 }, { transform: 'translateY(0)', opacity: 1 },
      ], { duration: 200, easing: 'cubic-bezier(.23,1,.32,1)' }) ?? null;
    }
    previousStop.current = stop;
    return () => { handMotion.current?.cancel(); cardMotion.current?.cancel(); };
  }, [stop, badDate, motion]);
  function chooseStop(index: number, event: MouseEvent) {
    setMotion(event.detail > 0); setStop(index); setBadDate(false);
  }
  function chooseMessage(index: number, event: MouseEvent) {
    handoffMotion.current?.cancel();
    setMessage(index);
    if (event.detail > 0 && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      handoffMotion.current = handoffDot.current?.animate([
        { transform: 'translateY(0)', opacity: .4 },
        { transform: 'translateY(24px)', opacity: 1 },
      ], { duration: 240, easing: 'cubic-bezier(.23,1,.32,1)' }) ?? null;
    }
  }
  return <section className="case-section time-room" data-module={module} aria-labelledby="time-heading">
    <div className="time-intro"><p className="section-kicker">How it works / Time control</p>
      <h2 id="time-heading">A date to act.<br />A reason to stop.</h2>
      <p>Two separate routines: a contract agenda and a message decision desk. A contract status does not send a message.</p>
      <p className="time-disclosure">Interactive simulation · fictional examples · no messages sent</p>
    </div>
    <div className="time-module-picker" role="group" aria-label="Choose a module">
      <button type="button" aria-pressed={module === 'agenda'} aria-controls="time-agenda" onClick={() => setModule('agenda')}>A / Contract agenda</button>
      <button type="button" aria-pressed={module === 'triage'} aria-controls="time-triage" onClick={() => setModule('triage')}>B / Message triage</button>
    </div>
    <div className="time-desks">
      <section id="time-agenda" className="time-desk time-agenda" aria-labelledby="agenda-heading">
        <header><span className="time-module-number">A</span><div><p className="section-kicker">Contract tracker</p><h3 id="agenda-heading">The renewal agenda.</h3></div></header>
        <p>Back up the master, calculate expiry from the receipt date and term, then write a separate tracked sheet.</p>
        <div className="time-clock" aria-hidden="true"><svg viewBox="0 0 300 170">
          <path d="M34 145 A120 120 0 1 1 266 145" /><path d="M55 139 A98 98 0 1 1 245 139" />
          {contractStops.map((_, i) => <line key={i} x1="150" y1="12" x2="150" y2="22" transform={`rotate(${i * 42 - 105} 150 130)`} />)}
          <line ref={hand} className="time-hand" x1="150" y1="130" x2="150" y2="32" style={{ transform: `rotate(${stop * 42 - 105}deg)` }} />
          <circle cx="150" cy="130" r="5" />
        </svg><span>BUSINESS TIME / ILLUSTRATION</span></div>
        <fieldset className="time-date-picker"><legend>Move this example toward its expiry</legend>
          <div>{contractStops.map((days, i) => <button key={days} type="button" data-days={days} aria-pressed={!badDate && stop === i} onClick={event => chooseStop(i, event)}>{days > 0 ? `${days} days left` : days === 0 ? 'Due today' : 'Past due'}</button>)}</div>
          <button className="time-bad-date" type="button" data-bad-date aria-pressed={badDate} onClick={event => { setMotion(event.detail > 0); setBadDate(v => !v); }}>Try an unclear date</button>
        </fieldset>
        <div className="time-contract-result" ref={card} data-category={category.id} aria-live="polite">
          <span className="time-example">EXAMPLE CONTRACT</span><h4>{category.title}</h4>
          <p>{badDate ? 'The date cannot be read safely.' : contractStops[stop] > 0 ? `${contractStops[stop]} days until expiry.` : contractStops[stop] === 0 ? 'Expiry is today.' : 'Expiry has passed.'} {category.action}</p>
        </div>
        <ol className="time-agenda-list">{contractCategories.map(item => <li key={item.id} data-current={category.id === item.id}><span aria-hidden="true" /><div><b>{item.title}</b><small>{item.boundary}</small></div>{category.id === item.id && <em>Example here</em>}</li>)}</ol>
        <p className="time-footnote">The dates move only when you choose. No live countdown. An unclear row is flagged while other rows continue.</p>
      </section>
      <section id="time-triage" className="time-desk time-triage" aria-labelledby="triage-heading">
        <header><span className="time-module-number">B</span><div><p className="section-kicker">Message triage</p><h3 id="triage-heading">The human boundary.</h3></div></header>
        <p>Choose an example category to see the intended decision. This illustrates policy; it does not classify text.</p>
        <fieldset className="time-message-picker"><legend>Example message category</legend><div>{messageSamples.map((item, i) => <button key={item.id} type="button" data-message={item.id} aria-pressed={message === i} onClick={event => chooseMessage(i, event)}>{item.title}</button>)}</div></fieldset>
        <div className="time-handoff" data-route={sample.route}>
          <span>Example category</span><i aria-hidden="true"><b ref={handoffDot} /></i><div aria-live="polite"><b>{sample.route === 'human' ? 'Stop → a person takes over' : 'Approved text → mock reply'}</b><p>{sample.detail}</p><small>{sample.route === 'human' ? 'No reply draft attached' : 'Local mock log only'}</small></div>
        </div>
        <p className="time-boundary-note">Known gap: mixed-intent messages can bypass this intended boundary in the audited implementation. The optional AI draft filter also has a known bypass.</p>
        <section className="time-reminders" aria-labelledby="reminder-heading">
          <p className="section-kicker">Separate follow-up example</p><h4 id="reminder-heading">Check again. Keep the record.</h4>
          <p>One eligible email example, with its saved ledger kept intact. It is independent of the category chosen above.</p>
          <div className="time-reminder-actions" role="group" aria-label="Simulate follow-up checks">
            <button type="button" data-reminder="boundary" onClick={() => { setHours(24); setReminder(s => checkReminder(s, 24)); }}>Check at 24 hours</button>
            <button type="button" data-reminder="later" onClick={() => { setHours(25); setReminder(s => checkReminder(s, 25)); }}>Check after 24 hours</button>
            <button type="button" data-reminder="replay" onClick={() => setReminder(s => checkReminder(s, hours))}>Replay saved check</button>
            <button type="button" data-reminder="reply" onClick={() => setReminder(s => checkReminder({ ...s, replied: true }, hours))}>Customer replied</button>
          </div>
          <div className="time-ledger" data-result={reminder.result} aria-live="polite"><strong>{reminder.logged ? '1' : '0'}</strong><div><b>mock reminder in this example</b><p>{reminderResults[reminder.result]}</p></div></div>
          <button type="button" className="time-reset" data-reminder="reset" onClick={() => { setHours(24); setReminder(initialReminder); }}>Reset this example ↺</button>
          <p className="time-boundary-note">This shows sequential checks on saved state. Re-import and concurrent delivery are not proven safe; the audit found that an import can erase reminder history.</p>
        </section>
      </section>
    </div>
    <ol className="time-steps"><li><b>A / Protect</b><span>Back up the master.</span></li><li><b>A / Recalculate</b><span>Write a separate status sheet.</span></li><li><b>B / Decide</b><span>Approved text or human handoff.</span></li><li><b>B / Remember</b><span>Check the saved reminder record.</span></li></ol>
  </section>;
}

export function TimeEvidence() {
  return <section className="case-section time-evidence" aria-labelledby="time-evidence-heading">
    <p className="section-kicker">Evidence / Recorded, not live</p><h2 id="time-evidence-heading">The proof has boundaries.</h2>
    <div className="time-proof-columns"><article><span>A / CONTRACTS</span><h3>200 per run.</h3><p>Synthetic contracts, including 45 difficult date rows. The reference-date check matched a manual audit: 7 of 7 renewals on 4 September 2026.</p><small>Dossier §3.1–3.3, §6 K2, §8</small></article>
      <article><span>B / MESSAGES</span><h3>18 test messages.</h3><p>6 of 6 sensitive fixtures were escalated, with no draft attached. Delivery remained a local mock log; external API calls: 0.</p><small>Dossier §6 K5/K8, §8</small></article>
      <article><span>B / SAVED LEDGER</span><h3>12 stayed 12.</h3><p>Six sequential follow-up checks kept the same 12 mock reminders. This does not prove safe re-import or concurrent delivery.</p><small>Dossier §6 K6, §7 finding 1</small></article></div>
    <div className="time-dates-note"><h3>Business dates are not elapsed days.</h3><p>The video’s seven-day segment uses simulated business dates. Separate scheduler evidence records 8 unattended firings across 9 real days, 5–13 September 2026. One missed business date was not backfilled.</p></div>
    <div className="time-audit"><p className="section-kicker">Self-review / 6 September 2026</p><h3>Seven defects, kept in view.</h3><p>The dossier reports four High and three Medium findings. Acceptance A9/A10 remains open. These are documented limits, not claims of a production-ready system.</p>
      <ol>{auditFindings.map(([severity, title, detail]) => <li key={title}><details><summary><span>{severity}</span>{title}<b aria-hidden="true">+</b></summary><p>{detail}</p></details></li>)}</ol>
      <p className="time-footnote">Source: CAPABILITY_DUEWATCH §7, §8 and §11. This page summarizes the dossier snapshot; it is not a fresh audit of the underlying project.</p>
    </div>
  </section>;
}
