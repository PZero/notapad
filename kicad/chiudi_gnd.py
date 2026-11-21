"""Passo finale dopo sbroglia.py + cuci_gnd.py (python di KiCad):  python.exe chiudi_gnd.py

(a) coppie GND scollegate con posizione nota (pad/pista/via): pistino diritto o a L da 0,15 mm sul lato superiore;
(b) isole del piano GND superiore senza via: una via dove isola e piano inferiore si sovrappongono.
Ogni aggiunta rispetta 0,1 mm da tutto il rame delle altre reti.
"""
import json, math, os, re, subprocess, sys
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import genera_pcb
import notapad_def as D
PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
CLI = os.path.join(os.path.dirname(sys.executable), "kicad-cli.exe")
OX, OY = genera_pcb.OX, genera_pcb.OY
ANT_TOP = OY + D.H - 5.2
CLR, W, VR = FromMM(0.1), FromMM(0.15), FromMM(0.225)


def drc():
    out = os.path.join(HERE, "routing", "drc_chiudi.json")
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--refill-zones", "-o", out, PCB], capture_output=True)
    return json.load(open(out, encoding="utf-8"))


def obstacles(b):
    ob = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() != "GND":
                for L in ob:
                    if p.IsOnLayer(L): ob[L].append(p.GetEffectiveShape(L))
    for t in b.GetTracks():
        if t.GetNetname() == "GND": continue
        for L in ob:
            if t.IsOnLayer(L): ob[L].append(t.GetEffectiveShape(L))
    return ob


def free(ob, L, shape):
    return not any(o.Collide(shape, CLR) for o in ob[L])


def clusters(b):
    """gruppi connessi della rete GND: isole dei piani, pad, piste, via (union-find geometrico)"""
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    def u(a, c): par[f(a)] = f(c)
    isl = []
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        L = z.GetLayer(); fp = z.GetFilledPolysList(L)
        for i in range(fp.OutlineCount()):
            s = pcbnew.SHAPE_POLY_SET(); s.AddOutline(fp.Outline(i))
            o = fp.Outline(i); bb = o.BBox(); pts = []
            step = FromMM(0.25); r = FromMM(0.2)
            y = bb.GetY()
            while y <= bb.GetBottom():
                x = bb.GetX()
                while x <= bb.GetRight():
                    c = VECTOR2I(int(x), int(y))
                    if all(s.Contains(VECTOR2I(int(x + r * math.cos(a)), int(y + r * math.sin(a))))
                           for a in (0, 1.5708, 3.1416, 4.7124, 0.785, 2.356, 3.927, 5.498)):
                        pts.append(c)
                    x += step
                y += step
            isl.append((("Z", L, i), L, s, pts))
    items = []
    for fpn in b.GetFootprints():
        for p in fpn.Pads():
            if p.GetNetname() == "GND": items.append((("P", fpn.GetReference(), p.GetNumber()), p))
    for t in b.GetTracks():
        if t.GetNetname() == "GND": items.append((("V" if t.GetClass() == "PCB_VIA" else "T", t.m_Uuid.AsString()), t))
    for k, it in items:
        f(k)
        for L in [l for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if b.IsLayerEnabled(l)]:
            if not it.IsOnLayer(L): continue
            sh = it.GetEffectiveShape(L)
            for zk, zl, s, _ in isl:
                if zl == L and s.Collide(sh, FromMM(0.005)): u(k, zk)
            for k2, it2 in items:
                if k2 != k and it2.IsOnLayer(L) and it2.GetEffectiveShape(L).Collide(sh, FromMM(0.005)): u(k, k2)
    for zk, *_ in isl: f(zk)
    groups = {}
    for k in par: groups.setdefault(f(k), []).append(k)
    # punti di aggancio per lato
    anchors = {}
    imap = dict(items); zmap = {zk: (zl, pts) for zk, zl, s, pts in isl}
    for root, ks in groups.items():
        A = []
        for k in ks:
            if k[0] == "Z":
                zl, pts = zmap[k]; A += [(zl, p) for p in pts]
            else:
                it = imap[k]
                if k[0] == "T":
                    A += [(it.GetLayer(), it.GetStart()), (it.GetLayer(), it.GetEnd())]
                else:
                    for L in (pcbnew.F_Cu, pcbnew.B_Cu):     # ancoraggi solo sui lati esterni
                        if it.IsOnLayer(L): A.append((L, it.GetPosition()))
        anchors[root] = A
    main = max(groups, key=lambda r: len(groups[r]))
    return groups, anchors, main


