import {
  BoxGeometry, CatmullRomCurve3, CylinderGeometry, Group, LatheGeometry, Matrix4, Mesh,
  MeshStandardMaterial, SphereGeometry, TorusGeometry, TubeGeometry, Vector2, Vector3,
  type BufferGeometry, type Object3D,
} from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import type { InstrumentId } from '@/lib/instruments';

const TAU = Math.PI * 2;
const RIGHT = Math.PI / 2;
const UP = new Vector3(0, 1, 0);
const FORWARD = new Vector3(0, 0, 1);
const at = (x: number, y: number, z: number) => new Vector3(x, y, z);

/** One palette for the whole observatory: silver metal, dark navy structure, restrained
 *  brass, warm amber light and optical glass. Instruments rename these, never restyle them. */
type Spec = { color: string; metalness?: number; roughness?: number; emissive?: string; emissiveIntensity?: number; flat?: boolean };
const FINISHES: Record<string, Spec> = {
  steel: { color: '#91a6bc', metalness: .68, roughness: .33 },
  navy: { color: '#152337', metalness: .55, roughness: .48 },
  panel: { color: '#425368', metalness: .35, roughness: .64 },
  graphite: { color: '#101a2a', metalness: .46, roughness: .68 },
  brass: { color: '#c18c4b', metalness: .72, roughness: .30 },
  trim: { color: '#d0d7da', metalness: .72, roughness: .26 },
  glass: { color: '#081c29', metalness: .90, roughness: .12, emissive: '#397f9c', emissiveIntensity: .28 },
  lamp: { color: '#dc9b5b', metalness: .05, roughness: .42, emissive: '#ffad60', emissiveIntensity: .65 },
  cable: { color: '#1a2436', metalness: .28, roughness: .78 },
};

/** A machine shop: one material per finish, one geometry per part, and a final pass that
 *  bakes every static part into a single mesh per material per moving assembly. */
function shop(names: Record<string, string>, extra: Record<string, Spec> = {}) {
  const geometries = new Set<BufferGeometry>();
  const materials: MeshStandardMaterial[] = [];
  const made = new Map<string, MeshStandardMaterial>();

  const finish = (key: string) => {
    const found = made.get(key);
    if (found) return found;
    const spec = extra[key] ?? FINISHES[key];
    if (!spec) throw new Error(`Unknown instrument finish: ${key}`);
    const material = new MeshStandardMaterial({ color: spec.color, metalness: spec.metalness ?? .5, roughness: spec.roughness ?? .5, flatShading: spec.flat ?? false });
    if (spec.emissive) { material.emissive.set(spec.emissive); material.emissiveIntensity = spec.emissiveIntensity ?? 1; }
    material.name = names[key] ?? key;
    made.set(key, material);
    materials.push(material);
    return material;
  };
  const put = (parent: Object3D, geometry: BufferGeometry, key: string, x = 0, y = 0, z = 0) => {
    geometries.add(geometry);
    const mesh = new Mesh(geometry, finish(key));
    mesh.position.set(x, y, z);
    parent.add(mesh);
    return mesh;
  };

  const box = (parent: Object3D, w: number, h: number, d: number, key: string, x = 0, y = 0, z = 0) =>
    put(parent, new BoxGeometry(w, h, d), key, x, y, z);
  /** Vertical cylinder; pass a bottom radius for a taper, or 3 segments for a prism. */
  const cyl = (parent: Object3D, r: number, h: number, key: string, x = 0, y = 0, z = 0, rBottom = r, segments = 28) =>
    put(parent, new CylinderGeometry(r, rBottom, h, segments), key, x, y, z);
  /** Cylinder laid along X — bearings, rollers, barrels on a horizontal axis. */
  const drum = (parent: Object3D, r: number, length: number, key: string, x = 0, y = 0, z = 0, segments = 24) => {
    const mesh = cyl(parent, r, length, key, x, y, z, r, segments);
    mesh.rotation.z = RIGHT;
    return mesh;
  };
  /** Torus lying flat in the XZ plane — collars, bearing races, orbital tracks. */
  const ring = (parent: Object3D, r: number, tube: number, key: string, x = 0, y = 0, z = 0, segments = 44, minor = 6) => {
    const mesh = put(parent, new TorusGeometry(r, tube, minor, segments), key, x, y, z);
    mesh.rotation.x = RIGHT;
    return mesh;
  };
  /** Torus standing upright in the XY plane — aperture rings, screen frames, hoops. */
  const hoop = (parent: Object3D, r: number, tube: number, key: string, x = 0, y = 0, z = 0, segments = 44, minor = 6) =>
    put(parent, new TorusGeometry(r, tube, minor, segments), key, x, y, z);
  const ball = (parent: Object3D, r: number, key: string, x = 0, y = 0, z = 0, w = 20, h = 14) =>
    put(parent, new SphereGeometry(r, w, h), key, x, y, z);
  /** Round strut between two points: struts, shafts, hand rails. */
  const rod = (parent: Object3D, a: Vector3, b: Vector3, r: number, key: string, segments = 10) => {
    const direction = new Vector3().subVectors(b, a);
    const mesh = put(parent, new CylinderGeometry(r, r, direction.length(), segments), key);
    mesh.position.copy(a).addScaledVector(direction, .5);
    mesh.quaternion.setFromUnitVectors(UP, direction.clone().normalize());
    return mesh;
  };
  /** Rectangular member between two points: brackets, cable trays, light ribbons. */
  const bar = (parent: Object3D, a: Vector3, b: Vector3, w: number, h: number, key: string) => {
    const direction = new Vector3().subVectors(b, a);
    const mesh = put(parent, new BoxGeometry(w, h, direction.length()), key);
    mesh.position.copy(a).addScaledVector(direction, .5);
    mesh.quaternion.setFromUnitVectors(FORWARD, direction.clone().normalize());
    return mesh;
  };
  const lathe = (parent: Object3D, profile: Vector2[], key: string, segments = 36, x = 0, y = 0, z = 0) =>
    put(parent, new LatheGeometry(profile, segments), key, x, y, z);
  /** Routed cable or conduit through a list of way points. */
  const cable = (parent: Object3D, points: Vector3[], r: number, key: string, segments = 16) =>
    put(parent, new TubeGeometry(new CatmullRomCurve3(points), segments, r, 5, false), key);
  const group = (parent: Object3D, name: string, x = 0, y = 0, z = 0) => {
    const child = new Group();
    child.name = name;
    child.position.set(x, y, z);
    parent.add(child);
    return child;
  };
  /** Fasteners around a circle in the XZ plane. */
  const studs = (parent: Object3D, count: number, radius: number, r: number, key: string, y = 0, cx = 0, cz = 0) => {
    for (let i = 0; i < count; i++) {
      const angle = i / count * TAU;
      const stud = ball(parent, r, key, cx + Math.cos(angle) * radius, y, cz + Math.sin(angle) * radius, 6, 4);
      stud.scale.y = .62;
    }
  };
  /** A calibrated scale: evenly spaced marks with a longer one every `major`. */
  const scale = (parent: Object3D, count: number, radius: number, key: string, y: number, major = 5, length = .08) => {
    for (let i = 0; i < count; i++) {
      const angle = i / count * TAU;
      const mark = box(parent, i % major === 0 ? length : length * .55, .012, .018, key,
        Math.cos(angle) * radius, y, Math.sin(angle) * radius);
      mark.rotation.y = -angle;
    }
  };
  /** Knurling, ratchet teeth or gear teeth around a circle in the XZ plane. */
  const teeth = (parent: Object3D, count: number, radius: number, w: number, h: number, d: number, key: string, y = 0, cx = 0, cz = 0) => {
    for (let i = 0; i < count; i++) {
      const angle = i / count * TAU;
      const tooth = box(parent, w, h, d, key, cx + Math.cos(angle) * radius, y, cz + Math.sin(angle) * radius);
      tooth.rotation.y = -angle;
    }
  };
  /** The same, around an axis laid along X: gear rims and knurled collars on a shaft. */
  const teethX = (parent: Object3D, count: number, radius: number, w: number, h: number, d: number, key: string, x = 0, cy = 0, cz = 0) => {
    for (let i = 0; i < count; i++) {
      const angle = i / count * TAU;
      const tooth = box(parent, w, h, d, key, x, cy + Math.cos(angle) * radius, cz + Math.sin(angle) * radius);
      tooth.rotation.x = -angle;
    }
  };

  /** The stepped foundation every instrument shares with the observatory deck. */
  const plinth = (parent: Object3D, radius: number, deck: number) => {
    cyl(parent, radius, .13, 'graphite', 0, .065, 0, radius * 1.02, 48);
    ring(parent, radius * .995, .015, 'lamp', 0, .132, 0, 56);
    cyl(parent, radius * .955, .11, 'navy', 0, .185, 0, radius * .975, 48);
    cyl(parent, radius * .915, .1, 'panel', 0, .29, 0, radius * .94, 48);
    ring(parent, radius * .925, .022, 'brass', 0, .33, 0, 52);
    // A flat plated deck: radial seams, a hub plate and a graduated rim.
    cyl(parent, radius * .88, .08, 'navy', 0, deck - .04, 0, radius * .88, 64);
    for (let i = 0; i < 8; i++) {
      const angle = i / 8 * TAU + .2;
      const seam = box(parent, radius * .80, .014, .022, 'panel', Math.cos(angle) * radius * .43, deck + .002, Math.sin(angle) * radius * .43);
      seam.rotation.y = -angle;
    }
    cyl(parent, radius * .30, .02, 'panel', 0, deck + .008, 0, radius * .30, 48);
    ring(parent, radius * .30, .014, 'trim', 0, deck + .012, 0, 44);
    ring(parent, radius * .885, .014, 'trim', 0, deck, 0, 56);
    scale(parent, 24, radius * .80, 'trim', deck + .006, 4, radius * .07);
    studs(parent, 12, radius * .70, .026, 'trim', deck + .008);
    // Lit service bays around the skirt, as on the observatory drum.
    for (let i = 0; i < 12; i++) {
      const angle = i / 12 * TAU + .26;
      const cx = Math.cos(angle), cz = Math.sin(angle);
      const bay = box(parent, radius * .17, .10, .04, 'navy', cx * radius * .952, .205, cz * radius * .952);
      bay.rotation.y = -angle;
      const lit = box(parent, radius * .13, .062, .03, 'lamp', cx * radius * .968, .205, cz * radius * .968);
      lit.rotation.y = -angle;
    }
    // Service hatches keep the deck from reading as one poured slab.
    for (let i = 0; i < 3; i++) {
      const angle = i / 3 * TAU + .5;
      const cx = Math.cos(angle) * radius * .60, cz = Math.sin(angle) * radius * .60;
      const hatch = box(parent, radius * .26, .022, radius * .15, 'panel', cx, deck + .006, cz);
      hatch.rotation.y = -angle;
      const seam = box(parent, radius * .26, .026, .01, 'trim', cx, deck + .008, cz);
      seam.rotation.y = -angle;
    }
  };

  /** Hundreds of parts become a handful of draws: one mesh per material per assembly.
   *  `assemblies` lists every group that must keep its own merged meshes — the moving
   *  pivots, and the static mount whose material names `cases.ts` anchors leader lines to. */
  const finalize = (root: Group, assemblies: Object3D[]) => {
    const moving = assemblies;
    const pivots = new Set<Object3D>(moving);
    const depth = (object: Object3D) => { let d = 0; for (let p = object.parent; p; p = p.parent) d++; return d; };
    root.updateWorldMatrix(true, true);
    for (const assembly of [...moving].sort((a, b) => depth(b) - depth(a)).concat(root)) {
      const inverse = new Matrix4().copy(assembly.matrixWorld).invert();
      const batches = new Map<MeshStandardMaterial, BufferGeometry[]>();
      const gather = (parent: Object3D) => {
        for (const child of [...parent.children]) {
          if (child instanceof Mesh) {
            const geometry = child.geometry.clone().applyMatrix4(new Matrix4().multiplyMatrices(inverse, child.matrixWorld));
            const material = child.material as MeshStandardMaterial;
            if (!batches.has(material)) batches.set(material, []);
            batches.get(material)!.push(geometry);
            parent.remove(child);
          } else if (!pivots.has(child)) gather(child);
        }
      };
      gather(assembly);
      const merged: Mesh[] = [];
      batches.forEach((parts, material) => {
        const geometry = mergeGeometries(parts);
        parts.forEach(part => part.dispose());
        if (!geometry) throw new Error(`${root.name}: assembly geometry could not be merged`);
        geometries.add(geometry);
        const mesh = new Mesh(geometry, material);
        assembly.add(mesh);
        merged.push(mesh);
      });
      // An assembly's own geometry comes before its nested pivots, so a leader line that
      // looks up a material by name under a mount finds the mount's part, not a child's.
      assembly.children = [...merged, ...assembly.children.filter(child => !merged.includes(child as Mesh))];
    }
    return {
      object: root,
      materials,
      dispose() {
        geometries.forEach(geometry => geometry.dispose());
        materials.forEach(material => material.dispose());
      },
    };
  };

  return { put, box, cyl, drum, ring, hoop, ball, rod, bar, lathe, cable, group, studs, scale, teeth, teethX, plinth, finalize };
}

