"""Post 2 – Reel/Short/TikTok "What if your ideas never got lost again?" (1080x1920, 30 fps, ~21 s).
Fotogrammi generati con PIL dagli sfondi del progetto, montati con ffmpeg; musica: video/build/musica.wav (generata da noi).
Uscita: social/post/02_reel-ideas/reel.mp4 + copertina.jpg
"""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, '..', '..')
OUT = os.path.join(D, '02_reel-ideas'); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
F = 'C:/Windows/Fonts/'
INK = (239, 235, 227); MUTE = (170, 165, 156); BRONZE = (196, 150, 104); LED = (95, 211, 200); BG = (14, 14, 16)
def f(n, s): return ImageFont.truetype(F + n, s)
SB, R_, GEO = 'seguisb.ttf', 'segoeui.ttf', 'GeorgiaPro-Regular.ttf'

def carica(nome, y0, y1):
    im = Image.open(os.path.join(R, 'sfondi', 'png', nome)).convert('RGB')
    im = im.crop((0, y0, im.width, y1))
    # porta a 9:16 riempiendo in larghezza
    s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))

def kenburns(base, t, z0=1.0, z1=1.08):
    z = z0 + (z1 - z0) * t; w, h = int(W / z), int(H / z)
    x, y = (W - w) // 2, (H - h) // 2
    return base.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

def a_capo(d, s, font, larg):
    righe, r = [], ''
    for p in s.split(' '):
        t = (r + ' ' + p).strip()
        if d.textlength(t, font=font) > larg and r: righe.append(r); r = p
        else: r = t
    return righe + [r]

def scritta(img, righe, alpha, y=360, font=None, col=INK, sotto=None):
    """Testo centrato con fade (alpha 0..1); zona alta, lontano dai pulsanti dell'app."""
    if alpha <= 0: return img
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    font = font or f(SB, 76); a = int(255 * min(1, alpha))
    for riga in a_capo(d, righe, font, W - 160):
        d.text(((W - d.textlength(riga, font=font)) / 2, y), riga, font=font, fill=col + (a,)); y += font.size * 1.18
    if sotto:
        fs = f(R_, 40)
        for riga in a_capo(d, sotto, fs, W - 200):
            d.text(((W - d.textlength(riga, font=fs)) / 2, y + 18), riga, font=fs, fill=MUTE + (a,)); y += fs.size * 1.3
    out = img.convert('RGBA'); out.alpha_composite(lay); return out.convert('RGB')

def velo_alto(img, h=900, forza=210):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for yy in range(h): d.line((0, yy, W, yy), fill=int(forza * (1 - yy / h) ** 1.2))
    return Image.composite(Image.new('RGB', (W, H), BG), img, m)

# scene: (durata s, funzione(t01) -> immagine)
nero = Image.new('RGB', (W, H), BG)
midnight = velo_alto(carica('01_midnight_iphone.png', 120, 2150))
rec = velo_alto(carica('08_recording_iphone.png', 300, 2000))
mics = velo_alto(carica('05_two-microphones_iphone.png', 250, 2100))
esploso = velo_alto(carica('04_exploded-board_iphone.png', 0, 2150))
from PIL import ImageFilter
_g = Image.new('RGB', (W, H), BG); ImageDraw.Draw(_g).ellipse((140, 700, 940, 1500), fill=(44, 36, 30))
contatti = _g.filter(ImageFilter.GaussianBlur(160))

def fade(t, dur, a=0.25, b=0.25):
    s = t * dur; return min(1, s / a) if s < a else (min(1, (dur - s) / b) if s > dur - b else 1)

def sc_gancio(t):
    img = nero.copy()
    img = scritta(img, 'What if your ideas never got lost again?', min(1, t * 3), y=720, font=f(SB, 92))
    return img

def sc_meet(t):
    img = kenburns(midnight, t)
    return scritta(img, 'Meet notªpad.', min(1, t * 4), y=300, sotto='A tiny resin monolith you wear all day.')

def sc_rec(t):
    img = kenburns(rec, t, 1.08, 1.0)
    return scritta(img, 'It records your day.', min(1, t * 4), y=300, sotto='Squeeze both sides to mark what matters.')

def sc_mics(t):
    img = kenburns(mics, t)
    return scritta(img, 'Two microphones.', min(1, t * 4), y=300, sotto='One wakes up only when someone speaks.')

def sc_ai(t):
    img = kenburns(esploso, t, 1.0, 1.06)
    return scritta(img, 'Your AI, not ours.', min(1, t * 4), y=300, col=INK, sotto='Open MCP server. No subscription, no locked-in cloud.')

def sc_fine(t):
    img = kenburns(contatti, t, 1.04, 1.0)
    img = scritta(img, 'Open source. Built in public.', min(1, t * 4), y=480, sotto='Follow the build:')
    # monogramma e handle
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, max(0, (t - .15) * 4)))
    g, ga = f(GEO, 150), f(GEO, 70)
    wN, wa, wP = d.textlength('N', font=g), d.textlength('a', font=ga), d.textlength('P', font=g)
    x = (W - (wN + wa + wP + 24)) / 2; y = 860
    d.text((x, y), 'N', font=g, fill=INK + (a,)); d.text((x + wN + 12, y + 8), 'a', font=ga, fill=BRONZE + (a,))
    d.rectangle((x + wN + 12, y + 92, x + wN + 12 + wa, y + 98), fill=BRONZE + (a,))
    d.text((x + wN + wa + 24, y), 'P', font=g, fill=INK + (a,))
    h = '@notapadlabs'; fh = f(SB, 54); d.text(((W - d.textlength(h, font=fh)) / 2, 1070), h, font=fh, fill=LED + (a,))
    k = 'ko-fi.com/notapad'; fk = f(R_, 40); d.text(((W - d.textlength(k, font=fk)) / 2, 1160), k, font=fk, fill=MUTE + (a,))
    out = img.convert('RGBA'); out.alpha_composite(lay); return out.convert('RGB')

SCENE = [(2.8, sc_gancio), (3.4, sc_meet), (3.4, sc_rec), (3.4, sc_mics), (3.6, sc_ai), (4.4, sc_fine)]
XF = 0.35  # dissolvenza tra scene

tot = sum(d for d, _ in SCENE)
cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
       '-i', os.path.join(R, 'video', 'build', 'musica.wav'),
       '-filter_complex', f'[1:a]atrim=0:{tot},afade=t=in:d=0.6,afade=t=out:st={tot-1.2}:d=1.2,volume=0.8[a]',
       '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'medium',
       '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', os.path.join(OUT, 'reel.mp4')]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
prev_last = None
for i, (dur, fn) in enumerate(SCENE):
    n = int(dur * FPS)
    for k in range(n):
        fr = fn(k / max(1, n - 1))
        if prev_last is not None and k < int(XF * FPS):
            fr = Image.blend(prev_last, fr, k / (XF * FPS))
        if i == 1 and k == int(n * .6): fr.save(os.path.join(OUT, 'copertina.jpg'), quality=92)
        p.stdin.write(fr.tobytes())
    prev_last = fr
p.stdin.close(); p.wait()
print('ok', round(tot, 1), 's')
