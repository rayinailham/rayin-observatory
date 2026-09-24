'use client';

import { Fragment, useEffect, useMemo, useRef, useState, useSyncExternalStore, type CSSProperties } from 'react';
import Image from 'next/image';
import { gsap } from 'gsap';
import { crosscheckRun as run } from '@/lib/crosscheck-run';
import { findings, findingsIntro, inspectionNote, inspectionSteps, scanLanes, type Finding } from '@/lib/crosscheck-room';
import { useReducedMotion } from './use-reduced-motion';

const WIDE = '(min-width: 1024px)';
function useWide() {
  return useSyncExternalStore(callback => {
    const media = window.matchMedia(WIDE);
    media.addEventListener('change', callback);
    return () => media.removeEventListener('change', callback);
  }, () => window.matchMedia(WIDE).matches, () => false);
}

const clamp = (n: number) => Math.max(0, Math.min(1, n));
const ease = (n: number) => { const t = clamp(n); return t * t * (3 - 2 * t); };
const span = (p: number, from: number, to: number) => ease((p - from) / (to - from));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Story beats on the scan's progress (0–1). Each beat is a pure function of progress, so replaying
// or jumping back to a step runs the scan in reverse and a click can never queue animations.
const BEATS = { map: [0, .12], scan: [.12, .5], sort: [.52, .76], hand: [.78, .96] } as const;
// Where each step's beat finishes: a step button plays (or rewinds) the scan to there.
const stepEnd = [BEATS.map[1], BEATS.scan[1], BEATS.sort[1], 1];
const stepAt = (p: number) => p < BEATS.scan[0] + .02 ? 0 : p < BEATS.sort[0] ? 1 : p < BEATS.hand[0] ? 2 : 3;

type Layout = ReturnType<typeof layoutFor>;
function layoutFor(wide: boolean) {
  const labels = wide ? 156 : 0;
  const matrixW = wide ? 594 : 360;
  const gap = wide ? 14 : 10;
  const colPitch = (matrixW - gap * 2) / 27;
  const rowPitch = wide ? 11 : 9;
  const top = wide ? 30 : 24;
  const matrixH = rowPitch * 40;
  const accessTop = top + matrixH + (wide ? 44 : 38);
  const accessRow = wide ? 6 : 5;
  const flowsTop = accessTop + accessRow * 3 + (wide ? 34 : 30);
  const colX = (c: number) => labels + c * colPitch + Math.floor(c / 9) * gap;
  const chipCols = wide ? 6 : 3;
  const chipW = wide ? 88 : 110;
  const chipH = wide ? 22 : 20;
  const chipGapX = (matrixW - chipCols * chipW) / (chipCols - 1);
  const chipsTop = top + matrixH / 2 - ((Math.ceil(18 / chipCols) * (chipH + 8)) - 8) / 2;
  return {
    wide, labels, matrixW, gap, colPitch, rowPitch, top, matrixH, accessTop, accessRow, flowsTop, colX,
    width: labels + matrixW, height: flowsTop + (wide ? 24 : 22),
    chip: (i: number) => ({ x: labels + (i % chipCols) * (chipW + chipGapX), y: chipsTop + Math.floor(i / chipCols) * (chipH + 8) }),
    chipW, chipH,
  };
}

const issueRows = new Set<number>(run.issues.flatMap(issue => issue.row === null ? [] : [issue.row]));
const priorityClass = (priority: string) => priority.toLowerCase();

function cellsPath(layout: Layout, rows: readonly number[], flagged: boolean, stacked = false) {
  const w = layout.colPitch - (layout.wide ? 2 : 1.6);
  const h = layout.rowPitch - (layout.wide ? 3 : 2.6);
  let d = '';
  rows.forEach(r => {
    const line = run.matrix[r];
    for (let c = 0; c < 27; c++) {
      if ((line[c] === '1') !== flagged) continue;
      // A single row is drawn at y = 0 inside its own group, so a kept row can merge in place.
      d += `M${(layout.colX(c) - layout.labels).toFixed(2)} ${stacked ? (r * layout.rowPitch).toFixed(2) : 0}h${w.toFixed(2)}v${h.toFixed(2)}h${(-w).toFixed(2)}z`;
    }
  });
  return d;
}

