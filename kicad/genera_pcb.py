"""Genera notapad_v0.1.kicad_pcb (contorno, impronte, reti, regole, keepout).
Da eseguire con il python di KiCad:  "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" genera_pcb.py
Le UUID dei simboli vengono lette da notapad_v0.1.kicad_sch (generato prima da genera_sch.py).
"""
import json, os, re, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D

OX, OY = 100.0, 100.0          # posizione dell'angolo alto-sinistro della scheda nel foglio
LIB = os.path.join(HERE, "lib", "notapad.pretty")
OUT = os.path.join(HERE, "notapad_v0.1.kicad_pcb")


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def sch_uuids():
    path = os.path.join(HERE, "notapad_v0.1.kicad_sch")
    if not os.path.exists(path):
        return {}, None
    s = open(path, encoding="utf-8").read()
    root = re.search(r'^\(kicad_sch[^\n]*\n\s*\(uuid "?([0-9a-f-]+)', s, re.M)
    m = {}
    for u, r in re.findall(r'\(uuid "?([0-9a-f-]+)"?\)\s*\(property "Reference" "([^"]+)"', s):
        m.setdefault(r, u)          # simboli a più unità: vale la prima
    return m, root.group(1) if root else None


def build():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(D.STRATI)
    b.SetCopperLayerCount(D.STRATI)
    ds.SetBoardThickness(FromMM(D.SPESSORE))
    if D.STRATI == 4:
        # stackup: F.Cu segnali / In1.Cu piano GND / In2.Cu segnali+alimentazioni / B.Cu segnali+GND
        b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
        b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_SIGNAL)
    # regole JLC 2 strati (verificate su jlcpcb.com/capabilities)
    ds.m_MinClearance = FromMM(0.1)
    ds.m_TrackMinWidth = FromMM(0.1)
    ds.m_ViasMinSize = FromMM(0.45)
    ds.m_MinThroughDrill = FromMM(0.25)
    ds.m_CopperEdgeClearance = FromMM(0.3)
    ds.m_HoleClearance = FromMM(0.2)
    ds.m_HoleToHoleMin = FromMM(0.25)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(0.1))
    nc.SetTrackWidth(FromMM(0.1))
    nc.SetViaDiameter(FromMM(0.45))
    nc.SetViaDrill(FromMM(0.25))
    ns = ds.m_NetSettings
    for name, width in (("PWR", 0.2), ("3V3", 0.15)):
        c = pcbnew.NETCLASS(name)
        c.SetClearance(FromMM(0.1)); c.SetTrackWidth(FromMM(width))
        c.SetViaDiameter(FromMM(0.45)); c.SetViaDrill(FromMM(0.25))
        ns.SetNetclass(name, c)
    for net in ("VBUS", "VBAT", "VSYS", "MOTOR_N"):
        ns.SetNetclassPatternAssignment(net, "PWR")
    ns.SetNetclassPatternAssignment("3V3", "3V3")

    # --- contorno con angoli raggiati ---
    r = D.CORNER_R
    w, h = D.W, D.H
    def seg(a, c):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.05))
        s.SetStart(P(*a)); s.SetEnd(P(*c)); b.Add(s)
    def arc(cx, cy, sx, sy, ang):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_ARC)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.05))
        s.SetCenter(P(cx, cy)); s.SetStart(P(sx, sy))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
        b.Add(s)
    seg((r, 0), (w - r, 0)); seg((w, r), (w, h - r)); seg((w - r, h), (r, h)); seg((0, h - r), (0, r))
    arc(w - r, r, w - r, 0, 90); arc(w - r, h - r, w, h - r, 90)
    arc(r, h - r, r, h, 90); arc(r, r, 0, r, 90)

    # --- reti ---
    ncn = json.load(open(os.path.join(HERE, "nc_nets.json")))
    netobj = {}
    for name in sorted(set(D.nets()) | set(ncn.values())):
        n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); netobj[name] = n

    uu, root = sch_uuids()
    for ref, (fam, pads, (x, y, rot)) in D.C.items():
        sym, fpname, lcsc, val = D.P[fam]
        fp = pcbnew.FootprintLoad(LIB, fpname)
        if fp is None:
            raise SystemExit("impronta mancante " + fpname)
        fp.SetFPID(pcbnew.LIB_ID("notapad", fpname))
        fp.SetReference(ref); fp.SetValue(val)
        fp.SetField("LCSC Part", lcsc)
        fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot)
        if ref in uu:
            fp.SetPath(pcbnew.KIID_PATH("/" + uu[ref]))
            fp.SetSheetname("Root"); fp.SetSheetfile("notapad_v0.1.kicad_sch")
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num in pads:
                pad.SetNet(netobj[pads[num]])
            elif f"{ref}.{num}" in ncn:
                pad.SetNet(netobj[ncn[f"{ref}.{num}"]])
        # serigrafia: riferimenti nascosti (scheda troppo piccola), restano in F.Fab
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(pcbnew.F_Fab)
        b.Add(fp)

    # --- keepout antenna: tutta la larghezza, dal bordo basso fino a dove finisce l'area pad del modulo ---
    ant_top = D.H - 5.2
    rame = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if D.STRATI == 4 else (pcbnew.F_Cu, pcbnew.B_Cu)
    for layer in rame:
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowFootprints(False)
        z.SetLayer(layer)
        ol = z.Outline(); ol.NewOutline()
        for px, py in ((0, ant_top), (w, ant_top), (w, h), (0, h)):
            ol.Append(FromMM(OX + px), FromMM(OY + py))
        z.SetZoneName("KEEPOUT_ANTENNA")
        b.Add(z)

    if D.STRATI == 4:
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.In1_Cu); z.SetNet(netobj["GND"])
        z.SetLocalClearance(FromMM(0.15)); z.SetMinThickness(FromMM(0.15))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline(); ol.NewOutline()
        for px, py in ((0, 0), (w, 0), (w, h), (0, h)):
            ol.Append(FromMM(OX + px), FromMM(OY + py))
        z.SetZoneName("GND_IN1"); b.Add(z)

    # --- testo sul retro ---
    t = pcbnew.PCB_TEXT(b)
    t.SetText("notªpad v0.1"); t.SetLayer(pcbnew.B_SilkS)
    t.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); t.SetTextThickness(FromMM(0.12))
    t.SetPosition(P(8.25, 22.5)); t.SetMirrored(True)
    b.Add(t)
    add_preroutes(b)
    place_previas(b)
    return b


