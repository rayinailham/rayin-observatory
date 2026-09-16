// Presentation timing, not a scale model of the solar system. Scroll selects the
// planet; elapsed time alone drives the idle orbit, so stopping never rewinds it.
export const planets = [
  { name: 'Mercury', color: '#aaa399', kind: 2, size: .65, tilt: .01, spin: .06 },
  { name: 'Venus', color: '#d9b779', kind: 1, size: .85, tilt: .05, spin: -.035 },
  { name: 'Earth', color: '#6aa9d6', kind: 0, size: .9, tilt: .41, spin: .12 },
  { name: 'Mars', color: '#c57551', kind: 2, size: .75, tilt: .44, spin: .11 },
  { name: 'Jupiter', color: '#d6ae80', kind: 1, size: 1.2, tilt: .05, spin: .18 },
  { name: 'Saturn', color: '#d6be8c', kind: 1, size: .85, tilt: -.38, spin: 0 },
  { name: 'Uranus', color: '#9ad6dc', kind: 3, size: .95, tilt: 1.71, spin: .09 },
  { name: 'Neptune', color: '#4f7ed6', kind: 3, size: .95, tilt: .49, spin: .10 },
] as const;

const clamp = (value: number) => Math.max(0, Math.min(1, value));
const ease = (value: number) => { const t = clamp(value); return t * t * t * (t * (t * 6 - 15) + 10); };

export function samplePlanetJourney(progress: number, time: number, desktop: boolean, reducedMotion = false) {
  const position = clamp(progress) * (planets.length - 1);
  const index = Math.min(planets.length - 1, Math.floor(position + .5));
  const local = position - index;
  // Hold in the margin, then exit upper-right. The next planet enters lower-right.
  // Both sides of a handoff are invisible: no crossfade with two planets on screen.
  const transit = Math.sign(local) * ease((Math.abs(local) - .23) / .27);
  const opacity = 1 - ease((Math.abs(local) - .34) / .14);
  const phase = time * Math.PI * 2 / (28 + index * 4);
  return {
    index, opacity,
    x: (desktop ? .32 : .37) + (reducedMotion ? 0 : .10 * Math.abs(transit) + Math.cos(phase) * .022),
    // Mobile hero copy fills the top; chapters leave a margin beside the heading.
    y: (desktop ? .31 : .035 + .275 * ease(progress / .1)) + (reducedMotion ? 0 : .075 * transit + Math.sin(phase) * .017),
  };
}
