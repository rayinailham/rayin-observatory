import assert from 'node:assert/strict';
import { planets, samplePlanetJourney as sample } from '../lib/planetary-motion.ts';

assert.deepEqual(planets.map(p => p.name), ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']);
const observed = [];
for (let step = 0; step <= 10000; step++) {
  const p = step / 10000;
  const pose = sample(p, 0, true);
  if (observed.at(-1) !== pose.index) observed.push(pose.index);
  assert.ok(pose.opacity >= 0 && pose.opacity <= 1);
  // The same scroll location always selects the same planet, independent of time.
  assert.equal(sample(p, 1000, true).index, pose.index);
  if (step) assert.ok(pose.index >= sample(p - .0001, 0, true).index);
}
assert.deepEqual(observed, [0, 1, 2, 3, 4, 5, 6, 7]);
for (let i = 0; i < 7; i++) {
  const boundary = (i + .5) / 7;
  assert.equal(sample(boundary - 1e-7, 0, true).opacity, 0);
  assert.equal(sample(boundary + 1e-7, 0, true).opacity, 0);
}
for (const desktop of [true, false]) {
  for (let i = 0; i < 8; i++) {
    const p = i / 7, period = 28 + i * 4;
    const start = sample(p, 0, desktop), end = sample(p, period, desktop);
    assert.equal(start.opacity, 1);
    assert.ok(Math.hypot(start.x - end.x, start.y - end.y) < 1e-10, 'orbit must close');
    const center = { x: desktop ? .32 : .37, y: start.y };
    let previous = start;
    for (let frame = 1; frame <= 240; frame++) {
      const next = sample(p, frame * period / 240, desktop);
      const cross = (previous.x - center.x) * (next.y - center.y) - (previous.y - center.y) * (next.x - center.x);
      assert.ok(cross > 0, 'one consistent counterclockwise orbit');
      assert.ok(Math.hypot(next.x - previous.x, next.y - previous.y) < .001, 'no loop seam');
      previous = next;
    }
    assert.deepEqual(sample(p, 0, desktop, true), sample(p, 999, desktop, true), 'reduced motion stays still');
  }
}
assert.equal(sample(-1, 0, true).index, 0);
assert.equal(sample(2, 0, true).index, 7);
console.log('PASS: order, 10,001 scroll samples, invisible handoffs, 16 closed orbits, direction, loop seams, reduced motion, endpoints');
