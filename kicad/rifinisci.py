"""Rifinitura (python di KiCad):  python.exe rifinisci.py [passate] [protect]

Riparte dalla scheda gia' sbrogliata: riesporta il DSN con le piste esistenti, rilancia Freerouting
(le piste esistenti possono essere rifatte, salvo con 'protect') per chiudere i collegamenti rimasti aperti,
reimporta, porta a 0,1 mm le strozzature, riempie i piani. Poi si lancia chiudi_gnd.py tutto.
"""
import os, re, subprocess, sys, time
import pcbnew
from pcbnew import FromMM
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import notapad_def as D
import genera_pcb
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
RDIR = os.path.join(HERE, "routing")
DSN = os.path.join(RDIR, "rif.dsn")
JAR = os.environ.get("FREEROUTING_JAR") or os.path.join(os.path.expanduser("~"), "tools", "freerouting", "freerouting-2.5.0.jar")
passes = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].isdigit() else "60"
b = pcbnew.LoadBoard(PCB)
assert pcbnew.ExportSpecctraDSN(b, DSN)
d = open(DSN, encoding="utf-8").read()
d = re.sub(r'^\(pcb "[^"]*"', '(pcb "rif.dsn"', d, count=1)
if "protect" in sys.argv:
    d = d.replace("(type route)", "(type protect)")
d = d.replace("(clearance 100)", "(clearance 115)")
open(DSN, "w", encoding="utf-8").write(d)
procs = {}
for name, extra in (("greedy", []), ("random", ["-is", "random"]), ("seq", ["-is", "sequential"]), ("hybrid", ["-us", "hybrid"])):
    ses = os.path.join(RDIR, f"rif_{name}.ses")
    if os.path.exists(ses): os.remove(ses)
    log = open(os.path.join(RDIR, f"fr_rif_{name}.log"), "w", encoding="utf-8")
    procs[name] = (subprocess.Popen(["java", "-Xmx700m", "-jar", JAR, "-de", DSN, "-do", ses, "-mp", passes, "-mt", "2",
                                     "-l", "en", "--gui.enabled=false", *extra], stdout=log, stderr=subprocess.STDOUT), ses, log)
best = None
for name, (pr, ses, log) in procs.items():
    pr.wait(); log.close()
    txt = open(log.name, encoding="utf-8", errors="replace").read()
    m = re.findall(r"\((\d+) unrouted and (\d+) violations\)", txt)
    unr = int(m[-1][0]) if m else 999
    print(f"  rif/{name}: {unr} non sbrogliati")
    if os.path.exists(ses) and (best is None or unr < best[0]): best = (unr, name, ses)
print("scelto", best[1])
assert pcbnew.ImportSpecctraSES(b, best[2])
# strozzature a 0,1 mm
n = 0
for t in b.GetTracks():
    if t.GetClass() != "PCB_VIA" and t.GetWidth() < FromMM(0.1):
        t.SetWidth(FromMM(0.1)); n += 1
print("piste allargate:", n)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
