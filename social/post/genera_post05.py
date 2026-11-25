"""Post 5 – carosello "Where do your recordings go?" (Instagram 4:5). Confronto onesto, nessun marchio."""
from comune import *
OUT = os.path.join(D, '05_where-recordings-go'); N = 5
slides = []

# 1 – domanda
im = velo(sfondo('08_recording_iphone.png', 430), alto=600, basso=300); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'A question worth asking')
y = testo(d, (80, 132), 'You record your whole day. Where does it go?', f(SB, 66))
testo(d, (80, y + 14), 'Swipe for how we are designing notªpad.', f(R_, 34), MUTE)
marchio(d); numero(d, 1, N); slides.append(im)

# 2 – confronto a due colonne
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Two ways to build an AI recorder')
cx = [80, 580]; tit = ['The usual way', 'notªpad']; col = [MUTE, LED]
righe = [('Audio uploaded to the maker\'s cloud', 'Audio stays on your devices'),
         ('Their AI, their prompts', 'The AI you choose, via MCP'),
         ('Monthly subscription', 'No subscription'),
         ('Closed app and firmware', 'Open hardware and software'),
         ('Notes stay in their app', 'Notes become yours')]
d.text((cx[0], 160), tit[0], font=f(SB, 44), fill=col[0]); d.text((cx[1], 160), tit[1], font=f(SB, 44), fill=col[1])
d.line((540, 160, 540, 1150), fill=(60, 58, 55), width=2)
y = 270
for a, b in righe:
    ya = testo(d, (cx[0], y), a, f(R_, 33), MUTE, larg=420, inter=1.2)
    yb = testo(d, (cx[1], y), b, f(SB, 33), INK, larg=420, inter=1.2)
    y = max(ya, yb) + 52
marchio(d); numero(d, 2, N); slides.append(im)

# 3 – il percorso dei dati (schema verticale)
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'The path of a recording')
passi = [('1', 'notªpad', 'Records to its own memory. Nothing leaves it until it syncs.'),
         ('2', 'Your phone', 'Bluetooth sync. Speech-to-text runs on the phone itself.'),
         ('3', 'Open MCP server', 'Hands your notes to your AI. Once your AI has them, we delete them.'),
         ('4', 'Your AI', 'Organises your day. The result is yours to keep.')]
y = 170
for i, (n, t, s) in enumerate(passi):
    c = LED if i == 2 else (BRONZE if i == 3 else INK)
    d.ellipse((80, y, 160, y + 80), outline=c, width=4); fn = f(B, 40)
    d.text((120 - d.textlength(n, font=fn) / 2, y + 12), n, font=fn, fill=c)
    yy = testo(d, (200, y + 4), t, f(SB, 42), INK, larg=W - 280)
    yy = testo(d, (200, yy + 2), s, f(R_, 31), MUTE, larg=W - 280, inter=1.25)
    if i < 3: d.line((120, y + 92, 120, yy + 30), fill=(70, 68, 64), width=3)
    y = yy + 44
marchio(d); numero(d, 3, N); slides.append(im)

# 4 – sei tu a decidere
im = velo(sfondo('02_macro-slit_iphone.png', 220), alto=680, basso=300); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Your call')
y = testo(d, (80, 132), 'Prefer nothing in the middle? Run the server yourself.', f(SB, 58))
testo(d, (80, y + 14), 'The server is open source too. Your recordings never have to touch anyone else\'s computer.', f(R_, 34), MUTE, inter=1.3)
marchio(d); numero(d, 4, N); slides.append(im)

# 5 – chiusura
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Tell us', BRONZE)
y = testo(d, (80, 132), 'What would you want an AI to do with your day?', f(SB, 62))
y = testo(d, (80, y + 20), 'A to-do list? A diary? Meeting minutes? Reply in the comments: we read them all.', f(R_, 36), MUTE, inter=1.3)
testo(d, (80, H - 300), 'Work in progress: this is the design, not a finished product.', f(R_, 30), MUTE)
marchio(d); numero(d, 5, N); slides.append(im)

salva_carosello(slides, OUT); print('ok')
