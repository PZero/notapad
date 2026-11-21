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
| 21/11/2026 | Licenza: da decidere | Non scelta; il README dice "to be decided" |
| 21/11/2026 | Caricatore MCP73831T-2ACI/OT (C424093) al posto del TP4054, carica 50 mA, uscita STAT su P0.07 | Stesso componente del tag SwimTimer: un solo Extended da pagare in un pannello unico; stessa piedinatura |
| 21/11/2026 | Scheda a 4 strati, 1,0 mm (In1 GND continuo, In2 segnali e alimentazioni) | A 2 strati restavano 7 collegamenti aperti; Economic PCBA JLC non accetta 4 strati da 0,8 mm |
| 21/11/2026 | Lunghezza della scheda fissata a 38 mm (monolite ~41 mm) | A 35 mm restavano 4 collegamenti aperti; a 38 mm DRC pulito al primo giro |
| 21/11/2026 | Lo spessore del monolite può crescere di 1–2 mm | Non è un vincolo per l'utente: apre a batterie da 5 mm |
| 21/11/2026 | Piste di alimentazione lasciate a 0,2 mm (3V3 a 0,15 mm) | Bastano per i consumi (picco motorino compreso); allargarle avrebbe richiesto un nuovo sbroglio |
| 21/11/2026 | Export per JLC, PCBWay e ALLPCB in `kicad/fab_out/` con `genera_fab.py`, che sostituisce `kicad/jlc_out/` | Confronto dei preventivi tra tre fornitori |
| 21/11/2026 | Batteria LiPo 502025 scartata | 20 mm di larghezza: più del monolite (17,5 mm) |
