# Stato del progetto

**Ultimo aggiornamento:** 25/11/2026 (notte), Fase 1: scheda v0.1 progettata (ERC 0, DRC 0, parità 0, 130 via) ma **non congelata**. Ricerca sponsor in corso (dettagli solo nei file privati). Da oggi il progetto ha mail, social e un piano di pubblicazione propri.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm generata da script; export in `kicad/fab_out/` (24/11).
- Scheda 24/11: MK2 = Vesper VM3011, accelerometro LIS2DH12, Q4 DMN2004DWK per motorino + cicalino, 5V sul VBUS. Dettagli in `docs/pinout_v0.1.md`.
- Firmware di prova XIAO 0.2.0 e app di prova 0.10.0: compilano, non collaudati con parlato vero.
- 25/11: architettura software definita (piano); MK1 passa a MSM261DGT006. **MEMSensing conferma: stessa impronta, piedinatura e foro (0,65 mm) del DGT003**; foro nella resina consigliato 0,8–1,0 mm, guarnizione in gomma contro le perdite; offrono una revisione acustica gratuita su una sezione 3D.
- **25/11 – identità e social del progetto:**
  - Mail del progetto `notapad.team@gmail.com`; Ko-fi spostato su questa mail.
  - Instagram, YouTube e TikTok **@notapadlabs** (nome uguale ovunque; TikTok mostra «notApad» fino al 2/12). Logo: monogramma NªP (Georgia), banner YouTube.
  - Piano editoriale in `social/piano_editoriale.md`: 1 Reel/Short + 1 carosello a settimana, 5 temi, primi 8 post. Post in `social/post/`.
  - Post 1 (carosello «Meet notªpad»): TikTok programmato 25/11 18:30; Instagram via attività programmata alle 18:30.
  - Post 2 (Reel 21 s): YouTube Short e TikTok programmati per l'1/12 18:30; Instagram via attività programmata.
  - README e pagina: sezione unica «Support the project» (obiettivo 3–5 prototipi, ~300 €, individui + aziende) e link a tutti i social.
- Controllo posta: ogni ora 8–20, diario con bozze da confermare (sessione «Diario della posta»); legge anche Ko-fi su notapad.team.
- Nordic: progetto registrato, offerto un contatto diretto con il referente locale (modulo da compilare).

## In corso
- Ricerca sponsor (dettagli nei file privati).
- VM3011: reperibilità incerta, valutare un'alternativa per MK2.
- Revisione della scheda: cicalino 4×4, canalino acustico del VM3011.
- Verificare l'uscita dei post 1 e 2 (Instagram dipende da app Claude + Chrome profilo «notepad» aperti).

## Prossimi passi
1. Rispondere a MEMSensing; compilare il modulo Nordic.
2. Aggiornare BOM e `kicad/` al DGT006 (codice LCSC da trovare); foro frontale 0,8–1,0 mm nei gusci.
3. Preparare i post 3–6 (materiale già pronto) e programmarli a coppie ogni due settimane.
4. Video demo e foto del banco XIAO (riprese dopo il 28/11).
5. Scelta del produttore; congelare Gerber, BOM e posizionamento.
6. Ko-fi: attivare la 2FA; link in bio Instagram dall'app.
7. Dopo l'approvazione di GitHub Sponsors: `github: PZero` in `.github/FUNDING.yml`.

## In pausa
- Firmware per la scheda v0.1 (Zephyr, E73, NAND, LC3). App nativa. Pre-order E73 su JLC. Find Hub / Find My.
- Post Community su YouTube (il canale nuovo non li ha ancora).

## Abbandonato
- Montaggio in casa; variante con XIAO.

## Costi
- ~97 € per 2 schede montate (stima 21/11), pezzi fuori PCBA ~40–60 €: da ricalcolare con la BOM del 24/11. Social e strumenti: 0 €.
