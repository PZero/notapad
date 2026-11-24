# Changelog

## 24/11/2026 (board revision)
- electronics: board v0.1 regenerated (16.5 × 38 mm, 4 layers, ERC 0, DRC 0, parity 0, 130 vias): MK2 replaced by the Vesper VM3011 PDM microphone with acoustic wake-up (about 10 µA listening, metallised acoustic hole); new LIS2DH12 accelerometer on I2C; 4×4 mm buzzer on the back driven by Q4, now a DMN2004DWK dual MOSFET shared with the vibration motor; 5V from the contacts goes to the nRF52840 VBUS pin (R6/R7 and STAT read removed); P0.28/P0.07 are now I2C. Reason: acoustic standby and hardware groundwork for Google Find Hub and Apple Find My (DULT: sound emitter mandatory, motion sensor recommended).
- electronics: JLC BOM, placement and Gerber exports regenerated in `kicad/fab_out/` and `jlc/`.
- repo: `kicad/genera_sch.py` stops if a component is missing from the schematic; `kicad/genera_fab.py` corrects the MCP73832 part code in the PCBWay/ALLPCB BOM, no longer drops the acoustic-hole footprint from the placement file, and applies the JLC rotation correction for the MSM261 family. New footprints and symbols for VM3011, LGA-12 (LIS2DH12) and DMN2004DWK.
- docs: `docs/STATO.md`, `docs/DECISIONI.md`, `docs/DOMANDE-APERTE.md`, `docs/pinout_v0.1.md`, `CLAUDE.md` and the `jlc/` files updated.
- repo: test suite `verifica/` extended to 71 tests (new B15 and D16): 45 PASS, 23 WARN, 2 not verifiable, 1 FAIL (E02: JLC page not re-checked).
- firmware and app: no changes yet; the new pinout (VM3011 on P0.03, I2C on P0.28/P0.07) is not implemented in the firmware.
- docs: project page gets a concept animation, section `#find` («Finding a lost notªpad»), showing how an item-finding network would locate a board left behind; README updated to match. No hardware or firmware change.

## 24/11/2026
- docs: README and project page no longer name suppliers; rule added to `.claude/agents/comunicazione.md`; battery life corrected to about 20 h with the 110 mAh cell and about 11–12 h of memory.
- docs: technical article for a sponsorship request in Italian and English (`docs/pcbway_articolo_it.md`, `docs/pcbway_article_en.md`), with a PDF bundle in `docs/pcbway_pdf/` (HTML, PDF, images, form field text in `campi_modulo.md`). Sponsor application under review.
- docs: `docs/STATO.md`, `docs/DECISIONI.md` and `docs/DOMANDE-APERTE.md` updated; the board is not frozen and will be revised in the coming weeks (microphone with acoustic wake-up, Google Find Hub).
- repo: new `/fine-sessione-fast` command (local documents only, no page, README, commit or push); `CLAUDE.md` battery estimate updated; `.gitignore` excludes the private email drafts `docs/pcbway_risposta_it.md` and `docs/pcbway_reply_en.md`.
- electronics: no changes to board, BOM, pinout or JLC export files.
- firmware and app: no changes in this entry.

## 23/11/2026
- app: test app `app/` v0.10.0: Whisper decoder at full precision (fp16/fp32 instead of q4); large-v3-turbo chosen automatically on PCs with WebGPU fp16; audio sent to Whisper in 10–25 s windows cut at pauses (`app/vad.js`), with filters for hallucinations and repetitions and a limited VAD threshold.
- app: voice commands use the same transcriber as the recordings; the separate whisper-base CPU transcriber is removed.
- app: transcription on request: only commands are transcribed automatically; the rest starts with the "Transcribe" and "Transcribe new" buttons.
- app: models can be loaded from `app/modelli/` (git-ignored) or copied from the browser cache with a button; app version shown next to the title; recordings table fixed; silences not recorded by the firmware are restored (up to 60 s per gap).
- app: new unit test `app/test/vad.test.mjs`; adpcm, voices and vad tests pass.
- firmware: XIAO test firmware 0.2.0 (`firmware/xiao-prova/`) writes to memory only when it hears sound (adaptive threshold, 0.5 s pre-roll, 3 s tail); new `VAD 0|1|<n>` command; status flag bit 7 "listening" in `protocollo.h`. Compiled and flashed; not yet tested with real sounds.
- docs: `docs/STATO.md` rewritten, eight new rows in `docs/DECISIONI.md`, `docs/DOMANDE-APERTE.md` updated; README and project page updated by the comunicazione agent.
- repo: `.claude/launch.json` added (local dev server for the app preview); `app/modelli/` added to `.gitignore`.
- electronics: no changes to board, BOM, pinout or JLC export files.

