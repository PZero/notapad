"""Post 3 – carosello evergreen "Why notapad matters / we need your feedback" (Instagram 4:5).
Senza date né tappe: si può ripubblicare in qualunque momento (anche nei periodi senza novità)."""
from comune import *
OUT = os.path.join(D, '03_why-it-matters'); N = 7
slides = []

# 1 – copertina
im = velo(sfondo('01_midnight_iphone.png', 520), alto=480, basso=260); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Why we are building this')
testo(d, (80, 132), 'Your best ideas are said out loud. Then they are gone.', f(SB, 64))
marchio(d); numero(d, 1, N); slides.append(im)

# 2 – il problema
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'The problem')
y = testo(d, (80, 132), 'A thought on a walk. A promise in a meeting. A name you meant to remember.', f(SB, 56))
testo(d, (80, y + 30), 'Most of what we say and hear is never written down. A day later, it is mostly lost.', f(R_, 38), MUTE, inter=1.3)
marchio(d); numero(d, 2, N); slides.append(im)

# 3 – perché non basta ciò che esiste
im = velo(sfondo('08_recording_iphone.png', 430), alto=640, basso=300); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Why not just buy one?')
y = testo(d, (80, 132), 'AI recorders exist. But your days live in someone else\'s cloud.', f(SB, 56))
testo(d, (80, y + 20), 'They pick the AI for you, charge every month, and if the company changes its plans, your memories go with it.', f(R_, 34), MUTE, inter=1.3)
marchio(d); numero(d, 3, N); slides.append(im)

# 4 – i principi
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'What notªpad stands for', BRONZE)
y = 150
for tit, sub in [('Your data.', 'Recordings stay on your devices. You decide where they go.'),
                 ('Your AI.', 'Any assistant you like, through an open MCP server.'),
                 ('Open, all the way.', 'Hardware, firmware and app are public: build it, repair it, change it.'),
                 ('No subscription.', 'A device you own, not a service you rent.')]:
    y = testo(d, (80, y), tit, f(SB, 50)); y = testo(d, (80, y + 2), sub, f(R_, 32), MUTE, inter=1.25) + 38
marchio(d); numero(d, 4, N); slides.append(im)

# 5 – i riscontri contano
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Why your feedback matters')
y = testo(d, (80, 132), 'Might you use one someday? Then your opinion matters most.', f(SB, 56))
y = testo(d, (80, y + 16), 'We are two makers, not a company. We would rather build what you need than guess, and the design is still open.', f(R_, 32), MUTE, inter=1.3)
y = testo(d, (80, y + 30), 'Tell us honestly:', f(SB, 38), BRONZE) + 14
for q in ['Would you wear it all day?', 'What would worry you about it?', 'What should it do with your day?', 'What would make you trust it?']:
    d.ellipse((84, y + 16, 98, y + 30), fill=LED)
    y = testo(d, (124, y), q, f(R_, 38), INK, larg=W - 200) + 14
marchio(d); numero(d, 5, N); slides.append(im)

# 6 – come aiutare
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'How you can help', BRONZE)
y = 150
for i, (tit, sub) in enumerate([('Tell us what you need.', 'The most valuable help of all. Comments and DMs are always open.'),
                                ('Share it.', 'With someone who loses ideas, or who would never trust a closed recorder.'),
                                ('Chip in.', 'Individuals: ko-fi.com/notapad. Every coffee goes into prototype boards.'),
                                ('Sponsor the prototypes.', 'Companies: help us build the first 3–5 boards. Write to notapad.team@gmail.com')]):
    c = LED if i == 0 else INK
    n = str(i + 1); d.ellipse((80, y + 2, 140, y + 62), outline=c, width=3); fn = f(B, 32)
    d.text((110 - d.textlength(n, font=fn) / 2, y + 10), n, font=fn, fill=c)
    yy = testo(d, (170, y), tit, f(SB, 46), c, larg=W - 250)
    y = testo(d, (170, yy + 2), sub, f(R_, 31), MUTE, larg=W - 250, inter=1.25) + 44
marchio(d); numero(d, 6, N); slides.append(im)

# 7 – chiusura
im = velo(sfondo('03_gold-contacts_iphone.png', 560), alto=520, basso=560); d = ImageDraw.Draw(im)
etichetta(d, (80, 86), 'Build it with us', BRONZE)
testo(d, (80, 132), 'An open recorder needs open conversation.', f(SB, 62))
y = H - 390
y = testo(d, (80, y), 'Start now: what would you need it to do? Tell us in the comments.', f(SB, 36))
d.text((80, y + 20), 'Follow @notapadlabs', font=f(SB, 32), fill=LED)
marchio(d); numero(d, 7, N); slides.append(im)

salva_carosello(slides, OUT); print('ok')
