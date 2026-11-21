"""notªpad v0.1 - genera distinta JLC, tabella collegamenti e contorno scheda."""
import csv
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

OUT = "/home/claude/jlc/"

# ---------------- Distinta componenti (formato BOM JLCPCB) ----------------
bom = [
    # Comment, Designator, Footprint, LCSC, Note
    ("E73-2G4M08S1C nRF52840", "U1", "SMD 18x13mm (libreria LCSC)", "C356849", "Extended; antenna a filo del bordo"),
    ("W25N02KVZEIR 2Gbit NAND", "U2", "WSON-8 8x6mm", "C3010298", "Extended; stessa impronta della W25N01GV C88868"),
    ("Microfono PDM LMD3526B261-OA1", "MK1,MK2", "SMD 3.5x2.7mm", "C5373238", "Extended; VERIFICARE top-port"),
    ("TP4054", "U3", "SOT-23-5", "C5381776", "Extended; 1=CHRG 2=GND 3=BAT 4=VCC 5=PROG"),
    ("XC6206P332MR-G 3.3V", "U4", "SOT-23", "C5446", "Basic; 1=GND 2=OUT 3=IN"),
    ("TTP223-BA6-TD", "U5,U6", "SOT-23-6", "C42422127", "Extended; 1=Q 2=VSS 3=I 4=AHLB 5=VDD 6=TOG"),
    ("MHPA1010RGBDT RGB anodo comune", "D1,D2,D3", "SMD 1x1mm", "C404280", "Extended"),
    ("AO3401A", "Q1", "SOT-23", "C15127", "Basic"),
    ("2N7002", "Q2,Q3", "SOT-23", "C8545", "Basic"),
    ("AO3400A", "Q4", "SOT-23", "C20917", "Basic"),
    ("1N4148WS", "D4,D5,D6", "SOD-323", "", "Basic; scegliere nel BOM tool"),
    ("20k 1%", "R1", "0402", "", "PROG: 50 mA di carica"),
    ("1M 1%", "R2,R4,R8,R9", "0402", "", ""),
    ("100k 1%", "R3,R5,R6,R7,R10", "0402", "", ""),
    ("1k 1%", "R11,R14,R17", "0402", "", "LED rosso"),
    ("470R 1%", "R12,R13,R15,R16,R18,R19", "0402", "", "LED verde e blu"),
    ("1uF 10V X5R", "C1,C2,C3,C4", "0402", "", ""),
    ("4.7uF 10V X5R", "C5", "0603", "", "VDD modulo"),
    ("100nF 16V X7R", "C6,C7,C8,C9,C10,C11", "0402", "", ""),
    ("10pF C0G", "C12,C13", "0402", "", "sensibilita tocco, da tarare (0-50 pF)"),
]
with open(OUT + "notapad_v0.1_BOM_JLC.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Note"])
    w.writerows(bom)

# Montati a mano (non vanno nella BOM JLC)
hand = [
    ("J1..J4", "Pin dorati passanti 5V/GND/SWDIO/SWCLK", "a mano o THT JLC se a catalogo"),
    ("BT1", "LiPo ~3.5x16x19 mm ~60 mAh con PCM", "a mano, piazzole BT+ BT- sul retro"),
    ("M1", "Motorino a moneta 0820 (8x2 mm)", "nello strato batteria sotto la zona A, fili a piazzole M+ M- sul retro"),
    ("TP_A, TP_B", "Fili verso i listelli tattili", "a mano"),
]
with open(OUT + "notapad_v0.1_montaggio_a_mano.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Rif.", "Componente", "Come"])
    w.writerows(hand)