## 22/11/2026 (test bench page)
- docs: project page gets a "test bench" section (`#bench`) with an animated four-step scene: the test board records, syncs over Bluetooth to the local web app, the app runs voice detection, Whisper with a timestamp per word, speaker separation and a voice command, and the next step moves the same blocks into the open MCP server. It replaces six test-bench cards in the progress section; the 15 "Done" cards are now a single compact card.
- docs: README updated (update of 22 Nov, status and roadmap, project history); home-automation references removed from the README and the project page.
- docs: `docs/STATO.md`, `docs/DECISIONI.md` (one new row: the test board and app are a bench, features move to the MCP server) and `docs/DOMANDE-APERTE.md` updated.
- electronics: no changes to board, BOM, pinout or JLC export files.
- firmware and app: no changes in this entry.

## 22/11/2026 (evening)
- firmware: `firmware/xiao-prova/` gains IMU gestures for the test board: double tap starts/stops recording, single tap sends a command confirmed by 5 yellow flashes; 6 s segments around a gesture are marked in the file header and synced with priority. Compiled and flashed to the XIAO nRF52840 Sense; the gesture-to-sync path is not yet verified on the device.
- app: speaker separation added: `app/voci.js` (WeSpeaker embeddings, owner profile as "Me", other voices as "Speaker N", turn assignment with a minimum run length) and `app/vad.js` (voice activity detection); transcript shown in chronological order with per-word timestamps. Unit tests in `app/test/voci.test.mjs` pass together with `app/test/adpcm.test.mjs`.
- app: voice commands for home automation in `app/comandi.js`: recognised with a regular expression (no AI, no cost) and sent to a Home Assistant REST endpoint; the long-lived token is stored only in the browser. First tests with real lights succeeded. Planned to move to the MCP server.
- docs: `docs/STATO.md`, `docs/DECISIONI.md` and `docs/DOMANDE-APERTE.md` updated with the test-bench status; README and project page updated by the comunicazione agent.
- electronics: no changes to board, BOM, pinout or JLC export files.

