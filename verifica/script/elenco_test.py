# -*- coding: utf-8 -*-
"""Elenco dei test della revisione pre-ordine notapad v0.1 (dati per scrivi_risultati.py)."""
P = ""  # percorsi relativi alla radice del repository
FONTI = [
    {"id": "DEF", "descrizione": "Definizione unica componenti/reti/piazzamento", "url_o_percorso": P + "kicad/notapad_def.py"},
    {"id": "SCH", "descrizione": "Schema KiCad", "url_o_percorso": P + "kicad/notapad_v0.1.kicad_sch"},
    {"id": "NET", "descrizione": "Netlist esportata ora con kicad-cli 10.0.8", "url_o_percorso": "scratchpad verifica/out/netlist.net"},
    {"id": "PCB", "descrizione": "Scheda KiCad (letta con pcbnew)", "url_o_percorso": P + "kicad/notapad_v0.1.kicad_pcb"},
    {"id": "PRO", "descrizione": "Regole progetto e .kicad_dru", "url_o_percorso": P + "kicad/notapad_v0.1.kicad_pro"},
    {"id": "GBR", "descrizione": "Gerber/drill JLC (zip estratto)", "url_o_percorso": P + "kicad/fab_out/jlcpcb/notapad_v0.1_gerber_4strati.zip"},
    {"id": "BOM", "descrizione": "BOM JLC", "url_o_percorso": P + "kicad/fab_out/jlcpcb/notapad_v0.1_BOM_JLC.csv"},
    {"id": "CPL", "descrizione": "CPL JLC", "url_o_percorso": P + "kicad/fab_out/jlcpcb/notapad_v0.1_CPL_JLC.csv"},
    {"id": "LEGGIMI", "descrizione": "Note d'ordine JLC", "url_o_percorso": P + "kicad/fab_out/jlcpcb/LEGGIMI.md"},
    {"id": "COLL", "descrizione": "Collegamenti per rete", "url_o_percorso": P + "jlc/notapad_v0.1_collegamenti.csv"},
    {"id": "PINOUT", "descrizione": "Pinout nRF52840 v0.1", "url_o_percorso": P + "docs/pinout_v0.1.md"},
    {"id": "MANO", "descrizione": "Pezzi montati a mano", "url_o_percorso": P + "jlc/notapad_v0.1_montaggio_a_mano.csv"},
    {"id": "DXF", "descrizione": "Contorno DXF", "url_o_percorso": P + "jlc/notapad_v0.1_contorno.dxf"},
    {"id": "LIB", "descrizione": "Simboli e impronte LCSC (easyeda2kicad)", "url_o_percorso": P + "kicad/lib/"},
    {"id": "3D", "descrizione": "Modelli 3D LCSC (altezze)", "url_o_percorso": P + "kicad/lib/notapad.3dshapes/"},
    {"id": "DOC", "descrizione": "CLAUDE.md, STATO.md, DECISIONI.md", "url_o_percorso": P + "docs/STATO.md"},
    {"id": "E73_EASYEDA", "descrizione": "Simbolo LCSC/EasyEDA E73-2G4M08S1C (43 pin)", "url_o_percorso": "https://www.flux.ai/lcsc/e73-2g4m08s1c~410y.md"},
    {"id": "E73_MAN", "descrizione": "Manuale Ebyte E73-2G4M08S1C v1.9 (PDF cifrato: non leggibile con gli strumenti disponibili)", "url_o_percorso": "https://www.rcscomponents.kiev.ua/datasheets/e73-2g4m08s1c_usermanual_v1_9.pdf"},
    {"id": "JLC_E73", "descrizione": "JLC C356849: Extended, 'PCBA Type: Standard Only', 'X-ray Inspection: Required', SMD 18x13", "url_o_percorso": "https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E732G4M08S1C/C356849"},
    {"id": "NRF_PIN", "descrizione": "nRF52840 PS, Pin assignments aQFN73 (pin 'Standard drive, low frequency I/O only'; pin QSPI consigliati)", "url_o_percorso": "https://docs.nordicsemi.com/bundle/ps_nrf52840/page/pin.html"},
    {"id": "DS_MIC", "descrizione": "MEMSensing MSM261DGT003 datasheet V1.0 (sett. 2021): top-ported, 4x2x1,1 mm, pin 1 VDD, 2/5 GND, 3 DATA, 4 CLK, 6 L/R; VDD 1,6-3,6 V; clock std 1,1-4,0 MHz, low-power 150-900 kHz; IDD 670 uA @2,4 MHz", "url_o_percorso": "https://img.dfrobot.com.cn/wikicn/5d57611a3416442fa39bffca/f6851bc4cfbc655c7348b2bcd83268fb.pdf"},
    {"id": "JLC_MIC", "descrizione": "JLC C48227730 MSM261DGT003 LGA-6(2x4), Extended, Economic e Standard", "url_o_percorso": "https://jlcpcb.com/partdetail/C48227730"},
    {"id": "JLC_NAND", "descrizione": "JLC C3010298 W25N02KVZEIR WSON-8-EP(6x8), Extended, Economic e Standard", "url_o_percorso": "https://jlcpcb.com/partdetail/C3010298"},
    {"id": "JLC_CHG", "descrizione": "JLC C424093 MCP73831T-2ACI/OT SOT-23-5, Extended", "url_o_percorso": "https://jlcpcb.com/partdetail/C424093"},
    {"id": "JLC_C38066", "descrizione": "JLC C38066 MCP73832T-2ACI/OT SOT-23-5 (STAT open-drain), Extended, Economic e Standard", "url_o_percorso": "https://jlcpcb.com/partdetail/C38066"},
    {"id": "MCP_STAT", "descrizione": "MCP73831/2: STAT tri-state (H/L/Hi-Z) sul 31, open-drain sul 32; a fine carica il 31 va ALTO (alimentato da VDD)", "url_o_percorso": "https://www.snapeda.com/questions/question/difference-between-mcp73831-and-mcp73832"},
    {"id": "MCP_DS", "descrizione": "Microchip MCP73831/2 DS20001984H (PDF cifrato, non leggibile qui: valori VOH/IREG da riconfermare)", "url_o_percorso": "https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf"},
    {"id": "JLC_TTP", "descrizione": "JLC C42422127 TTP223-BA6-TD SOT-23-6, Extended", "url_o_percorso": "https://jlcpcb.com/partdetail/C42422127"},
    {"id": "TTP_DS", "descrizione": "TTP223-BA6: 1 Q, 2 VSS, 3 I, 4 AHLB (0 = attivo alto), 5 VDD, 6 TOG (0 = diretto)", "url_o_percorso": "https://www.datasheetspdf.com/pdf/770045/TT/TTP223-BA6/1"},
    {"id": "JLC_LED", "descrizione": "JLC C404280 MHPA1010RGBDT 1x1 mm anodo comune, Vf R 1,7-2,3 V, G/B 2,5-3,5 V, Extended", "url_o_percorso": "https://jlcpcb.com/partdetail/C404280"},
    {"id": "LED_EASYEDA", "descrizione": "Simbolo LCSC/EasyEDA MHPA1010RGBDT: 1 +, 2 R-, 3 G-, 4 B-", "url_o_percorso": "https://www.flux.ai/lcsc/mhpa1010rgbdt~5tf8.md"},
    {"id": "LED_DS", "descrizione": "Datasheet MEIHUA MHPA1010RGBDT (PDF solo immagini: non leggibile)", "url_o_percorso": "https://storage.googleapis.com/graviton-electric-symbols/document_assets/lcsc/2409272202_MEIHUA-MHPA1010RGBDT_C404280.pdf"},
    {"id": "JLC_Q2", "descrizione": "JLC C83571 2N7002DW-7-F SOT-363, Extended", "url_o_percorso": "https://jlcpcb.com/partdetail/C83571"},
    {"id": "JLC_LDO", "descrizione": "JLC C5446 XC6206P332MR-G SOT-23-3L, Basic", "url_o_percorso": "https://jlcpcb.com/partdetail/C5446"},
    {"id": "JLC_Q1", "descrizione": "JLC C15127 AO3401A SOT-23, Basic", "url_o_percorso": "https://jlcpcb.com/partdetail/C15127"},
    {"id": "JLC_Q4", "descrizione": "JLC C20917 AO3400A SOT-23, Basic", "url_o_percorso": "https://jlcpcb.com/partdetail/C20917"},
    {"id": "JLC_D", "descrizione": "JLC C2128 1N4148WS SOD-323", "url_o_percorso": "https://jlcpcb.com/partdetail/C2128"},
    {"id": "JLC_C5", "descrizione": "JLC C23733 CL05A475MP5NRNC 4,7 uF 10 V X5R 0402", "url_o_percorso": "https://jlcpcb.com/partdetail/C23733"},
]

