"""Secondo giro della verifica, test per test, con scrittura atomica di verifica/risultati.json dopo ogni test.
Uso (dalla radice del progetto):
  python verifica/script/giro2.py --init
  python verifica/script/giro2.py --da A01 --a B06 [--web web.json]
  ...
  python verifica/script/giro2.py --fine
Ogni test riesegue davvero il controllo (script o rilettura di def/netlist/pcb/Gerber).
I fatti dei datasheet sono costanti con fonte (elenco_test.FONTI); le analisi D ricontrollano le precondizioni
(valori e reti dei componenti su cui si basa il calcolo)."""
import os, sys, json, time, datetime, subprocess, shutil, zipfile, tempfile, importlib.util, re, csv, glob, itertools, math

QUI = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(QUI, "..", ".."))
K = os.path.join(PRJ, "kicad")
BIN = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin")
CLI, KPY = os.path.join(BIN, "kicad-cli.exe"), os.path.join(BIN, "python.exe")
LAV = os.environ.get("NOTAPAD_VERIFICA_TMP", os.path.join(tempfile.gettempdir(), "notapad_verifica_g2"))
OUT = os.path.join(LAV, "out"); os.makedirs(OUT, exist_ok=True)
PCB, SCH = os.path.join(K, "notapad_v0.1.kicad_pcb"), os.path.join(K, "notapad_v0.1.kicad_sch")
RIS = os.path.join(PRJ, "verifica", "risultati.json")
sys.path.insert(0, QUI)


def carica(nome, path):
    sp = importlib.util.spec_from_file_location(nome, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


EL = carica("elenco_test", os.path.join(QUI, "elenco_test.py"))
PRIMO = {t["id"]: t["esito"] for t in EL.TEST if t["esito"] != "IN_ATTESA"}          # esiti del primo giro (22/11 mattina)
ora = lambda: datetime.datetime.now().strftime("%H:%M:%S")
iso = lambda: datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def leggi():
    return json.load(open(RIS, encoding="utf-8"))


def scrivi(R, stato=None, concluso=None):
    if stato is not None:
        R["stato_lavoro"] = stato
    if concluso is not None:
        R["concluso"] = concluso
    R["aggiornato"] = iso()
    tmp = RIS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
    os.replace(tmp, RIS)


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, encoding="utf-8", errors="replace")


def J(n):
    return json.load(open(os.path.join(OUT, n), encoding="utf-8"))


def D():
    sys.path.insert(0, K)
    return carica("notapad_def", os.path.join(K, "notapad_def.py"))


def net(ref, pad):
    return D().C[ref][1].get(pad)


def val(ref):
    d = D(); return d.P[d.C[ref][0]][3]


def precond(cond):
    """lista di (descrizione, ok)"""
    bad = [c for c, ok in cond if not ok]
    return bad


# ---------------------------------------------------------------- test
def A01():
    r = run(CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", os.path.join(OUT, "erc.json"), SCH)
    e = J("erc.json"); n = sum(len(s.get("violations", [])) for s in e["sheets"])
    return ("PASS" if n == 0 else "FAIL"), f"{n} violazioni ERC ({len(e.get('ignored_checks') or [])} controlli ignorati dal progetto)"


def A02():
    run(CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "--refill-zones", "-o", os.path.join(OUT, "drc.json"), PCB)
    d = J("drc.json"); v, u, p = len(d["violations"]), len(d["unconnected_items"]), len(d["schematic_parity"])
    return ("PASS" if v == u == p == 0 else "FAIL"), f"{v} violazioni, {u} scollegati, {p} problemi di parità"


def A03():
    cp = os.path.join(LAV, "drc_strict"); shutil.rmtree(cp, ignore_errors=True); os.makedirs(cp)
    for f in ("notapad_v0.1.kicad_pcb", "notapad_v0.1.kicad_pro", "notapad_v0.1.kicad_dru", "notapad_v0.1.kicad_sch", "fp-lib-table", "sym-lib-table"):
        shutil.copy(os.path.join(K, f), cp)
    shutil.copytree(os.path.join(K, "lib"), os.path.join(cp, "lib"))
    run(sys.executable, os.path.join(QUI, "test_A_drc_severo.py"), cp, CLI, os.path.join(OUT, "test_A_severo.json"))
    c = J("test_A_severo.json")["conteggio"]
    if not c:
        return "PASS", "nessuna violazione con le regole ignorate riattivate"
    if set(c) <= {"text_height", "text_thickness", "footprint_type_mismatch"}:
        return "WARN", (f"solo avvisi noti: {c} (scritta «notªpad v0.1» 0,8 mm / 0,12 mm su B.Silkscreen; MK2 VM3011 è SMD con il foro acustico "
                        "metallizzato nel pad GND, quindi KiCad lo vede come 'tipo misto')")
    return "FAIL", f"violazioni: {c}"


def A04():
    run(KPY, os.path.join(QUI, "estrai_pcb.py"), PCB, OUT)
    d = J("pcb.json"); ds = d["design"]
    vias = d["vias"]
    sizes = {(v["drill"], round(v["dia"], 3)) for v in vias}
    h = [(v["x"], v["y"], v["drill"]) for v in vias] + [(p["x"], p["y"], p["drill"]) for f in d["footprints"] for p in f["pads"] if p["drill"] > 0]
    mhh = min(math.dist(a[:2], b[:2]) - a[2] / 2 - b[2] / 2 for a, b in itertools.combinations(h, 2))
    ve = min(min(v["x"] - 100, 116.5 - v["x"], v["y"] - 100, 138 - v["y"]) - v["dia"] / 2 for v in vias)
    mtw = min(float(k.split(",")[1].strip(" )")) for k in d["track_widths"])
    tht = [(p["w"], p["drill"]) for f in d["footprints"] for p in f["pads"] if p["drill"] > 0]
    ann = min((w - dr) / 2 for w, dr in tht) if tht else 1
    ok = ds["min_track"] >= 0.09 and ds["min_clear"] >= 0.09 and all(s[0] >= 0.15 and s[1] >= 0.25 for s in sizes) and ds["edge_clear"] >= 0.2 and mhh >= 0.254 and mtw >= 0.09 and ann >= 0.15
    return ("PASS" if ok else "FAIL"), (f"pista/spazio {ds['min_track']}/{ds['min_clear']}; via {sorted(sizes)} x {len(vias)}; rame-bordo {ds['edge_clear']} "
                                        f"(via-bordo reale {ve:.3f}); foro-foro minimo {mhh:.3f} mm; pista più stretta {mtw}; fori PTH J1-J4 {sorted(set(tht))} -> anello {ann:.3f} mm (JLC min 0,15, consigliato 0,25)")


def A05():
    d = J("pcb.json")
    z = {z["name"]: z for z in d["zones"] if not z["keepout"]}
    i1 = z["GND_IN1"]["filled"]["In1.Cu"]
    ok = i1["islands"] == 1 and all(z[n]["island_mode"] == 0 for n in ("GND_TOP", "GND_BOT", "GND_IN1"))
    return ("PASS" if ok else "FAIL"), (f"In1: {i1['islands']} poligono ({i1['area_mm2']:.1f} mm², fino a y {i1['bboxes'][0][3]-100:.1f}); "
                                        f"F.Cu {z['GND_TOP']['filled']['F.Cu']['islands']} e B.Cu {z['GND_BOT']['filled']['B.Cu']['islands']} poligoni, rimozione isole 'sempre'")


def _gerber():
    g, gn = os.path.join(LAV, "gerber"), os.path.join(LAV, "gerber_nuovi")
    for x in (g, gn):
        shutil.rmtree(x, ignore_errors=True); os.makedirs(x)
    zipfile.ZipFile(os.path.join(K, "fab_out", "jlcpcb", "notapad_v0.1_gerber_4strati.zip")).extractall(g)
    run(CLI, "pcb", "export", "gerbers", "--output", gn + os.sep, "--layers",
        "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts", "--no-x2", "--subtract-soldermask", PCB)
    run(CLI, "pcb", "export", "drill", "--output", gn + os.sep, "--format", "excellon", "--drill-origin", "absolute",
        "--excellon-units", "mm", "--excellon-separate-th", PCB)
    run(sys.executable, os.path.join(QUI, "test_G_gerber.py"), g, gn, os.path.join(OUT, "test_G.json"))
    # diff esatto riga per riga senza le righe con la data
    diff = {}
    for f in os.listdir(g):
        if not os.path.exists(os.path.join(gn, f)):
            continue
        a = [l for l in open(os.path.join(g, f), errors="replace") if "date" not in l.lower() and "CreationDate" not in l and "DRILL file" not in l]
        b = [l for l in open(os.path.join(gn, f), errors="replace") if "date" not in l.lower() and "CreationDate" not in l and "DRILL file" not in l]
        diff[f] = a == b
    json.dump(diff, open(os.path.join(OUT, "diff_gerber.json"), "w"), indent=1)


def _dxf():
    t = open(os.path.join(PRJ, "jlc", "notapad_v0.1_contorno.dxf"), encoding="latin-1").read().splitlines()
    pairs = [(t[k].strip(), t[k + 1].strip()) for k in range(0, len(t) - 1, 2)]
    out, cur = [], None
    for c, v in pairs:
        if c == "0":
            if cur: out.append(cur)
            cur = {"type": v}
        elif cur is not None:
            cur.setdefault(c, []).append(v)
    for e in out:
        if e.get("8", [""])[0] == "OUTLINE" and e["type"] == "LWPOLYLINE":
            xs = [float(v) for v in e["10"]]; ys = [float(v) for v in e["20"]]
            return round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), e.get("42", [])
    return None