## 22/11/2026
- app: automatic transcription with Whisper in the browser added: new `app/trascrittore.js` (Web Worker, transformers.js 4.3.2 from jsDelivr, WebGPU or WASM, `onnx-community/whisper-*` models); `app/app.js` stores transcripts in IndexedDB (`trascrizioni`), queues transcription after each sync, shows a timestamp per sentence, exports TXT and filters silence and hallucinations; new Transcription section in `app/index.html`. Tested: 17 s of Italian speech transcribed in 4.8 s with whisper-base on WebGPU. Not yet tested on the real device.
- app: `app/sw.js` sends COOP/COEP headers for multithreaded WASM and caches the transcription library; `app/LEGGIMI.md` updated; ADPCM tests still pass.
- docs: `docs/STATO.md` rewritten; three new rows in `docs/DECISIONI.md` (Whisper in the browser; PWA also for Android with Flutter postponed; battery 501520 does not fit the 9 mm monolith); new entries in `docs/DOMANDE-APERTE.md`; firmware/app paragraph in `CLAUDE.md`.
- electronics: no changes to board, BOM, pinout or JLC export files.
- firmware: test firmware `firmware/xiao-prova/` added for a Seeed XIAO nRF52840 Sense with battery (Arduino + Bluefruit): records at 16 kHz in IMA ADPCM on a 512-sector ring in the 2 MB QSPI flash; asks for sync at 80% memory; each sector is erased only after an ACK with CRC32; shutdown at 3.50 V; watchdog. Compiles (16% flash, 13% RAM); not yet tested on the board.
- app: test app `app/` added: a local PWA for Windows (`avvia.cmd` opens localhost:8787; Web Bluetooth, IndexedDB, WAV export); ADPCM tests `app/test/adpcm.test.mjs` pass. Not yet tested with the real device.
- docs: README and project page updated with the firmware and app test status, progress and history; references to a sister project removed.
- electronics: charger changed from MCP73831 to MCP73832T-2ACI/OT (C38066): its STAT output is open-drain, so P0.07 no longer sits near 5 V; same footprint, def, schematic, PCB values, BOM and pinout updated; copper Gerbers unchanged.
- electronics: monolith raised from 8 to 9 mm (page, 3D model, README, CLAUDE.md); battery candidate 381620 (3.8 × 16 × 20 mm) with 501520 as fallback.
- electronics: charging contacts J1–J4 set to 2.0 × 4.0 mm targets in 1.0–1.1 mm holes; export files in `kicad/fab_out/` regenerated (only drill files changed); DRC clean, layer parity clean.
- repo: pre-order verification added in `verifica/`: 69 cross-checks in 8 areas (scripts in `verifica/script/`, results in `verifica/risultati.json`, page `verifica/index.html`, target section drawing); last run 41 PASS, 25 WARN, 1 FAIL (E73 "Standard Only" at JLCPCB, quote to be reconfirmed), 2 N/V.
- repo: wallpaper drafts added in `sfondi/` (8 phone wallpapers as SVG sources and PNG for Android and iPhone, gallery page, scripts); all 8 approved and published, previews in `pagina/sfondi/`, linked from the README and the project page; LED light corrected to three separate lights and the wallpaper 7 captions aligned.
- docs: README and project page updated with the pre-order verification section, progress, history and the 9 mm monolith; `docs/STATO.md`, `docs/DECISIONI.md`, `docs/DOMANDE-APERTE.md` and the hand-assembly list updated.
- repo: licences added: MIT for software and documentation (`LICENSE`), CERN-OHL-S-2.0 for hardware (`LICENSE-HARDWARE`, official SPDX text); README gets license badges and a License section.
- repo: sponsor outreach started: requests drafted for PCB makers and component suppliers in `docs/sponsor_contatti.md` (public company addresses only); public issue #1 "Looking for sponsors: first 2–5 notªpad units" pinned; "Looking for sponsors" section added to the README and the project page.
- docs: `docs/STATO.md` rewritten; 3 new rows in `docs/DECISIONI.md`; sponsor section and battery candidates (501520 or 381620) in `docs/DOMANDE-APERTE.md`.
- docs: README and project page updated (progress, project history, status and roadmap) to 22/11; `.claude/agents/comunicazione.md` updated with the sponsor rules.
- docs: presentation page animation fixed: the flicker (z-fighting) while the monolith rotates came from the internal battery model sharing its back face with the shell; the model battery is now 15 × 19 × 3.2 mm and sits 0.2 mm inside. Not yet checked on the published page.
- docs: monolith size corrected from 38 to 41 × 17.5 × 8 mm in the page text and the "inside" panel (38 mm is the board length); progress and history of the page updated.
- docs: README update (CAD fit check added as next step, project history with the last five milestones); `docs/STATO.md` rewritten; new row in `docs/DECISIONI.md`; two new open questions in `docs/DOMANDE-APERTE.md` (battery fit in the 8 mm thickness, check of the animation on the published page).
- electronics: no changes to components, pinout, board or export files.
- docs: presentation page reworked for phones: the 3D object is framed to fill the free space above the title, a single centred caption replaces the floating labels, hero text fades on scroll, the 3D view hides when the next section arrives, wider exploded-view framing, tighter typography and iPhone safe-area padding. Desktop layout unchanged; tested at 375 and 390 px, not yet on a real iPhone.
- docs: presentation page scenes reworked. The MCP diagram redraws vertically on phones (no more horizontal scroll). The group scene shows two overlapping groups: a note to group A reaches all its members, then a note to group B reaches all of its own, and the person in both gets both. The squeeze scene now shows gestures as points of attention and priority sync on a recording timeline, next to a reassignable "your settings" card; the text says touch, light and vibration behaviours are customisable, like the AI processing.
- docs: battery shortlist narrowed: 602030, 401020, 401230 and 402020 ruled out (too wide, too long or too small for the 8 mm monolith); 381620 (3.8 × 16 × 20 mm, about 110 mAh, estimate from listings) is the candidate, with protection to be confirmed; 501520 only if the monolith goes to 9 mm. Recorded in `docs/DECISIONI.md`, `docs/DOMANDE-APERTE.md`, README, page and shopping list.
- docs: charging contacts decided: flat-head target contacts on the monolith and single pogo pins with magnets in the base, instead of full magnetic connectors; open check of the target shank diameter against the 1.0 mm holes of J1–J4 before ordering the boards.
- docs: README, project page and `docs/STATO.md` updated with the new battery and contact status and the 22/11 milestones (commit links).

