import { DUE_ORBITS } from './instrument-models';
import {
  AdditiveBlending, BufferAttribute, BufferGeometry, Color, DoubleSide, MathUtils, Mesh, MeshBasicMaterial,
  MeshStandardMaterial, Points, RingGeometry, ShaderMaterial, SphereGeometry, TorusGeometry,
  type Material, type Object3D,
} from 'three';

export type Rig = { update: (time: number) => void; dispose: () => void; observe?: () => void };

// Point sprites are sized in CSS pixels; the scene refreshes the device pixel ratio each frame.
export const pointScale = { value: 1 };

const amber = new Color('#F2A541');
const ok = new Color('#5BE49B');
const alarm = new Color('#FF5A5F');
const inkTrace = new Color('#1A2440');
const line = new Color('#303A50');
const photon = new Color('#FFE9C4');
const TAU = Math.PI * 2;

const hash = (n: number) => { const s = Math.sin(n * 91.7) * 43758.5453; return s - Math.floor(s); };

function meshesUnder(object: Object3D | undefined) {
  const meshes: Mesh[] = [];
  object?.traverse(child => { if (child instanceof Mesh) meshes.push(child); });
  return meshes;
}

const materialName = (mesh: Mesh) => (mesh.material as Material).name;

function dots(capacity: number, size: number) {
  const geometry = new BufferGeometry();
  const position = new BufferAttribute(new Float32Array(capacity * 3), 3);
  const color = new BufferAttribute(new Float32Array(capacity * 3), 3);
  const sizes = new BufferAttribute(new Float32Array(capacity).fill(size), 1);
  geometry.setAttribute('position', position);
  geometry.setAttribute('color', color);
  geometry.setAttribute('size', sizes);
  const material = new ShaderMaterial({
    uniforms: { uScale: pointScale }, vertexColors: true, transparent: true, depthWrite: false, blending: AdditiveBlending,
    vertexShader: `uniform float uScale;
attribute float size;
varying vec3 vColor;
void main() { vColor = color; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); gl_PointSize = size * uScale; }`,
    fragmentShader: `varying vec3 vColor;
void main() {
  float d = length(gl_PointCoord - .5) * 2.;
  float a = smoothstep(1., 0., d);
  gl_FragColor = vec4(vColor * a * a, 1.);
  #include <colorspace_fragment>
}`,
  });
  const points = new Points(geometry, material);
  points.frustumCulled = false;
  return { points, geometry, material, position, color, sizes };
}

function glow(radiusIn: number, radiusOut: number) {
  return new Mesh(new RingGeometry(radiusIn, radiusOut, 48), new MeshBasicMaterial({
    color: amber, transparent: true, opacity: 0, blending: AdditiveBlending, depthWrite: false, side: DoubleSide, toneMapped: false,
  }));
}

function disposeAll(items: (BufferGeometry | Material)[]) { items.forEach(item => item.dispose()); }

// CrossCheck: the three engines light in turn, then agree together and turn green.
// Each channel's focus collar creeps while that channel is reading.
function crosscheck(view: Object3D, materials: MeshStandardMaterial[]): Rig {
  const lenses = [1, 2, 3].map(i => materials.filter(material => material.name === `Lens${i}Glow`));
  const collars = [0, 1, 2].map(i => view.getObjectByName(`FocusPivot${i}`));
  const strip = materials.filter(material => material.name === 'Amber light');
  const pivot = view.getObjectByName('OpticsPivot');
  const tint = new Color();
  return { dispose() {}, update(time) {
    const u = time % 6.6;
    const fade = 1 - MathUtils.smoothstep(u, 5.6, 6.4);
    const all = MathUtils.smoothstep(u, 3.7, 4.2) * fade;
    tint.copy(amber).lerp(ok, all);
    lenses.forEach((group, j) => {
      const turn = Math.sin(MathUtils.clamp((u - j * 1.2) / 1.2, 0, 1) * Math.PI);
      const ignite = MathUtils.smoothstep(u, 3.7 + j * .1, 3.85 + j * .1) * fade;
      group.forEach(material => { material.emissive.copy(tint); material.emissiveIntensity = .05 + turn ** 2 * 2 + ignite * 2.6; });
      const collar = collars[j];
      if (collar) collar.rotation.y = Math.sin(time * .22 + j * 2.1) * .16 + turn * .9;
    });
    strip.forEach(material => { material.emissive.copy(amber).lerp(ok, all * .85); material.emissiveIntensity = .6 + all * 1.6; });
    if (pivot) pivot.rotation.set(Math.sin(time * .65) * .022, Math.sin(time * .27) * .12 * (1 - all), 0);
  } };
}

