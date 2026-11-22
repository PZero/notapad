# Registro delle decisioni

Le decisioni precedenti al 21/11/2026 (oggetto, elettronica v0.1, colata) sono riassunte in `CLAUDE.md`.

| Data | Decisione | Motivazione |
|---|---|---|
| 21/11/2026 | Pinout nRF52840 rifatto (`docs/pinout_v0.1.md`) | L'E73-2G4M08S1C non porta fuori P0.11/14/16/19/21/23/25/27 e P1.01 |
| 21/11/2026 | Microfoni MK1/MK2: MSM261DGT003 C48227730 al posto di LMD3526B261-OA1 | Il LMD3526 è bottom-port (datasheet). Il MSM261DGT003 è top-port, 4×2 mm, a magazzino JLC |
| 21/11/2026 | LED: una resistenza 470 Ω sull'anodo comune, un colore alla volta in multiplex | Da 9 a 3 resistenze, serve spazio in zona B |
| 21/11/2026 | C14 1 µF su LATCH_ON | Il latch regge circa 0,5 s durante un reset (watchdog a batteria) |
| 21/11/2026 | Nessun quarzo 32 kHz: P0.00/P0.01 usati come GPIO, firmware con LFRC | Servono pin; il quarzo non ci sta |
| 21/11/2026 | Il caricatore TP4054 resta sul monolite, non nella basetta | Contatti senza tensione fuori dalla basetta, segnale CHRG disponibile, carica piena a 4,2 V; spostarlo farebbe guadagnare solo ~12 mm² |
| 21/11/2026 | Luce dei LED solo dalla fessura frontale, riempita di resina opalina | La resina pigmentata blocca la luce; per più LED mancano spazio, pin e batteria |
| 21/11/2026 | Programmazione SWD con Raspberry Pi 3 + OpenOCD; Pico (debugprobe) eventuale | Il nRF52840 non ha bootloader in ROM: il primo bootloader va caricato via SWD, poi OTA via BLE |
| 21/11/2026 | App: Flutter, sviluppo su Android prima (proposta, da confermare) | Nessuno ha un Mac; il simulatore iOS non ha BLE; iOS si compila nel cloud |
| 21/11/2026 | Repository GitHub `PZero/notapad`, privato (superata: vedi sotto) | Progetto condiviso con un amico |
| 21/11/2026 | Repository `PZero/notapad` reso PUBBLICO | Visibilità del progetto; GitHub Pages non è disponibile sui repo privati del piano gratuito |
| 21/11/2026 | README e pagina in inglese; `docs/` resta in italiano | Pubblico internazionale; documenti di lavoro nella lingua del team |
| 21/11/2026 | La pagina animata su GitHub Pages (https://pzero.github.io/notapad/) sostituisce l'artefatto Claude come riferimento | Versione unica, versionata nel repo, aggiornata dal workflow `pages.yml` |
| 21/11/2026 | Agente `comunicazione` per README e pagina; `git-readme` fa CHANGELOG, controllo segreti/privacy, commit e push | Separare comunicazione e custodia del repo |
| 21/11/2026 | Licenza: da decidere (superata: vedi sotto) | Non scelta; il README dice "to be decided" |
| 21/11/2026 | Caricatore MCP73831T-2ACI/OT (C424093) al posto del TP4054, carica 50 mA, uscita STAT su P0.07 | Stesso componente del tag SwimTimer: un solo Extended da pagare in un pannello unico; stessa piedinatura |
| 21/11/2026 | Scheda a 4 strati, 1,0 mm (In1 GND continuo, In2 segnali e alimentazioni) | A 2 strati restavano 7 collegamenti aperti; Economic PCBA JLC non accetta 4 strati da 0,8 mm |
| 21/11/2026 | Lunghezza della scheda fissata a 38 mm (monolite ~41 mm) | A 35 mm restavano 4 collegamenti aperti; a 38 mm DRC pulito al primo giro |
| 21/11/2026 | Lo spessore del monolite può crescere di 1–2 mm | Non è un vincolo per l'utente: apre a batterie da 5 mm |
| 21/11/2026 | Piste di alimentazione lasciate a 0,2 mm (3V3 a 0,15 mm) | Bastano per i consumi (picco motorino compreso); allargarle avrebbe richiesto un nuovo sbroglio |
| 21/11/2026 | Export per JLC, PCBWay e ALLPCB in `kicad/fab_out/` con `genera_fab.py`, che sostituisce `kicad/jlc_out/` | Confronto dei preventivi tra tre fornitori |
| 21/11/2026 | Batteria LiPo 502025 scartata | 20 mm di larghezza: più del monolite (17,5 mm) |
| 21/11/2026 | Modulo E73-2G4M08S1CX (C2764963) scartato | Datasheet: solo connettore IPEX, antenna esterna obbligatoria; la scheda è disegnata per l'antenna stampata del C |
| 21/11/2026 | Strategia v0: montaggio in casa con stencil e piastra riscaldante; prima 5 schede nude, poi lotti più grandi (50 schede ~45 €) | Le spese fisse JLC (~100 € a ordine) si ripagano con l'attrezzatura (~60 €, una volta); errori di rotazione e valori si correggono al banco; i componenti si comprano a blocchi con scorte |
| 21/11/2026 | v0: montaggio JLC Economic, 2 schede montate su 5 (~112 €); E73 e microfoni presi da LCSC nel magazzino JLC. Montaggio in casa per i lotti successivi | NextPCB Rev 0: 199 $ senza microfoni (non disponibili); JLC più economico. Il v0 montato in fabbrica separa gli errori di progetto da quelli di saldatura |
| 21/11/2026 | Microfoni MK1/MK2: rotazione +180° nel CPL per JLC (generata da `genera_fab.py`) | Nell'anteprima JLC il pin 1 del modello C48227730 era opposto al pad 1 dell'impronta; dopo la correzione i puntini coincidono |
| 21/11/2026 | NextPCB Rev 0 scartato per la v0 | Rifiuta i pannelli, chiede 50×50 mm minimi e non ha il microfono MSM261: 199 $ senza microfoni, JLC resta più conveniente |
| 21/11/2026 | NAND resta la W25N02KVZEIR (C3010298, ~10 $) | GD5F2GQ5UEYIGR costa 20,78 $ (25 pz), W25N01GVZEIG 1 Gbit costa 9,69 $, la W25N02KVTBIR a 4,90 $ è un BGA-24 esaurito |
| 21/11/2026 | Finitura ENIG (o HASL senza piombo) e pasta Sn42Bi58 per i ritocchi in casa | Piombo e bismuto insieme fondono a ~96 °C; la bassa temperatura (~170 °C sulla piastra) non rifonde le saldature SAC305 di JLC |
| 21/11/2026 | Valutata la variante con XIAO nRF52840 Plus (20 GPIO, ~20,5 × 37 × 11 mm); email a Seeed Fusion inviata dall'utente (bozza in `docs/seeed_richiesta_en.md`) | Sconto 30% sul PCBA XIAO e possibile sponsorizzazione; la scheda con E73 resta l'alternativa pronta |
| 21/11/2026 | Campioni gratuiti LCSC: solo per ordini > 50 $, max 10 $ e 3 codici al mese; utili MCP73831 (C424093) e LSM6DSV16X (C5267406) | E73, NAND e microfono non sono tra i campioni |
| 21/11/2026 | Solo JLC per la v0 e i lotti successivi: abbandonate la variante XIAO/Seeed Fusion, PCBWay, ALLPCB, NextPCB | Preventivo JLC 97 € per 2 schede montate e spedite; nessun negozio italiano costa meno di LCSC per i chip; la XIAO costa più dell'E73, è larga 17,5 mm e ha 13 GPIO contro i ~20 necessari |
| 21/11/2026 | Niente montaggio in casa: tutte le schede montate da JLC | L'utente non ha piastra, pasta e flussante; montare a metà aumenta solo i costi |
| 21/11/2026 | Q2 resta il 2N7002DW (Extended), niente sostituzione con 2× AO3400A | Nessun 2N7002DW Basic; i due SOT-23 richiederebbero di ripiazzare la zona A e risbrogliare per ~3 € |
| 21/11/2026 | NAND W25N02KV e caricatore MCP73831 restano Extended | Nessuna NAND e nessun caricatore SOT-23-5 (nemmeno i TP4054) nella libreria Basic JLC |
| 21/11/2026 | E73: 2 pezzi (non 3) in pre-order dal Parts Manager JLC verso My Inventory | Senza montaggio in casa la scorta non serve; i pezzi restano a JLC per il PCBA |
| 22/11/2026 | Licenze: CERN-OHL-S-2.0 per l'hardware (`LICENSE-HARDWARE`), MIT per software e documenti (`LICENSE`) | Richieste da NLnet e dagli sponsor; la S (reciproca) obbliga a pubblicare le modifiche all'hardware |
| 22/11/2026 | Sponsor: email a JLCPCB, Ebyte, PCBWay, Seeed Fusion, NextPCB ed Elecrow; NLnet con modulo (non email); firma «The notªpad team» | Abbattere i costi delle prime 2–5 unità, passo necessario prima della fase software; testi in `docs/sponsor_contatti.md` |
| 22/11/2026 | Canale pubblico per gli sponsor: issue fissata #1 su GitHub; README e pagina senza nomi di aziende e senza email personali | Un rifiuto o un silenzio non deve sembrare una vetrina; i nomi si aggiungono solo come «Sponsored by» |
| 22/11/2026 | Lista della spesa invariata dopo il confronto con dema-import.it | Utili solo la batteria 381620 (110 mAh, 3,8 mm) e il flussante; motorini 0820, resina e stagno sottile non ci sono |
| 22/11/2026 | Animazione 3D della pagina: batteria del modello ridotta a 15 × 19 × 3,2 mm e tenuta 0,2 mm dentro il guscio; dimensione nel testo corretta a 41 mm | La faccia posteriore coincidente col guscio causava z-fighting (sfarfallio); 38 mm è la lunghezza della scheda, non del monolite |
