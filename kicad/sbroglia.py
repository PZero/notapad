"""Sbroglio: esporta DSN, lancia Freerouting, reimporta SES, aggiunge piani GND, riempie, salva.
python di KiCad:  python.exe sbroglia.py [passate]"""
import os, subprocess, sys, time
import pcbnew
from pcbnew import FromMM
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
DSN = os.path.join(HERE, "routing", "notapad.dsn"); SES = DSN[:-3] + "ses"
JAR = r"C:\Users\fnico\tools\freerouting\freerouting-2.5.0.jar"
OX, OY = 100.0, 100.0
os.makedirs(os.path.dirname(DSN), exist_ok=True)
passes = sys.argv[1] if len(sys.argv) > 1 else "40"

import genera_pcb
genera_pcb.write_pro()
b = genera_pcb.build()            # scheda pulita: impronte, reti, keepout (niente piste)
pcbnew.SaveBoard(PCB, b)
b = pcbnew.LoadBoard(PCB)         # ricaricata per avere le regole del .kicad_pro
assert pcbnew.ExportSpecctraDSN(b, DSN), "export DSN fallito"
import re
variants = {"greedy": [], "random": ["-is", "random"], "seq": ["-is", "sequential"], "hybrid": ["-us", "hybrid"]}
procs = {}
t0 = time.time()
for name, extra in variants.items():
    ses = DSN[:-4] + "_" + name + ".ses"
    if os.path.exists(ses): os.remove(ses)
    log = open(os.path.join(HERE, "routing", "fr_" + name + ".log"), "w", encoding="utf-8")
    procs[name] = (subprocess.Popen(["java", "-Xmx700m", "-jar", JAR, "-de", DSN, "-do", ses, "-mp", passes, "-mt", "2",
                                     "-l", "en", "--gui.enabled=false", *extra], stdout=log, stderr=subprocess.STDOUT), ses, log)
best = None
for name, (pr, ses, log) in procs.items():
    pr.wait(); log.close()
    txt = open(log.name, encoding="utf-8", errors="replace").read()
    m = re.findall(r"\((\d+) unrouted and (\d+) violations\)", txt)
    unr = int(m[-1][0]) if m else 999
    print(f"  {name}: {unr} non sbrogliati", "" if os.path.exists(ses) else "(nessun SES)")
    if os.path.exists(ses) and (best is None or unr < best[0]):
        best = (unr, name, ses)
print("freerouting", round(time.time() - t0), "s -> scelto", best[1])
SES = best[2]
assert pcbnew.ImportSpecctraSES(b, SES), "import SES fallito"

# piani GND su entrambi i lati (fuori dal keepout antenna)
gnd = b.FindNet("GND")
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
    z.SetLocalClearance(FromMM(0.15)); z.SetMinThickness(FromMM(0.15))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.15)); z.SetThermalReliefSpokeWidth(FromMM(0.2))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline(); ol.NewOutline()
    for px, py in ((0, 0), (D.W, 0), (D.W, D.H), (0, D.H)):
        ol.Append(FromMM(OX + px), FromMM(OY + py))
    z.SetZoneName("GND_" + ("TOP" if layer == pcbnew.F_Cu else "BOT"))
    b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print("salvato con sbroglio:", PCB)