// SurgeLine: every dish sweeps on its own rhythm and fires its own pulse.
const DISHES = [
  { yaw: .41, yawA: .4, pitch: .67, pitchA: .17, phase: 0, period: 1.9, offset: 0 },
  { yaw: .29, yawA: .3, pitch: .53, pitchA: .22, phase: 2.1, period: 2.7, offset: .8 },
  { yaw: .47, yawA: .34, pitch: .31, pitchA: .13, phase: 4.2, period: 1.45, offset: 1.3 },
  { yaw: .23, yawA: .46, pitch: .71, pitchA: .2, phase: 1.3, period: 3.3, offset: .4 },
];

function surgeline(view: Object3D): Rig {
  const made: (BufferGeometry | Material)[] = [];
  const dishes = DISHES.map((params, i) => {
    const pivot = view.getObjectByName(`DishPivot${i}`);
    const signal = meshesUnder(pivot).filter(mesh => materialName(mesh) === 'surgeline signal').map(mesh => mesh.material as MeshStandardMaterial);
    const rings = [0, 1].map(() => {
      const ring = glow(.2, .245);
      ring.frustumCulled = false;
      made.push(ring.geometry, ring.material);
      pivot?.add(ring);
      return ring;
    });
    return { params, pivot, signal, rings };
  });
  return { dispose: () => disposeAll(made), update(time) {
    dishes.forEach(({ params: p, pivot, signal, rings }) => {
      if (!pivot) return;
      const cycle = (time + p.offset) / p.period;
      const flash = Math.max(0, 1 - (cycle % 1) * 5) ** 2;
      pivot.rotation.set(Math.sin(time * p.pitch + p.phase) * p.pitchA,
        Math.sin(time * p.yaw + p.phase) * p.yawA + Math.sin(time * p.yaw * 2.3 + p.phase * 1.7) * p.yawA * .35, 0);
      pivot.scale.setScalar(1 + flash * .05);
      signal.forEach(material => { material.emissiveIntensity = .3 + flash * 2.8; });
      rings.forEach((ring, k) => {
        const travel = (cycle + k * .5) % 1;
        ring.position.z = .84 + travel * .9;
        ring.scale.setScalar(.35 + travel * 1.5);
        (ring.material as MeshBasicMaterial).opacity = (1 - travel) ** 2.2 * .9;
      });
    });
  } };
}

// DriftWatch: the paper really feeds, the pen draws a live trace, and a drift event
// kicks the needle into a red spike.
const burst = (t: number) => {
  const n = Math.floor(t / 5.2);
  return Math.exp(-(((t - n * 5.2 - 4.1) / .34) ** 2)) * (.55 + .45 * hash(n));
};
const reading = (t: number) => .03 * Math.sin(t * 9.1) + .022 * Math.sin(t * 15.7 + 1.3) + .014 * Math.sin(t * 27.3 + .4) + burst(t) * .5 * Math.sin(t * 15);

