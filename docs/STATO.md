# Stato del progetto

**Ultimo aggiornamento:** 24/11/2026 (sessione del 23/11), Fase 1: scheda v0.1 verificata, ordine JLC in attesa (E03). In parallelo il **banco di prova** XIAO nRF52840 Sense + app locale, che questa sessione ha migliorato molto (trascrizione, registrazione solo col suono).

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm da script (ERC 0, DRC 0). Export in `kicad/fab_out/jlcpcb/`. Verifica pre-ordine (`verifica/`, 69 test): 41 PASS, 25 WARN, 1 FAIL (E03).
- **Firmware di prova XIAO 0.2.0** (`firmware/xiao-prova/`, caricato il 23/11): registra 16 kHz ADPCM, anello sulla QSPI, scarico BLE con ACK/CRC, sync all'80%, doppio tocco = avvia/ferma, tocco singolo = comando.
  - **Novità:** scrive in memoria solo quando sente suono (soglia adattiva sul rumore di fondo, minimo 120, pre-ascolto di 0,5 s in RAM, 3 s di coda); comandi `VAD 0|1|<n>`; chip «in ascolto» nell'app. Compila (142 KB, RAM 20%), non provato con suoni veri.
- **App di prova 0.10.0** (`app/`, PWA locale, la versione si legge accanto al titolo):
  - **Trascrizione molto migliorata:** decoder Whisper a precisione piena (fp16/fp32, non più q4: era la causa principale degli errori), large-v3-turbo automatico sul PC con WebGPU fp16, finestre di 10–25 s tagliate nelle pause (non più 30 s a caso), livellamento del volume, filtro di frasi inventate e ripetizioni.
  - **Comandi** passano dallo stesso modello (prima whisper-base su CPU: un comando chiaro diventava parole senza senso).
  - **Trascrizione a richiesta:** in automatico solo i comandi; il resto col pulsante «Trascrivi» o «Trascrivi le nuove».
  - **Modelli in locale:** l'app cerca prima la cache, poi `app/modelli/` (fuori da git), poi Internet; pulsante «Salva i modelli in una cartella».
  - **Tabella registrazioni** leggibile su PC e telefono; i silenzi non scritti dal firmware vengono rimessi (fino a 60 s per buco).
  - Test node: `adpcm`, `voci`, `vad` passano.
- **Sponsor:** risposte da PCBWay (chiede se siamo studenti e se c'è un piano commerciale) e Seeed (sconto 30% solo con moduli XIAO). Bozze di replica pronte, l'invio è dell'utente. Stima Seeed: PCB 4 strati 5 pezzi $39,90 + ~$30 di spedizione, montaggio non calcolato.

## In corso
- **E03, bloccante:** E73 «Standard Only» su JLC; verificare se l'Economic PCBA lo accetta, poi pagare (coupon fino al **2/12**).
- Collaudo sul campo: qualità della nuova trascrizione (download turbo ~1,6 GB), soglia del suono del firmware 0.2.0 (tarare con `INFO`), tempi per ora di audio.

## Prossimi passi
1. Chiudere E03 e pagare l'ordine JLC.
2. Provare firmware 0.2.0 e app 0.10.0 con parlato vero; tarare soglia del suono e confrontare small/turbo.
3. Ordinare i pezzi fuori JLC (batteria 381620 con PCM, target 2,0 × 4,0 mm, motorini 0820, resina, stagno).
4. Portare trascrizione, voci e comandi nel **server MCP**; comandi che funzionino anche con la PWA fuori casa.
5. Mezzi gusci SLA a 9 mm (F07, F09); firmware Zephyr per la scheda (PDM 1,280 MHz, DCDC spento, gesti e comandi come sulla XIAO, ascolto con soglia).

## In pausa
- Firmware per la scheda v0.1 (E73, NAND, LC3). Pinout in `docs/pinout_v0.1.md`.
- App nativa: Capacitor per Android; iPhone richiede un Mac. Non deciso.
- Standby acustico hardware (microfono con risveglio, tipo Vesper VM3011): idea per la v0.2, non per l'ordine attuale.

## Abbandonato
- XIAO/Seeed, PCBWay, ALLPCB, NextPCB per la produzione: solo JLC (se uno sponsor accetta, eccezione per il primo lotto da decidere).

## Costi
- 2 schede montate: 97 € (da riconfermare se serve lo Standard PCBA). Pezzi fuori JLC ~40–60 €. Totale v0 ~140–170 €. Banco di prova: 0 €.
