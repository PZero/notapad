"""Genera notapad_v0.1.kicad_sch: simboli in griglia, etichetta di rete su ogni pin, X sui pin liberi.
Python di sistema:  python genera_sch.py
"""
import os, re, sys, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as D

LIBF = os.path.join(HERE, "lib", "notapad.kicad_sym")
OUT = os.path.join(HERE, "notapad_v0.1.kicad_sch")
NS = uuid.UUID("6a2b0000-0000-4000-8000-000000000001")   # UUID stabili tra una rigenerazione e l'altra


def uid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


# ---------- lettura libreria (blocchi simbolo di primo livello) ----------
PAD1 = '''  (symbol "PAD1"
    (in_bom yes)
    (on_board yes)
    (property "Reference" "J" (id 0) (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PAD1" (id 1) (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (id 3) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "PAD1_0_1"
      (circle (center 0 0) (radius 0.762) (stroke (width 0.254) (type default)) (fill (type none)))
      (pin passive line (at -3.81 0 0) (length 3.048)
        (name "1" (effects (font (size 1.27 1.27))))
        (number "1" (effects (font (size 1.27 1.27))))
      )
    )
  )
'''
lib = open(LIBF, encoding="utf-8").read()
if '(symbol "PAD1"' not in lib:
    lib = lib.rstrip()[:-1].rstrip() + "\n" + PAD1 + ")\n"
    open(LIBF, "w", encoding="utf-8").write(lib)


def blocks(text):
    """nome -> testo del blocco (symbol "NOME" ...) di primo livello"""
    out, i = {}, 0
    while True:
        m = re.compile(r'\n  \(symbol "([^"]+)"').search(text, i)
        if not m:
            return out
        start = m.start() + 1; depth = 0; j = start
        while True:
            c = text[j]
            if c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: break
            elif c == '"':
                j = text.index('"', j + 1)
            j += 1
        out[m.group(1)] = text[start:j + 1]; i = j


LB = blocks(lib)