# ---------------- Tabella dei collegamenti (netlist) ----------------
nets = {
    "VBUS": ["J1", "U3.4 VCC", "C1.1", "D5.A", "R6.1", "C10.1"],
    "GND": ["J2", "U3.2", "C1.2", "C2.2", "R1.2", "Q2.S", "R4.2", "R5.2", "Q3.S", "R7.2",
            "U4.1", "C3.2", "C4.2", "U1.GND (tutti)", "C5.2", "C6.2", "U2.4", "U2.EP",
            "C7.2", "MK1.GND", "MK1.SELECT", "MK2.GND", "C8.2", "C9.2",
            "U5.2", "U5.4", "U5.6", "U6.2", "U6.4", "U6.6", "C12.2", "C13.2",
            "Q4.S", "R10.2", "R9.2", "C11.2", "BT1.-"],
    "VBAT": ["BT1.+", "U3.3 BAT", "C2.1", "Q1.S", "R2.1"],
    "LATCH_G": ["Q1.G", "R2.2", "Q2.D"],
    "VBUS_D": ["D5.K", "R3.1"],
    "LATCH_ON": ["R3.2", "D6.K", "Q2.G", "R4.1"],
    "HOLD": ["D6.A", "U1.P0.11"],
    "VSYS": ["Q1.D", "U4.3 IN", "C3.1", "R8.1", "D1.A", "D2.A", "D3.A", "M1.+", "D4.K"],
    "PROG": ["U3.5", "R1.1"],
    "CHRG": ["U3.1", "U1.P0.07"],
    "RST_G": ["C10.2", "R5.1", "Q3.G"],
    "NRESET": ["Q3.D", "U1.P0.18"],
    "VBUS_SENSE": ["R6.2", "R7.1", "U1.P0.12"],
    "3V3": ["U4.2 OUT", "C4.1", "U1.VDD", "U1.VDDH (se presente)", "C5.1", "C6.1",
            "U2.8 VCC", "C7.1", "MK1.VDD", "MK2.VDD", "MK2.SELECT", "C8.1", "C9.1",
            "U5.5", "U6.5"],
    "VBAT_SENSE": ["R8.2", "R9.1", "C11.1", "U1.P0.02/AIN0"],
    "QSPI_CS": ["U2.1", "U1.P0.17"],
    "QSPI_IO1": ["U2.2", "U1.P0.21"],
    "QSPI_IO2": ["U2.3", "U1.P0.22"],
    "QSPI_IO0": ["U2.5", "U1.P0.20"],
    "QSPI_SCK": ["U2.6", "U1.P0.19"],
    "QSPI_IO3": ["U2.7", "U1.P0.23"],
    "PDM_CLK": ["MK1.CLK", "MK2.CLK", "U1.P0.26"],
    "PDM_DATA": ["MK1.DATA", "MK2.DATA", "U1.P0.27"],
    "TOUCH_A_PAD": ["U5.3", "C12.1", "TP_A"],
    "TOUCH_B_PAD": ["U6.3", "C13.1", "TP_B"],
    "TOUCH_A": ["U5.1", "U1.P0.06"],
    "TOUCH_B": ["U6.1", "U1.P0.08"],
    "MOTOR_N": ["M1.-", "Q4.D", "D4.A"],
    "MOTOR_G": ["Q4.G", "R10.1", "U1.P0.16"],
    "SWDIO": ["J3", "U1.SWDIO"],
    "SWCLK": ["J4", "U1.SWDCLK"],
}
leds = [("D1", ["P0.13", "P0.14", "P0.15"], ["R11", "R12", "R13"]),
        ("D2", ["P0.24", "P0.25", "P1.00"], ["R14", "R15", "R16"]),
        ("D3", ["P1.01", "P1.02", "P1.04"], ["R17", "R18", "R19"])]
for d, pins, rs in leds:
    for col, p, r in zip("RGB", pins, rs):
        nets[f"{d}_{col}"] = [f"{d}.{col}", f"{r}.1"]
        nets[f"{d}_{col}_IO"] = [f"{r}.2", f"U1.{p}"]
with open(OUT + "notapad_v0.1_collegamenti.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Net", "Collegamenti"])
    for k, v in nets.items():
        w.writerow([k, " ; ".join(v)])

