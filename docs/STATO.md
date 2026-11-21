# Stato del progetto

**Ultimo aggiornamento:** 21/11/2026 — Fase 1: scheda v0.1 (KiCad → preventivo JLC)

## Fatto
- Concept, render delle finiture, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`).
- Strumenti installati su Windows: KiCad 10.0.8, easyeda2kicad, Freerouting 2.5.0 (`C:\Users\fnico\tools\freerouting`).
- Libreria KiCad dai codici LCSC ufficiali in `kicad/lib/` (simboli, impronte, 3D).
- Verifiche sui datasheet:
  - il modulo E73 non porta fuori 9 GPIO del pinout originale → pinout rifatto in `docs/pinout_v0.1.md`;
  - il microfono LMD3526B261 è bottom-port → sostituito con MSM261DGT003 (C48227730), top-port.
- Riduzioni di spazio: una resistenza per LED sull'anodo comune (era una per colore), 2N7002 doppio opzionale.
- Aggiunto C14 1 µF sul latch: senza, un reset a batteria spegnerebbe il dispositivo.

## In corso
- Sottoagente elettronica: generatore KiCad (schema + scheda), piazzamento, sbroglio Freerouting, DRC, export Gerber/BOM/CPL in `kicad/jlc_out/`.

## Prossimi passi
1. Controllare l'esito dello sbroglio e del DRC; se A+B non bastano, decidere tra le opzioni (vedi domande aperte).
2. Caricare Gerber/BOM/CPL su JLC solo per il preventivo e controllare le rotazioni nell'anteprima.
3. Pannello unico notªpad + tag SwimTimer: confrontare il preventivo con quello delle schede separate.
4. Ordine Economic PCBA, 0,8 mm, HASL, 2 montate su 5, entro il 2/12 per il coupon Black Friday.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout per il firmware già in `docs/pinout_v0.1.md`.
- In `C:\ncs` c'è un download parziale della toolchain Nordic (1,5 GB), lasciato per il firmware.