TEST = []


def T(id, tit, metodo, fonti, atteso, trovato, esito, grav, azione="", script=""):
    TEST.append({"id": id, "categoria": id[0], "titolo": tit, "metodo": metodo, "fonti": fonti, "atteso": atteso,
                 "trovato": trovato, "esito": esito, "gravita": grav, "azione": azione, "script": script})


# ---------------- A ----------------
T("A01", "ERC rieseguito", "kicad-cli sch erc --severity-all sullo schema attuale", ["SCH"], "0 violazioni",
  "0 violazioni (4 controlli ignorati dal progetto)", "PASS", "bassa", "", "kicad-cli (vedi LEGGIMI script)")
T("A02", "DRC con parità schema e scollegati", "kicad-cli pcb drc --severity-all --schematic-parity --refill-zones", ["PCB", "SCH"],
  "0 violazioni, 0 scollegati, parità 0", "0 violazioni, 0 scollegati, 0 problemi di parità", "PASS", "alta", "", "kicad-cli")
T("A03", "DRC severo: regole ignorate riattivate + testo minimo JLC", "Copia del progetto con le 11 regole 'ignore' portate a 'error' (silk_over_copper, silk_overlap, missing_courtyard, ...) e testo min 1,0 mm / 0,15 mm",
  ["PRO", "PCB"], "nessuna violazione", "solo 2: la scritta «notªpad v0.1» su B.Silkscreen è alta 0,8 mm con tratto 0,12 mm (JLC consiglia >= 1,0 / 0,15)", "WARN", "bassa",
  "Facoltativo: portare il testo a 1,0 mm / 0,15 mm, altrimenti può risultare poco leggibile (è comunque sul retro, sotto la batteria)", "test_A_drc_severo.py")
T("A04", "Regole di progetto contro capacità JLC multistrato", "Confronto design settings (pcbnew) e .kicad_dru con jlcpcb.com/capabilities citate in CLAUDE.md",
  ["PRO", "PCB", "DOC"], "pista/spazio >= 0,09, via foro >= 0,15 e diam. >= 0,25 (senza sovrapprezzo 0,25/0,45), rame-bordo >= 0,2, foro-foro >= 0,254 (reti diverse)",
  "pista/spazio 0,10/0,10; via 0,25/0,45 (anello 0,10) su tutte le 114 via; rame-bordo 0,25 (min via-bordo reale 0,264); foro-foro minimo reale 0,318 mm; piste minime 0,10, 3V3 0,112-0,15, alimentazioni 0,15-0,2",
  "PASS", "media", "", "estrai_pcb.py")
T("A05", "Piano GND In1 continuo, isole e rame orfano", "Zone riempite lette con pcbnew: numero di isole per strato e modalità di rimozione isole", ["PCB"],
  "In1 un solo poligono fino al keepout; isole rimosse", "In1: 1 poligono (478,6 mm², 0-32,8 mm); F.Cu 16 e B.Cu 4 poligoni con rimozione isole 'sempre' (tutti connessi); In2 senza versamento (segnali)",
  "PASS", "media", "", "estrai_pcb.py")
T("A06", "Contorno: 16,5 x 38 mm, raggio 1 mm, pcb vs Gerber vs DXF", "Edge.Cuts del pcb (gr_line + gr_arc), Gerber Edge_Cuts (bbox e archi), DXF layer OUTLINE (bulge)",
  ["PCB", "GBR", "DXF"], "16,5 x 38, 4 archi R 1",
  "pcb: 4 gr_line + 4 gr_arc R 1,0 (mid a 0,707), chiuso, 16,5 x 38,0; Gerber: bbox 16,55 x 38,05 (linea 0,05) con 8 comandi d'arco; DXF OUTLINE: polilinea chiusa 16,5 x 38,0 con 4 bulge 0,4142 (archi di 90°); keepout DXF 5,2 mm = 38-32,8", "PASS", "media", "", "test_G_gerber.py")