function driftwatch(view: Object3D, materials: MeshStandardMaterial[]): Rig {
  const needle = view.getObjectByName('NeedlePivot');
  const oldTrace = view.getObjectByName('PaperFeed');
  if (oldTrace) oldTrace.visible = false;
  const rollers = [0, 1].map(i => view.getObjectByName(`RollerPivot${i}`));
  const tip = materials.filter(material => material.name === 'driftwatch alarm');
  // Pen tip at (0.12, 0.98, 0.30); the paper surface sits at y 0.95 and runs to z -0.65.
  const N = 150, HISTORY = 2.4, PEN_X = .12, PEN_Z = .3, END_Z = -.6, Y = .962, WIDTH = .022;
  const speed = (PEN_Z - END_Z) / HISTORY;
  const trace = new BufferGeometry();
  const tracePosition = new BufferAttribute(new Float32Array(N * 6), 3);
  const traceColor = new BufferAttribute(new Float32Array(N * 6), 3);
  const index: number[] = [];
  for (let i = 0; i < N - 1; i++) index.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2);
  trace.setIndex(index);
  trace.setAttribute('position', tracePosition);
  trace.setAttribute('color', traceColor);
  const traceMaterial = new MeshBasicMaterial({ vertexColors: true, side: DoubleSide, toneMapped: false });
  const ticks = new BufferGeometry();
  const TICKS = 5, SPAN = 1.5;
  const tickPosition = new BufferAttribute(new Float32Array(TICKS * 12), 3);
  const tickIndex: number[] = [];
  for (let k = 0; k < TICKS; k++) tickIndex.push(k * 4, k * 4 + 1, k * 4 + 2, k * 4 + 1, k * 4 + 3, k * 4 + 2);
  ticks.setIndex(tickIndex);
  ticks.setAttribute('position', tickPosition);
  const tickMaterial = new MeshBasicMaterial({ color: '#8E97AB', side: DoubleSide, toneMapped: false });
  const traceMesh = new Mesh(trace, traceMaterial);
  const tickMesh = new Mesh(ticks, tickMaterial);
  traceMesh.frustumCulled = tickMesh.frustumCulled = false;
  view.add(traceMesh, tickMesh);
  const xs = new Float32Array(N), zs = new Float32Array(N), heat = new Float32Array(N);
  const tone = new Color();
  return { dispose: () => disposeAll([trace, traceMaterial, ticks, tickMaterial]), update(time) {
    for (let i = 0; i < N; i++) {
      const age = i / (N - 1) * HISTORY;
      xs[i] = PEN_X + reading(time - age);
      zs[i] = PEN_Z - age * speed;
      heat[i] = burst(time - age);
    }
    for (let i = 0; i < N; i++) {
      const a = Math.max(0, i - 1), b = Math.min(N - 1, i + 1);
      const dx = xs[b] - xs[a], dz = zs[b] - zs[a], length = Math.hypot(dx, dz) || 1;
      const nx = -dz / length * WIDTH / 2, nz = dx / length * WIDTH / 2;
      tracePosition.setXYZ(i * 2, xs[i] + nx, Y, zs[i] + nz);
      tracePosition.setXYZ(i * 2 + 1, xs[i] - nx, Y, zs[i] - nz);
      tone.copy(inkTrace).lerp(alarm, Math.min(1, heat[i] * 1.8));
      traceColor.setXYZ(i * 2, tone.r, tone.g, tone.b);
      traceColor.setXYZ(i * 2 + 1, tone.r, tone.g, tone.b);
    }
    tracePosition.needsUpdate = traceColor.needsUpdate = true;
    for (let k = 0; k < TICKS; k++) {
      const z = .86 - ((time * speed + k * SPAN / TICKS) % SPAN);
      tickPosition.setXYZ(k * 4, -.9, Y - .004, z - .004);
      tickPosition.setXYZ(k * 4 + 1, .9, Y - .004, z - .004);
      tickPosition.setXYZ(k * 4 + 2, -.9, Y - .004, z + .004);
      tickPosition.setXYZ(k * 4 + 3, .9, Y - .004, z + .004);
    }
    tickPosition.needsUpdate = true;
    const quake = burst(time);
    if (needle) needle.rotation.z = Math.asin(MathUtils.clamp(reading(time) / 1.22, -.9, .9));
    tip.forEach(material => { material.emissiveIntensity = .4 + quake * 3.5; });
    rollers.forEach(roller => { if (roller) roller.rotation.x = -time * speed / .16; });
    view.position.x = quake * Math.sin(time * 70) * .012;
  } };
}

