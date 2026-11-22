"""Test F: courtyard (sovrapposizioni, dentro il bordo), pianta lato inferiore (batteria, motorino, contatti,
piazzole a mano, keepout), LED nella fessura, impilamento nello spessore. Produce out/test_F.json con 'pianta' e 'stack'.
Uso: python test_F_meccanica.py <out dir>
Ipotesi dichiarate (nessun CAD del guscio esiste): vedi IPOTESI."""
import sys, os, json, itertools
out = sys.argv[1]
pcb = json.load(open(os.path.join(out, "pcb.json"), encoding="utf-8"))
W, H = 16.5, 38.0
IPOTESI = {
    "E73_altezza_mm": 3.0,        # modello 3D LCSC/EasyEDA 'H3.0' (datasheet Ebyte non leggibile qui)
    "batteria": {"nome": "381620", "spessore": 3.8, "w": 16.0, "h": 20.0},
    "batteria_attuale": {"nome": "~60 mAh", "spessore": 3.5, "w": 16.0, "h": 19.0},
    "motorino": {"d": 8.0, "spessore": 2.0},
    "keepout_antenna_da_y": 32.8,
    "testa_target_d": 2.0,        # spalla del target Ø2,0 x 0,5 (scelta utente 22/11), corpo Ø1,5 x 4,0
    "target_altezza": 4.5,        # spalla 0,5 + corpo 4,0 dietro la scheda
    "target_coda_d": 0.9, "target_coda_l": 2.0,
    "monolite_mm": 9.0, "resina_fronte": 0.6, "resina_retro": 0.6,
    "fessura_led_w": 10.0,
    "resina_min_mm": 0.5,         # minimo di resina/guscio per faccia (ipotesi prudente per SLA + colata)
}
fp = {f["ref"]: f for f in pcb["footprints"]}


def bb(ref, lay="F.Courtyard"):
    c = fp[ref].get("cy", {}).get(lay)
    return None if not c else [c[0] - 100, c[1] - 100, c[2] - 100, c[3] - 100]


def ov(a, b):
    return min(a[2], b[2]) - max(a[0], b[0]) > 1e-6 and min(a[3], b[3]) - max(a[1], b[1]) > 1e-6


R = {"ipotesi": IPOTESI, "problemi": [], "note": []}
top = {r: bb(r) for r in fp if bb(r)}
bot = {r: bb(r, "B.Courtyard") for r in fp if bb(r, "B.Courtyard")}
for (a, A), (b, B) in itertools.combinations(top.items(), 2):
    if ov(A, B):
        R["problemi"].append(f"courtyard sovrapposti (sopra): {a} {b}")
for r, A in top.items():
    if A[0] < -0.05 or A[1] < -0.05 or A[2] > W + 0.05 or A[3] > H + 0.05:
        R["problemi"].append(f"courtyard {r} fuori dal bordo: {[round(v, 3) for v in A]}")
# distanze minime tra courtyard (sopra)
gaps = []
for (a, A), (b, B) in itertools.combinations(top.items(), 2):
    dx = max(A[0] - B[2], B[0] - A[2], 0); dy = max(A[1] - B[3], B[1] - A[3], 0)
    gaps.append((round((dx * dx + dy * dy) ** 0.5, 3), a, b))
R["gap_minimi_courtyard"] = sorted(gaps)[:8]

# ---- pianta lato inferiore ----
I = IPOTESI
ko = I["keepout_antenna_da_y"]
j_y = fp["J1"]["y"] - 100
y_mot_min = j_y + I["testa_target_d"] / 2 + 0.3
for bat in (I["batteria"], I["batteria_attuale"]):
    by1 = ko; by0 = ko - bat["h"]
    batt = [(W - bat["w"]) / 2, by0, (W + bat["w"]) / 2, by1]
    mot_y0 = y_mot_min; mot_y1 = mot_y0 + I["motorino"]["d"]
    spazio = by0 - y_mot_min
    mot = [W / 2 - 4, mot_y0, W / 2 + 4, mot_y1]
    rr = {"batteria": [round(v, 2) for v in batt], "motorino": [round(v, 2) for v in mot],
          "spazio_tra_target_e_batteria_mm": round(spazio, 2), "motorino_ci_sta": spazio >= I["motorino"]["d"]}
    sotto = []
    for r in ("BT1P", "BT1N", "M1P", "M1N", "TPA", "TPB"):
        A = bot[r]
        if ov(A, batt):
            sotto.append(f"{r} sotto la batteria (y {A[1]:.2f}-{A[3]:.2f}, batteria da {by0:.2f})")
        if ov(A, mot):
            sotto.append(f"{r} sotto il motorino")
    for r in ("J1", "J2", "J3", "J4"):
        A = bb(r, "B.Courtyard")
        if ov(A, batt) or ov(A, mot):
            sotto.append(f"{r} interferisce con batteria/motorino")
    rr["interferenze"] = sotto
    R[f"pianta_{bat['nome']}"] = rr

# ---- LED nella fessura ----
leds = [fp[r] for r in ("D1", "D2", "D3")]
xs = [f["x"] - 100 for f in leds]; ys = [f["y"] - 100 for f in leds]
c = (min(xs) + max(xs)) / 2
R["led"] = {"x": xs, "y": ys, "centro": c, "passo": [round(xs[1] - xs[0], 2), round(xs[2] - xs[1], 2)],
            "ingombro_x": [round(bb("D1")[0], 2), round(bb("D3")[2], 2)],
            "fessura_x": [round(W / 2 - I["fessura_led_w"] / 2, 2), round(W / 2 + I["fessura_led_w"] / 2, 2)],
            "dentro": bb("D1")[0] >= W / 2 - 5 and bb("D3")[2] <= W / 2 + 5, "allineati_y": len(set(ys)) == 1}