export function InspectionField() {
  const wide = useWide();
  const reducedMotion = useReducedMotion();
  const layout = useMemo(() => layoutFor(wide), [wide]);
  const section = useRef<HTMLElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  const [step, setStep] = useState(reducedMotion ? 3 : 0);
  // The scan plays by itself once it comes into view; the visitor can replay it or jump to a step.
  const playTo = useRef<(to: number, from?: number) => void>(() => {});
  const allRows = useMemo(() => run.matrix.map((_, i) => i), []);
  const passPath = useMemo(() => cellsPath(layout, allRows, false, true), [layout, allRows]);
  const removedRows = useMemo(() => allRows.filter(r => !issueRows.has(r)), [allRows]);
  const keptRows = useMemo(() => allRows.filter(r => issueRows.has(r)), [allRows]);
  const removedPath = useMemo(() => removedRows.map(r => ({ r, d: cellsPath(layout, [r], true) })).filter(row => row.d), [layout, removedRows]);

  useEffect(() => {
    const root = svg.current;
    const stage = section.current;
    if (!root || !stage) return;
    const q = <T extends Element>(selector: string) => Array.from(root.querySelectorAll<T>(selector));
    const reveal = root.querySelector<SVGRectElement>('[data-part=reveal]')!;
    const scanBar = root.querySelector<SVGGElement>('[data-part=scan-bar]')!;
    const outline = root.querySelector<SVGGElement>('[data-part=outline]')!;
    const pass = root.querySelector<SVGPathElement>('[data-part=pass]')!;
    const removed = root.querySelector<SVGGElement>('[data-part=removed]')!;
    const kept = q<SVGGElement>('[data-kept]');
    const accessReveal = root.querySelector<SVGRectElement>('[data-part=access-reveal]')!;
    const access = root.querySelector<SVGGElement>('[data-part=access]')!;
    const flows = q<SVGRectElement>('[data-flow]');
    const chips = q<SVGGElement>('[data-chip]');
    const matrixLabels = root.querySelector<SVGGElement>('[data-part=labels]');
    const removedGrey = root.querySelector<SVGGElement>('[data-part=removed-grey]')!;
    // Only touch the DOM when a rounded value changes: during a scrub most parts are at rest.
    // Fades use inherited fill-/stroke-opacity, not `opacity`: opacity on an SVG group paints it into its
    // own transparency layer every frame (Phase 7A Testing: hand-over beat 47 → see CODEMAP).
    const written = new Map<Element, Record<string, string>>();
    const put = (element: SVGElement, name: string, value: string | number, attribute = false) => {
      const text = typeof value === 'number' ? value.toFixed(3) : value;
      const record = written.get(element) ?? {};
      if (record[name] === text) return;
      record[name] = text;
      written.set(element, record);
      if (attribute) element.setAttribute(name, text);
      else element.style.setProperty(name, text);
    };
    let shown = -1;

    const draw = (p: number) => {
      const map = span(p, ...BEATS.map);
      const scan = span(p, ...BEATS.scan);
      const sort = span(p, ...BEATS.sort);
      const hand = span(p, ...BEATS.hand);
      put(outline, 'stroke-opacity', map * (1 - hand) * .9);
      if (matrixLabels) put(matrixLabels, 'fill-opacity', map * (1 - hand * .85));
      // Three lanes scan together: the same front crosses Chromium, Firefox and WebKit.
      put(reveal, 'height', (scan * layout.matrixH + (scan > 0 ? layout.rowPitch : 0)).toFixed(1), true);
      put(scanBar, 'transform', `translate(0 ${(scan * layout.matrixH).toFixed(1)})`, true);
      put(scanBar, 'opacity', scan > 0 && scan < 1 ? 1 : 0);
      put(accessReveal, 'width', (span(scan, .55, 1) * layout.matrixW).toFixed(1), true);
      put(access, 'fill-opacity', map);
      flows.forEach((pip, i) => put(pip, 'fill-opacity', span(scan, .7 + i * .06, .76 + i * .06)));
      // Sorting: clean visits dim, rows whose signals were all expected behaviour cross-fade to grey,
      // repeated signals on a real problem collapse into one merged mark.
      put(pass, 'fill-opacity', lerp(.62, .1, sort) * (1 - hand * .6));
      put(removed, 'fill-opacity', (1 - sort) * (1 - hand * .7));
      put(removedGrey, 'fill-opacity', sort * .32 * (1 - hand * .7));
      kept.forEach(row => {
        put(row, 'transform', `translate(${layout.labels} ${row.dataset.y}) scale(${lerp(1, 1 / 27 * 1.6, sort).toFixed(3)} 1)`, true);
        put(row, 'fill-opacity', 1 - hand * .8);
      });
      chips.forEach((chip, i) => {
        const t = span(hand, i * .025, .55 + i * .025);
        const x = lerp(Number(chip.dataset.fromX), Number(chip.dataset.toX), t);
        const y = lerp(Number(chip.dataset.fromY), Number(chip.dataset.toY), t);
        put(chip, 'transform', `translate(${x.toFixed(1)} ${y.toFixed(1)})`, true);
        const shown = span(hand, i * .025, .2 + i * .025);
        put(chip, 'fill-opacity', shown);
        put(chip, 'stroke-opacity', shown);
      });
      const next = stepAt(p);
      if (next !== shown) { shown = next; setStep(next); stage.dataset.step = String(next); }
      root.dataset.progress = p.toFixed(3);
    };

    if (reducedMotion) { draw(1); playTo.current = () => {}; return; }
    const tween = { p: 0 };
    playTo.current = (to, from = tween.p) => {
      gsap.killTweensOf(tween);
      gsap.fromTo(tween, { p: from }, { p: to, duration: Math.max(.6, Math.abs(to - from) * 7), ease: 'power1.inOut', onUpdate: () => draw(tween.p) });
    };
    draw(0);
    const seen = new IntersectionObserver(entries => {
      if (!entries.some(entry => entry.isIntersecting)) return;
      seen.disconnect();
      playTo.current(1);
    }, { threshold: .45 });
    seen.observe(stage);
    return () => { seen.disconnect(); gsap.killTweensOf(tween); };
  }, [layout, reducedMotion]);

  const { width, height } = layout;
  const laneWidth = layout.colPitch * 9;
  const flowPitch = layout.wide ? 30 : 26;
  const accessPitch = layout.matrixW / run.accessPages;
  const chipOrigin = (issue: typeof run.issues[number]) => issue.source === 'sweep'
    ? { x: layout.labels, y: layout.top + (issue.row ?? 0) * layout.rowPitch }
    : issue.source === 'access' ? { x: layout.labels + layout.matrixW * .3, y: layout.accessTop }
      : { x: layout.labels + 2 * flowPitch, y: layout.flowsTop };

  return <section ref={section} className="inspection-field" aria-labelledby="flow-heading" data-step={reducedMotion ? 3 : 0}>
    <div className="inspection-stage">
      <div className="inspection-copy">
        <p className="section-kicker">How it works</p>
        <h2 id="flow-heading">From page visits<br />to a clear report.</h2>
        <ol className="inspection-steps">{inspectionSteps.map((item, i) => <li key={item.title} data-active={i === step} data-done={i < step}>
          <span className="inspection-step-index" aria-hidden="true">{String(i + 1).padStart(2, '0')}</span>
          <h3><button className="inspection-step-button" aria-pressed={i === step} onClick={() => playTo.current(stepEnd[i])}>{item.title}</button></h3><p>{item.body}</p><p className="inspection-readout">{item.readout}</p>
        </li>)}</ol>
        <button className="inspection-replay" onClick={() => playTo.current(1, 0)}>Replay the scan <span aria-hidden="true">↻</span></button>
        <div className="inspection-detail" aria-hidden="true"><p>{inspectionSteps[step].body}</p><p className="inspection-readout">{inspectionSteps[step].readout}</p></div>
      </div>
      <figure className="inspection-figure">
        <svg ref={svg} className="inspection-matrix" viewBox={`0 0 ${width} ${height}`} role="img"
          aria-label="Coverage matrix of the recorded demo run: 40 pages across three browsers, three screen sizes and three roles. 422 of 1,080 visits were flagged, 881 raw signals were sorted, and 18 unique issues remained: 3 High, 14 Medium, 1 Low.">
          <defs><clipPath id="inspection-reveal"><rect data-part="reveal" x="0" y={layout.top - 2} width={width} height="0" /></clipPath>
            <clipPath id="inspection-access-reveal"><rect data-part="access-reveal" x={layout.labels} y={layout.accessTop - 2} width="0" height={layout.accessRow * 3 + 4} /></clipPath></defs>
          {scanLanes.map((lane, i) => <text key={lane} className="lane-label" x={layout.colX(i * 9) + laneWidth / 2} y={layout.top - 9} textAnchor="middle">{lane}</text>)}
          {layout.wide && <g data-part="labels" className="route-labels">{run.routes.map((route, r) => <text key={route} x={layout.labels - 12} y={layout.top + r * layout.rowPitch + layout.rowPitch * .62} textAnchor="end">{route}</text>)}</g>}
          <g data-part="outline" className="matrix-outline">{[0, 1, 2].map(lane => <rect key={lane} x={layout.colX(lane * 9) - 3} y={layout.top - 3} width={laneWidth + 4} height={layout.matrixH + 4} />)}</g>
          <g clipPath="url(#inspection-reveal)">
            <path data-part="pass" className="cells-pass" d={passPath} transform={`translate(${layout.labels} ${layout.top})`} />
            {(['removed', 'removed-grey'] as const).map(part => <g key={part} data-part={part} className={`cells-${part}`}>{removedPath.map(row => <path key={row.r} d={row.d} transform={`translate(${layout.labels} ${layout.top + row.r * layout.rowPitch})`} />)}</g>)}
            {keptRows.map(r => <g key={r} data-kept={r} data-y={layout.top + r * layout.rowPitch} className="cells-kept" transform={`translate(${layout.labels} ${layout.top + r * layout.rowPitch})`}><path d={cellsPath(layout, [r], true)} /></g>)}
          </g>
          <g data-part="scan-bar" className="scan-bar">{[0, 1, 2].map(lane => <rect key={lane} x={layout.colX(lane * 9) - 3} y={layout.top - 1.5} width={laneWidth + 4} height="1.5" />)}</g>

          <text className="strip-label" x={layout.labels} y={layout.accessTop - 8}>Access · 72 pages × 3 roles</text>
          <g data-part="access" clipPath="url(#inspection-access-reveal)" className="access-cells">
            {Array.from({ length: 3 }, (_, role) => <rect key={role} className="access-ok" x={layout.labels} y={layout.accessTop + role * layout.accessRow} width={layout.matrixW} height={layout.accessRow - 1.4} />)}
            {run.violations.map(([page, role]) => <rect key={`${page}-${role}`} className="access-leak" x={layout.labels + page * accessPitch} y={layout.accessTop + role * layout.accessRow} width={Math.max(3, accessPitch)} height={layout.accessRow - 1.4} />)}
          </g>
          <text className="strip-label" x={layout.labels} y={layout.flowsTop - 8}>Flows · 5 tasks as Editor</text>
          {run.flows.map((flow, i) => <rect key={flow.name} data-flow={i} className={flow.passed ? 'flow-pass' : 'flow-fail'} x={layout.labels + i * flowPitch} y={layout.flowsTop} width={flowPitch - 8} height={layout.wide ? 12 : 10} />)}

          {run.issues.map((issue, i) => {
            const from = chipOrigin(issue);
            const to = layout.chip(i);
            return <g key={issue.id} data-chip={issue.id} className={`issue-chip ${priorityClass(issue.priority)}`} data-from-x={from.x} data-from-y={from.y} data-to-x={to.x} data-to-y={to.y} transform={`translate(${to.x} ${to.y})`}>
              <rect width={layout.chipW} height={layout.chipH} /><rect className="issue-chip-mark" width="3" height={layout.chipH} />
              <text x="10" y={layout.chipH * .66}>{issue.id}</text><text className="issue-chip-priority" x={layout.chipW - 7} y={layout.chipH * .66} textAnchor="end">{issue.priority}</text>
            </g>;
          })}
        </svg>
        <figcaption>
          <span className="inspection-legend"><i className="legend-pass" />Clean<i className="legend-flagged" />Flagged<i className="legend-removed" />Removed by rule</span>
          <span>{inspectionNote}</span>
        </figcaption>
      </figure>
    </div>
  </section>;
}

