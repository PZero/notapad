"""Export di produzione in kicad/fab_out/{jlcpcb,pcbway,allpcb}/ (python di sistema):  python genera_fab.py

- Gerber RS-274X + drill Excellon (tutti gli strati di rame, anche quelli interni) in uno ZIP, uguale per i tre produttori
- JLCPCB: BOM (Comment, Designator, Footprint, LCSC Part #) e CPL (Designator, Mid X, Mid Y, Layer, Rotation)
- PCBWay / ALLPCB: BOM con produttore e MPN (dai simboli LCSC) + centroid
- LEGGIMI.md con le opzioni d'ordine
Se il DRC non è pulito (violazioni o collegamenti mancanti) gli ZIP vengono marcati BOZZA_NON_ORDINARE.
"""
import csv, glob, json, os, re, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D

CLI = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe")
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
FAB = os.path.join(HERE, "fab_out")
TMP = os.path.join(FAB, "_tmp")
# Cancella solo le cartelle che questo script rigenera: nextpcb/ e nextpcb_pannello52/ sono fatte da crea_scheda_51x51.py
for _s in ("jlcpcb", "pcbway", "allpcb", "_tmp"):
    shutil.rmtree(os.path.join(FAB, _s), ignore_errors=True)
os.makedirs(TMP, exist_ok=True)


