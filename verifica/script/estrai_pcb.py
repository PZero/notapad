"""Estrae dal .kicad_pcb (pcbnew di KiCad) footprint, pad, reti, courtyard, via, zone, contorno -> out/pcb.json
Uso: <KiCad>\\bin\\python.exe estrai_pcb.py <percorso .kicad_pcb> <cartella out>"""
import sys, json, os
import pcbnew

pcb_path, outdir = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(pcb_path)
mm = pcbnew.ToMM
ox, oy = 100.0, 100.0  # origine scheda nel file (angolo alto sinistro), verificata sotto dal contorno

out = {"footprints": [], "vias": [], "tracks": 0, "zones": [], "edge": None}
for fp in b.GetFootprints():
    pos = fp.GetPosition()
    d = {"ref": fp.GetReference(), "value": fp.GetValue(), "fpid": str(fp.GetFPID().GetLibItemName()),
         "x": mm(pos.x), "y": mm(pos.y), "rot": fp.GetOrientationDegrees(),
         "layer": b.GetLayerName(fp.GetLayer()), "attrs": fp.GetAttributes(),
         "dnp": fp.IsDNP(), "excl_bom": fp.IsExcludedFromBOM(), "excl_pos": fp.IsExcludedFromPosFiles(),
         "pads": [], "courtyard": None, "models": [m.m_Filename for m in fp.Models()]}
    for p in fp.Pads():
        pp = p.GetPosition(); sz = p.GetSize(pcbnew.F_Cu) if hasattr(p, "GetSize") else None
        try:
            sz = p.GetSize(pcbnew.PADSTACK.ALL_LAYERS)
        except Exception:
            try:
                sz = p.GetSize()
            except Exception:
                sz = None
        d["pads"].append({"num": p.GetNumber(), "net": p.GetNetname(), "x": mm(pp.x), "y": mm(pp.y),
                          "w": mm(sz.x) if sz else None, "h": mm(sz.y) if sz else None,
                          "drill": mm(p.GetDrillSize().x), "attr": int(p.GetAttribute()),
                          "layers": [b.GetLayerName(l) for l in p.GetLayerSet().Seq()]})
    for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        try:
            poly = fp.GetCourtyard(lay)
            if poly.OutlineCount():
                bb = poly.BBox()
                d.setdefault("cy", {})[b.GetLayerName(lay)] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
        except Exception as e:
            d["cy_err"] = str(e)
    out["footprints"].append(d)

for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        v = t
        out["vias"].append({"x": mm(v.GetPosition().x), "y": mm(v.GetPosition().y), "net": v.GetNetname(),
                            "drill": mm(v.GetDrillValue()), "dia": mm(v.GetWidth(pcbnew.F_Cu)) if True else None,
                            "type": int(v.GetViaType())})
    else:
        out["tracks"] += 1
widths = {}
for t in b.GetTracks():
    if t.GetClass() != "PCB_VIA":
        k = (t.GetNetname(), round(mm(t.GetWidth()), 3))
        widths[str(k)] = widths.get(str(k), 0) + 1
out["track_widths"] = widths

for z in b.Zones():
    zz = {"net": z.GetNetname(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
          "keepout": z.GetIsRuleArea(), "name": z.GetZoneName()}
    bb = z.GetBoundingBox(); zz["bbox"] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
    if z.GetIsRuleArea():
        zz.update({"no_tracks": z.GetDoNotAllowTracks(), "no_vias": z.GetDoNotAllowVias(),
                   "no_pads": z.GetDoNotAllowPads(), "no_copper_pour": z.GetDoNotAllowZoneFills(),
                   "no_fp": z.GetDoNotAllowFootprints()})
    else:
        polys = {}
        for l in z.GetLayerSet().Seq():
            fp_ = z.GetFilledPolysList(l)
            polys[b.GetLayerName(l)] = {"islands": fp_.OutlineCount(),
                                        "area_mm2": sum(abs(fp_.Outline(i).Area()) for i in range(fp_.OutlineCount())) / 1e12,
                                        "bboxes": [[mm(fp_.Outline(i).BBox().GetLeft()), mm(fp_.Outline(i).BBox().GetTop()),
                                                    mm(fp_.Outline(i).BBox().GetRight()), mm(fp_.Outline(i).BBox().GetBottom())]
                                                   for i in range(fp_.OutlineCount())]}
        zz["filled"] = polys
        zz["min_island_mm2"] = z.GetMinIslandArea() / 1e12 if hasattr(z, "GetMinIslandArea") else None
        zz["island_mode"] = int(z.GetIslandRemovalMode())
    out["zones"].append(zz)

edge = [d for d in b.GetDrawings() if b.GetLayerName(d.GetLayer()) == "Edge.Cuts"]
bb = b.GetBoardEdgesBoundingBox()
out["edge"] = {"bbox": [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
               "items": [(d.GetShapeTypeName() if hasattr(d, "GetShapeTypeName") else d.GetClass(),
                          mm(d.GetStart().x), mm(d.GetStart().y), mm(d.GetEnd().x), mm(d.GetEnd().y)) for d in edge]}
ds = b.GetDesignSettings()
out["design"] = {"copper_layers": b.GetCopperLayerCount(), "thickness": mm(ds.GetBoardThickness()),
                 "min_track": mm(ds.m_TrackMinWidth), "min_clear": mm(ds.m_MinClearance),
                 "min_via_dia": mm(ds.m_ViasMinSize), "min_via_drill": mm(ds.m_MinThroughDrill),
                 "min_annular": mm(ds.m_ViasMinAnnularWidth), "edge_clear": mm(ds.m_CopperEdgeClearance),
                 "hole_clear": mm(ds.m_HoleClearance), "hole_to_hole": mm(ds.m_HoleToHoleMin)}
texts = []
for d in b.GetDrawings():
    if d.GetClass() in ("PCB_TEXT", "PTEXT"):
        texts.append({"layer": b.GetLayerName(d.GetLayer()), "text": d.GetText(), "x": mm(d.GetPosition().x),
                      "y": mm(d.GetPosition().y), "h": mm(d.GetTextHeight()), "mirrored": d.IsMirrored()})
out["texts"] = texts
json.dump(out, open(os.path.join(outdir, "pcb.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out["footprints"]), "footprint,", len(out["vias"]), "via,", out["tracks"], "piste,", len(out["zones"]), "zone")
