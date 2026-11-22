# Stato del progetto

**Ultimo aggiornamento:** 22/11/2026 (sera), Fase 1: scheda v0.1 verificata, ordine JLC in attesa dell'E73 e del tipo di PCBA; iniziati i test di firmware e app su una XIAO nRF52840 Sense

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), libreria KiCad dai codici LCSC, scheda 4 strati 1,0 mm 16,5 × 38 mm generata da script (ERC 0, DRC 0, parità 0). Export in `kicad/fab_out/jlcpcb/`.
- **Verifica pre-ordine automatica (22/11):** `verifica/`, con 69 test in 8 aree (A regole/DRC, B pinout vs datasheet, C simbolo↔impronta, D circuito, E BOM/CPL, F meccanica, G Gerber, H documenti). Ogni dato è incrociato su almeno 2 fonti e ogni test ha uno script ripetibile in `verifica/script/`. Esiti in `verifica/risultati.json`; la pagina `verifica/index.html` è generata da `genera_pagina.py`, con avanzamento in diretta. È pubblicata come artefatto privato (link nella conversazione, non nel repo).
  - Giro 1: 37 PASS, 26 WARN, 3 FAIL, 2 N/V. Giro 2, dopo il cambio caricatore: 39 PASS, 26 WARN, 2 FAIL, 2 N/V. Giro 3, con fori 1,1 e 9 mm: **41 PASS, 25 WARN, 1 FAIL (E03), 2 N/V**, nessun WARN alto.
- **Caricatore:** MCP73831 → **MCP73832T-2ACI/OT (C38066)**, perché lo STAT tri-state del 31, alimentato dal 5V, portava P0.07 a ~5 V. Stessa impronta: cambiano solo BOM e valori, Gerber invariati.
- **Monolite 9 mm** (a 8 mm restavano 0,1 mm di resina per faccia).
- **Contatti J1–J4:** target 2,0 × 4,0 mm (coda Ø0,9 × 2, spalla Ø2 × 0,5, corpo Ø1,5 × 4,0), la punta esce di 0,1 mm dal retro. Fori allargati a **1,1 mm** (piazzola 1,6). Cambiano solo i file di foratura; DRC con parità pulito. Disegno in sezione: `verifica/target_sezione.png`.
- **Comunicazione:** sezione "Pre-order verification" nel README e "Checked before we pay" nella pagina. 8 sfondi per cellulare in `sfondi/` (iPhone e Android, spazio "Sponsor" separato nel sorgente), approvati tutti e 8 e pubblicati su pagina e README.
- **Firmware di prova** (`firmware/xiao-prova/`, XIAO nRF52840 Sense con batteria, Arduino + Bluefruit): registra a 16 kHz in IMA ADPCM, anello di 512 settori sulla QSPI da 2 MB (~4 min), sincronizzazione all'80%, ACK + CRC, spegnimento a 3,50 V, watchdog. Compila (16 % flash, 13 % RAM); **non ancora caricato né provato sulla scheda**.
- **App di prova** (`app/`): PWA per Windows solo locale (`avvia.cmd` → localhost:8787, Edge/Chrome, Web Bluetooth, IndexedDB), con auto-sincronizzazione all'80%, ascolto ed export WAV. Prove del formato `node app/test/adpcm.test.mjs` superate; Bluetooth vero non provato.
- Preventivo JLC precedente: 97 € per 2 schede montate (Economic PCBA), E73 in pre-order verso My Inventory.

## In corso
- **E03, bloccante:** sulla pagina JLC l'E73 (C356849) è «Standard Only» con X-ray. Bisogna verificare nel carrello se l'Economic PCBA lo accetta; se no, rifare il preventivo con lo Standard PCBA.
- Attendere l'E73 in My Inventory, poi selezionarlo su U1, controllare l'anteprima (rotazioni E05, DFM: corpo di U6 su un pad di C7, F11) e pagare (coupon fino al **2/12**).
- Primo collaudo della XIAO: caricare `firmware/xiao-prova`, collegare l'app, verificare registrazione, sincronizzazione all'80%, qualità dell'audio e velocità di scarico.
- Risposte degli sponsor.

## Prossimi passi
1. Chiudere E03 nel carrello JLC e pagare.
2. Ordinare i pezzi fuori JLC: batteria 381620 con PCM, target 2,0 × 4,0 mm, motorini 0820, resina, stagno.
3. Disegnare i due mezzi gusci SLA a **9 mm**, con canale per MK2, sigillatura delle porte dei microfoni e boccola dell'anello (F07, F09).
4. Firmware, da ricordare (dalla verifica): clock PDM 1,280 MHz, DCDC spento finché non è confermato, risparmio con 5V presente e VBAT < 3,1 V, pull-up interno su STAT.
5. Basetta con pogo e magneti a polarità certa (D15: SWD senza ESD).

## In pausa (per scelta dell'utente)
- Firmware per la scheda v0.1 (E73, NAND, LC3) e app mobile: dopo i test sulla XIAO. Pinout in `docs/pinout_v0.1.md`.
- Cartella locale `ncs` (toolchain Nordic parziale).

## Abbandonato
- XIAO/Seeed, PCBWay, ALLPCB, NextPCB per la produzione: solo JLC. Montaggio in casa.

## Costi
- 2 schede montate: 97 € (da riconfermare se serve lo Standard PCBA). Pezzi fuori JLC ~40–60 €. Totale v0 ~140–170 €.
- Extended JLC: 7 componenti × 3 $ a ordine (l'MCP73832 sostituisce l'MCP73831, il conto non cambia).