# controllo: ogni designatore della BOM compare nella netlist
used = " ".join(" ".join(v) for v in nets.values())
missing = []
for row in bom:
    for d in row[1].split(","):
        if d + "." not in used and d not in used:
            missing.append(d)
print("designatori senza collegamenti:", missing or "nessuno")

# ---------------- Contorno scheda + zone (DXF, mm, origine in basso a sinistra) ----------------
W, H = 16.5, 35.0   # y=35 e il bordo alto (lato anello)
def Y(top):  # coordinate dall'alto -> DXF
    return H - top

doc = ezdxf.new("R2010", setup=True)
for name, col in [("OUTLINE", 7), ("ZONE", 8), ("KEEPOUT", 1), ("GUIDA", 3)]:
    doc.layers.add(name, color=col)
msp = doc.modelspace()
r = 1.0
pts = [(r, 0, 0), (W - r, 0, 0.4142), (W, r, 0), (W, H - r, 0.4142), (W - r, H, 0),
       (r, H, 0.4142), (0, H - r, 0), (0, r, 0.4142)]
msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "OUTLINE"})
for t in (7, 17):
    msp.add_line((0, Y(t)), (W, Y(t)), dxfattribs={"layer": "ZONE"})
msp.add_lwpolyline([(0, 0), (W, 0), (W, 5), (0, 5)], close=True, dxfattribs={"layer": "KEEPOUT"})
msp.add_text("KEEPOUT ANTENNA (verificare su datasheet E73)", height=0.6,
             dxfattribs={"layer": "KEEPOUT"}).set_placement((0.5, 2.2))
