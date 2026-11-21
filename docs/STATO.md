# Stato del progetto

**Ultimo aggiornamento:** 21/11/2026, Fase 1: scheda v0.1 chiusa, ordine v0 su JLC in preparazione

## Fatto
- Concept, render, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`), libreria KiCad dai codici LCSC (`kicad/lib/`).
- Verifiche sui datasheet: pinout E73 rifatto (`docs/pinout_v0.1.md`); microfono MSM261DGT003 top-port con pin 1 VDD, 2/5 GND, 3 DATA, 4 CLK, 6 L/R, VDD 1,6–3,6 V; E73-2G4M08S1CX scartato (solo IPEX).
- **Scheda chiusa (21/11):** 4 strati, 1,0 mm, 16,5 × 38 mm, componenti solo sopra. ERC 0, DRC 0, 0 scollegati, parità 0, 115 via. Stackup F.Cu segnali / In1 GND / In2 segnali+alimentazioni / B.Cu segnali+GND. Piste 0,10/0,10 mm, via 0,25/0,45 mm, alimentazioni 0,2 mm, 3V3 0,15 mm.
- **Export** in `kicad/fab_out/`: `jlcpcb/`, `pcbway/`, `allpcb/` (da `genera_fab.py`), `nextpcb/` (scheda 51 × 51 con circuito nell'angolo, per Rev 0) e `nextpcb_pannello52/` (pannello 52 × 52). Nel CPL JLC i microfoni sono ruotati di +180° (verificato nell'anteprima JLC).
- Pannello di prova monolite + tag SwimTimer (DRC 0) in `kicad/pannello/` (cartella fuori da Git: contiene file di SwimTimer).
- Piano acquisti in `acquisti/`: `ordine_v0_3monoliti_v2.csv` (25 righe, per montaggio in casa), `stima_10monoliti.csv`, `altri_distributori.csv`, `LEGGIMI.md`.
- Richiesta a Seeed Fusion (variante XIAO nRF52840 Plus, sconto 30% PCBA) inviata dall'utente; bozza in `docs/seeed_richiesta_en.md`.

## In corso
- Ordine v0 su JLC: Economic PCBA, 4 strati, 1,0 mm, ENIG o HASL senza piombo, 2 montate su 5. Preventivo 118 € con 2 montate, senza E73 (non disponibile a magazzino JLC). MK1/MK2 ora forniti da JLC, rotazioni controllate.

## Prossimi passi
1. Procurare l'E73 (C356849): Parts Manager → Order Parts, 3 pezzi da LCSC verso "My Inventory", poi selezionarlo su U1 e controllare l'antenna verso il bordo basso. Stima totale ~135 €. Coupon Black Friday fino al 2/12.
2. Scegliere la batteria (501520 sicura; 501525 al limite) e comprare batteria e motorino a parte (LCSC non spedisce LiPo).
3. Quando arrivano le schede: collaudo (alimentazioni, SWD, firmware minimo di prova per LED, microfoni, NAND, tocco); montare in casa le 3 schede nude con stencil, piastra e pasta Sn42Bi58.
4. Attendere la risposta di Seeed; se conviene, progettare la variante XIAO nRF52840 Plus.
5. Dopo la v0: lotti con le schede nude (50 per ~45 €), componenti a blocchi con scorte; tag SwimTimer a 4 strati da 1,0 mm; basetta con XIAO.

## Costi (stime del 21/11)
- Componenti per monolite ~19 $ (NAND ~10 $, E73 ~7 $); sotto ~10 $ solo con una NAND cinese compatibile, da verificare.
- Spese fisse JLC ~100 € a ordine; attrezzatura per saldare in casa ~60–70 € una tantum.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout in `docs/pinout_v0.1.md`.
- Cartella locale `ncs` con download parziale della toolchain Nordic (1,5 GB).
