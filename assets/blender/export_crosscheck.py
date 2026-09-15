"""Run through Blender GUI MCP with __file__ set; preserve the approved source."""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'assets/blender/crosscheck-web.blend'


def export_crosscheck():
    if OUTPUT.exists():
        raise RuntimeError('Export source exists; inspect before rebuilding.')
    if bpy.data.is_dirty:
        raise RuntimeError('Save current Blender work before exporting.')
    source = bpy.data.scenes['CrossCheck / three optics']
    window = bpy.context.window_manager.windows[0]
    window.scene = source
    with bpy.context.temp_override(window=window):
        bpy.ops.scene.new(type='FULL_COPY')
        scene = window.scene
        scene.name = 'CrossCheck / web export'
        # Checkpoint before destructive conversion of the copied objects.
        bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
        meshes = [o for o in scene.objects if o.type == 'MESH']
        lenses = [next(o for o in meshes if o.name.startswith(f'Optic {i} lens')
                       and not any(x in o.name for x in ('retainer', 'reflection')))
                  for i in range(1, 4)]
        moving = [o for o in meshes if o.name.startswith(('Optic ', 'Lens retaining screw'))]

        def join(objects, name):
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = objects[0]
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.join()
            obj = bpy.context.object
            obj.name = name
            return obj

        body = join([o for o in moving if o not in lenses], 'OpticsBody')
        join([o for o in meshes if o not in moving], 'CrossCheckMount')
        pivot = bpy.data.objects.new('OpticsPivot', None)
        scene.collection.objects.link(pivot)
        pivot.location = (0, 0, 2.3)
        bpy.context.view_layer.update()
        for i, lens in enumerate(lenses, 1):
            lens.name = f'Lens{i}'
            lens.data.materials[0] = lens.data.materials[0].copy()
            lens.data.materials[0].name = f'Lens{i}Glow'
        for obj in [body, *lenses]:
            matrix = obj.matrix_world.copy()
            obj.parent = pivot
            obj.matrix_world = matrix
        scene.render.filepath = str(ROOT / 'assets/renders/crosscheck/crosscheck-web-review.png')
        Path(scene.render.filepath).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(ROOT / 'web/public/models/crosscheck.glb'),
            export_format='GLB', use_active_scene=True, export_cameras=False,
            export_lights=False, export_animations=False, export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
        )
        bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
        print('EXPORTED', (ROOT / 'web/public/models/crosscheck.glb').stat().st_size)


if __name__ == '__main__':
    export_crosscheck()
