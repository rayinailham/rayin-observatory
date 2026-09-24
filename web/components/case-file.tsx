'use client';

import { Fragment, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { gsap } from 'gsap';
import { caseFiles } from '@/lib/cases';
import { instruments, type InstrumentId } from '@/lib/instruments';
import { FindingSheet, InspectionField, NextTeaser } from './crosscheck-room';
import { DispatchRoom, DispatchEvidence } from './surgeline-room';
import { MonitoringRoom, MonitoringEvidence } from './driftwatch-room';
import { TimeControlRoom, TimeEvidence } from './duewatch-room';
import { VisualStudio, StudioEvidence } from './brandwall-room';

const lines = (text: readonly string[]) => text.map((line, i) => <Fragment key={line}>{i > 0 && <br />}{line}</Fragment>);

export default function CaseFile({ id }: { id: InstrumentId }) {
  const index = caseFiles.findIndex(item => item.id === id);
  const file = caseFiles[index];
  const { name, category } = instruments.find(item => item.id === id)!;
  const next = instruments.find(item => item.id === caseFiles[(index + 1) % caseFiles.length].id)!;
  const [selected, setSelected] = useState<number | null>(null);
  const root = useRef<HTMLElement>(null);
  const card = useRef<HTMLDivElement>(null);
  const cardMotion = useRef<Animation | null>(null);
  function inspect(next: number | null, pointer: boolean) {
    setSelected(next);
    cardMotion.current?.cancel();
    if (pointer) cardMotion.current = card.current?.animate([
      { opacity: .55, transform: 'translateY(5px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ], { duration: 180, easing: 'cubic-bezier(.23, 1, .32, 1)' }) ?? null;
  }
  useEffect(() => {
    const context = gsap.context(() => {}, root);
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const display = entry.target.querySelector<HTMLElement>('[data-count]')!;
      const target = Number(display.dataset.count);
      const counter = { value: 0 };
      context.add(() => gsap.to(counter, { value: target, duration: 1.25, ease: 'power2.out',
        onUpdate: () => { display.textContent = Math.round(counter.value).toLocaleString('en-US'); },
      }));
      observer.unobserve(entry.target);
    }), { threshold: .55 });
    root.current?.querySelectorAll('.case-reading').forEach(item => observer.observe(item));
    return () => { cardMotion.current?.cancel(); observer.disconnect(); context.revert(); };
  }, []);

  return <main ref={root} className="case-page" data-case={id}>
    <section className="case-brief" aria-labelledby="case-heading">
      <div className="case-title">
      <Link onNavigate={event => event.preventDefault()} className="case-back" href={`/#${id}`} data-home-target="return">↙ Return to the instrument</Link>
      <p className="section-kicker">Case file {String(index + 1).padStart(2, '0')} / {category}{file.draft && <span className="draft-label">DRAFT</span>}</p>
      <h1 id="case-heading" tabIndex={-1}>{name}</h1>
      <p className="case-deck">{lines(file.deck)}</p>
      </div>
      <div className="case-brief-copy">
      <h2>Brief</h2>
      {file.brief.map(paragraph => <p key={paragraph}>{paragraph}</p>)}
      <p className="case-context">{file.context}</p>
      </div>
    </section>

    <section id="case-instrument" className="case-instrument" aria-labelledby="instrument-heading">
      <div className="case-instrument-heading"><p className="section-kicker">The instrument</p><h2 id="instrument-heading">{lines(file.instrumentHeading)}</h2><p>Tap a marker to inspect a component.</p></div>
      <div className="case-inspection">
      <div className="case-instrument-still" aria-hidden="true" style={{ backgroundImage: `url('/images/${id}-fallback.png')` }} />
      <svg className="hotspot-leaders" aria-hidden="true">
        {file.components.map((item, i) => <line key={item.id} data-hotspot-line={item.id} data-active={selected === i} x1={`${item.marker[0]}%`} y1={`${item.marker[1]}%`} x2="50%" y2="45%" />)}
      </svg>
      {file.components.map((item, i) => <button key={item.id} className={`instrument-hotspot hotspot-${i}`} data-hotspot={item.id}
        style={{ left: `${item.marker[0]}%`, top: `${item.marker[1]}%` }}
        aria-label={`Inspect ${item.title}`} aria-expanded={selected === i} aria-controls="component-card"
        onClick={event => inspect(selected === i ? null : i, event.detail > 0)}>{String(i + 1).padStart(2, '0')}</button>)}
      </div>
      <div ref={card} id="component-card" className="component-card" data-selected={selected !== null} aria-live="polite">
        {selected === null ? <><p className="section-kicker">Inspection controls</p><p>{lines(file.components.map((item, i) => `${String(i + 1).padStart(2, '0')} / ${item.title}`))}</p></> : <>
          <div className="component-card-top"><h3>{file.components[selected].title}</h3><button aria-label="Close component card" onClick={event => inspect(null, event.detail > 0)}>×</button></div>
          <p className="component-label">{file.components[selected].label}</p><p>{file.components[selected].body}</p>
        </>}
      </div>
    </section>

    <div className="case-details">
      {/* Personal rooms replace the shared flow only when their phase is active. */}
      {id === 'crosscheck' ? <><InspectionField /><FindingSheet /></> : id === 'surgeline' ? <><DispatchRoom /><DispatchEvidence /></> : id === 'driftwatch' ? <><MonitoringRoom /><MonitoringEvidence /></> : id === 'duewatch' ? <><TimeControlRoom /><TimeEvidence /></> : id === 'brandwall' ? <><VisualStudio /><StudioEvidence /></> : <section className="case-section" aria-labelledby="flow-heading">
        <p className="section-kicker">How it works</p><h2 id="flow-heading">{lines(file.flowHeading)}</h2>
        <ol className="signal-flow">{file.flow.map(step => <li key={step.title}><span className="signal-node" aria-hidden="true" /><h3>{step.title}</h3><p>{step.body}</p></li>)}</ol>
      </section>}

      <section className="case-section" aria-labelledby="readings-heading">
        <p className="section-kicker">Readings</p><h2 id="readings-heading">{lines(file.readingsHeading)}</h2>
        <p>{file.readingsIntro}</p>
        <div className="case-readings">{file.readings.map(item => <article className="case-reading" key={item.label}>
          <strong aria-label={`${item.value.toLocaleString('en-US')}${item.suffix} ${item.label}`}><span aria-hidden="true" data-count={item.value}>{item.value.toLocaleString('en-US')}</span><span aria-hidden="true">{item.suffix}</span></strong>
          <h3>{item.label}</h3><p>{item.context}</p>
        </article>)}</div>
        <details className="case-limits"><summary>What these results cover <span aria-hidden="true">+</span></summary>
          {file.limits.map(paragraph => <p key={paragraph}>{paragraph}</p>)}
        </details>
      </section>

      <section className="case-section" aria-labelledby="tools-heading"><p className="section-kicker">Tools used</p><h2 id="tools-heading">The working kit.</h2>
        <p>Explore the skills behind this instrument.</p><ul className="case-tools">{file.tools.map(tool => <li key={tool}><Link onNavigate={event => event.preventDefault()} href="/#skills" data-home-target="#skills">{tool}<span aria-hidden="true">↗</span></Link></li>)}</ul>
      </section>

      <section className="case-section" aria-labelledby="demo-heading"><p className="section-kicker">Demo video</p><h2 id="demo-heading">See the evidence.</h2>
        <p>{file.video.intro}</p>
        <video className="case-video" controls playsInline muted preload="none" poster={`/images/${id}-demo-poster.jpg`} aria-label={file.video.label}>
          <source src={`/videos/${id}-explainer.mp4`} type="video/mp4" />Your browser does not support embedded video.
        </video>
        <a className="case-video-link" href={`/videos/${id}-explainer.mp4`}>Open video full size ↗</a>
      </section>

      <section className="case-section case-next" aria-labelledby="next-heading"><p className="section-kicker">Next instrument</p><h2 id="next-heading">{next.name}</h2>
        {id === 'crosscheck' && <NextTeaser lines={caseFiles[(index + 1) % caseFiles.length].deck} />}
        {id === 'brandwall' && <p className="brand-next">The image has its evidence. Next, look through CrossCheck’s three lenses: browsers, permissions and the work a user needs to finish.</p>}
        {id === 'duewatch' && <p className="time-next">The schedule has its limits. Next, turn to BrandWall’s visual studio: compare brand assets across surfaces and see exactly where layouts break.</p>}
        {id === 'driftwatch' && <p className="monitor-next">The data has a history. Next, give the work a schedule — with DueWatch’s contract checks and human handoff.</p>}
        {id === 'surgeline' && <div className="dispatch-next"><span aria-hidden="true">─ ─ ─ ╱╲ ─ ─</span><p>The dispatch is accounted for. Next, watch what changes between one day and the next.</p></div>}
        <Link onNavigate={event => event.preventDefault()} className="case-button" href={`/work/${next.id}`} data-case-target={next.id}>Open the next case file <span aria-hidden="true">↗</span></Link>
        <Link onNavigate={event => event.preventDefault()} className="case-back" href={`/#${id}`} data-home-target="return">↙ Return to {name}</Link>
      </section>
    </div>
  </main>;
}
