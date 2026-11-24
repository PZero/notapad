# Stato del progetto

**Ultimo aggiornamento:** 24/11/2026, Fase 1: scheda v0.1 **rigenerata con standby acustico, accelerometro e cicalino** (ERC 0, DRC 0, parità 0, 130 via) ma **non congelata**: revisione in corso prima dei file definitivi. Candidatura di sponsorizzazione PCBWay inviata e **in revisione** (nessun tempo dichiarato; ci aspettiamo giorni, al massimo un paio di settimane). In parallelo il banco di prova XIAO nRF52840 Sense + app locale.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm da script. Export in `kicad/fab_out/` (rigenerati il 24/11).
- **Scheda 24/11:** MK2 = Vesper VM3011 (risveglio acustico, ZPL ~10 µA, DOUT su P0.03), accelerometro LIS2DH12 (I2C), Q4 doppio MOSFET DMN2004DWK per motorino + cicalino (cicalino 4×4 mm a mano sul retro, BZ+/BZ−), 5V sul pin VBUS del nRF (tolti R6/R7 e la lettura di STAT, liberi P0.28/P0.07 = I2C). Servono per Find Hub e Apple Find My (DULT: emettitore sonoro obbligatorio, sensore di movimento raccomandato). Dettagli in `docs/pinout_v0.1.md`.
- **Suite `verifica/` aggiornata** (71 test: 45 PASS, 23 WARN noti, 2 non verificabili, 1 FAIL = E02 pagina JLC non riletta). Ha trovato e fatto correggere: rotazione CPL del VM3011 (era 180° ereditata) e impronta senza courtyard.
- Errore BOM corretto: U3 riportava il codice dell'MCP73831; ora MCP73832.
- Deploy Pages fallito il 24/11 mattina = errore temporaneo di GitHub, già rientrato.
- **Firmware di prova XIAO 0.2.0** (`firmware/xiao-prova/`): registra 16 kHz ADPCM, anello sulla QSPI, scarico BLE con ACK/CRC, sync all'80%, gesti, registra solo col suono. Compila; non provato con suoni veri.
- **App di prova 0.10.0** (`app/`, PWA locale): Whisper a precisione piena (turbo su WebGPU), finestre ai silenzi, comandi vocali, trascrizione a richiesta.
- Sponsorizzazione PCBWay: articolo IT/EN, PDF, mail e modulo inviati (bozze private, fuori da git).

## In corso
- Attesa di PCBWay. Mail di aggiornamento sulle modifiche della scheda: solo con la risposta o un sollecito verso il 2–3/12. Se la candidatura salta, passare agli altri sponsor.
- **Verifica disponibilità BOM nel magazzino PCBWay** (non fatta: serve il caricamento sul loro sito; più a rischio E73, MSM261, MHPA1010, TTP223, VM3011). Se montano loro J1–J4 serve un target di catalogo (Mill-Max 19xx) o inviare i nostri.
- Revisione della scheda: restano il volume del cicalino 4×4, il canalino acustico del VM3011 nei gusci, la reperibilità del VM3011 (LCSC esaurito, datasheet preliminare).
- Collaudo sul campo di firmware 0.2.0 e app 0.10.0.

## Prossimi passi
1. Leggere i datasheet del cicalino (KLJ-4020 / FST-4020), decidere foro di uscita e posizione sul retro.
2. Verificare stock VM3011 su Digi-Key/Mouser (e alternativa se non si trova).
3. Provare firmware 0.2.0 e app 0.10.0 con parlato vero; tarare la soglia.
4. Congelare Gerber, BOM e posizionamento; poi ordinare i pezzi fuori dal PCBA (batteria 381620 con PCM, target 2,0 × 4,0, motorini, cicalino, resina).
5. App Android, server MCP, gusci SLA a 9 mm con canalino del VM3011, firmware Zephyr per la scheda (standby ZPL, I2C, DULT).

## In pausa
- Firmware per la scheda v0.1 (E73, NAND, LC3). App nativa (Capacitor/iPhone). Pre-order E73 su JLC (E03). Registrazione Find Hub (Nearby Console) e Apple Find My (richiede MFi).

## Abbandonato
- Montaggio in casa, Seeed Fusion (sconto solo con XIAO). Il «solo JLC» del 21/11 non vale finché non si sa lo sponsor.

## Costi
- Preventivo di prima stima: ~97 € per 2 schede montate; pezzi fuori PCBA ~40–60 € (+ cicalino); da ricalcolare con la nuova BOM (3 Extended in più). Banco di prova: 0 €.
