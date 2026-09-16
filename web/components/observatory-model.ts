import {
  BoxGeometry, CylinderGeometry, DoubleSide, Group, MathUtils, Mesh,
  MeshStandardMaterial, SphereGeometry, TorusGeometry, TubeGeometry,
  CatmullRomCurve3, Matrix4, Vector3, type BufferGeometry,
} from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const TAU = Math.PI * 2;

/** A real-time model: every moving assembly owns its pivot; all resources are local. */
export function buildObservatory() {
  const object = new Group();
  object.name = 'Observatory';
  const geometries = new Set<BufferGeometry>();
  const materials = {
    shell: new MeshStandardMaterial({ color: '#91a6bc', metalness: .68, roughness: .33, side: DoubleSide }),
    dark: new MeshStandardMaterial({ color: '#152337', metalness: .55, roughness: .48 }),
    wall: new MeshStandardMaterial({ color: '#425368', metalness: .35, roughness: .64 }),
    brass: new MeshStandardMaterial({ color: '#c18c4b', metalness: .72, roughness: .3 }),
    trim: new MeshStandardMaterial({ color: '#d0d7da', metalness: .72, roughness: .26 }),
    glass: new MeshStandardMaterial({ color: '#081c29', metalness: .9, roughness: .12, emissive: '#397f9c', emissiveIntensity: .28 }),
    light: new MeshStandardMaterial({ color: '#dc9b5b', emissive: '#ffad60', emissiveIntensity: .65, toneMapped: false }),
  };
  type Finish = keyof typeof materials;
  const add = (parent: Group, geometry: BufferGeometry, finish: Finish, x = 0, y = 0, z = 0) => {
    geometries.add(geometry);
    const mesh = new Mesh(geometry, materials[finish]);
    mesh.position.set(x, y, z);
    parent.add(mesh);
    return mesh;
  };
  const box = (parent: Group, w: number, h: number, d: number, finish: Finish, x = 0, y = 0, z = 0) => add(parent, new BoxGeometry(w, h, d), finish, x, y, z);
  const cylinder = (parent: Group, r: number, h: number, finish: Finish, y = 0, rBottom = r) => add(parent, new CylinderGeometry(r, rBottom, h, 64), finish, 0, y);
  const ring = (parent: Group, r: number, tube: number, finish: Finish, y = 0) => {
    const mesh = add(parent, new TorusGeometry(r, tube, 8, 96), finish, 0, y);
    mesh.rotation.x = Math.PI / 2;
    return mesh;
  };

  // Stepped foundation, luminous service channel and an open observation deck.
  cylinder(object, 2.65, .18, 'dark', -1.46, 2.72);
  cylinder(object, 2.52, .12, 'wall', -1.31);
  ring(object, 2.54, .018, 'light', -1.28);
  cylinder(object, 2.38, .12, 'dark', -1.21);
  cylinder(object, 1.94, 1.24, 'wall', -.55);
  ring(object, 1.96, .045, 'brass', -.02);
  cylinder(object, 2.14, .12, 'dark', .11);
  ring(object, 2.10, .045, 'trim', .19);
  ring(object, 1.98, .025, 'light', .21);
  for (let i = 0; i < 24; i++) {
    const angle = i / 24 * TAU;
    const bay = new Group();
    bay.rotation.y = angle;
    object.add(bay);
    box(bay, .032, 1.1, .05, 'brass', 0, -.55, 1.951);
    if (i % 3 !== 0) {
      box(bay, .29, .64, .07, 'dark', .21, -.55, 1.92);
      box(bay, .21, .51, .025, 'light', .21, -.53, 1.964);
      box(bay, .025, .54, .035, 'brass', .21, -.53, 1.99);
      box(bay, .23, .025, .035, 'brass', .21, -.57, 1.99);
    }
    const post = cylinder(bay, .018, .36, 'trim', -1.0);
    post.position.z = 2.37;
  }
  ring(object, 2.37, .023, 'trim', -.82);
  ring(object, 2.37, .014, 'dark', -1.04);
  // Entrance and broad stairs interrupt the circular base.
  box(object, .66, .91, .16, 'dark', 0, -.73, 1.96);
  box(object, .44, .72, .04, 'glass', 0, -.74, 2.05);
  box(object, .5, .028, .04, 'light', 0, -.36, 2.09);
  for (let i = 0; i < 4; i++) box(object, .87, .09, .25, 'wall', 0, -1.19 - i * .09, 2.12 + i * .2);

  const dome = new Group();
  dome.name = 'DomeAzimuth';
  dome.position.y = .24;
  object.add(dome);
  // Segmented hemisphere with a genuinely open observing slit, rather than a painted cutout.
  const start = Math.PI / 2 + .52;
  const span = TAU - 1.04;
  for (let i = 0; i < 28; i++) {
    const phi = start + i / 28 * span;
    add(dome, new SphereGeometry(2.02, 5, 28, phi + .007, span / 28 - .014, .025, Math.PI / 2 - .025), 'shell');
    const points = Array.from({ length: 29 }, (_, j) => {
      const theta = .035 + j / 28 * (Math.PI / 2 - .035);
      return new Vector3(-2.035 * Math.cos(phi) * Math.sin(theta), 2.035 * Math.cos(theta), 2.035 * Math.sin(phi) * Math.sin(theta));
    });
    add(dome, new TubeGeometry(new CatmullRomCurve3(points), 28, .014, 4, false), 'dark');
  }
  for (const phi of [start, start + span]) {
    const points = Array.from({ length: 33 }, (_, j) => {
      const theta = j / 32 * Math.PI / 2;
      return new Vector3(-2.055 * Math.cos(phi) * Math.sin(theta), 2.055 * Math.cos(theta), 2.055 * Math.sin(phi) * Math.sin(theta));
    });
    add(dome, new TubeGeometry(new CatmullRomCurve3(points), 32, .045, 8, false), 'brass');
  }
  ring(dome, 2.03, .07, 'shell');
  ring(dome, 2.045, .021, 'brass', .08);
  for (let i = 0; i < 36; i++) {
    const angle = i / 36 * TAU;
    const bolt = add(dome, new SphereGeometry(.026, 6, 4), 'trim', Math.cos(angle) * 2.083, 0, Math.sin(angle) * 2.083);
    bolt.scale.y = .7;
  }

  const mount = new Group();
  mount.name = 'TelescopeAzimuth';
  object.add(mount);
  cylinder(mount, .51, .14, 'brass', .32);
  cylinder(mount, .34, .56, 'dark', .64, .43);
  cylinder(mount, .42, .13, 'trim', .95);
  for (const side of [-1, 1]) {
    box(mount, .12, .62, .3, 'shell', side * .43, 1.19);
    const bearing = add(mount, new CylinderGeometry(.19, .19, .16, 32), 'brass', side * .46, 1.42);
    bearing.rotation.z = Math.PI / 2;
  }
  const telescope = new Group();
  telescope.name = 'TelescopeAltitude';
  telescope.position.y = 1.42;
  telescope.rotation.x = -.40;
  mount.add(telescope);
  const tube = add(telescope, new CylinderGeometry(.32, .37, 1.6, 48), 'shell', 0, 0, .36);
  tube.rotation.x = Math.PI / 2;
  for (const z of [-.42, -.12, .83, 1.12]) {
    const collar = add(telescope, new TorusGeometry(.345, .045, 10, 48), z === 1.12 ? 'brass' : 'dark', 0, 0, z);
    collar.rotation.z = Math.PI / 2;
  }
  const lens = add(telescope, new SphereGeometry(.29, 40, 24), 'glass', 0, 0, 1.15);
  lens.scale.z = .18;
  add(telescope, new TorusGeometry(.25, .012, 8, 48), 'trim', 0, 0, 1.175);
  box(telescope, .12, .11, 1.14, 'brass', 0, .36, .23);
  const finder = add(telescope, new CylinderGeometry(.065, .085, .65, 16), 'dark', .17, .45, .37);
  finder.rotation.x = Math.PI / 2;
  box(telescope, .36, .32, .21, 'dark', 0, 0, -.56);
  box(telescope, .14, .045, .025, 'light', 0, .07, -.674);
  // Counterweight and a small instrument cabinet on the service deck.
  box(mount, .08, .08, .58, 'trim', 0, .91, -.55);
  box(mount, .4, .23, .26, 'dark', 0, .91, -.82);
  const cabinet = new Group();
  cabinet.position.set(1.75, -1.1, -.9);
  cabinet.rotation.y = -.5;
  object.add(cabinet);
  box(cabinet, .56, .52, .38, 'dark', 0, .26);
  box(cabinet, .43, .22, .015, 'glass', 0, .35, .2);
  box(cabinet, .23, .02, .02, 'light', 0, .35, .22);

  // Hundreds of architectural details become a handful of draws per moving assembly.
  // Keep only the three mechanical pivots separate; bake static descendants in local space.
  const moving = new Set([dome, mount, telescope]);
  for (const assembly of [telescope, mount, dome, object]) {
    assembly.updateWorldMatrix(true, true);
    const inverse = new Matrix4().copy(assembly.matrixWorld).invert();
    const batches = new Map<MeshStandardMaterial, BufferGeometry[]>();
    const gather = (group: Group) => {
      for (const child of [...group.children]) {
        if (child instanceof Group) { if (!moving.has(child)) gather(child); }
        else if (child instanceof Mesh) {
          const geometry = child.geometry.clone().applyMatrix4(new Matrix4().multiplyMatrices(inverse, child.matrixWorld));
          const material = child.material as MeshStandardMaterial;
          if (!batches.has(material)) batches.set(material, []);
          batches.get(material)!.push(geometry);
          group.remove(child);
        }
      }
    };
    gather(assembly);
    batches.forEach((parts, material) => {
      const geometry = mergeGeometries(parts);
      parts.forEach(part => part.dispose());
      if (!geometry) throw new Error('Observatory assembly geometry could not be merged');
      geometries.add(geometry);
      assembly.add(new Mesh(geometry, material));
    });
  }

  return {
    object,
    update(time: number, scroll: number) {
      dome.rotation.y = Math.sin(time * .12) * .075 + MathUtils.smootherstep(scroll, 0, 1) * .48;
      mount.rotation.y = Math.sin(time * .16) * .16 + scroll * .22;
      telescope.rotation.x = -.40 - Math.sin(time * .23) * .065 - scroll * .24;
    },
    dispose() {
      geometries.forEach(geometry => geometry.dispose());
      Object.values(materials).forEach(material => material.dispose());
    },
  };
}
