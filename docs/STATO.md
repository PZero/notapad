# Stato del progetto

**Ultimo aggiornamento:** 21/11/2026, Fase 1: scheda v0.1 chiusa, ordine v0 su JLC in corso (solo JLC)

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`), libreria KiCad dai codici LCSC (`kicad/lib/`).
- Verifiche sui datasheet: pinout E73 rifatto (`docs/pinout_v0.1.md`); microfono MSM261DGT003 top-port; E73-2G4M08S1CX scartato (solo IPEX).
- **Scheda chiusa:** 4 strati, 1,0 mm, 16,5 × 38 mm, componenti solo sopra. ERC 0, DRC 0, 0 scollegati, 115 via. Export in `kicad/fab_out/jlcpcb/` (microfoni ruotati +180° nel CPL, verificato nell'anteprima JLC).
- **Preventivo JLC: 97 € per 2 schede montate e spedite** (Economic PCBA, 5 PCB, 2 montate). Microfoni (4) comprati da JLC in automatico.
- **E73:** 2 pezzi in pre-order dal Parts Manager (13,51 €, coperti da coupon), restano nel magazzino JLC per il montaggio.
- Verificato: nessun negozio italiano costa meno di LCSC/JLC per i chip; nessun equivalente Basic per Q2, NAND, caricatore; una scheda "solo Basic" non si può fare (BLE, NAND, microfoni, LED RGB, tocco non esistono in Basic).
- Lista della spesa Amazon per i pezzi fuori da JLC: `acquisti/spesa_amazon.md` (~40–60 € stimati).

## In corso
- Attendere la conferma del prezzo del pre-order E73 (email JLC entro 48 h) e l'arrivo in **My Inventory**.
- Poi: riaprire il preventivo PCBA, selezionare la scorta su U1, controllare l'antenna verso il bordo basso nell'anteprima 3D, pagare con spedizione economica e coupon Black Friday (fino al 2/12).

## Prossimi passi
1. Ordinare da Amazon: batteria 501520 (120 mAh dichiarati, 5 × 15 × 20 mm), motorini 0820 (8 × 2 mm, NON 8 × 3,4), resina epossidica piccola; programmatore SWD solo se il Raspberry Pi 3 non basta.
2. Disegnare i due mezzi gusci SLA della v0.1 e ordinarli su JLC3DP (se possibile nello stesso pacco delle schede).
3. All'arrivo delle schede: saldare a filo batteria, motorino e contatti J1–J4 (serve solo un saldatore a punta fine), collaudo (alimentazioni, SWD, firmware minimo per LED, microfoni, NAND, tocco).
4. Basetta di ricarica con molle pogo: dopo il collaudo.

## Abbandonato (21/11)
- Variante XIAO (Seeed Fusion), PCBWay, ALLPCB, NextPCB: si resta solo su JLC.
- Montaggio in casa (stencil, piastra, pasta Sn42Bi58): non c'è l'attrezzatura; tutte le schede montate da JLC. Il piano in `acquisti/ordine_v0_*` e `stima_10monoliti.csv` resta come riferimento.

## Costi
- 2 schede montate: 97 € (E73 coperto da coupon). Pezzi Amazon ~40–60 €. Totale v0 stimato ~140–170 € (senza gusci SLA e saldatore).
- Tasse Extended JLC: 7 componenti × 3 $ a ordine (E73, NAND, microfono, LED, TTP223, MCP73831, 2N7002DW), si diluiscono con lotti più grandi.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout in `docs/pinout_v0.1.md`.
- Cartella locale `ncs` con download parziale della toolchain Nordic (1,5 GB).
