'use client';

import { useLayoutEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { monitoringScenarios, monitoringSteps, sampleBaseline, sampleChanged, sourceLedger } from '@/lib/driftwatch-room';
import { useReducedMotion } from './use-reduced-motion';

export function MonitoringRoom() {
  const [choice, setChoice] = useState(0);
  const [compared, setCompared] = useState(false);
  const [replay, setReplay] = useState(0);
  const pointer = useRef(false);
  const root = useRef<HTMLElement>(null);
  const reduced = useReducedMotion();
  const scenario = monitoringScenarios[choice];
  const hasRows = scenario.id === 'change' || scenario.id === 'recovery';

  useLayoutEffect(() => {
    if (!compared || reduced || !pointer.current) return;
    const context = gsap.context(() => {
      // The clip window opens left → right; the path itself never scales, so the spike draws in place.
      gsap.fromTo('.monitor-trace-window', { scaleX: 0 }, { scaleX: 1, svgOrigin: '0 35', duration: .8, ease: 'none' });
      gsap.fromTo('.monitor-result', { opacity: 0, y: 5 }, { opacity: 1, y: 0, duration: .2, delay: .6, ease: 'power2.out' });
    }, root);
    return () => context.revert();
  }, [choice, compared, replay, reduced]);

  return <section ref={root} className="case-section monitoring-room" aria-labelledby="flow-heading" data-scenario={scenario.id} data-compared={compared} data-verdict={compared ? scenario.alarm ? 'alarm' : 'healthy' : 'pending'}>
    <div className="monitor-intro"><p className="section-kicker">How it works / The comparison desk</p>
      <h2 id="flow-heading">What changed?<br />Can you trust it?</h2>
      <p>I keep the last good snapshot in view. Choose what happens next, then compare the evidence before calling the data healthy.</p>
      <p className="monitor-disclosure">Interactive illustration · fictional pages and example days below. Not a live monitor or a replay of the daily runs.</p>
    </div>
    <ol className="monitor-steps">{monitoringSteps.map(step => <li key={step.title}><h3>{step.title}</h3><p>{step.body}</p></li>)}</ol>
    <fieldset className="monitor-scenarios"><legend>Choose a situation</legend><div>{monitoringScenarios.map((item, i) =>
      <button key={item.id} type="button" data-scenario-choice={item.id} aria-pressed={choice === i} onClick={() => { setChoice(i); setCompared(false); }}>{item.label}</button>)}</div></fieldset>
    <div className="monitor-workspace">
      <div className="monitor-timeline" aria-label="Illustrated comparison days">
        <span><em>Day 1</em><b>Last good snapshot</b></span>
        {scenario.id === 'recovery' && <span className="monitor-failed-day"><em>Day 2</em><b>Failed · skipped</b></span>}
        <span><em>Day {scenario.day}</em><b>{scenario.id === 'missing' ? 'Run missing' : 'Current collection'}</b></span>
      </div>
      <div className="monitor-snapshots">
        <article className="monitor-snapshot" data-snapshot="baseline"><header><span>BASELINE / KEPT</span><em>Day 1</em></header>
          <h3>Last successful run</h3><ul>{sampleBaseline.map(row => <li key={row.id}><code>{row.id}</code><span>{row.title}</span></li>)}</ul>
        </article>
        <article className="monitor-snapshot" data-snapshot="current"><header><span>{hasRows ? 'CURRENT / COLLECTED' : scenario.id === 'missing' ? 'CURRENT / ABSENT' : 'CURRENT / EMPTY'}</span><em>Day {scenario.day}</em></header>
          <h3>{hasRows ? 'A new snapshot' : scenario.id === 'missing' ? 'No snapshot exists' : 'No records collected'}</h3>
          {hasRows ? <ul>{(scenario.id === 'recovery' ? sampleBaseline : sampleChanged).map(row => <li key={row.id}><code>{row.id}</code><span>{row.title}</span></li>)}</ul>
            : <div className="monitor-empty"><span aria-hidden="true">{scenario.id === 'missing' ? '—' : '∅'}</span><p>{scenario.id === 'missing' ? 'No run manifest. The watchdog must speak.' : 'An empty result is not proof of an empty source.'}</p></div>}
        </article>
      </div>
      <div className="monitor-comparison">
        <div className="monitor-compare-control"><button className="case-button" type="button" data-compare onClick={event => { pointer.current = event.detail > 0; setCompared(true); setReplay(n => n + 1); }}>{compared ? 'Compare again' : 'Compare snapshots'} <span aria-hidden="true">↗</span></button>
          <p>Illustrated signal · green = healthy, red = alarm</p></div>
        <div className="monitor-trace" aria-hidden="true"><svg viewBox="0 0 600 70" preserveAspectRatio="none"><defs><clipPath id="monitor-trace-clip"><rect className="monitor-trace-window" width="600" height="70" /></clipPath></defs><path className="monitor-trace-base" d="M0 38H600" /><g className="monitor-trace-reveal" clipPath="url(#monitor-trace-clip)"><path d={compared && scenario.alarm ? 'M0 38H260L276 34L288 42L306 8L318 62L334 32L350 38H600' : 'M0 38H160L176 35L192 40L208 38H600'} /></g></svg><span>{compared ? scenario.alarm ? 'ALARM' : 'HEALTHY' : 'AWAITING COMPARISON'}</span></div>
        <div className="monitor-result" aria-live="polite" aria-atomic="true">
          {compared ? <>
            <div className="monitor-verdict"><p className="section-kicker">{scenario.kind === 'pipeline' ? 'Pipeline health' : scenario.kind === 'source' ? 'Source comparison' : 'Recovery record'}</p><h3>{scenario.heading}</h3><p>{scenario.summary}</p></div>
            <div className="monitor-diff" data-diff={scenario.id}><h4>{scenario.alarm ? 'Reason & next action' : 'Field-level difference'}</h4>
              {scenario.id === 'change' ? <ul>
                <li data-change="changed"><b>Changed · /guide</b><span>title</span><del>Getting started</del><ins>Getting started with the API</ins></li>
                <li data-change="added"><b>Added · /start</b><span>Quick start</span></li>
                <li data-change="removed"><b>Removed · /notes</b><span>Release notes</span></li>
                <li data-change="unchanged"><b>Unchanged · /help</b><span>Help centre</span></li>
              </ul> : <><p className="monitor-cause">{scenario.cause}</p><p>{scenario.action}</p>
                {scenario.id === 'recovery' && <p className="monitor-resolved">Day 2: empty run → Day 3: resolved. Baseline remains Day 1 for this comparison. No field changes.</p>}
                {scenario.codes.length > 0 && <details className="monitor-codes"><summary>Alarm record</summary><ul>{scenario.codes.map(code => <li key={code}><code>{code}</code></li>)}</ul></details>}</>}
              {scenario.id === 'change' && <p>{scenario.action} Fetch timestamps are excluded from the comparison.</p>}
            </div>
          </> : <div className="monitor-pending"><h3>Read both days. Then compare.</h3><p>The baseline stays intact whichever situation you choose.</p></div>}
        </div>
      </div>
    </div>
  </section>;
}

export function MonitoringEvidence() {
  return <section className="case-section monitoring-evidence" aria-labelledby="monitor-evidence-heading">
    <div><p className="section-kicker">Recorded evidence / Separate from the illustration</p><h2 id="monitor-evidence-heading">A small archive.<br />A tested alarm.</h2>
      <p>Project records, checked on 13 Sep 2026. These figures describe the documented run window, not collection happening today.</p></div>
    <div className="monitor-source-ledger"><p className="monitor-total"><strong>1,323</strong> records per day / four sources</p>
      <ul>{sourceLedger.map(source => <li key={source.name}><strong>{source.count}</strong><div><h3>{source.name}</h3><p>{source.role}</p></div></li>)}</ul></div>
    <div className="monitor-soak"><h3>Three unattended days</h3><ol>{['01', '02', '03'].map((day, i) => <li key={day}><time dateTime={`2026-09-${day}`}>{day} Sep 2026</time><b>Four runs finished</b><span>{i === 0 ? 'Manifests + next-day watchdog' : 'Timer journal + manifests'}</span></li>)}</ol>
      <p>12/12 runs exited cleanly. The 01 Sep timer trigger is supported indirectly; its journal entry had rotated away. The next two days have direct journal evidence.</p></div>
    <div className="monitor-proof-note"><h3>11/11 test scenarios handled correctly.</h3><p>Zero false positives in that test. Three scenarios were ordinary additions, edits and removals that correctly stayed quiet; the others tested failures. This is controlled evidence, not a promise to detect every future break.</p>
      <p>The public sources stayed unchanged during the eight recorded dates. Change detection was tested on the owned lab. A real runner setup failure was also caught; the failed days remain in the history.</p></div>
  </section>;
}