T("A07", "Via dentro i pad SMD", "pcbnew: poligono reale di ogni pad SMD contro ogni via", ["PCB"], "nessuna via nei pad (risucchio di stagno)",
  "1 sola: via GND con centro dentro il pad 5 (GND) del modulo U1 a (14,60; 28,68)", "WARN", "bassa",
  "Accettabile su un pad di massa castellato; se si risbroglia spostarla fuori dal pad (o chiedere via tappate)", "test_A_via_in_pad.py")
T("A08", "Gerber del zip = scheda attuale", "Riesportati Gerber e drill con le stesse opzioni di genera_fab.py e confrontati riga per riga (esclusa la data)",
  ["GBR", "PCB"], "identici", "identici (solo la riga con la data differisce); il pcb non è cambiato dopo l'export", "PASS", "alta", "", "test_G_gerber.py")
T("A09", "Annotazione dello schema", "Messaggio di kicad-cli all'export della netlist", ["SCH", "NET"], "nessun avviso",
  "kicad-cli avvisa 'lo schema ha errori di annotazione' (probabilmente riferimenti senza numero: TPA, TPB, BT1P/BT1N, M1P/M1N); ERC 0 e parità 0", "WARN", "bassa",
  "Nessuna per l'ordine; eventualmente rinominare TP1/TP2, BT1/BT2, M1/M2", "")

# ---------------- B ----------------
T("B01", "E73: numero pad -> GPIO", "def.py e netlist contro il simbolo LCSC/EasyEDA (nomi AIx/XLx tradotti in P0.xx) e la tabella di pinout.md", ["DEF", "NET", "E73_EASYEDA", "PINOUT", "E73_MAN"],
  "pad 4 P0.28, 7 P0.02, 8 P0.29, 9 P0.31, 10 P0.30, 11 P0.00, 12 P0.26, 13 P0.01, 14 P0.06, 15 P0.05, 16 P0.08, 17 P1.09, 18 P0.04, 20 P0.12, 22 P0.07, 26 P0.18, 28 P0.15, 30 P0.17, 32 P0.20, 33 P0.13, 34 P0.22, 35 P0.24, 36 P1.00, 37 SWDIO, 38 P1.02, 39 SWCLK, 40 P1.04",
  "Tutti coincidenti tra simbolo LCSC, def.py, netlist e pinout.md. Il manuale Ebyte (fonte indipendente) è un PDF cifrato e non è stato leggibile qui", "WARN", "bassa",
  "Confronto a vista una tantum con la tabella 'Pin definition' del manuale Ebyte (il simbolo LCSC e l'impronta hanno la stessa origine)", "test_C_simbolo_impronta.py")
T("B02", "E73: nessun pin non esposto; pin 'low frequency'", "Pin usati contro i 43 pad del modulo e contro la lista nRF52840 'Standard drive, low frequency I/O only'", ["E73_EASYEDA", "NRF_PIN", "DEF"],
  "Nessuno di P0.11/14/16/19/21/23/25/27, P1.01; segnali veloci (QSPI, PDM) non su pin low-frequency",
  "Nessun pin non esposto usato. Su pin low-frequency (<= 10 kHz) solo segnali lenti: TOUCH_B P0.31, HOLD P0.29, VBAT P0.02, MOTOR_G P0.30, VBUS P0.28, LED3 G/B P1.02/P1.04. QSPI e PDM su pin normali (P1.09 non è nella lista)",
  "PASS", "media", "Firmware: PWM dei LED su P1.02/P1.04 e del motore su P0.30 <= 10 kHz, drive standard", "")
T("B03", "E73: alimentazione (VDD, VDDH, DCCH, VBUS, GND)", "Reti dei pad 19/23/25/27/5/21/24", ["DEF", "NET", "E73_EASYEDA"],
  "Modalità normale: VDD e VDDH entrambi a 3V3, DCCH libero, VBUS libero se non si usa USB, tutte le GND collegate",
  "19 VCC e 23 VDH su 3V3, 25 DCH e 27 VBS non collegati, 5/21/24 GND", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B04", "E73: componenti interni (induttore DCDC, condensatori, quarzi)", "Ricerca nel manuale Ebyte", ["E73_MAN"],
  "Sapere se REG1 DCDC si può abilitare e se serve disaccoppiamento esterno", "Manuale non leggibile (PDF cifrato). XL1/XL2 esposti: nessun quarzo 32 kHz interno, coerente con LFRC", "NON_VERIFICABILE", "media",
  "Firmware: lasciare il DCDC spento finché non si conferma l'induttore interno; in caso positivo abilitarlo (consumo CPU quasi dimezzato)", "")
T("B05", "W25N02KVZEIR: piedinatura WSON-8", "Simbolo LCSC, def.py e netlist contro la piedinatura Winbond standard WSON-8", ["LIB", "DEF", "NET", "JLC_NAND"],
  "1 /CS, 2 DO(IO1), 3 /WP(IO2), 4 GND, 5 DI(IO0), 6 CLK, 7 /HOLD(IO3), 8 VCC, EP GND",
  "Coincide: CS->QSPI_CS, IO1, IO2, GND, IO0, SCK, IO3, 3V3, EP->GND; package JLC WSON-8-EP 6x8 come l'impronta", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B06", "MSM261DGT003: pin e porta", "Datasheet (testo estratto) contro simbolo, def.py e netlist", ["DS_MIC", "LIB", "DEF", "NET"],
  "1 VDD, 2/5 GND, 3 DATA, 4 CLK, 6 L/R; top-port; VDD 1,6-3,6 V",
  "Coincide; datasheet: 'omnidirectional, Top-ported', 4 x 2 x 1,1 mm, foro Ø0,65; MK1 L/R=GND, MK2 L/R=3V3, DATA e CLK in comune (configurazione stereo del datasheet)", "PASS", "alta", "", "pdf_testo.py")
T("B07", "MCP73831T-2ACI/OT: pin, corrente e tensione", "Simbolo e reti contro la piedinatura SOT-23-5 del caricatore; formula IREG = 1000 V / RPROG", ["LIB", "DEF", "NET", "JLC_CHG", "MCP_DS"],
  "1 STAT, 2 VSS, 3 VBAT, 4 VDD, 5 PROG; 50 mA con 20 kOhm; 4,20 V ('-2')",
  "Coincide; 1000/20 k = 50 mA (0,45-0,8 C per celle 60-110 mAh); 4,20 V adatta a LiPo standard (valori del datasheet da memoria: PDF Microchip cifrato)", "PASS", "media", "", "test_C_simbolo_impronta.py")
