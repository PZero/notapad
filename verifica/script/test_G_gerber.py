"""Test G/A/F sui Gerber JLC: strati presenti, confronto con export fresco, via nel drill, keepout antenna,
contorno Edge_Cuts, serigrafia lato inferiore.
Uso: python test_G_gerber.py <cartella gerber zip estratto> <cartella gerber rigenerati> <out json>"""
import sys, os, re, json, glob

gdir, ndir, outp = sys.argv[1], sys.argv[2], sys.argv[3]
R = {}
need = ["F_Cu", "In1_Cu", "In2_Cu", "B_Cu", "F_Mask", "B_Mask", "F_Paste", "F_Silkscreen", "B_Silkscreen", "Edge_Cuts", "PTH.drl", "NPTH.drl"]
files = os.listdir(gdir)
R["strati_presenti"] = {n: any(n in f for f in files) for n in need}


def norm(path):
    out = []
    for l in open(path, encoding="utf-8", errors="replace"):
        if "CreationDate" in l or l.startswith("; DRILL file") or "Created by KiCad" in l or "date" in l.lower() and l.startswith("G04"):
            continue
        out.append(l.strip())
    return out


diff = {}
for f in files:
    base = re.sub(r"\.(gtl|g1|g2|gbl|gts|gbs|gtp|gto|gbo|gm1)$", "", f)
    cand = [c for c in os.listdir(ndir) if c.startswith(base + ".") or c == f]
    if not cand:
        continue
    a, b = norm(os.path.join(gdir, f)), norm(os.path.join(ndir, cand[0]))
    diff[f] = "identico" if a == b else f"DIVERSO ({len(a)} vs {len(b)} righe)"
R["confronto_export_fresco"] = diff

# drill
drl = open(glob.glob(os.path.join(gdir, "*-PTH.drl"))[0]).read()
tools = dict(re.findall(r"^T(\d+)C([\d.]+)", drl, re.M))
cnt, cur = {}, None
for l in drl.splitlines():
    m = re.match(r"^T(\d+)$", l)
    if m:
        cur = m.group(1); continue
    if l.startswith("X") and cur:
        cnt[tools[cur]] = cnt.get(tools[cur], 0) + 1
R["fori_PTH"] = cnt
npth = open(glob.glob(os.path.join(gdir, "*-NPTH.drl"))[0]).read()
R["fori_NPTH"] = len(re.findall(r"^X", npth, re.M))


def gerber_objs(path):
    """lista di (tipo, x, y, raggio_approx, aperture) in mm; regioni come bbox"""
    txt = open(path, encoding="utf-8", errors="replace").read()
    aps = {}
    for m in re.finditer(r"%ADD(\d+)([A-Za-z]+),([\d.X]+)", txt):
        dims = [float(v) for v in m.group(3).split("X") if v]
        aps[m.group(1)] = (m.group(2), dims)
    for m in re.finditer(r"%ADD(\d+)([A-Za-z_][\w]*)\*%", txt):
        aps.setdefault(m.group(1), (m.group(2), [0.5]))
    objs = []
    x = y = 0.0; ap = None; region = False; rpts = []
    for cmd in re.split(r"\*", txt):
        cmd = cmd.strip().lstrip("%")
        if cmd.startswith("G36"):
            region = True; rpts = []; continue
        if cmd.startswith("G37"):
            if rpts:
                xs = [p[0] for p in rpts]; ys = [p[1] for p in rpts]
                objs.append(("region", min(xs), min(ys), max(xs), max(ys), None))
            region = False; continue
        m = re.match(r"^D(\d+)$", cmd)
        if m and int(m.group(1)) >= 10:
            ap = m.group(1); continue
        m = re.match(r"^(?:G0?[123])?X(-?\d+)Y(-?\d+)(?:I-?\d+J-?\d+)?D0?([123])$", cmd)
        if not m:
            m2 = re.match(r"^(?:G0?[123])?(X(-?\d+))?(Y(-?\d+))?(?:I-?\d+J-?\d+)?D0?([123])$", cmd)
            if not m2:
                continue
            nx = int(m2.group(2)) / 1e6 if m2.group(2) else x
            ny = int(m2.group(4)) / 1e6 if m2.group(4) else y
            d = m2.group(5)
        else:
            nx, ny, d = int(m.group(1)) / 1e6, int(m.group(2)) / 1e6, m.group(3)
        if region:
            rpts.append((nx, ny))
        else:
            r = 0.0
            if ap in aps:
                r = max(aps[ap][1]) / 2 if aps[ap][1] else 0
            if d == "3":
                objs.append(("flash", nx - r, ny - r, nx + r, ny + r, ap))
            elif d == "1":
                objs.append(("draw", min(x, nx) - r, min(y, ny) - r, max(x, nx) + r, max(y, ny) + r, ap))
        x, y = nx, ny
    return objs


# keepout antenna: y_scheda > 32.8 mm -> Y gerber < -132.8 (origine KiCad 100,100, Y invertita)
KO = -132.8
ko = {}
for lay in ["F_Cu", "In1_Cu", "In2_Cu", "B_Cu"]:
    p = glob.glob(os.path.join(gdir, f"*-{lay}.*"))[0]
    objs = gerber_objs(p)
    inside = [o for o in objs if o[2] < KO - 0.001]
    ko[lay] = {"oggetti_totali": len(objs), "oggetti_in_keepout": len(inside),
               "dettaglio": [(o[0], round(o[1] - 100, 2), round(-o[4] - 100, 2), round(o[3] - 100, 2), round(-o[2] - 100, 2)) for o in inside][:20]}
R["keepout_antenna"] = ko

# contorno
eo = gerber_objs(glob.glob(os.path.join(gdir, "*-Edge_Cuts.*"))[0])
xs = [o[1] for o in eo] + [o[3] for o in eo]; ys = [o[2] for o in eo] + [o[4] for o in eo]
R["edge_bbox_mm"] = [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)]
eraw = open(glob.glob(os.path.join(gdir, "*-Edge_Cuts.*"))[0]).read()
R["edge_archi_G03_G02"] = len(re.findall(r"G0[23]", eraw)) + len(re.findall(r"I-?\d+J-?\d+D01", eraw))
# serigrafia retro
bs = gerber_objs(glob.glob(os.path.join(gdir, "*-B_Silkscreen.*"))[0])
fs = gerber_objs(glob.glob(os.path.join(gdir, "*-F_Silkscreen.*"))[0])
R["serigrafia"] = {"B_oggetti": len(bs), "F_oggetti": len(fs),
                   "B_bbox": [round(min(o[1] for o in bs) - 100, 2), round(-max(o[4] for o in bs) - 100, 2),
                              round(max(o[3] for o in bs) - 100, 2), round(-min(o[2] for o in bs) - 100, 2)] if bs else None}
# pasta: nessuna pasta sui pad a mano (retro non ha file pasta)
R["pasta_retro_presente"] = any("B_Paste" in f for f in files)
json.dump(R, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False)[:5000])
