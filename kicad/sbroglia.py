"""Sbroglio di notapad_v0.1 (python di KiCad):  python.exe sbroglia.py [passate]

1. rigenera la scheda pulita da genera_pcb (impronte, reti, regole, keepout antenna)
2. esporta il DSN e TOGLIE la rete GND: GND non si sbroglia a piste, la portano i piani
3. lancia Freerouting con 4 strategie in parallelo e tiene la migliore
4. reimporta, porta a 0,1 mm le piste strozzate, aggiunge piani GND sopra e sotto,
   cuce i due piani con via messe solo dove entrambi i riempimenti coprono il foro
"""
import math, os, re, subprocess, sys, time
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D
import genera_pcb

PCB = os.path.join(HERE, "notapad_v0.1.kicad_pcb")
RDIR = os.path.join(HERE, "routing"); os.makedirs(RDIR, exist_ok=True)
DSN = os.path.join(RDIR, "notapad.dsn")
ROUTED = os.path.join(RDIR, "routed.kicad_pcb")
# Freerouting: variabile d'ambiente FREEROUTING_JAR, altrimenti %USERPROFILE%\tools\freerouting\freerouting-2.5.0.jar
JAR = os.environ.get("FREEROUTING_JAR") or os.path.join(os.path.expanduser("~"), "tools", "freerouting",
                                                         "freerouting-2.5.0.jar")
OX, OY = genera_pcb.OX, genera_pcb.OY
ANT_TOP = D.H - 5.2
passes = sys.argv[1] if len(sys.argv) > 1 else "100"
# modalità: "protect" = in fase 2 le piste dei segnali sono bloccate; "libero" = Freerouting può spostarle
MODO_GND = sys.argv[2] if len(sys.argv) > 2 else "libero"
RIUSA_SEGNALI = "riusa" in sys.argv
UNICO = "unico" in sys.argv                    # GND sbrogliata insieme ai segnali (solo prove a 2 strati)                  # GND sbrogliata insieme ai segnali, una sola fase
VARIANTI = ["greedy", "random"] if UNICO else ["greedy", "random", "seq", "hybrid"]

# ---------- 1. scheda pulita ----------
genera_pcb.write_pro()
pcbnew.SaveBoard(PCB, genera_pcb.build())
b = pcbnew.LoadBoard(PCB)

# ---------- 2. DSN senza GND ----------
assert pcbnew.ExportSpecctraDSN(b, DSN), "export DSN fallito"
dsn = open(DSN, encoding="utf-8").read()
dsn = re.sub(r'^\(pcb "[^"]*"', '(pcb "notapad.dsn"', dsn, count=1)   # niente percorsi assoluti nel file
if not UNICO and D.STRATI == 2:   # 2 strati: GND esce dalla prima fase; 4 strati: resta, col piano su In1
    dsn = re.sub(r"\n\s*\(net GND\s*\(pins[^)]*\)\s*\)", "", dsn, count=1)
    dsn = re.sub(r"(\(class [^\n(]*?) GND\b", r"\1", dsn)
    # a 4 strati: niente "plane GND" nel DSN (la rete non c'è più); In1 resta di tipo power, quindi il router non ci passa
    dsn = re.sub(r"\n\s*\(plane GND \(polygon[^)]*\)\)", "", dsn)
dsn = dsn.replace("(clearance 100)", "(clearance 115)")
if False:   # (prova scartata: il wire_keepout su In1 blocca anche le via in Freerouting)
    x0, y0, x1, y1 = int(OX * 1000), int(-OY * 1000), int((OX + D.W) * 1000), int(-(OY + D.H) * 1000)
    ko = f"(wire_keepout \"\" (polygon In1.Cu 0  {x0} {y0}  {x1} {y0}  {x1} {y1}  {x0} {y1}  {x0} {y0}))"
    i = dsn.index('(keepout ""', dsn.index("(structure"))      # accanto ai keepout scritti da KiCad
    dsn = dsn[:i] + ko + "\n    " + dsn[i:]
