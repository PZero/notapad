# Stato del progetto

**Ultimo aggiornamento:** 25/11/2026 (sera), Fase 1: scheda v0.1 progettata (ERC 0, DRC 0, parità 0, 130 via) ma **non congelata**. Ricerca di sponsor e finanziamenti in corso (dettagli solo nei file privati, `docs/finanziamenti/`). Il progetto ha mail, social e un piano di pubblicazione propri.

## Fatto
- Concept, render, pagina (`pagina/`), scheda 4 strati 1,0 mm 16,5 × 38 mm generata da script; export in `kicad/fab_out/` (24/11). Dettagli componenti in `docs/pinout_v0.1.md`.
- Firmware di prova XIAO 0.2.0 e app di prova 0.10.0: compilano, non collaudati con parlato vero.
- Architettura software definita (piano 25/11). MK1 → MSM261DGT006 (MEMSensing: stessa impronta, piedinatura e foro 0,65 mm; foro nella resina 0,8–1,0 mm con guarnizione). Risposta inviata a MEMSensing.
- **Social (25/11):** @notapadlabs su Instagram, YouTube e TikTok; mail `notapad.team@gmail.com`. Post 1 (carosello «Meet notªpad») pubblicato su TikTok e, a mano, su Instagram.
- **Post 2–7 pronti** in `social/post/` (immagini, reel, `testo.md`, script `genera_*.py` con `comune.py`) e **programmati alle 18:30**: 27/11 post 3 (carosello evergreen «Why we are building this», 7 slide: perché, feedback dei futuri utenti, «How you can help») · 28/11 reel 4 «Pick the finish» (IG, YT, TikTok) · 30/11 post 5 «Where do your recordings go?» · 1/12 reel 2 · 3/12 reel 6 «It sleeps until you speak» · 5/12 post 7 «16.5 × 38 mm, four layers». Calendario in `social/piano_editoriale.md`.
- **Diario della posta (25/11):** pagina privata con le novità della posta del progetto e le bozze di risposta, che partono solo dopo la conferma dell'utente (dettagli nei file privati).
- Attività programmate: pubblicazioni (usano «Browser 1», Chrome del profilo «notepad»), controllo posta periodico, **statistiche social** ogni sera fino al 6/12 poi il lunedì (scrive `social/statistiche.md`, sola lettura).
- **Finanziamenti:** modulo Nordic inviato (progetto registrato con ID per i ticket DevZone, referente italiano in arrivo); ST ha preso in carico 5 LIS2DH12; Ko-fi attivo; GitHub Sponsors in approvazione. **NLnet abbandonato** (policy AI v2.0). PCBWay 9th Project Design Contest (24/1/2027) e Tindie × PCBWay (31/1/2027): regolamenti verificati, nessun divieto sull'AI. Autodesk scartato.
- Pagina PCBWay9 pronta in `docs/finanziamenti/concorso_pcbway9_bozza.md` con immagini e schema in `pcbway9_media/` (rendering 3D, PDF).
- Repo: autore dei prossimi commit impostato a `PZero` (noreply GitHub) nella config locale; i 34 commit passati restano «Your Name».
- README: nuovo sottotitolo «open wearable voice recorder with an open data layer» (pubblicato, commit a49f5af). La stessa modifica in `pagina/index.html` è fatta ma **non committata**.

## In corso
- Ricerca sponsor (file privati). Richieste di campioni: Vesper, MEMSensing, Winbond; Ebyte (E73) senza risposta, sollecito verso il 2/12.
- VM3011: reperibilità incerta, valutare un'alternativa per MK2.
- Revisione della scheda: cicalino 4×4, canalino acustico del VM3011.

## Prossimi passi
1. Pubblicare la pagina del progetto sul concorso PCBWay9 (account PCBWay, ~20 min, tocca a te).
2. Aggiornare BOM e `kicad/` al DGT006 (codice LCSC da trovare); decidere l'alternativa a MK2.
3. Video demo e foto del banco XIAO (riprese dopo il 28/11); poi la relazione per Tindie × PCBWay.
4. Tindie: il banco XIAO esistente vale solo con aggiunte sostanziali fatte durante il concorso (distinguere nel report vecchio e nuovo; privacy e consenso per l'audio).
5. Controllare le statistiche dei post e adattare il ritmo dopo il 6/12 (oggi 4–5 post a settimana, poi 2).
6. Scelta del produttore (~5/12); congelare Gerber, BOM e posizionamento.
7. Ko-fi: 2FA; link in bio Instagram; con GitHub Sponsors approvato: `github: PZero` in `.github/FUNDING.yml`.
8. Pulizia: togliere le righe NLnet dal calendario di `docs/finanziamenti/piano.md` (10/12, 15–28/12, 2/1); controllo posta di nuovo ogni 2 ore.
9. Idea non avviata: sondaggio breve per i futuri utenti (link nel post 3 e in bio).

## In pausa
- Firmware per la scheda v0.1 (Zephyr, E73, NAND, LC3). App nativa. Pre-order E73 su JLC. Find Hub / Find My (Apple solo con MFi).
- Post Community su YouTube (il canale nuovo non li ha ancora).

## Abbandonato
- Montaggio in casa; variante con XIAO; NLnet Restack (policy AI v2.0); concorso Autodesk.

## Costi
- ~97 € per 2 schede montate (stima 21/11), pezzi fuori PCBA ~40–60 €: da ricalcolare con la BOM del 24/11. Social e strumenti: 0 €.

Ultima chiusura veloce: 25/11/2026, documenti non pubblicati (pagina, README, CHANGELOG e commit al prossimo `/fine-sessione`).
