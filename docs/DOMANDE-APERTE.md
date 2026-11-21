# Domande aperte

## Elettronica
- Zone A+B: se dopo le riduzioni lo sbroglio non riesce, scegliere tra: togliere i 2 TTP223 a favore del tocco software sul nRF (~24 mm², −6 $ di Extended), allungare la scheda di 1–2 mm, spostare i LED più in alto.
- 2N7002 doppio (C83571, Extended, +3 $) solo se serve spazio.
- Diametro dei fori dei pin dorati J1–J4 (ora 1,0 mm): dipende dai pin che comprerete.
- Limiti JLC su pista/spazio a 2 strati (0,1 o 0,127 mm): da confermare sulla pagina capabilities.

## Produzione
- Pannello unico notªpad + tag SwimTimer: stesso spessore (0,8 mm), mouse bites lontano dall'antenna; confrontare i preventivi.
- Acquisto Pico (circa 4–5 € dai rivenditori ufficiali, non 16 € su Amazon) solo se servirà spesso; per ora basta il Pi 3.

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
