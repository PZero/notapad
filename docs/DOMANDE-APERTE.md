# Domande aperte

## Elettronica
- Ingombro in CAD (scheda 1 mm + motorino 2 mm + batteria) dentro gli 8 mm del monolite: da fare prima di pagare il PCBA; la 501520 da 5 mm non lascia margine di resina.
- Pagina: controllare dall'iPhone vero lo sfarfallio dell'animazione, il layout mobile e le tre scene (non verificati su un dispositivo reale).
- Batteria: la 381620 (3,8 × 16 × 20 mm, 110 mAh) è la scelta consigliata; trovare un annuncio che dichiari la protezione (PCM) e prenderne 2–3. La 501520 solo se il monolite passa a 9 mm. All'arrivo verificare spessore reale, PCM (scheda verde sotto il nastro) e lato del filo +.
- Diametro della coda dei contatti "target" (AliExpress 4000437657657): non indicato nell'annuncio; chiedere le quote al venditore e, se serve, allargare i fori di J1–J4 (ora 1,0 mm) prima di pagare JLC.
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

## App (in pausa)
- Confermare Flutter + Android per primo.
- Repository dell'app: questo stesso o uno separato? Invitare l'amico come collaboratore.
- Qualcuno di voi ha un telefono Android?

## Basetta di ricarica (idea, dopo il primo ordine del monolite)
- Basetta con **XIAO RP2040** + molle pogo: alimenta il 5V per la carica e fa da **programmatore SWD** (firmware `debugprobe`, come un Pico), collegata al PC via USB-C.
- Il monolite invece non ci rientra: lo XIAO nRF52840 è troppo grande (21×17,8 mm) e ha troppo pochi GPIO.

## Design
- Effetto "monolite che si illumina tutto" (resina traslucida, più LED): eventualmente per una versione successiva.