# ---- impilamento ----
alt_top = I["E73_altezza_mm"]
for bat in (I["batteria"], I["batteria_attuale"]):
    tot = alt_top + 1.0 + bat["spessore"]
    R[f"stack_{bat['nome']}"] = {"componenti_mm": round(tot, 2),
                                  "margine_8mm_per_faccia": round((8 - tot) / 2, 2),
                                  "margine_9mm_per_faccia": round((9 - tot) / 2, 2)}
prof = round(I["monolite_mm"] - I["resina_fronte"] - alt_top - 1.0, 2)
drill = fp["J1"]["pads"][0]["drill"]; padd = fp["J1"]["pads"][0]["w"]
# distanza spalla (Ø2,0) dei target da motorino e batteria (pianta 381620)
mot = R["pianta_381620"]["motorino"]; bat = R["pianta_381620"]["batteria"]
dmin = []
for r in ("J1", "J2", "J3", "J4"):
    jx, jy = fp[r]["x"] - 100, fp[r]["y"] - 100
    cx, cy = W / 2, (mot[1] + mot[3]) / 2
    dmin.append(round(((jx - cx) ** 2 + (jy - cy) ** 2) ** 0.5 - 4.0 - I["testa_target_d"] / 2, 2))
R["target_vs_retro"] = {"profondita_retro_disponibile_mm": prof, "altezza_target_mm": I["target_altezza"],
                        "sporgenza_mm": round(I["target_altezza"] - prof, 2), "resina_dietro_batteria_mm": round(prof - I["batteria"]["spessore"], 2),
                        "foro_mm": drill, "pad_mm": padd, "anello_mm": round((padd - drill) / 2, 3),
                        "gioco_coda_diametrale_mm": round(drill - I["target_coda_d"], 2),
                        "coda_sopra_scheda_mm": round(I["target_coda_l"] - 1.0, 2),
                        "distanza_spalla_motorino_mm": dmin, "distanza_spalla_batteria_mm": round(bat[1] - (fp["J1"]["y"] - 100 + I["testa_target_d"] / 2), 2)}
R["stack_9mm"] = {"strati": [["resina/guscio fronte", 0.0, I["resina_fronte"]], ["U1 E73 (3,0 mm)", I["resina_fronte"], I["resina_fronte"] + alt_top],
                             ["scheda 1,0 mm", I["resina_fronte"] + alt_top, I["resina_fronte"] + alt_top + 1.0],
                             ["batteria 381620 3,8 mm", I["resina_fronte"] + alt_top + 1.0, I["resina_fronte"] + alt_top + 1.0 + I["batteria"]["spessore"]],
                             ["resina/guscio retro", I["resina_fronte"] + alt_top + 1.0 + I["batteria"]["spessore"], I["monolite_mm"]]],
                  "target": [I["resina_fronte"] + alt_top + 1.0, I["resina_fronte"] + alt_top + 1.0 + I["target_altezza"]]}

# ---- pianta per risultati.json ----
pianta = []
for r, A in sorted(top.items()):
    if r.startswith("J"):
        continue
    pianta.append({"nome": f"{r} {fp[r]['value'][:22]}", "tipo": "top", "x": round(A[0], 2), "y": round(A[1], 2),
                   "w": round(A[2] - A[0], 2), "h": round(A[3] - A[1], 2)})
for r, A in sorted(bot.items()):
    if r.startswith("J"):
        continue
    pianta.append({"nome": f"{r} piazzola retro", "tipo": "bottom", "x": round(A[0], 2), "y": round(A[1], 2),
                   "w": round(A[2] - A[0], 2), "h": round(A[3] - A[1], 2)})
for r in ("J1", "J2", "J3", "J4"):
    f = fp[r]
    dr = f["pads"][0]["drill"]
    pianta.append({"nome": f"{r} foro {dr:.1f} mm (pad 1,6), target spalla Ø2,0".replace(".", ","), "tipo": "foro", "x": round(f["x"] - 100 - 0.8, 2),
                   "y": round(f["y"] - 100 - 0.8, 2), "w": 1.6, "h": 1.6})
b = R["pianta_381620"]["batteria"]; m = R["pianta_381620"]["motorino"]
pianta.append({"nome": "Batteria 381620 16x20x3,8 (ipotesi: fino al keepout)", "tipo": "bottom", "x": b[0], "y": b[1], "w": round(b[2] - b[0], 2), "h": round(b[3] - b[1], 2)})
pianta.append({"nome": "Motorino 0820 D8x2 (ipotesi)", "tipo": "bottom", "x": m[0], "y": m[1], "w": 8.0, "h": 8.0})
pianta.append({"nome": "Keepout antenna (4 strati)", "tipo": "keepout", "x": 0, "y": ko, "w": W, "h": round(H - ko, 2)})
pianta.append({"nome": "Fessura LED 10 mm (ipotesi centrata)", "tipo": "fessura", "x": R["led"]["fessura_x"][0], "y": round(ys[0] - 1.0, 2), "w": 10.0, "h": 2.0})
for r in ("MK1", "MK2"):
    f = fp[r]
    pianta.append({"nome": f"{r} porta top (lid, verso il fronte)", "tipo": "porta", "x": round(f["x"] - 100 - 0.35, 2), "y": round(f["y"] - 100 - 0.35, 2), "w": 0.7, "h": 0.7})
pianta.append({"nome": "Zona anello/boccola (resina sopra il bordo, 1,5 mm se centrata)", "tipo": "keepout", "x": 4.25, "y": -1.5, "w": 8.0, "h": 1.5})
R["pianta"] = pianta
json.dump(R, open(os.path.join(out, "test_F.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in R.items() if k != "pianta"}, indent=1, ensure_ascii=False))
