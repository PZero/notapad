# Stato del progetto

**Ultimo aggiornamento:** 21/11/2026 — Fase 1: scheda v0.1 (KiCad → preventivo JLC)

## Fatto
- Concept, render delle finiture, pagina di presentazione (`pagina/`), distinta e collegamenti v0.1 (`jlc/`).
- Strumenti installati su Windows: KiCad 10.0.8, easyeda2kicad, Freerouting 2.5.0 (installato in una cartella `tools/` locale).
- Libreria KiCad dai codici LCSC ufficiali in `kicad/lib/` (simboli, impronte, 3D).
- Verifiche sui datasheet:
  - il modulo E73 non porta fuori 9 GPIO del pinout originale → pinout rifatto in `docs/pinout_v0.1.md`;
  - il microfono LMD3526B261 è bottom-port → sostituito con MSM261DGT003 (C48227730), top-port.
- Riduzioni di spazio: una resistenza per LED sull'anodo comune (era una per colore), 2N7002 doppio opzionale.
- Aggiunto C14 1 µF sul latch: senza, un reset a batteria spegnerebbe il dispositivo.
- Caricatore MCP73831 (C424093) e C5 4,7 µF 0402 (C23733), comuni con SwimTimer; rete CHRG rinominata STAT.
- Scheda allungata a 16,5 × 38 mm (decisione utente, 21/11): con 35 mm la massa non si chiudeva su 2 strati. Monolite da ~38 a ~41 mm. Contorno in `jlc/notapad_v0.1_contorno.dxf` (generato da `kicad/genera_dxf.py`).

## Esito sbroglio (21/11 sera)
- Scheda 16,5×38: ERC 0, parità 0, DRC 0 violazioni, 7 collegamenti aperti (5 segnali + 2 gruppi GND). Gerber BOZZA, non ordinare.

## In corso
- Sottoagente elettronica: generatore KiCad (schema + scheda), piazzamento, sbroglio Freerouting, DRC, export Gerber/BOM/CPL in `kicad/jlc_out/`.

## Prossimi passi
1. Controllare l'esito dello sbroglio e del DRC; se A+B non bastano, decidere tra le opzioni (vedi domande aperte).
2. Caricare Gerber/BOM/CPL su JLC solo per il preventivo e controllare le rotazioni nell'anteprima.
3. Pannello unico notªpad + tag SwimTimer: confrontare il preventivo con quello delle schede separate.
4. Ordine Economic PCBA, 0,8 mm, HASL, 2 montate su 5, entro il 2/12 per il coupon Black Friday.

## In pausa (per scelta dell'utente)
- Firmware e app: si riparte dopo la scheda. Pinout per il firmware già in `docs/pinout_v0.1.md`.
- In una cartella locale `ncs` c'è un download parziale della toolchain Nordic (1,5 GB), lasciato per il firmware.

## Ripartenza (21/11/2026, sessione interrotta per risparmiare token)
- Scheda: decisi **4 strati da 1,0 mm** (Economic PCBA JLC non accetta 4 strati da 0,8 mm). Stackup: F.Cu segnali / In1 GND continuo / In2 segnali+alimentazioni / B.Cu segnali+GND; keepout antenna su tutti gli strati.
- Tentativo a 4 strati interrotto: era a 38 mm (35 e 36,5 provati prima), giro 1 di 2, con solo 2 errori DRC (strozzature da 0,05 mm su In2, piano In1 senza piste). I file in `kicad/` sono in quello stato intermedio. Ultimo stato a 2 strati: 16,5×38 mm, 7 collegamenti aperti.
- Prossimo passo: agente NUOVO (non fork, modello Sonnet) che legge questo file, `docs/DECISIONI.md`, `docs/pinout_v0.1.md` e gli script in `kicad/`, poi: 4 strati 1,0 mm, prova 35 mm → 36,5 → 38, DRC 0 violazioni e 0 pad scollegati, export in `kicad/fab_out/jlcpcb|pcbway|allpcb` (BOM con MPN, CPL, LEGGIMI).
- Dopo: basette XIAO (notªpad e SwimTimer), tag SwimTimer a 4 strati 1,0 mm, pannello unico e confronto preventivi (JLC unico vs basette a Seeed).
