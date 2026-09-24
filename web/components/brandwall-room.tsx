'use client';

import { useId, useState, useSyncExternalStore } from 'react';
import { boundaries, specimens, studioRules } from '@/lib/brandwall-room';

const WIDE = '(min-width: 1024px)';
function useWide() {
  return useSyncExternalStore(callback => {
    const media = window.matchMedia(WIDE);
    media.addEventListener('change', callback);
    return () => media.removeEventListener('change', callback);
  }, () => window.matchMedia(WIDE).matches, () => false);
}

type Specimen = typeof specimens[number];
// Both captures of a pair always share one view; a phone may use a taller crop that fills its frame.
function Capture({ specimen, after = false, view = specimen.view }: { specimen: Specimen; after?: boolean; view?: string }) {
  const clip = useId();
  const [x, y, width, height] = view.split(' ').map(Number);
  return <svg viewBox={view} role="img" aria-label={`${specimen.asset}: ${after ? specimen.after : specimen.before}`}>
    <defs><clipPath id={clip}><rect x={x} y={y} width={width} height={height} /></clipPath></defs>
    <g clipPath={`url(#${clip})`}><image transform={after && specimen.id === 'contrast' ? 'translate(0 -29)' : undefined} href={`/images/brandwall/${specimen.capture}__${after ? 'after' : 'before'}.png`} width={after ? specimen.afterWidth : specimen.width} height={specimen.height} /></g>
  </svg>;
}

export function VisualStudio() {
  const [selected, setSelected] = useState(0);
  const [mode, setMode] = useState<'before' | 'split' | 'after'>('before');
  const specimen = specimens[selected];
  const view = useWide() || !('phoneView' in specimen) ? specimen.view : specimen.phoneView;
  const reveal = mode === 'before' ? 100 : mode === 'after' ? 0 : 50;
  return <section className="case-section brand-studio" aria-labelledby="flow-heading" data-specimen={specimen.id} data-view={mode}>
    <header className="brand-intro"><p className="section-kicker">How it works / Visual studio</p>
      <h2 id="flow-heading">Same asset.<br />A different outcome.</h2>
      <p>I put extreme assets into ordinary layouts, measure the break, then check the same view after the rules change.</p>
      <ol className="brand-steps"><li>Specimen</li><li>Surface + theme</li><li>Measure</li><li>Compare</li></ol>
    </header>
    <div className="brand-desk">
      <div className="brand-contact-sheet" role="group" aria-label="Recorded specimens">
        {specimens.map((item, i) => <button key={item.id} data-specimen-choice={item.id} aria-pressed={selected === i} onClick={() => setSelected(i)}>
          <span className="brand-thumb" aria-hidden="true"><Capture specimen={item} /></span>
          <span><small>0{i + 1} / {item.short}</small><b>{item.asset}</b></span>
        </button>)}
      </div>
      <div className="brand-comparison">
        <div className="brand-caption"><span>{specimen.surface} · Light</span><span>{specimen.code}</span></div>
        <h3>{specimen.title}</h3>
        <div className="brand-view-controls" role="group" aria-label="Compare recorded captures">
          {(['before', 'split', 'after'] as const).map(view => <button key={view} data-brand-view={view} aria-pressed={mode === view} onClick={() => setMode(view)}>{view === 'split' ? 'Compare' : view === 'before' ? 'Before rules' : 'After rules'}</button>)}
        </div>
        <div className="brand-pair" data-pair={specimen.id}>
          <div className="brand-image"><Capture specimen={specimen} view={view} /></div>
          <div className="brand-image brand-after" style={{ clipPath: `inset(0 ${reveal}% 0 0)` }} aria-hidden={mode === 'before'}><Capture specimen={specimen} view={view} after /></div>
          <div className="brand-seam" style={{ left: `${100 - reveal}%`, opacity: mode === 'split' ? 1 : 0 }} aria-hidden="true"><span>AFTER / BEFORE</span></div>
        </div>
        <p className="brand-verdict" aria-live="polite">{mode === 'split' ? 'Aligned view: after on the left, before on the right. Tap either full view to inspect it.' : mode === 'after' ? specimen.after : specimen.before}</p>
        <div className="brand-annotation"><span>MEASURE</span><p>{specimen.measure}</p><span>RULE</span><p>{specimen.rule}</p></div>
        <details className="brand-source"><summary>See the full captures + source</summary>
          <p>Recorded English gallery · synthetic assets · owned desktop target. Same crop size in both views. The article footer is aligned vertically to account for its changed page position. These are archived screenshots, not a live test.</p>
          <p className="brand-capture-id">{specimen.capture}</p>
          <a href={`/images/brandwall/${specimen.capture}__before.png`} target="_blank" rel="noreferrer">Full before ↗</a>
          <a href={`/images/brandwall/${specimen.capture}__after.png`} target="_blank" rel="noreferrer">Full after ↗</a>
        </details>
      </div>
    </div>
  </section>;
}

