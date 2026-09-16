'use client';

import { useMemo, useRef, type MutableRefObject } from 'react';
import { useFrame } from '@react-three/fiber';
import { Color, Group, MathUtils, Mesh, Vector3, type Material, type Object3D, type ShaderMaterial } from 'three';
import { planets, samplePlanetJourney } from '@/lib/planetary-motion';
import type { Rig } from './instrument-motion';
import type { CaseView } from '@/lib/cases';

const vertexShader = `varying vec3 vNormal; varying vec3 vPosition;
void main() { vNormal = normalize(normalMatrix * normal); vPosition = position;
gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`;
const fragmentShader = `
uniform vec3 uColor; uniform float uKind; uniform float uTime; uniform float uOpacity;
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
 gl_FragColor=vec4(color,uOpacity);
 #include <colorspace_fragment>
}`;

type PlanetUniforms = { uColor: { value: Color }; uKind: { value: number }; uTime: { value: number }; uOpacity: { value: number } };

function Planet({ uniforms, materialRef }: { uniforms: PlanetUniforms; materialRef: (material: ShaderMaterial | null) => void }) {
  return <mesh><sphereGeometry args={[1, 48, 32]} /><shaderMaterial ref={materialRef} uniforms={uniforms} vertexShader={vertexShader} fragmentShader={fragmentShader} transparent depthWrite={false} /></mesh>;
}

/** One screen-anchored planet, with independent scroll passage and idle orbit. */
export default function PlanetaryJourney({ progress, caseView, reducedMotion, saturnRig }: {
  progress: MutableRefObject<number>; caseView: MutableRefObject<CaseView>;
  reducedMotion: boolean; saturnRig: Rig & { object: Object3D };
}) {
  const groups = useRef<(Group | null)[]>([]);
  const bodies = useRef<(Group | null)[]>([]);
  const materials = useRef<(ShaderMaterial | null)[]>([]);
  const journey = useRef<number | null>(null);
  const elapsed = useRef(0);
  const axes = useMemo(() => ({ right: new Vector3(), up: new Vector3(), back: new Vector3() }), []);
  const uniforms = useMemo(() => planets.map(planet => ({ uColor: { value: new Color(planet.color) }, uKind: { value: planet.kind }, uTime: { value: 0 }, uOpacity: { value: 1 } })), []);
  const saturnMaterials = useMemo(() => {
    const materials = new Set<Material>();
    saturnRig.object.traverse(child => {
      if (child instanceof Mesh) (Array.isArray(child.material) ? child.material : [child.material]).forEach(material => materials.add(material));
    });
    return [...materials].map(material => {
      material.transparent = true;
      return { material, opacity: material.opacity };
    });
  }, [saturnRig]);

  useFrame((state, delta) => {
    const step = Math.min(delta, .05);
    if (!reducedMotion) elapsed.current += step;
    // Lenis already smooths wheel input. A short, non-overshooting settle also handles
    // native touch, history restoration and scrollbar jumps without chapter resets.
    journey.current = journey.current === null || reducedMotion || caseView.current.active
      ? progress.current : MathUtils.damp(journey.current, progress.current, 12, step);
    const pose = samplePlanetJourney(journey.current, elapsed.current, state.size.width >= 1024, reducedMotion);
    const zoom = 'zoom' in state.camera ? Number(state.camera.zoom) : 100;
    const width = state.size.width / zoom, height = state.size.height / zoom;
    axes.right.set(1, 0, 0).applyQuaternion(state.camera.quaternion);
    axes.up.set(0, 1, 0).applyQuaternion(state.camera.quaternion);
    axes.back.set(0, 0, -6).applyQuaternion(state.camera.quaternion);
    groups.current.forEach((group, i) => {
      if (!group) return;
      group.visible = i === pose.index && pose.opacity > .001 && !caseView.current.active && caseView.current.mix < .01;
      if (!group.visible) return;
      group.position.copy(axes.back).addScaledVector(axes.right, width * pose.x).addScaledVector(axes.up, height * pose.y);
      // Cancel the instrument camera's orbit before applying the planet's own axial tilt.
      group.quaternion.copy(state.camera.quaternion);
      group.scale.setScalar(Math.min(height * .047, width * .052) * planets[i].size);
      bodies.current[i]?.rotation.set(.15, elapsed.current * planets[i].spin, planets[i].tilt, 'ZYX');
      // R3F preserves its own uniform wrappers; mutate the mounted material, not props.
      const material = materials.current[i];
      if (material) {
        material.uniforms.uTime.value = elapsed.current;
        material.uniforms.uOpacity.value = pose.opacity;
      }
      if (i === 5) {
        saturnMaterials.forEach(({ material, opacity }) => { material.opacity = opacity * pose.opacity; });
        saturnRig.update(elapsed.current);
      }
    });
  });
  return <>{planets.map((planet, i) => <group key={planet.name} name={`JourneyPlanet-${planet.name}`} visible={false} ref={group => { groups.current[i] = group; }}>
    <group ref={group => { bodies.current[i] = group; }}>
      {i === 5 ? <primitive object={saturnRig.object} /> : <Planet uniforms={uniforms[i]} materialRef={material => { materials.current[i] = material; }} />}
    </group>
  </group>)}</>;
}