def main():
    b = pcbnew.LoadBoard(PCB)
    gnd = b.FindNet("GND")
    ob = obstacles(b)
    for giro in range(6):
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        groups, anchors, mainr = clusters(b)
        rest = [r for r in groups if r != mainr]
        print(f"giro {giro}: {len(rest)} gruppi GND staccati")
        if not rest:
            break
        joined = 0
        for r in rest:
            cand = []
            for r2 in groups:
                if r2 == r: continue
                for La, pa in anchors[r]:
                    for Lb, pb in anchors[r2]:
                        if La != Lb: continue
                        d = math.hypot(pa.x - pb.x, pa.y - pb.y)
                        if d < FromMM(6.0): cand.append((d, La, pa, pb))
            cand.sort(key=lambda c: c[0])
            ok = False
            for d, L, pa, pb in cand[:4000]:
                for path in ([pa, pb], [pa, VECTOR2I(pb.x, pa.y), pb], [pa, VECTOR2I(pa.x, pb.y), pb]):
                    if all(OX + 0.3 < ToMM(p.x) < OX + 16.2 and OY + 0.3 < ToMM(p.y) < ANT_TOP for p in path) and                        all(free(ob, L, pcbnew.SHAPE_SEGMENT(p, q, W)) for p, q in zip(path, path[1:])):
                        for p, q in zip(path, path[1:]):
                            if p == q: continue
                            t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q); t.SetWidth(W)
                            t.SetLayer(L); t.SetNet(gnd); b.Add(t)
                        ok = True; break
                if ok: break
            pads = [f"{k[1]}.{k[2]}" for k in groups[r] if k[0] == "P"]
            print("   ", pads or "isola", "->", "collegato" if ok else
                  f"NESSUN percorso (candidati {len(cand)}, min {ToMM(cand[0][0]) if cand else 0:.2f} mm)")
            joined += ok
            if ok:
                break          # ricalcola i gruppi dopo ogni unione
        if not joined:
            break
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    rep = drc()
    print("DRC:", len(rep.get("unconnected_items", [])), "non connessi,",
          sum(1 for v in rep.get("violations", []) if v.get("severity") == "error"), "errori")




# ---------------------------------------------------------------------------------------------
# Collegamenti a due lati: pista sul lato di A -> via libera su entrambi i lati -> pista sul lato di B
# ---------------------------------------------------------------------------------------------
class Ostacoli:
    """forme di rame per lato con bbox, per controlli rapidi; esclude la rete indicata"""
    def __init__(self, b, net):
        self.L = {l: [] for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if b.IsLayerEnabled(l)}
        self.holes = []
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetDrillSize().x > 0:
                    self.holes.append((p.GetPosition(), p.GetDrillSize().x / 2))
                if p.GetNetname() == net: continue
                for L in self.L:
                    if p.IsOnLayer(L): self.add(L, p.GetEffectiveShape(L))
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                self.holes.append((t.GetPosition(), t.GetDrill() / 2))
            if t.GetNetname() == net: continue
            for L in self.L:
                if t.IsOnLayer(L): self.add(L, t.GetEffectiveShape(L))

    def add(self, L, sh):
        bb = sh.BBox(); self.L[L].append((bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom(), sh))

    def free(self, L, sh):
        bb = sh.BBox(); m = CLR + FromMM(0.05)
        x0, y0, x1, y1 = bb.GetX() - m, bb.GetY() - m, bb.GetRight() + m, bb.GetBottom() + m
        for a, b_, c, d, o in self.L[L]:
            if c < x0 or a > x1 or d < y0 or b_ > y1: continue
            if o.Collide(sh, CLR): return False
        return True


def via_ok(ob, v):
    if not (OX + 0.6 < ToMM(v.x) < OX + 15.9 and OY + 0.6 < ToMM(v.y) < ANT_TOP - 0.3): return False
    c = pcbnew.SHAPE_CIRCLE(v, VR)
    if not all(ob.free(L, c) for L in ob.L): return False
    return all(math.hypot(v.x - h.x, v.y - h.y) > r + FromMM(0.125 + 0.2) for h, r in ob.holes)


def _legs(p, q):
    """percorsi diritto e a L da p a q"""
    return [[p, q], [p, VECTOR2I(q.x, p.y), q], [p, VECTOR2I(p.x, q.y), q]]


def _free_path(ob, L, path):
    return all(ob.free(L, pcbnew.SHAPE_SEGMENT(a, c, W)) for a, c in zip(path, path[1:]) if a != c)