def add_preroutes(b):
    """aggiunge (o riaggiunge dopo un import SES) i collegamenti PREROUTE"""
    vias_done = set()
    have_v = {(t.GetPosition().x, t.GetPosition().y) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"}
    have_t = {tuple(sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]))
              for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"}
    for entry in D.PREROUTE:
        net, (r1, n1), dst = entry[:3]
        way = entry[3] if len(entry) > 3 else []
        p1 = [p for p in b.FindFootprintByReference(r1).Pads() if p.GetNumber() == n1][0]
        if isinstance(dst[0], str):
            end = [p for p in b.FindFootprintByReference(dst[0]).Pads() if p.GetNumber() == dst[1]][0].GetPosition()
        else:
            dst = (dst[0], D.s(dst[1]))
            end = P(*dst)
            if dst not in vias_done and (end.x, end.y) not in have_v:
                v = pcbnew.PCB_VIA(b); v.SetPosition(end); v.SetWidth(FromMM(0.45)); v.SetDrill(FromMM(0.25))
                v.SetNet(b.FindNet(net)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetLocked(True); b.Add(v); vias_done.add(dst)
        pts = [p1.GetPosition()] + [P(w[0], D.s(w[1])) for w in way] + [end]
        key = tuple(sorted([(pts[0].x, pts[0].y), (pts[1].x, pts[1].y)]))
        if key in have_t:
            continue
        for a, c in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c)
            t.SetWidth(FromMM(0.15)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net))
            t.SetLocked(True)
            b.Add(t)


PREVIA_POS = {}   # (ref, pad) -> (x, y) scelti al primo build, riusati dopo ogni import SES


