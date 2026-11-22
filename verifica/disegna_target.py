"""Disegna verifica/target_sezione.svg: sezione in scala del monolite da 9 mm con i target 2,0 x 4,0 mm,
più la vista dal retro con contatti, motorino e batteria. Misure da notapad_def.py / risultati.json (giro 2).
Uso: python verifica/disegna_target.py
"""
import math
import pathlib

OUT = pathlib.Path(__file__).parent / "target_sezione.svg"

# --- misure (mm) ---
L, SP, LARG = 41.0, 9.0, 17.5            # monolite
OFF_L, OFF_X = 1.5, 0.5                  # scheda 38 x 16.5 dentro il monolite (ipotesi: centrata)
Z_FRONTE = 0.6                           # resina davanti
E73 = 3.0
Z_PCB0 = Z_FRONTE + E73                  # 3.6
Z_PCB1 = Z_PCB0 + 1.0                    # 4.6
BAT = 3.8                                # 381620
MOT = 2.0
J_Y = 2.5                                # asse dei contatti dal bordo alto della scheda
J_X = [1.8, 4.6, 11.9, 14.7]
CODA_D, CODA_L = 0.9, 2.0
SPALLA_D, SPALLA_L = 2.0, 0.5
CORPO_D, CORPO_L = 1.5, 4.0
MOT_C, MOT_R = (8.25, 7.8), 4.0          # centro motorino sulla scheda
BAT_Y = (12.8, 32.8)

S = 18          # px/mm vista in sezione
S2 = 12         # px/mm vista dal retro
INK, MUT, LINE = "#121315", "#5d636b", "#c9ccd1"
GOLD, BOARD, RES = "#d4a63a", "#1f7a4d", "#e8eaee"


