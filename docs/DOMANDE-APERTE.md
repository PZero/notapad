# Domande aperte

## Elettronica
- Batteria: 501520 (5 × 15 × 20 mm, ~80–100 mAh) o 501525 (~120–150 mAh, margine di circa 1 mm prima del keepout dell'antenna a ~33 mm)? Dove comprarla e il motorino (LCSC non spedisce LiPo).
- Diametro dei fori dei pin dorati J1–J4 (ora 1,0 mm): dipende dai pin che comprerete.
- NAND: la W25N02KVZEIR costa ~10 $; cercare una SPI NAND 2 Gbit WSON-8 8×6 cinese compatibile (XT26G02, DS35Q2GA, FM25S02) e verificarne pin e comandi sul datasheet.
- IO2/IO3 della NAND senza pull-up: verificare sul datasheet Winbond.
- Corrente di carica: tenere R1 = 20 kΩ (50 mA) o passare a 33 kΩ (30 mA)? Con 470 Ω i LED verde e blu sono tenui (~1 mA).
- Land pattern del microfono (ereditato dall'impronta EasyEDA) da confrontare col disegno del datasheet; pin 1 dei LED da controllare col tester prima del reflow.

## Produzione
- E73-2G4M08S1C (C356849) non disponibile su JLC: comprarlo da LCSC nel magazzino JLC (3 pezzi). Il CX non va bene (solo IPEX).
- Pannello unico notªpad + tag SwimTimer (file pronto in `kicad/pannello/`): confrontare il preventivo con le schede separate.
- Montaggio in casa dei lotti successivi: stencil, piastra e pasta Sn42Bi58 (~60–70 €).
- Risposta di Seeed Fusion: XIAO nRF52840 Plus ammessa allo sconto 30%? saldano i pad sul retro? sponsorizzazione per progetti aperti?
- Acquisto Pico (circa 4–5 € dai rivenditori ufficiali) solo se servirà spesso; per ora basta il Pi 3.

## App (in pausa)
- Confermare Flutter + Android per primo.
- Repository dell'app: questo stesso o uno separato? Invitare l'amico come collaboratore.
- Qualcuno di voi ha un telefono Android?

## Basetta di ricarica (idea, dopo il primo ordine del monolite)
- Basetta con **XIAO RP2040** + molle pogo: alimenta il 5V per la carica e fa da **programmatore SWD** (firmware `debugprobe`, come un Pico), collegata al PC via USB-C.
- Possibile **sponsorizzazione Seeed Fusion**: i loro programmi richiedono un modulo XIAO sulla scheda. Nel 2026 c'è uno sconto del 30% sul PCBA XIAO; le campagne a schede gratis erano a tempo. Scrivere a Seeed Fusion per verificare le condizioni attuali.
- Il monolite invece non ci rientra: lo XIAO nRF52840 è troppo grande (21×17,8 mm) e ha troppo pochi GPIO.

## Design
- Effetto "monolite che si illumina tutto" (resina traslucida, più LED): eventualmente per una versione successiva.

## Repository
- Licenza: da decidere.
