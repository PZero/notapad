"""Test H: collegamenti.csv <-> netlist kicad-cli ; pinout.md <-> def.py ; cifre di CLAUDE.md/STATO.md <-> pcb.
Uso: python test_H_documenti.py <progetto> <out dir>"""
import sys, os, csv, json, re
prj, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(prj, "kicad"))
from sexpr import parse, find, child
import notapad_def as D
P = []
nl = parse(open(os.path.join(out, "netlist.net"), encoding="utf-8").read())
netl = {}
for n in find(nl, "net"):
    nm = child(n, "name")
    if nm and not nm[1].startswith("unconnected"):
        netl[nm[1].lstrip("/")] = sorted(f"{child(x, 'ref')[1]}.{child(x, 'pin')[1]}" for x in find(n, "node"))
col = {r["Net"]: sorted(s.strip() for s in r["Collegamenti"].split(";")) for r in
       csv.DictReader(open(os.path.join(prj, "jlc", "notapad_v0.1_collegamenti.csv"), encoding="utf-8"))}
for k in set(netl) | set(col):
    if netl.get(k) != col.get(k):
        P.append(f"rete {k}: netlist {netl.get(k)} csv {col.get(k)}")
# pinout.md: righe "| segnale | GPIO | pad |"
md = open(os.path.join(prj, "docs", "pinout_v0.1.md"), encoding="utf-8").read()
e73 = D.C["U1"][1]
MAP = {"QSPI_IO0": "QSPI_IO0", "QSPI_SCK": "QSPI_SCK", "QSPI_IO3": "QSPI_IO3", "QSPI_IO1": "QSPI_IO1", "QSPI_IO2": "QSPI_IO2",
       "QSPI_CS": "QSPI_CS", "PDM_CLK": "PDM_CLK", "PDM_DATA": "PDM_DATA", "TOUCH_A": "TOUCH_A", "TOUCH_B": "TOUCH_B",
       "MOTOR_G": "MOTOR_G", "HOLD": "HOLD", "VBAT_SENSE": "VBAT_SENSE", "NRESET": "NRESET",
       # 24/11: VBUS_SENSE e STAT tolti; nuovi segnali
       "VBUS": "VBUS", "I2C_SDA": "I2C_SDA", "I2C_SCL": "I2C_SCL", "MIC_WAKE": "MIC_WAKE", "BUZ_G": "BUZ_G"}
for line in md.splitlines():
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 3:
        continue
    sig = cells[0].split(" ")[0]
    pads = re.findall(r"\d+", cells[2])
    if sig in MAP and pads:
        if e73.get(pads[0]) != MAP[sig]:
            P.append(f"pinout.md {sig} pad {pads[0]} -> def {e73.get(pads[0])}")
    m = re.match(r"LED(\d) R / G / B", cells[0])
    if m and len(pads) == 3:
        i = m.group(1)
        for pad, col_ in zip(pads, "RGB"):
            if e73.get(pad) != f"D{i}_{col_}":
                P.append(f"pinout.md LED{i}{col_} pad {pad} -> def {e73.get(pad)}")
    if cells[0].startswith("SWDIO") and pads[:2] != ["37", "39"]:
        P.append("pinout SWD")
pcb = json.load(open(os.path.join(out, "pcb.json"), encoding="utf-8"))
nvia = len(pcb["vias"])
cl = open(os.path.join(prj, "CLAUDE.md"), encoding="utf-8").read()
st = open(os.path.join(prj, "docs", "STATO.md"), encoding="utf-8").read()
for nome, txt in (("CLAUDE.md", cl), ("STATO.md", st)):
    m = re.search(r"(\d+)\s*via", txt)
    if m and int(m.group(1)) != nvia:
        P.append(f"{nome}: {m.group(1)} via, pcb {nvia}")
mano = open(os.path.join(prj, "jlc", "notapad_v0.1_montaggio_a_mano.csv"), encoding="utf-8").read()
if "381620" not in mano:
    P.append("montaggio_a_mano.csv: batteria ancora '~3.5x16x19 ~60 mAh' (STATO.md indica 381620); J1..J4 'pin dorati' invece dei target 7,0 mm")
riga_stat = next((l for l in md.splitlines() if l.startswith("| STAT")), "")
chg_lcsc = D.P["CHG"][2]
if chg_lcsc == "C424093" and "pull-up interno" in riga_stat:
    P.append("pinout.md: STAT descritto come open-drain con pull-up interno, ma MCP73831 ha uscita tri-state (alto = VDD = 5 V)")
if chg_lcsc == "C38066" and ("MCP73832" not in riga_stat or "open-drain" not in riga_stat):
    P.append("pinout.md: la riga STAT non cita MCP73832 open-drain")
for nome, txt in (("CLAUDE.md", cl), ("STATO.md", st)):
    if chg_lcsc == "C38066" and "C424093" in txt and "MCP73832" not in txt:
        P.append(f"{nome}: cita ancora C424093/MCP73831 come caricatore")
an = json.load(open(os.path.join(prj, "kicad", "anteprima.json"), encoding="utf-8"))
bt = [o for o in an if o["ref"] == "BT1P"]
# il rettangolo del pad in anteprima.json è (x, y, w, h) dall'angolo: si confronta il centro
if bt and abs((cy := bt[0]["pads"][0][1] + bt[0]["pads"][0][3] / 2) - (pcb_y := [f for f in pcb["footprints"] if f["ref"] == "BT1P"][0]["y"] - 100)) > 0.3:
    P.append(f"kicad/anteprima.json non aggiornato (BT1P y {cy:.2f} vs pcb {pcb_y:.2f})")
# foro dei contatti e spessore del monolite nei documenti
drill_j = [f for f in pcb["footprints"] if f["ref"] == "J1"][0]["pads"][0]["drill"]
docs = {n: open(os.path.join(prj, *n.split("/")), encoding="utf-8").read() for n in ("CLAUDE.md", "docs/STATO.md", "docs/DOMANDE-APERTE.md", "docs/pinout_v0.1.md", "kicad/fab_out/jlcpcb/LEGGIMI.md")}
for n, txt in docs.items():
    if abs(drill_j - 1.1) < 1e-6 and re.search(r"fori[^.]{0,40}1,0 mm|1,0 mm di J1", txt):
        P.append(f"{n}: cita ancora i fori J1-J4 da 1,0 mm (pcb {drill_j})")
    if re.search(r"negli 8 mm|dentro gli 8 mm", txt):
        P.append(f"{n}: cita ancora lo spessore di 8 mm")
riga_bat = next((l for l in cl.splitlines() if l.startswith("- Strato sotto la scheda")), "")
if "381620" in st and "381620" not in riga_bat:
    P.append("montaggio/CLAUDE.md: la riga 'Strato sotto la scheda' cita ancora la cella ~3,5 x 16 x 19 (60 mAh), non la 381620")
json.dump({"problemi": P, "via_pcb": nvia}, open(os.path.join(out, "test_H.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\n".join(P) or "nessun problema")
