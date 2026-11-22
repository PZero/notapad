"""Scrive verifica/risultati.json (scrittura atomica .tmp -> rename) dai dati di elenco_test.py.
Uso: python scrivi_risultati.py <progetto> "<stato_lavoro>" [--concluso]"""
import sys, os, json, datetime, importlib.util
qui = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("elenco_test", os.path.join(qui, "elenco_test.py"))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
prj = sys.argv[1]
stato = sys.argv[2] if len(sys.argv) > 2 else ""
concluso = "--concluso" in sys.argv
pianta = {"scheda": [16.5, 38], "oggetti": []}
import tempfile
fj = os.path.join(qui, "out", "test_F.json")
if not os.path.exists(fj):
    fj = os.path.join(os.environ.get("NOTAPAD_VERIFICA_TMP", os.path.join(tempfile.gettempdir(), "notapad_verifica")), "out", "test_F.json")
if os.path.exists(fj):
    pianta["oggetti"] = json.load(open(fj, encoding="utf-8"))["pianta"]
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
R = {"aggiornato": now, "stato_lavoro": stato, "concluso": concluso,
     "data": "2026-11-22", "scheda": "notapad v0.1", "fonti": E.FONTI, "test": E.TEST,
     "sintesi": E.SINTESI, "stack": E.STACK, "pianta": pianta}
d = os.path.join(prj, "verifica"); os.makedirs(d, exist_ok=True)
tmp = os.path.join(d, "risultati.json.tmp")
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(R, f, indent=1, ensure_ascii=False)
os.replace(tmp, os.path.join(d, "risultati.json"))
from collections import Counter
print(now, dict(Counter(t["esito"] for t in E.TEST)))
