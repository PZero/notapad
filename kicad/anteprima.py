"""Disegna anteprima.json (lato superiore + piazzole del retro) in anteprima.png. Python di sistema."""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "anteprima.json")))
sys.path.insert(0, HERE)
import notapad_def as _D
HH = _D.H
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "anteprima.png")
fig, ax = plt.subplots(figsize=(7, 14))
H = max(c["y"] + c["h"] for c in data) if False else HH
ax.add_patch(FancyBboxPatch((0, 0), 16.5, H, boxstyle="round,pad=0,rounding_size=1", fc="#1f5f3a", ec="k"))
for y in (7, H - 18):
    ax.axhline(y, color="w", ls=":", lw=0.8)
ax.add_patch(Rectangle((0, H - 5.2), 16.5, 5.2, fc="none", ec="r", hatch="//", lw=0.5))
area = 0
for c in data:
    back = all(p[5] for p in c["pads"]) and c["pads"]
    if not back:
        ax.add_patch(Rectangle((c["x"], c["y"]), c["w"], c["h"], fc="none", ec="#ffd34d", lw=0.6))
        if c["y"] + c["h"] < H - 17.5:
            area += c["w"] * c["h"]
    for x, y, w, h, net, isb in c["pads"]:
        ax.add_patch(Rectangle((x, y), w, h, fc=("#4aa3ff" if isb else "#e0a040"), ec="none", alpha=0.85))
        if w * h > 0.3:
            ax.text(x + w / 2, y + h / 2, net[:7], fontsize=3, ha="center", va="center", color="k")
    ax.text(c["x"] + c["w"] / 2, c["y"] + c["h"] / 2, c["ref"], fontsize=5.5, ha="center", va="center",
            color="w", weight="bold")
ax.set_xlim(-0.5, 17); ax.set_ylim(H + 0.5, -0.5); ax.set_aspect("equal")
ax.set_title(f"courtyard sopra la linea y=zona C: {area:.0f} mm² su {16.5*(H-18):.0f}")
plt.savefig(out, dpi=200, bbox_inches="tight")
print("area A+B", round(area, 1))

# controllo sovrapposizioni: courtyard e pad come rettangoli separati, solo lato superiore
def rects(c):
    r=[(c["x"],c["y"],c["x"]+c["w"],c["y"]+c["h"])]
    r+=[(x,y,x+w,y+h) for x,y,w,h,_,isb in c["pads"] if not isb]
    return r
top=[c for c in data if not (c["pads"] and all(p[5] for p in c["pads"]))]
bad=[]
for i,a_ in enumerate(top):
    for R in rects(a_)[1:]:
        if R[0]<0.3 or R[1]<0.3 or R[2]>16.2 or R[3]>34.7: bad.append((a_["ref"],"rame-bordo",[round(v,2) for v in R]))
    for b in top[i+1:]:
        m=0
        for A in rects(a_):
            for B in rects(b):
                ox=min(A[2],B[2])-max(A[0],B[0]); oy=min(A[3],B[3])-max(A[1],B[1])
                if ox>0.01 and oy>0.01: m=max(m,min(ox,oy))
        if m: bad.append((a_["ref"],b["ref"],round(m,2)))
print("sovrapposizioni:", bad or "nessuna")
