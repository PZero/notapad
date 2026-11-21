# notªpad – contesto del progetto

Registratore AI indossabile fai-da-te, stile Plaud/Omi: un monolite di resina da portare al collo che registra tutto il giorno, si sincronizza via Bluetooth e lascia la trascrizione e l'organizzazione delle note a un'AI scelta dall'utente (tramite un server MCP aperto). Progetto di Fabio, a Genova, con un amico. Lingua di lavoro: italiano.

Questo file riassume una lunga conversazione su claude.ai (21 novembre 2026). Le decisioni qui sotto sono già prese dall'utente: non rimetterle in discussione senza motivo.

## Link
- Documento di progetto hardware (Claude Docs, sempre aggiornato): https://claude.ai/artifact/6a2wrKuLfgengGXYKWjrQz
- Pagina di presentazione animata (GitHub Pages): https://pzero.github.io/notapad/  (sorgente: `pagina/index.html`, pubblicata dal workflow `pages.yml`; l'artefatto Claude è stato cancellato)

## Oggetto finale
- Monolite in resina circa 41 × 17,5 × 8 mm (fallback 9 mm; era 38 mm: +3 mm per la scheda allungata il 21/11, stesso margine di resina; lo spessore può crescere di 1–2 mm senza problemi), aspetto finale scelto tra 6 finiture (render in `render/`). Le venature "radica" non sono piaciute.
- Anello in acciaio in alto, annegato con boccola: non deve potersi staccare.
- Sensori di tocco su ENTRAMBI i fianchi (listelli metallici = elettrodi): il tocco vale solo se attivi tutti e due (gesto "stretta"), per evitare attivazioni dal petto.
- 3 LED RGB dietro una fessura frontale da 10 mm; motorino di vibrazione per le notifiche.
- 2 microfoni PDM: uno frontale (foro sulla faccia anteriore) e uno superiore (canalino verso la faccia superiore, accanto all'anello).
- 4 contatti dorati a vista sul retro, in coppie sul bordo alto: 5V, GND (ricarica) e SWDIO, SWCLK (firmware via cavo nella v0.1; poi anche OTA via BLE). Sono un elemento estetico distintivo. Le molle pogo stanno nella basetta, non sul monolite.
- Colata: JLC non annega l'elettronica. v0.1 = due mezzi gusci SLA da JLC3DP + riempimento epossidico a bassa esotermia; versione finale = master SLA → stampo silicone → colata piena pigmentata.

## Elettronica v0.1 (decisa)
- Scheda 16,5 × 38 mm, **4 strati, 1,0 mm** (F.Cu segnali / In1 GND continuo / In2 segnali e alimentazioni / B.Cu segnali e GND; keepout antenna su tutti gli strati; a 2 strati e a 35 mm non si chiudeva; Economic PCBA non accetta 4 strati da 0,8 mm), HASL, componenti SOLO sul lato superiore (JLCPCB Economic PCBA, 2 montate su 5 per il primo giro). Serigrafia «notªpad v0.1» sul lato inferiore.
- Zone dall'alto: A 0–7 mm (pin, MK2, caricatore MCP73831, latch) · B 7–20 mm (3 LED, NAND, MK1, LDO, TTP223, passivi; corridoi GND sopra e sotto la NAND) · C 20–38 mm (modulo E73, antenna a filo del bordo inferiore con keepout, niente rame né batteria sotto).
- Strato sotto la scheda: motorino Ø8×2 mm sotto la zona A, batteria LiPo con PCM ~3,5 × 16 × 19 mm (~60 mAh) fino al bordo dell'antenna. Candidata più capiente: 501520 (5 × 15 × 20 mm, ~80–100 mAh), da confermare; scartate 502025 (troppo larga) ; la 501525 (25 mm) è al limite: il keepout dell'antenna inizia a ~33 mm.
- Componenti principali (codici LCSC): E73-2G4M08S1C nRF52840 C356849 · W25N02KVZEIR 256 MB C3010298 (la 512 MB W25N04KV costa >5 € in più: scartata per ora, stessa impronta) · 2× microfono PDM **MSM261DGT003 C48227730** (top-port verificato sul datasheet; il vecchio LMD3526B261-OA1 era BOTTOM-port, scartato) · caricatore **MCP73831T-2ACI/OT C424093** (stesso del tag SwimTimer per pagare un solo Extended in un pannello unico; stessa piedinatura del TP4054 che sostituisce; carica 50 mA con R prog 20 k; uscita STAT su P0.07) · XC6206P332MR-G C5446 · 2× TTP223-BA6-TD C42422127 · 3× LED RGB anodo comune MHPA1010RGBDT C404280 · AO3401A C15127 · **2N7002DW-7-F C83571** (doppio SOT-363: latch + reset, sostituisce i due 2N7002) · AO3400A C20917 · 1N4148WS C2128. Passivi tutti Basic.
- LED: una sola 470 Ω (C25117) sull'anodo comune di ciascun LED (R11–R13), catodi diretti ai GPIO (un colore alla volta per LED). C14 1 µF su LATCH_ON: il latch regge ~0,5 s durante un reset. C6 (100 nF sul VDD del modulo) tolto per mancanza di spazio: restano C5 4,7 µF (0402 C23733, stesso di SwimTimer) + C4 1 µF.
- Progetto KiCad 10 in `kicad/` (tutto generato da script, non disegnato a mano): `notapad_def.py` = fonte unica di componenti, reti e piazzamento · `genera_sch.py` → schema (ERC 0) · `genera_pcb.py` → scheda + regole · catena completa (`NOTAPAD_H=38`, default): `genera_sch.py` → `sbroglia.py 100 protect` → `chiudi_gnd.py tutto` → `rifinisci.py` → `chiudi_gnd.py tutto` → `pulisci.py` → `genera_dxf.py` → `genera_fab.py` → `kicad/fab_out/jlcpcb|pcbway|allpcb/` (Gerber ZIP, BOM, CPL/centroid, LEGGIMI) e aggiorna `jlc/notapad_v0.1_BOM_JLC.csv` e `jlc/notapad_v0.1_collegamenti.csv` (`genera_jlc.py` e `kicad/jlc_out/` superati). Libreria LCSC in `kicad/lib/` (easyeda2kicad, pin resi "passive", serigrafia spostata in F.Fab). Pezzi a mano: `jlc/notapad_v0.1_montaggio_a_mano.csv`.
- Regole (verificate su jlcpcb.com/capabilities, multistrato): pista/spazio 0,10/0,10 mm (min 0,09), via 0,25/0,45 mm (senza sovrapprezzo), rame-bordo 0,25 mm (JLC min 0,2), alimentazioni 0,2 mm, 3V3 0,15 mm (bastano per i consumi).
- Gestione batteria (lezione da altri progetti): firmware avvisa a 3,65 V e spegne a 3,50 V rilasciando HOLD → un latch a P-MOSFET stacca tutto (restano < ~5 µA). Il 5V dei contatti riaccende il latch (diodo) e dà un impulso di reset al nRF52840 (100 nF + 2N7002 su P0.18): "reset mettendolo in carica". Watchdog sempre attivo. PCM della cella come ultima protezione.
- Pin nRF52840: vedi `docs/pinout_v0.1.md` (fonte unica). L'E73 NON porta fuori P0.11/14/16/19/21/23/25/27 e P1.01: il pinout originale è stato rifatto (QSPI su P0.00/P0.01/P0.05/P0.04/P1.09/P0.12, PDM P0.26/P0.06, niente quarzo 32 kHz → LFRC).
- Stime: ~4,6 mA medi → ~11,5 h con 60 mAh; audio LC3 2×24 kbit/s → 216 MB per 10 h.

## Stato della scheda
Al 21/11: scheda chiusa, ERC 0, DRC 0 violazioni, 0 scollegati, parità 0 (115 via). Export pronti in `kicad/fab_out/`, non più bozza. Evitare il montaggio su due lati (Standard PCBA, +~70 $ di spese fisse) e i LED indirizzabili WS2812.

## Prossimo passo (richiesto dall'utente: fare TUTTO senza che lui disegni)
1. FATTO: KiCad 10.0.8, easyeda2kicad, Freerouting 2.5.0 (jar: variabile `FREEROUTING_JAR`, altrimenti `~/tools/freerouting/`).
2. FATTO: pinout E73 verificato (rifatto), microfono sostituito con un top-port.
3. FATTO: progetto KiCad generato, sbrogliato a 4 strati ed esportato.
4. Preventivo: caricare `kicad/fab_out/jlcpcb/` su JLC; controllare nell'anteprima le rotazioni di D1–D3, MK1/MK2, Q2, E73. Confrontare con PCBWay e ALLPCB.
5. Ordine: Economic PCBA, 4 strati, 1,0 mm, HASL, 2 su 5 montate; usare coupon Black Friday JLC (fino al 2 dicembre) se in tempo.
Firmware (XIAO nRF52840, Zephyr) e app sono IN PAUSA per scelta dell'utente: si riparte dopo la scheda. Per l'app la proposta è Flutter, partendo da Android: nessuno dei due ha un Mac (c'è solo quello della sorella) e iOS si compila nel cloud.

## Metodo di lavoro e memoria
- Sei il coordinatore e l'unico interlocutore dell'utente. Deleghi ai sottoagenti (`.claude/agents/`) e riporti solo la sintesi. Niente lavoro sul software finché l'utente non lo chiede: è attento ai token e ai costi (ogni componente JLC Extended costa 3 $ a ordine).
- A inizio sessione leggi `docs/STATO.md` (e `docs/DOMANDE-APERTE.md` se serve). Decisioni in `docs/DECISIONI.md`, pinout in `docs/pinout_v0.1.md` (fonte unica per elettronica e firmware).
- Repository GitHub PUBBLICO `PZero/notapad`, ramo `main`. README, pagina e commit in inglese; `docs/` in italiano.
- Comandi: `/stato` dopo `/clear`; `/fine-sessione` per aggiornare i documenti e fare commit e push (poi l'utente digita `/clear`).