def pins_of(block, unit=None):
    """pin (x, y, angolo, lunghezza, numero) dell'unità richiesta (le unità 0 sono comuni)"""
    out = []
    parts = re.split(r'(\(symbol "[^"]+_\d+_\d+")', block)
    cur = 0
    for p in parts:
        m = re.match(r'\(symbol "[^"]+_(\d+)_\d+"', p)
        if m:
            cur = int(m.group(1)); continue
        if unit is not None and cur not in (0, unit):
            continue
        out += [(float(x), float(y), int(float(a)), float(l), num, name) for x, y, a, l, name, num in re.findall(
            r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length ([-\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]+)"', p, re.S)]
    return out


def units_of(block):
    u = sorted({int(x) for x in re.findall(r'\(symbol "[^"]+_(\d+)_\d+"', block)} - {0})
    return u or [1]


def snap(v, g=2.54):
    return round(v / g) * g


# ---------- piazzamento nello schema: gruppi funzionali in colonne ----------
groups = [
    ("Alimentazione e latch", ["J1", "J2", "BT1P", "BT1N", "C1", "U3", "R1", "C2", "D5", "R3", "D6", "R4", "C14", "Q2", "Q3",
                               "R2", "Q1", "C10", "R5", "R6", "R7", "U4", "C3", "C4", "C5", "R8", "R9", "C11"]),
    ("nRF52840 e memoria", ["U1", "J3", "J4", "U2", "C7"]),
    ("Audio, tocco, LED, motore", ["MK1", "C8", "MK2", "C9", "U5", "C12", "TPA", "U6", "C13", "TPB",
                                   "D1", "R11", "D2", "R12", "D3", "R13", "Q4", "R10", "D4", "M1P", "M1N"]),
]

items, labels, ncs, texts = [], [], [], []
ncnets = {}
col_x = 25.4
for title, refs in groups:
    refs = [r for r in refs if r in D.C]
    texts.append((title, col_x, 20.32))
    y = 30.48; colw = 0
    for ref in refs:
        fam, pads, _ = D.C[ref]
        sym, fpn, lcsc, val = D.P[fam]
        blk = LB[sym]
        for unit in units_of(blk):
          pins = pins_of(blk, unit)
          xs = [p[0] for p in pins]; ys = [p[1] for p in pins]
          w = max(xs) - min(xs); h = max(ys) - min(ys)
          cx = snap(col_x - min(xs) + 15.24)
          cy = snap(y + max(ys) + 5.08)
          items.append((ref, sym, fpn, lcsc, val, cx, cy, unit))
          for px, py, ang, ln, num, pname in pins:
            X, Y = round(cx + px, 3), round(cy - py, 3)
            net = pads.get(num)
            if net is None:
                ncs.append((X, Y)); ncnets[f"{ref}.{num}"] = f"unconnected-({ref}-{pname}-Pad{num})"
            else:
                la = {0: 180, 180: 0, 90: 270, 270: 90}[ang]
                labels.append((net, X, Y, la))
          y = cy - min(ys) + 10.16
          colw = max(colw, w + 45)
          if y > 380:
              col_x += colw; colw = 0; y = 30.48
    col_x += colw + 10.16

# ---------- scrittura ----------
o = []
o.append('(kicad_sch (version 20211123) (generator genera_sch.py)\n')
o.append(f'  (uuid {uid("root")})\n  (paper "A1")\n')
o.append('  (title_block (title "notªpad v0.1") (date "2026-11-21") (rev "0.1") (company "Genova"))\n')
o.append('  (lib_symbols\n')
for sym in sorted({i[1] for i in items}):
    blk = LB[sym].replace(f'(symbol "{sym}"', f'(symbol "notapad:{sym}"', 1)
    o.append("    " + blk.replace("\n", "\n  ") + "\n")
o.append('  )\n')
for t, x, y in texts:
    o.append(f'  (text "{t}" (at {x} {y} 0) (effects (font (size 3 3) bold) (justify left bottom)) (uuid {uid("t", t)}))\n')
for net, x, y, a in labels:
    j = "right" if a in (180, 270) else "left"
    o.append(f'  (global_label "{net}" (shape passive) (at {x} {y} {a}) (fields_autoplaced) '
             f'(effects (font (size 1.016 1.016)) (justify {j})) (uuid {uid("l", net, x, y)}))\n')
for x, y in ncs:
    o.append(f'  (no_connect (at {x} {y}) (uuid {uid("nc", x, y)}))\n')
for ref, sym, fpn, lcsc, val, cx, cy, unit in items:
    u = uid("sym", ref, unit) if unit > 1 else uid("sym", ref)
    o.append(f'  (symbol (lib_id "notapad:{sym}") (at {cx} {cy} 0) (unit {unit}) (in_bom {"no" if not lcsc else "yes"}) (on_board yes)\n')
    o.append(f'    (uuid {u})\n')
    o.append(f'    (property "Reference" "{ref}" (id 0) (at {cx} {cy - 3.81} 0) (effects (font (size 1.27 1.27))))\n')
    o.append(f'    (property "Value" "{val}" (id 1) (at {cx} {cy + 3.81} 0) (effects (font (size 1.27 1.27))))\n')
    o.append(f'    (property "Footprint" "notapad:{fpn}" (id 2) (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) hide))\n')
    o.append(f'    (property "Datasheet" "" (id 3) (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) hide))\n')
    o.append(f'    (property "LCSC Part" "{lcsc}" (id 4) (at {cx} {cy} 0) (effects (font (size 1.27 1.27)) hide))\n')
    for p in pins_of(LB[sym]):
        o.append(f'    (pin "{p[4]}" (uuid {uid("pin", ref, p[4])}))\n')
    o.append('  )\n')
o.append('  (sheet_instances (path "/" (page "1")))\n  (symbol_instances\n')
for ref, sym, fpn, lcsc, val, cx, cy, unit in items:
    u = uid("sym", ref, unit) if unit > 1 else uid("sym", ref)
    o.append(f'    (path "/{u}" (reference "{ref}") (unit {unit}) (value "{val}") (footprint "notapad:{fpn}"))\n')
o.append('  )\n)\n')
open(OUT, "w", encoding="utf-8").write("".join(o))
import json
json.dump(ncnets, open(os.path.join(HERE, "nc_nets.json"), "w"), indent=1)
print(len(items), "simboli,", len(labels), "etichette,", len(ncs), "pin liberi ->", OUT)
