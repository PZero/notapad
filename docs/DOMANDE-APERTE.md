# Domande aperte

## Elettronica
- **E73 e tipo di PCBA (E03):** la pagina JLC lo dà «Standard Only» con X-ray. L'Economic PCBA lo accetta nel carrello? Se no, quanto costa lo Standard per 2 schede?
- Corpo di U6 sopra un pad di C7 (~0,05 mm, F11): controllare nel DFM di JLC.
- Componenti interni dell'E73 (induttore DCDC, condensatori): il manuale Ebyte è un PDF cifrato. Finché non si conferma, DCDC spento nel firmware.
- Cella molto scarica (D03): in precondizionamento il caricatore dà ~5 mA e il sistema ne consuma ~5. Serve una modalità risparmio nel firmware?
- Pagina: controllare dall'iPhone vero lo sfarfallio dell'animazione, il layout mobile, le tre scene e la nuova scena del banco di prova (testo SVG ~12 px a 375 px: ingrandire se scomodo). Non verificati su un dispositivo reale.
- Batteria: la 381620 (3,8 × 16 × 20 mm, 110 mAh) è la scelta consigliata; trovare un annuncio che dichiari la protezione (PCM) e prenderne 2–3. Con il monolite a 9 mm la 501520 (5 mm) non entra (0,6 + 3,0 + 1,0 + 5,0 + 0,6 = 10,2 mm): resta la 381620. All'arrivo verificare spessore reale, PCM (scheda verde sotto il nastro) e lato del filo +.
- Basetta: lato di appoggio dei contatti (specchio) e polarità dei magneti da verificare col tester; mappatura dei pin XIAO RP2040 secondo la versione di `debugprobe` scelta.
- NAND: la W25N02KVZEIR costa ~10 $; cercare una SPI NAND 2 Gbit WSON-8 8×6 cinese compatibile (XT26G02, DS35Q2GA, FM25S02) e verificarne pin e comandi sul datasheet.
- IO2/IO3 della NAND senza pull-up: verificare sul datasheet Winbond.
- Corrente di carica: tenere R1 = 20 kΩ (50 mA) o passare a 33 kΩ (30 mA)? Con 470 Ω i LED verde e blu sono tenui (~1 mA).
- Land pattern del microfono (ereditato dall'impronta EasyEDA) da confrontare col disegno del datasheet; pin 1 dei LED da controllare col tester prima del reflow.

## Sponsor
- Risposte da JLCPCB, Ebyte, PCBWay, Seeed, NextPCB ed Elecrow; se arrivano buoni, ricalcolare il preventivo.
- Moduli online di PCBWay ed Elecrow da compilare; proposta NLnet (scadenza probabile 3/1/2027, da verificare su nlnet.nl).
- Ebyte: i moduli devono arrivare nel magazzino JLC, altrimenti serve uno sconto.

## Produzione
- Prezzo confermato del pre-order E73 (2 pezzi): email JLC entro 48 h; i pezzi devono arrivare in My Inventory prima del PCBA.
- I gusci SLA di JLC3DP possono viaggiare nello stesso pacco delle schede?
- Pannello unico notªpad + tag SwimTimer (file pronto in `kicad/pannello/`): confrontare il preventivo con le schede separate.
- Programmatore SWD: il Raspberry Pi 3 basta per il nRF52840? Altrimenti Raspberry Pi Debug Probe o Pico con `debugprobe`.

## App (banco di prova)
- Comandi: whisper-base su CPU capisce male alcune parole (spegni → «spenni»); le regole lo tollerano. Basta, o i comandi devono usare whisper-small (~250 MB, ~3× più lento)?
- Velocità della trascrizione lunga con small + VAD su registrazioni vere: quanti minuti per ora di audio?
- Soglie delle voci (0,40 / 0,35) da tarare con conversazioni vere a 2–3 persone.
- Android: Capacitor (app vera, Bluetooth a schermo spento, installazione via USB) o PWA su https? iPhone: serve un Mac.
- Peso dei modelli sul telefono (base ~80 MB, small ~250 MB, voci 26 MB): scaricarli solo col Wi-Fi?
- Come portare trascrizione, voci e comandi nel server MCP (strumenti per l'AI scelta dall'utente).
- Repository dell'app: questo stesso o uno separato? Invitare l'amico come collaboratore.

## Basetta di ricarica (idea, dopo il primo ordine del monolite)
- Basetta con **XIAO RP2040** + molle pogo: alimenta il 5V per la carica e fa da **programmatore SWD** (firmware `debugprobe`, come un Pico), collegata al PC via USB-C.
- Il monolite invece non ci rientra: lo XIAO nRF52840 è troppo grande (21×17,8 mm) e ha troppo pochi GPIO.

## Design
- Effetto "monolite che si illumina tutto" (resina traslucida, più LED): eventualmente per una versione successiva.

