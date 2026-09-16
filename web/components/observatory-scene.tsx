'use client';

import { Component, Suspense, useEffect, useLayoutEffect, useMemo, useRef, type ReactNode, type MutableRefObject } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Center, Environment, Lightformer, useGLTF } from '@react-three/drei';
import { Group, MathUtils, Mesh, MeshStandardMaterial, OrthographicCamera, Vector3, type Material, type Object3D } from 'three';
import { instruments, type ChapterState } from '@/lib/instruments';
import { pointScale, rigInstrument, saturn, type Rig } from './instrument-motion';
import Sky from './sky';
import { buildObservatory } from './observatory-model';
import { buildInstrument, type BuiltInstrument } from './instrument-models';
import PlanetaryJourney from './planetary-journey';
import { caseFiles, type CaseComponent, type CaseView } from '@/lib/cases';

useGLTF.setDecoderPath('/draco/');

type SceneProps = {
  entered: boolean;
  reducedMotion: boolean;
  progress: MutableRefObject<number>;
  planetProgress: MutableRefObject<number>;
  chapter: MutableRefObject<ChapterState>;
  caseView: MutableRefObject<CaseView>;
  /** Request the five instrument models; the shell sets it once the hero and fonts are ready. */
  loadInstruments: boolean;
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

type InstrumentView = { view: Object3D; materials: MeshStandardMaterial[]; built: BuiltInstrument; rig: Rig };

// The five instruments are built behind the hero, from the same construction kit as the
// observatory: Enter waits only for the dome, Saturn and fonts. Until the shell asks for
// them `views` stays empty, so chapters and cases briefly show no model.
function Instruments({ viewsRef, groupsRef, onInstrumentTap }: {
  viewsRef: MutableRefObject<InstrumentView[]>;
  groupsRef: MutableRefObject<(Group | null)[]>;
  onInstrumentTap: (index: number) => void;
}) {
  const loaded = useMemo(() => instruments.map(item => {
    const built = buildInstrument(item.id);
    return { view: built.object, materials: built.materials, built, rig: rigInstrument(item.id, built.object, built.materials, showObserver) };
  }), []);
  // Layout effect: World's frame loop must see the views before these groups render once.
  useLayoutEffect(() => {
    viewsRef.current = loaded;
    return () => {
      viewsRef.current = [];
      loaded.forEach(item => {
        item.rig.dispose();
        item.built.dispose();
      });
    };
  }, [loaded, viewsRef]);
  useEffect(() => {
    const brandwall = loaded[instruments.findIndex(item => item.id === 'brandwall')];
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
  }, [loaded, onInstrumentTap]);
  // Hidden until World's frame loop places them, so they never flash at the origin.
  return <>{loaded.map((item, i) => <group key={instruments[i].id} visible={false} ref={group => { groupsRef.current[i] = group; }}><Center><primitive object={item.view} /></Center></group>)}</>;
}

function World({ entered, reducedMotion, progress, planetProgress, chapter, caseView, loadInstruments, onReady, onInstrumentTap }: SceneProps) {
  // The dome is procedural; only Saturn's source model is needed before entering.
  const ambient = useGLTF('/models/ambient.glb');
  const views = useRef<InstrumentView[]>([]);
  const planet = useMemo(() => saturn(ambient.scene), [ambient.scene]);
  useEffect(() => () => planet.dispose(), [planet]);
  const observatory = useMemo(() => buildObservatory(), []);
  useEffect(() => () => observatory.dispose(), [observatory]);
  const heroScroll = useRef(0);
  const cameraAngle = useRef(0);
  const domeRef = useRef<Group>(null);
  const instrumentRefs = useRef<(Group | null)[]>([]);
  const revealed = useRef(0);
  const { size } = useThree();
  const viewport = { width: size.width / 100, height: size.height / 100 };
  const desktop = size.width >= 1024;
  const casePosition = useRef(0);
  const projected = useMemo(() => new Vector3(), []);
  const frames = useRef(0);
  const cameraUp = useMemo(() => new Vector3(), []);
  const cameraRight = useMemo(() => new Vector3(), []);

  useFrame((state, delta) => {
    if (++frames.current === 2) onReady();
    const step = Math.min(delta, 0.05);
    revealed.current = MathUtils.damp(revealed.current, entered ? 1 : 0, 2.2, step);
    pointScale.value = state.gl.getPixelRatio();
    const time = reducedMotion ? 0 : state.clock.elapsedTime;
    heroScroll.current = MathUtils.damp(heroScroll.current, progress.current, 6, step);
    const scroll = reducedMotion ? 0 : heroScroll.current;
    const reveal = chapter.current.reveal;
    const orbit = chapter.current.orbit;
    const { index, transition, outro, from } = chapter.current;
    const { mix, index: caseIndex } = caseView.current;
    const baseAngle = (index > 0 || from !== undefined) && transition < 1 ? MathUtils.lerp(-.95, .55, transition) : (.55 - orbit * 1.5) * reveal;
    cameraAngle.current = MathUtils.damp(cameraAngle.current, reducedMotion ? .35 : MathUtils.lerp(baseAngle, .55, mix), 9, step);
    const angle = cameraAngle.current;
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
    views.current.forEach((moving, i) => {
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
      const scale = (desktop ? Math.min(viewport.width * .63, viewport.height * .98) : viewport.width * .92) / 5.65 * (0.9 + revealed.current * .1 - scroll * .14);
      domeRef.current.scale.setScalar(scale);
      domeRef.current.position.copy(cameraRight).multiplyScalar(desktop ? viewport.width * MathUtils.lerp(.19, -.14, MathUtils.smootherstep(scroll, .1, 1)) : 0);
      domeRef.current.position.y = -viewport.height * ((desktop ? .10 : .20) - scroll * .06) - (1 - revealed.current) * .45 + reveal * viewport.height * 1.4;
      domeRef.current.rotation.set(.14 + scroll * .10, -.30 + scroll * .65, 0);
      if (domeRef.current.visible) observatory.update(time, scroll);
    }
    const caseModel = views.current[caseIndex];
    if (stageRect && mix > .99 && caseModel) {
      state.camera.updateMatrixWorld();
      instrumentRefs.current[caseIndex]?.updateWorldMatrix(true, true);
      caseFiles[caseIndex].components.forEach(item => {
        const line = document.querySelector<SVGLineElement>(`[data-hotspot-line="${item.id}"]`);
        if (!line || !anchor(caseModel.view, item, projected)) return;
        projected.project(state.camera);
        line.setAttribute('x2', String((projected.x + 1) * size.width / 2 - stageLeft));
        line.setAttribute('y2', String((1 - projected.y) * size.height / 2 - stageRect.top));
      });
    }
  }, -1); // Camera first; screen-anchored decoration reads this frame’s transform.

  return <>
    <Sky progress={progress} chapter={chapter} reducedMotion={reducedMotion} />
    <PlanetaryJourney progress={planetProgress} caseView={caseView} reducedMotion={reducedMotion} saturnRig={planet} />
    <ambientLight intensity={.6} />
    <directionalLight position={[3, 6, 5]} intensity={.65} color="#cadcff" />
    <directionalLight position={[-4, 1, 3]} intensity={.55} color="#F2A541" />
    <directionalLight position={[0, 4, -4]} intensity={.9} color="#a1b6e7" />
    <Environment resolution={128} frames={1}>
      <Lightformer intensity={2} color="#cadcff" position={[0, 5, -5]} scale={[10, 5, 1]} />
      <Lightformer intensity={1.3} color="#F2A541" position={[-5, 1, 2]} rotation={[0, Math.PI / 2, 0]} scale={[4, 8, 1]} />
      <Lightformer intensity={1.8} color="#a1b6e7" position={[5, 3, 1]} rotation={[0, -Math.PI / 2, 0]} scale={[5, 7, 1]} />
    </Environment>
    <group ref={domeRef}><primitive object={observatory.object} /></group>
    {loadInstruments && <Suspense fallback={null}><Instruments viewsRef={views} groupsRef={instrumentRefs} onInstrumentTap={onInstrumentTap} /></Suspense>}
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
