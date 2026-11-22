# Stato del progetto

**Ultimo aggiornamento:** 22/11/2026, Fase 1: scheda v0.1 chiusa, ordine v0 su JLC in attesa dell'E73, ricerca sponsor avviata

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`), libreria KiCad dai codici LCSC (`kicad/lib/`).
- **Scheda chiusa:** 4 strati, 1,0 mm, 16,5 × 38 mm, componenti solo sopra. ERC 0, DRC 0, 0 scollegati, 115 via. Export in `kicad/fab_out/jlcpcb/`. Pinout E73 e microfono MSM261DGT003 (top-port) verificati sui datasheet.
- **Preventivo JLC: 97 € per 2 schede montate e spedite** (Economic PCBA, 5 PCB, 2 montate). E73: 2 pezzi in pre-order verso My Inventory (coupon).
- **Licenze (22/11):** hardware CERN-OHL-S-2.0, software e documenti MIT. **Sponsor:** email inviate a 6 aziende (testi in `docs/sponsor_contatti.md`); issue pubblica fissata #1; sezione "Looking for sponsors" su README e pagina (senza nomi di aziende).
- **Pagina (22/11):** sfarfallio dell'animazione eliminato (batteria del modello 3D 15 × 19 × 3,2 mm, 0,2 mm dentro il guscio); dimensione corretta a 41 mm; layout telefono rifatto (oggetto grande, didascalia unica, schema MCP verticale senza scroll orizzontale); animazione dei gruppi con due insiemi A e B (uno in comune); gesti come punti di attenzione e sync prioritaria su timeline, con tocco, luci e vibrazione personalizzabili. Controllata a 375, 390 e 1280 px, non su un iPhone vero.
- **Batteria (22/11):** scartate 602030, 401020, 401230 e 402020 (troppo larghe, lunghe o povere di mAh); migliore la 381620 (3,8 × 16 × 20 mm, 110 mAh) con PCM da confermare; 501520 solo se il monolite passa a 9 mm.
- **Contatti (22/11):** trovati su AliExpress i "target" a testa piatta per il monolite (femmina PCB, altezza 7,0 mm) e su eBay le molle pogo singole 6-1,5-3,0-1,5-0,8 mm per la basetta. Schema della basetta fatto (8 saldature, 4 pogo + 4 fili allo XIAO RP2040).

## In corso
- Attendere l'email JLC sul prezzo del pre-order E73 e l'arrivo in **My Inventory**; poi selezionare la scorta su U1, controllare l'antenna e pagare (coupon Black Friday fino al **2/12**).
- Attendere le risposte degli sponsor. Se arrivano buoni: aggiornare il preventivo e citare lo sponsor su README e pagina.

## Prossimi passi
1. **Prima di pagare il PCBA:** controllo di ingombro in CAD (scheda 1 mm + motorino 2 mm + batteria negli 8 mm) e verifica del diametro della coda dei target contro i fori da 1,0 mm di J1–J4: se serve, si allargano ora.
2. Ordinare i pezzi fuori JLC: batteria 381620 con protezione (2–3 pezzi), target 7,0 mm, motorini 0820, resina, stagno sottile; pogo e magneti solo per la basetta.
3. Compilare i moduli online di PCBWay ed Elecrow; proposta NLnet (scadenza probabile 3/1/2027, da verificare).
4. Disegnare i due mezzi gusci SLA per JLC3DP; alle schede in arrivo saldare batteria, motorino e J1–J4 e collaudare.
5. Basetta di ricarica con molle pogo e magneti (polarità garantita): dopo il collaudo.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout in `docs/pinout_v0.1.md`. Nota: `CLAUDE.md` cita ancora il firmware per XIAO nRF52840, ma la v0.1 usa il modulo E73.
- Cartella locale `ncs` con download parziale della toolchain Nordic (1,5 GB).

## Abbandonato (21/11)
- Variante XIAO (Seeed Fusion), PCBWay, ALLPCB, NextPCB per la produzione: solo JLC (restano come possibili sponsor). Montaggio in casa: tutte le schede montate da JLC.

## Costi
- 2 schede montate: 97 € (E73 coperto da coupon). Pezzi fuori JLC ~40–60 €. Totale v0 stimato ~140–170 € (senza gusci SLA e saldatore), azzerabile in parte dagli sponsor.
- Tasse Extended JLC: 7 componenti × 3 $ a ordine.