def place_previas(b):
    """via GND accanto ai pad di D.PREVIA: punto libero più vicino (solo pad e altre via come ostacoli)"""
    import math
    gnd = b.FindNet("GND")
    pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
    vias = [(ToMM(t.GetPosition().x) - OX, ToMM(t.GetPosition().y) - OY) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    lista = list(D.PREVIA)
    if getattr(D, "PREVIA_TUTTI_GND", False):
        for fp in b.GetFootprints():
            if fp.GetReference() == "U1": continue
            for q in fp.Pads():
                key = (fp.GetReference(), q.GetNumber())
                if q.GetNetname() == "GND" and q.IsOnLayer(pcbnew.F_Cu) and q.GetDrillSize().x == 0                         and key != ("U2", "9") and key not in lista:
                    lista.append(key)
    for ref, num in lista:
        pad = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]
        layer = pcbnew.B_Cu if not pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.F_Cu
        if (ref, num) not in PREVIA_POS:
            px, py = ToMM(pad.GetPosition().x) - OX, ToMM(pad.GetPosition().y) - OY
            bb = pad.GetBoundingBox(); r0 = max(ToMM(bb.GetWidth()), ToMM(bb.GetHeight())) / 2
            best = None; r = r0 + 0.28
            while best is None and r < r0 + 1.6:
                for k in range(48):
                    a = 2 * math.pi * k / 48
                    x, y = px + r * math.cos(a), py + r * math.sin(a)
                    if not (0.6 < x < D.W - 0.6 and 0.6 < y < D.H - 5.6):
                        continue
                    if any(math.hypot(x - vx, y - vy) < 0.75 for vx, vy in vias):
                        continue
                    c = pcbnew.SHAPE_CIRCLE(P(x, y), FromMM(0.225))
                    seg = pcbnew.SHAPE_SEGMENT(pad.GetPosition(), P(x, y), FromMM(0.15))
                    bad = False
                    for q in pads:
                        if q.GetNetname() == "GND":
                            if q.GetEffectiveShape(pcbnew.F_Cu).Collide(c, FromMM(0.05)) and q is not pad:
                                bad = True; break
                            continue
                        for L in (pcbnew.F_Cu, pcbnew.B_Cu):
                            if q.IsOnLayer(L) and q.GetEffectiveShape(L).Collide(c, FromMM(0.12)):
                                bad = True; break
                        if not bad and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(seg, FromMM(0.12)):
                            bad = True
                        if bad: break
                    if not bad:
                        best = (x, y); break
                r += 0.05
            if best is None:
                PREVIA_POS[(ref, num)] = None
            if best is None:
                continue
            PREVIA_POS[(ref, num)] = best
        if PREVIA_POS[(ref, num)] is None:
            continue
        x, y = PREVIA_POS[(ref, num)]
        vias.append((x, y))
        if not any(t.GetClass() == "PCB_VIA" and t.GetPosition() == P(x, y) for t in b.GetTracks()):
            v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(FromMM(0.45)); v.SetDrill(FromMM(0.25))
            v.SetNet(gnd); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetLocked(True); b.Add(v)
        if not any(t.GetClass() == "PCB_TRACK" and {(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)} ==
                   {(pad.GetPosition().x, pad.GetPosition().y), (P(x, y).x, P(x, y).y)} for t in b.GetTracks()):
            t = pcbnew.PCB_TRACK(b); t.SetStart(pad.GetPosition()); t.SetEnd(P(x, y)); t.SetWidth(FromMM(0.15))
            t.SetLayer(layer); t.SetNet(gnd); t.SetLocked(True); b.Add(t)


def dump(b, path):
    """geometria per l'anteprima matplotlib"""
    out = []
    for fp in b.GetFootprints():
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
        pads = []
        for p in fp.Pads():
            pb = p.GetBoundingBox()
            pads.append([ToMM(pb.GetX()) - OX, ToMM(pb.GetY()) - OY, ToMM(pb.GetWidth()), ToMM(pb.GetHeight()),
                         p.GetNetname(), p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu)])
        out.append(dict(ref=fp.GetReference(), x=ToMM(bb.GetX()) - OX, y=ToMM(bb.GetY()) - OY,
                        w=ToMM(bb.GetWidth()), h=ToMM(bb.GetHeight()), pads=pads))
    json.dump(out, open(path, "w"), indent=0)


def write_pro():
    """regole di progetto nel .kicad_pro (pcbnew standalone non lo salva)"""
    pro = {
        "meta": {"filename": "notapad_v0.1.kicad_pro", "version": 3},
        "board": {"design_settings": {
            "rules": {"min_clearance": 0.1, "min_track_width": 0.1, "min_via_diameter": 0.45,
                      "min_via_annular_width": 0.1, "min_through_hole_diameter": 0.25, "min_hole_clearance": 0.2,
                      "min_hole_to_hole": 0.2, "min_copper_edge_clearance": 0.25, "min_silk_clearance": 0.0,
                      "solder_mask_to_copper_clearance": 0.0, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1},
            "rule_severities": {"silk_overlap": "ignore", "silk_over_copper": "ignore", "silk_edge_clearance": "ignore",
                                "text_height": "ignore", "text_thickness": "ignore", "lib_footprint_issues": "ignore"},
            "track_widths": [0.0, 0.127, 0.2, 0.3], "via_dimensions": [{"diameter": 0.0, "drill": 0.0},
                                                                         {"diameter": 0.45, "drill": 0.25}]}},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.1, "track_width": 0.1, "via_diameter": 0.45, "via_drill": 0.25,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "priority": 2147483647},
                {"name": "PWR", "clearance": 0.1, "track_width": 0.2, "via_diameter": 0.45, "via_drill": 0.25, "priority": 0},
                {"name": "3V3", "clearance": 0.1, "track_width": 0.15, "via_diameter": 0.45, "via_drill": 0.25, "priority": 1}],
            "meta": {"version": 4},
            "netclass_patterns": [{"netclass": "PWR", "pattern": n} for n in ("VBUS", "VBAT", "VSYS", "MOTOR_N")]
                                 + [{"netclass": "3V3", "pattern": "3V3"}]},
        "schematic": {"meta": {"version": 1}},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    }
    json.dump(pro, open(os.path.join(HERE, "notapad_v0.1.kicad_pro"), "w"), indent=2)


if __name__ == "__main__":
    write_pro()
    b = build()
    pcbnew.SaveBoard(OUT, b)
    dump(b, os.path.join(HERE, "anteprima.json"))
    print("salvato", OUT)
