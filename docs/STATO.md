# Stato del progetto

**Ultimo aggiornamento:** 24/11/2026, Fase 1: scheda v0.1 verificata ma **non congelata** (revisione in corso prima dei file definitivi). Candidatura di sponsorizzazione PCBWay inviata e **in revisione**. In parallelo il banco di prova XIAO nRF52840 Sense + app locale.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm da script (ERC 0, DRC 0). Export in `kicad/fab_out/`. Verifica pre-ordine (`verifica/`, 69 test): 41 PASS, 25 WARN, 1 FAIL (E03).
- **Firmware di prova XIAO 0.2.0** (`firmware/xiao-prova/`): registra 16 kHz ADPCM, anello sulla QSPI, scarico BLE con ACK/CRC, sync all'80%, gesti, registra solo col suono (soglia adattiva, pre-ascolto 0,5 s). Compila; non provato con suoni veri.
- **App di prova 0.10.0** (`app/`, PWA locale): Whisper a precisione piena (turbo su WebGPU), finestre ai silenzi, comandi dallo stesso modello, trascrizione a richiesta, modelli in locale.
- **Sponsorizzazione PCBWay (24/11):** articolo tecnico IT/EN (`docs/pcbway_articolo_it.md`, `docs/pcbway_article_en.md`) e PDF professionale (`docs/pcbway_pdf/`); email di risposta inviata (bozze private, fuori da git); modulo sponsorpublish compilato e inviato, ora «in revisione». Chiesto: 5 schede montate, un solo sponsor, logo anche in serigrafia, aperti a richieste particolari.
- **Pulizia pubblica:** tolti da README e pagina tutti i nomi di fornitori (JLC e altri); regola aggiunta all'agente `comunicazione`. Consumi corretti ovunque: ~4,6 mA → **~20 h** con la 381620 da 110 mAh; memoria 256 MB = **11–12 h** di stereo continuo (il limite è la memoria).
- Nuovo comando `/fine-sessione-fast` (solo documenti locali, niente commit).

## In corso
- Attesa risposta di PCBWay (e degli altri sponsor). Se l'obiettivo di 5 schede montate è realistico, adattare la distinta ai componenti del loro magazzino.
- **Revisione della scheda** (qualche settimana) prima di congelare Gerber, BOM e posizionamento: microfono con risveglio acustico, compatibilità Find Hub.
- Collaudo sul campo di firmware 0.2.0 e app 0.10.0 (trascrizione, soglia del suono, tempi).

## Prossimi passi
1. Valutare microfono con AAD (TDK T5838, non ancora verificato su LCSC) o analogico + LPCOMP del nRF52840; Google Find Hub (Apple Find My richiede MFi; DULT anti-tracciamento).
2. Provare firmware 0.2.0 e app 0.10.0 con parlato vero; tarare soglia e confrontare small/turbo.
3. App Android e architettura del server MCP (trascrizione, voci, comandi).
4. Ordinare i pezzi fuori dal PCBA (batteria 381620 con PCM, target 2,0 × 4,0 mm, motorini, resina) quando il produttore è deciso.
5. Mezzi gusci SLA a 9 mm; firmware Zephyr per la scheda.

## In pausa
- Firmware per la scheda v0.1 (E73, NAND, LC3). Pinout in `docs/pinout_v0.1.md`.
- App nativa: Capacitor per Android; iPhone richiede un Mac. Non deciso.
- Pre-order E73 su JLC (E03): non confermato nulla, solo verifica a carrello. Il produttore non è deciso: dipende dallo sponsor.

## Abbandonato
- Montaggio in casa, Seeed Fusion come produttore (sconto 30% solo con moduli XIAO). Il «solo JLC» del 21/11 non vale più finché non si sa lo sponsor.

## Costi
- Preventivo di prima stima: ~97 € per 2 schede montate; pezzi fuori PCBA ~40–60 €. Banco di prova: 0 €. Con sponsor: da definire.