def r(x, y, w, h, fill, stroke="none", sw=1, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def t(x, y, s, size=13, anchor="start", fill=INK, weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{s}</text>'


def quota(x1, y1, x2, y2, testo, lato=1):
    """quota verticale (x1==x2) o orizzontale"""
    g = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{MUT}" stroke-width="1" marker-start="url(#f)" marker-end="url(#f)"/>'
    if x1 == x2:
        g += t(x1 + 6 * lato, (y1 + y2) / 2 + 4, testo, 12, "start" if lato > 0 else "end", MUT)
    else:
        g += t((x1 + x2) / 2, y1 - 6, testo, 12, "middle", MUT)
    return g


parti = []
# ---------- vista 1: sezione lungo l'asse dei contatti ----------
X0, Y0 = 150, 150
Z = lambda z: Y0 + z * S
X = lambda l: X0 + l * S
parti.append(t(40, 40, "Sezione lungo la fila dei contatti (scala 18:1, misure in mm)", 18, weight=600))
parti.append(t(40, 64, "Fronte in alto, retro in basso. Target 2,0 × 4,0 mm in J1–J4, monolite 9 mm.", 13, fill=MUT))
# monolite
parti.append(f'<rect x="{X(0)}" y="{Z(0)}" width="{L*S}" height="{SP*S}" rx="{1.5*S}" fill="{RES}" stroke="{INK}" stroke-width="1.5"/>')
# anello
parti.append(f'<circle cx="{X(-1.6)}" cy="{Z(SP/2)}" r="{1.7*S}" fill="none" stroke="#9aa0a8" stroke-width="{0.6*S}"/>')
parti.append(t(X(-1.6), Z(SP/2) + 1.7*S + 28, "anello", 12, "middle", MUT))
# scheda
parti.append(r(X(OFF_L), Z(Z_PCB0), 38 * S, 1.0 * S, BOARD))
parti.append(t(X(OFF_L + 38) - 6, Z(Z_PCB0) + 13, "scheda 1,0", 12, "end", "#fff"))
# componenti lato sopra
parti.append(r(X(OFF_L + 19.97), Z(Z_FRONTE), 18.08 * S, E73 * S, "#3a3f47"))
parti.append(t(X(OFF_L + 29), Z(Z_FRONTE) + E73 * S / 2 + 5, "modulo E73 · 3,0", 13, "middle", "#fff"))
for l0, l1, h, nome in [(6.0, 7.5, 1.1, ""), (8.0, 9.0, 0.9, "LED"), (10.5, 16.5, 0.9, ""), (14.3, 18.4, 1.1, "")]:
    parti.append(r(X(OFF_L + l0), Z(Z_PCB0 - h), (l1 - l0) * S, h * S, "#7b828c"))
parti.append(t(X(OFF_L + 12), Z(Z_PCB0 - 1.1) - 6, "componenti bassi ≤ 1,1", 12, "middle", MUT))
# batteria e motorino (dietro la scheda)
parti.append(r(X(OFF_L + BAT_Y[0]), Z(Z_PCB1), 20 * S, BAT * S, "#c7b8e6"))
parti.append(t(X(OFF_L + 22.8), Z(Z_PCB1) + BAT * S / 2 + 5, "batteria 381620 · 3,8", 13, "middle"))
parti.append(r(X(OFF_L + MOT_C[1] - MOT_R), Z(Z_PCB1), 2 * MOT_R * S, MOT * S, "#f2d38a", "#b08a2e", 1, 'stroke-dasharray="5 3" fill-opacity=".55"'))
parti.append(t(X(OFF_L + MOT_C[1]) + 20, Z(SP) + 22, "motorino Ø8×2, tratteggiato: è fuori dal piano dei contatti", 12, "start", MUT))
# target
lj = OFF_L + J_Y
def target(lc, z_spalla):
    g = r(X(lc - CODA_D / 2), Z(z_spalla - CODA_L), CODA_D * S, CODA_L * S, GOLD, "#8a6a1c")
    g += r(X(lc - SPALLA_D / 2), Z(z_spalla), SPALLA_D * S, SPALLA_L * S, GOLD, "#8a6a1c")
    g += r(X(lc - CORPO_D / 2), Z(z_spalla + SPALLA_L), CORPO_D * S, CORPO_L * S, GOLD, "#8a6a1c")
    return g
parti.append(target(lj, Z_PCB1))
# stagno sopra
parti.append(f'<path d="M{X(lj-0.8)} {Z(Z_PCB0)} Q{X(lj-0.45)} {Z(Z_PCB0-0.7)} {X(lj-0.45)} {Z(Z_PCB0-1.0)} L{X(lj+0.45)} {Z(Z_PCB0-1.0)} Q{X(lj+0.45)} {Z(Z_PCB0-0.7)} {X(lj+0.8)} {Z(Z_PCB0)} Z" fill="#b9bcc2" opacity=".9"/>')
# quote sul target
zf = Z_PCB1 + SPALLA_L + CORPO_L
xq = X(lj) + 30
parti.append(quota(xq, Z(Z_PCB1), xq, Z(zf), "4,5", 1))
parti.append(quota(X(0) - 90, Z(0), X(0) - 90, Z(SP), "9,0", -1))
parti.append(f'<line x1="{X(0)-90}" y1="{Z(SP)}" x2="{X(lj)+60}" y2="{Z(SP)}" stroke="{INK}" stroke-dasharray="3 3"/>')
# etichette target
parti.append(f'<line x1="{X(lj)+16}" y1="{Z(zf)-4}" x2="{X(lj)+150}" y2="{Z(SP)+52}" stroke="{MUT}"/>')
parti.append(t(X(lj) + 154, Z(SP) + 56, "punta del target: 0,1 mm fuori dal retro → contatto con la molla della basetta", 13))
parti.append(f'<line x1="{X(lj)+14}" y1="{Z(Z_PCB0-1.0)}" x2="{X(lj)+150}" y2="{Z(0)-26}" stroke="{MUT}"/>')
parti.append(t(X(lj) + 154, Z(0) - 22, "coda Ø0,9 attraversa la scheda e sporge 1,0 sopra: si salda dal lato componenti", 13))

# dettaglio ingrandito
DX, DY, D = 10, Z(SP) + 150, 40
parti.append(t(DX, DY - 30, "Dettaglio 40:1 – target nel foro", 16, weight=600))
zd = lambda z: DY + (z - (Z_PCB0 - 1.2)) * D
xd = lambda x: DX + 120 + x * D
parti.append(r(xd(-3), zd(Z_PCB0), 6 * D, 1.0 * D, BOARD))
for dia, col, lab in [(1.1, "#0d3d27", "foro 1,1 consigliato"), (1.0, "#0a2e1d", "")]:
    pass
parti.append(r(xd(-0.55), zd(Z_PCB0), 1.1 * D, 1.0 * D, "#0a2e1d"))
parti.append(r(xd(-0.8), zd(Z_PCB0) - 2, 1.6 * D, 2, "#d9b44a"))
parti.append(r(xd(-0.8), zd(Z_PCB1), 1.6 * D, 2, "#d9b44a"))
g = r(xd(-CODA_D / 2), zd(Z_PCB1 - CODA_L), CODA_D * D, CODA_L * D, GOLD, "#8a6a1c")
g += r(xd(-SPALLA_D / 2), zd(Z_PCB1), SPALLA_D * D, SPALLA_L * D, GOLD, "#8a6a1c")
g += r(xd(-CORPO_D / 2), zd(Z_PCB1 + SPALLA_L), CORPO_D * D, 1.2 * D, GOLD, "#8a6a1c")
parti.append(g)
parti.append(t(xd(3.4), zd(Z_PCB0) + 26, "scheda 1,0 mm", 13))
parti.append(t(xd(3.4), zd(Z_PCB1 - 1.3) + 4, "coda Ø0,9 · sporge 1,0", 13))
parti.append(t(xd(3.4), zd(Z_PCB1) + 16, "spalla Ø2,0 × 0,5 sotto la scheda", 13))
parti.append(t(xd(3.4), zd(Z_PCB1 + 1.2), "corpo Ø1,5 × 4,0 verso il retro", 13))
parti.append(t(xd(-3), zd(Z_PCB1 + 1.9) + 14, "Foro 1,0 mm: 0,1 di gioco sul nominale, quasi zero con la tolleranza ±0,08.", 13, fill="#b23b1e"))
parti.append(t(xd(-3), zd(Z_PCB1 + 1.9) + 32, "Consigliato 1,1 mm, piazzola 1,6 invariata.", 13, fill="#b23b1e", weight=600))

# ---------- vista 2: dal retro ----------
VX, VY = 560, Z(SP) + 150
parti.append(t(VX - 20, VY - 52, "Vista dal retro (scala 12:1)", 16, weight=600))
BX = lambda x: VX + (LARG - (x + OFF_X)) * S2   # specchiato: visto da dietro
BY = lambda y: VY + (y + OFF_L) * S2
parti.append(f'<rect x="{VX}" y="{VY}" width="{LARG*S2}" height="{L*S2}" rx="{1.5*S2}" fill="{RES}" stroke="{INK}" stroke-width="1.5"/>')
parti.append(f'<circle cx="{VX+LARG*S2/2}" cy="{VY-1.6*S2}" r="{1.7*S2}" fill="none" stroke="#9aa0a8" stroke-width="{0.6*S2}"/>')
parti.append(f'<rect x="{BX(16.5)}" y="{BY(0)}" width="{16.5*S2}" height="{38*S2}" rx="{S2}" fill="none" stroke="{BOARD}" stroke-dasharray="4 3"/>')
parti.append(f'<rect x="{BX(16.25)}" y="{BY(BAT_Y[0])}" width="{16*S2}" height="{20*S2}" fill="#c7b8e6" opacity=".8"/>')
parti.append(t(VX + LARG * S2 / 2, BY(22.8) + 4, "batteria", 12, "middle"))
parti.append(f'<circle cx="{BX(MOT_C[0])}" cy="{BY(MOT_C[1])}" r="{MOT_R*S2}" fill="#f2d38a" stroke="#b08a2e" opacity=".85"/>')
parti.append(t(BX(MOT_C[0]), BY(MOT_C[1]) + 4, "motorino", 12, "middle"))
nomi = ["5V", "GND", "SWDIO", "SWCLK"]
for x, n in zip(J_X, nomi):
    parti.append(f'<circle cx="{BX(x)}" cy="{BY(J_Y)}" r="{CORPO_D/2*S2}" fill="{GOLD}" stroke="#8a6a1c"/>')
    parti.append(t(BX(x), BY(J_Y) - 14, n, 10, "middle", MUT))
d = math.dist((J_X[1], J_Y), MOT_C) - MOT_R - SPALLA_D / 2
parti.append(t(VX + LARG * S2 + 14, BY(J_Y) + 4, "contatti Ø1,5", 12, fill=MUT))
parti.append(t(VX + LARG * S2 + 14, BY(MOT_C[1]) + 4, f"spalla–motorino: {d:.1f} mm liberi", 12, fill=MUT))
parti.append(t(VX + LARG * S2 + 14, BY(BAT_Y[0]) + 20, "batteria da y 12,8: lontana", 12, fill=MUT))

W = max(int(VX + LARG * S2 + 250), int(X(L) + 40))
H = int(BY(38) + 60)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Inter, sans-serif">'
       f'<defs><marker id="f" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="{MUT}"/></marker></defs>'
       f'<rect width="100%" height="100%" fill="#fff"/>' + "".join(parti) + "</svg>")
OUT.write_text(svg, encoding="utf-8")
print(OUT, W, H, f"spazio spalla-motorino {d:.2f} mm")
