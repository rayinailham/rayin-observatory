'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { gsap } from 'gsap';
import { components, readings, caseTools } from '@/lib/crosscheck-case';

export default function CrossCheckCase() {
  const [selected, setSelected] = useState<number | null>(null);
  const root = useRef<HTMLElement>(null);
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
    return () => { observer.disconnect(); context.revert(); };
  }, []);

  return <main ref={root} className="case-page">
    <section className="case-brief" aria-labelledby="case-heading">
      <Link onNavigate={event => event.preventDefault()} className="case-back" href="/#crosscheck" data-home-target="return">↙ Return to the instrument</Link>
      <p className="section-kicker">Case file 01 / Web QA</p>
      <h1 id="case-heading" tabIndex={-1}>CrossCheck</h1>
      <p className="case-deck">Find the gaps.<br />Bring back proof.</p>
      <h2>Brief</h2>
      <p>Your app can work in one browser and fail in another. Different screens and user permissions make the gaps harder to spot.</p>
      <p>I build repeatable checks, then turn the results into a short list of issues with steps, screenshots and priorities.</p>
      <p className="case-context">Owned WordPress + CRM demo. Results shown here come from a test app with deliberately planted bugs.</p>
    </section>

    <section id="case-instrument" className="case-instrument" aria-labelledby="instrument-heading">
      <div className="case-instrument-heading"><p className="section-kicker">The instrument</p><h2 id="instrument-heading">Three lenses.<br />One target.</h2><p>Tap a marker to inspect a component.</p></div>
      <div className="case-instrument-still" aria-hidden="true" />
      <svg className="hotspot-leaders" aria-hidden="true">
        {components.map((item, i) => <line key={item.id} data-hotspot-line={item.node} x1={i === 1 ? '88%' : '12%'} y1={`${[32, 44, 57][i]}%`} x2="50%" y2="45%" />)}
      </svg>
      {components.map((item, i) => <button key={item.id} className={`instrument-hotspot hotspot-${i}`} data-hotspot={item.node}
        aria-label={`Inspect ${item.title}`} aria-expanded={selected === i} aria-controls="component-card"
        onClick={() => setSelected(selected === i ? null : i)}>{String(i + 1).padStart(2, '0')}</button>)}
      <div id="component-card" className="component-card" aria-live="polite">
        {selected === null ? <><p className="section-kicker">Inspection controls</p><p>01 / Browser matrix<br />02 / Access checks<br />03 / End-to-end flows</p></> : <>
          <div className="component-card-top"><h3>{components[selected].title}</h3><button aria-label="Close component card" onClick={() => setSelected(null)}>×</button></div>
          <p className="component-label">{components[selected].label}</p><p>{components[selected].body}</p>
        </>}
      </div>
    </section>

    <div className="case-details">
      <section className="case-section" aria-labelledby="flow-heading">
        <p className="section-kicker">How it works</p><h2 id="flow-heading">From page visits<br />to a clear report.</h2>
        <ol className="signal-flow">
          <li><span className="signal-node" aria-hidden="true" /><h3>Map the app</h3><p>I discover pages and define who should be allowed to open each one.</p></li>
          <li><span className="signal-node" aria-hidden="true" /><h3>Run the checks</h3><p>Browser checks, permission checks and full user tasks collect results and screenshots.</p></li>
          <li><span className="signal-node" aria-hidden="true" /><h3>Verify & sort</h3><p>I confirm suspected access leaks, merge duplicates and remove expected behavior using documented rules.</p></li>
          <li><span className="signal-node" aria-hidden="true" /><h3>Hand over the evidence</h3><p>A spreadsheet and screenshot gallery show what failed, how to reproduce it and what needs attention first.</p></li>
        </ol>
      </section>

      <section className="case-section" aria-labelledby="readings-heading">
        <p className="section-kicker">Readings</p><h2 id="readings-heading">Measured on<br />the demo.</h2>
        <p>These are recorded results from the owned test app, not live counters or client production results.</p>
        <div className="case-readings">{readings.map(item => <article className="case-reading" key={item.label}>
          <strong aria-label={`${item.value.toLocaleString('en-US')}${item.suffix} ${item.label}`}><span aria-hidden="true" data-count={item.value}>{item.value.toLocaleString('en-US')}</span><span aria-hidden="true">{item.suffix}</span></strong>
          <h3>{item.label}</h3><p>{item.context}</p>
        </article>)}</div>
        <details className="case-limits"><summary>What these results cover <span aria-hidden="true">+</span></summary>
          <p>The 881 signals include browser findings, permission violations and a failed user flow. They became 18 unique issues. A later clean-copy run changed the raw finding count while retaining the same 18 issues.</p>
          <p>Screen sizes are emulated. Permission violations were confirmed in Chromium desktop. This work checks web behavior and access rules; penetration testing, load testing and human judgment about business rules sit outside its scope.</p>
        </details>
      </section>

      <section className="case-section" aria-labelledby="tools-heading"><p className="section-kicker">Tools used</p><h2 id="tools-heading">The working kit.</h2>
        <p>Explore the skills behind this instrument.</p><ul className="case-tools">{caseTools.map(tool => <li key={tool}><Link onNavigate={event => event.preventDefault()} href="/#skills" data-home-target="#skills">{tool}<span aria-hidden="true">↗</span></Link></li>)}</ul>
      </section>

      <section className="case-section" aria-labelledby="demo-heading"><p className="section-kicker">Demo video</p><h2 id="demo-heading">See the evidence.</h2>
        <p>English captions. No audio. Original demo footage, with its progress replay clearly labeled.</p>
        <video className="case-video" controls playsInline muted preload="none" poster="/images/crosscheck-demo-poster.jpg" aria-label="CrossCheck demo with burned-in English captions">
          <source src="/videos/crosscheck-explainer.mp4" type="video/mp4" />Your browser does not support embedded video.
        </video>
        <a className="case-video-link" href="/videos/crosscheck-explainer.mp4">Open video full size ↗</a>
      </section>

      <section className="case-section case-next" aria-labelledby="next-heading"><p className="section-kicker">Next instrument</p><h2 id="next-heading">SurgeLine</h2>
        <Link onNavigate={event => event.preventDefault()} className="case-button" href="/#surgeline" data-home-target="#surgeline">Explore on the observatory floor <span aria-hidden="true">↗</span></Link>
        <Link onNavigate={event => event.preventDefault()} className="case-back" href="/#crosscheck" data-home-target="return">↙ Return to CrossCheck</Link>
      </section>
    </div>
  </main>;
}
