'use client';

import { Component, Suspense, useEffect, useMemo, useRef, type ReactNode, type MutableRefObject } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Center, Environment, Lightformer, useGLTF } from '@react-three/drei';
import { Group, MathUtils, Mesh, MeshStandardMaterial, OrthographicCamera, Vector3, type Material, type Object3D } from 'three';
import { instruments, type ChapterState } from '@/lib/instruments';
import { pointScale, rigInstrument, saturn } from './instrument-motion';
import Sky from './sky';
import { caseFiles, type CaseComponent, type CaseView } from '@/lib/cases';

useGLTF.setDecoderPath('/draco/');

type SceneProps = {
  entered: boolean;
  progress: MutableRefObject<number>;
  chapter: MutableRefObject<ChapterState>;
  caseView: MutableRefObject<CaseView>;
  onReady: () => void;
  onFailure: () => void;
  onInstrumentTap: (index: number) => void;
};

// BrandWall's detector state is shown in the chapter hint; the page owns the markup.
const showObserver = (observed: boolean) => document.getElementById('observer-readout')?.setAttribute('data-observed', String(observed));

// Leader endpoint: the node's origin, or the centre of its child mesh whose material name
// contains `part` (a moving planet, a dish feed, the prism), so the line follows the rig.
function anchor(view: Object3D, item: CaseComponent, target: Vector3) {
  const node = view.getObjectByName(item.node);
  if (!node) return false;
  if (!item.part) { node.getWorldPosition(target); return true; }
  let mesh: Mesh | undefined;
  node.traverse(child => { if (!mesh && child instanceof Mesh && (child.material as Material).name.includes(item.part!)) mesh = child; });
  if (!mesh) return false;
  if (!mesh.geometry.boundingSphere) mesh.geometry.computeBoundingSphere();
  mesh.localToWorld(target.copy(mesh.geometry.boundingSphere!.center));
  return true;
}

class SceneBoundary extends Component<{ onFailure: () => void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}

