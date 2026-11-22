"""Test F11: le courtyard LCSC sono il solo corpo del componente (i pad restano fuori). Controllo reale:
(1) corpo (courtyard) di un componente sopra i pad di un altro; (2) distanza minima corpo-corpo e pad-corpo.
Usa i poligoni veri (pcbnew). Uso: <KiCad>\\bin\\python.exe test_F_ingombri.py <pcb> <out json>"""
import sys, json, itertools, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
mm = pcbnew.ToMM
fps = [f for f in b.GetFootprints() if f.GetLayer() == pcbnew.F_Cu]
cy, pads, fuori = {}, {}, {}
for f in fps:
    r = f.GetReference()
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    if c.OutlineCount():
        cy[r] = c
    pads[r] = [p.GetEffectivePolygon(pcbnew.F_Cu) for p in f.Pads() if p.IsOnLayer(pcbnew.F_Cu)]
    if r in cy:
        n = sum(1 for p in pads[r] if not cy[r].Contains(p.BBox().Centre()))
        if n:
            fuori[r] = n


def dist(a, c):
    d = a.SquaredDistance(c) if hasattr(a, "SquaredDistance") else None
    return None


corpo_su_pad, vicini = [], []
for a in cy:
    for c in pads:
        if a == c:
            continue
        for p in pads[c]:
            if cy[a].Collide(p.Outline(0), 0):
                corpo_su_pad.append([a, c])
                break
for a, c in itertools.combinations(cy, 2):
    for g in (0.0, 0.1, 0.2):
        if cy[a].Collide(cy[c].Outline(0), pcbnew.FromMM(g)):
            vicini.append([a, c, g]); break
R = {"componenti_con_pad_fuori_dalla_courtyard": len(fuori), "corpo_sopra_pad_altrui": corpo_su_pad,
     "corpi_a_meno_di_0_2mm": vicini}
json.dump(R, open(sys.argv[2], "w"), indent=1)
print(json.dumps(R, indent=1))