def run(*a):
    r = subprocess.run([CLI, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)


# ---- DRC ----
drc = os.path.join(TMP, "drc.json")
run("pcb", "drc", "--format", "json", "--refill-zones", "--schematic-parity", "-o", drc, PCB)
rep = json.load(open(drc, encoding="utf-8"))
n_unc = len(rep.get("unconnected_items", []))
n_err = sum(1 for v in rep.get("violations", []) if v.get("severity") == "error")
n_par = len(rep.get("schematic_parity", []))
pulito = n_unc == 0 and n_err == 0 and n_par == 0
tag = "" if pulito else "_BOZZA_NON_ORDINARE"

# ---- Gerber + drill ----
GD = os.path.join(TMP, "gerber"); os.makedirs(GD)
rame = "F.Cu,In1.Cu,In2.Cu,B.Cu" if D.STRATI == 4 else "F.Cu,B.Cu"
run("pcb", "export", "gerbers", "--output", GD + os.sep,
    "--layers", rame + ",F.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts", "--no-x2", "--subtract-soldermask", PCB)
run("pcb", "export", "drill", "--output", GD + os.sep, "--format", "excellon", "--drill-origin", "absolute",
    "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", PCB)
zname = f"notapad_v0.1_gerber_{D.STRATI}strati{tag}.zip"
zsrc = os.path.join(TMP, zname)
with zipfile.ZipFile(zsrc, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(os.path.join(GD, "*"))):
        z.write(f, os.path.basename(f))

# ---- posizioni (coordinate assolute, come nei Gerber) ----
pos_csv = os.path.join(TMP, "pos.csv")
run("pcb", "export", "pos", "--output", pos_csv, "--format", "csv", "--units", "mm", "--side", "front", "--exclude-fp-th", PCB)
pos = {r["Ref"]: r for r in csv.DictReader(open(pos_csv, encoding="utf-8"))}

# ---- produttore e MPN dai simboli LCSC ----
lib = open(os.path.join(HERE, "lib", "notapad.kicad_sym"), encoding="utf-8").read()
def prop(sym, name):
    i = lib.find(f'(symbol "{sym}"')
    j = lib.find('\n  (symbol "', i + 10)
    m = re.search(r'"%s"\s+"([^"]*)"' % re.escape(name), lib[i:j if j > 0 else None])
    return m.group(1) if m else ""

key = lambda r: (r.rstrip("0123456789"), int("0" + "".join(c for c in r if c.isdigit())))
groups, cpl = {}, []
for ref, (fam, pads, _) in D.C.items():
    sym, fpn, lcsc, val = D.P[fam]
    groups.setdefault(fam, []).append(ref)
    if fam not in D.HAND:
        p = pos[ref]
        cpl.append([ref, f'{float(p["PosX"]):.4f}', f'{float(p["PosY"]):.4f}', "Top", f'{float(p["Rot"]) % 360:g}'])
cpl.sort(key=lambda r: key(r[0]))

VERIFICA = {"LED", "MIC", "NMOS2", "E73"}
rows_jlc, rows_full = [], []
for fam, refs in sorted(groups.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
    refs = sorted(refs, key=key)
    sym, fpn, lcsc, val = D.P[fam]
    if fam in D.HAND:
        rows_full.append([", ".join(refs), len(refs), "", "", val, fpn.replace("_", " "), "",
                          "DNP: non montare (montaggio a mano)"])
        continue
    manu = re.sub(r"\(.*?\)", "", prop(sym, "Manufacturer")).strip()
    mpn = prop(sym, "MPN") or sym
    note = []
    if not manu: note.append("produttore da verificare")
    if fam in VERIFICA: note.append("verificare l'orientamento a vista")
    rows_jlc.append([val, ",".join(refs), fpn, lcsc])
    rows_full.append([", ".join(refs), len(refs), manu, mpn, val, fpn, lcsc, "; ".join(note)])

LEGG = """notªpad v0.1 - file di produzione per {fab}
{stato}
Opzioni d'ordine
- Strati: {strati} (F.Cu segnali · In1 GND continuo · In2 segnali+alimentazioni · B.Cu segnali+GND) · spessore {sp} mm
- Dimensioni: {w} x {h} mm  ·  quantità: 5 PCB, 2 montate
- Finitura: HASL senza piombo (se disponibile)  ·  solder mask verde  ·  serigrafia bianca
- Assemblaggio: solo lato superiore (top). J1-J4, BT1P/BT1N, M1P/M1N, TPA/TPB NON vanno montati (DNP: montaggio a mano)
- Pista/spazio 0,10/0,10 mm (minimo JLC 4 strati 0,09) · via 0,25/0,45 mm foro/diametro (senza sovrapprezzo: JLC addebita i fori 0,2-0,25 solo con diametro < 0,45) · rame-bordo 0,25 mm (minimo JLC 0,2)
File
- {zip}: Gerber RS-274X + drill Excellon (PTH e NPTH separati)
- BOM e posizionamento: coordinate in mm, le stesse dei Gerber (origine del file KiCad), solo lato Top
{extra}"""
EXTRA_ALT = """Rotazioni nel centroid: sono quelle di KiCad con le impronte LCSC/EasyEDA (orientamento JLC).
Da verificare a vista nell'anteprima del produttore: LED D1-D3 (MHPA1010RGBDT, pin 1 = anodo),
microfoni MK1/MK2 (MSM261DGT003, foro in alto, pin 1 = VDD), Q2 (SOT-363 doppio), U1 (modulo E73, antenna verso il bordo basso).
"""
for fab in ("jlcpcb", "pcbway", "allpcb"):
    d = os.path.join(FAB, fab); os.makedirs(d)
    shutil.copy(zsrc, os.path.join(d, zname))
    if fab == "jlcpcb":
        with open(os.path.join(d, "notapad_v0.1_BOM_JLC.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writerows(rows_jlc)
        with open(os.path.join(d, "notapad_v0.1_CPL_JLC.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
            # Correzioni verificate nell'anteprima JLC (21/11/2026): il modello JLC del microfono
            # C48227730 ha il pin 1 opposto al pad 1 dell'impronta EasyEDA -> +180 gradi.
            JLC_ROT = {"MK": 180}
            def rot_jlc(ref, rot):
                off = next((v for k, v in JLC_ROT.items() if re.fullmatch(k + r"\d+", ref)), 0)
                return f'{(float(rot) + off) % 360:g}'
            w.writerows([[r[0], r[1] + "mm", r[2] + "mm", r[3], rot_jlc(r[0], r[4])] for r in cpl])
        extra = "Economic PCBA, codici LCSC già nella BOM. Controllare le rotazioni nell'anteprima JLC.\n"
    else:
        hdr = ["Item", "Designator", "Qty", "Manufacturer", "Manufacturer Part Number", "Description/Value", "Package", "LCSC (riferimento)", "Note"]
        rows = [[i + 1] + r for i, r in enumerate(rows_full)]
        with open(os.path.join(d, "notapad_v0.1_BOM.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
        try:
            import openpyxl
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "BOM"; ws.append(hdr)
            for r in rows: ws.append(r)
            wb.save(os.path.join(d, "notapad_v0.1_BOM.xlsx"))
        except ImportError:
            pass
        with open(os.path.join(d, "notapad_v0.1_centroid.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Designator", "Mid X (mm)", "Mid Y (mm)", "Layer", "Rotation"]); w.writerows(cpl)
        extra = EXTRA_ALT
    stato = "SCHEDA PRONTA: DRC pulito." if pulito else \
        f"ATTENZIONE: NON ORDINARE. DRC non pulito ({n_unc} collegamenti mancanti, {n_err} errori, {n_par} parità)."
    open(os.path.join(d, "LEGGIMI.md"), "w", encoding="utf-8").write(LEGG.format(
        fab=fab.upper(), stato=stato, strati=D.STRATI, sp=f"{D.SPESSORE:.1f}".replace(".", ","),
        w=f"{D.W:g}".replace(".", ","), h=f"{D.H:g}".replace(".", ","), zip=zname, extra=extra))
shutil.rmtree(TMP)

# riepiloghi in ../jlc/
J = os.path.join(HERE, "..", "jlc")
shutil.copy(os.path.join(FAB, "jlcpcb", "notapad_v0.1_BOM_JLC.csv"), os.path.join(J, "notapad_v0.1_BOM_JLC.csv"))
with open(os.path.join(J, "notapad_v0.1_collegamenti.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["Net", "Collegamenti"])
    for net, items in sorted(D.nets().items()):
        w.writerow([net, " ; ".join(f"{r}.{p}" for r, p in sorted(items, key=lambda i: (key(i[0]), i[1])))])
print("DRC pulito" if pulito else f"DRC NON pulito: {n_unc} non connessi, {n_err} errori, {n_par} parità -> BOZZA")
print("scritti:", ", ".join(sorted(os.listdir(FAB))))