function World({ entered, progress, chapter, caseView, onReady, onInstrumentTap }: SceneProps) {
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
      const shell = document.querySelector('.observatory.has-entered[data-flight=idle]');
      if (shell?.getAttribute('data-chapter') !== 'brandwall') return;
      const target = event.target as HTMLElement;
      if (target.closest('button, a, summary, dialog') || !target.closest('#brandwall .instrument-stage, .case-inspection')) return;
      brandwall?.rig.observe?.();
      onInstrumentTap(4);
    };
    window.addEventListener('click', tap);
    return () => window.removeEventListener('click', tap);
  }, [views, onInstrumentTap]);
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
  const { size } = useThree();
  const viewport = { width: size.width / 100, height: size.height / 100 };
  const desktop = size.width >= 1024;
  const casePosition = useRef(0);
  const projected = useMemo(() => new Vector3(), []);
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
    const { index, transition, outro, from } = chapter.current;
    const { mix, index: caseIndex } = caseView.current;
    const baseAngle = (index > 0 || from !== undefined) && transition < 1 ? MathUtils.lerp(-.95, .55, transition) : (.55 - orbit * 1.5) * reveal;
    const angle = MathUtils.lerp(baseAngle, .55, mix);
    const elevation = MathUtils.lerp(.25 * reveal, .25, mix);
    const distance = MathUtils.lerp(16, 10, mix);
    const zoom = MathUtils.lerp(100, 130, mix);
    if (state.camera instanceof OrthographicCamera && state.camera.zoom !== zoom) {
      state.camera.zoom = zoom;
      state.camera.updateProjectionMatrix();
    }
    const stage = caseView.current.active ? document.querySelector<HTMLElement>('.case-inspection') : null;
    const stageRect = stage?.getBoundingClientRect();
    const stageLeft = stageRect ? stageRect.left - state.gl.domElement.getBoundingClientRect().left : 0;
    const targetY = stageRect ? (size.height / 2 - stageRect.top - stageRect.height * (desktop ? .50 : .47)) / zoom : -viewport.height * .03;
    const homeX = desktop ? viewport.width * .20 : 0;
    const caseX = stageRect ? (stageLeft + stageRect.width / 2 - size.width / 2) / zoom : homeX * 100 / zoom;
    casePosition.current = MathUtils.damp(casePosition.current, targetY, 12, step);
    // The camera itself travels around the stationary mount; scroll backward retraces it.
    state.camera.position.set(distance * Math.sin(angle) * Math.cos(elevation), distance * Math.sin(elevation), distance * Math.cos(angle) * Math.cos(elevation));
    state.camera.lookAt(0, 0, 0);
    cameraUp.set(0, 1, 0).applyQuaternion(state.camera.quaternion);
    cameraRight.set(1, 0, 0).applyQuaternion(state.camera.quaternion);
    views.forEach((moving, i) => {
      const group = instrumentRefs.current[i];
      if (!group) return;
      const incoming = i === index;
      const outgoing = i === (from ?? index - 1) && transition < 1;
      group.visible = mix > .001 && i === caseIndex || (mix < .999 && reveal > 0 && outro < 1 && (incoming || outgoing));
      const offset = incoming ? -(1 - transition) : transition;
      const fit = i === 0 ? 4.4 : 3.5;
      const homeScale = Math.min(viewport.width * (desktop ? .48 : .82), viewport.height * (desktop ? .66 : .37)) / fit;
      const caseScale = desktop
        ? Math.min((stageRect?.width ?? size.width * .55) * .76, size.height * .60) / zoom / fit
        : Math.min(viewport.width * .62, viewport.height * .33) / fit;
      const inCase = i === caseIndex ? mix : 0;
      group.scale.setScalar(MathUtils.lerp(homeScale, caseScale, inCase));
      group.position.copy(cameraUp).multiplyScalar(MathUtils.lerp(viewport.height * (-.03 + offset + outro), casePosition.current, inCase));
      group.position.addScaledVector(cameraRight, MathUtils.lerp(homeX, caseX, inCase));
      if (group.visible) moving.rig.update(time);
    });
    if (domeRef.current) {
      domeRef.current.visible = reveal < .7 && mix < .01;
      const scale = (desktop ? Math.min(viewport.width * .58, viewport.height * .94) : viewport.width) / 7.4 * (0.83 + revealed.current * 0.17 + scroll * .2);
      domeRef.current.scale.setScalar(scale);
      domeRef.current.position.copy(cameraRight).multiplyScalar(desktop ? viewport.width * .19 : 0);
      domeRef.current.position.y = -viewport.height * ((desktop ? .035 : .135) - scroll * .12) - (1 - revealed.current) * .45 + reveal * viewport.height * 1.4;
      domeRef.current.rotation.set(.30 + scroll * .10, -.48 + scroll * .6 + Math.sin(time * .1) * .025, 0);
    }
    if (planetRef.current) {
      planetRef.current.visible = mix < .9;
      // Screen-anchored so the orbiting camera never sweeps it across the instrument;
      // in the chapter it settles beside the heading as a small moon.
      const moon = MathUtils.smoothstep(reveal, .35, .9);
      cameraRight.set(1, 0, 0).applyQuaternion(state.camera.quaternion);
      cameraBack.set(0, 0, -1).applyQuaternion(state.camera.quaternion).multiplyScalar(4);
      planetRef.current.position.copy(cameraBack)
        .addScaledVector(cameraRight, viewport.width * MathUtils.lerp(.31, .38, moon))
        .addScaledVector(cameraUp, viewport.height * MathUtils.lerp(desktop ? .30 : .015, .31, moon) + Math.sin(time * .14) * .05);
      planetRef.current.rotation.set(.4 + Math.sin(time * .21) * .05, .15 + time * .015, -.38 + Math.sin(time * .17) * .04);
      planetRef.current.scale.setScalar((desktop ? Math.min(viewport.width * .45, viewport.height * .7) : viewport.width) * .072 * MathUtils.lerp(1, .78, moon));
      planet.update(time);
    }
    if (stageRect && mix > .99) {
      state.camera.updateMatrixWorld();
      instrumentRefs.current[caseIndex]?.updateWorldMatrix(true, true);
      caseFiles[caseIndex].components.forEach(item => {
        const line = document.querySelector<SVGLineElement>(`[data-hotspot-line="${item.id}"]`);
        if (!line || !anchor(views[caseIndex].view, item, projected)) return;
        projected.project(state.camera);
        line.setAttribute('x2', String((projected.x + 1) * size.width / 2 - stageLeft));
        line.setAttribute('y2', String((1 - projected.y) * size.height / 2 - stageRect.top));
      });
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
