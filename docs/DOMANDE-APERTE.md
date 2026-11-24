# Domande aperte

## Elettronica
- **E73 e tipo di PCBA (E03):** la pagina JLC lo dà «Standard Only» con X-ray. L'Economic PCBA lo accetta nel carrello? Se no, quanto costa lo Standard per 2 schede?
- Corpo di U6 sopra un pad di C7 (~0,05 mm, F11): controllare nel DFM di JLC.
- Componenti interni dell'E73 (induttore DCDC, condensatori): il manuale Ebyte è un PDF cifrato. Finché non si conferma, DCDC spento nel firmware.
- Cella molto scarica (D03): in precondizionamento il caricatore dà ~5 mA e il sistema ne consuma ~5. Serve una modalità risparmio nel firmware?
- Pagina: controllare dall'iPhone vero lo sfarfallio dell'animazione, il layout mobile, le tre scene e la nuova scena del banco di prova (testo SVG ~12 px a 375 px: ingrandire se scomodo). Non verificati su un dispositivo reale.
- Autonomia: ~20 h stimati con 110 mAh (corretto il 24/11); confermare con il consumo misurato sulla XIAO e sulla scheda vera.
- Batteria: la 381620 (3,8 × 16 × 20 mm, 110 mAh) è la scelta consigliata; trovare un annuncio che dichiari la protezione (PCM) e prenderne 2–3. Con il monolite a 9 mm la 501520 (5 mm) non entra (0,6 + 3,0 + 1,0 + 5,0 + 0,6 = 10,2 mm): resta la 381620. All'arrivo verificare spessore reale, PCM (scheda verde sotto il nastro) e lato del filo +.
- Basetta: lato di appoggio dei contatti (specchio) e polarità dei magneti da verificare col tester; mappatura dei pin XIAO RP2040 secondo la versione di `debugprobe` scelta.
- NAND: la W25N02KVZEIR costa ~10 $; cercare una SPI NAND 2 Gbit WSON-8 8×6 cinese compatibile (XT26G02, DS35Q2GA, FM25S02) e verificarne pin e comandi sul datasheet.
- IO2/IO3 della NAND senza pull-up: verificare sul datasheet Winbond.
- Corrente di carica: tenere R1 = 20 kΩ (50 mA) o passare a 33 kΩ (30 mA)? Con 470 Ω i LED verde e blu sono tenui (~1 mA).
- Land pattern del microfono (ereditato dall'impronta EasyEDA) da confrontare col disegno del datasheet; pin 1 dei LED da controllare col tester prima del reflow.

## Sponsor
- **PCBWay:** risposta e articolo inviati il 24/11, candidatura «in revisione»: attendere l'esito (credito, buono o schede?) e se 5 schede montate sono realistiche. Seeed: sconto 30% solo con moduli XIAO. Se uno sponsor accetta, ritirare le altre richieste.
- Risposte da JLCPCB, Ebyte, PCBWay, Seeed, NextPCB ed Elecrow; se arrivano buoni, ricalcolare il preventivo.
- Modulo online di Elecrow da compilare; proposta NLnet (scadenza probabile 3/1/2027, da verificare su nlnet.nl).
- Ebyte: i moduli devono arrivare nel magazzino JLC, altrimenti serve uno sconto.

## Produzione
- Produttore non deciso: nessun ordine confermato (solo preventivo e verifica a carrello dell'E73). Dipende dallo sponsor.
- I gusci SLA di JLC3DP possono viaggiare nello stesso pacco delle schede?
- Pannello unico notªpad + tag SwimTimer (file pronto in `kicad/pannello/`): confrontare il preventivo con le schede separate.
- Programmatore SWD: il Raspberry Pi 3 basta per il nRF52840? Altrimenti Raspberry Pi Debug Probe o Pico con `debugprobe`.

## App (banco di prova)
- Qualità e velocità della nuova trascrizione (turbo fp16 con finestre ai silenzi) su registrazioni vere: quanti minuti per ora di audio? La GPU integrata regge turbo o serve small?
- Soglia del suono del firmware 0.2.0 (minimo 120, fattore 3 sul fondo): perde parole dette piano? registra troppo rumore? Tarare con `INFO`/`VAD <n>`.
- Copia dei modelli su file (`app/modelli/`): provata solo la lettura; il pulsante «Salva i modelli in una cartella» va provato a mano.
- Comandi con la PWA fuori casa: come raggiungere i dispositivi da remoto in https (da decidere quando si passa al server MCP).
- Soglie delle voci (0,40 / 0,35) da tarare con conversazioni vere a 2–3 persone.
- Android: Capacitor (app vera, Bluetooth a schermo spento, installazione via USB) o PWA su https? iPhone: serve un Mac.
- Peso dei modelli sul telefono (base ~80 MB, small ~250 MB, voci 26 MB): scaricarli solo col Wi-Fi?
- Come portare trascrizione, voci e comandi nel server MCP (strumenti per l'AI scelta dall'utente).
- Repository dell'app: questo stesso o uno separato? Invitare l'amico come collaboratore.

## Basetta di ricarica (idea, dopo il primo ordine del monolite)
- Basetta con **XIAO RP2040** + molle pogo: alimenta il 5V per la carica e fa da **programmatore SWD** (firmware `debugprobe`, come un Pico), collegata al PC via USB-C.
- Il monolite invece non ci rientra: lo XIAO nRF52840 è troppo grande (21×17,8 mm) e ha troppo pochi GPIO.

## Standby e ascolto
- **Per la revisione (qualche settimana):** microfono con risveglio acustico (TDK T5838 da verificare su LCSC, oppure analogico + LPCOMP); Google Find Hub su nRF52840 (Apple Find My solo con MFi; DULT anti-tracciamento). Decidere cosa entra nella v0.1 definitiva.
- Microfono con risveglio acustico (Vesper VM3011 o simile) per la v0.2: valutare consumo, prezzo e disponibilità su LCSC; ora si risparmia solo memoria, non batteria.
- Con 2 microfoni sulla scheda: usarli per scegliere il canale migliore, ridurre il rumore e capire chi parla (sopra/davanti)?

## Design
- Effetto "monolite che si illumina tutto" (resina traslucida, più LED): eventualmente per una versione successiva.

