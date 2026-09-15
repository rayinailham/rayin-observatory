'use client';

import { Component, Suspense, useEffect, useMemo, useRef, type ReactNode, type MutableRefObject } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Center, Environment, Lightformer, useGLTF } from '@react-three/drei';
import { Group, MathUtils, Mesh, MeshStandardMaterial, Vector3 } from 'three';
import { instruments, type ChapterState } from '@/lib/instruments';

useGLTF.setDecoderPath('/draco/');

type SceneProps = {
  entered: boolean;
  progress: MutableRefObject<number>;
  chapter: MutableRefObject<ChapterState>;
  onReady: () => void;
  onFailure: () => void;
};

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
  const views = useMemo(() => models.map(model => {
    const view = model.scene.clone(true);
    const materials: MeshStandardMaterial[] = [];
    const lenses: MeshStandardMaterial[] = [];
    view.traverse(object => {
      if (!(object instanceof Mesh)) return;
      const clone = (source: MeshStandardMaterial) => {
        const material = source.clone();
        material.roughness = Math.max(material.roughness, .5);
        material.metalness = Math.min(material.metalness, .55);
        materials.push(material);
        if (/^Lens[123]Glow$/.test(material.name)) {
          material.emissive.set('#F2A541');
          lenses[Number(material.name[4]) - 1] = material;
        }
        return material;
      };
      object.material = Array.isArray(object.material) ? object.material.map(clone) : clone(object.material);
    });
    return { view, materials, lenses, pivot: view.getObjectByName('OpticsPivot'),
      dishes: [0, 1, 2, 3].map(i => view.getObjectByName(`DishPivot${i}`)),
      needle: view.getObjectByName('NeedlePivot'), paper: view.getObjectByName('PaperFeed'),
      rollers: [0, 1].map(i => view.getObjectByName(`RollerPivot${i}`)),
      rings: [0, 1, 2].map(i => view.getObjectByName(`OrbitPivot${i}`)),
      prism: view.getObjectByName('PrismPivot'), spectrum: view.getObjectByName('SpectrumPivot'),
    };
  }), [models]);
  useEffect(() => () => views.forEach(item => item.materials.forEach(material => material.dispose())), [views]);
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
  const starsRef = useRef<Group>(null);
  const revealed = useRef(0);
  const { viewport } = useThree();
  const frames = useRef(0);
  const cameraUp = useMemo(() => new Vector3(), []);
  const cameraRight = useMemo(() => new Vector3(), []);
  const cameraBack = useMemo(() => new Vector3(), []);
  const starPositions = useMemo(() => {
    const points = new Float32Array(210 * 3);
    // Deterministic sky; these are decoration, never presented as astronomy data.
    let seed = 71;
    const random = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
    for (let i = 0; i < points.length; i += 3) {
      points[i] = (random() - .5) * 18;
      points[i + 1] = (random() - .5) * 25;
      points[i + 2] = -6 - random() * 6;
    }
    return points;
  }, []);

  useFrame((state, delta) => {
    if (++frames.current === 2) onReady();
    const step = Math.min(delta, 0.05);
    revealed.current = MathUtils.damp(revealed.current, entered ? 1 : 0, 2.2, step);
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
      if (!group.visible) return;
      if (moving.pivot) moving.pivot.rotation.x = Math.sin(time * .65) * .022;
      moving.lenses.forEach((material, j) => {
        const wave = Math.max(0, Math.cos(time * 1.4 - j * Math.PI * 2 / 3));
        material.emissiveIntensity = .06 + wave ** 6 * 1.5;
      });
      moving.dishes.forEach((dish, j) => { if (dish) dish.rotation.y = Math.sin(time * .55 - j * .65) * .22; });
      moving.materials.forEach(material => {
        if (material.name === 'surgeline signal') material.emissiveIntensity = .25 + Math.max(0, Math.sin(time * 2)) ** 8 * 2;
        if (material.name === 'driftwatch alarm') material.emissiveIntensity = .3 + Math.max(0, Math.sin(time * .8)) ** 24 * 2;
      });
      if (moving.needle) moving.needle.rotation.z = Math.sin(time * 19) * .018 + Math.max(0, Math.sin(time * .8)) ** 24 * .12;
      if (moving.paper) moving.paper.position.z = Math.sin(time * .45) * .08;
      moving.rollers.forEach(roller => { if (roller) roller.rotation.x = time * .3; });
      moving.rings.forEach((ring, j) => { if (ring) ring.rotation.y = time * [.13, -.2, .28][j]; });
      if (moving.prism) moving.prism.rotation.y = time * .16;
      if (moving.spectrum) moving.spectrum.rotation.y = Math.sin(time * .5) * .06;
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
      planetRef.current.rotation.set(.4, .15 + time * .015, -.38);
      planetRef.current.scale.setScalar(viewport.width * .065 * MathUtils.lerp(1, .78, moon));
    }
    if (starsRef.current) starsRef.current.rotation.z = Math.sin(time * .018) * .035;
  });

  return <>
    <ambientLight intensity={.6} />
    <directionalLight position={[3, 6, 5]} intensity={.65} color="#cadcff" />
    <directionalLight position={[-4, 1, 3]} intensity={.55} color="#F2A541" />
    <directionalLight position={[0, 4, -4]} intensity={.9} color="#a1b6e7" />
    <Environment resolution={128} frames={1}>
      <Lightformer intensity={2} color="#cadcff" position={[0, 5, -5]} scale={[10, 5, 1]} />
      <Lightformer intensity={1.3} color="#F2A541" position={[-5, 1, 2]} rotation={[0, Math.PI / 2, 0]} scale={[4, 8, 1]} />
      <Lightformer intensity={1.8} color="#a1b6e7" position={[5, 3, 1]} rotation={[0, -Math.PI / 2, 0]} scale={[5, 7, 1]} />
    </Environment>
    <group ref={starsRef}>
      <points>
        <bufferGeometry><bufferAttribute attach="attributes-position" args={[starPositions, 3]} /></bufferGeometry>
        <pointsMaterial color="#A5AEC2" size={.018} transparent opacity={.65} sizeAttenuation />
      </points>
    </group>
    <group ref={planetRef}><primitive object={ambient.scene} /></group>
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
