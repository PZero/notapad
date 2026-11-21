"""Export per JLCPCB in kicad/jlc_out/: Gerber+drill ZIP, BOM e CPL (Economic PCBA, lato superiore).
Python di sistema:  python genera_jlc.py
"""
import csv, glob, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D

CLI = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe")
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
OUT = os.path.join(HERE, "jlc_out")
GDIR = os.path.join(OUT, "gerber")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(GDIR)


def run(*a):
    r = subprocess.run([CLI, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)


# ---- Gerber + drill ----
run("pcb", "export", "gerbers", "--output", GDIR + os.sep,
    "--layers", "F.Cu,B.Cu,F.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts",
    "--no-x2", "--subtract-soldermask", PCB)
run("pcb", "export", "drill", "--output", GDIR + os.sep, "--format", "excellon", "--drill-origin", "absolute",
    "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", PCB)
# DRC: se la scheda non è pulita il pacchetto Gerber viene marcato come BOZZA e non va ordinato
import json
drc = os.path.join(OUT, "_drc.json")
run("pcb", "drc", "--format", "json", "--refill-zones", "--schematic-parity", "-o", drc, PCB)
rep = json.load(open(drc, encoding="utf-8")); os.remove(drc)
n_unc = len(rep.get("unconnected_items", []))
n_err = sum(1 for v in rep.get("violations", []) if v.get("severity") == "error")
pulito = n_unc == 0 and n_err == 0
zpath = os.path.join(OUT, "notapad_v0.1_gerber.zip" if pulito else "notapad_v0.1_gerber_BOZZA_NON_ORDINARE.zip")
if not pulito:
    open(os.path.join(OUT, "NON_ORDINARE.txt"), "w", encoding="utf-8").write(
        f"Scheda NON pronta: {n_unc} collegamenti mancanti e {n_err} errori DRC.\n"
        "BOM e CPL sono validi (dipendono solo dal piazzamento); i Gerber sono una bozza.\n")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(os.path.join(GDIR, "*"))):
        z.write(f, os.path.basename(f))

# ---- posizioni dalla scheda (coordinate assolute come nei Gerber) ----
pos_csv = os.path.join(OUT, "_pos_kicad.csv")
run("pcb", "export", "pos", "--output", pos_csv, "--format", "csv", "--units", "mm", "--side", "front",
    "--exclude-fp-th", PCB)
pos = {r["Ref"]: r for r in csv.DictReader(open(pos_csv, encoding="utf-8"))}
os.remove(pos_csv)

# Correzioni di rotazione JLC (gradi da sommare) per impronta, se l'anteprima JLC lo richiede.
# Le impronte arrivano da EasyEDA/LCSC, quindi l'orientamento dovrebbe già essere quello JLC: tutto a 0.
ROT_FIX = {}

cpl, bom = [], {}
for ref, (fam, pads, _) in D.C.items():
    if fam in D.HAND:
        continue
    sym, fpn, lcsc, val = D.P[fam]
    p = pos[ref]
    rot = (float(p["Rot"]) + ROT_FIX.get(fpn, 0)) % 360
    cpl.append([ref, f'{float(p["PosX"]):.4f}mm', f'{float(p["PosY"]):.4f}mm', "Top", f"{rot:g}"])
    bom.setdefault((val, fpn, lcsc), []).append(ref)

key = lambda r: (r.rstrip("0123456789"), int("0" + "".join(c for c in r if c.isdigit())))
with open(os.path.join(OUT, "notapad_v0.1_CPL_JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    w.writerows(sorted(cpl, key=lambda r: key(r[0])))
with open(os.path.join(OUT, "notapad_v0.1_BOM_JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fpn, lcsc), refs in sorted(bom.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
        w.writerow([val, ",".join(sorted(refs, key=key)), fpn, lcsc])
print("DRC pulito" if pulito else f"ATTENZIONE: {n_unc} non connessi, {n_err} errori -> Gerber marcati BOZZA")
print("OK:", zpath, "|", len(cpl), "componenti nel CPL |", len(bom), "righe BOM")

# ---- aggiorna anche i file di riepilogo in ../jlc/ ----
J = os.path.join(HERE, "..", "jlc")
shutil.copy(os.path.join(OUT, "notapad_v0.1_BOM_JLC.csv"), os.path.join(J, "notapad_v0.1_BOM_JLC.csv"))
with open(os.path.join(J, "notapad_v0.1_collegamenti.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Net", "Collegamenti"])
    for net, items in sorted(D.nets().items()):
        w.writerow([net, " ; ".join(f"{r}.{p}" for r, p in sorted(items, key=lambda i: (key(i[0]), i[1])))])
print("aggiornati ../jlc/notapad_v0.1_BOM_JLC.csv e ../jlc/notapad_v0.1_collegamenti.csv")
