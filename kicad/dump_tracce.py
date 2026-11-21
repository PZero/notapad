"""(python di KiCad) scrive tracce.json con piste, via e pad della scheda sbrogliata"""
import json, os, pcbnew
from pcbnew import ToMM
HERE = os.path.dirname(os.path.abspath(__file__)); OX = OY = 100.0
b = pcbnew.LoadBoard(os.path.join(HERE, "notapad_v0.1.kicad_pcb"))
T, V, PADS = [], [], []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        V.append([ToMM(t.GetPosition().x) - OX, ToMM(t.GetPosition().y) - OY, ToMM(t.GetWidth(pcbnew.F_Cu))])
    else:
        T.append([ToMM(t.GetStart().x) - OX, ToMM(t.GetStart().y) - OY, ToMM(t.GetEnd().x) - OX, ToMM(t.GetEnd().y) - OY,
                  ToMM(t.GetWidth()), t.GetLayer() == pcbnew.B_Cu])
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        PADS.append([ToMM(bb.GetX()) - OX, ToMM(bb.GetY()) - OY, ToMM(bb.GetWidth()), ToMM(bb.GetHeight()),
                     p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu)])
json.dump(dict(t=T, v=V, p=PADS), open(os.path.join(HERE, "tracce.json"), "w"))
print(len(T), "segmenti,", len(V), "via")