type Shop = ReturnType<typeof shop>;
export type BuiltInstrument = ReturnType<Shop['finalize']>;

// ---------------------------------------------------------------------------
// CrossCheck — a three-channel telescope. Every channel is a real optical train:
// focuser, draw tube, baffled barrel, a focus collar that turns, and a recessed
// objective. The three channels are trued against each other, not merely bolted on.
// ---------------------------------------------------------------------------

const TILT = 1.144;                         // channel elevation, preserved from the original model
const AXIS = at(0, Math.cos(TILT), Math.sin(TILT));
const LIFT = at(0, -Math.sin(TILT), Math.cos(TILT));
const CHANNELS = [{ side: -.52, rise: -.118 }, { side: .52, rise: -.118 }, { side: 0, rise: -1.009 }];
/** A point on a channel's axis, in optics-pivot space. */
const seat = (index: number, along: number) =>
  at(CHANNELS[index].side, 0, 0).addScaledVector(LIFT, CHANNELS[index].rise).addScaledVector(AXIS, along);

function channel(s: Shop, optics: Group, index: number) {
  const { side, rise } = CHANNELS[index];
  const tube = s.group(optics, `Channel${index}`, side, -rise * Math.sin(TILT), rise * Math.cos(TILT));
  tube.rotation.x = TILT;
  const lens = `Lens${index + 1}Glow`;
  // Main tube with two raised stiffening bands, a lit service strip and their fasteners.
  s.cyl(tube, .41, 1.66, 'steel', 0, .34, 0, .41, 36);
  for (const y of [-.06, .78]) {
    s.ring(tube, .425, .042, 'panel', 0, y, 0, 40);
    s.studs(tube, 8, .425, .024, 'trim', y + .043);
  }
  s.ring(tube, .418, .016, 'trim', 0, .36, 0, 40);
  for (const y of [.14, .34, .54]) s.box(tube, .05, .022, .03, 'lamp', 0, y, .425);
  // Aperture: a stepped hood, a brass ring and an objective recessed behind three baffles.
  s.cyl(tube, .43, .18, 'steel', 0, 1.26, 0, .415, 36);
  s.ring(tube, .422, .034, 'brass', 0, 1.32, 0, 40);
  s.ring(tube, .374, .016, 'trim', 0, 1.27, 0, 36);
  for (const y of [1.10, .98, .86]) s.ring(tube, .372, .013, 'graphite', 0, y, 0, 32);
  const objective = s.ball(tube, .362, lens, 0, 1.17, 0, 36, 22);
  objective.scale.y = .62;
  s.ring(tube, .368, .022, 'brass', 0, 1.20, 0, 36);
  s.cyl(tube, .38, .12, 'graphite', 0, 1.115, 0, .38, 32);
  // Focus collar: knurled, and it genuinely turns about the optical axis.
  const focus = s.group(tube, `FocusPivot${index}`, 0, .40, 0);
  s.ring(focus, .48, .058, 'brass', 0, 0, 0, 40);
  s.teeth(focus, 20, .525, .028, .10, .05, 'brass');
  s.box(focus, .07, .05, .16, 'trim', .53, .07, 0);
  // Rear focuser: draw tube, rack housing, a pinion knob and a status lamp.
  s.cyl(tube, .36, .22, 'navy', 0, -.56, 0, .30, 28);
  s.box(tube, .50, .30, .40, 'graphite', 0, -.74, 0);
  s.box(tube, .54, .06, .44, 'panel', 0, -.60, 0);
  s.drum(tube, .11, .11, 'brass', .32, -.74, 0, 16);
  s.rod(tube, at(.24, -.74, 0), at(.40, -.74, 0), .028, 'trim');
  s.teethX(tube, 14, .12, .07, .025, .025, 'brass', .32, -.74, 0);
  s.box(tube, .16, .035, .18, 'lamp', 0, -.90, 0);
  // Channel plate and the alignment target the crew sights along.
  s.box(tube, .20, .015, .09, 'trim', 0, .462, .455);
  s.box(tube, .05, .012, .05, 'brass', 0, .462, .49);
  // The anchor the case file's leader line ends on: the objective's front face.
  s.group(tube, `Lens${index + 1}`, 0, 1.31, 0);
  s.box(tube, .07, .015, .03, 'lamp', 0, 1.20, .40);
  return focus;
}

