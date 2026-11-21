import bpy, math, sys
from mathutils import Vector

shot = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "hero"
import os
out = f"/home/claude/render/monolite_{shot}{('_'+os.environ['VAR']) if os.environ.get('VAR') else ''}.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
import os
sc.cycles.samples = int(os.environ.get("SPP","160"))
sc.cycles.use_denoising = True
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.render.resolution_percentage = int(os.environ.get("PCT","100"))
sc.render.resolution_x = 1400
sc.render.resolution_y = 1750 if shot != "back" else 1400
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX'
try:
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass

W, D, H = 17.0, 8.0, 38.0  # mm: larghezza X, spessore Y, altezza Z

def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]

# ---------- materiale resina nera con venature marroni ----------
resin, n, l, bs = mat("Resina")
tc = n.new("ShaderNodeTexCoord")
mp = n.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0.4, 0.9, 0.3)
wave = n.new("ShaderNodeTexWave"); wave.inputs["Scale"].default_value = 0.035
wave.inputs["Distortion"].default_value = 9.0; wave.inputs["Detail"].default_value = 9.0
wave.inputs["Detail Scale"].default_value = 1.6
noise = n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.12
noise.inputs["Detail"].default_value = 8.0
mix = n.new("ShaderNodeMix"); mix.data_type = 'FLOAT'; mix.inputs["Factor"].default_value = 0.35
ramp = n.new("ShaderNodeValToRGB")
cr = ramp.color_ramp
cr.elements[0].position = 0.30; cr.elements[0].color = (0.006, 0.004, 0.003, 1)
cr.elements[1].position = 0.64; cr.elements[1].color = (0.085, 0.040, 0.018, 1)
e = cr.elements.new(0.48); e.color = (0.022, 0.011, 0.006, 1)
e = cr.elements.new(0.82); e.color = (0.006, 0.004, 0.003, 1)
l.new(tc.outputs["Object"], mp.inputs["Vector"])
l.new(mp.outputs["Vector"], wave.inputs["Vector"])
l.new(mp.outputs["Vector"], noise.inputs["Vector"])
l.new(wave.outputs["Fac"], mix.inputs["A"])
l.new(noise.outputs["Fac"], mix.inputs["B"])
l.new(mix.outputs["Result"], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.22
bs.inputs["Coat Weight"].default_value = 1.0
bs.inputs["Coat Roughness"].default_value = 0.03
bs.inputs["Coat IOR"].default_value = 1.55


VAR = os.environ.get("VAR", "")
if VAR:
    for lk in list(l):
        if lk.to_socket == bs.inputs["Base Color"]:
            l.remove(lk)
    bs.inputs["Coat Weight"].default_value = 1.0; bs.inputs["Coat Roughness"].default_value = 0.04
    if VAR == "forged":
        mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
        vor = n.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 0.55
        vor.inputs["Randomness"].default_value = 1.0
        dn = n.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 0.25; dn.inputs["Detail"].default_value = 4
        mv = n.new("ShaderNodeMix"); mv.data_type = 'VECTOR'; mv.inputs["Factor"].default_value = 0.55
        l.new(mp.outputs["Vector"], mv.inputs[4]); l.new(dn.outputs["Color"], mv.inputs[5])
        l.new(mv.outputs[1], vor.inputs["Vector"])
        sep = n.new("ShaderNodeSeparateColor"); l.new(vor.outputs["Color"], sep.inputs["Color"])
        r2 = n.new("ShaderNodeValToRGB"); c2 = r2.color_ramp
        c2.elements[0].position = 0.0; c2.elements[0].color = (0.006, 0.006, 0.007, 1)
        c2.elements[1].position = 1.0; c2.elements[1].color = (0.16, 0.16, 0.17, 1)
        ee = c2.elements.new(0.55); ee.color = (0.02, 0.02, 0.022, 1)
        l.new(sep.outputs[0], r2.inputs["Fac"]); l.new(r2.outputs["Color"], bs.inputs["Base Color"])
        l.new(sep.outputs[1], bs.inputs["Metallic"])
        bs.inputs["Roughness"].default_value = 0.35
    else:
        cfg = {"matte": ((0.012, 0.012, 0.013), 0.0, 0.6, 0.0),
               "piano": ((0.004, 0.004, 0.005), 0.0, 0.05, 1.0),
               "anthracite": ((0.10, 0.105, 0.11), 0.7, 0.32, 1.0),
               "navy": ((0.004, 0.013, 0.04), 0.0, 0.25, 1.0),
               "ivory": ((0.72, 0.68, 0.60), 0.0, 0.4, 0.5)}[VAR]
        bs.inputs["Base Color"].default_value = (*cfg[0], 1)
        bs.inputs["Metallic"].default_value = cfg[1]; bs.inputs["Roughness"].default_value = cfg[2]
        bs.inputs["Coat Weight"].default_value = cfg[3]
    sc.render.filepath = ""

steel, *_x, b = mat("Acciaio")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.88, 1)
b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.09

gold, *_x, b = mat("Oro")
b.inputs["Base Color"].default_value = (1.0, 0.74, 0.32, 1)
b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.13

