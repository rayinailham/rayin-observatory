'use client';

import { useCallback, useEffect, useLayoutEffect, useRef, useState, type MutableRefObject, type ReactNode } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { apertureScreen, caseFiles, caseIndex, type CaseView } from '@/lib/cases';
import { useProgress } from '@react-three/drei';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ObservatoryAudio } from '@/lib/ambient';
import { instruments, type ChapterState } from '@/lib/instruments';

// Static import: the 3D chunk downloads with the first JS instead of after hydration (Enter waits
// for it). The module is SSR-safe; Canvas only renders its container on the server.
import Scene from './observatory-scene';
import { useReducedMotion } from './use-reduced-motion';
const SOUND_KEY = 'rayin-observatory:sound';
const caseOf = (path: string) => caseIndex(path.startsWith('/work/') ? path.slice('/work/'.length) : null);

// Lens iris (Phase 7A): ink between a lens and the screen edge. A `disc` grows out of the lens and
// covers the screen; a `hole` opens in the ink and uncovers it. The centre follows the scene's
// apertureScreen (kept on screen), or stays where the last cover closed so a case opens from the
// lens it was entered through, even when that lens now sits below the fold.
type IrisState = 'hidden' | 'disc' | 'hole';
type IrisCentre = { x: number; y: number };
const irisReach = () => Math.hypot(window.innerWidth, window.innerHeight);
let irisCentre: IrisCentre = { x: 0, y: 0 };
function lensCentre(): IrisCentre {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const x = Number.isFinite(apertureScreen.x) ? apertureScreen.x : w / 2;
  const y = Number.isFinite(apertureScreen.y) ? apertureScreen.y : h * .45;
  return { x: Math.min(w * .9, Math.max(w * .1, x)), y: Math.min(h * .86, Math.max(h * .14, y)) };
}
function setIris(element: HTMLElement | null, state: IrisState, r = 0, centre = irisCentre) {
  if (!element) return;
  element.dataset.state = state;
  element.style.setProperty('--iris-x', `${centre.x.toFixed(1)}px`);
  element.style.setProperty('--iris-y', `${centre.y.toFixed(1)}px`);
  element.style.setProperty('--iris-r', `${r.toFixed(1)}px`);
  element.style.setProperty('--iris-ring', Math.max(0, 1 - r / irisReach()).toFixed(3));
}
function irisTween(element: HTMLElement | null, motion: MutableRefObject<gsap.core.Tween | null>, state: 'disc' | 'hole', from: number, to: number, duration: number, ease: string, delay = 0, follow = true) {
  motion.current?.kill();
  const proxy = { r: from };
  const place = () => { if (follow) irisCentre = lensCentre(); setIris(element, state, proxy.r); };
  place();
  const tween = gsap.to(proxy, { r: to, duration, ease, delay,
    onUpdate: place,
    onComplete: () => {
      if (state === 'disc' ? to <= 0 : to >= irisReach() * .98) setIris(element, 'hidden');
      if (motion.current === tween) motion.current = null;
    },
  });
  motion.current = tween;
  return tween;
}