# segnali preferibilmente SOPRA: il lato inferiore costa di più, così il piano GND sotto resta continuo
COSTI = """
    (autoroute_settings
      (fanout off) (autoroute on) (postroute on) (vias on)
      (via_costs 50) (plane_via_costs 5) (start_ripup_costs 100)
      (layer_rule F.Cu (active on) (preferred_direction vertical)
        (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 1.5))
      (layer_rule B.Cu (active on) (preferred_direction horizontal)
        (preferred_direction_trace_costs 4.0) (against_preferred_direction_trace_costs 5.0))
    )"""
if D.STRATI == 2:   # solo a 2 strati: a 4 il piano GND è In1
    i = dsn.index("(boundary", dsn.index("(structure"))
    dsn = dsn[:i] + COSTI.strip() + "\n    " + dsn[i:]
open(DSN, "w", encoding="utf-8").write(dsn)
if "solo_dsn" in sys.argv:
    sys.exit(0)

# ---------- 3. Freerouting, 4 strategie ----------
def freerouting(dsn_path, tag):
    variants = {"greedy": [], "random": ["-is", "random"], "seq": ["-is", "sequential"], "hybrid": ["-us", "hybrid"]}
    variants = {k: v for k, v in variants.items() if k in VARIANTI}
    procs, t0 = {}, time.time()
    for name, extra in variants.items():
        ses = dsn_path[:-4] + "_" + name + ".ses"
        if os.path.exists(ses): os.remove(ses)
        log = open(os.path.join(RDIR, f"fr_{tag}_{name}.log"), "w", encoding="utf-8")
        procs[name] = (subprocess.Popen(["java", "-Xmx700m", "-jar", JAR, "-de", dsn_path, "-do", ses, "-mp", passes,
                                         "-mt", "2", "-l", "en", "--gui.enabled=false", *extra],
                                        stdout=log, stderr=subprocess.STDOUT), ses, log)
    best = None
    for name, (pr, ses, log) in procs.items():
        pr.wait(); log.close()
        txt = open(log.name, encoding="utf-8", errors="replace").read()
        m = re.findall(r"\((\d+) unrouted and (\d+) violations\)", txt)
        unr = int(m[-1][0]) if m else 999
        print(f"  {tag}/{name}: {unr} non sbrogliati")
        if os.path.exists(ses) and (best is None or unr < best[0]):
            best = (unr, name, ses)
    print(f"freerouting {tag}", round(time.time() - t0), "s -> scelto", best[1])
    return best


def fix_widths(b):
    """porta a 0,1 mm le strozzature di Freerouting, ma solo dove la pista allargata resta a 0,1 mm dalle altre reti"""
    obst = {l: [] for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if b.IsLayerEnabled(l)}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            for L in obst:
                if p.IsOnLayer(L): obst[L].append((p.GetNetCode(), p.GetEffectiveShape(L)))
    for t in b.GetTracks():
        for L in obst:
            if t.IsOnLayer(L): obst[L].append((t.GetNetCode(), t.GetEffectiveShape(L)))
    n = bad = 0
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA" and t.GetWidth() < FromMM(0.1):
            seg = pcbnew.SHAPE_SEGMENT(t.GetStart(), t.GetEnd(), FromMM(0.1))
            if any(nc != t.GetNetCode() and sh.Collide(seg, FromMM(0.1)) for nc, sh in obst[t.GetLayer()]):
                bad += 1; continue
            t.SetWidth(FromMM(0.1)); n += 1
    if bad:
        print(f"  ATTENZIONE: {bad} strozzature lasciate sotto 0,1 mm (allargarle violerebbe la distanza)")
    return n


