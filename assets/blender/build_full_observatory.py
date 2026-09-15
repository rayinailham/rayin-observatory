"""Phase 3 instruments. Execute through Blender GUI MCP, never headless.
New scenes only; refuse overwrite, checkpoint before mesh conversion/join.
"""
from pathlib import Path
import bpy
import math
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SLUGS = ('surgeline', 'driftwatch', 'duewatch', 'brandwall')

def material(name, color, metal=.5, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = .38
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = emission
    return m

def finish(obj, name, mat, parent=None):
    obj.name = name
    obj.data.materials.append(mat)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    if obj.type == 'MESH':
        for p in obj.data.polygons: p.use_smooth = True
    return obj

def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=finish(bpy.context.object,name,mat); o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    b=o.modifiers.new('Machined edges','BEVEL'); b.width=.045; b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, r, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=depth, location=loc)
    return finish(bpy.context.object,name,mat)

def sphere(name, loc, r, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=loc)
    return finish(bpy.context.object,name,mat)

def line(name, coords, mat, radius=.018):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=radius; c.bevel_resolution=2
    sp=c.splines.new('POLY'); sp.points.add(len(coords)-1)
    for p,co in zip(sp.points,coords): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    return finish(o,name,mat)

def ring(name, loc, radius, mat, rotation=(0,0,0), thickness=.035):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,location=loc,major_radius=radius,minor_radius=thickness,rotation=rotation)
    return finish(bpy.context.object,name,mat)

def pivot(name, loc, objects):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=loc
    bpy.context.view_layer.update()
    for child in objects:
        world=child.matrix_world.copy(); child.parent=o; child.matrix_world=world
    return o

def roller_marks(mat):
    # Witness lines make a smooth cylindrical drum's feed rotation visible.
    for i,y in enumerate([-.88,.7]):
        marks=[]
        for j in range(4):
            a=j*math.tau/4
            marks.append(line('Roller witness', [(-.95,y+.152*math.cos(a),.98+.152*math.sin(a)),(.95,y+.152*math.cos(a),.98+.152*math.sin(a))],mat,.009))
        pivot('RollerPivot'+str(i),(0,y,.98),marks)

def setup(slug):
    scene=bpy.data.scenes.new(slug+' / web review'); bpy.context.window.scene=scene
    scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX'; prefs.get_devices()
        for device in prefs.devices: device.use=device.type=='OPTIX'
        scene.cycles.device='GPU'
    except Exception: scene.cycles.device='CPU'
    scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.world=bpy.data.worlds.new(slug+' night'); scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.045,.065,.12,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    scene.view_settings.view_transform='AgX'
    bpy.ops.object.camera_add(location=(5,-9,6))
    cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=5.5; scene.camera=cam
    for loc,power,color,size in [((2,-4,7),900,(.66,.78,1),5),((-4,-2,3),650,(1,.58,.22),4),((1,4,5),1300,(.45,.65,1),3)]:
        bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    return scene

