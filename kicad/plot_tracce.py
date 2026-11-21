"""(python di sistema) tracce.json -> sbroglio.png: un pannello per strato di rame"""
import json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notapad_def as _D
d = json.load(open(os.path.join(HERE, "tracce.json")))
strati = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"] if _D.STRATI == 4 else ["F.Cu", "B.Cu"]
col = {"F.Cu": "#ff5040", "In1.Cu": "#40c070", "In2.Cu": "#e0c020", "B.Cu": "#3c8dff"}
fig, axs = plt.subplots(1, len(strati), figsize=(4.2 * len(strati), 10))
for ax, L in zip(axs, strati):
    ax.add_patch(FancyBboxPatch((0, 0), _D.W, _D.H, boxstyle="round,pad=0,rounding_size=1", fc="#10301f", ec="k"))
    for poly in d.get("z", {}).get(L, []):
        ax.add_patch(Polygon(poly, closed=True, fc=col[L], ec="none", alpha=0.35))
    for x, y, w, h, isb in d["p"]:
        ax.add_patch(Rectangle((x, y), w, h, fc="#c8a050", alpha=0.5, ec="none"))
    for x1, y1, x2, y2, w, lay in d["t"]:
        if lay == L:
            ax.plot([x1, x2], [y1, y2], color=col[L], lw=w * 9, solid_capstyle="round")
    for x, y, dia in d["v"]:
        ax.add_patch(Circle((x, y), dia / 2, fc="#ddd", ec="k", lw=0.2))
    ax.set_xlim(-0.5, _D.W + 0.5); ax.set_ylim(_D.H + 0.5, -0.5); ax.set_aspect("equal"); ax.set_title(L)
fig.suptitle(f"notªpad v0.1 · {_D.STRATI} strati · {_D.W:g} x {_D.H:g} mm · {len(d['v'])} via")
plt.savefig(os.path.join(HERE, "sbroglio.png"), dpi=150, bbox_inches="tight")
