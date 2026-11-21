# Stato del progetto

**Ultimo aggiornamento:** 21/11/2026, Fase 1: scheda v0.1 pronta per il preventivo JLC

## Fatto
- Concept, render delle finiture, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`).
- Strumenti su Windows: KiCad 10.0.8, easyeda2kicad, Freerouting 2.5.0 (cartella `tools/` locale).
- Libreria KiCad dai codici LCSC ufficiali in `kicad/lib/`.
- Verifiche sui datasheet: pinout E73 rifatto (`docs/pinout_v0.1.md`), microfono top-port MSM261DGT003.
- Caricatore MCP73831 (C424093) e C5 4,7 µF 0402, comuni con SwimTimer; rete CHRG rinominata STAT.
- **Scheda chiusa (21/11):** 4 strati, 1,0 mm, 16,5 × 38 mm, componenti solo sopra.
  - Controlli: ERC 0, DRC 0 violazioni, 0 scollegati, parità schema-scheda 0 (ricontrollati con kicad-cli).
  - Stackup: F.Cu segnali / In1 GND continuo / In2 segnali e alimentazioni / B.Cu segnali e GND. Keepout antenna su tutti gli strati. 115 via.
  - Regole: pista/spazio 0,10/0,10 mm, via 0,25/0,45 mm (senza sovrapprezzo), rame-bordo 0,25 mm.
  - Larghezze rimaste: alimentazioni 0,2 mm e 3V3 0,15 mm (non 0,25 e 0,2). Sufficienti per i consumi.
  - 35 mm provato: 4 collegamenti aperti. 36,5 mm non completato. Scelto 38 mm.
- Export pronto in `kicad/fab_out/jlcpcb|pcbway|allpcb/` (Gerber ZIP, BOM, CPL/centroid, `LEGGIMI.md`). Il vecchio `kicad/jlc_out/` (bozza) è stato cancellato.

## Catena degli script (`kicad/`, riproducibile con `NOTAPAD_H=38`, default 38)
`genera_sch.py` → `sbroglia.py 100 protect` → `chiudi_gnd.py tutto` → `rifinisci.py` → `chiudi_gnd.py tutto` → `pulisci.py` → `genera_dxf.py` → `genera_fab.py`.
- `genera_fab.py` sostituisce `genera_jlc.py` per gli export.
- `kicad/tracce.json` e `kicad/sbroglio.png` sono anteprime di lavoro, non da ordinare.

## Prossimi passi
1. Caricare `kicad/fab_out/jlcpcb/` su JLC solo per il preventivo. Nell'anteprima controllare le rotazioni di D1–D3, MK1/MK2, Q2 ed E73.
2. Scegliere la batteria. Candidata 501520 (5 × 15 × 20 mm, ~80–100 mAh), da verificare sul datasheet dell'E73. La 502025 (20 mm di larghezza) non entra. La 501525 (5 × 15 × 25, ~120–150 mAh) ci starebbe al limite: nell'anteprima `kicad/sbroglio.png` il keepout dell'antenna inizia a ~33 mm e la cella, partendo da 7 mm, arriverebbe a ~32.
3. Confrontare i preventivi JLC, PCBWay e ALLPCB; valutare il pannello unico con il tag SwimTimer.
4. Ordine Economic PCBA, 4 strati, 1,0 mm, HASL, 2 montate su 5, entro il 2/12 per il coupon Black Friday.
5. Dopo: basette XIAO (notªpad e SwimTimer), tag SwimTimer a 4 strati da 1,0 mm.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout per il firmware in `docs/pinout_v0.1.md`.
- In una cartella locale `ncs` c'è un download parziale della toolchain Nordic (1,5 GB), lasciato per il firmware.
