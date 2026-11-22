#!/usr/bin/env python3
"""Trasforma sfondi/sorgenti/*.svg in sfondi/png/ (iPhone 1179x2556, Android 1080x2400) con Edge headless."""
import glob, os, subprocess, sys, time
from PIL import Image

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = os.path.dirname(os.path.abspath(__file__))
SIZES = {"iphone": (1179, 2556), "android": (1080, 2400)}
os.makedirs(os.path.join(BASE, "png"), exist_ok=True)
for svg in sorted(glob.glob(os.path.join(BASE, "sorgenti", "*.svg"))):
    name = os.path.splitext(os.path.basename(svg))[0]
    for dev, (w, h) in SIZES.items():
        out = os.path.join(BASE, "png", f"{name}_{dev}.png")
        # finestra piu' alta di 200 px: poi si ritaglia (la UI headless puo' sottrarre altezza)
        if os.path.exists(out): os.remove(out)
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h}", f"--screenshot={out}", "file:///" + svg.replace("\\", "/")],
                       check=True, capture_output=True, timeout=120)
        t0 = time.time(); last = -1
        while time.time() - t0 < 90:
            if os.path.exists(out):
                sz = os.path.getsize(out)
                if sz > 0 and sz == last: break
                last = sz
            time.sleep(1)
        im = Image.open(out)
        if im.size != (w, h):
            im = im.crop((0, 0, w, h))
        im.save(out, optimize=True)
        print(name, dev, Image.open(out).size)
