# notªpad – contesto del progetto

Registratore AI indossabile fai-da-te, stile Plaud/Omi: un monolite di resina da portare al collo che registra tutto il giorno, si sincronizza via Bluetooth e lascia la trascrizione e l'organizzazione delle note a un'AI scelta dall'utente (tramite un server MCP aperto). Progetto dell'utente con un amico (repo pubblico: niente nomi né città nei file). Lingua di lavoro: italiano.

Questo file riassume una lunga conversazione su claude.ai (21 novembre 2026). Le decisioni qui sotto sono già prese dall'utente: non rimetterle in discussione senza motivo.

## Link
- Documento di progetto hardware (Claude Docs, sempre aggiornato): https://claude.ai/artifact/6a2wrKuLfgengGXYKWjrQz
- Pagina di presentazione animata (GitHub Pages): https://pzero.github.io/notapad/  (sorgente: `pagina/index.html`, pubblicata dal workflow `pages.yml`; l'artefatto Claude è stato cancellato)

## Oggetto finale
- Monolite in resina circa 41 × 17,5 × **9 mm** (22/11: a 8 mm, con E73 alto 3 mm e cella 381620 da 3,8 mm, restavano 0,1 mm di resina per faccia; a 9 mm ne restano 0,6; era 38 mm: +3 mm per la scheda allungata il 21/11, stesso margine di resina; lo spessore può crescere di 1–2 mm senza problemi), aspetto finale scelto tra 6 finiture (render in `render/`). Le venature "radica" non sono piaciute.
- Anello in acciaio in alto, annegato con boccola: non deve potersi staccare.
- Sensori di tocco su ENTRAMBI i fianchi (listelli metallici = elettrodi): il tocco vale solo se attivi tutti e due (gesto "stretta"), per evitare attivazioni dal petto.
- 3 LED RGB dietro una fessura frontale da 10 mm; motorino di vibrazione per le notifiche.
- 2 microfoni PDM: uno frontale (foro sulla faccia anteriore) e uno superiore con risveglio acustico (VM3011, bottom-port: foro metallizzato nella scheda e canalino nella resina verso la faccia superiore, accanto all'anello). In più accelerometro LIS2DH12 e cicalino magnetico 4×4 mm sul retro (24/11), richiesti per Google Find Hub / Apple Find My (specifica DULT: emettitore sonoro ≥ 60 phon a 25 cm).
- 4 contatti dorati a vista sul retro, in coppie sul bordo alto: 5V, GND (ricarica) e SWDIO, SWCLK (firmware via cavo nella v0.1; poi anche OTA via BLE). Sono un elemento estetico distintivo. Le molle pogo stanno nella basetta, non sul monolite.
- Colata: JLC non annega l'elettronica. v0.1 = due mezzi gusci SLA da JLC3DP + riempimento epossidico a bassa esotermia; versione finale = master SLA → stampo silicone → colata piena pigmentata.

## Elettronica v0.1 (decisa)
- Scheda 16,5 × 38 mm, **4 strati, 1,0 mm** (F.Cu segnali / In1 GND continuo / In2 segnali e alimentazioni / B.Cu segnali e GND; keepout antenna su tutti gli strati; a 2 strati e a 35 mm non si chiudeva; Economic PCBA non accetta 4 strati da 0,8 mm), HASL, componenti SOLO sul lato superiore (JLCPCB Economic PCBA, 2 montate su 5 per il primo giro; finitura ENIG o HASL senza piombo, perché i lotti successivi si montano in casa con pasta Sn42Bi58). Serigrafia «notªpad v0.1» sul lato inferiore.
- Zone dall'alto: A 0–7 mm (pin, MK2 VM3011, caricatore MCP73832, latch) · B 7–20 mm (3 LED, NAND, MK1, LDO, TTP223, passivi; corridoi GND sopra e sotto la NAND) · C 20–38 mm (modulo E73, antenna a filo del bordo inferiore con keepout, niente rame né batteria sotto).
- Strato sotto la scheda: motorino Ø8×2 mm sotto la zona A (1,4 mm dalle spalle dei target), batteria LiPo **381620** con PCM (3,8 × 16 × 20 mm, ~110 mAh) da y 12,8 fino al keepout dell'antenna (~33 mm). Contatti J1–J4: target 2,0 × 4,0 mm in fori da 1,1 mm, la punta esce di 0,1 mm dal retro del monolite da 9 mm.
- Componenti principali (codici LCSC): E73-2G4M08S1C nRF52840 C356849 · W25N02KVZEIR 256 MB C3010298 (la 512 MB W25N04KV costa >5 € in più: scartata per ora, stessa impronta) · MK1 microfono PDM **MSM261DGT003 C48227730** (top-port) · MK2 **Vesper VM3011-U1 C7149370** (24/11: PDM con risveglio acustico, ZPL ~10 µA, VDD 1,6–3,6 V, bottom-port; LCSC esaurito, Digi-Key a listino; datasheet preliminare) · accelerometro **LIS2DH12TR C110926** (I2C 0x18) · cicalino 4×4 mm a mano (KLJ-4020 C556936 o FST-4020 C391027, volume da verificare) · caricatore **MCP73832T-2ACI/OT C38066** (22/11: sostituisce l'MCP73831 C424093, il cui STAT tri-state alimentato dal 5V portava P0.07 a ~5 V; dal 24/11 STAT non è collegato e P0.07 è I2C_SDA; carica 50 mA con R prog 20 k) · XC6206P332MR-G C5446 · 2× TTP223-BA6-TD C42422127 · 3× LED RGB anodo comune MHPA1010RGBDT C404280 · AO3401A C15127 · **2N7002DW-7-F C83571** (doppio SOT-363: latch + reset, sostituisce i due 2N7002) · **DMN2004DWK-7 C156343** (24/11: doppio N-MOS per motorino + cicalino, al posto dell'AO3400A) · 1N4148WS C2128. Passivi tutti Basic.
- LED: una sola 470 Ω (C25117) sull'anodo comune di ciascun LED (R11–R13), catodi diretti ai GPIO (un colore alla volta per LED). C14 1 µF su LATCH_ON: il latch regge ~0,5 s durante un reset. C6 (100 nF sul VDD del modulo) tolto per mancanza di spazio: restano C5 4,7 µF (0402 C23733, stesso di SwimTimer) + C4 1 µF.
- Progetto KiCad 10 in `kicad/` (tutto generato da script, non disegnato a mano): `notapad_def.py` = fonte unica di componenti, reti e piazzamento · `genera_sch.py` → schema (ERC 0) · `genera_pcb.py` → scheda + regole · catena completa (`NOTAPAD_H=38`, default): `genera_sch.py` → `sbroglia.py 100 protect` → `chiudi_gnd.py tutto` → `rifinisci.py` → `chiudi_gnd.py tutto` → `pulisci.py` → `genera_dxf.py` → `genera_fab.py` → `kicad/fab_out/jlcpcb|pcbway|allpcb/` (Gerber ZIP, BOM, CPL/centroid, LEGGIMI) e aggiorna `jlc/notapad_v0.1_BOM_JLC.csv` e `jlc/notapad_v0.1_collegamenti.csv` (`genera_jlc.py` e `kicad/jlc_out/` superati). Libreria LCSC in `kicad/lib/` (easyeda2kicad, pin resi "passive", serigrafia spostata in F.Fab). Pezzi a mano: `jlc/notapad_v0.1_montaggio_a_mano.csv`.
- Regole (verificate su jlcpcb.com/capabilities, multistrato): pista/spazio 0,10/0,10 mm (min 0,09), via 0,25/0,45 mm (senza sovrapprezzo), rame-bordo 0,25 mm (JLC min 0,2), alimentazioni 0,2 mm, 3V3 0,15 mm (bastano per i consumi).
- Gestione batteria (lezione da altri progetti): firmware avvisa a 3,65 V e spegne a 3,50 V rilasciando HOLD → un latch a P-MOSFET stacca tutto (restano < ~5 µA). Il 5V dei contatti riaccende il latch (diodo), va al pin VBUS del nRF52840 (rilevamento interno, dal 24/11 niente partitore) e dà un impulso di reset (100 nF + 2N7002 su P0.18): "reset mettendolo in carica". Watchdog sempre attivo. PCM della cella come ultima protezione.
- Pin nRF52840: vedi `docs/pinout_v0.1.md` (fonte unica). L'E73 NON porta fuori P0.11/14/16/19/21/23/25/27 e P1.01: il pinout originale è stato rifatto (QSPI su P0.00/P0.01/P0.05/P0.04/P1.09/P0.12, PDM P0.26/P0.06, niente quarzo 32 kHz → LFRC). Dal 24/11: MIC_WAKE P0.03, I2C P0.07/P0.28 (pull-up interni), cicalino P1.13; restano liberi solo pad nel keepout dell'antenna.
- Stime: ~4,6 mA medi → ~20 h con la 381620 da 110 mAh (poco margine senza DCDC; da misurare); audio LC3 2×24 kbit/s → 216 MB per 10 h.

## Stato della scheda
Al 24/11 (con VM3011, LIS2DH12 e pilota del cicalino): scheda chiusa, ERC 0, DRC 0 violazioni, 0 scollegati, parità 0 (130 via; fori J1–J4 da 1,1 mm dal 22/11). Export pronti in `kicad/fab_out/`, non più bozza. Evitare il montaggio su due lati (Standard PCBA, +~70 $ di spese fisse) e i LED indirizzabili WS2812.

## Prossimo passo (richiesto dall'utente: fare TUTTO senza che lui disegni)
1. FATTO: KiCad 10.0.8, easyeda2kicad, Freerouting 2.5.0 (jar: variabile `FREEROUTING_JAR`, altrimenti `~/tools/freerouting/`).
2. FATTO: pinout E73 verificato (rifatto), microfono sostituito con un top-port.
3. FATTO: progetto KiCad generato, sbrogliato a 4 strati ed esportato.
4. FATTO: preventivo JLC 97 € per 2 schede montate e spedite. SOLO JLC (21/11): XIAO/Seeed, PCBWay, ALLPCB, NextPCB e montaggio in casa abbandonati.
5. Ordine v0 su JLC: E73 (C356849) 2 pezzi in pre-order verso "My Inventory" (coperti da coupon); quando arrivano, selezionarli su U1, controllare l'antenna e pagare (coupon Black Friday fino al 2/12). Pezzi fuori JLC: `acquisti/spesa_amazon.md`.
Firmware e app ripartiti il 22/11 su richiesta dell'utente: firmware di prova su XIAO nRF52840 Sense con batteria (Arduino + Bluefruit) in `firmware/xiao-prova/`, app di prova PWA in `app/` (Web Bluetooth, IndexedDB; locale su Windows, https per Android da pubblicare). Sincronizzazione automatica all'80% della memoria e trascrizione automatica con Whisper nel browser (transformers.js, WebGPU/WASM, solo sul dispositivo). Catena XIAO → app provata con l'hardware il 22/11. Per la scheda definitiva resta l'ipotesi Zephyr; Flutter solo se la PWA su Android non basta.

## Metodo di lavoro e memoria
- Sei il coordinatore e l'unico interlocutore dell'utente. Deleghi ai sottoagenti (`.claude/agents/`) e riporti solo la sintesi. Niente lavoro sul software finché l'utente non lo chiede: è attento ai token e ai costi (ogni componente JLC Extended costa 3 $ a ordine).
- A inizio sessione leggi `docs/STATO.md` (e `docs/DOMANDE-APERTE.md` se serve). Decisioni in `docs/DECISIONI.md`, pinout in `docs/pinout_v0.1.md` (fonte unica per elettronica e firmware).
- Repository GitHub PUBBLICO `PZero/notapad`, ramo `main`. README, pagina e commit in inglese; `docs/` in italiano.
- Comandi: `/stato` dopo `/clear`; `/fine-sessione` per aggiornare i documenti e fare commit e push (poi l'utente digita `/clear`).
