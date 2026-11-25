"""Monogramma rotondo NªP per i social: varianti di carattere e colore."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
F = 'C:/Windows/Fonts/'
BG = (14, 14, 16); INK = (239, 235, 227); BRONZE = (184, 137, 90); LED = (95, 211, 200); IVORY = (232, 226, 214)
S = 4; N = 1080 * S

def mono(font, bg, ink, acc, peso_a=0.46, nome=None, alone=True):
    im = Image.new('RGB', (N, N), bg)
    if alone:
        g = Image.new('RGB', (N, N), bg)
        warm = tuple(min(255, c + 22) for c in bg) if sum(bg) < 200 else tuple(max(0, c - 14) for c in bg)
        ImageDraw.Draw(g).ellipse((N*.18, N*.18, N*.82, N*.82), fill=warm)
        im = g.filter(ImageFilter.GaussianBlur(N * .1))
    d = ImageDraw.Draw(im)
    size = int(N * 0.40)
    f = ImageFont.truetype(F + font, size); fa = ImageFont.truetype(F + font, int(size * peso_a))
    bN = d.textbbox((0, 0), 'N', font=f); bP = d.textbbox((0, 0), 'P', font=f); ba = d.textbbox((0, 0), 'a', font=fa)
    gap = size * 0.03
    wN, wP, wa = bN[2]-bN[0], bP[2]-bP[0], ba[2]-ba[0]
    tot = wN + gap + wa + gap + wP
    x = (N - tot) / 2
    cap_top, cap_bot = bN[1], bN[3]; capH = cap_bot - cap_top
    y = (N - capH) / 2 - cap_top
    d.text((x - bN[0], y), 'N', font=f, fill=ink)
    xa = x + wN + gap
    ya = y + cap_top - ba[1]          # a allineata in alto con le maiuscole
    d.text((xa - ba[0], ya), 'a', font=fa, fill=acc)
    ly = y + cap_top + (ba[3]-ba[1]) + size * 0.05
    d.rectangle((xa, ly, xa + wa, ly + size * 0.035), fill=acc)
    d.text((xa + wa + gap - bP[0], y), 'P', font=f, fill=ink)
    im = im.resize((1080, 1080), Image.LANCZOS)
    return im

def tondo(im):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse((0, 0, im.width-1, im.height-1), fill=255)
    p = Image.new('RGBA', im.size, (0, 0, 0, 0)); p.paste(im, (0, 0), m); return p

varianti = [
    ('A_segoe_bold', mono('segoeuib.ttf', BG, INK, BRONZE)),
    ('B_segoe_light', mono('segoeuil.ttf', BG, INK, BRONZE)),
    ('C_georgia', mono('GeorgiaPro-Regular.ttf', BG, INK, BRONZE)),
    ('D_bahnschrift', mono('bahnschrift.ttf', BG, INK, LED)),
    ('E_avorio', mono('segoeuisl.ttf', IVORY, (24, 24, 26), BRONZE)),
    ('F_bronzo', mono('segoeuisl.ttf', BG, BRONZE, LED)),
]
os.makedirs(os.path.join(D, 'monogramma'), exist_ok=True)
T = 360; cols = 3; righe = 2
grid = Image.new('RGB', (cols*T + (cols+1)*30, righe*(T+60) + 30), (245, 243, 238))
gd = ImageDraw.Draw(grid); fl = ImageFont.truetype(F + 'segoeui.ttf', 26)
for i, (n, im) in enumerate(varianti):
    im.save(os.path.join(D, 'monogramma', n + '.png'))
    c, r = i % cols, i // cols
    x = 30 + c*(T+30); y = 30 + r*(T+60)
    grid.paste(tondo(im.resize((T, T), Image.LANCZOS)), (x, y), tondo(im.resize((T, T), Image.LANCZOS)))
    gd.text((x, y + T + 8), n.replace('_', ' '), font=fl, fill=(60, 60, 60))
grid.save(os.path.join(D, 'monogramma', 'confronto.png'))
print('ok')