// DueWatch: each planet runs its tilted track at a Kepler speed (period² ∝ radius³, so
// outer worlds are slower) while the tracks themselves slowly precess.
const ORBIT_SPEED = (radius: number) => 1.1 * (.65 / radius) ** 1.5;

function duewatch(view: Object3D, materials: MeshStandardMaterial[]): Rig {
  const sun = materials.filter(material => material.name === 'duewatch signal');
  const alarms = materials.filter(material => material.name === 'duewatch alarm');
  const orbits = DUE_ORBITS.map((spec, i) => ({
    track: view.getObjectByName(`OrbitPivot${i}`),
    planet: view.getObjectByName(`PlanetPivot${i}`),
    speed: ORBIT_SPEED(spec.radius),
    precession: spec.precession,
  }));
  return { dispose() {}, update(time) {
    orbits.forEach(orbit => {
      if (orbit.track) orbit.track.rotation.y = time * orbit.precession;
      if (orbit.planet) orbit.planet.rotation.y = time * orbit.speed;
    });
    // The red world flashes each time it passes its due mark.
    const lap = (time * orbits[1].speed) % TAU;
    const due = Math.exp(-((Math.min(lap, TAU - lap) / .3) ** 2));
    alarms.forEach(material => { material.emissiveIntensity = .5 + due * 2.6; });
    sun.forEach(material => { material.emissiveIntensity = 1 + Math.sin(time * 1.3) * .35 + due * .4; });
  } };
}

// BrandWall: photons leave the collimator, pass the prism and land on the sensor screen.
// Detector off → they build an interference (wave) pattern; detector on → the pattern
// collapses into two plain bands, as in the double-slit experiment. Tap observes.
const SPECTRUM = [[.95, .15, .16], [.95, .43, .065], [.36, .89, .61], [.24, .58, .95]].map(([r, g, b]) => new Color().setRGB(r, g, b));

