#!/usr/bin/env python3
"""Genera sfondi/index.html: galleria autonoma (immagini come data URI) dei 8 sfondi."""
import base64, io, os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
ITEMS = [
    ("01_midnight", "Midnight", "A midnight-blue monolith hanging from its cord in a soft teal glow: calm, minimal, dark."),
    ("02_macro-slit", "Macro slit", "Close-up of the glossy black face and the three LEDs glowing red, green and blue behind the slit."),
    ("03_gold-contacts", "Gold contacts", "The back of the monolith: four gold contacts for 5V, GND, SWDIO and SWCLK."),
    ("04_exploded-board", "Exploded view", "Technical isometric view: resin shell, board, battery and motor, back shell."),
    ("05_two-microphones", "Two microphones", "Abstract sound waves from the front and top microphones overlapping into an interference pattern."),
    ("06_ivory-light", "Ivory", "A light wallpaper: the ivory finish on a warm paper background."),
    ("07_six-finishes", "Six finishes", "The six chosen finishes side by side: carbon, soft-touch, gloss, anthracite, blue, ivory."),
    ("08_recording", "Recording", "A speech waveform in teal fading to bronze, with the REC light."),
]
cards = []
for i, (key, title, desc) in enumerate(ITEMS, 1):
    im = Image.open(os.path.join(BASE, "png", f"{key}_iphone.png")).convert("RGB")
    im = im.resize((420, round(420 * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    cards.append(f'''<figure class="card"><div class="phone"><div class="notch"></div><img src="{uri}" alt="Wallpaper {i}: {title}" loading="lazy"></div>
<figcaption><span class="n">{i}</span><h2>{title}</h2><p>{desc}</p></figcaption></figure>''')

html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>notªpad wallpapers</title>
<style>
:root{{color-scheme:dark;--bg:#0e0e10;--ink:#efebe3;--mute:#9a968e;--line:#2a2a2f;--bronze:#b8895a}}
*{{box-sizing:border-box;min-width:0}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 Inter,"Segoe UI",system-ui,sans-serif;overflow-x:clip}}
header{{padding:56px max(5vw,16px) 8px;max-width:1200px;margin:0 auto}}
h1{{font:600 clamp(34px,6vw,56px)/1.05 "Inter Tight",Inter,"Segoe UI",sans-serif;letter-spacing:-.02em;margin:0}}
header p{{color:var(--mute);max-width:40em;margin:12px 0 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:44px 28px;padding:36px max(5vw,16px) 80px;max-width:1200px;margin:0 auto}}
.card{{margin:0;display:flex;flex-direction:column;align-items:center}}
.phone{{position:relative;width:100%;max-width:260px;aspect-ratio:1179/2556;border-radius:38px;padding:7px;background:linear-gradient(145deg,#3a3a40,#121214);box-shadow:0 0 0 1px #4a4a52,0 30px 60px -20px #000}}
.phone img{{display:block;width:100%;height:100%;object-fit:cover;border-radius:31px}}
.notch{{position:absolute;z-index:2;top:16px;left:50%;transform:translateX(-50%);width:28%;height:20px;border-radius:12px;background:#000}}
figcaption{{margin-top:18px;max-width:260px;width:100%}}
.n{{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;border:1px solid var(--bronze);color:var(--bronze);font-size:14px;font-weight:600}}
h2{{display:inline;font:600 19px "Inter Tight",Inter,"Segoe UI",sans-serif;margin-left:10px;vertical-align:middle}}
figcaption p{{color:var(--mute);font-size:14px;margin:8px 0 0}}
footer{{color:var(--mute);font-size:13px;text-align:center;padding:0 16px 48px}}
</style></head><body>
<header><h1>notªpad wallpapers</h1>
<p>Eight proposals for phone wallpapers, numbered 1 to 8. Each comes in iPhone (1179 × 2556) and Android (1080 × 2400). The clock area at the top is kept clear and a discreet "Sponsor" slot sits above the home bar.</p></header>
<main class="grid">
{chr(10).join(cards)}
</main>
<footer>Previews are reduced; full-size PNG files are in sfondi/png/.</footer>
</body></html>'''
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
print(len(html) // 1024, "KB")