pins_x = [1.8, 4.6, 11.9, 14.7]
for x, n in zip(pins_x, ["5V", "GND", "SWDIO", "SWCLK"]):
    msp.add_circle((x, Y(2.5)), 0.8, dxfattribs={"layer": "GUIDA"})
    msp.add_text(n, height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((x - 0.8, Y(4.0)))
msp.add_lwpolyline([(6.5, Y(0.7)), (10.0, Y(0.7)), (10.0, Y(3.35)), (6.5, Y(3.35))], close=True,
                   dxfattribs={"layer": "GUIDA"})
msp.add_text("MK2 superiore", height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((6.2, Y(4.4)))
for x in (5.25, 8.25, 11.25):
    msp.add_lwpolyline([(x - .5, Y(8)), (x + .5, Y(8)), (x + .5, Y(9)), (x - .5, Y(9))], close=True,
                       dxfattribs={"layer": "GUIDA"})
msp.add_text("3 LED sotto la fessura", height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((4.5, Y(10.0)))
msp.add_lwpolyline([(12.4, Y(12.0)), (15.9, Y(12.0)), (15.9, Y(14.7)), (12.4, Y(14.7))], close=True,
                   dxfattribs={"layer": "GUIDA"})
msp.add_text("MK1 frontale", height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((11.6, Y(15.6)))
msp.add_lwpolyline([(1.75, Y(17)), (14.75, Y(17)), (14.75, Y(35)), (1.75, Y(35))], close=True, dxfattribs={"layer": "GUIDA"})
msp.add_text("E73 18x13", height=0.7, dxfattribs={"layer": "GUIDA"}).set_placement((5.5, Y(24)))
msp.add_text("notªpad v0.1", height=0.9, dxfattribs={"layer": "GUIDA"}).set_placement((1.0, Y(16.3)))
doc.layers.add("STRATO_BATTERIA", color=5)
msp.add_circle((8.25, Y(7.0)), 4.0, dxfattribs={"layer": "STRATO_BATTERIA"})
msp.add_text("motorino (strato batteria)", height=0.5, dxfattribs={"layer": "STRATO_BATTERIA"}).set_placement((4.6, Y(6.2)))
msp.add_lwpolyline([(0.25, Y(11)), (16.25, Y(11)), (16.25, Y(30)), (0.25, Y(30))], close=True, dxfattribs={"layer": "STRATO_BATTERIA"})
msp.add_text("batteria 16x19 (strato batteria)", height=0.5, dxfattribs={"layer": "STRATO_BATTERIA"}).set_placement((1.0, Y(29.2)))
doc.saveas(OUT + "notapad_v0.1_contorno.dxf")

# ---------------- Anteprima PNG ----------------
fig, ax = plt.subplots(figsize=(4.4, 8.6), dpi=170)
ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle="round,pad=0,rounding_size=1", fc="#1f5d3a", ec="#0c2a1a", lw=2))
ax.add_patch(Rectangle((1.75, 0), 13, 18, fc="#c9ccd1", ec="#222", lw=1))
ax.add_patch(Rectangle((0, 0), W, 5, fc="none", ec="#e8251a", hatch="///", lw=1))
ax.text(W / 2, 2.5, "keepout antenna", ha="center", va="center", color="#b0201a", fontsize=7)
ax.text(8.25, 11, "E73 nRF52840\n18 × 13 mm", ha="center", va="center", fontsize=8)
for y in (Y(7), Y(17)):
    ax.axhline(y, color="#9fd3b4", lw=.7, ls="--")
for lbl, y in (("A", Y(3.5)), ("B", Y(12)), ("C", Y(26))):
    ax.text(-1.2, y, lbl, fontsize=11, weight="bold", va="center", ha="center", color="#333")
ax.add_patch(Circle((8.25, Y(7)), 4, fc="none", ec="#7fb2ff", ls="--", lw=1))
ax.add_patch(Rectangle((0.25, Y(30)), 16, 19, fc="none", ec="#7fb2ff", ls="--", lw=1))
ax.text(8.25, Y(29.0), "batteria ~60 mAh (sotto la scheda)", ha="center", fontsize=5.5, color="#1d4fb0")
for x, n in zip(pins_x, ["5V", "GND", "SWDIO", "SWCLK"]):
    ax.add_patch(Circle((x, Y(2.5)), 0.8, fc="#f2c14e", ec="#8a6500"))
    ax.text(x, Y(4.2), n, ha="center", fontsize=5, color="white")
ax.add_patch(Rectangle((6.5, Y(3.35)), 3.5, 2.65, fc="#444", ec="white", lw=.6))
ax.text(8.25, Y(2.0), "MK2", ha="center", va="center", fontsize=6, color="white")
ax.text(8.25, Y(5.6), "motorino sotto (tratteggio)", ha="center", fontsize=5, color="#cfe3ff")
for x in (5.25, 8.25, 11.25):
    ax.add_patch(Rectangle((x - .5, Y(9)), 1, 1, fc="#ffffff", ec="#89f"))
ax.text(8.25, Y(10.4), "3 LED RGB", ha="center", fontsize=6, color="white")
ax.add_patch(Rectangle((12.4, Y(14.7)), 3.5, 2.7, fc="#444", ec="white", lw=.6))
ax.text(14.15, Y(13.35), "MK1", ha="center", va="center", fontsize=6, color="white")
ax.add_patch(Rectangle((0.8, Y(16.6)), 11, 5.4, fc="none", ec="#ddd", lw=.6, ls=":"))
ax.text(6.3, Y(13.9), "NAND · TTP223 ×2 · LDO\nMOSFET · R e C", ha="center", va="center", fontsize=5.5, color="#ddd")
ax.text(W / 2, H + 1.2, "notªpad v0.1 · 16,5 × 35 mm · lato componenti", ha="center", fontsize=7)
ax.set_xlim(-2.2, W + 1); ax.set_ylim(-1, H + 2.2); ax.set_aspect("equal"); ax.axis("off")
fig.savefig(OUT + "notapad_v0.1_contorno_anteprima.png", bbox_inches="tight", facecolor="white")
print("ok")
