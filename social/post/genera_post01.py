"""Post 1 – carosello "Meet notapad" (Instagram 4:5, 1080x1350)."""
from PIL import Image, ImageDraw, ImageFont
import os
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, '..', '..')
OUT = os.path.join(D, '01_meet-notapad'); os.makedirs(OUT, exist_ok=True)
F = 'C:/Windows/Fonts/'
W, H = 1080, 1350
INK = (239, 235, 227); MUTE = (170, 165, 156); BRONZE = (196, 150, 104); LED = (95, 211, 200); BG = (14, 14, 16)
def f(n, s): return ImageFont.truetype(F + n, s)
B, SB, L, R_ = 'segoeuib.ttf', 'seguisb.ttf', 'segoeuil.ttf', 'segoeui.ttf'

def sfondo(nome, y0):
    im = Image.open(os.path.join(R, 'sfondi', 'png', nome)).convert('RGB')
    h = int(im.width * H / W)
    return im.crop((0, y0, im.width, y0 + h)).resize((W, H), Image.LANCZOS)

def velo(im, alto=0, basso=0):
    """Sfuma verso il nero in alto e/o in basso per far leggere il testo."""
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(H):
        a = 0
        if alto and y < alto: a = int(235 * (1 - y / alto) ** 1.3)
        if basso and y > H - basso: a = max(a, int(235 * ((y - (H - basso)) / basso) ** 1.3))
        d.line((0, y, W, y), fill=a)
    nero = Image.new('RGB', (W, H), BG); return Image.composite(nero, im, m)

def testo(d, xy, s, font, fill=INK, larg=W - 160, inter=1.18):
    x, y = xy; righe = []; r = ''
    for p in s.split(' '):
        t = (r + ' ' + p).strip()
        if d.textlength(t, font=font) > larg and r: righe.append(r); r = p
        else: r = t
    righe.append(r)
    for riga in righe:
        d.text((x, y), riga, font=font, fill=fill); y += font.size * inter
    return y

def marchio(d, y=H - 78, x=80):
    fn = f(B, 34); fa = f(B, 19)
    d.text((x, y), 'not', font=fn, fill=INK); x2 = x + d.textlength('not', font=fn) + 2
    d.text((x2, y + 3), 'a', font=fa, fill=BRONZE); wa = d.textlength('a', font=fa)
    d.line((x2, y + 26, x2 + wa, y + 26), fill=BRONZE, width=2)
    d.text((x2 + wa + 3, y), 'pad', font=fn, fill=INK)

def numero(d, i, n=5):
    s = f'{i}/{n}'; fn = f(R_, 26); d.text((W - 80 - d.textlength(s, font=fn), H - 72), s, font=fn, fill=MUTE)

def etichetta(d, xy, s, col=LED):
    fn = f(SB, 24); x, y = xy
    d.text((x, y), s.upper(), font=fn, fill=col)

slides = []

# 1 – copertina
im = velo(sfondo('01_midnight_iphone.png', 520), alto=430, basso=260); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Open-source · wearable · AI')
testo(d, (80, 132), 'A tiny resin monolith that remembers your day.', f(SB, 64))
marchio(d); numero(d, 1); slides.append(im)

# 2 – cosa fa
im = velo(sfondo('08_recording_iphone.png', 430), alto=560, basso=300); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'What it does')
y = 140
for tit, sub in [('Records your day.', 'Two microphones, ~20 hours on a tiny cell.'),
                 ('Squeeze to mark what matters.', 'Touch both sides at once: no accidental taps.'),
                 ('Syncs to your phone.', 'Bluetooth, no cloud in between.')]:
    y = testo(d, (80, y), tit, f(SB, 50)); y = testo(d, (80, y + 4), sub, f(R_, 32), MUTE) + 26
marchio(d); numero(d, 2); slides.append(im)

# 3 – la tua AI (slide di testo con schema)
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Your AI, not ours')
y = testo(d, (80, 132), 'You choose who transcribes and organises your notes.', f(SB, 58))
y = testo(d, (80, y + 20), 'notªpad exposes your recordings through an open MCP server. Plug in the assistant you already use, or one running on your own computer.', f(R_, 34), MUTE, inter=1.3)
# schema: monolite -> telefono -> MCP -> AI
cy = y + 230; xs = [170, 420, 670, 920]; etich = ['notªpad', 'your phone', 'MCP', 'any AI']
for i, x in enumerate(xs):
    col = LED if i == 2 else INK
    if i == 0: d.rounded_rectangle((x - 28, cy - 64, x + 28, cy + 64), 12, outline=INK, width=4); d.line((x - 14, cy - 36, x + 14, cy - 36), fill=LED, width=6)
    elif i == 1: d.rounded_rectangle((x - 36, cy - 66, x + 36, cy + 66), 14, outline=INK, width=4)
    elif i == 2: d.ellipse((x - 62, cy - 62, x + 62, cy + 62), outline=LED, width=4); fn = f(B, 34); d.text((x - d.textlength('MCP', font=fn) / 2, cy - 22), 'MCP', font=fn, fill=LED)
    else: d.ellipse((x - 62, cy - 62, x + 62, cy + 62), outline=BRONZE, width=4); fn = f(B, 40); d.text((x - d.textlength('AI', font=fn) / 2, cy - 26), 'AI', font=fn, fill=BRONZE)
    fn = f(R_, 28); d.text((x - d.textlength(etich[i], font=fn) / 2, cy + 90), etich[i], font=fn, fill=MUTE)
    if i < 3: d.line((x + 80, cy, xs[i + 1] - 80, cy), fill=MUTE, width=3); d.polygon([(xs[i+1]-80, cy), (xs[i+1]-94, cy-8), (xs[i+1]-94, cy+8)], fill=MUTE)
testo(d, (80, cy + 230), 'No subscription. No locked-in cloud.', f(SB, 40), INK)
marchio(d); numero(d, 3); slides.append(im)

# 4 – aperto
im = velo(sfondo('04_exploded-board_iphone.png', 140), alto=520, basso=260); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Open, all the way')
y = testo(d, (80, 132), 'Every file is public.', f(SB, 64))
testo(d, (80, y + 6), 'Hardware CERN-OHL-S-2.0 · software MIT · 4-layer KiCad board, firmware and app on GitHub.', f(R_, 32), MUTE, inter=1.3)
marchio(d); numero(d, 4); slides.append(im)

# 5 – chiusura
im = velo(sfondo('03_gold-contacts_iphone.png', 560), alto=520, basso=560); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Building in public', BRONZE)
y = testo(d, (80, 132), 'Two makers. One first prototype on the way.', f(SB, 62))
y = H - 370
y = testo(d, (80, y), 'Follow @notapadlabs for every step:', f(SB, 38))
y = testo(d, (80, y + 6), 'board, firmware, resin, first recording.', f(R_, 34), MUTE)
d.text((80, y + 22), 'Support the build: ko-fi.com/notapad', font=f(SB, 32), fill=BRONZE)
marchio(d); numero(d, 5); slides.append(im)

for i, s in enumerate(slides, 1):
    s.save(os.path.join(OUT, f'slide_{i}.jpg'), quality=93)
# foglio di anteprima
t = 360; g = Image.new('RGB', (5 * t + 6 * 16, int(t * H / W) + 32), (240, 238, 233))
for i, s in enumerate(slides):
    g.paste(s.resize((t, int(t * H / W)), Image.LANCZOS), (16 + i * (t + 16), 16))
g.save(os.path.join(OUT, 'anteprima.jpg'), quality=90)
print('ok')