T("B08", "MCP73831: livello dell'uscita STAT su P0.07", "Tipo di uscita STAT (MCP73831 tri-state, MCP73832 open-drain) contro l'alimentazione del pin nRF", ["MCP_STAT", "MCP_DS", "DEF", "PINOUT"],
  "Su un GPIO a 3,3 V serve un'uscita open-drain o un livello <= VDD+0,3 V",
  "L'MCP73831 ha STAT tri-state alimentato da VDD = VBUS = 5 V: a carica completa porta P0.07 a ~5 V (VOH ~ VDD-0,3 V) direttamente, senza resistenza: supera il massimo assoluto del nRF52840 (VDD+0,3 V) e inietta corrente nel 3V3 attraverso il diodo di protezione. pinout.md lo tratta come open-drain con pull-up (abitudine del TP4054)",
  "FAIL", "alta",
  "Senza toccare i Gerber: sostituire U3 con MCP73832T-2ACI/OT (LCSC C38066, stesso SOT-23-5 e piedinatura, STAT open-drain, Extended come prima) e usare il pull-up interno di P0.07 (basso = in carica, alto = finita o senza 5V; VBUS_SENSE distingue). Aggiornare def.py/BOM e pinout.md", "")
T("B09", "XC6206P332MR: piedinatura SOT-23", "Simbolo e reti contro la piedinatura Torex (MR: 1 VSS, 2 VOUT, 3 VIN)", ["LIB", "DEF", "NET", "JLC_LDO"],
  "1 GND, 2 3V3, 3 VSYS", "1 GND, 2 Vout=3V3, 3 Vin=VSYS", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B10", "AO3401A e AO3400A: G/S/D e soglie", "Simbolo (1 G, 2 S, 3 D) e reti; soglie dei datasheet AOS", ["LIB", "DEF", "JLC_Q1", "JLC_Q4"],
  "Q1 P-MOS: S=VBAT, D=VSYS, G=LATCH_G; Q4 N-MOS: S=GND, D=MOTOR_N, G=MOTOR_G",
  "Coincide. Q4 Vgs 3,3 V >> Vth (0,65-1,45 V); Q1 Vgs = -VBAT (-3,5...-4,2 V) >> |Vth| (0,5-1,3 V)", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B11", "2N7002DW-7-F: piedinatura SOT-363", "Gruppi di pin del simbolo LCSC ({1,2,6} e {4,5,3}) contro le reti; piedinatura Diodes S1-G1-D2-S2-G2-D1", ["LIB", "DEF", "JLC_Q2"],
  "FET A: S=GND, G=LATCH_ON, D=LATCH_G; FET B: S=GND, G=RST_G, D=NRESET",
  "Coincide (1 S, 2 G, 6 D; 4 S, 5 G, 3 D). Il simbolo LCSC scambia le etichette 1/2 dei due FET, ma i transistor sono identici: nessun effetto", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B12", "TTP223-BA6-TD: piedinatura e opzioni", "Simbolo e reti contro la tabella pin TTP223-BA6", ["LIB", "DEF", "TTP_DS", "JLC_TTP"],
  "1 Q, 2 VSS, 3 I, 4 AHLB=0 (attivo alto), 5 VDD, 6 TOG=0 (diretto); Cs tra I e VSS",
  "Coincide: Q->TOUCH_A/B, AHLB e TOG a GND, VDD 3V3 (range 2,0-5,5 V), C12/C13 10 pF tra pad e GND", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("B13", "MHPA1010RGBDT: anodo comune e colori", "Simbolo LCSC contro reti; datasheet MEIHUA cercato", ["LED_EASYEDA", "JLC_LED", "LED_DS", "DEF"],
  "pad dell'anodo su LEDx_A, catodi R/G/B sui GPIO giusti",
  "Rete coerente col simbolo LCSC (1 +, 2 R-, 3 G-, 4 B-); anodo comune confermato da JLC. Datasheet solo immagini: assegnazione dei pad non confermata da fonte indipendente", "WARN", "bassa",
  "Controllare nell'anteprima JLC il segno di polarità; se i colori risultano scambiati si corregge nel firmware (non serve rifare la scheda, purché il pad 1 sia l'anodo)", "")
T("B14", "1N4148WS: polarità", "Impronta SOD-323 (pad 1 col segno di catodo) e simbolo (1 K, 2 A) contro le reti", ["LIB", "DEF"],
  "D4 K=VSYS (ricircolo), D5 K=VBUS_D, D6 K=LATCH_ON", "Coincide per D4, D5, D6", "PASS", "alta", "", "test_C_simbolo_impronta.py")

# ---------------- C ----------------
T("C01", "Simbolo = impronta = def = netlist = pcb", "Per ogni componente: numeri pin del simbolo vs pad dell'impronta, reti di def.py vs netlist kicad-cli vs pad del pcb, posizione/rotazione/impronta/lato", ["LIB", "DEF", "NET", "PCB"],
  "nessuna differenza", "0 differenze su 53 riferimenti", "PASS", "alta", "", "test_C_simbolo_impronta.py")
T("C02", "Geometria delle impronte contro i disegni meccanici", "Pad/passo/corpo delle impronte LCSC contro i disegni dei datasheet", ["LIB", "DS_MIC", "LED_DS", "E73_MAN"],
  "impronte coerenti coi disegni", "SOT-23/-5/-6, SOT-363, SOD-323, 0402, WSON-8 (EP 3,4 x 4,3) con misure standard plausibili. MIC: impronta 'LMD4020T261-OC3' ma è quella assegnata da LCSC al C48227730; LED ed E73: disegni non leggibili (PDF a immagini/cifrati)", "NON_VERIFICABILE", "media",
  "Nell'anteprima JLC controllare che i pad coincidano col modello per MK1/MK2, D1-D3 e U1", "")
T("C03", "Modelli 3D allineati alle impronte", "Ingombro dei .wrl contro courtyard", ["3D", "PCB"], "modelli centrati e coerenti",
  "Tutti coerenti; U1 18 x 13 x 3,0 mm (origine non centrata, coincide col courtyard), MIC 4 x 2 x 1,16, LED 1 x 1 x 0,92, WSON 0,75 mm", "PASS", "bassa", "", "")

# ---------------- D ----------------
T("D01", "Latch: accensione, tenuta, spegnimento", "Calcolo a mano su R2 1M, Q2A, D6, R3 100k, R4 1M, C14 1uF", ["DEF", "NET"],
  "5V accende, HOLD mantiene, HOLD basso spegne in < ~1 s, reset regge ~0,5 s",
  "Con 5V: LATCH_ON = 4,3 V x 1M/1,1M = 3,9 V, tau 91 ms -> Q2A on dopo ~50 ms. Con HOLD 3,3 V: LATCH_ON ~2,8-2,9 V > Vth max 2,5 V (basta 4 uA da R2). HOLD basso/reset: tau R4·C14 = 1 s, Q2A si spegne dopo ~0,4-0,8 s secondo Vth (1,0-2,5 V): coerente con '~0,5 s'", "PASS", "alta", "", "")
T("D02", "Latch: corrente da spento", "Somma delle perdite a batteria con latch aperto", ["DEF", "JLC_CHG", "JLC_Q1", "JLC_Q2"],
  "< ~5 uA", "Tipico < 2-3 uA (scarica del caricatore MCP7383x senza VDD ~1-2 uA + perdite MOS nA). Caso limite: IDSS max di Q2A da datasheet (1 uA a 60 V) x R2 1M = 1 V su Q1, vicino alla Vth min dell'AO3401A (0,5 V): a 4 V la perdita reale è di nA, ma R2 1M lascia poco margine", "WARN", "bassa",
  "Al collaudo misurare la corrente da spento; se Q1 conduce in parte, R2 a 470k", "")
T("D03", "Batteria a 0 V, scollegata, precondizionamento", "Analisi del caricatore con carico di sistema collegato direttamente a VBAT", ["DEF", "MCP_DS"],
  "si ricarica sempre; senza batteria non danneggia",
  "Senza batteria e con 5V: il nRF parte dall'uscita del caricatore (utile al banco, max 50 mA, motore escluso). Con cella sotto ~3 V il caricatore precondiziona a ~5 mA mentre il sistema (acceso dal 5V via D5) ne assorbe ~5: la cella può non risalire mai", "WARN", "media",
  "Firmware: con VBUS presente e VBAT < 3,1 V entrare in risparmio (radio, mic e LED spenti) finché la cella non risale", "")
T("D04", "Impulso di reset dal 5V su P0.18", "C10 100 nF, R5 100k, Q2B", ["DEF", "NET"],
  "impulso di decine di ms, poi rilascio", "tau 10 ms: NRESET basso ~7-16 ms (Vth 2,5-1,0 V), poi RST_G -> 0 e reset rilasciato; allo stacco del 5V il gate va a -5 V (Vgs max ±20 V). Avviene prima della chiusura del latch (~50 ms): se era spento si accende pulito", "PASS", "media",
  "Firmware: abilitare P0.18 come reset in UICR (CONFIG_GPIO_AS_PINRESET)", "")
T("D05", "Partitore VBAT 1M/1M per il SAADC", "Impedenza e range contro il SAADC del nRF52840", ["DEF"],
  "<= 800 kOhm con TACQ 40 us; tensione nel range", "500 kOhm + C11 100 nF (serbatoio), 4,2 V -> 2,1 V < 3,6 V fondo scala (gain 1/6, rif. 0,6 V); 2,1 uA a latch chiuso. Misura VSYS (dopo Q1), praticamente VBAT", "PASS", "media",
  "Firmware: TACQ 40 us", "")
T("D06", "Partitore VBUS 100k/100k", "Livello su P0.28", ["DEF"], "<= VDD+0,3 V", "5,0-5,25 V -> 2,5-2,6 V: ok a nRF acceso. Con cella scarica (3V3 assente) e 5V presente inietta ~40 uA nel pin non alimentato (Thevenin 50k)", "WARN", "bassa",
  "Accettabile; eventualmente R7 a 47k nei lotti futuri", "")
T("D07", "LDO XC6206: dropout, picco, condensatori", "Calcolo con dropout tipico e carichi di picco", ["DEF", "JLC_LDO", "PCB"],
  "3,3 V stabili fino a 3,5 V di batteria; Cin/Cout >= 1 uF", "Picco ~55 mA (radio 17 mA + NAND ~25-35 mA + mic ~1,5 mA + CPU): dropout ~60-140 mV, regola fino a ~3,4-3,45 V. Cout 1 uF + 4,7 uF vicini; Cin C3 1 uF su VSYS a ~7 mm dal pin di ingresso", "WARN", "bassa",
  "Nessuna per l'ordine; al collaudo verificare l'assenza di oscillazioni sul 3V3", "")
T("D08", "LED: correnti reali", "(VSYS - Vf - VOL)/470 con Vf JLC", ["JLC_LED", "DEF"], "colori visibili su tutta la scarica, corrente entro il GPIO",
  "Rosso: 2,8 mA a 3,5 V, 4,3 mA a 4,2 V (serve high-drive H0 per il pieno). Verde/blu (Vf 2,5-3,5 V, tip. ~3,0): ~0,8 mA a 3,5 V, ~2,3 mA a 4,2 V; con Vf al massimo a 3,5 V restano spenti. Catodo da spento a ~2,0-2,8 V < VDD: nessuna iniezione", "WARN", "bassa",
  "Firmware: drive H0S1 sui catodi; aspettarsi verde/blu fiochi sotto ~3,6 V", "")
T("D09", "Motorino: MOSFET, diodo, pull-down", "Reti di Q4, D4, R10, M1P/M1N", ["DEF", "NET"], "MOS a basso lato, diodo di ricircolo, gate a massa da spento",
  "Q4 AO3400A tra MOTOR_N e GND, D4 catodo su VSYS anodo su MOTOR_N (ricircolo corretto), R10 100k pull-down, piste 0,2 mm sufficienti per ~80 mA", "PASS", "media",
  "Firmware: PWM per non superare i ~3 V nominali del motorino con la cella a 4,2 V", "")
T("D10", "Tocco TTP223", "Alimentazione, uscita, condensatori", ["DEF", "PCB", "TTP_DS"], "3V3, uscita CMOS attiva alta, 100 nF locale",
  "3V3 e uscite su P0.08/P0.31 ok; Cs 10 pF. Nessun 100 nF dedicato: U6 ha C7 a ~1,7 mm, U5 ha il condensatore 3V3 più vicino (C4/C5) a ~7 mm", "WARN", "bassa",
  "Al collaudo controllare falsi tocchi; nei lotti futuri un 100 nF accanto a U5", "")
T("D11", "Microfoni: L/R, clock, disaccoppiamento", "Datasheet MSM261DGT003 contro rete e clock PDM del nRF52840", ["DS_MIC", "DEF"],
  "L/R opposti, clock nel range di un modo, 100 nF per mic",
  "MK1 L/R=GND, MK2 L/R=3V3, C8/C9 100 nF vicini. Range clock: low-power 150-900 kHz, standard 1,1-4,0 MHz; il PDM del nRF (1,000/1,032 default/1,067/1,231/1,280/1,333 MHz) cade nel buco 0,9-1,1 MHz con i valori bassi", "WARN", "media",
  "Firmware: clock PDM 1,280 MHz (rapporto 80 -> 16 kHz) o 1,231/1,333; mai il default 1,032 MHz", "")
T("D12", "NAND: pull-up e compatibilità QSPI", "Reti di CS/WP/HOLD; funzionamento del QSPI nRF con una SPI-NAND", ["DEF", "JLC_NAND"],
  "CS alto all'accensione; IO2/IO3 non flottanti", "Nessun pull-up su CS/WP/HOLD: finché il firmware non configura i pin la NAND vede ingressi flottanti (nessun danno, nessun clock). Il QSPI nRF è pensato per NOR: la NAND (page read 13h + lettura buffer) richiede istruzioni personalizzate o SPIM", "WARN", "bassa",
  "Firmware: CS alto subito al boot; prevedere driver SPI-NAND (QSPI con CINSTR o SPIM)", "")
T("D13", "Stima consumi ~4,6 mA", "Somma dei consumi dai datasheet", ["DS_MIC", "DOC"], "coerente", "Mic 2 x ~0,7 mA, PDM+CPU per LC3 stereo con LDO interno (DCDC non confermato) ~2-3 mA, radio a sync rare, NAND a scatti: 4,6 mA plausibile ma senza margine se il DCDC non c'è", "WARN", "bassa",
  "Misurare al collaudo; con la 381620 (110 mAh) l'autonomia sale a ~20 h", "")
T("D14", "Carica: terminazione con il sistema acceso", "Carico di sistema in parallelo alla cella", ["DEF", "MCP_DS"], "la carica termina",
  "Il sistema (~4,6 mA) è sulla cella: con terminazione a C/10 ~5 mA il caricatore può non terminare e tenere la cella a 4,20 V in CV", "WARN", "bassa",
  "Firmware: in basetta ridurre i consumi; accettabile per la v0.1", "")
T("D15", "Contatti esposti: ESD, sudore, inversione", "Reti di J1-J4", ["DEF", "DOC"], "protezione sui pin esposti",
  "SWDIO/SWCLK vanno diretti ai pin nRF e VBUS al caricatore senza TVS né resistenze; se la basetta tocca i contatti a rovescio, 5 V su SWCLK", "WARN", "media",
  "Basetta con polarità meccanica certa (magneti); nei lotti futuri valutare resistenze serie da 100-470 Ohm su SWD", "")

# ---------------- E ----------------
T("E01", "Riferimenti in BOM e CPL", "Insieme dei ref di def.py (esclusi i montati a mano) contro BOM, CPL, jlc/BOM", ["DEF", "BOM", "CPL"],
  "43 componenti SMD in entrambi, nessun extra", "43 in CPL e in BOM (19 righe), jlc/ BOM uguale; J1-J4, BT1P/N, M1P/N, TPA/TPB esclusi", "PASS", "alta", "", "test_E_bom_cpl.py")
T("E02", "Codici LCSC, package, Basic/Extended", "Pagine JLC dei codici", ["JLC_E73", "JLC_NAND", "JLC_MIC", "JLC_CHG", "JLC_TTP", "JLC_LED", "JLC_Q2", "JLC_LDO", "JLC_Q1", "JLC_Q4", "JLC_D", "JLC_C5", "BOM"],
  "codici e package giusti, 7 Extended", "Tutti i codici corrispondono al pezzo e al package; Extended: E73, W25N02KV, MSM261, MCP73831, TTP223, MHPA1010, 2N7002DW = 7; LDO, AO3401A, AO3400A Basic. Passivi non ricontrollati (JLC ha limitato le richieste)", "PASS", "media", "", "test_E_bom_cpl.py")
T("E03", "E73 montabile con Economic PCBA?", "Pagina JLC del C356849", ["JLC_E73", "LEGGIMI"], "Economic PCBA",
  "JLC indica 'PCBA Type: Standard Only' e 'X-ray Inspection: Required' per l'E73: con Economic PCBA il modulo non dovrebbe essere accettato; Standard PCBA costa di più (spese fisse) e il preventivo da 97 € potrebbe non valere", "FAIL", "alta",
  "Prima di pagare: verificare nel carrello JLC che il tipo di PCBA sia accettato con U1; se passa a Standard, rifare il preventivo (e decidere) prima di confermare", "")
T("E04", "Coordinate CPL", "CPL contro pcbnew e contro un pos esportato ora da kicad-cli", ["CPL", "PCB"], "uguali (Y negativa come nei Gerber)", "Uguali per tutti i 43", "PASS", "alta", "", "test_E_bom_cpl.py")
T("E05", "Rotazioni CPL e pin 1", "Rotazione CPL contro pcb (+180 documentato per MK1/MK2) e pin 1 delle impronte", ["CPL", "PCB", "LIB", "DOC"],
  "rotazioni JLC corrette", "CPL = rotazione KiCad (impronte LCSC, convenzione JLC) per tutti tranne MK1/MK2 (+180, già verificato in anteprima il 21/11). Non verificabile da qui l'anteprima per gli altri polarizzati", "WARN", "media",
  "Nell'anteprima JLC controllare il pin 1 di U1 (antenna verso il bordo), U2 (WSON), U3, U4, U5, U6, Q1, Q2 (SOT-363), Q4, D1-D3 (LED), D4-D6 (catodo), MK1/MK2", "test_E_bom_cpl.py")
T("E06", "Lato e componenti esclusi", "Layer CPL, attributi DNP/BOM/pos nel pcb", ["CPL", "PCB", "LEGGIMI"], "tutti Top; montati a mano esclusi",
  "Tutti Top; J1-J4 esclusi dalla BOM e dal CPL (THT esclusi), piazzole retro escluse da BOM e posizioni", "PASS", "media", "", "test_E_bom_cpl.py")

# ---------------- F ----------------
T("F01", "Courtyard: sovrapposizioni e bordo", "DRC (poligoni) + controllo indipendente sui rettangoli dei courtyard", ["PCB"], "nessuna sovrapposizione, dentro la scheda",
  "DRC: 0 sovrapposizioni. Sui rettangoli solo U6/C7 si toccano di 0,08 mm (il poligono reale di U6 non sovrapposto). U1 sporge di 0,02-0,045 mm dal bordo inferiore: voluto (antenna a filo)", "PASS", "media", "", "test_F_meccanica.py")
T("F02", "Altezze dei componenti", "Modelli 3D LCSC e datasheet", ["3D", "DS_MIC", "E73_MAN"], "componente più alto noto",
  "U1 E73 3,0 mm (solo dal modello LCSC 'H3.0', datasheet non leggibile), MIC 1,1 (datasheet), SOT-23-5 1,25, LED 0,92, WSON 0,75", "WARN", "media",
  "Misurare l'E73 all'arrivo (o chiedere a Ebyte): decide lo spessore", "")
T("F03", "Impilamento negli 8 mm (e 9 mm)", "E73 + scheda 1,0 + batteria, dove si sovrappongono (y 20-32,8)", ["3D", "PCB", "DOC"], ">= 0,5 mm di resina per faccia",
  "381620: 3,0 + 1,0 + 3,8 = 7,8 mm -> 0,1 mm per faccia a 8 mm (insufficiente), 0,6 mm a 9 mm. Cella 3,5 mm: 7,5 mm -> 0,25 mm a 8 mm, 0,75 mm a 9 mm. Il motorino (2 mm) è fuori dall'E73 e non conta", "FAIL", "media",
  "Non riguarda i Gerber: con E73 da 3 mm il monolite va a 9 mm (o cella <= 3,0 mm). Decidere prima di disegnare i gusci", "test_F_meccanica.py")
T("F04", "Pianta inferiore: batteria, motorino, keepout", "Ipotesi: batteria centrata che finisce a 32,8 mm, motorino Ø8 sotto la zona A sotto le teste dei target", ["PCB", "DOC"],
  "nessuna sovrapposizione, batteria fuori dal keepout",
  "381620: batteria 12,8-32,8 mm, motorino 3,8-11,8 mm (spazio 9 mm per 8): ci stanno, nessuna sovrapposizione, batteria fuori dal keepout. Margini 0,5-1 mm", "PASS", "media", "", "test_F_meccanica.py")
T("F05", "Piazzole a mano sul retro accessibili", "Piazzole BT1P/BT1N, TPA/TPB, M1P/M1N contro batteria e motorino", ["PCB"], "piazzole fuori dalla batteria",
  "BT1P/BT1N (y 12,6-14,4) restano sotto la batteria di ~1,6 mm (381620) o ~0,6 mm (19 mm); TPA/TPB sotto di 0,15 mm. M1P/M1N liberi. Non si può allungare la batteria verso il basso (keepout)", "WARN", "media",
  "Saldare i fili prima di posare la cella, lato PCM in alto e fili ripiegati; oppure nei lotti futuri spostare BT+/BT- ai fianchi del motorino", "test_F_meccanica.py")
T("F06", "LED nella fessura frontale", "Posizioni D1-D3 contro una fessura da 10 mm centrata", ["PCB", "DOC"], "dentro, centrati, stesso y",
  "x 5,25/8,25/11,25 (passo 3,0), ingombro 4,7-11,8 mm dentro 3,25-13,25; tutti a y 8,5; emissione verso il lato componenti = fronte", "PASS", "media", "", "test_F_meccanica.py")
T("F07", "Porte dei microfoni", "Orientamento della porta (top-port) e cosa c'è sopra", ["DS_MIC", "PCB"], "porte libere verso la faccia giusta",
  "Entrambe le porte sono sul coperchio, rivolte verso il FRONTE. MK1 (14,6; 16,4) ok per il foro frontale. MK2 (8,25; 1,35) guarda il fronte: il canalino verso la faccia superiore deve piegare a 90° nel guscio. Nessun componente sopra", "WARN", "bassa",
  "Gusci: canale a L per MK2; sigillare le porte durante la colata (la resina nel foro distrugge il mic)", "")
T("F08", "Contatti J1-J4: fori e target", "Fori 1,0 mm (pad 1,6) contro i target 7,0 mm; profondità dal retro della scheda alla faccia posteriore", ["PCB", "DOC", "GBR"],
  "coda che entra nel foro; altezza del target = spazio dietro la scheda",
  "Fori 1,0 mm PTH (anello 0,3), coppie a x 1,8/4,6 e 11,9/14,7 sul bordo alto, distanza dai componenti sopra >= 0,008 mm (C10/J3, D5/J1-J2: saldatura a mano stretta). Diametro coda sconosciuto. Dietro la scheda servono ~4,3 mm (batteria 3,8 + resina): un target da 7,0 mm sporge di ~2,7 mm", "WARN", "alta",
  "Prima di pagare: avere dal venditore diametro coda e altezza; se la coda > 0,9 mm allargare i fori (unica modifica che tocca i Gerber); scegliere target ~4-4,5 mm o accettare la sporgenza", "test_F_meccanica.py")
T("F09", "Anello e boccola", "Spazio libero sopra la zona A", ["PCB", "DOC"], "volume riservato per la boccola", "Nessuno spazio riservato sulla scheda: MK2 è al centro del bordo alto (y 0,3-2,4) e J1-J4 occupano il resto; con 41 mm di monolite restano ~1,5 mm di resina sopra la scheda se centrata", "WARN", "media",
  "Gusci: spostare la scheda verso il basso (antenna a ~0,5 mm dal fondo) per avere ~2,5 mm sopra, o boccola laterale; da decidere nel CAD del guscio", "")
T("F11", "Ingombro reale: corpi sopra pad altrui (courtyard LCSC = solo corpo)", "pcbnew: poligono della courtyard (corpo) di ogni componente contro i poligoni dei pad degli altri; corpi a meno di 0,2 mm",
  ["PCB", "LIB"], "nessun corpo sopra pad altrui", "", "IN_ATTESA", "media", "Nell'anteprima/DFM JLC controllare C7 accanto a U6; nei lotti futuri allontanarlo di 0,2 mm", "test_F_ingombri.py")
T("F10", "Keepout antenna e antenna a filo", "Gerber dei 4 strati di rame: oggetti in y > 32,8 mm; posizione del modulo", ["GBR", "PCB", "E73_MAN"], "nessun rame oltre i pad del modulo; antenna sul bordo",
  "F.Cu: solo i pad 1, 2, 41, 42, 43 del modulo (non collegati); In1, In2, B.Cu: 0 oggetti. Modulo a filo del bordo inferiore (38,02 mm)", "PASS", "alta", "", "test_G_gerber.py")

# ---------------- G ----------------
T("G01", "Strati Gerber presenti", "Elenco file del zip e gbrjob", ["GBR"], "4 rame, 2 maschere, 2 serigrafie, pasta top, Edge_Cuts, PTH, NPTH",
  "Tutti presenti (nessuna pasta sotto: corretto, piazzole a mano)", "PASS", "alta", "", "test_G_gerber.py")
T("G02", "Fori e via", "Conteggio nel drill PTH/NPTH contro il pcb", ["GBR", "PCB"], "via = pcb", "114 via 0,25 + 4 fori 1,0 mm; NPTH vuoto; pcb 114 via (i documenti dicono 115)", "PASS", "media", "", "test_G_gerber.py")
T("G03", "Spessore e strati dichiarati", "LEGGIMI e gbrjob", ["LEGGIMI", "GBR"], "4 strati, 1,0 mm", "LEGGIMI: 4 strati 1,0 mm, HASL senza piombo; gbrjob: LayerNumber 4, BoardThickness 1.0, Size 16,55 x 38,05 (con lo spessore della linea)", "PASS", "media", "", "")
T("G04", "Serigrafia «notªpad v0.1» sul retro", "Testo nel pcb e tratti nel Gerber B_Silkscreen", ["PCB", "GBR"], "sul retro, speculare, carattere ª presente",
  "B.Silkscreen, speculare, a (8,25; 22,5), 110 tratti continui su 7,5 mm. Che la ª sia resa bene non si vede senza un visualizzatore; 0,8/0,12 mm sotto il consiglio JLC", "WARN", "bassa",
  "Guardare il B_Silkscreen nel visualizzatore Gerber di JLC", "test_G_gerber.py")
T("G05", "Serigrafia sui pad", "DRC severo (silk_over_copper attivo) ed export con --subtract-soldermask", ["PCB", "GBR"], "nessuna", "Nessuna violazione", "PASS", "media", "", "test_A_drc_severo.py")
T("G06", "Fiducial e note Economic PCBA", "Presenza di fiducial e note nel LEGGIMI", ["PCB", "LEGGIMI"], "non obbligatori per JLC", "Nessun fiducial (JLC non li richiede per Economic); note DNP e controllo rotazioni presenti", "PASS", "bassa", "", "")

# ---------------- H ----------------
T("H01", "collegamenti.csv = netlist", "Confronto rete per rete", ["COLL", "NET"], "identici", "Identici", "PASS", "media", "", "test_H_documenti.py")
T("H02", "pinout.md = def.py", "Tabella del pinout contro i pad E73 di def.py", ["PINOUT", "DEF"], "identici", "Identici (segnali, pad, LED, SWD)", "PASS", "media", "", "test_H_documenti.py")
T("H03", "Numeri nei documenti", "Via, misure, valori in CLAUDE.md/STATO.md contro pcb", ["DOC", "PCB"], "coerenti",
  "CLAUDE.md e STATO.md dicono 115 via, il pcb e il drill ne hanno 114; il resto (misure, C14, C4/C5, R11-R13) coerente", "WARN", "bassa", "Correggere 115 -> 114", "test_H_documenti.py")
T("H04", "File superati", "montaggio_a_mano.csv e kicad/anteprima.json contro STATO e pcb", ["MANO", "DOC", "PCB"], "aggiornati",
  "montaggio_a_mano.csv cita la cella ~3,5 x 16 x 19 (60 mAh) e 'pin dorati' invece di 381620 e target; anteprima.json ha posizioni della scheda da 35 mm (BT1P y 11,2 invece di 13,5)", "WARN", "bassa", "Aggiornare o segnare come superati", "test_H_documenti.py")
T("H05", "Descrizione di STAT in pinout.md", "Testo contro il componente montato", ["PINOUT", "MCP_STAT"], "coerente col caricatore",
  "Descrive STAT come open-drain con pull-up interno ('ex CHRG del TP4054'): vero per MCP73832, non per MCP73831 (vedi B08)", "WARN", "media", "Si risolve con la correzione di B08", "test_H_documenti.py")

SINTESI = ("Scheda elettricamente pulita: ERC/DRC 0 anche con le regole ignorate riattivate, parità 0, Gerber identici al pcb, "
 "simbolo-impronta-netlist-documenti coerenti, keepout antenna vuoto su tutti gli strati, BOM/CPL completi e con 7 Extended. "
 "NON ordinabile così com'è per due motivi: (1) B08 l'MCP73831 porta STAT a ~5 V su P0.07 (uscita tri-state alimentata dal 5V): "
 "si risolve senza toccare i Gerber montando l'MCP73832T-2ACI/OT (C38066, stessa impronta, open-drain); "
 "(2) E03 JLC dichiara l'E73 'Standard Only' con raggi X: il preventivo Economic da 97 € va riconfermato nel carrello prima di pagare. "
 "Prima di pagare va anche chiusa F08 (diametro coda e altezza dei target: unico punto che può cambiare i Gerber, i fori da 1,0 mm). "
 "F03 (8 mm non bastano con E73 da 3 mm e cella da 3,8 mm: servono 9 mm) e gli altri WARN riguardano gusci, firmware e collaudo, non la scheda.")
STACK = {"spessore_mm": 8, "strati": [
    {"nome": "guscio/resina fronte (resta 0,1 mm: insufficiente)", "da_mm": 0.0, "a_mm": 0.1},
    {"nome": "U1 E73 (3,0 mm dal modello LCSC; LED 0,9, mic 1,1)", "da_mm": 0.1, "a_mm": 3.1},
    {"nome": "scheda 4 strati 1,0 mm", "da_mm": 3.1, "a_mm": 4.1},
    {"nome": "batteria 381620 3,8 mm (motorino 2,0 mm altrove, sotto la zona A)", "da_mm": 4.1, "a_mm": 7.9},
    {"nome": "guscio/resina retro (resta 0,1 mm: insufficiente)", "da_mm": 7.9, "a_mm": 8.0}],
  "nota": "A 9 mm restano 0,6 mm per faccia (0,75 con cella da 3,5 mm). Target J1-J4: servono ~4,3 mm dietro la scheda, non 7,0."}
