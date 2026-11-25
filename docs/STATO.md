# Stato del progetto

**Ultimo aggiornamento:** 25/11/2026 (sera), Fase 1: scheda v0.1 progettata (ERC 0, DRC 0, parità 0, 130 via) ma **non congelata**. Ricerca di sponsor e finanziamenti in corso: dettagli solo nei file privati, esclusi da git. In parallelo il banco di prova XIAO nRF52840 Sense + app locale.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm generata da script; export in `kicad/fab_out/` (24/11).
- Scheda 24/11: MK2 = Vesper VM3011 (risveglio acustico), accelerometro LIS2DH12 (I2C), Q4 DMN2004DWK per motorino + cicalino, 5V sul VBUS del nRF. Dettagli in `docs/pinout_v0.1.md`.
- Suite `verifica/` (71 test) rilanciata sulla scheda del 24/11.
- Firmware di prova XIAO 0.2.0 (`firmware/xiao-prova/`) e app di prova 0.10.0 (`app/`): compilano, non ancora collaudati con parlato vero.
- **25/11 – finanziamenti:**
  - Ricerca sponsor in corso; nessun accordo.
  - Donazioni: Ko-fi attivo (ko-fi.com/notapad) con il pulsante «Sponsor» del repository; GitHub Sponsors in attesa di approvazione.
  - Le mail agli sponsor non sono più tracciate da git (`.gitignore`).
- **25/11 – architettura software definita (piano, non costruita):** app desktop e mobile → server notªpad con server MCP → AI scelta dall'utente con template agentico → artefatto → app. Trascrizioni temporanee sul server, cancellate dopo il ritiro. Integrazioni via MCP (comando vocale → Home Assistant funziona già nell'app di prova). Pagina con le scene `#how` e `#integrations`, README «How it works (planned)».
- **25/11 – microfono MK1:** da MSM261DGT003 a **DGT006** (versione aggiornata). Impronta e piedinatura da confermare; BOM e `kicad/` **non ancora aggiornati** (restano col DGT003).
- Video demo: bozza con musica e segnaposto in `video/` (privato, fuori da git); le riprese arrivano dopo il 28/11.
- Pubblicazione Pages: il workflow ora ha due passaggi (build e deploy) dopo un errore ricorrente.

## In corso
- Ricerca sponsor in corso (dettagli nei file privati).
- **VM3011:** reperibilità incerta; valutare un'alternativa per MK2 prima di congelare la scheda.
- Revisione della scheda: volume del cicalino 4×4, canalino acustico del VM3011 nei gusci.
- Collaudo sul campo di firmware 0.2.0 e app 0.10.0.

## Prossimi passi
1. Video demo e foto del banco XIAO.
2. Scelta del produttore; con il DGT006 confermare impronta/piedinatura e aggiornare BOM e scheda.
3. Eventuale alternativa al VM3011; datasheet del cicalino.
4. Riformulare README e pagina da «AI recorder» a «open voice recorder with an open data layer (MCP)».
5. Congelare Gerber, BOM e posizionamento; ordinare i pezzi fuori dal PCBA.
6. Dopo l'approvazione di GitHub Sponsors: aggiungere `github: PZero` in `.github/FUNDING.yml` e il link nel README.

## In pausa
- Firmware per la scheda v0.1 (Zephyr, E73, NAND, LC3). App nativa. Pre-order E73 su JLC (E03). Registrazione Find Hub e Apple Find My (MFi).

## Abbandonato
- Montaggio in casa; variante con XIAO.

## Costi
- Stime precedenti: ~97 € per 2 schede montate (scheda del 21/11); pezzi fuori PCBA ~40–60 €. Da ricalcolare con la BOM del 24/11. Banco di prova: 0 €.