best = (0, "riuso", DSN[:-4] + "_greedy.ses") if RIUSA_SEGNALI else freerouting(DSN, "segnali")
assert pcbnew.ImportSpecctraSES(b, best[2]), "import SES fallito"
genera_pcb.add_preroutes(b); genera_pcb.place_previas(b)
print("piste allargate a 0,1 mm:", fix_widths(b))

if not UNICO and D.STRATI == 2:
    # ---------- 3b. seconda fase: solo GND, con le piste dei segnali bloccate ----------
    DSN2 = os.path.join(RDIR, "notapad_gnd.dsn")
    assert pcbnew.ExportSpecctraDSN(b, DSN2)
    d2 = open(DSN2, encoding="utf-8").read()
    d2 = re.sub(r'^\(pcb "[^"]*"', '(pcb "notapad_gnd.dsn"', d2, count=1)
    if MODO_GND == "protect":
        d2 = d2.replace("(type route)", "(type protect)")
    d2 = d2.replace("(clearance 100)", "(clearance 115)")
    open(DSN2, "w", encoding="utf-8").write(d2)
    best2 = freerouting(DSN2, "gnd")
    assert pcbnew.ImportSpecctraSES(b, best2[2]), "import SES GND fallito"
    genera_pcb.add_preroutes(b); genera_pcb.place_previas(b)
    print("piste allargate a 0,1 mm:", fix_widths(b))
    pcbnew.SaveBoard(ROUTED, b)

else:
    pcbnew.SaveBoard(ROUTED, b)

# ---------- 4. piani e cucitura ----------

gnd = b.FindNet("GND")
zones = []
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
    z.SetLocalClearance(FromMM(0.15)); z.SetMinThickness(FromMM(0.12))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(FromMM(0.15)); z.SetThermalReliefSpokeWidth(FromMM(0.2))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline(); ol.NewOutline()
    for px, py in ((0, 0), (D.W, 0), (D.W, D.H), (0, D.H)):
        ol.Append(FromMM(OX + px), FromMM(OY + py))
    z.SetZoneName("GND_" + ("TOP" if layer == pcbnew.F_Cu else "BOT"))
    b.Add(z); zones.append(z)
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(zones)

VIA_D, VIA_DRILL = 0.45, 0.25
existing = [(ToMM(t.GetPosition().x), ToMM(t.GetPosition().y)) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
holes = [(ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetDrillSize().x) / 2)
         for fp in b.GetFootprints() for p in fp.Pads() if p.GetDrillSize().x > 0]
fills = [z.GetFilledPolysList(z.GetLayer()) for z in zones]
r_need = VIA_D / 2 + 0.05


def covered(x, y):
    for poly in fills:
        for k in range(12):
            a = 2 * math.pi * k / 12
            if not poly.Contains(VECTOR2I(FromMM(x + r_need * math.cos(a)), FromMM(y + r_need * math.sin(a)))):
                return False
    return True


added = []
step = 0.25
y = OY + 0.6 if D.STRATI == 2 else OY + 1e9   # a 4 strati niente cucitura alla cieca (In2 ha piste)
while y < OY + ANT_TOP - 0.5:
    x = OX + 0.6
    while x < OX + D.W - 0.6:
        ok = covered(x, y)
        ok = ok and all(math.hypot(x - vx, y - vy) >= VIA_D + 0.25 for vx, vy in existing)
        ok = ok and all(math.hypot(x - vx, y - vy) >= 1.3 for vx, vy in added)
        ok = ok and all(math.hypot(x - hx, y - hy) >= hr + VIA_DRILL / 2 + 0.3 for hx, hy, hr in holes)
        if ok:
            v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
            v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DRILL)); v.SetNet(gnd)
            v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            b.Add(v); added.append((x, y))
        x += step
    y += step
print("via di cucitura GND:", len(added))
filler.Fill(b.Zones())
pcbnew.SaveBoard(PCB, b)
print("salvato:", PCB)
import cuci_gnd
cuci_gnd.main()
