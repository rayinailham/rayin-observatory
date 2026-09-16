'use client';

import { useMemo, useRef, type MutableRefObject } from 'react';
import { useFrame } from '@react-three/fiber';
import { Color, Group, MathUtils, ShaderMaterial, Vector3 } from 'three';
import type { ChapterState } from '@/lib/instruments';
import type { CaseView } from '@/lib/cases';

const vertexShader = `varying vec3 vNormal; varying vec3 vPosition;
void main() { vNormal = normalize(normalMatrix * normal); vPosition = position;
gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`;
const fragmentShader = `
uniform vec3 uColor; uniform float uKind; uniform float uTime;
varying vec3 vNormal; varying vec3 vPosition;
float hash(vec3 p) { return fract(sin(dot(p, vec3(127.1,311.7,74.7))) * 43758.5453); }
float noise(vec3 p) {
 vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
 return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
 mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
void main() {
 vec3 n=normalize(vNormal), p=vPosition*4.;
 float detail=noise(p*2.)*.6+noise(p*5.)*.3+noise(p*12.)*.1;
 float bands=sin(p.y*15.+noise(p*2.)*3.+uTime*.05)*.5+.5;
 vec3 color=uColor * mix(.5,1.25,detail);
 if(uKind<.5) { color=mix(vec3(.035,.16,.29),vec3(.17,.33,.24),smoothstep(.45,.58,noise(p*.65)));
   float cloud=noise(p*3.+vec3(uTime*.018,0.,0.)); color=mix(color,vec3(.68,.79,.85),smoothstep(.66,.83,cloud)*.65);
 } else if(uKind<1.5) { color=uColor*mix(.55,1.28,bands)*mix(.8,1.1,detail); }
 float light=max(dot(n,normalize(vec3(-.65,.65,1.))),0.);
 color*=.13+light*.95;
 float rim=pow(1.-max(n.z,0.),3.)*max(dot(n,normalize(vec3(-.8,.3,.6))),0.);
 color+=uColor*rim*.6;
 gl_FragColor=vec4(color,1.);
 #include <colorspace_fragment>
}`;

function Planet({ kind, color }: { kind: number; color: string }) {
  const uniforms = useMemo(() => ({ uColor: { value: new Color(color) }, uKind: { value: kind }, uTime: { value: 0 } }), [color, kind]);
  return <mesh><sphereGeometry args={[1, 48, 32]} /><shaderMaterial uniforms={uniforms} vertexShader={vertexShader} fragmentShader={fragmentShader} /></mesh>;
}

/** Decorative planetary flybys stay in the margins, behind the instruments and copy. */
export default function PlanetaryJourney({ progress, chapter, caseView, reducedMotion }: {
  progress: MutableRefObject<number>; chapter: MutableRefObject<ChapterState>;
  caseView: MutableRefObject<CaseView>; reducedMotion: boolean;
}) {
  const groups = useRef<(Group | null)[]>([]);
  const journey = useRef(0);
  const axes = useMemo(() => ({ right: new Vector3(), up: new Vector3(), back: new Vector3() }), []);
  useFrame((state, delta) => {
    const { reveal, index, transition, orbit, outro } = chapter.current;
    const desktop = state.size.width >= 1024;
    const target = progress.current + reveal + Math.max(0, index - 1 + transition) + orbit * .55;
    journey.current = reducedMotion ? 0 : MathUtils.damp(journey.current, target, 5, Math.min(delta, .05));
    const t = journey.current;
    axes.right.set(1, 0, 0).applyQuaternion(state.camera.quaternion);
    axes.up.set(0, 1, 0).applyQuaternion(state.camera.quaternion);
    axes.back.set(0, 0, -6).applyQuaternion(state.camera.quaternion);
    groups.current.forEach((group, i) => {
      if (!group) return;
      group.visible = desktop && !reducedMotion && caseView.current.mix < .01 && outro < .99;
      if (!group.visible) return;
      const arrival = MathUtils.smootherstep(t, .15 + i * .65, .9 + i * .65);
      // Earth rises on the right; Jupiter and Mars cross the upper margin at different depths.
      const x = i === 0 ? .435 - Math.sin(t * .8) * .025 : i === 1 ? -.02 + Math.sin(t * .52) * .07 : -.32 + Math.cos(t * .62) * .055;
      const y = i === 0 ? -.66 + arrival * .53 + Math.sin(t * .75) * .11 : .74 - arrival * .41 + Math.sin(t * .7 + i) * .045;
      group.position.copy(axes.back).addScaledVector(axes.right, state.size.width / 100 * x)
        .addScaledVector(axes.up, state.size.height / 100 * y);
      const radius = [ .055, .035, .017 ][i] * state.size.height / 100;
      group.scale.setScalar(radius * (1 - outro * .8));
      group.rotation.y = state.clock.elapsedTime * .025 + t * .16;
      group.traverse(child => {
        if ('material' in child && child.material instanceof ShaderMaterial) child.material.uniforms.uTime.value = state.clock.elapsedTime;
      });
    });
  });
  return <>{['#6aa9d6', '#d6ae80', '#c57551'].map((color, i) => <group key={color} name={`JourneyPlanet${i}`} visible={false} ref={group => { groups.current[i] = group; }}><Planet kind={i} color={color} /></group>)}</>;
}