export function StudioEvidence() {
  const [boundary, setBoundary] = useState(0);
  const [broken, setBroken] = useState(false);
  const [dark, setDark] = useState(false);
  const point = boundaries[boundary];
  return <section className="case-section brand-evidence" aria-labelledby="brand-boundary-heading">
    <header><p className="section-kicker">Measured boundaries / Recorded sweep</p><h2 id="brand-boundary-heading">Where does it break?</h2>
      <p>11 boundaries, reported as tested ranges. Pick a measurement, then compare the last safe probe with the first failing one.</p></header>
    <div className="brand-boundary-desk">
      <div className="brand-boundary-controls">
        <div className="brand-axis" role="group" aria-label="Boundary measurement">{boundaries.map((item, i) => <button key={item.id} data-boundary={item.id} aria-pressed={i === boundary} onClick={() => { setBoundary(i); setBroken(false); }}>{item.label}</button>)}</div>
        <p>{point.context}</p>
        <div className="brand-probes" role="group" aria-label="Recorded probe"><button data-probe="safe" aria-pressed={!broken} onClick={() => setBroken(false)}>Last safe <b>{point.safe}</b></button><button data-probe="broken" aria-pressed={broken} onClick={() => setBroken(true)}>First failure <b>{point.broken}</b></button></div>
        <p className="brand-step">{point.unit} · sweep step {point.step}</p>
        <p className="brand-boundary-note">{point.note}</p>
      </div>
      <div className="brand-probe-view" data-axis={point.id} data-broken={broken} data-dark={dark}>
        <div className="brand-probe-head"><span>ILLUSTRATION / NOT A CAPTURE</span><button data-brand-theme onClick={() => setDark(!dark)} aria-pressed={dark}>Dark specimen {dark ? 'on' : 'off'}</button></div>
        <div className="brand-specimen-field" aria-hidden="true"><div className="brand-slot"><div className="brand-test-logo"><i /><i /><i /></div></div><div className="brand-test-name">A publication with a long name</div><i className="brand-measure-line" /></div>
        <p className="brand-probe-result" aria-live="polite">{broken ? 'First failing probe' : 'Last safe probe'} · {broken ? point.broken : point.safe} {point.unit}</p>
        <p>Theme switch changes this illustration only. It does not recalculate the recorded boundary.</p>
      </div>
    </div>
    <div className="brand-rules"><div><p className="section-kicker">Seven classes / Seven CSS rules</p><h3>Fix a class.<br />Keep the limits visible.</h3><p>Aspect distortion is checked too: deviation above 1% is flagged. The recorded matrix had <strong>0 BW-C4 findings</strong>; no invented before/after fix is shown.</p></div>
      <div>{studioRules.map(([code, label, body]) => <details key={code}><summary><span>{code}</span>{label}<b aria-hidden="true">+</b></summary><p>{body}</p></details>)}</div>
    </div>
    <div className="brand-record"><article><span>PRODUCTION RECORD</span><strong>186 → 18</strong><p>Seven CSS rules. Five classes closed. No new findings. The English gallery and video record 182 → 18; different name widths change text overflow.</p></article>
      <article><span>ASSET ACCEPTANCE</span><h3>Reject, don’t disguise.</h3><p>The remaining 18 findings are missing or empty assets: a real 404 and a hairline mark with no solid ink. A fallback is not an asset repair.</p></article>
      <article><span>OPEN LIMIT / A8</span><h3>A human still needs to read it.</h3><p>The gallery opens offline. Whether a non-technical person understands it without an explanation remains untested. A8 is partial.</p></article></div>
  </section>;
}
