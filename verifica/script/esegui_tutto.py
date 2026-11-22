"""Rilancia tutta la verifica pre-ordine (python di sistema; usa kicad-cli e il python di KiCad 10).
Uso: python verifica/script/esegui_tutto.py   (dalla radice del progetto)
Uscite in %TEMP%/notapad_verifica/out (o NOTAPAD_VERIFICA_TMP) ; poi scrivi_risultati.py aggiorna verifica/risultati.json."""
import os, subprocess, sys, zipfile, shutil, tempfile
QUI = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(QUI, "..", ".."))
K = os.path.join(PRJ, "kicad")
BIN = os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin")
CLI, KPY = os.path.join(BIN, "kicad-cli.exe"), os.path.join(BIN, "python.exe")
LAV = os.environ.get("NOTAPAD_VERIFICA_TMP", os.path.join(tempfile.gettempdir(), "notapad_verifica"))
OUT = os.path.join(LAV, "out"); os.makedirs(OUT, exist_ok=True)
PCB, SCH = os.path.join(K, "notapad_v0.1.kicad_pcb"), os.path.join(K, "notapad_v0.1.kicad_sch")


def run(*a):
    print(">", " ".join(a[:3])); subprocess.run(a, check=False)


run(CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", os.path.join(OUT, "erc.json"), SCH)
run(CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "--refill-zones", "-o", os.path.join(OUT, "drc.json"), PCB)
run(CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", os.path.join(OUT, "netlist.net"), SCH)
run(CLI, "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "-o", os.path.join(OUT, "pos.csv"), PCB)
g, gn = os.path.join(LAV, "gerber"), os.path.join(LAV, "gerber_nuovi")
for d in (g, gn):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
zipfile.ZipFile(os.path.join(K, "fab_out", "jlcpcb", "notapad_v0.1_gerber_4strati.zip")).extractall(g)
run(CLI, "pcb", "export", "gerbers", "--output", gn + os.sep, "--layers",
    "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts", "--no-x2", "--subtract-soldermask", PCB)
run(CLI, "pcb", "export", "drill", "--output", gn + os.sep, "--format", "excellon", "--drill-origin", "absolute",
    "--excellon-units", "mm", "--excellon-separate-th", PCB)
run(KPY, os.path.join(QUI, "estrai_pcb.py"), PCB, OUT)
run(KPY, os.path.join(QUI, "test_A_via_in_pad.py"), PCB, os.path.join(OUT, "test_A_viapad.json"))
cp = os.path.join(LAV, "drc_strict"); shutil.rmtree(cp, ignore_errors=True); os.makedirs(cp)
for f in ("notapad_v0.1.kicad_pcb", "notapad_v0.1.kicad_pro", "notapad_v0.1.kicad_dru", "notapad_v0.1.kicad_sch", "fp-lib-table", "sym-lib-table"):
    shutil.copy(os.path.join(K, f), cp)
shutil.copytree(os.path.join(K, "lib"), os.path.join(cp, "lib"))
run(sys.executable, os.path.join(QUI, "test_A_drc_severo.py"), cp, CLI, os.path.join(OUT, "test_A_severo.json"))
run(sys.executable, os.path.join(QUI, "test_C_simbolo_impronta.py"), PRJ, OUT)
run(sys.executable, os.path.join(QUI, "test_E_bom_cpl.py"), PRJ, OUT)
run(sys.executable, os.path.join(QUI, "test_F_meccanica.py"), OUT)
run(sys.executable, os.path.join(QUI, "test_G_gerber.py"), g, gn, os.path.join(OUT, "test_G.json"))
run(sys.executable, os.path.join(QUI, "test_H_documenti.py"), PRJ, OUT)
print("Fatto. Esiti e testi dei test: elenco_test.py -> python scrivi_risultati.py <progetto> \"stato\" [--concluso]")
