import Image from 'next/image';
import { instruments } from '@/lib/instruments';
import { skillGroups } from '@/lib/skills';

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
          <div className="proof-reading"><strong>{instrument.reading}</strong><span>{instrument.unit}<br /><small>{instrument.context}</small></span></div>
          <button className="case-button" data-open-case={instrument.id} aria-haspopup="dialog">Open case file <span aria-hidden="true">↗</span></button>
          <p className="orbit-hint">Scroll to orbit the instrument</p>
        </div>
      </div>
    </section>)}
    <div className="after-instruments">
      <section id="skills" className="text-section" aria-labelledby="skills-heading">
        <p className="section-kicker">The toolkit</p>
        <h2 id="skills-heading" tabIndex={-1}>Skills, with proof.</h2>
        <p className="section-intro">Choose a project beside each skill to explore the work behind it.</p>
        <div className="skill-groups">{skillGroups.map(group => <details key={group.name} className="skill-group">
          <summary>{group.name}<span aria-hidden="true">+</span></summary>
          <ul>{group.items.map(skill => <li key={skill.name}><h3>{skill.name}</h3>{skill.projects.length > 0 && <div className="skill-projects">{skill.projects.map(id => <a key={id} href={`#${id}`} data-skill-project={id} aria-label={`${skill.name}: explore ${instruments.find(item => item.id === id)?.name}`}>{instruments.find(item => item.id === id)?.name}<span aria-hidden="true">↗</span></a>)}</div>}</li>)}</ul>
        </details>)}</div>
      </section>
      <section id="about" className="text-section about-section" aria-labelledby="about-heading">
        <p className="section-kicker">Behind the instruments</p>
        <h2 id="about-heading" tabIndex={-1}>I’m Rayina Ilham.</h2>
        <figure className="portrait-scan">
          <Image src="/images/rayina-duotone.png" alt="Portrait of Rayina Ilham, treated in navy duotone with subtle scan lines" width={1086} height={1448} sizes="(max-width: 430px) calc(100vw - 48px), 382px" />
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
