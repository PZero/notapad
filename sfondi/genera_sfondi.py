#!/usr/bin/env python3
"""Genera gli 8 sfondi notªpad come SVG (sfondi/sorgenti/), vettoriali.

Canvas di progetto 1080 x 2400 (Android). Per iPhone 1179 x 2556 lo stesso SVG
viene reso con preserveAspectRatio="slice" (taglia ~32 px sopra e sotto):
il contenuto importante sta quindi tra y=100 e y=2300.
Zone telefono: orologio nel 30% alto (y < 720): nessun soggetto importante.
Spazio sponsor: <g id="sponsor"> separato, in basso al centro (sopra la barra home).
Sostituzione: cambiare il contenuto di <g id="sponsor"> con <image href="logo.png" .../>.
"""
import math, os, random
from scipy.spatial import Delaunay
import numpy as np

W, H = 1080, 2400
CX = W / 2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorgenti")
FONT = "'Inter Tight','Inter','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Mono',Consolas,'Courier New',monospace"
BRONZE, LED, INK, MUTE = "#b8895a", "#5fd3c8", "#efebe3", "#9a968e"

FINISHES = {
    "carbon": dict(name="Forged carbon", a="#232326", b="#0c0c0e", s1="#6a655c", s2="#2c2a27", gloss=.10, facets=True),
    "soft": dict(name="Soft-touch black", a="#3a3835", b="#1d1c1b", s1="#77716a", s2="#3a3733", gloss=.03),
    "gloss": dict(name="Gloss black", a="#15151a", b="#020203", s1="#52504f", s2="#1b1a19", gloss=.22),
    "anth": dict(name="Metallic anthracite", a="#4a4c52", b="#25262a", s1="#9b948a", s2="#4d4943", gloss=.14),
    "blue": dict(name="Midnight blue", a="#16295a", b="#071331", s1="#6b7390", s2="#222b48", gloss=.16),
    "ivory": dict(name="Ivory", a="#e8e1d3", b="#cdc4b3", s1="#f3eee4", s2="#bdb4a3", gloss=.12),
}


def svg_open(bg_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'preserveAspectRatio="xMidYMid slice" font-family="{FONT}">\n<defs>{bg_defs}</defs>\n')


def sponsor(color=INK, op=.5):
    return f'''<!-- SPONSOR PLACEHOLDER: replace the content of this group with the real logo, centred at (540, 2290) -->
<g id="sponsor" opacity="{op}" transform="translate({CX},2290)" fill="none" stroke="{color}">
  <rect x="-150" y="-30" width="300" height="60" rx="30" stroke-width="1.6"/>
  <text x="3" y="8" text-anchor="middle" font-size="22" letter-spacing="7" fill="{color}" stroke="none" font-weight="500">SPONSOR</text>
</g>
'''


def wordmark(y, color=INK, op=.9, size=46, sub=None):
    s = f'<g id="wordmark" text-anchor="middle" fill="{color}"><text x="{CX}" y="{y}" font-size="{size}" font-weight="600" letter-spacing="-1" opacity="{op}">notªpad</text>'
    if sub:
        s += f'<text x="{CX}" y="{y+40}" font-size="21" letter-spacing="5" fill="{MUTE}" opacity=".9">{sub}</text>'
    return s + "</g>\n"


def grain(opacity=.05, seed=3):
    return (f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="{seed}" result="n"/>'
            f'<feColorMatrix type="saturate" values="0"/></filter>')


def grain_rect(opacity=.06):
    return f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{opacity}" style="mix-blend-mode:overlay"/>\n'