bronze, *_x, b = mat("BronzoScuro")
b.inputs["Base Color"].default_value = (0.32, 0.20, 0.11, 1)
b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.38

led, *_x, b = mat("LED")
b.inputs["Base Color"].default_value = (0.02, 0.03, 0.03, 1)
b.inputs["Roughness"].default_value = 0.05
if shot != "back":
    b.inputs["Emission Color"].default_value = (0.15, 0.85, 0.80, 1)
    b.inputs["Emission Strength"].default_value = 9.0

hole, *_x, b = mat("Foro")
b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1); b.inputs["Roughness"].default_value = 0.9

leather, *_x, b = mat("Cordino")
b.inputs["Base Color"].default_value = (0.012, 0.010, 0.009, 1); b.inputs["Roughness"].default_value = 0.55
b.inputs["Coat Weight"].default_value = 0.3

# ---------- corpo ----------
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.object; body.name = "Monolite"
body.scale = (W, D, H); bpy.ops.object.transform_apply(scale=True)
bv = body.modifiers.new("bevel", 'BEVEL'); bv.width = 1.1; bv.segments = 8; bv.limit_method = 'NONE'
body.data.materials.append(resin)
bpy.ops.object.shade_smooth()

def box(name, size, loc, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bm = o.modifiers.new("b", 'BEVEL'); bm.width = bevel; bm.segments = 6
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o

def cyl(name, r, depth, loc, rot, m, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=64)
    o = bpy.context.object; o.name = name
    if bevel:
        bm = o.modifiers.new("b", 'BEVEL'); bm.width = bevel; bm.segments = 5
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o

# intarsi laterali bronzo (zone tattili: si stringe sui due fianchi)
for sx in (-1, 1):
    box(f"Tocco{sx}", (0.10, 1.4, 17.0), (sx * (W / 2 + 0.01), 0, -1.5), bronze, bevel=0.04)

# fessura LED frontale
box("LED", (6.0, 0.10, 0.9), (0, -D / 2 - 0.01, 12.5), led, bevel=0.04)

# 4 contatti dorati sul retro, in riga
for i, x in enumerate((-5.4, -1.8, 1.8, 5.4)):
    cyl(f"Pin{i}", 0.85, 0.30, (x, D / 2 + 0.02, -13.0), (math.radians(90), 0, 0), gold, bevel=0.08)

# foro microfono sul fondo
cyl("Mic", 0.45, 0.4, (0, 0, -H / 2 + 0.05), (0, 0, 0), hole)

# anello in acciaio (piano YZ) ancorato in alto
ring_c = H / 2 + 2.4
bpy.ops.mesh.primitive_torus_add(major_radius=3.0, minor_radius=0.65, location=(0, 0, ring_c),
                                 rotation=(0, math.radians(90), 0), major_segments=96, minor_segments=32)
ring = bpy.context.object; ring.data.materials.append(steel); bpy.ops.object.shade_smooth()
# boccola metallica a filo della resina
cyl("Boccola", 1.6, 0.6, (0, 0, H / 2 + 0.05), (0, 0, 0), steel, bevel=0.15)

# cordino in cuoio che passa nell'anello
cz = ring_c + 3.0 - 0.65 - 0.75
curve = bpy.data.curves.new("cord", 'CURVE'); curve.dimensions = '3D'
curve.bevel_depth = 0.75; curve.bevel_resolution = 6
sp = curve.splines.new('BEZIER'); pts = [(-46, 1.0, 95), (-7, 0.4, cz + 4.0), (0, 0, cz), (7, -0.4, cz + 4.0), (46, -1.0, 95)]
sp.bezier_points.add(len(pts) - 1)
for p, c in zip(sp.bezier_points, pts):
    p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
cord = bpy.data.objects.new("Cordino", curve); sc.collection.objects.link(cord)
curve.materials.append(leather)

# ---------- set fotografico ----------
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.004, 0.005, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# fondale curvo
bpy.ops.mesh.primitive_plane_add(size=1)
bd = bpy.context.object; bd.name = "Fondale"
bdm, nn, ll, bb = mat("Fondale")
bb.inputs["Base Color"].default_value = (0.035, 0.032, 0.030, 1); bb.inputs["Roughness"].default_value = 0.6

def light(name, kind, loc, rot, energy, size, color=(1, 1, 1), size_y=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y or size
    o = bpy.data.objects.new(name, ld); o.location = loc; o.rotation_euler = rot
    sc.collection.objects.link(o); return o

def look_at(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam)
sc.camera = cam
cam_d.clip_start = 1; cam_d.clip_end = 5000
cam_d.dof.use_dof = True

if shot == "hero":
    # ciondolo sospeso, vista 3/4 frontale
    body.rotation_euler = (0, 0, math.radians(-24))
    for o in (ring,):
        pass
    bd.scale = (900, 900, 1); bd.location = (0, 260, 0); bd.rotation_euler = (math.radians(90), 0, 0)
    bd.data.materials.append(bdm)
    # tutti i pezzi ruotano col corpo
    for o in bpy.data.objects:
        if o.type in ('MESH',) and o not in (body, bd):
            o.parent = body
    ring.parent = body; cord.parent = None
    cam.location = (38, -205, 14); cam_d.lens = 105
    look_at(cam, (0, 0, 3))
    cam_d.dof.focus_distance = (Vector((0, 0, 0)) - cam.location).length - 2
    cam_d.dof.aperture_fstop = 5.6
    k = light("Key", 'AREA', (-140, -110, 120), (0, 0, 0), 9e5, 90, (1.0, 0.95, 0.88)); look_at(k, (0, 0, 0))
    r1 = light("RimR", 'AREA', (110, 120, 40), (0, 0, 0), 6e5, 12, (1.0, 0.82, 0.6), 160); look_at(r1, (0, 0, 0))
    r2 = light("RimL", 'AREA', (-120, 110, 10), (0, 0, 0), 4e5, 12, (0.75, 0.85, 1.0), 160); look_at(r2, (0, 0, 0))
    f = light("Fill", 'AREA', (90, -160, -60), (0, 0, 0), 1.2e5, 120, (1, 1, 1)); look_at(f, (0, 0, 0))
    # alone caldo sul fondale
    g = light("Glow", 'SPOT', (0, 120, 30), (0, 0, 0), 2.5e5, 0, (1.0, 0.55, 0.28)); look_at(g, (0, 260, 10))
    g.data.spot_size = math.radians(55); g.data.spot_blend = 1.0
elif shot == "back":
    # appoggiato su ardesia, mostra retro con contatti dorati
    cord.hide_render = True
    for o in bpy.data.objects:
        if o.type == 'MESH' and o not in (body, bd):
            o.parent = body
    body.rotation_euler = (math.radians(90), 0, math.radians(32))
    body.location = (0, 0, D / 2)
    bd.scale = (900, 900, 1); bd.location = (0, 0, 0)
    sl, n2, l2, b2 = mat("Ardesia")
    nz = n2.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08; nz.inputs["Detail"].default_value = 12
    bp = n2.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12
    l2.new(nz.outputs["Fac"], bp.inputs["Height"]); l2.new(bp.outputs["Normal"], b2.inputs["Normal"])
    cr2 = n2.new("ShaderNodeValToRGB"); cr2.color_ramp.elements[0].color = (0.010, 0.010, 0.011, 1)
    cr2.color_ramp.elements[1].color = (0.05, 0.048, 0.045, 1)
    l2.new(nz.outputs["Fac"], cr2.inputs["Fac"]); l2.new(cr2.outputs["Color"], b2.inputs["Base Color"])
    b2.inputs["Roughness"].default_value = 0.55
    bd.data.materials.append(sl)
    cam.location = (-38, -78, 66); cam_d.lens = 85
    look_at(cam, (0, 0, 2))
    cam_d.dof.focus_distance = (Vector((0, 0, 2)) - cam.location).length
    cam_d.dof.aperture_fstop = 4.0
    k = light("Key", 'AREA', (120, -60, 160), (0, 0, 0), 8e5, 80, (1.0, 0.93, 0.85)); look_at(k, (0, 0, 0))
    r1 = light("Rim", 'AREA', (-60, 140, 60), (0, 0, 0), 5e5, 15, (1.0, 0.8, 0.6), 140); look_at(r1, (0, 0, 0))
    f = light("Fill", 'AREA', (-150, -120, 60), (0, 0, 0), 1.0e5, 100, (0.8, 0.88, 1.0)); look_at(f, (0, 0, 0))
elif shot == "side":
    # profilo: mostra lo spessore 8 mm e l'intarsio tattile
    for o in bpy.data.objects:
        if o.type == 'MESH' and o not in (body, bd):
            o.parent = body
    body.rotation_euler = (0, 0, math.radians(-68))
    bd.scale = (900, 900, 1); bd.location = (0, 0, -H / 2 - 0.01)
    gl, n3, l3, b3 = mat("Vetro nero")
    b3.inputs["Base Color"].default_value = (0.006, 0.006, 0.007, 1); b3.inputs["Roughness"].default_value = 0.06
    bd.data.materials.append(gl)
    cord.hide_render = True
    cam.location = (70, -150, 10); cam_d.lens = 100
    look_at(cam, (0, 0, 2))
    cam_d.dof.focus_distance = (Vector((0, 0, 0)) - cam.location).length
    cam_d.dof.aperture_fstop = 5.6
    k = light("Key", 'AREA', (-120, -100, 130), (0, 0, 0), 1.6e6, 90, (1.0, 0.95, 0.88)); look_at(k, (0, 0, 0))
    r1 = light("Rim", 'AREA', (100, 120, 50), (0, 0, 0), 6e5, 12, (1.0, 0.8, 0.58), 150); look_at(r1, (0, 0, 0))
    r2 = light("Top", 'AREA', (0, 40, 180), (0, 0, 0), 4e5, 60, (1, 1, 1)); look_at(r2, (0, 0, 0))

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("SAVED", out)
