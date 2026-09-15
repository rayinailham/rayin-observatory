'use client';

import dynamic from 'next/dynamic';
import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import type { CaseView } from '@/lib/crosscheck-case';
import { useProgress } from '@react-three/drei';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ObservatoryAudio } from '@/lib/ambient';
import { instruments, type ChapterState } from '@/lib/instruments';

const Scene = dynamic(() => import('./observatory-scene'), { ssr: false });
const SOUND_KEY = 'rayin-observatory:sound';

export default function ObservatoryShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isCase = pathname === '/work/crosscheck';
  const caseView = useRef<CaseView>({ mix: 0, active: false });
  const homeScroll = useRef<number | null>(null);
  const homeChapter = useRef<ChapterState | null>(null);
  const homeTarget = useRef<number | string | null>(null);
  const previousPath = useRef(pathname);
  const [flying, setFlying] = useState(false);
  const pageContent = useRef<HTMLDivElement>(null);
  const [entered, setEntered] = useState(false);
  const [sceneReady, setSceneReady] = useState(false);
  const [fontsReady, setFontsReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [sound, setSound] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<(typeof instruments)[number]>(instruments[0]);
  const [caseOpen, setCaseOpen] = useState(false);
  const [loadSlow, setLoadSlow] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const gate = useRef<HTMLDivElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const menu = useRef<HTMLDialogElement>(null);
  const caseFile = useRef<HTMLDialogElement>(null);
  const readout = useRef<HTMLOutputElement>(null);
  const progress = useRef(0);
  const chapter = useRef<ChapterState>({ reveal: 0, orbit: 0, index: 0, transition: 0, outro: 0 });
  const lenis = useRef<Lenis | null>(null);
  const audio = useRef<ObservatoryAudio | null>(null);
  const { progress: modelProgress } = useProgress();
  const ready = fontsReady && (sceneReady || failed);
  const loaded = ready ? 100 : Math.min(99, Math.round(modelProgress * .7 + (fontsReady ? 30 : 0)));
  const onReady = useCallback(() => setSceneReady(true), []);
  const onFailure = useCallback(() => setFailed(true), []);

  useEffect(() => {
    let active = true;
    Promise.all([
      document.fonts.load('400 16px Fraunces'),
      document.fonts.load('400 16px Inter'),
      document.fonts.load('400 16px "JetBrains Mono"'),
    ]).then(() => { if (active) setFontsReady(true); })
      .catch(() => { if (active) setFontsReady(true); });
    const timeout = window.setTimeout(() => setLoadSlow(true), 15000);
    const engine = new ObservatoryAudio();
    audio.current = engine;
    document.addEventListener('visibilitychange', engine.visibilityChanged);
    return () => {
      active = false;
      window.clearTimeout(timeout);
      document.removeEventListener('visibilitychange', engine.visibilityChanged);
      engine.dispose();
      audio.current = null;
    };
  }, []);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const scroller = new Lenis({ autoRaf: false, smoothWheel: true, syncTouch: true, lerp: .085 });
    lenis.current = scroller;
    scroller.stop();
    scroller.on('scroll', ScrollTrigger.update);
    const tick = (time: number) => scroller.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    return () => {
      scroller.off('scroll', ScrollTrigger.update);
      gsap.ticker.remove(tick);
      scroller.destroy();
      lenis.current = null;
    };
  }, []);

  useLayoutEffect(() => {
    const cameFromCase = previousPath.current === '/work/crosscheck' && !isCase;
    previousPath.current = pathname;
    const scroller = lenis.current;
    let frame = 0;
    let focusAfterFlight: HTMLElement | null = null;
    const context = gsap.context(() => {}, root);
    caseView.current.active = isCase;
    if (isCase) {
      chapter.current = { reveal: 1, orbit: 0, index: 0, transition: 1, outro: 0 };
      root.current?.setAttribute('data-chapter', 'crosscheck');
      root.current?.style.setProperty('--chapter-reveal', '1');
      scroller?.scrollTo(0, { immediate: true, force: true });
      window.scrollTo(0, 0);
      context.add(() => gsap.to(caseView.current, { mix: 1, duration: .85, ease: 'power2.inOut' }));
    }
    if (cameFromCase) {
      const destination = homeTarget.current ?? homeScroll.current ?? '#crosscheck';
      const element = typeof destination === 'string' ? document.querySelector<HTMLElement>(destination) : null;
      const y = typeof destination === 'number' ? destination : element ? element.getBoundingClientRect().top + window.scrollY : 0;
      scroller?.resize();
      scroller?.scrollTo(y, { immediate: true, force: true });
      window.scrollTo(0, y);
      context.add(() => gsap.to(caseView.current, { mix: 0, duration: .9, ease: 'power2.inOut' }));
      frame = requestAnimationFrame(() => {
        ScrollTrigger.refresh();
        focusAfterFlight = element?.querySelector<HTMLElement>('h2') ?? document.querySelector<HTMLElement>('[data-open-case="crosscheck"]');
      });
      homeTarget.current = null;
    }
    context.add(() => gsap.fromTo(pageContent.current, { opacity: 0 }, { opacity: 1, duration: .65, delay: .3,
      onComplete: () => {
        setFlying(false);
        frame = requestAnimationFrame(() => {
          // React must release inert before focus can move into the arriving page.
          (isCase ? document.getElementById('case-heading') : focusAfterFlight)?.focus({ preventScroll: true });
        });
      },
    }));
    return () => { context.revert(); cancelAnimationFrame(frame); };
  }, [pathname, isCase]);

  useEffect(() => {
    // Scroll ownership stays in the root. Route-specific triggers are rebuilt per page.
    const sections = instruments.map(item => document.getElementById(item.id));
    if (isCase || sections.some(section => !section)) {
      const trigger = ScrollTrigger.create({ trigger: 'main', start: 'top top', end: 'bottom bottom',
        onUpdate: self => {
          if (readout.current) readout.current.textContent = `${Math.round(self.progress * 100).toString().padStart(3, '0')}%`;
          root.current?.style.setProperty('--journey', String(self.progress));
        },
      });
      const observer = new ResizeObserver(() => ScrollTrigger.refresh());
      const main = document.querySelector('main');
      if (main) observer.observe(main);
      return () => { trigger.kill(); observer.disconnect(); };
    }
    const homeSections = sections as HTMLElement[];
    let positions: { top: number; height: number }[] = [];
    let skillsTop = 0;
    // A route change can refresh or scroll before React cleans up this trigger; the homepage
    // DOM is already gone then, so its stale sections must not measure or rewrite chapter state.
    const live = () => homeSections[0].isConnected;
    const measure = () => {
      positions = homeSections.map(section => ({ top: section.getBoundingClientRect().top + window.scrollY, height: section.offsetHeight }));
      skillsTop = document.getElementById('skills')!.getBoundingClientRect().top + window.scrollY;
    };
    const clamp = (n: number) => Math.max(0, Math.min(1, n));
    const syncChapters = () => {
      const y = window.scrollY;
      const height = homeSections[0].querySelector<HTMLElement>('.instrument-stage')!.offsetHeight;
      let index = 0;
      positions.forEach((pos, i) => { if (y >= pos.top - height) index = i; });
      const pos = positions[index];
      const reveal = clamp((y - positions[0].top + height) / height);
      const transition = clamp((y - pos.top + height) / height);
      const outro = clamp((y - skillsTop + height) / height);
      chapter.current = { index, reveal, transition, outro, orbit: clamp((y - pos.top) / Math.max(1, pos.height - height)) };
      root.current?.style.setProperty('--chapter-reveal', String(reveal));
      root.current?.setAttribute('data-chapter', outro >= 1 ? 'outro' : reveal > .4 ? instruments[index].id : 'dome');
      homeSections.forEach((_, i) => {
        const offset = i === index ? 1 - transition : i === index - 1 ? -transition : 2;
        root.current?.style.setProperty(`--instrument-${i}-offset`, String(offset - (i === index ? outro : 0)));
      });
    };
    measure();
    syncChapters();
    const trigger = ScrollTrigger.create({
      trigger: 'main', start: 'top top', end: 'bottom bottom',
      onRefresh: () => { if (live()) { measure(); syncChapters(); } },
      onUpdate: self => {
        if (!live()) return;
        syncChapters();
        if (readout.current) readout.current.textContent = `${Math.round(self.progress * 100).toString().padStart(3, '0')}%`;
        root.current?.style.setProperty('--journey', String(self.progress));
      },
    });
    const heroTrigger = ScrollTrigger.create({
      trigger: '#first-light', start: 'top top', end: 'bottom bottom',
      onUpdate: self => {
        progress.current = self.progress;
        root.current?.style.setProperty('--hero-journey', String(self.progress));
        root.current?.style.setProperty('--copy-opacity', String(Math.max(0, 1 - self.progress * 2.8)));
      },
    });
    const scan = gsap.fromTo('.portrait-scan img', { clipPath: 'inset(0 0 100% 0)' }, {
      clipPath: 'inset(0 0 0% 0)', ease: 'none',
      scrollTrigger: { trigger: '.portrait-scan', start: 'top 82%', end: 'center 50%', scrub: true },
    });
    const scanLine = gsap.fromTo('.scan-line', { top: '0%' }, { top: '100%', ease: 'none',
      scrollTrigger: { trigger: '.portrait-scan', start: 'top 82%', end: 'center 50%', scrub: true },
    });
    const observer = new ResizeObserver(() => ScrollTrigger.refresh());
    observer.observe(document.querySelector('main')!);
    return () => {
      trigger.kill();
      heroTrigger.kill();
      observer.disconnect();
      scan.scrollTrigger?.kill(); scan.kill();
      scanLine.scrollTrigger?.kill(); scanLine.kill();
    };
  }, [pathname, isCase]);

  useEffect(() => {
    if (entered && !menuOpen && !caseOpen && !flying) lenis.current?.start();
    else lenis.current?.stop();
  }, [entered, menuOpen, caseOpen, flying]);

  useEffect(() => {
    if (!entered) return;
    const context = gsap.context(() => {
      gsap.to(gate.current, { opacity: 0, yPercent: -4, duration: .7, ease: 'power2.inOut',
        onComplete: () => { if (gate.current) gate.current.hidden = true; } });
      if (document.querySelector('.hero-copy')) gsap.fromTo('.hero-copy', { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 1.1, delay: .3, ease: 'power3.out' });
    }, root);
    const timer = window.setTimeout(() => {
      (document.getElementById('case-heading') ?? document.getElementById('hero-heading'))?.focus({ preventScroll: true });
      ScrollTrigger.refresh();
    }, 750);
    return () => { context.revert(); window.clearTimeout(timer); };
  }, [entered]);

  async function setAudio(enabled: boolean) {
    try {
      const playing = await audio.current?.setEnabled(enabled) ?? false;
      setSound(playing);
      setAudioError(enabled && !playing);
      try { localStorage.setItem(SOUND_KEY, playing ? 'on' : 'off'); } catch { /* Private storage can be unavailable. */ }
    } catch {
      setSound(false);
      setAudioError(true);
    }
  }

  function enter(silent: boolean) {
    if (!ready || entered) return;
    let remembered = true;
    try { remembered = localStorage.getItem(SOUND_KEY) !== 'off'; } catch { /* Use the default. */ }
    // AudioContext is created/resumed synchronously inside this user gesture.
    void setAudio(!silent && remembered);
    lenis.current?.scrollTo(0, { immediate: true, force: true });
    setEntered(true);
  }

  function openMenu() { setMenuOpen(true); menu.current?.showModal(); }
  function openContact() { scrollFromMenu('#contact'); }
  // Lenis start() resets and cancels any running scrollTo, so restart before scrolling;
  // the menu-close effect's later start() is then a no-op.
  function scrollFromMenu(target: number | string) {
    if (isCase) { leaveCase(target); return; }
    menu.current?.close();
    setMenuOpen(false);
    lenis.current?.start();
    // Native focus/accordion scrolling can advance window.scrollY before Lenis catches up.
    // Resolve element destinations against the browser's actual position, not animatedScroll.
    const element = typeof target === 'string' ? document.querySelector<HTMLElement>(target) : null;
    const destination = typeof target === 'number' ? target : element ? element.getBoundingClientRect().top + window.scrollY : null;
    if (destination === null) return;
    lenis.current?.scrollTo(destination, { force: true, onComplete: () => {
      if (typeof target === 'string') document.querySelector<HTMLElement>(`${target} h2`)?.focus({ preventScroll: true });
    } });
  }
  function openCrossCheck() {
    if (flying) return;
    homeScroll.current = window.scrollY;
    homeChapter.current = { ...chapter.current };
    setFlying(true);
    lenis.current?.stop();
    router.prefetch('/work/crosscheck');
    gsap.to(pageContent.current, { opacity: 0, duration: .55 });
    gsap.to(caseView.current, { mix: 1, duration: .85, ease: 'power2.inOut',
      onComplete: () => router.push('/work/crosscheck', { scroll: false }),
    });
  }

  function leaveCase(target: number | string = 'return') {
    if (flying) return;
    menu.current?.close();
    setMenuOpen(false);
    homeTarget.current = target === 'return' ? homeScroll.current ?? '#crosscheck' : target;
    if (homeChapter.current) chapter.current = { ...homeChapter.current };
    setFlying(true);
    lenis.current?.stop();
    gsap.to(pageContent.current, { opacity: 0, duration: .3, onComplete: () => router.push('/', { scroll: false }) });
  }

  function returnToDome() { scrollFromMenu(0); }
  function goToWork() { scrollFromMenu('#crosscheck'); }

  return <div ref={root} className={`observatory ${entered ? 'has-entered' : ''}`} data-route={isCase ? 'case' : 'home'} data-flight={flying ? 'moving' : 'idle'} data-scene={failed ? 'fallback' : sceneReady ? 'ready' : 'loading'}>
    <div className="scene-layer" aria-hidden="true">
      {!failed && <Scene entered={entered} progress={progress} chapter={chapter} caseView={caseView} onReady={onReady} onFailure={onFailure} />}
      {failed && !isCase && <><div className="scene-fallback" />{instruments.map((item, i) => <div key={item.id} className={`instrument-fallback ${item.id}-fallback`} style={{ backgroundImage: `url('/images/${item.id}-fallback.png')`, transform: `translateY(calc(var(--instrument-${i}-offset, 2) * 100svh))` }} />)}</>}
    </div>
    <div ref={content} inert={!entered} className="site-content">
      <header className="site-header">
        <button className="wordmark" onClick={returnToDome} aria-label="Rayin Observatory, return to the dome">Rayin<span>Observatory</span></button>
        <div className="header-controls">
          <button className="sound-toggle" aria-label={sound ? 'Turn sound off' : 'Turn sound on'} aria-pressed={sound}
            onClick={() => void setAudio(!sound)}><span className="sound-bars" aria-hidden="true"><i /><i /><i /><i /></span><span>{sound ? 'On' : 'Off'}</span></button>
          <button className="menu-toggle" onClick={openMenu} aria-expanded={menuOpen} aria-controls="navigation">Menu<span aria-hidden="true">+</span></button>
        </div>
      </header>
      <div ref={pageContent} className="page-content" inert={flying} onClick={event => {
        const target = event.target as HTMLElement;
        const homeLink = target.closest<HTMLAnchorElement>('[data-home-target]');
        if (homeLink && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) { event.preventDefault(); leaveCase(homeLink.dataset.homeTarget); return; }
        const caseButton = target.closest<HTMLElement>('[data-open-case]');
        if (caseButton) {
          const item = instruments.find(item => item.id === caseButton.dataset.openCase);
          if (item?.id === 'crosscheck') { event.preventDefault(); openCrossCheck(); return; }
          if (item) { setSelectedCase(item); setCaseOpen(true); caseFile.current?.showModal(); }
        }
        const skill = target.closest<HTMLAnchorElement>('[data-skill-project]');
        const anchor = target.closest<HTMLAnchorElement>('[data-scroll-target]');
        if (skill || anchor) {
          event.preventDefault();
          const id = skill ? `#${skill.dataset.skillProject}` : anchor!.dataset.scrollTarget!;
          document.querySelectorAll('.skill-highlight').forEach(el => el.classList.remove('skill-highlight'));
          if (skill) document.querySelector(id)?.classList.add('skill-highlight');
          scrollFromMenu(id);
        }
      }}>{children}</div>
      <button className="hero-contact" onClick={openContact}>Contact <span aria-hidden="true">↗</span></button>
      <div className="progress-readout"><span>SCROLL</span><span className="readout-track" aria-hidden="true"><i /></span><output ref={readout} aria-label="Scroll progress">000%</output></div>
      {audioError && <p className="audio-notice" role="status">Sound could not start. Tap the sound control to retry.</p>}
      {failed && <p className="fallback-notice" role="status">Still view. Live 3D is unavailable on this device.</p>}
    </div>

    <div ref={gate} className="entry-gate" inert={entered} aria-label="Enter Rayin Observatory">
      <p className="gate-byline">A portfolio by Rayina Ilham</p>
      <div className="gate-main">
        <div className="calibration-orbit" aria-hidden="true"><span /><i /></div>
        <p className="gate-kicker">First light</p>
        <h1>Rayin<br />Observatory</h1>
        <div className="calibration-status" role="status"><span>{failed ? 'Still view ready' : ready ? 'Instruments calibrated' : 'Calibrating instruments…'}</span><output>{loaded}%</output></div>
        <div className="calibration-track" role="progressbar" aria-label="Loading instruments" aria-valuemin={0} aria-valuemax={100} aria-valuenow={loaded}><i style={{ transform: `scaleX(${loaded / 100})` }} /></div>
        <button className="enter-button" disabled={!ready} onClick={() => enter(false)}>Enter the Observatory <span aria-hidden="true">↗</span></button>
        <button className="silent-button" disabled={!ready} onClick={() => enter(true)}>Enter without sound</button>
        {loadSlow && !ready && <div className="loading-help"><p>Calibration is taking longer than expected.</p><button onClick={onFailure}>Continue with a still view</button></div>}
      </div>
      <p className="gate-note">Ambient sound after entry.<br />Your sound choice is remembered.</p>
    </div>

    <dialog ref={menu} id="navigation" className="control-dialog navigation-dialog" onClose={() => setMenuOpen(false)} onCancel={() => setMenuOpen(false)}>
      <div className="dialog-top"><span>Rayin Observatory</span><button onClick={() => menu.current?.close()}>Close <span aria-hidden="true">×</span></button></div>
      <nav aria-label="Main navigation"><button onClick={returnToDome}>The dome <span>↗</span></button><button onClick={goToWork}>Work <span>↗</span></button><button onClick={() => scrollFromMenu('#skills')}>Skills <span>↗</span></button><button onClick={() => scrollFromMenu('#about')}>About <span>↗</span></button><button onClick={openContact}>Contact <span>↗</span></button></nav>
      <p className="dialog-footnote">Five instruments. Explore the work behind each one.</p>
    </dialog>
    <dialog ref={caseFile} className="control-dialog contact-dialog" aria-labelledby="case-preview-heading" onClose={() => setCaseOpen(false)} onCancel={() => setCaseOpen(false)}>
      <div className="dialog-top"><span>Case file preview</span><button onClick={() => caseFile.current?.close()}>Close <span aria-hidden="true">×</span></button></div>
      <h2 id="case-preview-heading">{selectedCase.name}</h2>
      <p>The full case file is coming soon.</p>
      <p className="dialog-footnote">{selectedCase.preview}</p>
      <button className="case-button" onClick={() => caseFile.current?.close()}>Return to the instrument <span aria-hidden="true">↙</span></button>
    </dialog>
  </div>;
}