function buildCrossCheck(): BuiltInstrument {
  const s = shop({
    steel: 'Brushed steel', navy: 'Navy enamel', panel: 'Raised navy panels', graphite: 'Recess graphite',
    brass: 'Satin amber metal', trim: 'Polished trim', glass: 'Optical glass', lamp: 'Amber light',
    cable: 'Service loom',
  }, {
    Lens1Glow: { color: '#07202e', metalness: .52, roughness: .14, emissive: '#F2A541', emissiveIntensity: .05 },
    Lens2Glow: { color: '#07202e', metalness: .52, roughness: .14, emissive: '#F2A541', emissiveIntensity: .05 },
    Lens3Glow: { color: '#07202e', metalness: .52, roughness: .14, emissive: '#F2A541', emissiveIntensity: .05 },
  });
  const object = new Group();
  object.name = 'CrossCheck';
  const base = s.group(object, 'CrossCheckMount');
  s.plinth(base, 1.52, .34);

  // Azimuth drum: bearing race, ring gear and the drive that turns it.
  s.cyl(base, .70, .30, 'navy', 0, .49, 0, .78, 36);
  s.ring(base, .74, .045, 'brass', 0, .63, 0, 44);
  s.cyl(base, .64, .26, 'graphite', 0, .79, 0, .68, 36);
  s.teeth(base, 44, .70, .034, .07, .05, 'brass', .79);
  s.cyl(base, .60, .12, 'steel', 0, .96, 0, .62, 36);
  s.ring(base, .58, .018, 'trim', 0, 1.02, 0, 40);
  s.studs(base, 10, .54, .03, 'trim', 1.03);
  const motor = s.group(base, 'AzimuthDrive', .92, .79, .28);
  motor.rotation.y = -.30;
  s.drum(motor, .17, .34, 'graphite', 0, 0, 0, 20);
  for (const x of [-.11, -.03, .05]) s.drum(motor, .195, .02, 'navy', x, 0, 0, 20);
  s.box(motor, .1, .14, .14, 'navy', .22, 0, 0);
  s.box(motor, .06, .03, .09, 'lamp', .27, .04, 0);
  s.drum(motor, .07, .30, 'brass', -.30, 0, 0, 14);
  s.box(base, .28, .48, .24, 'navy', .92, .55, .28);
  s.cable(base, [at(1.02, .70, .40), at(1.10, .48, .50), at(1.0, .38, .62), at(.55, .38, .80)], .02, 'cable');

  // Fork arms carrying the altitude bearings at the optics-pivot height.
  for (const side of [-1, 1]) {
    const arm = s.group(base, side > 0 ? 'ForkRight' : 'ForkLeft', side * .62, 0, 0);
    s.box(arm, .17, 1.36, .52, 'steel', 0, 1.63, 0);
    s.box(arm, .19, .18, .58, 'navy', 0, 1.00, 0);
    s.box(arm, .19, .18, .58, 'navy', 0, 2.16, 0);
    s.box(arm, .09, .78, .26, 'graphite', side * .06, 1.60, 0);
    for (const z of [-.14, .14]) s.drum(arm, .085, .1, 'graphite', 0, 1.60, z, 14);
    s.drum(arm, .27, .14, 'brass', 0, 2.30, 0, 28);
    s.drum(arm, .17, .18, 'trim', side * .04, 2.30, 0, 20);
    s.teethX(arm, 6, .21, .05, .05, .05, 'trim', side * .02, 2.30, 0);
    s.cable(arm, [at(side * .05, .42, .30), at(side * .13, 1.1, .34), at(side * .05, 1.9, .26), at(0, 2.26, .12)], .019, 'cable');
  }

  const optics = s.group(object, 'OpticsPivot', 0, 2.30, 0);
  // Saddle plate: the cradle the three channels bolt to.
  const saddle = s.group(optics, 'Saddle');
  saddle.rotation.x = TILT;
  s.box(saddle, 1.64, .12, .30, 'steel', 0, .05, .30);
  s.box(saddle, 1.70, .05, .34, 'panel', 0, .12, .30);
  s.box(saddle, .34, .22, .30, 'navy', 0, .05, -.52);
  s.studs(saddle, 8, .70, .03, 'trim', .13);
  const collars = [0, 1, 2].map(index => channel(s, optics, index));
  // Alignment braces: the three channels are trued against each other.
  for (const along of [.16, 1.02]) {
    s.rod(optics, seat(0, along), seat(1, along), .035, 'trim');
    s.rod(optics, seat(0, along), seat(2, along), .035, 'trim');
    s.rod(optics, seat(1, along), seat(2, along), .035, 'trim');
  }
  // Junction box and service loom: the cabling that makes three channels one instrument.
  const junction = s.group(optics, 'Junction');
  junction.rotation.x = TILT;
  s.box(junction, .46, .24, .26, 'graphite', 0, -.30, -.30);
  s.box(junction, .40, .04, .05, 'lamp', 0, -.18, -.30);
  s.box(junction, .48, .05, .28, 'panel', 0, -.42, -.30);
  for (const index of [0, 1, 2]) {
    const tail = seat(index, -.62).addScaledVector(LIFT, .10);
    s.cable(optics, [tail, tail.clone().addScaledVector(AXIS, -.28).addScaledVector(LIFT, .18),
      seat(1, -.26).addScaledVector(LIFT, .36), seat(1, -.32).addScaledVector(LIFT, .30)], .022, 'cable', 14);
  }
  // Counterweight shaft keeps the tilted cluster balanced over the altitude bearings.
  s.rod(optics, seat(1, -.40).setX(0), seat(1, -1.28).setX(0), .055, 'trim');
  for (const along of [-.84, -1.10]) {
    const point = at(0, 0, 0).addScaledVector(AXIS, along);
    const weight = s.cyl(optics, .26, .16, 'navy', point.x, point.y, point.z, .26, 24);
    weight.quaternion.setFromUnitVectors(UP, AXIS);
    const collar = s.ring(optics, .275, .022, 'brass', point.x, point.y, point.z, 28);
    collar.quaternion.setFromUnitVectors(UP, AXIS);
    collar.rotateX(RIGHT);
  }
  return s.finalize(object, [base, optics, ...collars]);
}

