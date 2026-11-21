"""Contorno e zone in DXF (mm, origine in basso a sinistra) + anteprima PNG, da notapad_def.py.  Python di sistema."""
import os, sys
import ezdxf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import notapad_def as D
W, H, r = D.W, D.H, D.CORNER_R
ZA, ZB = 7.0, H - 18.0                 # confini zone A/B e B/C (dall'alto)
OUT = os.path.join(HERE, "..", "jlc", "notapad_v0.1_contorno")
Y = lambda top: H - top                # coordinate dall'alto -> DXF

doc = ezdxf.new("R2010", setup=True)
for name, col in [("OUTLINE", 7), ("ZONE", 8), ("KEEPOUT", 1), ("GUIDA", 3)]:
    doc.layers.add(name, color=col)
msp = doc.modelspace()
pts = [(r, 0, 0), (W - r, 0, 0.4142), (W, r, 0), (W, H - r, 0.4142), (W - r, H, 0), (r, H, 0.4142), (0, H - r, 0), (0, r, 0.4142)]
msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "OUTLINE"})
for t in (ZA, ZB):
    msp.add_line((0, Y(t)), (W, Y(t)), dxfattribs={"layer": "ZONE"})
msp.add_lwpolyline([(0, 0), (W, 0), (W, 5.2), (0, 5.2)], close=True, dxfattribs={"layer": "KEEPOUT"})
msp.add_text("KEEPOUT ANTENNA", height=0.6, dxfattribs={"layer": "KEEPOUT"}).set_placement((0.5, 2.2))
for ref in ("J1", "J2", "J3", "J4"):
    x, y, _ = D.C[ref][2]
    msp.add_circle((x, Y(y)), 0.8, dxfattribs={"layer": "GUIDA"})
    msp.add_text({"J1": "5V", "J2": "GND", "J3": "SWDIO", "J4": "SWCLK"}[ref], height=0.5,
                 dxfattribs={"layer": "GUIDA"}).set_placement((x - 0.8, Y(y + 1.5)))
boxes = {"MK2 superiore": ("MK2", 4.0, 2.0), "MK1 frontale": ("MK1", 2.0, 4.0)}
for label, (ref, w, h) in boxes.items():
    x, y, _ = D.C[ref][2]
    msp.add_lwpolyline([(x - w / 2, Y(y - h / 2)), (x + w / 2, Y(y - h / 2)), (x + w / 2, Y(y + h / 2)), (x - w / 2, Y(y + h / 2))],
                       close=True, dxfattribs={"layer": "GUIDA"})
    msp.add_text(label, height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((x - w / 2, Y(y + h / 2 + 0.8)))
for ref in ("D1", "D2", "D3"):
    x, y, _ = D.C[ref][2]
    msp.add_lwpolyline([(x - .5, Y(y - .5)), (x + .5, Y(y - .5)), (x + .5, Y(y + .5)), (x - .5, Y(y + .5))], close=True,
                       dxfattribs={"layer": "GUIDA"})
msp.add_text("3 LED sotto la fessura", height=0.5, dxfattribs={"layer": "GUIDA"}).set_placement((4.5, Y(D.C["D1"][2][1] + 1.5)))
msp.add_lwpolyline([(1.75, Y(H - 18)), (14.75, Y(H - 18)), (14.75, 0), (1.75, 0)], close=True, dxfattribs={"layer": "GUIDA"})
msp.add_text("E73 18x13", height=0.7, dxfattribs={"layer": "GUIDA"}).set_placement((5.5, Y(H - 11)))
doc.saveas(OUT + ".dxf")

fig, ax = plt.subplots(figsize=(4, 8.5))
ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle="round,pad=0,rounding_size=1", fc="#1f5f3a", ec="k"))
ax.add_patch(Rectangle((0, 0), W, 5.2, fc="none", ec="r", hatch="//", lw=0.6))
for t in (ZA, ZB):
    ax.axhline(Y(t), color="w", ls=":", lw=0.8)
for lab, yy in (("A", (H + Y(ZA)) / 2), ("B", (Y(ZA) + Y(ZB)) / 2), ("C", Y(ZB) / 2)):
    ax.text(-0.9, yy, lab, fontsize=10, weight="bold")
for ref in ("J1", "J2", "J3", "J4"):
    x, y, _ = D.C[ref][2]; ax.add_patch(Circle((x, Y(y)), 0.8, fc="#e8c060"))
for ref, w, h in (("MK2", 4, 2), ("MK1", 2, 4), ("D1", 1, 1), ("D2", 1, 1), ("D3", 1, 1), ("U2", 8, 6)):
    x, y, _ = D.C[ref][2]; ax.add_patch(Rectangle((x - w / 2, Y(y + h / 2)), w, h, fc="none", ec="#ffd34d"))
    ax.text(x, Y(y), ref, fontsize=6, color="w", ha="center", va="center")
ax.add_patch(Rectangle((1.75, 0), 13, 18, fc="none", ec="#9fd0ff")); ax.text(8.25, 9, "E73", color="w", ha="center")
ax.set_xlim(-1.2, W + 0.5); ax.set_ylim(-0.5, H + 0.5); ax.set_aspect("equal")
ax.set_title(f"notªpad v0.1 · {W:g} × {H:g} mm", fontsize=9)
plt.savefig(OUT + "_anteprima.png", dpi=180, bbox_inches="tight")
print("scritti", os.path.basename(OUT) + ".dxf e _anteprima.png")
