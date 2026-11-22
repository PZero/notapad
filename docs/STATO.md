# Stato del progetto

**Ultimo aggiornamento:** 22/11/2026 (notte), Fase 1: scheda v0.1 verificata, ordine JLC in attesa (E03). In parallelo, **banco di prova** XIAO nRF52840 Sense + app locale per capire funzionalità e prestazioni del software, che poi passerà al server MCP.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm da script (ERC 0, DRC 0). Export in `kicad/fab_out/jlcpcb/`.
- Verifica pre-ordine automatica (`verifica/`, 69 test): 41 PASS, 25 WARN, 1 FAIL (E03). Modifiche pre-ordine: MCP73832, monolite 9 mm, fori J1–J4 da 1,1 mm.
- **Banco di prova, firmware** (`firmware/xiao-prova/`, Arduino + Bluefruit): registrazione 16 kHz ADPCM, anello sulla QSPI, scarico BLE con ACK/CRC, sync all'80%.
  - **Doppio tocco** (IMU LSM6DS3TR-C) = avvia/ferma la registrazione (3 lampi verdi/rossi).
  - **Tocco singolo = comando:** 5 lampi gialli, poi giallo fisso; taglio dell'audio, 6 s a parte (bit 0 di `riservato` nella testata), scarico prioritario anche a metà di uno scarico lungo, poi la registrazione continua.
- **Banco di prova, app** (`app/`, PWA locale su localhost, Web Bluetooth, IndexedDB):
  - Whisper nel browser (transformers.js 4.3.2, modelli `_timestamped` con l'ora di ogni parola); modello automatico small sul PC, turbo a scelta.
  - Solo il parlato va a Whisper (`vad.js`, rilevatore a energia): in una giornata quasi tutto è silenzio.
  - **Chi parla** (`voci.js`): impronte WeSpeaker ResNet34 ogni 0,75 s, turni «Io» / «Interlocutore 1, 2…»; profilo del proprietario dal microfono o con «sono io» su una trascrizione; cursore di separazione.
  - Testo sempre in ordine cronologico, qualunque sia l'ordine di scarico.
  - **Comandi vocali** (`comandi.js`): «Comando, accendi/spegni la luce del bagno», tollerante agli errori di Whisper (spenni, bagnio…); secondo trascrittore (whisper-base su CPU) solo per i comandi, in parallelo. Primi test riusciti di accensione e spegnimento di luci domestiche.
- Test: `node app/test/adpcm.test.mjs` e `node app/test/voci.test.mjs` passano.
- **Pagina:** il banco di prova non è più una serie di card «Done» ma una scena animata (sezione `#bench`, prima di Progress): registrazione → Bluetooth → app (voce, Whisper, chi parla, comando) → *Next* server MCP. Layout orizzontale su desktop, verticale su telefono; provata nel browser simulato (375–1440 px), non su un iPhone vero.

## In corso
- **E03, bloccante:** E73 «Standard Only» su JLC. Verificare nel carrello se l'Economic PCBA lo accetta; poi selezionare l'E73 su U1 e pagare (coupon fino al **2/12**).
- Collaudo del banco di prova con parlato vero: precisione dei comandi con whisper-base, velocità della trascrizione lunga, separazione delle voci (soglie da tarare).

## Prossimi passi
1. Chiudere E03 e pagare l'ordine JLC.
2. Ordinare i pezzi fuori JLC: batteria 381620 con PCM, target 2,0 × 4,0 mm, motorini 0820, resina, stagno.
3. Misurare sul banco di prova: tempo per ora di registrazione, errori dei comandi; decidere se i comandi usano whisper-small.
4. Progettare il passaggio al **server MCP**: trascrizione, voci e comandi come strumenti dell'AI scelta dall'utente (la PWA resta solo banco di prova).
5. Disegnare i mezzi gusci SLA a 9 mm (F07, F09).
6. Firmware per la scheda (Zephyr): PDM 1,280 MHz, DCDC spento, pull-up su STAT, gesti e modalità comando come sulla XIAO.

## In pausa (per scelta dell'utente)
- Firmware per la scheda v0.1 (E73, NAND, LC3): dopo il banco di prova. Pinout in `docs/pinout_v0.1.md`.
- App nativa: Capacitor proposto per Android (Bluetooth a schermo spento); iPhone richiede un Mac. Non deciso.
- Cartella locale `ncs` (toolchain Nordic parziale).

## Abbandonato
- XIAO/Seeed, PCBWay, ALLPCB, NextPCB per la produzione: solo JLC. Montaggio in casa.

## Costi
- 2 schede montate: 97 € (da riconfermare se serve lo Standard PCBA). Pezzi fuori JLC ~40–60 €. Totale v0 ~140–170 €.
- Banco di prova: 0 € (XIAO già in casa, modelli AI gratuiti nel browser).