// ---------------------------------------------------------------------------
// SurgeLine — four steerable dishes on a shared base. Each dish is a shaped
// reflector with rear ribs, a feed horn on struts, trunnion bearings and a drive.
// ---------------------------------------------------------------------------

const DISH_SEATS = [
  { x: -.95, y: 1.4, z: -.25 }, { x: 0, y: 1.8, z: -.65 },
  { x: .95, y: 1.4, z: -.25 }, { x: 0, y: 1.2, z: .8 },
];
const RIM = .56, FOCUS = .30, SHELL = .045;
const DEPTH = RIM * RIM / (4 * FOCUS);

function dish(s: Shop, pivot: Group) {
  // A true parabolic shell with a rolled rim, not a disc: r² = 4fz.
  const profile: Vector2[] = [];
  const sweep = (offset: number, inward: boolean) => {
    for (let i = 0; i <= 9; i++) {
      const r = RIM * (inward ? 1 - i / 9 : i / 9);
      profile.push(new Vector2(r, r * r / (4 * FOCUS) + offset));
    }
  };
  sweep(0, false);
  profile.push(new Vector2(RIM + .032, DEPTH + .014), new Vector2(RIM + .032, DEPTH - .05));
  sweep(-SHELL, true);
  const shell = s.lathe(pivot, profile, 'ceramic', 36, 0, 0, .10);
  shell.rotation.x = RIGHT;
  s.hoop(pivot, RIM + .034, .022, 'brass', 0, 0, .10 + DEPTH, 40);
  // Panel seams: a real reflector is assembled from segments.
  for (let i = 0; i < 8; i++) {
    const angle = i / 8 * TAU + .2;
    const seam = s.box(pivot, .014, RIM * .92, .02, 'brass', Math.cos(angle) * RIM * .5, Math.sin(angle) * RIM * .5, .10 + RIM * RIM * .25 / (4 * FOCUS) + .012);
    seam.rotation.z = -angle + RIGHT;
  }
  s.hoop(pivot, RIM * .58, .009, 'brass', 0, 0, .10 + (RIM * .58) ** 2 / (4 * FOCUS) + .012, 40);
  // Rear ribs and a hoop: the reflector is stiffened, not a floating shell.
  for (let i = 0; i < 8; i++) {
    const angle = i / 8 * TAU;
    const rib = s.box(pivot, .034, .19, .26, 'steel', Math.cos(angle) * .33, Math.sin(angle) * .33, -.06);
    rib.rotation.z = -angle + RIGHT;
  }
  s.hoop(pivot, .36, .022, 'steel', 0, 0, -.02, 36);
  s.cyl(pivot, .17, .20, 'panel', 0, 0, -.11, .20, 20).rotation.x = RIGHT;
  // Feed horn at the focus on three struts, with its waveguide run back through the hub.
  for (let i = 0; i < 3; i++) {
    const angle = i / 3 * TAU + .5;
    s.rod(pivot, at(Math.cos(angle) * (RIM - .05), Math.sin(angle) * (RIM - .05), .10 + DEPTH - .02), at(0, 0, .40), .022, 'trim', 8);
  }
  s.cyl(pivot, .13, .20, 'signal', 0, 0, .40, .055, 20).rotation.x = -RIGHT;
  s.hoop(pivot, .135, .018, 'brass', 0, 0, .49, 24);
  s.cyl(pivot, .05, .40, 'brass', 0, 0, .22, .05, 14).rotation.x = RIGHT;
  // Receiver box behind the dish, its connectors and a service loop down to the yoke.
  s.box(pivot, .34, .26, .22, 'panel', 0, 0, -.26);
  s.box(pivot, .30, .22, .03, 'navy', 0, 0, -.375);
  s.box(pivot, .24, .05, .03, 'lamp', 0, .07, -.39);
  for (const x of [-.09, .09]) s.cyl(pivot, .035, .07, 'trim', x, -.06, -.40, .035, 10).rotation.x = RIGHT;
  s.cable(pivot, [at(.09, -.09, -.40), at(.18, -.24, -.40), at(.10, -.34, -.24), at(0, -.30, -.08)], .018, 'cable', 14);
  // Elevation trunnions and the yoke that carries them.
  for (const side of [-1, 1]) {
    s.drum(pivot, .115, .12, 'brass', side * .30, 0, -.02, 20);
    s.drum(pivot, .06, .10, 'trim', side * .34, 0, -.02, 12);
    s.rod(pivot, at(side * .30, 0, -.02), at(side * .19, -.33, -.06), .045, 'steel');
  }
  s.box(pivot, .40, .12, .20, 'steel', 0, -.36, -.06);
  s.cyl(pivot, .17, .12, 'navy', 0, -.44, -.06, .20, 20);
  s.box(pivot, .12, .02, .05, 'lamp', 0, -.36, .05);
}

function buildSurgeLine(): BuiltInstrument {
  const s = shop({
    steel: 'surgeline steel', navy: 'surgeline casing', panel: 'surgeline panel', graphite: 'surgeline graphite',
    brass: 'surgeline brass', trim: 'surgeline trim', glass: 'surgeline glass', lamp: 'surgeline lamp',
    ceramic: 'surgeline ceramic', cable: 'surgeline cable', signal: 'surgeline signal',
  }, {
    ceramic: { color: '#aebccd', metalness: .34, roughness: .46 },
    signal: { color: '#e8bd7a', metalness: .2, roughness: .35, emissive: '#F2A541', emissiveIntensity: .3 },
  });
  const object = new Group();
  object.name = 'SurgeLine';
  const base = s.group(object, 'surgelineMount');
  s.plinth(base, 1.75, .34);

  // Central equipment island: the work list every dish draws from.
  s.cyl(base, .62, .30, 'navy', 0, .49, 0, .70, 6);
  s.cyl(base, .58, .06, 'panel', 0, .67, 0, .58, 6);
  s.ring(base, .60, .02, 'brass', 0, .69, 0, 36);
  for (let i = 0; i < 6; i++) {
    const angle = i / 6 * TAU + .52;
    const cx = Math.cos(angle), cz = Math.sin(angle);
    const face = s.box(base, .46, .18, .05, 'graphite', cx * .58, .50, cz * .58);
    face.rotation.y = -angle;
    const lit = s.box(base, .34, .09, .03, 'lamp', cx * .60, .50, cz * .60);
    lit.rotation.y = -angle;
    for (const step of [-.16, 0, .16]) {
      const louvre = s.box(base, .11, .016, .04, 'trim', cx * .58 - cz * step, .63, cz * .58 + cx * step);
      louvre.rotation.y = -angle;
    }
  }

  const pivots = DISH_SEATS.map((mounting, index) => {
    // Tower, azimuth housing and drive live on the static deck; the dish turns above them.
    const tower = s.group(base, `Tower${index}`, mounting.x, 0, mounting.z);
    const height = mounting.y - .62;
    s.cyl(tower, .21, height, 'navy', 0, .34 + height / 2, 0, .27, 24);
    s.box(tower, .44, .05, .44, 'panel', 0, .37, 0);
    s.studs(tower, 6, .20, .026, 'trim', .40);
    for (const step of [.25, .55, .85]) s.ring(tower, .225, .018, 'brass', 0, .40 + height * step, 0, 28);
    s.cyl(tower, .26, .24, 'graphite', 0, mounting.y - .50, 0, .30, 28);
    s.ring(tower, .285, .034, 'brass', 0, mounting.y - .40, 0, 32);
    s.cyl(tower, .23, .12, 'steel', 0, mounting.y - .30, 0, .25, 28);
    s.studs(tower, 8, .20, .024, 'trim', mounting.y - .245);
    s.drum(tower, .10, .22, 'graphite', .29, mounting.y - .52, .06, 16);
    s.box(tower, .07, .11, .11, 'navy', .41, mounting.y - .52, .06);
    s.box(tower, .04, .03, .07, 'lamp', .45, mounting.y - .49, .06);
    s.cable(tower, [at(.30, mounting.y - .62, .10), at(.34, mounting.y - .90, .16), at(.24, .70, .20), at(.06, .40, .22)], .018, 'cable', 14);
    const pivot = s.group(base, `DishPivot${index}`, mounting.x, mounting.y, mounting.z);
    dish(s, pivot);
    return pivot;
  });

  // Cable trays run from each tower back to the island: four dishes, one system.
  for (const mounting of DISH_SEATS) {
    const angle = Math.atan2(mounting.z, mounting.x);
    s.bar(base, at(Math.cos(angle) * .64, .37, Math.sin(angle) * .64), at(mounting.x, .37, mounting.z), .18, .05, 'graphite');
    s.bar(base, at(Math.cos(angle) * .64, .40, Math.sin(angle) * .64), at(mounting.x, .40, mounting.z), .06, .03, 'brass');
  }
  return s.finalize(object, [base, ...pivots]);
}