def make(slug):
    out=ROOT/'assets/blender'/f'{slug}-web.blend'
    if out.exists(): raise RuntimeError(f'Refusing overwrite: {out}')
    scene=setup(slug)
    navy=material(slug+' casing',(.055,.085,.15))
    brass=material(slug+' brass',(.55,.29,.09),.7)
    ivory=material(slug+' ceramic',(.66,.7,.73),.25)
    amber=material(slug+' signal',(.95,.43,.065),.25,1)
    red=material(slug+' alarm',(1,.07,.09),.1,1.2)
    base=cylinder('Plinth',(0,0,.15),1.75,.3,navy)
    ring('Base trim',(0,0,.31),1.68,brass)
    for i in range(32):
        a=i*math.tau/32
        box('Index', (1.58*math.cos(a),1.58*math.sin(a),.32),(.065,.025,.02),brass).rotation_euler.z=a
    if slug=='surgeline':
        for i,(x,y,z) in enumerate([(-.95,.25,1.4),(0,.65,1.8),(.95,.25,1.4),(0,-.8,1.2)]):
            cylinder('Mast',(x,y,(z+.3)/2),.075,z-.3,brass)
            before=set(scene.objects)
            # Parabolic reflector opening toward -Y (glTF front +Z).
            verts=[(0,0,0)]; faces=[]; segments=40; steps=8; r=.62
            for j in range(1,steps+1):
                rad=r*j/steps
                for k in range(segments):
                    a=k*math.tau/segments; verts.append((rad*math.cos(a),-.40*(rad/r)**2,rad*math.sin(a)))
            for k in range(segments): faces.append((0,1+k,1+(k+1)%segments))
            for j in range(steps-1):
                for k in range(segments):
                    a=1+j*segments+k; b=1+j*segments+(k+1)%segments
                    faces.append((a,b,b+segments,a+segments))
            mesh=bpy.data.meshes.new('Parabolic reflector'); mesh.from_pydata(verts,[],faces); mesh.update()
            dish=bpy.data.objects.new('Reflector',mesh); scene.collection.objects.link(dish); dish.location=(x,y,z); finish(dish,'Reflector',ivory)
            ring('Dish rim',(x,y-.4,z),r,brass,(math.pi/2,0,0))
            for side in [-1,1]: line('Feed support',[(x+side*r,y-.4,z),(x,y-.84,z)],brass)
            sphere('Pulse'+str(i),(x,y-.82,z),.07,amber)
            pivot('DishPivot'+str(i),(x,y,z),set(scene.objects)-before)
    elif slug=='driftwatch':
        box('Recorder',(0,0,.63),(2.6,1.9,.52),navy)
        paper=box('Paper',(0,-.12,.93),(1.85,1.55,.04),ivory)
        for y in [-.88,.7]:
            o=cylinder('Paper roller',(0,y,.98),.15,2.2,brass); o.rotation_euler.y=math.pi/2
        roller_marks(ivory)
        for x in [-.85, .85]:
            cylinder('Frame pillar',(x,.48,1.55),.065,1.3,brass)
        line('Cross arm',[(-.85,.48,2.2),(.85,.48,2.2)],brass,.065)
        before=set(scene.objects)
        line('Needle arm',[(0,.48,2.2),(0,-.2,1.25),(.12,-.3,.98)],brass,.03)
        sphere('Needle tip',(.12,-.3,.98),.04,red)
        pivot('NeedlePivot',(0,.48,2.2),set(scene.objects)-before)
        coords=[]
        for i in range(100):
            y=-.78+i*.014; spike=math.exp(-((y+.25)/.10)**2)
            coords.append((.1*math.sin(i*1.7)+.55*spike*math.sin(i*1.1),y,.958))
        trace=line('Trace',coords,red,.012); pivot('PaperFeed',(0,0,0),[trace])
        for x in [-.62,-.31,0,.31,.62]: line('Paper grid',[(x,-.76,.955),(x,.56,.955)],navy,.003)
    elif slug=='duewatch':
        cylinder('Clock pillar',(0,0,1.08),.12,1.5,brass)
        sphere('Sun',(0,0,1.95),.3,amber)
        for i,(r,tilt) in enumerate([(1.3,.35),(.98,-.55),(.65,1.0)]):
            before=set(scene.objects)
            ring('Orbit',(0,0,1.95),r,brass,(tilt,.18*i,0),.025)
            sphere('Planet',(r,0,1.95),.11+i*.025,ivory if i!=1 else red)
            pivot('OrbitPivot'+str(i),(0,0,1.95),set(scene.objects)-before)
        ring('Meridian',(0,0,1.95),1.48,brass,(math.pi/2,0,0))
        line('Clock axis',[(0,0,.5),(0,0,3.45)],brass,.022)
    else:
        box('Optical bench',(0,0,.55),(2.8,1.7,.28),navy)
        cylinder('Prism stand',(0,0,1.1),.15,1,brass)
        verts=[(math.cos(a)*.65,math.sin(a)*.65,z) for z in [1.35,2.55] for a in [0,math.tau/3,2*math.tau/3]]
        mesh=bpy.data.meshes.new('Prism'); mesh.from_pydata(verts,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]); mesh.update()
        prism=bpy.data.objects.new('Prism',mesh); scene.collection.objects.link(prism)
        glass=material('Prism blue',(.17,.42,.68),.65); finish(prism,'Prism',glass)
        for p in mesh.polygons: p.use_smooth=False
        pivot('PrismPivot',(0,0,1.95),[prism])
        box('Collimator',(-1.12,0,1.95),(.5,.4,.4),navy)
        line('Incident light',[(-1.05,0,1.95),(-.45,0,1.95)],ivory,.045)
        before=set(scene.objects)
        for i,col in enumerate([(.95,.15,.16),(.95,.43,.065),(.36,.89,.61),(.24,.58,.95)]):
            beam_mat=material('Spectrum'+str(i),col,.1,.85)
            line('Band'+str(i),[(.35,0,1.95),(1.35,-.6+i*.4,1.5+i*.22)],beam_mat,.036)
        pivot('SpectrumPivot',(0,0,1.95),set(scene.objects)-before)
        box('Sensor',(1.4,0,1.96),(.12,1.75,1.35),navy)
    bpy.context.view_layer.update()
    scene.render.filepath=str(ROOT/'assets/renders/full-observatory'/f'{slug}-review.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    # Convert only the newly built active scene; preserve moving parent groups.
    for o in list(scene.objects):
        if o.type not in {'MESH','CURVE'}: continue
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.convert(target='MESH')
    groups={}
    for o in scene.objects:
        if o.type=='MESH': groups.setdefault(o.parent,[]).append(o)
    for parent,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects: o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]; bpy.ops.object.join()
        objects[0].name=parent.name+'Mesh' if parent else slug+'Mount'
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'web/public/models'/f'{slug}.glb'),export_format='GLB',use_active_scene=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    return {'slug':slug,'objects':len(scene.objects),'bytes':(ROOT/'web/public/models'/f'{slug}.glb').stat().st_size}

if __name__=='__main__':
    if bpy.data.is_dirty: raise RuntimeError('Save existing GUI changes before building')
    result={'instruments': [make(slug) for slug in SLUGS]}
