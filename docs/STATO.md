# Stato del progetto

**Ultimo aggiornamento:** 22/11/2026, Fase 1: scheda v0.1 chiusa, ordine v0 su JLC in attesa dell'E73, ricerca sponsor avviata

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`), libreria KiCad dai codici LCSC (`kicad/lib/`).
- **Scheda chiusa:** 4 strati, 1,0 mm, 16,5 × 38 mm, componenti solo sopra. ERC 0, DRC 0, 0 scollegati, 115 via. Export in `kicad/fab_out/jlcpcb/`. Pinout E73 e microfono MSM261DGT003 (top-port) verificati sui datasheet.
- **Preventivo JLC: 97 € per 2 schede montate e spedite** (Economic PCBA, 5 PCB, 2 montate). E73: 2 pezzi in pre-order verso My Inventory (coupon).
- **Licenze (22/11):** hardware CERN-OHL-S-2.0 (`LICENSE-HARDWARE`), software e documenti MIT (`LICENSE`); README aggiornato.
- **Sponsor (22/11):** email inviate a JLCPCB, Ebyte, PCBWay, Seeed Fusion, NextPCB ed Elecrow (testi in `docs/sponsor_contatti.md`). Issue pubblica fissata https://github.com/PZero/notapad/issues/1; sezione "Looking for sponsors" su README e pagina (senza nomi di aziende).
- Confronto con dema-import.it: utile solo la batteria 381620 (110 mAh, 3,8 × 16 × 20 mm, PCM, 2,50 €) e il flussante; la lista Amazon resta com'è (`acquisti/spesa_amazon.md`).

## In corso
- Attendere l'email JLC sul prezzo del pre-order E73 e l'arrivo in **My Inventory**; poi riaprire il preventivo PCBA, selezionare la scorta su U1, controllare l'antenna e pagare (coupon Black Friday fino al **2/12**).
- Attendere le risposte degli sponsor. Se arrivano buoni: aggiornare il preventivo e citare lo sponsor su README e pagina.

## Prossimi passi
1. Compilare i moduli online di PCBWay ed Elecrow; preparare la proposta NLnet (scadenza probabile 3/1/2027, da verificare) con il testo in `docs/sponsor_contatti.md`.
2. Ordinare i pezzi fuori JLC: batteria (501520 su Amazon o 381620 su dema-import, da decidere), motorini 0820, resina, stagno sottile; SWD solo se il Raspberry Pi 3 non basta.
3. Disegnare i due mezzi gusci SLA e ordinarli su JLC3DP; all'arrivo delle schede saldare batteria, motorino e J1–J4 e collaudare.
4. Basetta di ricarica con molle pogo: dopo il collaudo.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout in `docs/pinout_v0.1.md`. Nota: `CLAUDE.md` cita ancora il firmware per XIAO nRF52840, ma la v0.1 usa il modulo E73.
- Cartella locale `ncs` con download parziale della toolchain Nordic (1,5 GB).

## Abbandonato (21/11)
- Variante XIAO (Seeed Fusion), PCBWay, ALLPCB, NextPCB per la produzione: si resta solo su JLC (restano come possibili sponsor).
- Montaggio in casa: tutte le schede montate da JLC.

## Costi
- 2 schede montate: 97 € (E73 coperto da coupon). Pezzi fuori JLC ~40–60 €. Totale v0 stimato ~140–170 € (senza gusci SLA e saldatore), azzerabile in parte dagli sponsor.
- Tasse Extended JLC: 7 componenti × 3 $ a ordine.