// ---------------------------------------------------------------------------
// DriftWatch — a chart recorder. The paper really runs over its rollers, the pen
// rides an articulated arm, and the rig draws the live trace on the platen.
// ---------------------------------------------------------------------------

const PAPER_Y = .95, ROLLER_R = .16, ROLLER_Y = PAPER_Y - ROLLER_R;
const ROLLERS = [{ index: 0, z: 1.06 }, { index: 1, z: -.88 }];

function buildDriftWatch(): BuiltInstrument {
  const s = shop({
    steel: 'driftwatch steel', navy: 'driftwatch casing', panel: 'driftwatch panel', graphite: 'driftwatch graphite',
    brass: 'driftwatch brass', trim: 'driftwatch trim', glass: 'driftwatch glass', lamp: 'driftwatch lamp',
    ceramic: 'driftwatch ceramic', cable: 'driftwatch cable', paper: 'driftwatch paper', alarm: 'driftwatch alarm',
  }, {
    ceramic: { color: '#d3dae2', metalness: .04, roughness: .88 },
    paper: { color: '#d3dae2', metalness: .04, roughness: .88 },
    alarm: { color: '#ff7a7e', metalness: .1, roughness: .38, emissive: '#FF5A5F', emissiveIntensity: .4 },
  });
  const object = new Group();
  object.name = 'DriftWatch';
  const base = s.group(object, 'driftwatchMount');
  s.plinth(base, 1.75, .34);

  // Machined chassis: inset side panels, louvres, a lit inspection window and a control strip.
  s.box(base, 2.34, .46, 1.86, 'navy', 0, .57, 0);
  s.box(base, 2.40, .06, 1.92, 'panel', 0, .83, 0);
  s.box(base, 2.26, .10, 1.78, 'graphite', 0, .36, 0);
  for (const side of [-1, 1]) {
    s.box(base, .04, .28, 1.50, 'graphite', side * 1.17, .56, 0);
    for (const z of [-.56, -.19, .19, .56]) s.box(base, .03, .16, .26, 'panel', side * 1.19, .56, z);
    for (const z of [-1.06, 1.06]) s.box(base, .12, .52, .16, 'navy', side * 1.13, .58, z);
  }
  s.box(base, 1.90, .28, .04, 'graphite', 0, .56, .94);
  s.box(base, .86, .22, .05, 'glass', -.42, .57, .97);
  s.box(base, .78, .14, .02, 'lamp', -.42, .57, .955);
  s.box(base, .70, .20, .05, 'graphite', .52, .57, .97);
  for (const x of [.28, .46, .64, .82]) s.box(base, .08, .05, .03, 'lamp', x, .62, .99);
  for (const x of [.32, .58]) s.cyl(base, .07, .06, 'brass', x, .50, .99, .07, 16).rotation.x = RIGHT;
  s.box(base, 1.90, .06, .05, 'trim', 0, .72, .955);
  s.studs(base, 8, .86, .028, 'trim', .87);

  // Platen and paper path: supply drum, tension guides, chart bed, drive roller, take-up slot.
  s.box(base, 2.06, .10, 1.72, 'steel', 0, .87, .09);
  s.box(base, 2.10, .04, 1.76, 'panel', 0, .93, .09);
  s.box(base, 1.96, .012, 1.70, 'paper', 0, PAPER_Y - .014, .09);
  // The one `ceramic` mesh on the chassis: the chart the leader line for change detection ends on.
  s.box(base, 1.90, .014, 1.66, 'ceramic', 0, PAPER_Y - .004, .09);
  // Calibrated amplitude scale down both edges, and three light grid rules across it.
  for (let i = 0; i <= 18; i++) {
    const z = .97 - i / 18 * 1.74;
    for (const side of [-1, 1]) s.box(base, i % 3 === 0 ? .13 : .07, .016, .012, 'brass', side * .90, PAPER_Y + .003, z);
  }
  for (const x of [-.62, 0, .62]) s.box(base, .008, .016, 1.70, 'brass', x, PAPER_Y + .002, .10);
  // Paper tails leaving the bed: the sheet comes from somewhere and goes somewhere.
  s.box(base, 1.90, .014, .16, 'paper', 0, PAPER_Y - .004, .99);
  s.box(base, 1.90, .014, .16, 'paper', 0, PAPER_Y - .004, -.81);
  const feedTail = s.box(base, 1.88, .012, .36, 'paper', 0, ROLLER_Y - .06, 1.32);
  feedTail.rotation.x = -.92;
  const takeTail = s.box(base, 1.88, .012, .32, 'paper', 0, ROLLER_Y - .10, -1.08);
  takeTail.rotation.x = .96;
  s.box(base, 2.02, .07, .16, 'graphite', 0, ROLLER_Y - .24, -1.14);
  s.box(base, 1.94, .02, .04, 'trim', 0, ROLLER_Y - .20, -1.14);
  // Tension guides on real end bearings.
  for (const z of [.62, -.42]) {
    s.drum(base, .045, 1.98, 'trim', 0, PAPER_Y + .055, z, 14);
    for (const side of [-1, 1]) {
      s.drum(base, .085, .09, 'brass', side * 1.0, PAPER_Y + .055, z, 16);
      s.box(base, .06, .26, .10, 'steel', side * 1.02, PAPER_Y - .05, z);
    }
  }
  // Roller carriers, and the motor and gear train that drive the paper.
  for (const { index, z } of ROLLERS) {
    for (const side of [-1, 1]) {
      s.box(base, .10, .34, .26, 'steel', side * 1.02, ROLLER_Y - .06, z);
      s.drum(base, .105, .07, 'brass', side * 1.03, ROLLER_Y, z, 18);
    }
    if (index !== 1) continue;
    s.box(base, .24, .30, .30, 'graphite', 1.16, ROLLER_Y - .18, z);
    s.drum(base, .19, .06, 'brass', 1.16, ROLLER_Y - .34, z, 22);
    s.teethX(base, 18, .215, .05, .05, .04, 'brass', 1.16, ROLLER_Y - .34, z);
    s.drum(base, .13, .28, 'graphite', 1.30, ROLLER_Y - .56, z, 18);
    s.box(base, .05, .04, .07, 'lamp', 1.42, ROLLER_Y - .50, z);
    s.cable(base, [at(1.36, ROLLER_Y - .68, z), at(1.30, .60, z - .28), at(.90, .44, -1.0), at(.20, .42, -1.08)], .02, 'cable', 14);
  }

  // Gantry carrying the pen arm's bearing, braced back to the chassis.
  for (const side of [-1, 1]) {
    s.box(base, .14, 1.42, .22, 'steel', side * 1.05, 1.60, -.48);
    s.box(base, .17, .10, .28, 'navy', side * 1.05, .94, -.48);
    s.rod(base, at(side * 1.05, 1.24, -.44), at(side * 1.05, .98, .16), .034, 'trim');
    s.studs(base, 4, .09, .024, 'trim', .99, side * 1.05, -.48);
  }
  s.box(base, 2.28, .16, .20, 'steel', 0, 2.30, -.48);
  s.box(base, 2.32, .05, .24, 'panel', 0, 2.39, -.48);
  s.box(base, .52, .22, .26, 'navy', 0, 2.20, -.48);
  s.box(base, .34, .04, .05, 'lamp', 0, 2.31, -.36);
  s.drum(base, .19, .40, 'brass', 0, 2.20, -.48, 24);

  // The pen arm: bearing hub, counterweight, two links with a visible elbow, and the tip.
  const needle = s.group(base, 'NeedlePivot', 0, 2.20, -.48);
  s.drum(needle, .13, .30, 'trim', 0, 0, 0, 20);
  s.drum(needle, .07, .34, 'brass', 0, 0, 0, 16);
  s.rod(needle, at(0, .05, 0), at(-.05, .44, -.29), .046, 'trim');
  s.drum(needle, .145, .10, 'navy', -.05, .44, -.29, 18);
  s.drum(needle, .10, .13, 'brass', -.05, .44, -.29, 16);
  const elbow = at(.06, -.62, .40);
  const tip = at(.12, -1.22, .78);
  s.rod(needle, at(0, -.10, .04), elbow, .052, 'brass');
  for (const side of [-1, 1]) s.box(needle, .03, .17, .17, 'steel', elbow.x + side * .07, elbow.y, elbow.z);
  s.drum(needle, .055, .20, 'trim', elbow.x, elbow.y, elbow.z, 14);
  s.box(needle, .17, .05, .05, 'trim', elbow.x, elbow.y + .09, elbow.z);
  s.rod(needle, elbow, tip.clone().addScaledVector(new Vector3().subVectors(tip, elbow).normalize(), -.09), .034, 'brass');
  s.box(needle, .14, .15, .13, 'graphite', tip.x, tip.y + .11, tip.z - .02);
  s.cyl(needle, .035, .09, 'alarm', tip.x, tip.y + .015, tip.z, .012, 12);
  s.ball(needle, .028, 'alarm', tip.x, tip.y - .022, tip.z, 10, 8);
  // Ink capillary and the spring that keeps the pen on the paper.
  s.cable(needle, [at(-.02, .30, -.14), elbow.clone().add(at(-.06, .12, -.04)), at(.10, -.94, .58), at(tip.x, tip.y + .18, tip.z - .04)], .016, 'cable', 14);
  const spring = s.cyl(needle, .038, .26, 'trim', -.02, -.34, .14, .038, 10);
  spring.quaternion.setFromUnitVectors(UP, at(.1, -.9, .42).normalize());

  const rollers = ROLLERS.map(({ index, z }) => {
    const pivot = s.group(base, `RollerPivot${index}`, 0, ROLLER_Y, z);
    // The supply roll is paper; the drive roller is a dark, gripping drum.
    s.drum(pivot, ROLLER_R, 1.86, index === 0 ? 'ceramic' : 'graphite', 0, 0, 0, 28);
    for (const x of [-.93, .93]) {
      s.drum(pivot, ROLLER_R + .045, .05, 'brass', x, 0, 0, 24);
      if (index === 0) for (const r of [.13, .10, .07]) s.drum(pivot, r, .06, 'trim', x + (x > 0 ? .012 : -.012), 0, 0, 20);
    }
    s.drum(pivot, .05, 2.12, 'trim', 0, 0, 0, 12);
    // Index stripes make the rotation visible instead of implied.
    s.teethX(pivot, 4, ROLLER_R, 1.82, .012, .03, index === 0 ? 'brass' : 'trim', 0, 0, 0);
    if (index === 1) {
      s.drum(pivot, .20, .06, 'brass', 1.16, 0, 0, 22);
      s.teethX(pivot, 18, .215, .06, .05, .04, 'brass', 1.16, 0, 0);
    }
    return pivot;
  });
  return s.finalize(object, [base, needle, ...rollers]);
}