def unisci_due_lati(b, net, pa, La, pb, Lb, ob, raggio=2.5):
    """cerca V tale che pa->V su La e V->pb su Lb (diritti o a L) siano liberi; aggiunge piste e via"""
    mx, my = (pa.x + pb.x) / 2, (pa.y + pb.y) / 2
    step = FromMM(0.15); R = FromMM(raggio); k = int(R / step)
    pts = []
    for i in range(-k, k + 1):
        for j in range(-k, k + 1):
            v = VECTOR2I(int(mx + i * step), int(my + j * step))
            pts.append((math.hypot(v.x - pa.x, v.y - pa.y) + math.hypot(v.x - pb.x, v.y - pb.y), v))
    pts.sort(key=lambda t: t[0])
    for d, v in pts:
        if not via_ok(ob, v): continue
        l1 = next((p for p in _legs(pa, v) if _free_path(ob, La, p)), None)
        if not l1: continue
        l2 = next((p for p in _legs(v, pb) if _free_path(ob, Lb, p)), None)
        if not l2: continue
        nobj = b.FindNet(net)
        via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetWidth(FromMM(0.45)); via.SetDrill(FromMM(0.25))
        via.SetNet(nobj); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); b.Add(via)
        for path, L in ((l1, La), (l2, Lb)):
            for a, c in zip(path, path[1:]):
                if a == c: continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(W); t.SetLayer(L); t.SetNet(nobj); b.Add(t)
        return True
    return False


def chiudi_tutto(max_giri=8):
    for giro in range(max_giri):
        b = pcbnew.LoadBoard(PCB)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        fatti = 0
        # (1) reti di segnale aperte: posizioni dal DRC
        rep = drc()
        for v in rep.get("unconnected_items", []):
            its = v["items"]
            m = re.search(r"\[([^\]]+)\]", its[0]["description"])
            if not m or m.group(1) == "GND": continue
            net = m.group(1)
            pa, pb = [VECTOR2I(FromMM(i["pos"]["x"]), FromMM(i["pos"]["y"])) for i in its]
            def strati(desc):
                if desc.startswith(("Via", "PTH", "Piazzola PTH")) or " - " in desc: return [pcbnew.F_Cu, pcbnew.B_Cu]
                if "F.Cu" in desc: return [pcbnew.F_Cu]
                if "B.Cu" in desc: return [pcbnew.B_Cu]
                return []          # elemento su uno strato interno: non lo tocco
            sa, sb = strati(its[0]["description"]), strati(its[1]["description"])
            ob = Ostacoli(b, net)
            dist = ToMM(math.hypot(pa.x - pb.x, pa.y - pb.y))
            chiuso = False
            comuni = [l for l in sa if l in sb]
            lp = next((p for L in comuni for p in _legs(pa, pb) if _free_path(ob, L, p)), None) if comuni else None
            if lp:
                for a, c in zip(lp, lp[1:]):
                    if a == c: continue
                    t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(W); t.SetLayer(comuni[0])
                    t.SetNet(b.FindNet(net)); b.Add(t)
                chiuso = True
            for La in sa:
                for Lb in sb:
                    if not chiuso and unisci_due_lati(b, net, pa, La, pb, Lb, ob, raggio=min(5.0, dist / 2 + 1.0)):
                        chiuso = True
            print("   segnale", net, "chiuso" if chiuso else f"aperto ({dist:.1f} mm)")
            fatti += chiuso
        # (2) gruppi GND: dal gruppo più piccolo verso qualsiasi altro
        groups, anchors, mainr = clusters(b)
        rest = sorted([r for r in groups if r != mainr], key=lambda r: len(groups[r]))
        print(f"giro {giro}: {len(rest)} gruppi GND staccati")
        ob = Ostacoli(b, "GND")
        for r in rest:
            cand = []
            for r2 in groups:
                if r2 == r: continue
                for La, pa in anchors[r]:
                    for Lb, pb in anchors[r2]:
                        d = math.hypot(pa.x - pb.x, pa.y - pb.y)
                        if d < FromMM(5.0): cand.append((d, La, pa, Lb, pb))
            cand.sort(key=lambda c: c[0])
            seen = set(); ok = False
            for d, La, pa, Lb, pb in cand:
                key = (round(pa.x / 2e5), round(pa.y / 2e5), round(pb.x / 2e5), round(pb.y / 2e5), La, Lb)
                if key in seen: continue
                seen.add(key)
                if len(seen) > 60: break
                lp = next((p for p in _legs(pa, pb) if _free_path(ob, La, p)), None) if La == Lb else None
                if lp:
                    for a, c in zip(lp, lp[1:]):
                        if a == c: continue
                        t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(W); t.SetLayer(La)
                        t.SetNet(b.FindNet("GND")); b.Add(t)
                    ok = True; break
                if unisci_due_lati(b, "GND", pa, La, pb, Lb, ob, raggio=min(2.5, ToMM(d) / 2 + 0.8)):
                    ok = True; break
            pads = [f"{k[1]}.{k[2]}" for k in groups[r] if k[0] == "P"]
            print("   ", pads or "isola", "->", "collegato" if ok else "nessun percorso")
            if ok:
                fatti += 1; break            # ricalcola i gruppi
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(PCB, b)
        if not fatti:
            break
    rep = drc()
    print("DRC:", len(rep.get("unconnected_items", [])), "non connessi,",
          sum(1 for v in rep.get("violations", []) if v.get("severity") == "error"), "errori")


if __name__ == "__main__":
    if "tutto" in sys.argv:
        chiudi_tutto()
    else:
        main()