def monolith(cx, top, h, fkey, p, led=True, cord=False, side=True, cord_x=None):
    """Monolite frontale con fianco; p = prefisso id univoco. Ritorna (svg, geom)."""
    f = FINISHES[fkey]
    w = h * 17.5 / 41
    s = w * .13 if side else 0
    x0 = cx - (w + s) / 2
    r = w * .10
    ringr = w * .165
    ringc = top - ringr + w * .045
    out = []
    d = f'''<defs>
<linearGradient id="{p}f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{f['a']}"/><stop offset="1" stop-color="{f['b']}"/></linearGradient>
<linearGradient id="{p}sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset=".25" stop-color="#fff" stop-opacity=".02"/><stop offset=".8" stop-color="#000" stop-opacity=".10"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></linearGradient>
<linearGradient id="{p}sd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{f['s1']}"/><stop offset="1" stop-color="{f['s2']}"/></linearGradient>
<linearGradient id="{p}ed" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".35" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity=".18"/></linearGradient>
<linearGradient id="{p}gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a5230"/><stop offset=".4" stop-color="#f0cf9c"/><stop offset="1" stop-color="#9a6d40"/></linearGradient>
<linearGradient id="{p}st" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f6"/><stop offset=".45" stop-color="#6c6e76"/><stop offset=".7" stop-color="#dcdde2"/><stop offset="1" stop-color="#4a4b52"/></linearGradient>
<linearGradient id="{p}led" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff7a8a"/><stop offset=".18" stop-color="#e8ffff"/><stop offset=".5" stop-color="#ffffff"/><stop offset=".82" stop-color="#e8fff0"/><stop offset="1" stop-color="#7affb8"/></linearGradient>
<filter id="{p}glow" x="-60%" y="-400%" width="220%" height="900%"><feGaussianBlur stdDeviation="{max(4,w*.035):.1f}"/></filter>
<filter id="{p}glow2" x="-100%" y="-800%" width="300%" height="1700%"><feGaussianBlur stdDeviation="{max(10,w*.12):.1f}"/></filter>
<clipPath id="{p}cl"><rect x="{x0:.1f}" y="{top:.1f}" width="{w+s:.1f}" height="{h:.1f}" rx="{r:.1f}"/></clipPath>
</defs>'''
    out.append(d)
    if cord:
        cxr = cord_x if cord_x else w * 2.2
        rt = ringc - ringr
        out.append(f'''<defs><linearGradient id="{p}cg" gradientUnits="userSpaceOnUse" x1="0" y1="-20" x2="0" y2="{rt:.0f}"><stop offset="0" stop-color="#26262a" stop-opacity="0"/><stop offset=".55" stop-color="#2c2c31" stop-opacity=".95"/><stop offset="1" stop-color="#34343a"/></linearGradient></defs>
<g fill="none" stroke="url(#{p}cg)" stroke-width="{max(5,w*.018):.1f}" stroke-linecap="round">
<path d="M{cx-cxr:.0f} -20 C{cx-cxr*.55:.0f} {rt*.55:.0f} {cx-w*.3:.0f} {rt*.9:.0f} {cx:.0f} {rt+4:.0f}"/>
<path d="M{cx+cxr:.0f} -20 C{cx+cxr*.55:.0f} {rt*.55:.0f} {cx+w*.3:.0f} {rt*.9:.0f} {cx:.0f} {rt+4:.0f}"/></g>''')
    # ombra morbida di alone
    out.append(f'<g id="{p}ring"><circle cx="{cx:.1f}" cy="{ringc:.1f}" r="{ringr:.1f}" fill="none" stroke="url(#{p}st)" stroke-width="{w*.05:.1f}"/>'
               f'<circle cx="{cx:.1f}" cy="{ringc:.1f}" r="{ringr+w*.025:.1f}" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="1"/></g>')
    out.append(f'<g clip-path="url(#{p}cl)"><rect x="{x0:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{p}f)"/>')
    if f.get("facets"):
        rnd = random.Random(7)
        pts = np.array([[rnd.uniform(x0 - 30, x0 + w + 30), rnd.uniform(top - 30, top + h + 30)] for _ in range(70)])
        tri = Delaunay(pts)
        for t in tri.simplices:
            a = pts[t]
            g = rnd.randint(8, 70)
            out.append('<polygon points="' + " ".join(f"{x:.0f},{y:.0f}" for x, y in a) + f'" fill="rgb({g},{g},{g+3})" fill-opacity=".62" stroke="#000" stroke-opacity=".18" stroke-width=".8"/>')
    out.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{p}sh)"/>')
    if side:
        out.append(f'<rect x="{x0+w:.1f}" y="{top:.1f}" width="{s:.1f}" height="{h:.1f}" fill="url(#{p}sd)"/>')
        out.append(f'<rect x="{x0+w+s*.36:.1f}" y="{top+h*.42:.1f}" width="{s*.3:.1f}" height="{h*.27:.1f}" rx="{s*.05:.1f}" fill="url(#{p}gold)"/>')
        out.append(f'<rect x="{x0+w-s*.08:.1f}" y="{top:.1f}" width="{s*.16:.1f}" height="{h:.1f}" fill="#000" opacity=".35"/>')
    if f["gloss"]:
        out.append(f'<polygon points="{x0:.0f},{top:.0f} {x0+w*.62:.0f},{top:.0f} {x0:.0f},{top+h*.5:.0f}" fill="#fff" opacity="{f["gloss"]}"/>')
    out.append('</g>')
    out.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{w+s:.1f}" height="{h:.1f}" rx="{r:.1f}" fill="none" stroke="url(#{p}ed)" stroke-width="{max(1.5,w*.006):.1f}"/>')
    if led:
        sx, sy, sw, sh = cx - s / 2 - w * .28, top + h * .26, w * .56, w * .075
        out.append(f'<rect x="{sx-4:.1f}" y="{sy-4:.1f}" width="{sw+8:.1f}" height="{sh+8:.1f}" rx="{sh*.3:.1f}" fill="#000" opacity=".55"/>')
        out.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="url(#{p}led)" filter="url(#{p}glow2)" opacity=".55"/>')
        out.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="url(#{p}led)" filter="url(#{p}glow)" opacity=".9"/>')
        out.append(f'<rect id="{p}slit" x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" rx="{sh*.12:.1f}" fill="url(#{p}led)"/>')
    geom = dict(w=w, s=s, x0=x0, ringc=ringc, ringr=ringr, top=top, h=h)
    return "\n".join(out) + "\n", geom


def write(n, name, body_svg):
    path = os.path.join(OUT, f"{n:02d}_{name}.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body_svg + "</svg>\n")
    print("scritto", path)


# ---------------------------------------------------------------- 1
def s1():
    bg = '''<radialGradient id="bg" cx=".5" cy=".58" r=".75"><stop offset="0" stop-color="#1b2c58"/><stop offset=".55" stop-color="#0a1128"/><stop offset="1" stop-color="#04050b"/></radialGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#5fd3c8" stop-opacity=".32"/><stop offset="1" stop-color="#5fd3c8" stop-opacity="0"/></radialGradient>
<radialGradient id="floor" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#b8895a" stop-opacity=".18"/><stop offset="1" stop-color="#b8895a" stop-opacity="0"/></radialGradient>''' + grain()
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n'
    s += f'<ellipse cx="{CX}" cy="1360" rx="560" ry="760" fill="url(#halo)"/>\n'
    m, g = monolith(CX, 960, 880, "blue", "a", cord=True, cord_x=470)
    s += m
    s += f'<ellipse cx="{CX}" cy="2010" rx="330" ry="46" fill="url(#floor)"/>\n'
    s += wordmark(2090, sub="OPEN WEARABLE RECORDER")
    s += grain_rect(.07) + sponsor()
    write(1, "midnight", s)


# ---------------------------------------------------------------- 2
def s2():
    bg = '''<radialGradient id="bg" cx=".5" cy=".55" r=".8"><stop offset="0" stop-color="#17181d"/><stop offset="1" stop-color="#020203"/></radialGradient>
<linearGradient id="rf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset=".3" stop-color="#fff" stop-opacity=".09"/><stop offset=".34" stop-color="#fff" stop-opacity=".0"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="b1" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="26"/></filter>
<filter id="b2" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="b3" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="90"/></filter>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".08" stop-color="#fff" stop-opacity=".05"/><stop offset=".92" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity=".3"/></linearGradient>
<linearGradient id="stl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f6"/><stop offset=".45" stop-color="#6c6e76"/><stop offset=".7" stop-color="#dcdde2"/><stop offset="1" stop-color="#4a4b52"/></linearGradient>''' + grain()
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n'
    bx, bw = 80, 920
    top = 1000
    s += f'<rect x="{bx}" y="{top}" width="{bw}" height="1500" rx="96" fill="#0a0a0d" stroke="url(#edge)" stroke-width="3"/>\n'
    s += f'<rect x="{bx}" y="{top}" width="{bw}" height="1500" rx="96" fill="url(#rf)"/>\n'
    # anello (parziale)
    s += f'<circle cx="{CX}" cy="{top-90}" r="130" fill="none" stroke="url(#stl)" stroke-width="40"/>\n'
    s += f'<path d="M{bx+96} {top} H{bx+bw-96}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>\n'
    sx, sw, sy, sh = 300, 480, 1330, 64
    # alone colore dei 3 LED
    for i, (c, x) in enumerate((("#ff3a55", sx + 80), ("#35ff9a", CX), ("#3a7bff", sx + sw - 80))):
        s += f'<ellipse cx="{x}" cy="{sy+sh/2}" rx="150" ry="70" fill="{c}" opacity=".55" filter="url(#b1)" style="mix-blend-mode:screen"/>\n'
    s += f'<ellipse cx="{CX}" cy="{sy+sh/2+160}" rx="420" ry="300" fill="#8fe8ff" opacity=".12" filter="url(#b3)"/>\n'
    s += f'<rect x="{sx-12}" y="{sy-12}" width="{sw+24}" height="{sh+24}" rx="14" fill="#000"/>\n'
    s += f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="6" fill="#050507"/>\n'
    for c, x0 in (("#ff3a55", sx), ("#35ff9a", sx + sw / 3), ("#3a7bff", sx + 2 * sw / 3)):
        s += f'<rect x="{x0:.0f}" y="{sy}" width="{sw/3:.0f}" height="{sh}" fill="{c}" opacity=".55" filter="url(#b2)" style="mix-blend-mode:screen"/>\n'
    s += f'<rect x="{sx+6}" y="{sy+14}" width="{sw-12}" height="{sh-28}" rx="4" fill="#fff" opacity=".96" filter="url(#b2)"/>\n'
    s += f'<rect x="{sx+10}" y="{sy+22}" width="{sw-20}" height="{sh-44}" rx="3" fill="#fff"/>\n'
    s += f'<text x="{CX}" y="1750" text-anchor="middle" font-size="22" letter-spacing="8" fill="{MUTE}" opacity=".8">THREE LEDS. ONE SLIT.</text>\n'
    s += wordmark(2120, size=44)
    s += grain_rect(.06) + sponsor()
    write(2, "macro-slit", s)


# ---------------------------------------------------------------- 3
def s3():
    bg = '''<radialGradient id="bg" cx=".5" cy=".5" r=".8"><stop offset="0" stop-color="#2a2118"/><stop offset=".6" stop-color="#0f0c0a"/><stop offset="1" stop-color="#050404"/></radialGradient>
<radialGradient id="gd" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff2cf"/><stop offset=".25" stop-color="#e2b676"/><stop offset=".7" stop-color="#8e6030"/><stop offset="1" stop-color="#4c3015"/></radialGradient>
<radialGradient id="gh" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f0c27a" stop-opacity=".35"/><stop offset="1" stop-color="#f0c27a" stop-opacity="0"/></radialGradient>
<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b2420"/><stop offset="1" stop-color="#0b0908"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".4"/><stop offset=".4" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#fff" stop-opacity=".12"/></linearGradient>''' + grain(seed=9)
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n'
    top = 960
    s += f'<rect x="90" y="{top}" width="900" height="1500" rx="110" fill="url(#bd)" stroke="url(#edge)" stroke-width="3"/>\n'
    s += f'<rect x="90" y="{top}" width="900" height="1500" rx="110" filter="url(#grain)" opacity=".10" style="mix-blend-mode:overlay"/>\n'
    pts = [(CX - 250, 0), (CX - 110, 0), (CX + 110, 0), (CX + 250, 0)]
    cy = top + 170
    for i, (x, _) in enumerate(pts):
        s += f'<circle cx="{x}" cy="{cy}" r="120" fill="url(#gh)"/>\n'
        s += f'<circle cx="{x}" cy="{cy}" r="60" fill="#070504"/>\n'
        s += f'<circle cx="{x}" cy="{cy}" r="54" fill="url(#gd)"/>\n'
        s += f'<circle cx="{x}" cy="{cy}" r="54" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>\n'
        s += f'<ellipse cx="{x-14}" cy="{cy-18}" rx="22" ry="11" fill="#fff" opacity=".45" transform="rotate(-25 {x-14} {cy-18})"/>\n'
    labels = ["5V", "GND", "SWDIO", "SWCLK"]
    for (x, _), t in zip(pts, labels):
        s += f'<path d="M{x} {cy+78} V{cy+170}" stroke="{BRONZE}" stroke-opacity=".6" stroke-width="1.5"/>\n'
        s += f'<text x="{x}" y="{cy+210}" text-anchor="middle" font-family="{MONO}" font-size="26" letter-spacing="3" fill="{INK}" opacity=".85">{t}</text>\n'
    s += f'<path d="M{CX-250} {cy-100} H{CX-110} M{CX+110} {cy-100} H{CX+250}" stroke="{BRONZE}" stroke-opacity=".6" stroke-width="1.5"/>\n'
    s += f'<text x="{CX-180}" y="{cy-120}" text-anchor="middle" font-family="{MONO}" font-size="20" letter-spacing="3" fill="{BRONZE}">CHARGE</text>\n'
    s += f'<text x="{CX+180}" y="{cy-120}" text-anchor="middle" font-family="{MONO}" font-size="20" letter-spacing="3" fill="{BRONZE}">PROGRAM</text>\n'
    s += f'<text x="{CX}" y="1790" text-anchor="middle" font-size="24" letter-spacing="8" fill="{MUTE}" opacity=".85">FOUR GOLD CONTACTS</text>\n'
    s += wordmark(2120, size=44)
    s += grain_rect(.05) + sponsor()
    write(3, "gold-contacts", s)


# ---------------------------------------------------------------- 4
def s4():
    bg = '''<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1426"/><stop offset="1" stop-color="#050a14"/></linearGradient>
<pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0H0V60" fill="none" stroke="#5fd3c8" stroke-opacity=".07" stroke-width="1"/></pattern>
<filter id="gl"><feGaussianBlur stdDeviation="6"/></filter>'''
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>\n'
    k = 13.0  # px per mm
    M = "matrix(.866 .5 -.866 .5 0 0)"
    # centri dei piani (x=cx), quattro strati
    layers = [("a", 850), ("b", 1130), ("c", 1410), ("d", 1690)]
    cxs = CX - 110
    s += f'<path d="M{cxs} 700 V1980" stroke="{LED}" stroke-opacity=".25" stroke-dasharray="4 10"/>\n'
    for idx, (name, cy) in enumerate(layers):
        if idx == 1:
            pw, ph = 16.5 * k, 38 * k
        else:
            pw, ph = 17.5 * k, 41 * k
        s += f'<g transform="translate({cxs},{cy})">'
        # spessore
        th = 16 if idx != 1 else 6
        s += f'<g transform="translate(0,{th}) {M}"><rect x="{-pw/2}" y="{-ph/2}" width="{pw}" height="{ph}" rx="{12 if idx!=1 else 3}" fill="#000" opacity=".5"/></g>'
        fill = {0: "#13264d", 1: "#0c2a2e", 2: "#16192a", 3: "#13264d"}[idx]
        stroke = {0: "#8aa4d8", 1: LED, 2: "#a9a4d8", 3: "#8aa4d8"}[idx]
        s += f'<g transform="{M}"><rect x="{-pw/2}" y="{-ph/2}" width="{pw}" height="{ph}" rx="{12 if idx!=1 else 3}" fill="{fill}" fill-opacity=".88" stroke="{stroke}" stroke-width="1.8"/>'
        x0, y0 = -pw / 2, -ph / 2
        def comp(x, y, w, h, c="none", st=LED, op=.9):
            return f'<rect x="{x0+x*k:.1f}" y="{y0+y*k:.1f}" width="{w*k:.1f}" height="{h*k:.1f}" rx="2" fill="{c}" stroke="{st}" stroke-width="1.5" opacity="{op}"/>'
        if idx == 1:
            s += comp(2, 20.5, 12.5, 16, "#16494b")            # E73
            s += comp(3, 22, 10.5, 2.5, "none")
            s += comp(3.5, 12, 9.5, 6, "#16494b")              # NAND
            for j in range(3):
                s += comp(5.6, 8.2 + j * 3.1 - 1, 5, 2.4, "#3a2a45", "#e0a8ff")
            s += comp(2, 1, 3.2, 2.4, "#4a3a1e", BRONZE); s += comp(11, 1, 3.2, 2.4, "#4a3a1e", BRONZE)
            s += comp(6.3, 3.6, 4, 3, "#16494b")
            # contatti
            for cx_, cy_ in ((3, .8), (13.5, .8), (3, 4.2), (13.5, 4.2)):
                s += f'<circle cx="{x0+cx_*k:.1f}" cy="{y0+cy_*k:.1f}" r="{k*.55:.1f}" fill="#e2b676" stroke="#fff3d6" stroke-width="1"/>'
            # tracce
            s += f'<path d="M{x0+8*k} {y0+7*k} V{y0+20.5*k} M{x0+4*k} {y0+18*k} H{x0+12*k}" stroke="{LED}" stroke-opacity=".5" stroke-width="1.4" fill="none"/>'
            s += f'<rect x="{x0+1.2*k}" y="{y0+27.5*k}" width="{14.1*k}" height="{9.8*k}" rx="3" fill="none" stroke="{LED}" stroke-opacity=".5" stroke-dasharray="4 5"/>'
        elif idx == 2:
            s += comp(3, 20, 11.5, 19, "#3a2f55", "#c7bdf0")   # batteria
            s += f'<circle cx="{x0+8.75*k:.1f}" cy="{y0+9*k:.1f}" r="{4*k:.1f}" fill="#252040" stroke="#c7bdf0" stroke-width="1.6"/>'
        elif idx in (0, 3):
            if idx == 0:
                s += f'<rect x="{x0+3.2*k}" y="{y0+10*k}" width="{10*k}" height="{.9*k}" fill="#fff" opacity=".9"/>'
            s += f'<circle cx="{x0+pw/2}" cy="{y0}" r="{k*1.8}" fill="none" stroke="#e8e8ee" stroke-width="3"/>' if idx == 0 else ""
        s += '</g></g>\n'
    # etichette
    for name, cy in layers:
        yy = cy + 60
        s += f'<path d="M{cxs+300} {cy} H{cxs+360}" stroke="{BRONZE}" stroke-opacity=".7"/><circle cx="{cxs+300}" cy="{cy}" r="4" fill="{BRONZE}"/>\n'
    for (name, cy), t in zip(layers, ["Resin shell", "Board", "Battery + motor", "Resin shell"]):
        s += f'<text x="{cxs+370}" y="{cy+8}" font-family="{MONO}" font-size="23" fill="{INK}" opacity=".85" letter-spacing="1">{t}</text>\n'
    s += f'<text x="{CX}" y="2000" text-anchor="middle" font-family="{MONO}" font-size="21" letter-spacing="5" fill="{LED}" opacity=".85">EXPLODED VIEW · v0.1</text>\n'
    s += wordmark(2100, size=42)
    s += sponsor()
    write(4, "exploded-board", s)


# ---------------------------------------------------------------- 5
def s5():
    bg = '''<radialGradient id="bg" cx=".5" cy=".6" r=".9"><stop offset="0" stop-color="#101319"/><stop offset="1" stop-color="#030406"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".26" stop-color="#000"/><stop offset=".42" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="m"><rect width="1080" height="2400" fill="url(#fade)"/></mask>
<radialGradient id="dot1"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#5fd3c8"/><stop offset="1" stop-color="#5fd3c8" stop-opacity="0"/></radialGradient>
<radialGradient id="dot2"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#e0a266"/><stop offset="1" stop-color="#e0a266" stop-opacity="0"/></radialGradient>'''
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n<g mask="url(#m)" style="isolation:isolate">\n'
    p1, p2 = (CX - 190, 1330), (CX + 200, 1560)
    for (px, py), col in ((p1, LED), (p2, "#e0a266")):
        s += f'<g fill="none" stroke="{col}" style="mix-blend-mode:screen">'
        r = 24
        i = 0
        while r < 1500:
            op = max(.05, .62 - r / 2200)
            s += f'<circle cx="{px}" cy="{py}" r="{r}" stroke-opacity="{op:.2f}" stroke-width="{2 if i%4 else 3.2}"/>'
            r += 26
            i += 1
        s += '</g>\n'
    s += '</g>\n'
    s += f'<circle cx="{p1[0]}" cy="{p1[1]}" r="70" fill="url(#dot1)"/><circle cx="{p2[0]}" cy="{p2[1]}" r="70" fill="url(#dot2)"/>\n'
    s += f'<text x="{p1[0]-48}" y="{p1[1]-56}" text-anchor="end" font-family="{MONO}" font-size="22" letter-spacing="3" fill="{LED}">MIC 1 · FRONT</text>\n'
    s += f'<text x="{p2[0]+48}" y="{p2[1]+70}" font-family="{MONO}" font-size="22" letter-spacing="3" fill="#e0a266">MIC 2 · TOP</text>\n'
    s += wordmark(2100, size=44, sub="TWO MICROPHONES. ONE STEREO PICTURE.")
    s += sponsor()
    write(5, "two-microphones", s)


# ---------------------------------------------------------------- 6
def s6():
    bg = '''<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3eee5"/><stop offset=".6" stop-color="#e2dacb"/><stop offset="1" stop-color="#cbbfa9"/></linearGradient>
<radialGradient id="warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="34"/></filter>''' + grain(seed=5)
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n'
    s += f'<ellipse cx="{CX}" cy="1350" rx="560" ry="720" fill="url(#warm)"/>\n'
    s += f'<ellipse cx="{CX+60}" cy="1975" rx="260" ry="34" fill="#5a4a30" opacity=".35" filter="url(#sh)"/>\n'
    m, g = monolith(CX, 940, 880, "ivory", "a", cord=True, cord_x=470)
    s += m
    s += wordmark(2100, color="#2a2620", size=44, sub="IVORY")
    s += grain_rect(.08) + sponsor("#2a2620", .55)
    s = s.replace('fill="#26262a" stop-opacity="0"', 'fill="#26262a" stop-opacity="0"')
    write(6, "ivory-light", s)


# ---------------------------------------------------------------- 7
def s7():
    bg = '''<radialGradient id="bg" cx=".5" cy=".5" r=".85"><stop offset="0" stop-color="#232022"/><stop offset="1" stop-color="#070708"/></radialGradient>''' + grain()
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n'
    keys = ["carbon", "soft", "gloss", "anth", "blue", "ivory"]
    xs = [200, 540, 880]
    for i, k in enumerate(keys):
        col, row = i % 3, i // 3
        x = xs[col]
        top = 890 + row * 560 + (40 if col == 1 else 0)
        m, g = monolith(x, top, 380, k, f"m{i}")
        s += m
        s += f'<text x="{x}" y="{top+380+52}" text-anchor="middle" font-size="22" letter-spacing="1" fill="{INK}" opacity=".75">{FINISHES[k]["name"]}</text>\n'
    s += wordmark(2110, size=44, sub="SIX FINISHES")
    s += grain_rect(.06) + sponsor()
    write(7, "six-finishes", s)


# ---------------------------------------------------------------- 8
def s8():
    bg = '''<radialGradient id="bg" cx=".5" cy=".6" r=".8"><stop offset="0" stop-color="#16120f"/><stop offset="1" stop-color="#050404"/></radialGradient>
<linearGradient id="bar" gradientUnits="userSpaceOnUse" x1="90" y1="0" x2="990" y2="0"><stop offset="0" stop-color="#5fd3c8"/><stop offset=".55" stop-color="#8fb7a0"/><stop offset="1" stop-color="#b8895a"/></linearGradient>
<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".3" stop-color="#000"/><stop offset=".4" stop-color="#fff"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="m"><rect width="1080" height="2400" fill="url(#bf)"/></mask>
<radialGradient id="rec"><stop offset="0" stop-color="#ff5a5a"/><stop offset=".3" stop-color="#ff3a3a" stop-opacity=".7"/><stop offset="1" stop-color="#ff3a3a" stop-opacity="0"/></radialGradient>'''
    s = svg_open(bg) + f'<rect width="{W}" height="{H}" fill="url(#bg)"/>\n<g mask="url(#m)">\n'
    rnd = random.Random(11)
    n, step = 54, 18
    x0 = (W - n * step) / 2 + step / 2
    cy = 1500
    for i in range(n):
        t = i / (n - 1)
        env = math.exp(-((t - .5) / .28) ** 2) * .85 + .15
        hgt = max(14, 640 * env * (0.25 + 0.75 * abs(math.sin(i * .83) * math.cos(i * .37 + 1)) + rnd.random() * .2))
        x = x0 + i * step
        s += f'<line x1="{x:.1f}" y1="{cy-hgt/2:.1f}" x2="{x:.1f}" y2="{cy+hgt/2:.1f}" stroke="url(#bar)" stroke-width="9" stroke-linecap="round" opacity="{.4+.6*env:.2f}"/>\n'
    s += '</g>\n'
    s += f'<circle cx="{CX}" cy="1120" r="70" fill="url(#rec)"/><circle cx="{CX}" cy="1120" r="15" fill="#ff5a5a"/>\n'
    s += f'<text x="{CX}" y="1196" text-anchor="middle" font-family="{MONO}" font-size="24" letter-spacing="9" fill="{INK}" opacity=".85">REC</text>\n'
    s += f'<text x="{CX}" y="1890" text-anchor="middle" font-size="26" letter-spacing="1" fill="{INK}" opacity=".85">Records everything.</text>\n'
    s += f'<text x="{CX}" y="1930" text-anchor="middle" font-size="26" letter-spacing="1" fill="{MUTE}">You squeeze only when it matters.</text>\n'
    s += wordmark(2100, size=44)
    s += sponsor()
    write(8, "recording", s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (s1, s2, s3, s4, s5, s6, s7, s8):
        fn()
