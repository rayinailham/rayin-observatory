'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type PointerEvent as ReactPointerEvent } from 'react';
import { instruments } from '@/lib/instruments';
import { skillGroups } from '@/lib/skills';
import { useReducedMotion } from './use-reduced-motion';

const pad = (value: number) => String(value).padStart(2, '0');
const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));
const projectName = (id: string) => instruments.find(item => item.id === id)?.name;

/** Deck geometry lives in CSS so each breakpoint tunes its own fan; JS only reads it. */
type Metrics = { spread: number; drop: number; tilt: number; scale: number; step: number };
const fallback: Metrics = { spread: 40, drop: 12, tilt: 4, scale: .075, step: 130 };
const total = skillGroups.length;
const wrap = (value: number) => ((value % total) + total) % total;
/** Shortest signed distance on the ring, so the deck always shows cards on both sides. */
const ring = (value: number) => wrap(value + total / 2) - total / 2;
const reach = 3;
/** False while server-rendered, so the deck ships as a plain card stack until it can be driven. */
const subscribe = () => () => {};
const useHydrated = () => useSyncExternalStore(subscribe, () => true, () => false);

/** The toolkit as a draggable deck: the front card reads in full, its neighbours fan behind it. */
export default function SkillDeck() {
  const deck = useRef<HTMLDivElement>(null);
  const cards = useRef<(HTMLElement | null)[]>([]);
  const metrics = useRef<Metrics>(fallback);
  const pointer = useRef({ id: -1, x: 0, base: 0, moved: 0, position: 0, velocity: 0, time: 0, held: false });
  const current = useRef(0);
  const [active, setActive] = useState(0);
  const [entered, setEntered] = useState(false);
  const enhanced = useHydrated();
  const reducedMotion = useReducedMotion();

  const paint = useCallback((position: number, fan = 1) => {
    const { spread, drop, tilt, scale } = metrics.current;
    cards.current.forEach((card, index) => {
      if (!card) return;
      const depth = clamp(ring(index - position), -reach, reach);
      const distance = Math.abs(depth);
      card.style.transform = `translate3d(${depth * spread * fan}px, ${distance * drop * fan}px, 0) `
        + `rotate(${depth * tilt * fan}deg) scale(${1 - distance * scale * fan})`;
      // Two cards each side stay readable (75% and 50%); the third fades to nothing exactly at the
      // clamp, so the wrap-around never flashes a card across the deck.
      const fade = distance <= 2 ? 1 - distance * .25 : .5 * (reach - distance);
      card.style.opacity = String(clamp(fade, 0, 1) * (distance > .5 ? fan : 1));
      card.style.filter = distance < .05 ? 'none' : `blur(${(distance * .5).toFixed(2)}px)`;
      card.style.zIndex = String(60 - Math.round(distance * 10));
      card.style.pointerEvents = distance < 1.6 ? 'auto' : 'none';
    });
  }, []);

  const measure = useCallback(() => {
    if (!deck.current) return;
    const style = getComputedStyle(deck.current);
    const read = (name: keyof Metrics, property: string) => {
      const value = parseFloat(style.getPropertyValue(property));
      return Number.isFinite(value) ? value : fallback[name];
    };
    metrics.current = { spread: read('spread', '--deck-spread'), drop: read('drop', '--deck-drop'),
      tilt: read('tilt', '--deck-tilt'), scale: read('scale', '--deck-scale'), step: read('step', '--deck-step') };
  }, []);

  useEffect(() => {
    measure();
    // Stacked and square until the section is reached: the fan-out is the arrival.
    paint(0, 0);
    const resize = () => { measure(); paint(current.current); };
    window.addEventListener('resize', resize);
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { setEntered(true); observer.disconnect(); }
    }, { threshold: .2 });
    observer.observe(deck.current!);
    return () => { window.removeEventListener('resize', resize); observer.disconnect(); };
  }, [measure, paint]);

  useEffect(() => {
    current.current = active;
    if (entered) paint(active);
  }, [active, entered, paint]);

  useEffect(() => {
    if (!entered || reducedMotion) return;
    // The staggered delay belongs to the fan-out only; leaving it on would lag every later move.
    const element = deck.current;
    element?.classList.add('deck-enter');
    const timer = window.setTimeout(() => element?.classList.remove('deck-enter'), 1100);
    return () => window.clearTimeout(timer);
  }, [entered, reducedMotion]);

  const move = (direction: number) => setActive(value => wrap(value + direction));

  const down = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    pointer.current = { id: event.pointerId, x: event.clientX, base: active, moved: 0, position: active, velocity: 0, time: event.timeStamp, held: false };
  };

  const drag = (event: ReactPointerEvent<HTMLDivElement>) => {
    const state = pointer.current;
    if (state.id !== event.pointerId) return;
    const shift = event.clientX - state.x;
    state.moved = Math.max(state.moved, Math.abs(shift));
    if (state.moved < 5) return;
    if (!state.held) {
      // Captured only once a drag is real: capturing on pointerdown would retarget the click
      // away from a project link and swallow it.
      state.held = true;
      try { event.currentTarget.setPointerCapture(event.pointerId); } catch { /* the drag still tracks without capture */ }
    }
    deck.current?.setAttribute('data-dragging', 'true');
    const position = state.base - shift / metrics.current.step;
    state.velocity = (position - state.position) / Math.max(1, event.timeStamp - state.time);
    state.position = position;
    state.time = event.timeStamp;
    paint(position);
  };

  const release = (event: ReactPointerEvent<HTMLDivElement>) => {
    const state = pointer.current;
    if (state.id !== event.pointerId) return;
    state.id = -1;
    deck.current?.removeAttribute('data-dragging');
    if (state.moved < 5) {
      const card = (event.target as HTMLElement).closest<HTMLElement>('.skill-card');
      if (card && Number(card.dataset.index) !== active) setActive(Number(card.dataset.index));
      return;
    }
    // A flick carries one card further than the distance dragged.
    const flick = Math.abs(state.velocity) > .002 ? Math.sign(state.velocity) : 0;
    const target = wrap(Math.round(state.position) + flick);
    setActive(target);
    paint(target);
  };

  return <div ref={deck} className="skill-deck" data-enhanced={enhanced} data-entered={entered}
    role="group" aria-roledescription="carousel" aria-label="Skill groups"
    onKeyDown={event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      move(event.key === 'ArrowLeft' ? -1 : 1);
    }}>
    <div className="deck-stage" onPointerDown={down} onPointerMove={drag} onPointerUp={release} onPointerCancel={release}
      onClickCapture={event => {
        // A drag that ends over a project link must not follow it.
        if (pointer.current.moved < 5) return;
        pointer.current.moved = 0;
        event.preventDefault();
        event.stopPropagation();
      }}>
      {skillGroups.map((group, index) => <article key={group.name} ref={element => { cards.current[index] = element; }}
        className="skill-card" data-index={index} data-active={index === active} data-dense={group.items.length > 3}
        style={{ '--i': index } as CSSProperties}
        aria-roledescription="slide" aria-label={`${group.name}, ${index + 1} of ${total}`}>
        <p className="card-index">{pad(index + 1)}<span> / {pad(total)}</span></p>
        <h3>{group.name}</h3>
        <p className="card-blurb">{group.blurb}</p>
        <p className="card-label">Tools</p>
        <ul>{group.items.map(skill => <li key={skill.name}>
          <h4>{skill.name}</h4>
          <p className="skill-note">{skill.note}</p>
          {skill.projects.length > 0 && <div className="skill-projects">{skill.projects.map(id => <a key={id} href={`#${id}`}
            data-skill-project={id} tabIndex={enhanced && index !== active ? -1 : undefined}
            aria-label={`${skill.name}: explore ${projectName(id)}`}>{projectName(id)}<span aria-hidden="true">↗</span></a>)}</div>}
        </li>)}</ul>
        <p className="card-swaps"><span>Same job, other tools</span>{group.swaps.map(tool => <b key={tool}>{tool}</b>)}</p>
      </article>)}
    </div>
    <div className="deck-controls">
      <button className="deck-arrow" onClick={() => move(-1)} aria-label="Previous skill group"><span aria-hidden="true">←</span></button>
      <div className="deck-dots">{skillGroups.map((group, index) => <button key={group.name} className="deck-dot"
        data-active={index === active} onClick={() => setActive(index)} aria-label={group.name}
        aria-current={index === active ? 'true' : undefined}><i /></button>)}</div>
      <button className="deck-arrow" onClick={() => move(1)} aria-label="Next skill group"><span aria-hidden="true">→</span></button>
    </div>
    <p className="deck-readout" aria-live="polite">{pad(active + 1)} / {pad(total)} · {skillGroups[active].name}</p>
  </div>;
}
