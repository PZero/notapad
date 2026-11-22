# Stato del progetto

**Ultimo aggiornamento:** 22/11/2026 (fine sessione), Fase 1: scheda v0.1 verificata, ordine JLC in attesa dell'E73 e del tipo di PCBA; catena XIAO → app provata con l'hardware vero, trascrizione Whisper aggiunta all'app

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), libreria KiCad dai codici LCSC, scheda 4 strati 1,0 mm 16,5 × 38 mm generata da script (ERC 0, DRC 0, parità 0). Export in `kicad/fab_out/jlcpcb/`.
- **Verifica pre-ordine automatica** (`verifica/`, 69 test in 8 aree, script ripetibili): giro 3 con **41 PASS, 25 WARN, 1 FAIL (E03), 2 N/V**, nessun WARN alto. Da rilanciare prima di ogni ordine.
- **Modifiche pre-ordine (22/11):** caricatore MCP73831 → **MCP73832 (C38066)** (STAT a 5 V sul nRF52840); monolite **9 mm**; contatti J1–J4 con target 2,0 × 4,0 mm e fori da **1,1 mm** (cambiano solo i file di foratura).
- **Comunicazione:** sezione "Pre-order verification" in README e pagina; 8 sfondi per cellulare in `sfondi/`, tutti approvati e pubblicati.
- **Firmware di prova** (`firmware/xiao-prova/`, XIAO nRF52840 Sense, Arduino + Bluefruit, audio 16 kHz IMA ADPCM, anello da 512 settori sulla QSPI da 2 MB, sync all'80%, ACK + CRC, spegnimento a 3,50 V, watchdog): **caricato sulla XIAO (22/11) e provato con l'app: collegamento, registrazione e scarico dell'audio funzionano** (confermato dall'utente). Non ancora provati a fondo: sync automatica all'80%, qualità audio, velocità di scarico.
- **App di prova** (`app/`, PWA locale: `avvia.cmd` → localhost:8787, Edge/Chrome, Web Bluetooth, IndexedDB): ascolto ed export WAV, auto-sincronizzazione all'80%.
- **Trascrizione automatica (22/11):** Whisper nel browser (transformers.js 4.3.2 in Web Worker, WebGPU o WASM, modello automatico small sul PC / base sul telefono, italiano), lanciata dopo ogni sincronizzazione; testo con ora per frase, export TXT, filtro silenzio e frasi inventate. Provata su 17 s di parlato italiano: 4,8 s con whisper-base su WebGPU, testo corretto quasi parola per parola. Service worker con COOP/COEP per WASM multithread (Android). Dettagli in `app/LEGGIMI.md`.
- Preventivo JLC precedente: 97 € per 2 schede montate (Economic PCBA), E73 in pre-order verso My Inventory.

## In corso
- **E03, bloccante:** l'E73 (C356849) su JLC è «Standard Only» con X-ray. Verificare nel carrello se l'Economic PCBA lo accetta; se no, rifare il preventivo con lo Standard.
- Attendere l'E73 in My Inventory, poi selezionarlo su U1, controllare l'anteprima (rotazioni E05, DFM: corpo di U6 su un pad di C7, F11) e pagare (coupon fino al **2/12**).
- Collaudo della XIAO: sync all'80%, qualità dell'audio, velocità di scarico; trascrizione con parlato vero (modello small, installazione come app e service worker in Edge).
- Risposte degli sponsor.

## Prossimi passi
1. Chiudere E03 nel carrello JLC e pagare.
2. Ordinare i pezzi fuori JLC: batteria 381620 con PCM, target 2,0 × 4,0 mm, motorini 0820, resina, stagno.
3. Android: pubblicare l'app su https (GitHub Pages) e provarla con Chrome (Bluetooth e Whisper su telefono). Da decidere con l'utente.
4. Disegnare i due mezzi gusci SLA a **9 mm** (canale per MK2, sigillatura delle porte dei microfoni, boccola dell'anello: F07, F09).
5. Firmware per la scheda, da ricordare: clock PDM 1,280 MHz, DCDC spento finché non è confermato, risparmio con 5V presente e VBAT < 3,1 V, pull-up interno su STAT.
6. Basetta con pogo e magneti a polarità certa (D15: SWD senza ESD).

## In pausa (per scelta dell'utente)
- Firmware per la scheda v0.1 (E73, NAND, LC3): dopo i test sulla XIAO. Pinout in `docs/pinout_v0.1.md`.
- App mobile nativa (Flutter): la PWA su Android viene provata per prima.
- Cartella locale `ncs` (toolchain Nordic parziale).

## Abbandonato
- XIAO/Seeed, PCBWay, ALLPCB, NextPCB per la produzione: solo JLC. Montaggio in casa.

## Costi
- 2 schede montate: 97 € (da riconfermare se serve lo Standard PCBA). Pezzi fuori JLC ~40–60 €. Totale v0 ~140–170 €.
- Extended JLC: 7 componenti × 3 $ a ordine.
