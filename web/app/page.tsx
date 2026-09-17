import Image from 'next/image';
import type { CSSProperties } from 'react';
import { instruments } from '@/lib/instruments';
import { scanLanes } from '@/lib/crosscheck-room';
import SkillDeck from '@/components/skill-deck';

// Contact destinations supplied by the owner, 2026-09-15.
const EMAIL = 'rayinailham9@gmail.com';
const contactLinks = [
  { name: 'Email', label: EMAIL, href: `mailto:${EMAIL}`, external: false },
  { name: 'LinkedIn', label: 'Rayina Ilham', href: 'https://www.linkedin.com/in/rayinailham/', external: true },
  { name: 'GitHub', label: 'Rayina Ilham', href: 'https://github.com/rayinailham', external: true },
  { name: 'Upwork', label: 'Rayina Ilham', href: 'https://www.upwork.com/freelancers/~0107019e8124d357e2', external: true },
];

export default function Home() {
  return <main>
    <div id="first-light">
    <section className="hero-stage" aria-labelledby="hero-heading">
      <div className="hero-copy">
        <p className="hero-byline">Rayina Ilham</p>
        <h2 id="hero-heading" tabIndex={-1}>I automate.<br />I test.</h2>
        <p className="positioning">I’m an automation engineer. I build systems that test web apps, fill forms and monitor changing data.</p>
      </div>
      <p className="dome-caption">The observatory is open.</p>
    </section>
    </div>
    {instruments.map((instrument, index) => <section key={instrument.id} id={instrument.id} className="instrument-journey" aria-labelledby={`${instrument.id}-heading`}>
      <div className="instrument-stage">
        <div className="instrument-copy">
          <p className="instrument-kicker">{String(index + 1).padStart(2, '0')} / {instrument.category}</p>
          <h2 id={`${instrument.id}-heading`} tabIndex={-1}>{instrument.name}</h2>
          <p className="instrument-pitch">{instrument.pitch}</p>
        </div>
        <div className="instrument-reading">
          <div className="proof-reading"><strong>{instrument.reading}</strong><span>{instrument.id === 'surgeline' ? 'input rows · 49,950 unique' : instrument.unit}<br /><small>{instrument.context}</small></span></div>
          <button className="case-button" data-open-case={instrument.id}>Open case file <span aria-hidden="true">↗</span></button>
          {instrument.id === 'brandwall'
            ? <p className="orbit-hint" id="observer-readout" data-observed="false">Tap to observe · <b className="when-off">detector off, wave pattern</b><b className="when-on">detector on, particle pattern</b></p>
            : instrument.id === 'crosscheck'
              // Phase 7A (approved at gate 2026-09-16): the lenses sweep three browser lanes; each lane fills its 3 screen sizes × 3 roles as you orbit.
              ? <div className="scan-strip" role="img" aria-label="Scan pattern: three browsers, each checked at three screen sizes as three user roles">{scanLanes.map((lane, i) => <div key={lane} className="scan-lane" data-lane={i}>
                <span>{lane}</span><div aria-hidden="true">{Array.from({ length: 9 }, (_, c) => <i key={c} style={{ '--c': c } as CSSProperties} />)}</div>
              </div>)}</div>
              // Phase 7B (approved at gate 2026-09-17): three browser lanes fill with the orbit; lane 2 stops mid-way, then resumes where it stopped.
              : instrument.id === 'surgeline'
                ? <div className="dispatch-chapter" role="img" aria-label="Illustration: three browsers send records from a saved work list; browser 2 is cut, resumes, and every record reaches an outcome">{[0, 1, 2].map(lane => <div key={lane} className="dispatch-strand" data-strand={lane}>
                  <span>Browser {lane + 1}{lane === 1 && <b><em>cut</em><em>resumed</em></b>}</span><div aria-hidden="true">{Array.from({ length: 8 }, (_, c) => <i key={c} style={{ '--c': c } as CSSProperties} />)}</div>
                </div>)}<small>amber sent · green receipt saved · crash demo inside ↗</small></div>
              : instrument.id === 'driftwatch'
                ? <div className="monitor-chapter" role="img" aria-label="Illustrated trace: quiet collection, then an empty-run alarm; compare snapshots inside">
                  <svg viewBox="0 0 320 28" preserveAspectRatio="none" aria-hidden="true"><path className="monitor-chapter-base" d="M0 15H320" /><path className="monitor-chapter-line" pathLength="1" d="M0 15H118L126 13L136 17L144 15H195L203 3L211 25L220 12L228 15H320" /><path className="monitor-chapter-alarm" pathLength="1" d="M195 15L203 3L211 25L220 12L228 15" /></svg>
                  <span><b><em>Last good snapshot → compare</em><em>Empty run → alarm</em></b><small>Illustration</small></span>
                </div>
              : <p className="orbit-hint">Scroll to orbit the instrument</p>}
        </div>
      </div>
    </section>)}
    <div className="after-instruments">
      <section id="skills" className="text-section" aria-labelledby="skills-heading">
        <p className="section-kicker">The toolkit</p>
        <h2 id="skills-heading" tabIndex={-1}>Skills, with proof.</h2>
        <p className="section-intro">Drag the deck. Each card explains its tools, then links to the case files that prove them.</p>
        <SkillDeck />
      </section>
      <section id="about" className="text-section about-section" aria-labelledby="about-heading">
        <p className="section-kicker">Behind the instruments</p>
        <h2 id="about-heading" tabIndex={-1}>I’m Rayina Ilham.</h2>
        <figure className="portrait-scan">
          <Image src="/images/rayina-duotone.png" alt="Portrait of Rayina Ilham, treated in navy duotone with subtle scan lines" width={1086} height={1448} sizes="(min-width: 1024px) 440px, (max-width: 430px) calc(100vw - 48px), 382px" />
          <span className="scan-line" aria-hidden="true" />
          <figcaption>Rayina Ilham / Rayin Observatory</figcaption>
        </figure>
        <p>I build tools that check web apps, move spreadsheet rows through forms, and keep watch over changing data.</p>
        <p>I test what happens when things go wrong, then turn the results into clear reports. The work here uses owned test apps, synthetic data and documented sources, with limits stated alongside the proof.</p>
      </section>
      <section id="contact" className="text-section contact-section" aria-labelledby="contact-heading">
        <p className="section-kicker">Start a conversation</p>
        <h2 id="contact-heading" tabIndex={-1}>What needs<br />a closer look?</h2>
        <p className="section-intro">Tell me what you need to test, automate or monitor.</p>
        <a className="email-cta" href={`mailto:${EMAIL}`}>Email me <span aria-hidden="true">↗</span></a>
        <ul className="contact-links">{contactLinks.map(link => <li key={link.name}><a href={link.href} {...(link.external ? { target: '_blank', rel: 'noopener noreferrer' } : {})} aria-label={`${link.name}: ${link.label}`}>{link.name}<span aria-hidden="true">{link.label} ↗</span></a></li>)}</ul>
        <p className="footer-signature">Rayina Ilham<br /><span>Rayin Observatory</span></p>
        <a href="#first-light" data-scroll-target="#first-light" className="back-to-top">Back to the dome ↑</a>
      </section>
    </div>
  </main>;
}
