'use client';

import { useMemo, useRef, type MutableRefObject } from 'react';
import { useFrame } from '@react-three/fiber';
import { MathUtils, ShaderMaterial, Vector2 } from 'three';
import type { ChapterState } from '@/lib/instruments';

// Full-screen night sky: pitch black zenith easing into the ink horizon, procedural
// twinkling stars in three depths and a faint nebula band. Decoration, not astronomy data.
const vertexShader = `void main() { gl_Position = vec4(position.xy, 0., 1.); }`;

const fragmentShader = `
precision highp float;
uniform float uTime;
uniform vec2 uOffset;
uniform vec2 uRes;
uniform float uDpr;

float hash(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3. - 2. * f);
  return mix(mix(hash(i), hash(i + vec2(1., 0.)), f.x), mix(hash(i + vec2(0., 1.)), hash(i + 1.), f.x), f.y);
}
vec3 stars(vec2 px, float cell, float density, float depth, float size) {
  vec2 p = (px + uOffset * depth) / cell;
  vec2 id = floor(p);
  float h = hash(id);
  if (h > density) return vec3(0.);
  vec2 o = vec2(hash(id + 7.1), hash(id + 3.7)) - .5;
  float d = length(fract(p) - .5 - o * .7) * cell;
  float r = size * mix(.55, 1.25, hash(id + 3.3));
  float twinkle = .5 + .5 * sin(uTime * mix(.7, 2.6, hash(id + 5.)) + h * 60.);
  float light = smoothstep(r, 0., d) + exp(-d * d / (r * r * 7.)) * .45;
  float t = hash(id + 9.);
  vec3 tint = t < .14 ? vec3(1., .8, .58) : t < .42 ? vec3(.74, .84, 1.) : vec3(1.);
  return tint * light * mix(.45, 1., twinkle) * mix(.55, 1., hash(id + 1.7));
}
void main() {
  vec2 px = gl_FragCoord.xy / uDpr;
  vec2 screen = uRes / uDpr;
  float y = gl_FragCoord.y / uRes.y;
  vec3 horizon = vec3(.063, .09, .176);
  vec3 ink = vec3(.043, .063, .125);
  vec3 zenith = vec3(.004, .006, .016);
  // Owner revision: blue holds the lower 70%; only the top 30% deepens to black.
  vec3 color = mix(horizon, ink, smoothstep(0., .35, y));
  color = mix(color, zenith, smoothstep(.7, .97, y));
  vec2 q = (px + uOffset * .4) / 210.;
  float cloud = noise(q) * .55 + noise(q * 2.2) * .3 + noise(q * 4.7) * .15;
  float lane = exp(-pow((px.y - screen.y * .8 + (px.x - screen.x * .5) * .55) / (screen.y * .19), 2.));
  color += mix(vec3(.05, .045, .12), vec3(.1, .06, .05), noise(q * .6)) * lane * smoothstep(.35, .9, cloud) * .9;
  // Owner revision 3: gate-like density, only in the black top 30%; the blue 70% keeps a rare faint few.
  float reach = smoothstep(.62, .74, y);
  color += (stars(px, 29., .12, .5, .8) + stars(px, 74., .2, 1., 1.15) * 1.2) * reach * (1. + lane * .3);
  color += stars(px, 96., .14, .7, .75) * .45 * (1. - reach);
  color += (hash(gl_FragCoord.xy) - .5) / 255.;
  gl_FragColor = vec4(color, 1.);
}`;

export default function Sky({ progress, chapter, reducedMotion }: { progress: MutableRefObject<number>; chapter: MutableRefObject<ChapterState>; reducedMotion: boolean }) {
  const material = useRef<ShaderMaterial>(null);
  const uniforms = useMemo(() => ({ uTime: { value: 0 }, uOffset: { value: new Vector2() }, uRes: { value: new Vector2(1, 1) }, uDpr: { value: 1 } }), []);
  useFrame((state, delta) => {
    if (!material.current) return;
    const { uTime, uOffset, uRes, uDpr } = material.current.uniforms;
    uTime.value = reducedMotion ? 0 : state.clock.elapsedTime;
    // Stars drift against the camera orbit and the hero rise, deeper layers slower.
    const angle = Math.atan2(state.camera.position.x, state.camera.position.z);
    const travel = chapter.current.index + chapter.current.transition + chapter.current.orbit;
    const targetY = reducedMotion ? 0 : progress.current * 150 + travel * 55 + state.camera.position.y * 14;
    uOffset.value.x = MathUtils.damp(uOffset.value.x, reducedMotion ? 0 : angle * 240, 5, Math.min(delta, .05));
    uOffset.value.y = MathUtils.damp(uOffset.value.y, targetY, 5, Math.min(delta, .05));
    state.gl.getDrawingBufferSize(uRes.value);
    uDpr.value = state.gl.getPixelRatio();
  });
  return <mesh frustumCulled={false} renderOrder={-10}>
    <planeGeometry args={[2, 2]} />
    <shaderMaterial ref={material} uniforms={uniforms} vertexShader={vertexShader} fragmentShader={fragmentShader} depthTest={false} depthWrite={false} />
  </mesh>;
}
