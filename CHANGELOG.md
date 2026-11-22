# Changelog

## 22/11/2026
- electronics: charger changed from MCP73831 to MCP73832T-2ACI/OT (C38066): its STAT output is open-drain, so P0.07 no longer sits near 5 V; same footprint, def, schematic, PCB values, BOM and pinout updated; copper Gerbers unchanged.
- electronics: monolith raised from 8 to 9 mm (page, 3D model, README, CLAUDE.md); battery candidate 381620 (3.8 × 16 × 20 mm) with 501520 as fallback.
- electronics: charging contacts J1–J4 set to 2.0 × 4.0 mm targets in 1.0–1.1 mm holes; export files in `kicad/fab_out/` regenerated (only drill files changed); DRC clean, layer parity clean.
- repo: pre-order verification added in `verifica/`: 69 cross-checks in 8 areas (scripts in `verifica/script/`, results in `verifica/risultati.json`, page `verifica/index.html`, target section drawing); last run 41 PASS, 25 WARN, 1 FAIL (E73 "Standard Only" at JLCPCB, quote to be reconfirmed), 2 N/V.
- repo: wallpaper drafts added in `sfondi/` (8 phone wallpapers as SVG sources and PNG for Android and iPhone, gallery page, scripts); drafts, not yet approved and not linked from the README or the project page.
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
