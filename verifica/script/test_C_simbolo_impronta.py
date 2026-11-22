"""Test C + B (parte): simbolo (lib) <-> impronta (.kicad_mod) <-> def.py <-> netlist kicad-cli <-> pcb.json
Uso: python test_C_simbolo_impronta.py <progetto> <cartella out>"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexpr import parse, find, child

prj, out = sys.argv[1], sys.argv[2]
kic = os.path.join(prj, "kicad")
sys.path.insert(0, kic)
import notapad_def as D

lib = parse(open(os.path.join(kic, "lib", "notapad.kicad_sym"), encoding="utf-8").read())
syms = {}
for s in lib[1:]:
    if isinstance(s, list) and s[0] == "symbol":
        pins = {}
        for p in find(s, "pin"):
            nm = child(p, "name"); nu = child(p, "number")
            if nm and nu:
                pins[nu[1]] = nm[1]
        syms[s[1]] = pins

fps = {}
for f in os.listdir(os.path.join(kic, "lib", "notapad.pretty")):
    t = parse(open(os.path.join(kic, "lib", "notapad.pretty", f), encoding="utf-8").read())
    pads = {}
    for p in find(t, "pad"):
        at = child(p, "at"); sz = child(p, "size")
        pads.setdefault(p[1], []).append({"type": p[2], "shape": p[3], "at": [float(v) for v in at[1:3]],
                                          "size": [float(v) for v in sz[1:3]] if sz else None})
    fps[f[:-10]] = pads

# netlist kicad-cli
nl = parse(open(os.path.join(out, "netlist.net"), encoding="utf-8").read())
net_nl = {}
for n in find(nl, "net"):
    nm = child(n, "name")
    if not nm:
        continue
    for nd in find(n, "node"):
        net_nl[(child(nd, "ref")[1], child(nd, "pin")[1])] = nm[1]
comp_nl = {}
for c in find(nl, "comp"):
    ref = child(c, "ref")[1]
    comp_nl[ref] = {"value": child(c, "value")[1], "footprint": child(c, "footprint")[1] if child(c, "footprint") else ""}

pcb = json.load(open(os.path.join(out, "pcb.json"), encoding="utf-8"))
pcbfp = {f["ref"]: f for f in pcb["footprints"]}

ris = []
problems = []
for ref, (fam, pads, pos) in sorted(D.C.items()):
    sym, fpn, lcsc, val = D.P[fam]
    sp = syms.get(sym, {})
    fpp = fps.get(fpn, {})
    rec = {"ref": ref, "sym": sym, "fp": fpn, "sym_pins": sp, "fp_pads": sorted(fpp)}
    fp_nums = {k for k in fpp if k}
    sym_nums = set(sp)
    if sym_nums and fp_nums and sym_nums != fp_nums:
        problems.append(f"{ref}: pin simbolo {sorted(sym_nums)} != pad impronta {sorted(fp_nums)}")
    # def.py vs netlist vs pcb
    for pad, net in pads.items():
        nn = net_nl.get((ref, pad))
        if nn is None or nn.lstrip("/") != net:
            problems.append(f"{ref}.{pad}: def={net} netlist={nn}")
        pp = [p for p in pcbfp[ref]["pads"] if p["num"] == pad]
        if not pp or any(p["net"] != net for p in pp):
            problems.append(f"{ref}.{pad}: def={net} pcb={[p['net'] for p in pp]}")
    # pad del pcb non in def (devono essere unconnected)
    for p in pcbfp[ref]["pads"]:
        if p["num"] not in pads and p["num"] and not p["net"].startswith("unconnected") and p["net"] != "":
            problems.append(f"{ref}.{p['num']}: rete {p['net']} sul pcb ma non in def")
    # posizione def vs pcb
    x, y, r = pos
    f = pcbfp[ref]
    if abs(f["x"] - 100 - x) > 0.005 or abs(f["y"] - 100 - y) > 0.005:
        problems.append(f"{ref}: posizione def ({x},{y}) pcb ({f['x']-100:.3f},{f['y']-100:.3f})")
    if (f["rot"] - r) % 360 > 0.01 and (r - f["rot"]) % 360 > 0.01:
        problems.append(f"{ref}: rotazione def {r} pcb {f['rot']}")
    if f["fpid"] != fpn:
        problems.append(f"{ref}: impronta def {fpn} pcb {f['fpid']}")
    if f["layer"] != "F.Cu":
        problems.append(f"{ref}: lato {f['layer']}")
    if ref in comp_nl and comp_nl[ref]["value"] != val:
        problems.append(f"{ref}: Value schema '{comp_nl[ref]['value']}' def '{val}'")
    rec["sym_names_by_pad_net"] = {pad: (sp.get(pad), net) for pad, net in pads.items()}
    ris.append(rec)

# componenti in netlist/pcb non in def
for ref in set(comp_nl) | set(pcbfp):
    if ref not in D.C:
        problems.append(f"{ref}: presente in netlist/pcb ma non in def")
json.dump({"componenti": ris, "problemi": problems}, open(os.path.join(out, "test_C.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
for r in ris:
    print(r["ref"], r["sym"], {k: v for k, v in r["sym_names_by_pad_net"].items()})
print("PROBLEMI:", len(problems))
for p in problems:
    print("  ", p)
