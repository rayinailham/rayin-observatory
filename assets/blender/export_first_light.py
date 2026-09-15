"""Run through Blender GUI MCP. Preserve approved files; export Phase 1 only."""
from pathlib import Path
import bpy
import math

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'assets/blender/first-light.blend'
MODELS = ROOT / 'web/public/models'

def export_first_light():
    if OUTPUT.exists():
        raise FileExistsError(f'Refusing to overwrite {OUTPUT}')
    if bpy.data.is_dirty:
        raise RuntimeError('Save current Blender work before building the export scene')
    source = bpy.data.scenes.get('Dome / night review')
    if source is None:
        raise RuntimeError('Open the approved dome.blend first')
    scene = bpy.data.scenes.new('First light / dome export')
    bpy.context.window.scene = scene
    scene.world = source.world.copy()
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.filepath = str(ROOT / 'assets/renders/first-light/dome-web-review.png')
    scene.view_settings.view_transform = 'AgX'
    copies = []
    for original in source.objects:
        obj = original.copy()
        obj.data = original.data.copy()
        scene.collection.objects.link(obj)
        if obj.type in {'MESH', 'CURVE'}:
            copies.append(obj)
        if obj.type == 'CAMERA':
            scene.camera = obj
    # Checkpoint before converting and joining the temporary export copies.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in copies:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    dome = bpy.context.object
    dome.name = 'ObservatoryDome'
    MODELS.mkdir(parents=True, exist_ok=True)
    settings = dict(export_format='GLB', use_selection=True, use_active_scene=True, export_apply=True,
                    export_draco_mesh_compression_enable=True,
                    export_draco_mesh_compression_level=6,
                    export_cameras=False, export_lights=False, export_animations=False)
    bpy.ops.export_scene.gltf(filepath=str(MODELS / 'dome.glb'), **settings)

    sky = bpy.data.scenes.new('First light / ambient planet')
    bpy.context.window.scene = sky
    sky.world = scene.world.copy()
    mat = bpy.data.materials.new('First light / planet mineral')
    mat.diffuse_color = (0.19, 0.25, 0.34, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = mat.diffuse_color
    bsdf.inputs['Roughness'].default_value = 0.94
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1)
    planet = bpy.context.object
    planet.name = 'AmbientPlanet'
    planet.data.materials.append(mat)
    for p in planet.data.polygons:
        p.use_smooth = True
    ring_mat = bpy.data.materials.new('First light / dusty rings')
    ring_mat.diffuse_color = (0.24, 0.20, 0.15, 1)
    ring_mat.use_nodes = True
    ring_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = ring_mat.diffuse_color
    ring_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
    ring_objects = []
    for radius, thickness in [(1.45, .055), (1.59, .025), (1.68, .018)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=thickness,
            major_segments=96, minor_segments=6)
        ring = bpy.context.object
        ring.name = 'AmbientRing'
        ring.data.materials.append(ring_mat)
        ring_objects.append(ring)
    bpy.ops.object.select_all(action='DESELECT')
    planet.select_set(True)
    for obj in ring_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = planet
    bpy.ops.object.join()
    bpy.ops.export_scene.gltf(filepath=str(MODELS / 'ambient.glb'), **settings)
    bpy.context.window.scene = scene
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    return {'blend': str(OUTPUT), 'exports': {p.name:p.stat().st_size for p in MODELS.glob('*.glb')},
            'dome_polygons':len(dome.data.polygons), 'render':scene.render.filepath}

if __name__ == '__main__':
    result = export_first_light()
