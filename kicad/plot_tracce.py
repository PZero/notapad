"""(python di sistema) tracce.json -> sbroglio.png"""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "tracce.json")))
fig, ax = plt.subplots(figsize=(7, 14))
ax.add_patch(FancyBboxPatch((0, 0), 16.5, 35, boxstyle="round,pad=0,rounding_size=1", fc="#10301f", ec="k"))
for x, y, w, h, isb in d["p"]:
    ax.add_patch(Rectangle((x, y), w, h, fc="#4aa3ff" if isb else "#e0a040", alpha=0.6, ec="none"))
for x1, y1, x2, y2, w, isb in sorted(d["t"], key=lambda t: not t[5]):
    ax.plot([x1, x2], [y1, y2], color="#3c8dff" if isb else "#ff5040", lw=w * 14, solid_capstyle="round", alpha=0.85)
for x, y, dia in d["v"]:
    ax.add_patch(Circle((x, y), dia / 2, fc="#ddd", ec="k", lw=0.3))
ax.set_xlim(-0.5, 17); ax.set_ylim(35.5, -0.5); ax.set_aspect("equal")
ax.set_title(f'rosso = sopra, blu = sotto · {len(d["v"])} via')
plt.savefig(os.path.join(HERE, "sbroglio.png"), dpi=200, bbox_inches="tight")