// ---------------------------------------------------------------------------
// DueWatch — a mechanical orrery. Three tracks on distinct planes, each with its
// own ratchet, carriage and planet, driven from a visible gear train.
// ---------------------------------------------------------------------------

export const DUE_ORBITS = [
  { radius: .64, tilt: [.30, 0], precession: .05, size: .17, body: 'ceramic' },
  { radius: .96, tilt: [-.52, .26], precession: -.07, size: .20, body: 'alarm' },
  { radius: 1.28, tilt: [.88, -.30], precession: .09, size: .15, body: 'slate' },
] as const;
const TRAINS = [{ r: .30, teeth: 20, x: .44, z: .30 }, { r: .23, teeth: 16, x: -.50, z: .18 }, { r: .36, teeth: 24, x: .06, z: -.54 }];

function buildDueWatch(): BuiltInstrument {
  const s = shop({
    steel: 'duewatch steel', navy: 'duewatch casing', panel: 'duewatch panel', graphite: 'duewatch graphite',
    brass: 'duewatch brass', trim: 'duewatch trim', glass: 'duewatch glass', lamp: 'duewatch lamp',
    ceramic: 'duewatch ceramic', cable: 'duewatch cable', signal: 'duewatch signal',
    alarm: 'duewatch alarm', slate: 'duewatch ceramic slate',
  }, {
    ceramic: { color: '#dfe4ea', metalness: .18, roughness: .58 },
    slate: { color: '#7d8ea6', metalness: .42, roughness: .44 },
    signal: { color: '#f0c079', metalness: .12, roughness: .34, emissive: '#F2A541', emissiveIntensity: 1 },
    alarm: { color: '#e8595e', metalness: .18, roughness: .40, emissive: '#FF5A5F', emissiveIntensity: .5 },
  });
  const object = new Group();
  object.name = 'DueWatch';
  const base = s.group(object, 'duewatchMount');
  s.plinth(base, 1.75, .34);

  // Gear housing: three trains of different ratios, one per track.
  s.cyl(base, .76, .34, 'navy', 0, .51, 0, .84, 36);
  s.ring(base, .80, .03, 'brass', 0, .66, 0, 44);
  s.cyl(base, .82, .07, 'panel', 0, .71, 0, .82, 36);
  s.cyl(base, .78, .03, 'graphite', 0, .76, 0, .78, 36);
  s.studs(base, 10, .72, .028, 'trim', .78);
  // The train sits proud of the deck plate, where its ratios can be read.
  for (const train of TRAINS) {
    s.cyl(base, train.r, .07, 'brass', train.x, .82, train.z, train.r, 26);
    s.teeth(base, train.teeth, train.r + .025, .055, .07, .045, 'brass', .82, train.x, train.z);
    s.cyl(base, train.r * .45, .035, 'graphite', train.x, .86, train.z, train.r * .45, 20);
    s.cyl(base, .05, .20, 'trim', train.x, .86, train.z, .05, 12);
    s.ball(base, .045, 'brass', train.x, .95, train.z, 10, 8);
  }

  // Column with an engraved date scale and its brass collars.
  s.cyl(base, .19, 1.12, 'steel', 0, 1.35, 0, .27, 28);
  for (const y of [.92, 1.35, 1.78]) s.ring(base, .215, .026, 'brass', 0, y, 0, 32);
  for (let i = 0; i <= 12; i++) s.box(base, .06, .012, .022, i % 3 === 0 ? 'trim' : 'brass', .225, 1.00 + i * .062, 0);
  s.box(base, .015, .80, .03, 'graphite', .235, 1.38, 0);

  // Three balanced arms carrying the meridian hoops, and the hoops' timing marks.
  // A single graduated meridian, carried on two braced legs: the frame of reference.
  for (const side of [-1, 1]) {
    const foot = at(0, .88, side * .74);
    const head = at(0, 1.62, side * 1.14);
    s.rod(base, foot, head, .052, 'steel');
    s.rod(base, foot.clone().addScaledVector(at(0, 0, side), .30), head.clone().addScaledVector(UP, -.22), .026, 'trim');
    s.box(base, .22, .13, .20, 'navy', 0, .86, side * .74);
    s.ball(base, .075, 'brass', head.x, head.y, head.z, 12, 10);
  }
  s.hoop(base, 1.18, .034, 'brass', 0, 1.95, 0, 72, 8).rotation.y = RIGHT;
  s.hoop(base, 1.13, .012, 'trim', 0, 1.95, 0, 64).rotation.y = RIGHT;
  for (let i = 0; i < 24; i++) {
    const angle = i / 24 * TAU;
    const mark = s.box(base, .03, i % 6 === 0 ? .11 : .055, .014, i % 6 === 0 ? 'trim' : 'brass', 0, 1.95 + Math.cos(angle) * 1.22, Math.sin(angle) * 1.22);
    mark.rotation.x = -angle;
  }
  // Due mark: the index the red world is measured against, and the lamp that answers it.
  s.box(base, .09, .26, .05, 'alarm', 0, 1.95, 1.30);
  s.box(base, .15, .12, .10, 'graphite', 0, 1.95, 1.38);
  s.box(base, .22, .09, .04, 'alarm', 0, .50, 1.44);
  s.box(base, .30, .18, .10, 'graphite', 0, .50, 1.48);

  // The sun: the run clock everything else is timed against.
  s.ball(base, .30, 'signal', 0, 1.95, 0, 28, 20);
  s.ring(base, .315, .02, 'brass', 0, 1.95, 0, 36).rotation.x = RIGHT + .3;
  s.cyl(base, .085, .20, 'trim', 0, 1.95, 0, .085, 16);

  const pivots: Object3D[] = [];
  DUE_ORBITS.forEach((spec, index) => {
    const pivot = s.group(base, `OrbitPivot${index}`, 0, 1.95, 0);
    const track = s.group(pivot, `OrbitTrack${index}`);
    track.rotation.set(spec.tilt[0], 0, spec.tilt[1]);
    s.ring(track, spec.radius, .024, 'brass', 0, 0, 0, 56, 7);
    s.ring(track, spec.radius - .05, .011, 'trim', 0, 0, 0, 48);
    s.teeth(track, 24, spec.radius + .04, .02, .028, .045, 'brass');
    for (let i = 0; i < 4; i++) {
      const angle = i / 4 * TAU;
      s.box(track, .05, .034, .09, 'trim', Math.cos(angle) * (spec.radius + .05), 0, Math.sin(angle) * (spec.radius + .05)).rotation.y = -angle;
    }
    // Two slender brackets hold the track off a collar around the sun.
    s.ring(track, .36, .024, 'steel', 0, 0, 0, 36);
    for (const sign of [1, -1]) s.rod(track, at(sign * .36, 0, 0), at(sign * spec.radius, 0, 0), .022, 'steel', 8);
    const planet = s.group(track, `PlanetPivot${index}`);
    s.rod(planet, at(.30, 0, 0), at(spec.radius - .02, 0, 0), .028, 'trim', 10);
    s.cyl(planet, .07, .10, 'brass', .30, 0, 0, .07, 14);
    s.box(planet, .11, .09, .13, 'steel', spec.radius, 0, 0);
    for (const sign of [1, -1]) s.cyl(planet, .036, .04, 'trim', spec.radius, 0, sign * .055, .036, 10).rotation.x = RIGHT;
    s.cyl(planet, .028, .16, 'trim', spec.radius, .10, 0, .028, 10);
    s.ball(planet, spec.size, spec.body, spec.radius, .10 + spec.size, 0, 22, 16);
    const band = s.ring(planet, spec.size * 1.05, .012, 'brass', spec.radius, .10 + spec.size, 0, 28);
    band.rotation.set(RIGHT, 0, index === 2 ? .5 : .2);
    if (index === 2) s.ring(planet, spec.size * 1.9, .016, 'trim', spec.radius, .10 + spec.size, 0, 36).rotation.z = .5;
    pivots.push(pivot, planet);
  });
  return s.finalize(object, [base, ...pivots]);
}