export default function ObservatoryShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const reducedMotion = useReducedMotion();
  const router = useRouter();
  const current = caseOf(pathname);
  const isCase = current >= 0;
  const caseView = useRef<CaseView>({ mix: 0, active: false, index: 0 });
  const homeScroll = useRef<number | null>(null);
  const homeChapter = useRef<ChapterState | null>(null);
  const homeTarget = useRef<number | string | null>(null);
  const previousPath = useRef(pathname);
  const flight = useRef<gsap.core.Timeline | null>(null);
  const [flying, setFlying] = useState(false);
  const pageContent = useRef<HTMLDivElement>(null);
  const iris = useRef<HTMLDivElement>(null);
  const pulse = useRef<HTMLDivElement>(null);
  const ribbon = useRef<HTMLDivElement>(null);
  // Where the antenna sat on screen when its case was opened; Return restores that scroll, so the pulse lands there.
  const pulseHome = useRef<IrisCentre & { w: number; h: number } | null>(null);
  const sceneLayer = useRef<HTMLDivElement>(null);
  const progressBar = useRef<HTMLDivElement>(null);
  const irisMotion = useRef<gsap.core.Tween | null>(null);
  const [entered, setEntered] = useState(false);
  const [sceneReady, setSceneReady] = useState(false);
  const [fontsReady, setFontsReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [sound, setSound] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [loadSlow, setLoadSlow] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const gate = useRef<HTMLDivElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const menu = useRef<HTMLDialogElement>(null);
  const readout = useRef<HTMLOutputElement>(null);
  const progress = useRef(0);
  const planetProgress = useRef(0);
  const chapter = useRef<ChapterState>({ reveal: 0, orbit: 0, index: 0, transition: 0, outro: 0 });
  const lenis = useRef<Lenis | null>(null);
  const audio = useRef<ObservatoryAudio | null>(null);
  const [modelProgress, setModelProgress] = useState(0);
  const ready = fontsReady && (sceneReady || failed);
  const loaded = ready ? 100 : Math.min(99, Math.round(modelProgress * .7 + (fontsReady ? 30 : 0)));
  const onReady = useCallback(() => setSceneReady(true), []);
  const onFailure = useCallback(() => setFailed(true), []);
  const onInstrumentTap = useCallback((index: number) => audio.current?.click(index), []);

  useEffect(() => {
    // drei starts a new progress batch when another GLB is discovered. Never rewind the dial.
    const update = ({ progress }: { progress: number }) => setModelProgress(previous => Math.max(previous, progress));
    const unsubscribe = useProgress.subscribe(update);
    update(useProgress.getState());
    return unsubscribe;
  }, []);

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
    const scroller = new Lenis({ autoRaf: false, smoothWheel: !reducedMotion, syncTouch: false, lerp: .085 });
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
  }, [reducedMotion]);

  useLayoutEffect(() => {
    // History can interrupt a departure. Its old onComplete must never push a stale route.
    flight.current?.kill();
    flight.current = null;
    const from = caseOf(previousPath.current);
    const cameFromCase = from >= 0 && !isCase;
    previousPath.current = pathname;
    const scroller = lenis.current;
    let frame = 0;
    let focusAfterFlight: HTMLElement | null = null;
    const context = gsap.context(() => {}, root);
    caseView.current.active = isCase;
    if (isCase) {
      // Also the landing of a case-to-case chain: its camera sweep ends with this fly-in.
      caseView.current.index = current;
      chapter.current = { reveal: 1, orbit: 0, index: current, transition: 1, outro: 0 };
      root.current?.setAttribute('data-chapter', caseFiles[current].id);
      sceneLayer.current?.style.setProperty('--chapter-reveal', '1');
      scroller?.scrollTo(0, { immediate: true, force: true });
      window.scrollTo(0, 0);
      context.add(() => gsap.to(caseView.current, { mix: 1, duration: reducedMotion ? 0 : .78, ease: 'power2.inOut' }));
    }
    if (cameFromCase) {
      const id = caseFiles[from].id;
      const destination = homeTarget.current ?? homeScroll.current ?? `#${id}`;
      const element = typeof destination === 'string' ? document.querySelector<HTMLElement>(destination) : null;
      const y = typeof destination === 'number' ? destination : element ? element.getBoundingClientRect().top + window.scrollY : 0;
      scroller?.resize();
      scroller?.scrollTo(y, { immediate: true, force: true });
      window.scrollTo(0, y);
      context.add(() => gsap.to(caseView.current, { mix: 0, duration: reducedMotion ? 0 : .78, ease: 'power2.inOut' }));
      frame = requestAnimationFrame(() => {
        ScrollTrigger.refresh();
        focusAfterFlight = element?.querySelector<HTMLElement>('h2') ?? document.querySelector<HTMLElement>(`[data-open-case="${id}"]`);
      });
      homeTarget.current = null;
    }
    // A lens flight leaves the iris covering the screen; the arriving page always uncovers it,
    // including after Back interrupted a departure half way.
    const irisState = iris.current?.dataset.state;
    if (ribbon.current) { gsap.killTweensOf(ribbon.current); gsap.set(ribbon.current, { opacity: 0 }); ribbon.current.dataset.direction = 'idle'; }
    if (pulse.current) gsap.set(pulse.current.querySelectorAll('i'), { opacity: 0 });
    if (irisState === 'disc' || irisState === 'hole') {
      const r = parseFloat(iris.current!.style.getPropertyValue('--iris-r')) || 0;
      const reach = irisReach();
      if (reducedMotion) setIris(iris.current, 'hidden');
      else if (irisState === 'disc') {
        if (isCase && r >= reach * .98) irisTween(iris.current, irisMotion, 'hole', 0, reach, .75, 'power2.out', .12, false); // the inspection field opens from the lens
        else irisTween(iris.current, irisMotion, 'disc', r, 0, cameFromCase ? .72 : .3, 'power2.inOut', cameFromCase ? .08 : 0);
      } else if (!isCase && r <= 1) irisTween(iris.current, irisMotion, 'disc', reach, 0, .72, 'power2.inOut', .08); // the view settles back into the chapter lens
      else irisTween(iris.current, irisMotion, 'hole', r, reach, .3, 'power2.out');
    }
    context.add(() => gsap.fromTo(pageContent.current, { opacity: 0 }, { opacity: 1, duration: reducedMotion ? 0 : .55, delay: reducedMotion ? 0 : .25, ease: 'power2.out',
      onComplete: () => {
        setFlying(false);
        frame = requestAnimationFrame(() => {
          // React must release inert before focus can move into the arriving page.
          (isCase ? document.getElementById('case-heading') : focusAfterFlight)?.focus({ preventScroll: true });
        });
      },
    }));
    return () => { flight.current?.kill(); flight.current = null; context.revert(); cancelAnimationFrame(frame); };
  }, [pathname, isCase, current, reducedMotion]);

  useEffect(() => {
    // Scroll ownership stays in the root. Route-specific triggers are rebuilt per page.
    const sections = instruments.map(item => document.getElementById(item.id));
    if (isCase || sections.some(section => !section)) {
      const trigger = ScrollTrigger.create({ trigger: 'main', start: 'top top', end: 'bottom bottom',
        onUpdate: self => {
          if (readout.current) readout.current.textContent = `${Math.round(self.progress * 100).toString().padStart(3, '0')}%`;
          progressBar.current?.style.setProperty('--journey', String(self.progress));
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
    let journeyEnd = 1;
    // A route change can refresh or scroll before React cleans up this trigger; the homepage
    // DOM is already gone then, so its stale sections must not measure or rewrite chapter state.
    const live = () => homeSections[0].isConnected;
    const measure = () => {
      positions = homeSections.map(section => ({ top: section.getBoundingClientRect().top + window.scrollY, height: section.offsetHeight }));
      skillsTop = document.getElementById('skills')!.getBoundingClientRect().top + window.scrollY;
      journeyEnd = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    };
    const clamp = (n: number) => Math.max(0, Math.min(1, n));
    const syncChapters = () => {
      const y = window.scrollY;
      planetProgress.current = clamp(y / journeyEnd);
      const height = homeSections[0].querySelector<HTMLElement>('.instrument-stage')!.offsetHeight;
      let index = 0;
      positions.forEach((pos, i) => { if (y >= pos.top - height) index = i; });
      const pos = positions[index];
      const reveal = clamp((y - positions[0].top + height) / height);
      const transition = clamp((y - pos.top + height) / height);
      const outro = clamp((y - skillsTop + height) / height);
      chapter.current = { index, reveal, transition, outro, orbit: clamp((y - pos.top) / Math.max(1, pos.height - height)) };
      // Scroll-driven custom properties live on the element that uses them, never on the root: a root custom
      // property restyles the whole page on every scroll frame (7B: SurgeLine chapter under the 45 fps gate at 4x CPU).
      sceneLayer.current?.style.setProperty('--chapter-reveal', String(reveal));
      root.current?.setAttribute('data-chapter', outro >= 1 ? 'outro' : reveal > .4 ? instruments[index].id : 'dome');
      homeSections.forEach((_, i) => {
        const offset = i === index ? 1 - transition : i === index - 1 ? -transition : 2;
        sceneLayer.current?.style.setProperty(`--instrument-${i}-offset`, String(offset - (i === index ? outro : 0)));
        // Chapter-local scan progress (CrossCheck's lane strip): full once passed, empty before reached.
        homeSections[i].style.setProperty(`--instrument-${i}-orbit`, (i < index ? 1 : i > index ? 0 : chapter.current.orbit).toFixed(3));
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
        progressBar.current?.style.setProperty('--journey', String(self.progress));
      },
    });
    const hero = document.getElementById('first-light');
    const heroTrigger = ScrollTrigger.create({
      trigger: '#first-light', start: 'top top', end: 'bottom bottom',
      onUpdate: self => {
        progress.current = self.progress;
        hero?.style.setProperty('--hero-journey', String(self.progress));
        hero?.style.setProperty('--copy-opacity', String(Math.max(0, 1 - self.progress * 2.8)));
      },
    });
    const scan = gsap.fromTo('.portrait-scan img', { clipPath: reducedMotion ? 'inset(0)' : 'inset(0 0 100% 0)' }, {
      clipPath: 'inset(0 0 0% 0)', ease: 'none',
      scrollTrigger: { trigger: '.portrait-scan', start: 'top 82%', end: 'center 50%', scrub: true },
    });
    const scanLine = gsap.fromTo('.scan-line', { top: '0%' }, { top: reducedMotion ? '0%' : '100%', ease: 'none',
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
  }, [pathname, isCase, reducedMotion]);

  useEffect(() => {
    if (entered && !menuOpen && !flying) lenis.current?.start();
    else lenis.current?.stop();
  }, [entered, menuOpen, flying, reducedMotion]);

  // Pointer parallax on the gate. The eased value is written as a CSS variable, so every gate
  // layer reads the same pointer with its own depth multiplier instead of its own listener.
  useEffect(() => {
    const element = gate.current;
    if (entered || reducedMotion || !element) return;
    if (!window.matchMedia('(min-width: 1024px) and (hover: hover) and (pointer: fine)').matches) return;
    const target = { x: 0, y: 0 };
    const eased = { x: 0, y: 0 };
    const move = (event: PointerEvent) => {
      target.x = (event.clientX / window.innerWidth - .5) * 2;
      target.y = (event.clientY / window.innerHeight - .5) * 2;
    };
    const tick = () => {
      eased.x += (target.x - eased.x) * .055;
      eased.y += (target.y - eased.y) * .055;
      element.style.setProperty('--gate-px', eased.x.toFixed(4));
      element.style.setProperty('--gate-py', eased.y.toFixed(4));
    };
    window.addEventListener('pointermove', move, { passive: true });
    gsap.ticker.add(tick);
    // The last offset stays on the element: clearing it here would snap the layers back to centre
    // exactly as the exit timeline starts.
    return () => {
      window.removeEventListener('pointermove', move);
      gsap.ticker.remove(tick);
    };
  }, [entered, reducedMotion]);

  useEffect(() => {
    if (!entered) return;
    // Measure while the gate still covers everything: a refresh during the hand-off can shift
    // the hero mid-fade, which is exactly what makes the entry feel like a cut.
    ScrollTrigger.refresh();
    const wide = window.matchMedia('(min-width: 1024px)').matches;
    const context = gsap.context(() => {
      const hide = () => { if (gate.current) gate.current.hidden = true; };
      const exit = gsap.timeline({ onComplete: hide });
      // Wide screens leave in layers: controls lift away first, the field opens past the camera.
      // The scene's own arrival damp runs underneath, so something is always moving.
      if (reducedMotion) exit.to(gate.current, { opacity: 0, duration: 0 });
      else if (wide) exit
        .to('.gate-main > *', { y: -34, opacity: 0, duration: .5, ease: 'power2.in', stagger: { each: .045, from: 'end' } }, 0)
        .to('.gate-byline, .gate-note', { opacity: 0, duration: .4, ease: 'power2.in' }, 0)
        .to('.gate-rings i', { scale: 1.5, opacity: 0, duration: 1.15, ease: 'power2.inOut' }, 0)
        .to('.gate-stars i', { scale: 1.3, opacity: 0, duration: 1.15, ease: 'power2.inOut' }, 0)
        .to(gate.current, { opacity: 0, duration: .8, ease: 'sine.inOut' }, .16);
      else exit.to(gate.current, { opacity: 0, yPercent: -4, duration: .7, ease: 'power2.inOut' });
      // The hero lands as the gate clears, on the same curve as the camera settling behind it.
      if (document.querySelector('.hero-copy')) gsap.fromTo('.hero-copy', { y: reducedMotion ? 0 : wide ? 34 : 24, opacity: 0 },
        { y: 0, opacity: 1, duration: reducedMotion ? 0 : wide ? 1.15 : 1.1, delay: reducedMotion ? 0 : wide ? .5 : .3, ease: 'power3.out' });
    }, root);
    const timer = window.setTimeout(() => {
      (document.getElementById('case-heading') ?? document.getElementById('hero-heading'))?.focus({ preventScroll: true });
    }, reducedMotion ? 0 : 750);
    return () => { context.revert(); window.clearTimeout(timer); };
  }, [entered, reducedMotion]);

  useLayoutEffect(() => {
    if (!entered || isCase || reducedMotion) return;
    const media = gsap.matchMedia();
    media.add('(min-width: 1024px)', () => {
      gsap.to('.hero-copy', { y: -90, ease: 'none', scrollTrigger: {
        trigger: '#first-light', start: 'top top', end: 'bottom bottom', scrub: .8,
      } });
      gsap.utils.toArray<HTMLElement>('.text-section').forEach(section => {
        gsap.fromTo(section.querySelectorAll(':scope > h2, :scope > .section-intro'),
          { y: 32, opacity: .25 }, { y: 0, opacity: 1, ease: 'none', scrollTrigger: {
            trigger: section, start: 'top 85%', end: 'top 45%', scrub: .65,
          } });
      });
    }, root);
    return () => media.revert();
  }, [entered, isCase, pathname, reducedMotion]);

  async function setAudio(enabled: boolean, welcome = false) {
    try {
      const playing = await audio.current?.setEnabled(enabled) ?? false;
      setSound(playing);
      setAudioError(enabled && !playing);
      if (playing && welcome) audio.current?.transition('in');
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
    void setAudio(!silent && remembered, true);
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
    lenis.current?.scrollTo(destination, { force: true, immediate: reducedMotion, onComplete: () => {
      if (typeof target === 'string') document.querySelector<HTMLElement>(`${target} h2`)?.focus({ preventScroll: true });
    } });
  }
  function openCase(index: number) {
    if (flying || flight.current) return;
    const path = `/work/${caseFiles[index].id}`;
    homeScroll.current = window.scrollY;
    homeChapter.current = { ...chapter.current };
    pulseHome.current = { ...lensCentre(), w: window.innerWidth, h: window.innerHeight };
    caseView.current.index = index;
    setFlying(true);
    lenis.current?.stop();
    router.prefetch(path);
    audio.current?.transition('in');
    flight.current = gsap.timeline({ onComplete: () => router.push(path, { scroll: false }) })
      .to(pageContent.current, { opacity: 0, duration: reducedMotion ? 0 : .48, ease: 'power2.out' }, 0)
      .to(caseView.current, { mix: 1, duration: reducedMotion ? 0 : .78, ease: 'power2.inOut' }, 0);
    // Phase 7A: CrossCheck is entered through its lens; the arriving case opens the iris again.
    if (caseFiles[index].transition === 'ribbon') flight.current.add(ribbonFlight('out'), .08);
    else if (caseFiles[index].transition === 'pulse') flight.current.add(pulseFlight('out'), .08);
    else if (caseFiles[index].aperture && !reducedMotion) flight.current.add(irisTween(iris.current, irisMotion, 'disc', 0, irisReach(), .5, 'power2.in'), .32);
  }

  function ribbonFlight(direction: 'in' | 'out', centre = lensCentre()) {
    const sheet = ribbon.current;
    const timeline = gsap.timeline();
    if (!sheet || reducedMotion) return timeline;
    // One local layer; transform/opacity only. Full-width paper unrolls from the needle.
    const collapsed = { x: centre.x, y: centre.y, scaleX: .012, scaleY: .12 };
    const expanded = { x: 0, y: window.innerHeight * .46, scaleX: 1, scaleY: 1 };
    timeline.set(sheet, { opacity: .95, transformOrigin: '0 50%', ...(direction === 'out' ? collapsed : expanded) })
      .call(() => { sheet.dataset.direction = direction; })
      .to(sheet, { ...(direction === 'out' ? expanded : collapsed), duration: .7, ease: 'power2.inOut' })
      .to(sheet, { opacity: 0, duration: .14 })
      .call(() => { sheet.dataset.direction = 'idle'; });
    return timeline;
  }

  function pulseFlight(direction: 'in' | 'out', centre = lensCentre()) {
    const rings = pulse.current?.querySelectorAll('i');
    const timeline = gsap.timeline();
    if (!rings || reducedMotion) return timeline;
    gsap.set(pulse.current, { x: centre.x, y: centre.y });
    const far = Math.hypot(window.innerWidth, window.innerHeight) / 80;
    // Transform/opacity only; position sampled once, no root CSS writes on every frame.
    timeline.fromTo(rings, { scale: direction === 'out' ? .6 : far, opacity: direction === 'out' ? .85 : 0 },
      { scale: direction === 'out' ? far : .6, opacity: direction === 'out' ? 0 : .85, duration: .62, stagger: .07, ease: 'power2.inOut' });
    timeline.to(rings, { opacity: 0, duration: .12 });
    return timeline;
  }

  // Next instrument: the camera backs away from this instrument, sweeps to the next one as the
  // homepage chapter change does, then the arriving route flies in. Return then goes to that chapter.
  function chainCase(index: number) {
    if (flying || flight.current || !isCase) return;
    const path = `/work/${caseFiles[index].id}`;
    const from = caseView.current.index;
    homeScroll.current = null;
    homeChapter.current = null;
    setFlying(true);
    lenis.current?.stop();
    router.prefetch(path);
    audio.current?.transition('out');
    const sweep = { reveal: 1, orbit: 0, outro: 0, index, from, transition: 0 };
    flight.current = gsap.timeline({ onComplete: () => router.push(path, { scroll: false }) })
      .to(pageContent.current, { opacity: 0, duration: reducedMotion ? 0 : .4, ease: 'power2.out' }, 0)
      .to(caseView.current, { mix: 0, duration: reducedMotion ? 0 : .65, ease: 'power2.inOut' }, 0)
      .call(() => {
        caseView.current.index = index;
        chapter.current = sweep;
        root.current?.setAttribute('data-chapter', caseFiles[index].id);
        audio.current?.transition('in');
      })
      .to(sweep, { transition: 1, duration: reducedMotion ? 0 : .78, ease: 'power2.inOut' });
    if (caseFiles[from].transition === 'ribbon') flight.current.add(ribbonFlight('in'), 0);
    else if (caseFiles[from].transition === 'pulse') flight.current.add(pulseFlight('in'), 0);
    if (caseFiles[index].transition === 'ribbon') flight.current.add(ribbonFlight('out'), .78);
    else if (caseFiles[index].transition === 'pulse' && caseFiles[from].transition !== 'pulse') flight.current.add(pulseFlight('out'), .68);
  }

  function leaveCase(target: number | string = 'return') {
    if (flying || flight.current) return;
    menu.current?.close();
    setMenuOpen(false);
    homeTarget.current = target === 'return' ? homeScroll.current ?? `#${caseFiles[current].id}` : target;
    if (homeChapter.current) chapter.current = { ...homeChapter.current };
    setFlying(true);
    lenis.current?.stop();
    audio.current?.transition('out');
    flight.current = gsap.timeline({ onComplete: () => router.push('/', { scroll: false }) })
      .to(pageContent.current, { opacity: 0, duration: reducedMotion ? 0 : .28, ease: 'power2.out' }, 0);
    // Returning to the chapter closes the inspection field back into the lens first.
    // On the case page the antenna has usually scrolled away; aim at the chapter antenna the visitor left from.
    const home = pulseHome.current;
    const sameView = home && home.w === window.innerWidth && home.h === window.innerHeight && homeScroll.current !== null;
    if (target === 'return' && caseFiles[current].transition === 'ribbon') flight.current.add(ribbonFlight('in', sameView ? home : lensCentre()), 0);
    else if (target === 'return' && caseFiles[current].transition === 'pulse') flight.current.add(pulseFlight('in', sameView ? home : lensCentre()), 0);
    else if (target === 'return' && caseFiles[current].aperture && !reducedMotion) flight.current.add(irisTween(iris.current, irisMotion, 'hole', irisReach(), 0, .48, 'power2.in'), 0);
  }

  function returnToDome() { scrollFromMenu(0); }
  function goToWork() { scrollFromMenu('#crosscheck'); }

  return <div ref={root} className={`observatory ${entered ? 'has-entered' : ''}`} data-motion={reducedMotion ? 'reduced' : 'full'} data-route={isCase ? 'case' : 'home'} data-flight={flying ? 'moving' : 'idle'} data-scene={failed ? 'fallback' : sceneReady ? 'ready' : 'loading'}>
    <div ref={sceneLayer} className="scene-layer" aria-hidden="true">
      {!failed && <Scene reducedMotion={reducedMotion} entered={entered} progress={progress} planetProgress={planetProgress} chapter={chapter} caseView={caseView} loadInstruments={ready} onReady={onReady} onFailure={onFailure} onInstrumentTap={onInstrumentTap} />}
      {failed && !isCase && <><div className="scene-fallback" />{instruments.map((item, i) => <div key={item.id} className={`instrument-fallback ${item.id}-fallback`} style={{ backgroundImage: `url('/images/${item.id}-fallback.png')`, transform: `translateY(calc(var(--instrument-${i}-offset, 2) * 100svh))` }} />)}</>}
    </div>
    <div ref={content} inert={!entered} className="site-content" onClickCapture={event => {
      if (!entered || flying) return;
      const target = event.target as HTMLElement;
      if (target.closest('[data-hotspot], .component-card button')) audio.current?.click(current);
      else if (target.closest('summary, .menu-toggle, .dialog-top button')) audio.current?.click();
    }}>
      <header className="site-header">
        <button className="wordmark" onClick={returnToDome} aria-label="Rayin Observatory, return to the dome">Rayin<span>Observatory</span></button>
        <div className="header-controls">
          <nav className="desktop-navigation" aria-label="Desktop navigation" inert={flying}>
            <button onClick={goToWork}>Work</button>
            <button onClick={() => scrollFromMenu('#about')}>About</button>
            <button onClick={openContact}>Contact</button>
          </nav>
          <button className="sound-toggle" aria-label={sound ? 'Turn sound off' : 'Turn sound on'} aria-pressed={sound}
            onClick={() => void setAudio(!sound)}><span className="sound-bars" aria-hidden="true"><i /><i /><i /><i /></span><span>{sound ? 'On' : 'Off'}</span></button>
          <button className="menu-toggle" onClick={openMenu} aria-expanded={menuOpen} aria-controls="navigation">Menu<span aria-hidden="true">+</span></button>
        </div>
      </header>
      <div ref={pageContent} className="page-content" inert={flying} onClick={event => {
        const target = event.target as HTMLElement;
        const modified = event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
        const homeLink = target.closest<HTMLAnchorElement>('[data-home-target]');
        if (homeLink && !modified) { event.preventDefault(); leaveCase(homeLink.dataset.homeTarget); return; }
        const caseLink = target.closest<HTMLAnchorElement>('[data-case-target]');
        if (caseLink && !modified) { event.preventDefault(); chainCase(caseIndex(caseLink.dataset.caseTarget)); return; }
        const caseButton = target.closest<HTMLElement>('[data-open-case]');
        if (caseButton) { event.preventDefault(); openCase(caseIndex(caseButton.dataset.openCase)); return; }
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
      <div ref={iris} className="lens-iris" data-state="hidden" aria-hidden="true" />
      <div ref={ribbon} className="monitor-ribbon" data-direction="idle" aria-hidden="true"><svg viewBox="0 0 600 80" preserveAspectRatio="none"><path d="M0 40H250L264 35L278 46L296 40H600" /></svg><span>SNAPSHOT / COMPARE / RECORD</span></div>
      <div ref={pulse} className="dispatch-pulse" aria-hidden="true"><i /><i /><i /></div>
      <button className="hero-contact" onClick={openContact}>Contact <span aria-hidden="true">↗</span></button>
      <div ref={progressBar} className="progress-readout"><span>SCROLL</span><span className="readout-track" aria-hidden="true"><i /></span><output ref={readout} aria-label="Scroll progress">000%</output></div>
      {audioError && <p className="audio-notice" role="status">Sound could not start. Tap the sound control to retry.</p>}
      {failed && <p className="fallback-notice" role="status">Still view. Live 3D is unavailable on this device.</p>}
    </div>

    <div ref={gate} className="entry-gate" data-ready={ready} data-fallback={failed} inert={entered} aria-label="Enter Rayin Observatory">
      {/* Each layer is a wrapper that owns its parallax translate plus an inner <i> for GSAP to
          scale: GSAP folds transforms and drops a calc() `translate`, which would decentre it. */}
      <div className="gate-field" aria-hidden="true"><span className="gate-stars"><i /></span><span className="gate-rings"><i /></span><span className="gate-horizon" /></div>
      <p className="gate-byline">A portfolio by Rayina Ilham</p>
      <div className="gate-main">
        <div className="calibration-orbit" aria-hidden="true"><span /><i /><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" pathLength="100" strokeDasharray="100" strokeDashoffset={100 - loaded} /></svg></div>
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
  </div>;
}
