"""Phase 0 sources. Execute via Blender MCP in the existing Blender GUI.

Creates fresh scenes without deleting existing work; refuses to overwrite assets.
Render by selecting either scene and calling bpy.ops.render.render(write_still=True).
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]


def material(name, rgb, metallic=0.0, roughness=0.4, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*rgb, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat


def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if bevel:
            mod = obj.modifiers.new('Machined edge', 'BEVEL')
            mod.width = bevel
            mod.segments = 3
            obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def cylinder(name, radius, depth, pos, mat, direction=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=pos)
    obj = finish(bpy.context.object, name, mat, 0.025)
    obj.rotation_euler = Vector(direction).to_track_quat('Z', 'Y').to_euler()
    return obj


def ring(name, radius, thickness, pos, mat, direction=(0, 0, 1)):
    bpy.ops.mesh.primitive_torus_add(major_segments=80, minor_segments=12,
                                   major_radius=radius, minor_radius=thickness, location=pos)
    obj = finish(bpy.context.object, name, mat)
    obj.rotation_euler = Vector(direction).to_track_quat('Z', 'Y').to_euler()
    return obj


def beam(name, start, end, radius, mat):
    a, b = Vector(start), Vector(end)
    return cylinder(name, radius, (b-a).length, (a+b)/2, mat, b-a)


def curve(name, points, thickness, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = thickness
    data.bevel_resolution = 3
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, xyz in zip(spline.points, points):
        p.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    data.materials.append(mat)
    return obj


def scene_setup(name, target, camera_pos, scale):
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == 'OPTIX'
        if any(d.use for d in prefs.devices):
            scene.cycles.device = 'GPU'
    except Exception:
        scene.cycles.device = 'CPU'
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.world = bpy.data.worlds.new(name + ' night')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.055, 0.085, 0.16, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.object.camera_add(location=camera_pos)
    camera = bpy.context.object
    camera.name = name + ' review camera'
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    scene.camera = camera
    for label, pos, color, power, size in [
        ('Cool key', (1,-6,8), (0.58,0.72,1), 1500, 5),
        ('Amber rim', (-5,1,6), (1,0.52,0.18), 2000, 4),
        ('Upper rim', (3,5,8), (0.55,0.72,1), 2400, 3),
        ('Soft front', (5,-7,3), (0.7,0.8,1), 350, 4),
    ]:
        bpy.ops.object.light_add(type='AREA', location=pos)
        light = bpy.context.object
        light.name = label
        light.data.energy, light.data.color, light.data.shape, light.data.size = power, color, 'DISK', size
        light.rotation_euler = (Vector(target)-light.location).to_track_quat('-Z','Y').to_euler()
    return scene


def build():
    for name in ['dome', 'crosscheck']:
        if (ROOT / 'assets/blender' / (name + '.blend')).exists():
            raise FileExistsError('Use a versioned output before rebuilding: ' + name)
    navy = material('Navy enamel', (0.024,0.047,0.095), 0.72, 0.3)
    panel = material('Raised navy panels', (0.055,0.086,0.15), 0.65, 0.32)
    black = material('Recess graphite', (0.012,0.018,0.031), 0.45, 0.35)
    brass = material('Satin amber metal', (0.65,0.34,0.09), 0.78, 0.3)
    silver = material('Brushed steel', (0.32,0.4,0.5), 0.8, 0.28)
    glow = material('Amber light', (1,0.43,0.09), 0.25, 0.25, 2.2)
    lens = material('Optical glass', (0.008,0.021,0.039), 0.95, 0.065)
    lens.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 1

    dome = scene_setup('Dome / night review', (0,0,1.9), (7,-11,7), 8.7)
    cylinder('Foundation', 2.95, 0.24, (0,0,0.12), black)
    cylinder('Stepped plinth', 2.68, 0.24, (0,0,0.34), panel)
    cylinder('Drum', 2.37, 1.25, (0,0,1.06), navy)
    for z in [0.55,1.57,1.72]:
        ring('Drum collar', 2.4, 0.065, (0,0,z), brass if z==1.72 else silver)
    ring('Warm equator', 2.405, 0.022, (0,0,1.67), glow)
    for i in range(32):
        a=2*math.pi*i/32
        beam('Drum rib', (2.375*math.cos(a),2.375*math.sin(a),0.56),
             (2.375*math.cos(a),2.375*math.sin(a),1.56),0.017,black)
    # Open wedge faces the review camera. Each panel is its own editable shell.
    radius, base, count = 2.36, 1.75, 28
    for i in range(count):
        a0=math.radians(-46)+(math.radians(278)*i/count)
        a1=math.radians(-46)+(math.radians(278)*(i+1)/count)
        verts=[]
        for j in range(25):
            t=(math.pi/2-0.012)*j/24
            for a in [a0+0.002,a1-0.002]:
                verts.append((radius*math.cos(t)*math.cos(a),radius*math.cos(t)*math.sin(a),base+radius*math.sin(t)))
        faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(24)]
        mesh=bpy.data.meshes.new('Dome panel mesh');mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('Dome shell panel',mesh);dome.collection.objects.link(obj)
        finish(obj,obj.name,panel if i%4==0 else navy)
        mod=obj.modifiers.new('Shell thickness','SOLIDIFY');mod.thickness=0.055
    for a in [math.radians(-46),math.radians(232)]:
        points=[(radius*math.cos(t)*math.cos(a),radius*math.cos(t)*math.sin(a),base+radius*math.sin(t)) for t in [j*math.pi/2/64 for j in range(65)]]
        curve('Opening rail',points,0.045,brass)
        curve('Opening guide light',[(x,y,z+0.012) for x,y,z in points],0.014,glow)
    cylinder('Interior instrument pier',0.38,1.3,(0,0,2.0),black)
    beam('Interior telescope',(0,0.2,2.4),(0,-1.25,3.4),0.27,panel)
    for z,r in [(0.52,2.66),(0.3,2.91)]: ring('Base accent',r,0.025,(0,0,z),brass)
    dome.render.filepath=str(ROOT/'assets/renders/dome-night.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/blender/dome.blend'))

    scope = scene_setup('CrossCheck / three optics', (0,0,2.0), (6,-10,6.4), 5.4)
    cylinder('Azimuth foot',1.48,0.22,(0,0,0.11),black)
    cylinder('Azimuth platter',1.24,0.18,(0,0,0.3),navy)
    ring('Azimuth brass rim',1.27,0.04,(0,0,0.37),brass)
    cylinder('Instrument pier',0.37,1.38,(0,0,1.03),panel)
    ring('Pier collar',0.39,0.06,(0,0,1.53),brass)
    for x in [-0.89,0.89]:
        beam('Fork upright',(x,0,1.2),(x,0,2.35),0.13,navy)
        beam('Fork base',(0,0,1.4),(x,0,1.4),0.12,navy)
    beam('Altitude axle',(-1.03,0,2.3),(1.03,0,2.3),0.18,brass)
    cylinder('Altitude knob',0.32,0.19,(1.12,0,2.3),silver,(1,0,0))
    direction=Vector((0,-0.91,0.414)).normalized()
    up=Vector((0,0.414,0.91)).normalized()
    center=Vector((0,0,2.68))
    for index,(x,y) in enumerate([(-0.52,-0.23),(0.52,-0.23),(0,0.66)]):
        origin=center+Vector((x,0,0))+up*y
        cylinder(f'Optic {index+1} barrel',0.46,2.12,origin,panel,direction)
        for distance in [-0.99,-0.68,0.66,1.06]:
            pos=origin+direction*distance
            cylinder(f'Optic {index+1} band',0.484,0.11,pos,brass if distance in [-0.68,1.06] else black,direction)
        front=origin+direction*1.135
        cylinder(f'Optic {index+1} recess',0.409,0.025,front,black,direction)
        cylinder(f'Optic {index+1} lens',0.362,0.027,front+direction*0.019,lens,direction)
        ring(f'Optic {index+1} lens retainer',0.372,0.018,front+direction*0.036,glow,direction)
        ring(f'Optic {index+1} lens reflection',0.279,0.004,front+direction*0.038,silver,direction)
        cylinder(f'Optic {index+1} rear focus',0.18,0.27,origin-direction*1.2,black,direction)
        for angle in range(0,360,60):
            radial=Vector((math.cos(math.radians(angle)),0,0))+up*math.sin(math.radians(angle))
            cylinder('Lens retaining screw',0.021,0.026,front+radial*0.443+direction*0.005,silver,direction)
    for angle in range(0,360,10):
        a=math.radians(angle)
        beam('Azimuth tick',(1.1*math.cos(a),1.1*math.sin(a),0.402),
             ((1.19 if angle%30==0 else 1.15)*math.cos(a),(1.19 if angle%30==0 else 1.15)*math.sin(a),0.402),0.007,brass)
    scope.render.filepath=str(ROOT/'assets/renders/crosscheck-night.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/blender/crosscheck.blend'))
    return {'scenes':[dome.name,scope.name], 'objects':{s.name:len(s.objects) for s in [dome,scope]},'device':scope.cycles.device}


if __name__ == '__main__':
    result=build()