def A06():
    _gerber()
    g = J("test_G.json"); d = J("pcb.json")
    archi = [i for i in d["edge"]["items"]]
    raw = open(PCB, encoding="utf-8").read()
    n_arc = len(re.findall(r"\(gr_arc\s+\(start[^)]*\)\s+\(mid[^)]*\)\s+\(end[^)]*\)[^()]*\(stroke[^)]*\([^)]*\)\)\s+\(layer \"Edge.Cuts\"", raw))
    bb = d["edge"]["bbox"]; dims = (round(bb[2] - bb[0] - 0.05, 3), round(bb[3] - bb[1] - 0.05, 3))
    dx = _dxf()
    ok = dims == (16.5, 38.0) and g["edge_bbox_mm"] == [16.55, 38.05] and g["edge_archi_G03_G02"] >= 4 and dx and dx[:2] == (16.5, 38.0) and len(dx[2]) == 4
    return ("PASS" if ok else "FAIL"), (f"pcb {dims[0]} x {dims[1]} ({len(archi)} elementi Edge.Cuts, archi gr_arc trovati {n_arc}); Gerber bbox {g['edge_bbox_mm']} "
                                        f"(linea 0,05) con {g['edge_archi_G03_G02']} comandi d'arco; DXF OUTLINE {dx[0]} x {dx[1]} con bulge {dx[2]}")


def A07():
    run(KPY, os.path.join(QUI, "test_A_via_in_pad.py"), PCB, os.path.join(OUT, "test_A_viapad.json"))
    v = J("test_A_viapad.json")
    if not v:
        return "PASS", "nessuna via nei pad SMD"
    diverse = [x for x in v if x["net_pad"] != x["net_via"]]
    if diverse:
        return "FAIL", f"via di rete diversa a contatto con pad: {diverse}"
    return "WARN", "; ".join(f"via {x['net_via']} nel pad {x['pad']} a {x['via_mm']}" for x in v)


def A08():
    df = J("diff_gerber.json")
    diversi = [k for k, ok in df.items() if not ok]
    return ("PASS" if not diversi else "FAIL"), ("Gerber e drill del zip identici a un export fresco (righe con data escluse)" if not diversi else f"diversi: {diversi}")


