"""Funzioni comuni ai post (caroselli 1080x1350 e reel 1080x1920), stesso stile dei post 1 e 2."""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, '..', '..')
F = 'C:/Windows/Fonts/'
INK = (239, 235, 227); MUTE = (170, 165, 156); BRONZE = (196, 150, 104); LED = (95, 211, 200); BG = (14, 14, 16)
B, SB, L, R_, GEO = 'segoeuib.ttf', 'seguisb.ttf', 'segoeuil.ttf', 'segoeui.ttf', 'GeorgiaPro-Regular.ttf'
def f(n, s): return ImageFont.truetype(F + n, s)


def a_capo(d, s, font, larg):
    righe, r = [], ''
    for p in s.split(' '):
        t = (r + ' ' + p).strip()
        if d.textlength(t, font=font) > larg and r: righe.append(r); r = p
        else: r = t
    return righe + [r]


# ---------- caroselli 4:5 ----------
W, H = 1080, 1350

def sfondo(nome, y0, w=W, h=H):
    im = Image.open(os.path.join(R, 'sfondi', 'png', nome)).convert('RGB')
    hh = int(im.width * h / w)
    return im.crop((0, y0, im.width, y0 + hh)).resize((w, h), Image.LANCZOS)

def velo(im, alto=0, basso=0):
    w, h = im.size; m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for y in range(h):
        a = 0
        if alto and y < alto: a = int(235 * (1 - y / alto) ** 1.3)
        if basso and y > h - basso: a = max(a, int(235 * ((y - (h - basso)) / basso) ** 1.3))
        d.line((0, y, w, y), fill=a)
    return Image.composite(Image.new('RGB', (w, h), BG), im, m)

def testo(d, xy, s, font, fill=INK, larg=W - 160, inter=1.18):
    x, y = xy
    for riga in a_capo(d, s, font, larg):
        d.text((x, y), riga, font=font, fill=fill); y += font.size * inter
    return y

def marchio(d, y=H - 78, x=80):
    fn = f(B, 34); fa = f(B, 19)
    d.text((x, y), 'not', font=fn, fill=INK); x2 = x + d.textlength('not', font=fn) + 2
    d.text((x2, y + 3), 'a', font=fa, fill=BRONZE); wa = d.textlength('a', font=fa)
    d.line((x2, y + 26, x2 + wa, y + 26), fill=BRONZE, width=2)
    d.text((x2 + wa + 3, y), 'pad', font=fn, fill=INK)

def numero(d, i, n):
    s = f'{i}/{n}'; fn = f(R_, 26); d.text((W - 80 - d.textlength(s, font=fn), H - 72), s, font=fn, fill=MUTE)

def etichetta(d, xy, s, col=LED):
    d.text(xy, s.upper(), font=f(SB, 24), fill=col)

def salva_carosello(slides, out):
    os.makedirs(out, exist_ok=True)
    for i, s in enumerate(slides, 1): s.save(os.path.join(out, f'slide_{i}.jpg'), quality=93)
    t = 360; n = len(slides); g = Image.new('RGB', (n * t + (n + 1) * 16, int(t * H / W) + 32), (240, 238, 233))
    for i, s in enumerate(slides): g.paste(s.resize((t, int(t * H / W)), Image.LANCZOS), (16 + i * (t + 16), 16))
    g.save(os.path.join(out, 'anteprima.jpg'), quality=90)


# ---------- reel 9:16 ----------
VW, VH, FPS = 1080, 1920, 30

def carica916(nome, y0, y1):
    im = Image.open(os.path.join(R, 'sfondi', 'png', nome)).convert('RGB')
    im = im.crop((0, y0, im.width, y1))
    s = max(VW / im.width, VH / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - VW) // 2; y = (im.height - VH) // 2
    return im.crop((x, y, x + VW, y + VH))