// ---------------------------------------------------------------------------
// BrandWall — an optical bench. Lamp, collimator, rotating prism stage, detector
// ring and a receiver screen, all clamped to one machined rail.
// ---------------------------------------------------------------------------

const RAIL_Y = 1.58, AXIS_Y = 1.95;

/** A carrier: the clamped block, its clamp screw and three levelling screws. */
function carrier(s: Shop, base: Group, x: number, width: number, height: number) {
  s.box(base, width, .12, .46, 'graphite', x, RAIL_Y + .10, 0);
  s.box(base, width * .8, height, .30, 'steel', x, RAIL_Y + .16 + height / 2, 0);
  s.box(base, width + .06, .05, .50, 'panel', x, RAIL_Y + .18, 0);
  s.cyl(base, .055, .09, 'brass', x, RAIL_Y + .08, .28, .055, 14).rotation.x = RIGHT;
  for (const z of [-.17, .17]) s.cyl(base, .03, .12, 'trim', x + width * .3, RAIL_Y + .04, z, .03, 10);
  s.cyl(base, .03, .12, 'trim', x - width * .3, RAIL_Y + .04, 0, .03, 10);
}

function buildBrandWall(): BuiltInstrument {
  const s = shop({
    steel: 'brandwall steel', navy: 'brandwall casing', panel: 'brandwall panel', graphite: 'brandwall graphite',
    brass: 'brandwall brass', trim: 'brandwall trim', glass: 'brandwall glass', lamp: 'brandwall lamp',
    ceramic: 'brandwall ceramic', cable: 'brandwall cable', screen: 'brandwall screen',
  }, {
    ceramic: { color: '#b9c4d1', metalness: .26, roughness: .50 },
    screen: { color: '#0d1a2e', metalness: .22, roughness: .54 },
    'Prism blue': { color: '#5d93bb', metalness: .30, roughness: .05, emissive: '#1d5578', emissiveIntensity: .30, flat: true },
    Spectrum0: { color: '#f22929', metalness: .1, roughness: .32, emissive: '#F22929', emissiveIntensity: .45 },
    Spectrum1: { color: '#f26e11', metalness: .1, roughness: .32, emissive: '#F26E11', emissiveIntensity: .45 },
    Spectrum2: { color: '#5ce39c', metalness: .1, roughness: .32, emissive: '#5CE39C', emissiveIntensity: .45 },
    Spectrum3: { color: '#3d94f2', metalness: .1, roughness: .32, emissive: '#3D94F2', emissiveIntensity: .45 },
  });
  const object = new Group();
  object.name = 'BrandWall';
  const base = s.group(object, 'brandwallMount');
  s.plinth(base, 1.75, .34);

  // Two pedestals and a central column carry the rail.
  for (const x of [-1.10, 1.10]) {
    s.cyl(base, .19, RAIL_Y - .52, 'navy', x, .34 + (RAIL_Y - .52) / 2, 0, .25, 24);
    s.box(base, .44, .05, .44, 'panel', x, .37, 0);
    s.studs(base, 6, .18, .026, 'trim', .40, x, 0);
    s.ring(base, .205, .022, 'brass', x, RAIL_Y - .30, 0, 28);
    s.box(base, .40, .12, .40, 'steel', x, RAIL_Y - .18, 0);
  }
  s.box(base, .60, .52, .52, 'navy', 0, .60, 0);
  s.box(base, .66, .05, .58, 'panel', 0, .87, 0);
  s.box(base, .50, .16, .04, 'graphite', 0, .66, .27);
  for (const x of [-.14, 0, .14]) s.box(base, .07, .05, .03, 'lamp', x, .66, .285);
  s.cyl(base, .16, RAIL_Y - 1.0, 'steel', 0, .90 + (RAIL_Y - 1.0) / 2, 0, .20, 24);
  // The rail: a T-slot bar with a graduated scale along its front face.
  s.box(base, 3.32, .16, .40, 'steel', 0, RAIL_Y, 0);
  s.box(base, 3.36, .05, .46, 'panel', 0, RAIL_Y + .09, 0);
  s.box(base, 3.24, .07, .13, 'graphite', 0, RAIL_Y + .07, 0);
  for (let i = 0; i <= 32; i++) {
    const x = -1.61 + i * .1006;
    s.box(base, .012, i % 4 === 0 ? .09 : .05, .012, i % 4 === 0 ? 'trim' : 'brass', x, RAIL_Y - .02, .205);
  }
  s.box(base, 3.32, .04, .02, 'brass', 0, RAIL_Y + .04, .205);

  // Source: a finned lamp housing with its aperture facing down the bench.
  carrier(s, base, -1.45, .46, .16);
  s.drum(base, .24, .56, 'navy', -1.45, AXIS_Y, 0, 28);
  for (const x of [-1.64, -1.53, -1.42, -1.31]) s.drum(base, .285, .028, 'panel', x, AXIS_Y, 0, 28);
  s.drum(base, .18, .10, 'brass', -1.20, AXIS_Y, 0, 24);
  s.drum(base, .13, .06, 'lamp', -1.16, AXIS_Y, 0, 20);
  s.box(base, .16, .18, .18, 'graphite', -1.45, AXIS_Y, .30);
  for (const x of [-1.50, -1.40]) s.cyl(base, .028, .09, 'trim', x, AXIS_Y, .40, .028, 10).rotation.x = RIGHT;
  s.cable(base, [at(-1.45, AXIS_Y, .42), at(-1.56, 1.42, .44), at(-1.18, .88, .38), at(-.28, .70, .30)], .02, 'cable');

  // Collimator: the ceramic barrel the case file's first leader line ends on.
  carrier(s, base, -.75, .40, .14);
  s.drum(base, .16, .60, 'ceramic', -.75, AXIS_Y, 0, 28);
  for (const x of [-1.0, -.50]) s.drum(base, .19, .05, 'brass', x, AXIS_Y, 0, 24);
  s.drum(base, .175, .07, 'graphite', -.46, AXIS_Y, 0, 24);
  s.teethX(base, 8, .12, .02, .11, .05, 'trim', -.43, AXIS_Y, 0);
  s.drum(base, .20, .08, 'brass', -.86, AXIS_Y, 0, 24);
  s.teethX(base, 16, .21, .07, .03, .03, 'brass', -.86, AXIS_Y, 0);

  // Detector ring mount: the rig's own torus sits inside this holder.
  carrier(s, base, .86, .34, .12);
  s.box(base, .10, .26, .10, 'steel', .86, RAIL_Y + .34, 0);
  s.hoop(base, .42, .03, 'steel', .86, 1.90, 0, 40).rotation.y = RIGHT;
  for (const z of [-.30, .30]) s.box(base, .10, .10, .12, 'brass', .86, 1.90 - Math.sqrt(Math.max(0, .42 * .42 - z * z)), z);
  for (const y of [1.90 - .42, 1.90 + .42]) s.box(base, .10, .09, .10, 'brass', .86, y, 0);
  s.box(base, .13, .13, .13, 'graphite', .86, 1.90, -.44);
  s.cable(base, [at(.86, 1.86, -.50), at(1.0, 1.50, -.46), at(.70, 1.0, -.34), at(.20, .74, -.26)], .018, 'cable', 14);

  // Receiver: the framed screen the photons land on, and the detector housing behind it.
  carrier(s, base, 1.42, .48, .18);
  s.box(base, .06, 1.10, 1.86, 'screen', 1.40, AXIS_Y, 0);
  s.box(base, .03, 1.18, 1.94, 'navy', 1.46, AXIS_Y, 0);
  for (const y of [AXIS_Y - .58, AXIS_Y + .58]) s.box(base, .07, .05, 1.96, 'trim', 1.43, y, 0);
  for (const z of [-.96, .96]) s.box(base, .07, 1.20, .05, 'trim', 1.43, AXIS_Y, z);
  for (let i = -3; i <= 3; i++) s.box(base, .015, 1.04, .012, 'brass', 1.37, AXIS_Y, i * .24);
  s.box(base, .22, .52, .40, 'graphite', 1.58, AXIS_Y - .18, -.72);
  s.box(base, .04, .07, .22, 'lamp', 1.70, AXIS_Y - .04, -.72);
  s.box(base, .26, .05, .46, 'panel', 1.58, AXIS_Y + .10, -.72);
  s.box(base, .10, .34, .10, 'steel', 1.58, RAIL_Y + .26, -.72);
  s.cable(base, [at(1.66, 1.70, .26), at(1.72, 1.20, .34), at(1.30, .80, .40), at(.30, .70, .34)], .02, 'cable');

  // Rotating prism stage: a graduated table, the prism and the cage that holds it.
  const prism = s.group(base, 'PrismPivot', 0, AXIS_Y, 0);
  s.cyl(prism, .40, .06, 'trim', 0, -.56, 0, .40, 36);
  s.cyl(prism, .36, .04, 'graphite', 0, -.60, 0, .36, 36);
  s.scale(prism, 36, .38, 'brass', -.525, 3, .06);
  s.cyl(prism, .26, .06, 'brass', 0, .54, 0, .26, 30);
  s.cyl(prism, .44, 1.00, 'Prism blue', 0, 0, 0, .44, 3);
  for (let i = 0; i < 3; i++) {
    const angle = i / 3 * TAU - .5;
    s.cyl(prism, .026, 1.18, 'trim', Math.cos(angle) * .45, 0, Math.sin(angle) * .45, .026, 10);
    for (const y of [-.45, .45]) {
      const clamp = s.box(prism, .12, .045, .08, 'brass', Math.cos(angle) * .42, y, Math.sin(angle) * .42);
      clamp.rotation.y = -angle;
    }
  }
  s.cyl(prism, .14, .12, 'steel', 0, -.64, 0, .14, 18);

  // Refracted bands: red fans toward +z, blue toward −z, matching where photons land.
  const spectrum = s.group(base, 'SpectrumPivot', 0, AXIS_Y, 0);
  ([[-.48, .60], [-.16, .20], [.16, -.20], [.48, -.60]] as const).forEach(([rise, spread], i) => {
    s.bar(spectrum, at(.30, 0, 0), at(1.33, rise, spread), .028, .028, `Spectrum${i}`);
  });
  return s.finalize(object, [base, prism, spectrum]);
}

const BUILDERS: Record<InstrumentId, () => BuiltInstrument> = {
  crosscheck: buildCrossCheck,
  surgeline: buildSurgeLine,
  driftwatch: buildDriftWatch,
  duewatch: buildDueWatch,
  brandwall: buildBrandWall,
};

/** A real-time instrument: every moving assembly owns its pivot; all resources are local. */
export function buildInstrument(id: InstrumentId): BuiltInstrument {
  return BUILDERS[id]();
}
