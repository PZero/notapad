"""Test A: via dentro o a contatto con pad SMD (forma reale del pad, pcbnew HitTest) -> rischio di risucchio di stagno.
Uso: <KiCad>\\bin\\python.exe test_A_via_in_pad.py <pcb> <out json>"""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
res = []
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        for v in vias:
            r = v.GetWidth(pcbnew.F_Cu) // 2
            lay = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            sh = p.GetEffectivePolygon(lay)
            pos = v.GetPosition()
            centro = sh.Contains(pos)
            if centro or sh.Collide(pos, r):
                res.append({"pad": f"{fp.GetReference()}.{p.GetNumber()}", "net_pad": p.GetNetname(), "net_via": v.GetNetname(),
                            "via_mm": [round(pcbnew.ToMM(pos.x) - 100, 3), round(pcbnew.ToMM(pos.y) - 100, 3)],
                            "centro_nel_pad": bool(centro), "lato": b.GetLayerName(lay)})
json.dump(res, open(sys.argv[2], "w"), indent=1)
for r in res:
    print(r)
print(len(res), "contatti via-pad")
