"""Genera avatar e banner per i profili social di notapad (dai render)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, '..', 'render')
BG = (14, 14, 16); INK = (239, 235, 227); MUTE = (154, 150, 142); BRONZE = (184, 137, 90); LED = (95, 211, 200)
F = 'C:/Windows/Fonts/'
def font(n, s): return ImageFont.truetype(F + n, s)

# Finitura 2, nero opaco soft-touch (le venature radica sono scartate)
var = Image.open(os.path.join(R, 'monolite_varianti.jpg')).convert('RGB')
cella = var.crop((700, 0, 1400, 875))
def sfuma(img, bordo=90):
    m = Image.new('L', img.size, 0); d = ImageDraw.Draw(m)
    d.rectangle((bordo, bordo, img.width - bordo, img.height - bordo), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(bordo / 2))
    b = Image.new('RGB', img.size, BG); b.paste(img, (0, 0), m); return b

av = var.crop((700, 40, 1400, 740)).resize((1080, 1080), Image.LANCZOS)
av.save(os.path.join(D, 'avatar_1080.png'))

# Banner YouTube 2560x1440 (zona sicura centrale 1546x423)
bn = Image.new('RGB', (2560, 1440), BG)
dr = ImageDraw.Draw(bn)
mh = 700
m = sfuma(cella).resize((int(cella.width * mh / cella.height), mh), Image.LANCZOS)
x0 = 560
bn.paste(m, (x0, 720 - mh // 2 + 20))
tx = x0 + m.width - 20
f1 = font('segoeuib.ttf', 150); f2 = font('segoeui.ttf', 48)
dr.text((tx, 560), 'not', font=f1, fill=INK)
nx = tx + dr.textlength('not', font=f1)
fa = font('segoeuib.ttf', 80)
dr.text((nx + 4, 572), 'a', font=fa, fill=BRONZE)
dr.line((nx + 8, 668, nx + 8 + dr.textlength('a', font=fa), 668), fill=BRONZE, width=6)
dr.text((nx + 14 + dr.textlength('a', font=fa), 560), 'pad', font=f1, fill=INK)
dr.text((tx + 4, 760), 'Open-source wearable AI voice recorder', font=f2, fill=MUTE)
dr.ellipse((tx + 6, 842, tx + 26, 862), fill=LED)
dr.text((tx + 44, 826), 'Building in public', font=f2, fill=LED)
bn.save(os.path.join(D, 'banner_youtube_2560x1440.png'))
print('ok')
