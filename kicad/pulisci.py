"""Toglie le via 'dangling' (collegate a un solo strato) segnalate dal DRC (python di KiCad):  python.exe pulisci.py"""
import json, os, subprocess, sys
import pcbnew
from pcbnew import FromMM
HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
CLI = os.path.join(os.path.dirname(sys.executable), "kicad-cli.exe")
out = os.path.join(HERE, "routing", "drc_pulisci.json")
subprocess.run([CLI, "pcb", "drc", "--format", "json", "--refill-zones", "-o", out, PCB], capture_output=True)
rep = json.load(open(out, encoding="utf-8"))
pos = [(it["pos"]["x"], it["pos"]["y"]) for v in rep["violations"] if v["type"] == "via_dangling" for it in v["items"]]
b = pcbnew.LoadBoard(PCB); n = 0
for t in list(b.GetTracks()):
    if t.GetClass() == "PCB_VIA" and any(abs(pcbnew.ToMM(t.GetPosition().x) - x) < 0.01 and abs(pcbnew.ToMM(t.GetPosition().y) - y) < 0.01 for x, y in pos):
        b.Remove(t); n += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(PCB, b)
print("via dangling tolte:", n)
