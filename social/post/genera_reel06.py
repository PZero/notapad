"""Post 6 – Reel "Two microphones, one listens for you" (~19 s)."""
from comune import *
OUT = os.path.join(D, '06_reel-two-microphones')
nero = Image.new('RGB', (VW, VH), BG)
mics = velo_alto(carica916('05_two-microphones_iphone.png', 250, 2100))
fessura = velo_alto(carica916('02_macro-slit_iphone.png', 0, 2300))
rec = velo_alto(carica916('08_recording_iphone.png', 300, 2000))

def sc_gancio(t):
    return scritta(nero.copy(), 'It sleeps until you speak.', min(1, t * 3), y=720, font=f(SB, 96))

def sc_due(t):
    return scritta(kenburns(mics, t), 'Two microphones.', min(1, t * 4), y=300, sotto='One on the front, one on top.')

def sc_ascolta(t):
    img = kenburns(mics, t, 1.08, 1.14)
    return scritta(img, 'The top one keeps listening.', min(1, t * 4), y=300, sotto='It sips almost no power while the rest of notªpad sleeps.')

def sc_voce(t):
    # onde che crescono: qualcuno parla
    img = kenburns(rec, t, 1.0, 1.05)
    return scritta(img, 'Someone speaks…', min(1, t * 4), y=300, sotto='…and it wakes the whole device in a blink.')

def sc_led(t):
    img = kenburns(fessura, t, 1.0, 1.06)
    # bagliore dei LED che si accende
    g = Image.new('RGB', (VW, VH), BG); d = ImageDraw.Draw(g); a = min(1, t * 2.5)
    from PIL import ImageFilter
    for i, c in enumerate([(255, 70, 90), (60, 230, 140), (70, 130, 255)]):
        d.ellipse((240 + i * 220, 1000, 400 + i * 220, 1300), fill=tuple(int(v * .55 * a) for v in c))
    g = g.filter(ImageFilter.GaussianBlur(90))
    img = Image.fromarray(__import__('numpy').minimum(255, __import__('numpy').asarray(img, dtype='int16') + __import__('numpy').asarray(g, dtype='int16')).astype('uint8'))
    return scritta(img, 'Recording.', min(1, t * 4), y=300, sotto='Silence costs nothing. Your day lasts longer on one charge.')

def sc_fine(t):
    return finale(kenburns(mics, t, 1.04, 1.0).point(lambda v: int(v * .3)), t, 'Open source. Built in public.', 'Follow the build:')

SCENE = [(2.6, sc_gancio), (3.2, sc_due), (3.4, sc_ascolta), (3.0, sc_voce), (3.4, sc_led), (3.8, sc_fine)]
print('ok', monta_reel(SCENE, OUT, copertina=(1, .6)), 's')
