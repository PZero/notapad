"""Collega al GND i pad di massa rimasti su isole di piano (python di KiCad):  python.exe cuci_gnd.py

Ripete fino a 4 volte: DRC (kicad-cli, JSON) -> pad GND non connessi -> per ciascuno la via più vicina
(con pistino da 0,15 mm sul lato del pad) che rispetta 0,1 mm da tutto il rame delle altre reti -> riempie i piani.
Alla fine toglie le isole di rame rimaste scollegate.
"""
import json, math, os, re, subprocess, sys
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D
import genera_pcb

PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
CLI = os.path.join(os.path.dirname(sys.executable), "kicad-cli.exe")   # accanto al python di KiCad
OX, OY = genera_pcb.OX, genera_pcb.OY
ANT_TOP = D.H - 5.2
VIA_D, VIA_DRILL, CLR, TRACK_W = 0.45, 0.25, 0.1, 0.15


def drc_unconnected_gnd():
    out = os.path.join(HERE, "routing", "drc_cuci.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--refill-zones", "-o", out, PCB],
                   capture_output=True)
    rep = json.load(open(out, encoding="utf-8"))
    pads = set()
    for v in rep.get("unconnected_items", []):
        for it in v.get("items", []):
            m = re.search(r"(?:Pad|Piazzola|PTH pad|Piazzola PTH|piazzola PTH)\s+(\S+) \[GND\] (?:of|di) (\S+)",
                          it.get("description", ""))
            if m:
                pads.add((m.group(2), m.group(1)))
    return pads, len(rep.get("unconnected_items", []))


def main():
    for it in range(4):
        pads, n = drc_unconnected_gnd()
        print(f"giro {it}: {n} non connessi, pad GND da cucire: {len(pads)}")
        if not pads:
            break
        b = pcbnew.LoadBoard(PCB)
        gnd = b.FindNet("GND")
        LAYS = [l for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if b.IsLayerEnabled(l)]
        obst = {l: [] for l in LAYS}; obst["gndpad"] = []
        holes, gvias = [], []
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetDrillSize().x > 0:
                    holes.append((ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetDrillSize().x) / 2))
                for L in LAYS:
                    if p.IsOnLayer(L) and p.GetNetname() != "GND":
                        obst[L].append(p.GetEffectiveShape(L))
                # anche i pad GND sono ostacoli per la via (niente via nei pad)
                if p.GetNetname() == "GND" and p.IsOnLayer(pcbnew.F_Cu):
                    obst["gndpad"].append(p.GetEffectiveShape(pcbnew.F_Cu))
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                x, y = ToMM(t.GetPosition().x), ToMM(t.GetPosition().y)
                if t.GetNetname() == "GND":
                    gvias.append((x, y))
                else:
                    holes.append((x, y, ToMM(t.GetDrill()) / 2))
                    for L in LAYS:
                        obst[L].append(t.GetEffectiveShape(L))
            elif t.GetNetname() != "GND":
                obst[t.GetLayer()].append(t.GetEffectiveShape(t.GetLayer()))

        def free(shape, layer, clr=CLR):
            c = FromMM(clr)
            return not any(o.Collide(shape, c) for o in obst[layer])

        added = 0
        for ref, num in sorted(pads):
            fp = b.FindFootprintByReference(ref)
            pad = [p for p in fp.Pads() if p.GetNumber() == num and p.GetNetname() == "GND"][0]
            layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            px, py = ToMM(pad.GetPosition().x), ToMM(pad.GetPosition().y)
            bb = pad.GetBoundingBox(); r0 = math.hypot(ToMM(bb.GetWidth()), ToMM(bb.GetHeight())) / 2
            best = None
            P0 = pad.GetPosition()

            def path_ok(pts):
                for a, c in zip(pts, pts[1:]):
                    seg = pcbnew.SHAPE_SEGMENT(a, c, FromMM(TRACK_W))
                    if not free(seg, layer):
                        return False
                return True

            def l_paths(x, y):
                T = VECTOR2I(FromMM(x), FromMM(y))
                return [[P0, T], [P0, VECTOR2I(T.x, P0.y), T], [P0, VECTOR2I(P0.x, T.y), T]]

            # (a) via GND già esistente entro 3 mm, raggiunta con un pistino dritto o a L
            for vx, vy in sorted(gvias, key=lambda v: math.hypot(v[0] - px, v[1] - py)):
                if math.hypot(vx - px, vy - py) > 3.0:
                    break
                for pts in l_paths(vx, vy):
                    if path_ok(pts):
                        best = ("esistente", pts); break
                if best: break
            # (b) via nuova entro 3 mm
            r = r0 + 0.3
            while best is None and r < r0 + 3.0:
                for k in range(36):
                    a = 2 * math.pi * k / 36
                    x, y = px + r * math.cos(a), py + r * math.sin(a)
                    bx, by = x - OX, y - OY
                    if not (0.55 < bx < D.W - 0.55 and 0.55 < by < ANT_TOP - 0.3):
                        continue
                    if any(math.hypot(x - hx, y - hy) < hr + VIA_DRILL / 2 + 0.25 for hx, hy, hr in holes):
                        continue
                    if any(math.hypot(x - vx, y - vy) < VIA_D + 0.05 for vx, vy in gvias):
                        continue
                    c = pcbnew.SHAPE_CIRCLE(VECTOR2I(FromMM(x), FromMM(y)), FromMM(VIA_D / 2))
                    if not all(free(c, L) for L in LAYS):
                        continue
                    if any(g.Collide(c, 0) for g in obst["gndpad"]):
                        continue
                    for pts in l_paths(x, y):
                        if path_ok(pts):
                            best = ("nuova", pts); break
                    if best: break
                r += 0.1
            if best is None:
                print(f"  {ref}.{num}: nessun collegamento possibile entro 3 mm")
                continue
            kind, pts = best
            if kind == "nuova":
                end = pts[-1]
                v = pcbnew.PCB_VIA(b); v.SetPosition(end)
                v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DRILL)); v.SetNet(gnd)
                v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                b.Add(v); gvias.append((ToMM(end.x), ToMM(end.y)))
            for a, c in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c)
                t.SetWidth(FromMM(TRACK_W)); t.SetLayer(layer); t.SetNet(gnd); b.Add(t)
            print(f"  {ref}.{num}: collegato a via {kind}")
            added += 1
        print(f"  aggiunte {added} via")
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(PCB, b)
        if not added:
            break
    # isole di rame rimaste senza collegamento: via
    b = pcbnew.LoadBoard(PCB)
    for z in b.Zones():
        if not z.GetIsRuleArea():
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    pads, n = drc_unconnected_gnd()
    print("finale:", n, "non connessi")


if __name__ == "__main__":
    main()