function brandwall(view: Object3D, materials: MeshStandardMaterial[], onObserve?: (observed: boolean) => void): Rig {
  const prism = view.getObjectByName('PrismPivot');
  const spectrum = view.getObjectByName('SpectrumPivot');
  const beams = [0, 1, 2, 3].map(i => materials.filter(material => material.name === `Spectrum${i}`));
  const HITS = 380, FLIGHT = 60, LIFE = 4.6, TRAVEL = .8, RATE = 64, SCREEN_X = 1.325;
  const hits = dots(HITS, 3.4);
  const photons = dots(FLIGHT, 3);
  // The screen reads as phosphor: the pattern also glows through its back face.
  const behind = new Points(hits.geometry, hits.material);
  behind.position.x = .15;
  behind.frustumCulled = false;
  const detector = new Mesh(new TorusGeometry(.36, .016, 8, 48), new MeshBasicMaterial({ color: line, toneMapped: false }));
  detector.position.set(.86, 1.9, 0);
  detector.rotation.y = Math.PI / 2;
  view.add(hits.points, behind, photons.points, detector);
  const born = new Float32Array(HITS).fill(-99);
  const base = new Float32Array(HITS * 3);
  const flights = Array.from({ length: FLIGHT }, () => ({ born: -99, y: 0, z: 0, observed: false, landed: true }));
  const tone = new Color();
  let nextHit = 0, nextFlight = 0, spawnAt = 0, observeUntil = -1, pending = false, shown: boolean | null = null, mix = 0, last = 0;
  const observedAt = (t: number) => t < observeUntil || t % 13 > 8.5;
  const gauss = () => (Math.random() + Math.random() + Math.random() - 1.5) * 2;
  const landing = (observed: boolean) => {
    if (observed) return (Math.random() < .5 ? -.36 : .36) + gauss() * .05;
    for (let k = 0; k < 40; k++) {
      const z = (Math.random() * 2 - 1) * .8;
      if (Math.random() < Math.cos(z * Math.PI / .13) ** 2 * Math.exp(-((z / .62) ** 2))) return z;
    }
    return 0;
  };
  const spectrumAt = (z: number) => {
    const t = MathUtils.clamp((.6 - z) / 1.2, 0, 1) * 3, i = Math.min(2, Math.floor(t));
    return tone.lerpColors(SPECTRUM[i], SPECTRUM[i + 1], t - i);
  };
  return {
    observe() { pending = true; },
    dispose: () => disposeAll([hits.geometry, hits.material, photons.geometry, photons.material, detector.geometry, detector.material as Material]),
    update(time) {
      const step = Math.min(.1, Math.max(0, time - last));
      last = time;
      if (pending) { observeUntil = time + 5; pending = false; }
      const observed = observedAt(time);
      if (observed !== shown) { shown = observed; onObserve?.(observed); }
      mix = MathUtils.damp(mix, observed ? 1 : 0, 4, step);
      if (spawnAt < time - 1) spawnAt = time;
      while (spawnAt <= time) {
        const flight = flights[nextFlight++ % FLIGHT];
        flight.observed = observedAt(spawnAt);
        Object.assign(flight, { born: spawnAt, landed: false, z: landing(flight.observed), y: 1.95 + (Math.random() * 2 - 1) * .5 });
        spawnAt += 1 / RATE;
      }
      flights.forEach((flight, k) => {
        const age = time - flight.born;
        if (!flight.landed && age >= TRAVEL) {
          flight.landed = true;
          const slot = nextHit++ % HITS;
          born[slot] = flight.born + TRAVEL;
          hits.position.setXYZ(slot, SCREEN_X, flight.y, flight.z);
          spectrumAt(flight.z).toArray(base, slot * 3);
        }
        if (flight.landed) { photons.color.setXYZ(k, 0, 0, 0); return; }
        const t = age / TRAVEL;
        if (t < .42) photons.position.setXYZ(k, MathUtils.lerp(-1, 0, t / .42), 1.95, 0);
        else {
          const s = (t - .42) / .58;
          photons.position.setXYZ(k, MathUtils.lerp(0, SCREEN_X, s), MathUtils.lerp(1.95, flight.y, s), MathUtils.lerp(0, flight.z, s));
        }
        const color = flight.observed ? tone.copy(photon).multiplyScalar(1.2) : spectrumAt(flight.z).multiplyScalar(.7);
        photons.color.setXYZ(k, color.r, color.g, color.b);
        photons.sizes.setX(k, flight.observed ? 4.6 : 2.6);
      });
      photons.position.needsUpdate = photons.color.needsUpdate = photons.sizes.needsUpdate = true;
      for (let i = 0; i < HITS; i++) {
        const life = time - born[i];
        const fade = life < 0 ? 0 : life < .12 ? 1.8 : Math.max(0, 1 - life / LIFE) ** 1.3;
        hits.color.setXYZ(i, base[i * 3] * fade, base[i * 3 + 1] * fade, base[i * 3 + 2] * fade);
      }
      hits.position.needsUpdate = hits.color.needsUpdate = true;
      (detector.material as MeshBasicMaterial).color.copy(line).lerp(ok, mix);
      beams.forEach((group, i) => group.forEach(material => {
        material.emissiveIntensity = MathUtils.lerp(.6 + .45 * Math.sin(time * 5 + i * 1.4), .22, mix);
      }));
      if (prism) prism.rotation.y = time * .16;
      if (spectrum) spectrum.rotation.y = Math.sin(time * .5) * .06 * (1 - mix);
    },
  };
}

export function rigInstrument(id: string, view: Object3D, materials: MeshStandardMaterial[], onObserve?: (observed: boolean) => void): Rig {
  if (id === 'crosscheck') return crosscheck(view, materials);
  if (id === 'surgeline') return surgeline(view);
  if (id === 'driftwatch') return driftwatch(view, materials);
  if (id === 'duewatch') return duewatch(view, materials);
  return brandwall(view, materials, onObserve);
}