function EvidenceStrip({ finding }: { finding: Finding }) {
  if (finding.layer === 'matrix') {
    const highlighted = new Set<number>((run.evidenceCells as Record<string, readonly number[]>)[finding.id] ?? []);
    return <div className="evidence-strip" aria-label={`Found by the browser matrix: ${highlighted.size} of 27 browser, screen and role settings`}>
      <p className="evidence-strip-label"><span>Browser matrix</span><span>{highlighted.size} of 27 visits</span></p>
      <div className="evidence-lanes">{scanLanes.map((lane, l) => <div key={lane} className="evidence-lane"><span>{lane}</span><div>{Array.from({ length: 9 }, (_, c) => {
        const index = l * 9 + c;
        return <i key={c} data-hit={highlighted.has(index)} style={{ '--i': index } as CSSProperties} />;
      })}</div></div>)}</div>
      <p className="evidence-strip-axes" aria-hidden="true">Desktop · Tablet · Mobile, each as Admin · Editor · Viewer</p>
    </div>;
  }
  if (finding.layer === 'access') {
    return <div className="evidence-strip" aria-label="Found by the access checks: 216 page and role checks, 3 confirmed violations, 2 of them on this page">
      <p className="evidence-strip-label"><span>Access checks</span><span>3 of 216 confirmed</span></p>
      <div className="evidence-access">{['Admin', 'Editor', 'Viewer'].map((role, r) => <div key={role}><span>{role}</span><div>{Array.from({ length: run.accessPages }, (_, page) => {
        const leak = run.violations.find(([p, rr]) => p === page && rr === r);
        const mine = leak && page === run.violations[0][0];
        return <i key={page} data-leak={Boolean(leak)} data-hit={Boolean(mine)} style={{ '--i': page } as CSSProperties} />;
      })}</div></div>)}</div>
    </div>;
  }
  return <div className="evidence-strip" aria-label="Found by the end-to-end flows: 5 tasks, 4 passed, 1 lost data after reload">
    <p className="evidence-strip-label"><span>End-to-end flows</span><span>1 of 5 lost data</span></p>
    <ol className="evidence-flows">{run.flows.map((flow, i) => <li key={flow.name} data-hit={!flow.passed} style={{ '--i': i * 4 } as CSSProperties}><i />{flow.name}</li>)}</ol>
  </div>;
}

