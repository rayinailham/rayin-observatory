'use client';

import { Component, Suspense, useEffect, useMemo, useRef, type ReactNode, type MutableRefObject } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Center, Environment, Lightformer, useGLTF } from '@react-three/drei';
import { Group, MathUtils, Mesh, MeshStandardMaterial, Vector3 } from 'three';
import { instruments, type ChapterState } from '@/lib/instruments';
import { pointScale, rigInstrument, saturn } from './instrument-motion';
import Sky from './sky';

useGLTF.setDecoderPath('/draco/');

type SceneProps = {
  entered: boolean;
  progress: MutableRefObject<number>;
  chapter: MutableRefObject<ChapterState>;
  onReady: () => void;
  onFailure: () => void;
};

// BrandWall's detector state is shown in the chapter hint; the page owns the markup.
const showObserver = (observed: boolean) => document.getElementById('observer-readout')?.setAttribute('data-observed', String(observed));

class SceneBoundary extends Component<{ onFailure: () => void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}

function World({ entered, progress, chapter, onReady }: SceneProps) {
  const dome = useGLTF('/models/dome.glb');
  const ambient = useGLTF('/models/ambient.glb');
  const models = useGLTF(instruments.map(item => `/models/${item.id}.glb`));
  const views = useMemo(() => models.map((model, i) => {
    const view = model.scene.clone(true);
    const materials: MeshStandardMaterial[] = [];
    view.traverse(object => {
      if (!(object instanceof Mesh)) return;
      const clone = (source: MeshStandardMaterial) => {
        const material = source.clone();
        material.roughness = Math.max(material.roughness, .5);
        material.metalness = Math.min(material.metalness, .55);
        materials.push(material);
        if (/^Lens[123]Glow$/.test(material.name)) material.emissive.set('#F2A541');
        return material;
      };
      object.material = Array.isArray(object.material) ? object.material.map(clone) : clone(object.material);
    });
    return { view, materials, rig: rigInstrument(instruments[i].id, view, materials, showObserver) };
  }), [models]);
  useEffect(() => () => views.forEach(item => {
    item.rig.dispose();
    item.materials.forEach(material => material.dispose());
  }), [views]);
  useEffect(() => {
    const brandwall = views[instruments.findIndex(item => item.id === 'brandwall')];
    const tap = (event: MouseEvent) => {
      if (document.querySelector('.observatory')?.getAttribute('data-chapter') !== 'brandwall') return;
      if ((event.target as HTMLElement).closest('button, a, summary, dialog')) return;
      brandwall?.rig.observe?.();
    };
    window.addEventListener('click', tap);
    return () => window.removeEventListener('click', tap);
  }, [views]);
  const planet = useMemo(() => saturn(ambient.scene), [ambient.scene]);
  useEffect(() => () => planet.dispose(), [planet]);
  const domeView = useMemo(() => {
    const view = dome.scene.clone(true);
    view.traverse(object => {
      if (!(object instanceof Mesh) || !(object.material instanceof MeshStandardMaterial)) return;
      const material = object.material.clone();
      // Broader highlights suit the small real-time view; approved color stays intact.
      if (material.name !== 'Amber light') {
        material.roughness = Math.max(material.roughness, .65);
        material.metalness = Math.min(material.metalness, .45);
        material.envMapIntensity = .4;
      }
      object.material = material;
    });
    return view;
  }, [dome.scene]);
  useEffect(() => () => {
    domeView.traverse(object => {
      if (object instanceof Mesh && object.material instanceof MeshStandardMaterial) object.material.dispose();
    });
  }, [domeView]);
  const domeRef = useRef<Group>(null);
  const instrumentRefs = useRef<(Group | null)[]>([]);
  const planetRef = useRef<Group>(null);
  const revealed = useRef(0);
  const { viewport } = useThree();
  const frames = useRef(0);
  const cameraUp = useMemo(() => new Vector3(), []);
  const cameraRight = useMemo(() => new Vector3(), []);
  const cameraBack = useMemo(() => new Vector3(), []);

  useFrame((state, delta) => {
    if (++frames.current === 2) onReady();
    const step = Math.min(delta, 0.05);
    revealed.current = MathUtils.damp(revealed.current, entered ? 1 : 0, 2.2, step);
    pointScale.value = state.gl.getPixelRatio();
    const time = state.clock.elapsedTime;
    const scroll = progress.current;
    const reveal = chapter.current.reveal;
    const orbit = chapter.current.orbit;
    const { index, transition, outro } = chapter.current;
    const angle = index > 0 && transition < 1 ? MathUtils.lerp(-.95, .55, transition) : (.55 - orbit * 1.5) * reveal;
    const elevation = .25 * reveal;
    // The camera itself travels around the stationary mount; scroll backward retraces it.
    state.camera.position.set(16 * Math.sin(angle) * Math.cos(elevation), 16 * Math.sin(elevation), 16 * Math.cos(angle) * Math.cos(elevation));
    state.camera.lookAt(0, 0, 0);
    cameraUp.set(0, 1, 0).applyQuaternion(state.camera.quaternion);
    views.forEach((moving, i) => {
      const group = instrumentRefs.current[i];
      if (!group) return;
      const incoming = i === index;
      const outgoing = i === index - 1 && transition < 1;
      group.visible = reveal > 0 && outro < 1 && (incoming || outgoing);
      const offset = incoming ? -(1 - transition) : transition;
      group.scale.setScalar(Math.min(viewport.width * .82, viewport.height * .37) / (i === 0 ? 4.4 : 3.5));
      group.position.copy(cameraUp).multiplyScalar(viewport.height * (-.03 + offset + outro));
      if (group.visible) moving.rig.update(time);
    });
    if (domeRef.current) {
      domeRef.current.visible = reveal < .7;
      const scale = viewport.width / 7.4 * (0.83 + revealed.current * 0.17 + scroll * .2);
      domeRef.current.scale.setScalar(scale);
      domeRef.current.position.y = -viewport.height * (.135 - scroll * .12) - (1 - revealed.current) * .45 + reveal * viewport.height * 1.4;
      domeRef.current.rotation.set(.30 + scroll * .10, -.48 + scroll * .6 + Math.sin(time * .1) * .025, 0);
    }
    if (planetRef.current) {
      // Screen-anchored so the orbiting camera never sweeps it across the instrument;
      // in the chapter it settles beside the heading as a small moon.
      const moon = MathUtils.smoothstep(reveal, .35, .9);
      cameraRight.set(1, 0, 0).applyQuaternion(state.camera.quaternion);
      cameraBack.set(0, 0, -1).applyQuaternion(state.camera.quaternion).multiplyScalar(4);
      planetRef.current.position.copy(cameraBack)
        .addScaledVector(cameraRight, viewport.width * MathUtils.lerp(.31, .38, moon))
        .addScaledVector(cameraUp, viewport.height * MathUtils.lerp(.015, .31, moon) + Math.sin(time * .14) * .05);
      planetRef.current.rotation.set(.4 + Math.sin(time * .21) * .05, .15 + time * .015, -.38 + Math.sin(time * .17) * .04);
      planetRef.current.scale.setScalar(viewport.width * .072 * MathUtils.lerp(1, .78, moon));
      planet.update(time);
    }
  });

  return <>
    <Sky progress={progress} />
    <ambientLight intensity={.6} />
    <directionalLight position={[3, 6, 5]} intensity={.65} color="#cadcff" />
    <directionalLight position={[-4, 1, 3]} intensity={.55} color="#F2A541" />
    <directionalLight position={[0, 4, -4]} intensity={.9} color="#a1b6e7" />
    <Environment resolution={128} frames={1}>
      <Lightformer intensity={2} color="#cadcff" position={[0, 5, -5]} scale={[10, 5, 1]} />
      <Lightformer intensity={1.3} color="#F2A541" position={[-5, 1, 2]} rotation={[0, Math.PI / 2, 0]} scale={[4, 8, 1]} />
      <Lightformer intensity={1.8} color="#a1b6e7" position={[5, 3, 1]} rotation={[0, -Math.PI / 2, 0]} scale={[5, 7, 1]} />
    </Environment>
    <group ref={planetRef}><primitive object={planet.object} /></group>
    <group ref={domeRef}><Center><primitive object={domeView} /></Center></group>
    {views.map((item, i) => <group key={instruments[i].id} ref={group => { instrumentRefs.current[i] = group; }}><Center><primitive object={item.view} /></Center></group>)}
  </>;
}

export default function ObservatoryScene(props: SceneProps) {
  return <SceneBoundary onFailure={props.onFailure}>
    <Canvas orthographic camera={{ position: [0, 0, 16], zoom: 100, near: .1, far: 100 }}
      dpr={[1, 1.5]} gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      onCreated={({ gl }) => {
        gl.setClearColor('#0B1020', 0);
        gl.domElement.addEventListener('webglcontextlost', props.onFailure, { once: true });
      }}
      fallback={<span>Live 3D is unavailable.</span>}>
      <Suspense fallback={null}><World {...props} /></Suspense>
    </Canvas>
  </SceneBoundary>;
}