## 21/11/2026
- repo: manufacturing route fixed on JLCPCB only (PCBWay, ALLPCB, NextPCB, Seeed XIAO carrier variant and home assembly dropped); quote 97 EUR for 2 assembled and shipped v0.1 boards.
- electronics: E73 nRF52840 module out of stock at JLCPCB; 2 units pre-ordered through the JLC Parts Manager into the JLC warehouse, board order to follow their arrival.
- repo: `acquisti/spesa_amazon.md` added: shopping list for parts outside JLCPCB (LiPo 501520 candidate, 0820 vibration motor, epoxy kit, optional SWD probe and pogo connector), about 40 to 60 EUR (estimate).
- docs: status, decisions (5 new rows), open questions and CLAUDE.md next steps updated; README and presentation page updated by the comunicazione agent (via count 115).
- electronics: JLC pick-and-place file rotates both microphones by +180° (checked on the JLC preview); `kicad/genera_fab.py` now deletes only the folders it regenerates (jlcpcb, pcbway, allpcb).
- electronics: NextPCB exports added in `kicad/fab_out/nextpcb/` (single 51 × 51 mm board) and `kicad/fab_out/nextpcb_pannello52/` (52 × 52 mm panel with one board); NextPCB was then discarded for v0.
- repo: purchasing plan added in `acquisti/` (3-unit order, 10-unit estimate, other distributors for battery and vibration motor).
- docs: draft request to Seeed Fusion for an XIAO nRF52840 Plus variant (`docs/seeed_richiesta_en.md`).
- docs: status, decisions, open questions and CLAUDE.md updated; README and presentation page updated by the comunicazione agent.
- repo: `kicad/pannello/` added to `.gitignore` (it contains files from another project, not for GitHub).
- repo: impostazione del progetto (comandi `/stato` e `/fine-sessione`, agente `git-readme`, documenti di stato in `docs/`).
- elettronica: libreria KiCad dai codici LCSC ufficiali (`kicad/lib/`).
- elettronica: pinout nRF52840 rifatto sui pin realmente disponibili sul modulo E73 (`docs/pinout_v0.1.md`).
- elettronica: microfoni sostituiti con MSM261DGT003 (top-port); una resistenza per LED sull'anodo; C14 sul latch.
- repo: made the repository public; README rewritten in English; presentation page translated and published on GitHub Pages (https://pzero.github.io/notapad/) via .github/workflows/pages.yml; new comunicazione agent.
- electronics: board v0.1 moved to 4 layers, 1.0 mm, 16.5 × 38 mm; ERC 0, DRC 0, 0 unconnected nets, layer parity 0 (at 2 layers 7 nets were still open).
- electronics: MCP73831 charger replaces the TP4054, shared with SwimTimer; STAT on P0.07.
- electronics: battery candidates 501520 and 501525 (502025 rejected, too wide); to be confirmed.
- electronics: production files for JLCPCB, PCBWay and ALLPCB in `kicad/fab_out/`, generated by `kicad/genera_fab.py`; old draft `kicad/jlc_out/` removed.
- repo: new KiCad helper scripts `kicad/rifinisci.py` and `kicad/pulisci.py`; routing preview (`kicad/sbroglio.png`, `kicad/tracce.json`) and outline DXF regenerated.
- docs: status, decisions and open questions updated; README and presentation page updated with progress and history sections.
