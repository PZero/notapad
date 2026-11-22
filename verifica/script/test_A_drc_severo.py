"""Test A: DRC 'severo' su una COPIA del progetto: tutte le regole ignorate portate a 'error',
regole JLC multistrato (pista 0,09 -> usiamo 0,10, foro via 0,2, anello 0,13 consigliato, testo >= 1,0/0,15).
Uso: <KiCad>\\bin\\python.exe test_A_drc_severo.py <cartella copia> <kicad-cli> <out json>"""
import sys, json, os, subprocess
d, cli, outp = sys.argv[1], sys.argv[2], sys.argv[3]
pro = os.path.join(d, "notapad_v0.1.kicad_pro")
p = json.load(open(pro, encoding="utf-8"))
sev = p["board"]["design_settings"]["rule_severities"]
ign = [k for k, v in sev.items() if v == "ignore"]
for k in ign:
    sev[k] = "error"
r = p["board"]["design_settings"]["rules"]
r["min_text_height"] = 1.0        # JLC: altezza carattere consigliata >= 1,0 mm
r["min_text_thickness"] = 0.15    # JLC: tratto >= 0,15 mm
json.dump(p, open(pro, "w", encoding="utf-8"), indent=2)
rep = os.path.join(d, "drc_severo.json")
subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", rep,
                os.path.join(d, "notapad_v0.1.kicad_pcb")], capture_output=True)
R = json.load(open(rep, encoding="utf-8"))
from collections import Counter
c = Counter(v["type"] for v in R["violations"])
det = {}
for v in R["violations"]:
    det.setdefault(v["type"], []).append(" | ".join(i["description"] for i in v["items"])[:160])
out = {"regole_riattivate": ign, "conteggio": dict(c), "esempi": {k: v[:8] for k, v in det.items()},
       "unconnected": len(R.get("unconnected_items", [])), "parity": len(R.get("schematic_parity", []))}
json.dump(out, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])
