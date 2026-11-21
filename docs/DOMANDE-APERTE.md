# Domande aperte

## Elettronica
- Batteria: 501520 (5 × 15 × 20 mm, ~80–100 mAh) o la 351619 prevista (60 mAh)? Oppure la 501525 (~120–150 mAh), che arriverebbe a ~32 mm con il keepout dell'antenna a ~33 mm: margine di circa 1 mm, da verificare.
- Diametro dei fori dei pin dorati J1–J4 (ora 1,0 mm): dipende dai pin che comprerete.
- Rotazioni nel CPL: da controllare nell'anteprima JLC (D1–D3, MK1/MK2, Q2, E73).

## Produzione
- Pannello unico notªpad + tag SwimTimer: stesso spessore (ora 1,0 mm, 4 strati), mouse bites lontano dall'antenna; confrontare i preventivi.
- Quale fornitore: JLC, PCBWay o ALLPCB (export pronti per tutti e tre).
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

## Repository
- Licenza: da decidere.
