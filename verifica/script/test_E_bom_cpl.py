"""Test E: BOM/CPL JLC <-> pcb <-> def.py <-> BOM in jlc/ ; conteggio Extended; lato; posizioni e rotazioni.
Uso: python test_E_bom_cpl.py <progetto> <out dir>"""
import sys, os, csv, json, re
prj, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(prj, "kicad"))
import notapad_def as D
fab = os.path.join(prj, "kicad", "fab_out", "jlcpcb")
pcb = {f["ref"]: f for f in json.load(open(os.path.join(out, "pcb.json"), encoding="utf-8"))["footprints"]}
bom = list(csv.DictReader(open(os.path.join(fab, "notapad_v0.1_BOM_JLC.csv"), encoding="utf-8")))
cpl = list(csv.DictReader(open(os.path.join(fab, "notapad_v0.1_CPL_JLC.csv"), encoding="utf-8")))
bom2 = list(csv.DictReader(open(os.path.join(prj, "jlc", "notapad_v0.1_BOM_JLC.csv"), encoding="utf-8")))
P = []
bref = {}
for r in bom:
    for ref in r["Designator"].split(","):
        bref[ref.strip()] = r
b2ref = {}
for r in bom2:
    for ref in r[list(r.keys())[1]].split(","):
        b2ref[ref.strip()] = r
cref = {r["Designator"]: r for r in cpl}
hand = {ref for ref, (fam, _, _) in D.C.items() if fam in D.HAND}
smt = set(D.C) - hand
if set(bref) != smt:
    P.append(f"BOM refs diversi: mancanti {sorted(smt - set(bref))} in piu {sorted(set(bref) - smt)}")
if set(cref) != smt:
    P.append(f"CPL refs diversi: mancanti {sorted(smt - set(cref))} in piu {sorted(set(cref) - smt)}")
if set(b2ref) != set(bref):
    P.append(f"jlc/ BOM refs diversi da fab_out: {sorted(set(b2ref) ^ set(bref))}")
ROT_CORR = {"MIC": 180}  # correzione documentata in DECISIONI.md (21/11)
righe = []
for ref in sorted(smt):
    fam = D.C[ref][0]
    sym, fpn, lcsc, val = D.P[fam]
    b = bref.get(ref, {}); c = cref.get(ref, {})
    if b.get("LCSC Part #") != lcsc:
        P.append(f"{ref}: LCSC BOM {b.get('LCSC Part #')} def {lcsc}")
    if b.get("Footprint") != fpn:
        P.append(f"{ref}: footprint BOM {b.get('Footprint')} def {fpn}")
    f = pcb[ref]
    cx = float(c["Mid X"].replace("mm", "")); cy = float(c["Mid Y"].replace("mm", ""))
    if abs(cx - f["x"]) > 0.001 or abs(-cy - f["y"]) > 0.001:
        P.append(f"{ref}: CPL ({cx},{cy}) pcb ({f['x']},{-f['y']})")
    if c["Layer"] != "Top":
        P.append(f"{ref}: lato CPL {c['Layer']}")
    exp = (f["rot"] + ROT_CORR.get(fam, 0)) % 360
    if abs((float(c["Rotation"]) - exp) % 360) > 0.01:
        P.append(f"{ref}: rotazione CPL {c['Rotation']} attesa {exp} (pcb {f['rot']})")
    if f["value"] != val:
        P.append(f"{ref}: Value pcb '{f['value']}' def '{val}'")
    if b.get("Comment") != val:
        P.append(f"{ref}: Comment BOM '{b.get('Comment')}' def '{val}'")
    righe.append([ref, fam, lcsc, f["rot"], c["Rotation"], round(f["x"] - 100, 3), round(f["y"] - 100, 3)])
# controllo del CPL anche con il pos di kicad-cli (fonte indipendente)
pos = {r["Ref"]: r for r in csv.DictReader(open(os.path.join(out, "pos.csv"), encoding="utf-8"))}
for ref in smt:
    if ref not in pos:
        P.append(f"{ref}: assente nel pos kicad-cli")
        continue
    if abs(float(pos[ref]["PosX"]) - float(cref[ref]["Mid X"][:-2])) > 0.001 or abs(float(pos[ref]["PosY"]) - float(cref[ref]["Mid Y"][:-2])) > 0.001:
        P.append(f"{ref}: pos kicad-cli diverso dal CPL")
ext_fam = {"E73", "NAND", "CHG", "TTP", "LED", "NMOS2", "MIC", "MICZ", "ACC", "NMOSD"}  # 24/11: + VM3011, LIS2DH12, DMN2004DWK (da riconfermare sulle pagine)  # Extended verificati sulle pagine JLC
ext = sorted({D.P[D.C[r][0]][2] for r in smt if D.C[r][0] in ext_fam})
res = {"problemi": P, "righe": righe, "extended_codici": ext, "n_extended": len(ext),
       "n_righe_bom": len(bom), "n_cpl": len(cpl), "montati_a_mano": sorted(hand)}
json.dump(res, open(os.path.join(out, "test_E.json"), "w", encoding="utf-8"), indent=1)
print("problemi:", P); print("extended:", len(ext), ext); print(len(bom), "righe BOM,", len(cpl), "CPL")
