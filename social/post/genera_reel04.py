"""Post 4 – Reel "Pick the finish": le 6 finiture con il numero grande, voto nei commenti (~17 s)."""
from comune import *
OUT = os.path.join(D, '04_reel-pick-the-finish')
var = Image.open(os.path.join(R, 'render', 'monolite_varianti.jpg')).convert('RGB')
NOMI = ['Forged carbon', 'Soft-touch matte black', 'Gloss black', 'Metallic anthracite', 'Midnight blue', 'Ivory']

def cella(i):
    c, r = i % 3, i // 3; y0 = 0 if r == 0 else 940
    im = var.crop((c * 700, y0, c * 700 + 700, y0 + 865))
    im = im.resize((VW, int(865 * VW / 700)), Image.LANCZOS)
    base = Image.new('RGB', (VW, VH), BG); base.paste(im, (0, VH - im.height))
    return velo_alto(base, h=900, forza=255)
CELLE = [cella(i) for i in range(6)]
nero = Image.new('RGB', (VW, VH), BG)

def sc_gancio(t):
    img = scritta(nero.copy(), 'Six finishes. One notªpad.', min(1, t * 3), y=640, font=f(SB, 92))
    return scritta(img, 'Which one would you wear?', max(0, min(1, (t - .35) * 3)), y=960, font=f(R_, 56), col=MUTE)

def scena(i):
    def fn(t):
        img = kenburns(CELLE[i], t, 1.0, 1.05)
        lay = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * min(1, t * 5))
        n = str(i + 1); fn_ = f(B, 230); d.text(((VW - d.textlength(n, font=fn_)) / 2, 150), n, font=fn_, fill=LED + (a,))
        fs = f(SB, 60); d.text(((VW - d.textlength(NOMI[i], font=fs)) / 2, 470), NOMI[i], font=fs, fill=INK + (a,))
        out = img.convert('RGBA'); out.alpha_composite(lay); return out.convert('RGB')
    return fn

def sc_voto(t):
    img = scritta(nero.copy(), 'Vote 1 to 6 in the comments.', min(1, t * 4), y=300, font=f(SB, 80),
                  sotto='Your votes help us pick the first resin prototype.')
    a = min(1, max(0, (t - .1) * 3)); base = img.copy(); base.paste(GRIGLIA, (60, 700))
    return Image.blend(img, base, a)

def griglia():
    cw = (VW - 120 - 2 * 16) // 3; ch = int(cw * 865 / 700); g = Image.new('RGB', (VW - 120, 2 * (ch + 60)), BG); d = ImageDraw.Draw(g)
    for i in range(6):
        c, r = i % 3, i // 3; y0 = 0 if r == 0 else 940
        x, y = c * (cw + 16), r * (ch + 60)
        g.paste(var.crop((c * 700, y0, c * 700 + 700, y0 + 865)).resize((cw, ch), Image.LANCZOS), (x, y))
        s = f'{i + 1} · {NOMI[i]}'; fs = f(R_, 24)
        d.text((x + (cw - d.textlength(s, font=fs)) / 2, y + ch + 14), s, font=fs, fill=INK)
    return g
GRIGLIA = griglia()

def sc_fine(t):
    return finale(kenburns(CELLE[4], t, 1.04, 1.0).point(lambda v: int(v * .35)), t, 'Open source. Built in public.', 'Follow the build:')

SCENE = [(2.4, sc_gancio)] + [(1.7, scena(i)) for i in range(6)] + [(3.4, sc_voto), (3.6, sc_fine)]
print('ok', monta_reel(SCENE, OUT, copertina=(7, .9)), 's')