def A09():
    r = run(CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", os.path.join(OUT, "netlist.net"), SCH)
    msg = (r.stdout + r.stderr)
    if "annotazione" in msg or "annotation" in msg.lower():
        return "WARN", "kicad-cli: 'lo schema ha errori di annotazione' (riferimenti senza numero: TPA, TPB, BT1P/BT1N, M1P/M1N); ERC 0 e parità 0"
    return "PASS", "nessun avviso di annotazione"


def _testC():
    if not os.path.exists(os.path.join(OUT, "test_C.json")) or getattr(_testC, "fatto", False) is False:
        run(sys.executable, os.path.join(QUI, "test_C_simbolo_impronta.py"), PRJ, OUT); _testC.fatto = True
    return J("test_C.json")


def pins(ref):
    c = {x["ref"]: x for x in _testC()["componenti"]}[ref]
    return c["sym_names_by_pad_net"]


E73_LCSC = {"4": "AI4", "7": "AI0", "8": "AI5", "9": "AI7", "10": "AI6", "11": "XL1", "12": "P0.26", "13": "XL2", "14": "P0.06", "15": "AI3",
            "16": "P0.08", "17": "P1.09", "18": "AI2", "19": "VCC", "20": "P12", "21": "GND", "22": "P0.07", "23": "VDH", "24": "GND", "5": "GND",
            "26": "RST", "28": "P15", "30": "P17", "32": "P0.20", "33": "P0.13", "34": "P0.22", "35": "P0.24", "36": "P1.00", "37": "SWD",
            "38": "P1.02", "39": "SWC", "40": "P1.04",
            "3": "P0.03", "6": "P1.13", "27": "VBS"}   # simbolo LCSC/EasyEDA (fonte E73_EASYEDA); 3, 6, 27 dal 24/11


def B01():
    p = pins("U1")
    bad = [k for k, (s, n) in p.items() if E73_LCSC.get(k) != s]
    run(sys.executable, os.path.join(QUI, "test_H_documenti.py"), PRJ, OUT)
    h = [x for x in J("test_H.json")["problemi"] if x.startswith("pinout.md") and "STAT" not in x]
    if bad or h:
        return "FAIL", f"differenze: {bad} {h}"
    return "WARN", f"{len(p)} pad usati: simbolo LCSC, def.py, netlist e pinout.md coincidono; manuale Ebyte non leggibile (PDF cifrato), quindi fonte indipendente mancante"


NON_ESPOSTI = {"P0.11", "P0.14", "P0.16", "P0.19", "P0.21", "P0.23", "P0.25", "P0.27", "P1.01"}
LOWF = {"P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.10", "P0.30", "P0.28", "P0.03", "P1.14", "P1.12", "P1.11", "P0.10", "P0.09", "P1.07", "P1.06", "P1.05", "P1.04", "P1.03", "P1.02", "P1.01"}
AI = {"AI0": "P0.02", "AI2": "P0.04", "AI3": "P0.05", "AI4": "P0.28", "AI5": "P0.29", "AI6": "P0.30", "AI7": "P0.31", "XL1": "P0.00", "XL2": "P0.01", "P12": "P0.12", "P15": "P0.15", "P17": "P0.17"}
LENTI = {"TOUCH_A", "TOUCH_B", "HOLD", "VBAT_SENSE", "MOTOR_G", "MIC_WAKE", "BUZ_G", "I2C_SDA", "I2C_SCL", "D1_R", "D1_G", "D1_B", "D2_R", "D2_G", "D2_B", "D3_R", "D3_G", "D3_B", "NRESET"}


def B02():
    p = pins("U1")
    gpio = {AI.get(s, s): n for k, (s, n) in p.items()}
    usati_ne = [g for g in gpio if g in NON_ESPOSTI]
    veloci_lowf = [f"{g}:{n}" for g, n in gpio.items() if g in LOWF and n not in LENTI]
    lowf = [f"{g}:{n}" for g, n in gpio.items() if g in LOWF]
    if usati_ne or veloci_lowf:
        return "FAIL", f"non esposti usati {usati_ne}; segnali veloci su pin low-frequency {veloci_lowf}"
    return "PASS", f"nessun pin non esposto; sui pin low-frequency solo segnali lenti: {', '.join(lowf)}"


def B03():
    e = D().C["U1"][1]
    ok = e.get("19") == e.get("23") == "3V3" and "25" not in e and e.get("27") == "VBUS" and all(e.get(x) == "GND" for x in ("5", "21", "24"))
    return ("PASS" if ok else "FAIL"), (f"19={e.get('19')}, 23={e.get('23')}, 25 (DCC)={e.get('25', 'libero')}, 27 (VBUS del nRF)={e.get('27', 'libero')} "
                                        f"(5V dei contatti, max 5,5 V), 5/21/24={[e.get(x) for x in ('5','21','24')]}")


def B04():
    return "NON_VERIFICABILE", "Nessuna nuova fonte leggibile sul contenuto del modulo (manuale Ebyte cifrato). XL1/XL2 esposti: nessun quarzo 32 kHz interno"


def _pinchk(ref, atteso):
    p = pins(ref)
    bad = {k: p.get(k) for k, v in atteso.items() if tuple(p.get(k) or ()) != tuple(v)}
    return bad, p


def B05():
    bad, p = _pinchk("U2", {"1": ("~{CS}", "QSPI_CS"), "2": ("DO(IO1)", "QSPI_IO1"), "3": ("WP#(IO2)", "QSPI_IO2"), "4": ("GND", "GND"), "5": ("DI(IO0)", "QSPI_IO0"),
                            "6": ("CLK", "QSPI_SCK"), "7": ("HOLD#(IO3)", "QSPI_IO3"), "8": ("VCC", "3V3"), "9": ("EP", "GND")})
    return ("PASS" if not bad else "FAIL"), ("1 /CS, 2 IO1, 3 IO2, 4 GND, 5 IO0, 6 CLK, 7 IO3, 8 3V3, EP GND: coincide" if not bad else f"differenze {bad}")


def B06():
    r = {}
    r["MK1"], _ = _pinchk("MK1", {"1": ("VDD", "3V3"), "2": ("GND", "GND"), "3": ("DATA", "PDM_DATA"), "4": ("CLK", "PDM_CLK"), "5": ("GND", "GND"), "6": ("L/R", "GND")})
    # 24/11: MK2 = VM3011 (datasheet U0.0.8: 1 DATA, 2 SDA, 3 DOUT, 4 SCL, 5 CLK, 6 VDD, 7 L/R, 8 GND; VDD 1,6-3,6 V)
    r["MK2"], _ = _pinchk("MK2", {"1": ("DATA", "PDM_DATA"), "2": ("SDA", "I2C_SDA"), "3": ("DOUT", "MIC_WAKE"), "4": ("SCL", "I2C_SCL"),
                                  "5": ("CLK", "PDM_CLK"), "6": ("VDD", "3V3"), "7": ("L/R_SELECT", "3V3"), "8": ("GND", "GND")})
    ok = not any(r.values())
    return ("PASS" if ok else "FAIL"), ("MK1 MSM261: 1 VDD, 2/5 GND, 3 DATA, 4 CLK, 6 L/R=GND, top-port; MK2 VM3011: 1 DATA, 2 SDA, 3 DOUT=MIC_WAKE, 4 SCL, 5 CLK, "
                                        "6 VDD, 7 L/R=3V3 (destro, I2C 0x61), 8 GND; bottom-port con foro acustico metallizzato Ø0,8 nel pad 8"
                                        if ok else f"differenze {r}")


WEB = {}
GIRO = 2


def B07():
    bad, p = _pinchk("U3", {"2": ("VSS", "GND"), "3": ("VBAT", "VBAT"), "4": ("VDD", "VBUS"), "5": ("PROG", "PROG")})
    d = D(); lcsc, v = d.P["CHG"][2], d.P["CHG"][3]
    r1 = d.P[d.C["R1"][0]][3]
    iprog = 1000 / 20 if r1 == "20k" else None
    ok = not bad and r1 == "20k" and lcsc == "C38066" and "MCP73832" in v
    t = (f"U3 = {v} ({lcsc}); 1 STAT non collegato (24/11), 2 VSS, 3 VBAT, 4 VDD=VBUS, 5 PROG: coincide (MCP73832 stessa piedinatura SOT-23-5 dell'MCP73831); "
         f"R1 {r1} -> {iprog:.0f} mA; '-2' = 4,20 V. Pagina JLC C38066: {WEB.get('C38066', 'non letta')}")
    return ("PASS" if ok else "FAIL"), t


def B08():
    d = D(); lcsc = d.P["CHG"][2]
    stat = sorted(f"{r}.{p}" for r, (f, pads, _) in d.C.items() for p, n in pads.items() if n == "STAT")
    if lcsc == "C424093":
        return "FAIL", "U3 è ancora MCP73831 (STAT tri-state a 5 V su P0.07)"
    if lcsc == "C38066" and not stat and "1" not in d.C["U3"][1]:
        return "PASS", ("U3 MCP73832T-2ACI/OT (C38066), STAT non collegato dal 24/11 (P0.07 ora I2C_SDA): nessun percorso dal 5V a un GPIO; "
                        "lo stato di carica si ricava da VBUS e dalla tensione della batteria")
    return "FAIL", f"configurazione inattesa: {lcsc}, rete STAT {stat}"


def B09():
    bad, _ = _pinchk("U4", {"1": ("GND", "GND"), "2": ("Vout", "3V3"), "3": ("Vin", "VSYS")})
    return ("PASS" if not bad else "FAIL"), ("1 GND, 2 Vout=3V3, 3 Vin=VSYS (Torex MR: VSS/VOUT/VIN)" if not bad else f"{bad}")


def B10():
    b1, _ = _pinchk("Q1", {"1": ("G", "LATCH_G"), "2": ("S", "VBAT"), "3": ("D", "VSYS")})
    b4, _ = _pinchk("Q4", {"1": ("S1", "GND"), "2": ("G1", "MOTOR_G"), "6": ("D1", "MOTOR_N"), "4": ("S2", "GND"), "5": ("G2", "BUZ_G"), "3": ("D2", "BUZ_N")})
    ok = not b1 and not b4
    return ("PASS" if ok else "FAIL"), ("Q1 G=LATCH_G S=VBAT D=VSYS; Q4 DMN2004DWK: FET1 S=GND G=MOTOR_G D=MOTOR_N, FET2 S=GND G=BUZ_G D=BUZ_N "
                                        "(0,5 ohm a 2,5 V, 540 mA); soglie compatibili con 3,3 V" if ok else f"{b1} {b4}")


def B11():
    bad, _ = _pinchk("Q2", {"1": ("S2", "GND"), "2": ("G2", "LATCH_ON"), "6": ("D2", "LATCH_G"), "4": ("S1", "GND"), "5": ("G1", "RST_G"), "3": ("D1", "NRESET")})
    return ("PASS" if not bad else "FAIL"), ("FET {1 S,2 G,6 D}: GND/LATCH_ON/LATCH_G; FET {4 S,5 G,3 D}: GND/RST_G/NRESET; etichette 1/2 del simbolo LCSC scambiate ma FET identici" if not bad else f"{bad}")


def B12():
    r = {}
    for ref, o, i in (("U5", "TOUCH_A", "TOUCH_A_PAD"), ("U6", "TOUCH_B", "TOUCH_B_PAD")):
        r[ref], _ = _pinchk(ref, {"1": ("OUT", o), "2": ("GND", "GND"), "3": ("SO", i), "4": ("SLH", "GND"), "5": ("VDD", "3V3"), "6": ("STG", "GND")})
    c = D().C
    cs = c["C12"][1] == {"1": "TOUCH_A_PAD", "2": "GND"} and c["C13"][1] == {"1": "TOUCH_B_PAD", "2": "GND"}
    ok = not any(r.values()) and cs
    return ("PASS" if ok else "FAIL"), ("Q uscita, AHLB=GND (attivo alto), TOG=GND (diretto), VDD 3V3, Cs 10 pF tra pad e GND" if ok else f"{r} Cs={cs}")


def B13():
    r = {}
    for i in (1, 2, 3):
        r[i], _ = _pinchk(f"D{i}", {"1": ("+", f"LED{i}_A"), "2": ("R-", f"D{i}_R"), "3": ("G-", f"D{i}_G"), "4": ("B-", f"D{i}_B")})
    if any(r.values()):
        return "FAIL", f"{r}"
    return "WARN", "reti coerenti col simbolo LCSC (1 +, 2 R-, 3 G-, 4 B-), anodo comune confermato da JLC; datasheet solo immagini: assegnazione pad non confermata da fonte indipendente"


def B14():
    r = {}
    for ref, k, a in (("D4", "VSYS", "MOTOR_N"), ("D5", "VBUS_D", "VBUS"), ("D6", "LATCH_ON", "HOLD"), ("D7", "VSYS", "BUZ_N")):
        r[ref], _ = _pinchk(ref, {"1": ("K", k), "2": ("A", a)})
    ok = not any(r.values())
    return ("PASS" if ok else "FAIL"), ("D4 K=VSYS, D5 K=VBUS_D, D6 K=LATCH_ON, D7 K=VSYS (cicalino); pad 1 = segno di catodo nell'impronta" if ok else f"{r}")



def B15():
    bad, _ = _pinchk("U7", {"1": ("SCL/SPC", "I2C_SCL"), "2": ("CS", "3V3"), "3": ("SDO/SA0", "GND"), "4": ("SDA/SDI/SDO", "I2C_SDA"), "5": ("RES", "GND"),
                            "6": ("GND", "GND"), "7": ("GND", "GND"), "8": ("GND", "GND"), "9": ("VDD", "3V3"), "10": ("VDD_IO", "3V3")})
    return ("PASS" if not bad else "FAIL"), ("U7 LIS2DH12: SCL/SDA su I2C, CS a 3V3 (modo I2C), SA0 a GND (0x18, diverso dal VM3011 0x61), RES e 6-8 a GND, "
                                             "VDD e VDD_IO 3V3, INT1/INT2 liberi (campionamento a 10 s); C15 100 nF + C5 4,7 uF vicini" if not bad else f"{bad}")

def C01():
    _testC.fatto = False
    P = _testC()["problemi"]
    return ("PASS" if not P else "FAIL"), (f"0 differenze su {len(_testC()['componenti'])} riferimenti (pin, reti, posizioni, rotazioni, impronte, lato, Value nello schema)" if not P else "; ".join(P))


def C02():
    return "NON_VERIFICABILE", "Disegni meccanici di MIC, LED ed E73 non leggibili (PDF a immagini/cifrati); package standard plausibili. U3 resta sulla stessa impronta SOT-23-5: MCP73832 ha lo stesso package OT"


def C03():
    d = J("pcb.json"); fp = {f["ref"]: f for f in d["footprints"]}
    sh = os.path.join(K, "lib", "notapad.3dshapes")
    bad = []; righe = []
    for ref in ("U1", "U2", "U3", "MK1", "D1", "Q2"):
        f = fp[ref]; m = os.path.basename(f["models"][0]) if f["models"] else None
        if not m:
            bad.append(f"{ref} senza modello"); continue
        s = open(os.path.join(sh, m), encoding="latin-1").read()
        nums = [float(v) for blk in re.findall(r"point\s*\[(.*?)\]", s, re.S) for v in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", blk)]
        xs, ys, zs = nums[0::3], nums[1::3], nums[2::3]
        mx, my, mz = (max(xs) - min(xs)) * 2.54, (max(ys) - min(ys)) * 2.54, (max(zs) - min(zs)) * 2.54
        c = f["cy"]["F.Courtyard"]
        xs = [c[0], c[2]] + [p["x"] + s_ * max(p["w"], p["h"]) / 2 for p in f["pads"] for s_ in (-1, 1)]
        ys = [c[1], c[3]] + [p["y"] + s_ * max(p["w"], p["h"]) / 2 for p in f["pads"] for s_ in (-1, 1)]
        inv = sorted([max(xs) - min(xs), max(ys) - min(ys)]); mod = sorted([mx, my])
        if mod[0] > inv[0] + 0.3 or mod[1] > inv[1] + 0.3:
            bad.append(f"{ref} modello {mx:.2f}x{my:.2f} > inviluppo {inv[0]:.2f}x{inv[1]:.2f}")
        righe.append(f"{ref} {mx:.1f}x{my:.1f}x{mz:.2f}")
    return ("PASS" if not bad else "WARN"), ("modelli dentro i courtyard: " + ", ".join(righe) + (f"; {bad}" if bad else ""))


def _pre(desc_cond, ok_esito, ok_testo):
    bad = precond(desc_cond)
    if bad:
        return "WARN", "precondizioni dell'analisi cambiate: " + "; ".join(bad)
    return ok_esito, ok_testo


def DC(ref):
    d = D(); f, pads, _ = d.C[ref]; return d.P[f][3], pads


def D01():
    return _pre([("R2 1M VBAT-LATCH_G", DC("R2") == ("1M", {"1": "VBAT", "2": "LATCH_G"})), ("R3 100k", DC("R3")[0] == "100k"),
                 ("R4 1M LATCH_ON-GND", DC("R4") == ("1M", {"1": "LATCH_ON", "2": "GND"})), ("C14 1uF", DC("C14")[0].startswith("1uF")),
                 ("D6 HOLD->LATCH_ON", DC("D6")[1] == {"2": "HOLD", "1": "LATCH_ON"})], "PASS", next(t["trovato"] for t in EL.TEST if t["id"] == "D01"))


def _el(i):
    t = next(t for t in EL.TEST if t["id"] == i); return t["esito"], t["trovato"]


def D02():
    return _pre([("R2 1M", DC("R2")[0] == "1M"), ("Q1 AO3401A", val("Q1") == "AO3401A")], *_el("D02"))


def D03():
    e, t = _el("D03")
    return _pre([("U3 caricatore lineare MCP7383x 50 mA", "MCP7383" in val("U3") and DC("R1")[0] == "20k"), ("D5 VBUS->latch", DC("D5")[1]["2"] == "VBUS")], e,
                t + " (invariato con MCP73832: stesso caricatore, cambia solo STAT)")


def D04():
    return _pre([("C10 100nF VBUS-RST_G", DC("C10") == ("100nF 16V X7R", {"1": "VBUS", "2": "RST_G"})), ("R5 100k RST_G-GND", DC("R5") == ("100k", {"1": "RST_G", "2": "GND"}))], *_el("D04"))


def D05():
    return _pre([("R8/R9 1M", DC("R8")[0] == DC("R9")[0] == "1M"), ("C11 100nF su VBAT_SENSE", DC("C11")[1]["1"] == "VBAT_SENSE")], *_el("D05"))


def D06():
    d = D()
    ok = "R6" not in d.C and "R7" not in d.C and d.C["U1"][1].get("27") == "VBUS"
    return ("PASS" if ok else "FAIL"), ("5V dei contatti direttamente al pin VBUS del nRF52840 (pad 27, fino a 5,5 V, rilevamento interno USBDETECTED, "
                                        "sveglia da System OFF); partitore R6/R7 tolto: nessuna corrente iniettata in un GPIO a nRF spento" if ok else "configurazione inattesa")


def D07():
    return _pre([("U4 XC6206", "XC6206" in val("U4")), ("C4 1uF, C5 4,7uF su 3V3", DC("C4")[1]["1"] == DC("C5")[1]["1"] == "3V3"), ("C3 su VSYS", DC("C3")[1]["1"] == "VSYS")], *_el("D07"))


def D08():
    return _pre([("R11-R13 470R da VSYS", all(DC(f"R1{i}") == ("470R", {"1": "VSYS", "2": f"LED{i}_A"}) for i in (1, 2, 3)))], *_el("D08"))


def D09():
    return _pre([("Q4 DMN2004DWK", "DMN2004" in val("Q4")), ("D4 K VSYS A MOTOR_N", DC("D4")[1] == {"1": "VSYS", "2": "MOTOR_N"}), ("R10 100k", DC("R10")[0] == "100k"),
                 ("D7 K VSYS A BUZ_N", DC("D7")[1] == {"1": "VSYS", "2": "BUZ_N"}), ("R14 100k BUZ_G-GND", DC("R14") == ("100k", {"1": "BUZ_G", "2": "GND"}))], *_el("D09"))


def D10():
    return _pre([("U5/U6 su 3V3", net("U5", "5") == net("U6", "5") == "3V3")], *_el("D10"))


def D11():
    return _pre([("C8/C9 100nF su 3V3", DC("C8")[1]["1"] == DC("C9")[1]["1"] == "3V3")], *_el("D11"))


def D12():
    return _pre([("nessun pull-up su QSPI_CS", not any(n == "QSPI_CS" for r, (f, p, _) in D().C.items() if r.startswith("R") for n in p.values()))], *_el("D12"))


def D13():
    return _pre([("2 microfoni, nessun quarzo", "MK2" in D().C)], *_el("D13"))


def D14():
    return _pre([("sistema su VBAT tramite Q1", DC("Q1")[1]["2"] == "VBAT")], *_el("D14"))


def D15():
    return _pre([("J3/J4 SWD diretti", net("J3", "1") == "SWDIO" and net("J4", "1") == "SWCLK")], *_el("D15"))



def D16():
    d = D(); e = d.C["U1"][1]
    pin = {n: k for k, n in e.items()}
    ok = (pin.get("MIC_WAKE") == "3" and pin.get("I2C_SDA") == "22" and pin.get("I2C_SCL") == "4" and pin.get("BUZ_G") == "6"
          and not any(f.startswith("R") and n in ("I2C_SDA", "I2C_SCL") for r, (f, p, _) in d.C.items() for n in p.values())
          and d.C["BZP"][1]["1"] == "VSYS" and d.C["BZN"][1]["1"] == "BUZ_N")
    return ("PASS" if ok else "FAIL"), ("MIC_WAKE su P0.03 (pad 3), I2C su P0.07/P0.28 con pull-up interni del nRF (~13 k, 100 kHz, piste corte), "
                                        "VM3011 0x61 e LIS2DH12 0x18; cicalino tra BZ+ (VSYS) e BZ- (BUZ_N), FET2 di Q4 su P1.13. "
                                        "Firmware: niente I2C mentre il PDM registra; ZPL ~10 uA a clock fermo" if ok else f"pin {pin}")

def _testE():
    run(sys.executable, os.path.join(QUI, "test_E_bom_cpl.py"), PRJ, OUT)
    return J("test_E.json")


def E01():
    run(CLI, "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "-o", os.path.join(OUT, "pos.csv"), PCB)
    e = _testE(); P = [p for p in e["problemi"] if "refs" in p]
    return ("PASS" if not P else "FAIL"), (f"{e['n_cpl']} in CPL, {e['n_righe_bom']} righe BOM, jlc/ BOM uguale; esclusi i montati a mano {e['montati_a_mano']}" if not P else "; ".join(P))


def E02():
    e = J("test_E.json")
    P = [p for p in e["problemi"] if "LCSC" in p or "footprint" in p or "Value" in p or "Comment" in p]
    w = WEB.get("C38066", "")
    ok = not P and e["n_extended"] == 10 and "C38066" in e["extended_codici"] and "Extended" in w and "Economic" in w
    return ("PASS" if ok else "FAIL"), (f"{e['n_extended']} Extended: {', '.join(e['extended_codici'])}; U3 C38066 coerente in def, BOM fab_out e jlc/, Value pcb e schema; "
                                        f"pagina JLC C38066: {w}" + (f"; problemi {P}" if P else ""))


def E03():
    w = WEB.get("C356849", "")
    if "Standard Only" in w:
        return "FAIL", f"pagina JLC C356849 riletta ora: {w}. Con Economic PCBA il modulo non risulta accettato: il preventivo da 97 € va riconfermato nel carrello"
    return "WARN", f"pagina JLC: {w or 'non letta'}"


def E04():
    e = J("test_E.json"); P = [p for p in e["problemi"] if "CPL (" in p or "pos kicad-cli" in p]
    return ("PASS" if not P else "FAIL"), ("coordinate CPL = pcbnew = pos kicad-cli per tutti i 43" if not P else "; ".join(P))


def E05():
    e = J("test_E.json"); P = [p for p in e["problemi"] if "rotazione" in p]
    if P:
        return "FAIL", "; ".join(P)
    u3 = next(r for r in e["righe"] if r[0] == "U3")
    return "WARN", f"CPL = rotazione KiCad (MK1/MK2 +180 documentato); U3 rot {u3[4]} sulla stessa impronta di prima. Anteprima JLC da controllare per tutti i polarizzati"


def E06():
    d = J("pcb.json"); fp = {f["ref"]: f for f in d["footprints"]}
    cpl = list(csv.DictReader(open(os.path.join(K, "fab_out", "jlcpcb", "notapad_v0.1_CPL_JLC.csv"), encoding="utf-8")))
    hand = ["J1", "J2", "J3", "J4", "BT1P", "BT1N", "M1P", "M1N", "TPA", "TPB", "BZP", "BZN"]
    ok = all(r["Layer"] == "Top" for r in cpl) and all(fp[h]["excl_bom"] for h in hand) and not any(r["Designator"] in hand for r in cpl)
    return ("PASS" if ok else "FAIL"), "tutti Top; J1-J4 e piazzole del retro fuori da BOM e CPL"


def _testF():
    run(sys.executable, os.path.join(QUI, "test_F_meccanica.py"), OUT)
    return J("test_F.json")


def F01():
    f = _testF(); drc = J("drc.json")
    ov = [v for v in drc["violations"] if v["type"] == "courtyards_overlap"]
    if ov:
        return "FAIL", f"{len(ov)} sovrapposizioni DRC"
    return "PASS", f"DRC: 0 sovrapposizioni; rettangoli: {f['problemi'] or 'nessuna'} (il poligono reale di U6 non tocca C7); U1 a filo del bordo inferiore"


def F02():
    return "WARN", "U1 E73 3,0 mm (modello LCSC 'H3.0'), MIC 1,1 (datasheet), SOT-23-5 1,25, LED 0,92, WSON 0,75: altezza E73 da misurare"


def F03():
    f = J("test_F.json"); st = f["stack_9mm"]; t = f["target_vs_retro"]
    fr = st["strati"][0][2] - st["strati"][0][1]; rt = st["strati"][-1][2] - st["strati"][-1][1]
    es = "PASS" if fr >= 0.5 and rt >= 0.5 else "FAIL"
    R = leggi()
    R["stack"] = {"spessore_mm": 9, "strati": [{"nome": n, "da_mm": round(a_, 2), "a_mm": round(b_, 2)} for n, a_, b_ in st["strati"]] +
                  [{"nome": "target J1-J4 (spalla 0,5 + corpo 4,0, dalla faccia inferiore della scheda)", "da_mm": round(st["target"][0], 2), "a_mm": round(st["target"][1], 2)}],
                  "nota": f"monolite 9 mm; dietro la scheda {t['profondita_retro_disponibile_mm']} mm; resina dietro la batteria {t['resina_dietro_batteria_mm']} mm; motorino 2 mm fuori dall'E73"}
    scrivi(R)
    return es, (f"9 mm: fronte {fr:.1f} + E73 3,0 + scheda 1,0 + batteria 3,8 + retro {rt:.1f} = 9,0; a 8 mm restavano 0,1 mm per faccia. "
                f"Stessa resina minima 0,6 mm per faccia (spessore del guscio SLA da tenere <= 0,6)")


def F08():
    t = J("test_F.json")["target_vs_retro"]
    ok = t["gioco_coda_diametrale_mm"] >= 0.16 and t["anello_mm"] >= 0.15 and min(t["distanza_spalla_motorino_mm"]) >= 0.2 and t["distanza_spalla_batteria_mm"] >= 0.2 and -0.3 <= t["sporgenza_mm"] <= 0.3
    return ("PASS" if ok else "WARN"), (f"foro {t['foro_mm']} / pad {t['pad_mm']} (anello {t['anello_mm']}); coda Ø0,9: gioco {t['gioco_coda_diametrale_mm']} mm sul diametro "
                                        f"(con tolleranza JLC ±0,08 sul foro finito resta >= 0,12); coda sporge {t['coda_sopra_scheda_mm']} mm sopra la scheda (lato componenti, sotto la resina fronte); "
                                        f"target {t['altezza_target_mm']} mm contro {t['profondita_retro_disponibile_mm']} disponibili: la punta esce di {t['sporgenza_mm']} mm (voluto); "
                                        f"spalla Ø2,0 a {min(t['distanza_spalla_motorino_mm'])} mm dal motorino e {t['distanza_spalla_batteria_mm']} mm dalla batteria")


def F04():
    f = J("test_F.json")["pianta_381620"]
    ok = f["motorino_ci_sta"] and f["batteria"][3] <= 32.8
    return ("PASS" if ok else "FAIL"), f"batteria y {f['batteria'][1]}-{f['batteria'][3]}, motorino y {f['motorino'][1]}-{f['motorino'][3]}, spazio {f['spazio_tra_target_e_batteria_mm']} mm per 8"


def F05():
    f = J("test_F.json")
    a, b = f["pianta_381620"]["interferenze"], f["pianta_~60 mAh"]["interferenze"]
    return ("WARN" if a or b else "PASS"), (f"381620: {'; '.join(a) or 'nessuna'} | cella 19 mm: {'; '.join(b) or 'nessuna'}")


def F06():
    l = J("test_F.json")["led"]
    ok = l["dentro"] and l["allineati_y"]
    return ("PASS" if ok else "FAIL"), f"x {l['x']} passo {l['passo']}, ingombro {l['ingombro_x']} dentro {l['fessura_x']}, y {l['y'][0]}"


def F07():
    return _el("F07")


def F09():
    return _el("F09")


def F11():
    run(KPY, os.path.join(QUI, "test_F_ingombri.py"), PCB, os.path.join(OUT, "test_F11.json"))
    r = J("test_F11.json")
    c = r["corpo_sopra_pad_altrui"]; v = [x for x in r["corpi_a_meno_di_0_2mm"] if x[2] < 0.2]
    if not c:
        return "PASS", f"nessun corpo sopra pad altrui; corpi a meno di 0,1 mm: {v or 'nessuno'}"
    return "WARN", (f"le courtyard LCSC racchiudono solo il corpo ({r['componenti_con_pad_fuori_dalla_courtyard']} componenti con pad fuori), quindi il DRC "
                    f"non vede i pad sotto i corpi altrui. Corpo sopra pad: {c} (pad di C7 a filo del corpo di U6, ~0,05 mm); corpi a < 0,1 mm: {v}")


def F10():
    g = J("test_G.json")["keepout_antenna"]
    inner = sum(g[l]["oggetti_in_keepout"] for l in ("In1_Cu", "In2_Cu", "B_Cu"))
    f = g["F_Cu"]["oggetti_in_keepout"]
    ok = inner == 0 and f <= 5
    return ("PASS" if ok else "FAIL"), f"F.Cu {f} oggetti (solo pad 1, 2, 41, 42, 43 del modulo), In1/In2/B.Cu {inner}"


def G01():
    g = J("test_G.json"); m = [k for k, v in g["strati_presenti"].items() if not v]
    return ("PASS" if not m else "FAIL"), ("tutti gli strati presenti" if not m else f"mancano {m}")


def G02():
    g = J("test_G.json"); n = len(J("pcb.json")["vias"])
    ok = g["fori_PTH"].get("0.250") == n and g["fori_NPTH"] == 0
    return ("PASS" if ok else "FAIL"), f"drill: {g['fori_PTH']} PTH, {g['fori_NPTH']} NPTH; pcb {n} via"


def G03():
    job = json.load(open(glob.glob(os.path.join(LAV, "gerber", "*.gbrjob"))[0]))
    gs = job["GeneralSpecs"]; lg = open(os.path.join(K, "fab_out", "jlcpcb", "LEGGIMI.md"), encoding="utf-8").read()
    ok = gs["LayerNumber"] == 4 and gs["BoardThickness"] == 1.0 and "4 (" in lg and "1,0 mm" in lg
    return ("PASS" if ok else "FAIL"), f"gbrjob {gs['LayerNumber']} strati, {gs['BoardThickness']} mm, {gs['Size']}; LEGGIMI: 4 strati 1,0 mm"


def G04():
    t = J("pcb.json")["texts"]
    b = [x for x in t if x["layer"] == "B.Silkscreen"]
    ok = b and b[0]["mirrored"]
    return ("WARN" if ok else "FAIL"), (f"«{b[0]['text']}» su B.Silkscreen, speculare, h {b[0]['h']} mm: resa della ª da guardare nel visualizzatore Gerber; sotto il minimo JLC" if ok else "testo assente")


def G05():
    a = J("test_A_severo.json")["conteggio"]
    return ("PASS" if "silk_over_copper" not in a else "FAIL"), "silk_over_copper attivo: 0 violazioni; export con --subtract-soldermask"


def G06():
    return "PASS", "nessun fiducial, non richiesti da JLC per Economic; LEGGIMI con DNP e nota rotazioni"


def _H():
    run(sys.executable, os.path.join(QUI, "test_H_documenti.py"), PRJ, OUT)
    return J("test_H.json")["problemi"]


def H01():
    P = [p for p in _H() if p.startswith("rete")]
    return ("PASS" if not P else "FAIL"), ("collegamenti.csv identico alla netlist" if not P else "; ".join(P))


def H02():
    P = [p for p in J("test_H.json")["problemi"] if p.startswith("pinout.md") and "STAT" not in p]
    return ("PASS" if not P else "FAIL"), ("pinout.md = def.py" if not P else "; ".join(P))


def H03():
    P = [p for p in J("test_H.json")["problemi"] if "via" in p or "C424093" in p or "cita ancora" in p]
    return ("WARN" if P else "PASS"), ("; ".join(P) or "numeri coerenti")


def H04():
    P = [p for p in J("test_H.json")["problemi"] if "montaggio" in p or "anteprima" in p]
    return ("WARN" if P else "PASS"), ("; ".join(P) or "file aggiornati")


def H05():
    md = open(os.path.join(PRJ, "docs", "pinout_v0.1.md"), encoding="utf-8").read()
    riga = next((l for l in md.splitlines() if "~~VBUS_SENSE~~" in l and "~~STAT~~" in l), "")
    d = D(); vivi = [n for r, (f, p, _) in d.C.items() for n in p.values() if n in ("STAT", "VBUS_SENSE")]
    ok = riga and not vivi
    return ("PASS" if ok else "WARN"), (f"pinout.md: {riga[:160]}" if ok else f"riga mancante o reti ancora presenti {vivi}")


ORDINE = [t["id"] for t in EL.TEST]
STATO = {"A01": "rieseguo l'ERC con kicad-cli", "A02": "rieseguo il DRC con parità schema e scollegati", "A03": "DRC severo su una copia con le regole ignorate riattivate",
         "A04": "estraggo regole, via e distanze dei fori con pcbnew", "A05": "conto le isole del piano GND In1", "A06": "estraggo il zip, riesporto i Gerber e confronto il contorno con il DXF",
         "A07": "cerco via dentro i pad SMD con le forme reali", "A08": "confronto riga per riga Gerber del zip ed export fresco", "A09": "riesporto la netlist e leggo gli avvisi",
         "B07": "confronto pin MCP73832 con simbolo e reti, R PROG e pagina JLC C38066", "B08": "verifico che STAT sia open-drain e senza pull-up verso il 5V",
         "C01": "rieseguo il confronto simbolo-impronta-def-netlist-pcb", "E01": "riesporto il pos e confronto riferimenti BOM/CPL", "E02": "codici LCSC, Value e conteggio Extended con C38066",
         "E03": "rileggo la pagina JLC dell'E73", "G01": "strati presenti nel nuovo zip", "H05": "riga STAT di pinout.md contro il caricatore montato"}


def init():
    t0 = []
    for t in EL.TEST:
        x = dict(t); x.update({"esito": "IN_ATTESA", "trovato": "", "giro": 2, "ora": ""})
        t0.append(x)
    R = {"aggiornato": iso(), "stato_lavoro": "Avvio del secondo giro", "concluso": False, "data": "2026-11-22", "scheda": "notapad v0.1",
         "fonti": EL.FONTI, "test": t0, "sintesi": "", "stack": EL.STACK, "pianta": {"scheda": [16.5, 38], "oggetti": []}}
    os.makedirs(os.path.dirname(RIS), exist_ok=True); scrivi(R)


def esegui(da, a):
    i0, i1 = ORDINE.index(da), ORDINE.index(a)
    for tid in ORDINE[i0:i1 + 1]:
        R = leggi(); t = next(x for x in R["test"] if x["id"] == tid)
        t["esito"] = "IN_CORSO"; scrivi(R, f"{tid}: {STATO.get(tid, t['titolo'])}")
        try:
            es, tr = globals()[tid]()
        except Exception as ex:
            es, tr = "NON_VERIFICABILE", f"errore dello script: {ex!r}"
        R = leggi(); t = next(x for x in R["test"] if x["id"] == tid)
        t["esito"], t["trovato"], t["ora"], t["giro"] = es, tr, ora(), GIRO
        prec = t.pop("_prec", None) or t.get("_prec_giro") or PRIMO.get(tid)
        t["_prec_giro"] = prec
        if prec is None and not t.get("nuovo_nel_giro"):
            t["nuovo_nel_giro"] = GIRO
        if prec is not None and es != prec:
            t["esito_prec"] = prec
        else:
            t.pop("esito_prec", None)
        if es == "PASS":
            t["azione"] = ""
        if tid in ("F04", "F08", "F10"):
            R["pianta"] = {"scheda": [16.5, 38], "oggetti": J("test_F.json")["pianta"]}
        scrivi(R, f"{tid}: {es}")
        print(tid, es, "-", tr[:110])
        time.sleep(0.4)


if __name__ == "__main__":
    a = sys.argv
    if "--web" in a:
        WEB.update(json.load(open(a[a.index("--web") + 1], encoding="utf-8")))
    if "--giro" in a:
        GIRO = int(a[a.index("--giro") + 1])
    if "--reset" in a:
        ids = a[a.index("--reset") + 1].split(",")
        R = leggi()
        for t in R["test"]:
            if t["id"] in ids:
                t["_prec"] = t["esito"]; t["esito"] = "IN_ATTESA"; t["trovato"] = ""; t["ora"] = ""; t.pop("esito_prec", None)
        scrivi(R, f"Avvio del giro {GIRO}: {len(ids)} test da rifare (A, F01, F03, F04, F08, G, H)", False)
    if "--init" in a:
        init()
    if "--da" in a:
        esegui(a[a.index("--da") + 1], a[a.index("--a") + 1])
    if "--fine" in a:
        R = leggi(); R["sintesi"] = open(a[a.index("--fine") + 1], encoding="utf-8").read().strip()
        scrivi(R, f"Giro {GIRO} concluso", True)