export function FindingSheet() {
  const [selected, setSelected] = useState(0);
  const [view, setView] = useState<'before' | 'expected'>('before');
  const panel = useRef<HTMLDivElement>(null);
  const motion = useRef<Animation | null>(null);
  const finding = findings[selected];
  useEffect(() => () => motion.current?.cancel(), []);

  function choose(index: number) {
    if (index === selected) return;
    setSelected(index);
    setView('before');
    motion.current?.cancel();
    motion.current = panel.current?.animate([
      { opacity: .35, transform: 'translateY(6px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ], { duration: 220, easing: 'cubic-bezier(.23, 1, .32, 1)' }) ?? null;
  }

  const images = finding.images;
  const shown = view === 'expected' && images.expected ? images.expected : images.before;
  return <section className="case-section finding-sheet" aria-labelledby="findings-heading">
    <p className="section-kicker">Findings</p>
    <h2 id="findings-heading">Four of the 18,<br />with their proof.</h2>
    <p>{findingsIntro}</p>
    <div className="finding-desk">
      <div className="finding-list" role="group" aria-label="Choose a finding">
        {findings.map((item, i) => <button key={item.id} className="finding-tab" data-finding={item.id} aria-pressed={i === selected} aria-controls="finding-evidence" onClick={() => choose(i)}>
          <span className="finding-tab-top"><span>{item.id}</span><b className={`priority ${priorityClass(item.priority)}`}>{item.priority}</b></span>
          <span className="finding-tab-kind">{item.kind}</span>
          <span className="finding-tab-title">{item.title}</span>
        </button>)}
      </div>
      <div ref={panel} id="finding-evidence" className="finding-evidence" aria-live="polite" data-finding={finding.id}>
        <div className="finding-head">
          <p className="finding-meta"><span>{finding.id}</span><b className={`priority ${priorityClass(finding.priority)}`}>{finding.priority}</b><span>{finding.kind}</span><span>Lens · {finding.lens}</span></p>
          <h3>{finding.title}</h3>
          <p className="finding-where">{finding.where}</p>
        </div>
        <EvidenceStrip key={finding.id} finding={finding} />
        <div className="finding-proof" data-pair={Boolean(images.expected)} data-view={view}>
          {images.expected && <div className="finding-proof-toggle" role="group" aria-label="Screenshot">
            <button aria-pressed={view === 'before'} onClick={() => setView('before')}>{images.before.label}</button>
            <button aria-pressed={view === 'expected'} onClick={() => setView('expected')}>{images.expected.label}</button>
          </div>}
          <div className="finding-shots">
            {[images.before, images.expected].filter(Boolean).map(image => <figure key={image!.src} className="finding-shot" data-current={image === shown}>
              <Image src={image!.src} alt={image!.alt} width={shotSize[image!.src][0]} height={shotSize[image!.src][1]} sizes="(min-width: 1024px) 40vw, 90vw" />
              <figcaption>{image!.label}</figcaption>
            </figure>)}
          </div>
          <p className="finding-caption">{finding.caption}</p>
        </div>
        <div className="finding-repro">
          <h4>Steps to reproduce</h4>
          <ol>{finding.steps.map(item => <li key={item}>{item}</li>)}</ol>
          <dl>
            <div><dt>Expected</dt><dd>{finding.expected}</dd></div>
            <div data-actual><dt>Actual</dt><dd>{finding.actual}</dd></div>
          </dl>
        </div>
      </div>
    </div>
  </section>;
}

// Pixel sizes of the crops written by build_crosscheck_run.py.
const shotSize: Record<string, [number, number]> = {
  '/images/crosscheck/cc-003-actual.png': [1280, 440],
  '/images/crosscheck/cc-001-before.png': [744, 420],
  '/images/crosscheck/cc-001-expected.png': [744, 420],
  '/images/crosscheck/cc-017-before.png': [383, 824],
  '/images/crosscheck/cc-017-expected.png': [619, 824],
  '/images/crosscheck/cc-015-before.png': [383, 824],
  '/images/crosscheck/cc-015-expected.png': [383, 824],
};

export function NextTeaser({ lines }: { lines: readonly string[] }) {
  return <p className="case-next-deck">{lines.map((line, i) => <Fragment key={line}>{i > 0 && <br />}{line}</Fragment>)}</p>;
}