def kenburns(base, t, z0=1.0, z1=1.08):
    z = z0 + (z1 - z0) * t; w, h = int(VW / z), int(VH / z)
    x, y = (VW - w) // 2, (VH - h) // 2
    return base.crop((x, y, x + w, y + h)).resize((VW, VH), Image.BILINEAR)

def scritta(img, s, alpha, y=360, font=None, col=INK, sotto=None):
    if alpha <= 0: return img
    lay = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    font = font or f(SB, 76); a = int(255 * min(1, alpha))
    for riga in a_capo(d, s, font, VW - 160):
        d.text(((VW - d.textlength(riga, font=font)) / 2, y), riga, font=font, fill=col + (a,)); y += font.size * 1.18
    if sotto:
        fs = f(R_, 40)
        for riga in a_capo(d, sotto, fs, VW - 200):
            d.text(((VW - d.textlength(riga, font=fs)) / 2, y + 18), riga, font=fs, fill=MUTE + (a,)); y += fs.size * 1.3
    out = img.convert('RGBA'); out.alpha_composite(lay); return out.convert('RGB')

def velo_alto(img, h=900, forza=210):
    m = Image.new('L', (VW, VH), 0); d = ImageDraw.Draw(m)
    for yy in range(h): d.line((0, yy, VW, yy), fill=int(forza * (1 - yy / h) ** 1.2))
    return Image.composite(Image.new('RGB', (VW, VH), BG), img, m)

def finale(img, t, titolo, sotto):
    """Chiusura comune: monogramma NªP, @notapadlabs, ko-fi."""
    img = scritta(img, titolo, min(1, t * 4), y=480, sotto=sotto)
    lay = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, max(0, (t - .15) * 4)))
    g, ga = f(GEO, 150), f(GEO, 70)
    wN, wa, wP = d.textlength('N', font=g), d.textlength('a', font=ga), d.textlength('P', font=g)
    x = (VW - (wN + wa + wP + 24)) / 2; y = 860
    d.text((x, y), 'N', font=g, fill=INK + (a,)); d.text((x + wN + 12, y + 8), 'a', font=ga, fill=BRONZE + (a,))
    d.rectangle((x + wN + 12, y + 92, x + wN + 12 + wa, y + 98), fill=BRONZE + (a,))
    d.text((x + wN + wa + 24, y), 'P', font=g, fill=INK + (a,))
    h = '@notapadlabs'; fh = f(SB, 54); d.text(((VW - d.textlength(h, font=fh)) / 2, 1070), h, font=fh, fill=LED + (a,))
    k = 'ko-fi.com/notapad'; fk = f(R_, 40); d.text(((VW - d.textlength(k, font=fk)) / 2, 1160), k, font=fk, fill=MUTE + (a,))
    out = img.convert('RGBA'); out.alpha_composite(lay); return out.convert('RGB')

def monta_reel(scene, out, copertina=(1, .6), xf=0.35):
    """scene: [(durata s, funzione(t01) -> immagine)]; scrive reel.mp4 e copertina.jpg in out."""
    os.makedirs(out, exist_ok=True)
    tot = sum(d for d, _ in scene)
    cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
           '-i', os.path.join(R, 'video', 'build', 'musica.wav'),
           '-filter_complex', f'[1:a]atrim=0:{tot},afade=t=in:d=0.6,afade=t=out:st={tot-1.2}:d=1.2,volume=0.8[a]',
           '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'medium',
           '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', os.path.join(out, 'reel.mp4')]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    prev = None
    for i, (dur, fn) in enumerate(scene):
        n = int(dur * FPS)
        for k in range(n):
            fr = fn(k / max(1, n - 1))
            if prev is not None and k < int(xf * FPS): fr = Image.blend(prev, fr, k / (xf * FPS))
            if (i, k) == (copertina[0], int(n * copertina[1])): fr.save(os.path.join(out, 'copertina.jpg'), quality=92)
            p.stdin.write(fr.tobytes())
        prev = fr
    p.stdin.close(); p.wait()
    return round(tot, 1)