// Saturn: banded planet that visibly spins, a Cassini gap, ring dust orbiting at Kepler
// speeds and two small moons that pass in front of and behind the globe.
export function saturn(source: Object3D): Rig & { object: Object3D } {
  const object = source.clone(true);
  const made: (BufferGeometry | Material)[] = [];
  const meshes = meshesUnder(object);
  const planet = meshes.find(mesh => materialName(mesh).includes('planet'));
  const rings = meshes.find(mesh => materialName(mesh).includes('rings'));
  const shade = (mesh: Mesh | undefined, key: string, body: string) => {
    if (!mesh) return;
    const material = (mesh.material as MeshStandardMaterial).clone();
    material.customProgramCacheKey = () => key;
    material.onBeforeCompile = shader => {
      shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vObject;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvObject = position;');
      shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vObject;')
        .replace('#include <color_fragment>', `#include <color_fragment>\n${body}`);
    };
    mesh.material = material;
    made.push(material);
  };
  shade(planet, 'saturn-planet', `
    float lat = vObject.y;
    float band = sin(lat * 17. + sin(lat * 6.) * 1.4) * .5 + .5;
    float lon = atan(vObject.z, vObject.x);
    float storm = exp(-pow((lat + .32) / .08, 2.) - pow(sin((lon - .8) * .5) / .14, 2.));
    diffuseColor.rgb *= mix(.72, 1.18, band);
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(.55, .38, .22), storm * .8 + (1. - abs(lat)) * .1);`);
  shade(rings, 'saturn-rings', `
    float radius = length(vObject.xz);
    diffuseColor.rgb *= .72 + .28 * sin(radius * 41.);
    diffuseColor.rgb *= 1. - .78 * smoothstep(.03, 0., abs(radius - 1.47));`);
  const DUST = 520;
  const dust = new BufferGeometry();
  const orbit = new Float32Array(DUST * 3);
  for (let i = 0; i < DUST; i++) orbit.set([1.12 + Math.random() * .62, Math.random() * TAU, (Math.random() - .5) * .025], i * 3);
  dust.setAttribute('position', new BufferAttribute(new Float32Array(DUST * 3), 3));
  dust.setAttribute('orbit', new BufferAttribute(orbit, 3));
  const time = { value: 0 };
  const dustMaterial = new ShaderMaterial({
    uniforms: { uTime: time, uScale: pointScale }, transparent: true, depthWrite: false, blending: AdditiveBlending,
    vertexShader: `uniform float uTime;
uniform float uScale;
attribute vec3 orbit;
varying float vGlow;
void main() {
  float a = orbit.y + uTime * .55 * pow(orbit.x, -1.5);
  vGlow = .5 + .5 * sin(uTime * 2.3 + orbit.y * 17.);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(cos(a) * orbit.x, orbit.z, -sin(a) * orbit.x, 1.);
  gl_PointSize = 1.4 * uScale;
}`,
    fragmentShader: `varying float vGlow;
void main() {
  float a = smoothstep(1., 0., length(gl_PointCoord - .5) * 2.);
  gl_FragColor = vec4(vec3(1., .86, .66) * a * vGlow * .32, 1.);
  #include <colorspace_fragment>
}`,
  });
  const dustPoints = new Points(dust, dustMaterial);
  dustPoints.frustumCulled = false;
  const moonGeometry = new SphereGeometry(1, 16, 12);
  const moonMaterial = new MeshStandardMaterial({ color: '#CFC6B4', roughness: .85 });
  const moons = [{ radius: 2.3, size: .1, speed: .9, phase: 0 }, { radius: 2.85, size: .07, speed: .9 * (2.3 / 2.85) ** 1.5, phase: 2.4 }].map(spec => {
    const moon = new Mesh(moonGeometry, moonMaterial);
    moon.scale.setScalar(spec.size);
    object.add(moon);
    return { moon, ...spec };
  });
  object.add(dustPoints);
  made.push(dust, dustMaterial, moonGeometry, moonMaterial);
  return { object, dispose: () => disposeAll(made), update(t) {
    time.value = t;
    if (planet) planet.rotation.y = t * .35;
    moons.forEach(({ moon, radius, speed, phase }) => {
      const a = phase + t * speed;
      moon.position.set(Math.cos(a) * radius, Math.sin(a * .5) * .04, -Math.sin(a) * radius);
    });
  } };
}
