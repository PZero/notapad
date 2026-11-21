# notªpad – contesto del progetto

Registratore AI indossabile fai-da-te, stile Plaud/Omi: un monolite di resina da portare al collo che registra tutto il giorno, si sincronizza via Bluetooth e lascia la trascrizione e l'organizzazione delle note a un'AI scelta dall'utente (tramite un server MCP aperto). Progetto di Fabio, a Genova, con un amico. Lingua di lavoro: italiano.

Questo file riassume una lunga conversazione su claude.ai (21 novembre 2026). Le decisioni qui sotto sono già prese dall'utente: non rimetterle in discussione senza motivo.

## Link
- Documento di progetto hardware (Claude Docs, sempre aggiornato): https://claude.ai/artifact/6a2wrKuLfgengGXYKWjrQz
- Pagina di presentazione animata (artifact HTML): https://claude.ai/artifact/P663jgdXwZrpJRmRDysLiP  (sorgente: `pagina/index.html`)

## Oggetto finale
- Monolite in resina 38 × 17,5 × 8 mm (fallback 9 mm), aspetto finale scelto tra 6 finiture (render in `render/`). Le venature "radica" non sono piaciute.
- Anello in acciaio in alto, annegato con boccola: non deve potersi staccare.
- Sensori di tocco su ENTRAMBI i fianchi (listelli metallici = elettrodi): il tocco vale solo se attivi tutti e due (gesto "stretta"), per evitare attivazioni dal petto.
- 3 LED RGB dietro una fessura frontale da 10 mm; motorino di vibrazione per le notifiche.
- 2 microfoni PDM: uno frontale (foro sulla faccia anteriore) e uno superiore (canalino verso la faccia superiore, accanto all'anello).
- 4 contatti dorati a vista sul retro, in coppie sul bordo alto: 5V, GND (ricarica) e SWDIO, SWCLK (firmware via cavo nella v0.1; poi anche OTA via BLE). Sono un elemento estetico distintivo. Le molle pogo stanno nella basetta, non sul monolite.
- Colata: JLC non annega l'elettronica. v0.1 = due mezzi gusci SLA da JLC3DP + riempimento epossidico a bassa esotermia; versione finale = master SLA → stampo silicone → colata piena pigmentata.

## Elettronica v0.1 (decisa)
- Scheda 16,5 × 35 mm, 2 strati, 0,8 mm, HASL, componenti SOLO sul lato superiore (JLCPCB Economic PCBA, 2 montate su 5 per il primo giro). Serigrafia «notªpad v0.1» sul lato inferiore.
- Zone dall'alto: A 0–7 mm (pin, MK2, TP4054, latch) · B 7–17 mm (3 LED, NAND, MK1, LDO, TTP223, passivi) · C 17–35 mm (modulo E73, antenna a filo del bordo inferiore con keepout, niente rame né batteria sotto).
- Strato sotto la scheda: motorino Ø8×2 mm sotto la zona A, batteria LiPo con PCM ~3,5 × 16 × 19 mm (~60 mAh) fino al bordo dell'antenna.
- Componenti principali (codici LCSC): E73-2G4M08S1C nRF52840 C356849 · W25N02KVZEIR 256 MB C3010298 (la 512 MB W25N04KV costa >5 € in più: scartata per ora, stessa impronta) · 2× microfono PDM LMD3526B261-OA1 C5373238 (VERIFICARE che sia top-port) · TP4054 C5381776 (carica 50 mA, R prog 20 k) · XC6206P332MR-G C5446 · 2× TTP223-BA6-TD C42422127 · 3× LED RGB anodo comune MHPA1010RGBDT C404280 · AO3401A C15127 · 2N7002 C8545 · AO3400A C20917 · 1N4148WS (da scegliere, Basic).
- Distinta completa: `jlc/notapad_v0.1_BOM_JLC.csv`; collegamenti rete per rete: `jlc/notapad_v0.1_collegamenti.csv`; contorno e zone: `jlc/notapad_v0.1_contorno.dxf`; pezzi a mano: `jlc/notapad_v0.1_montaggio_a_mano.csv`; generatore: `jlc/genera.py`.
- Gestione batteria (lezione da altri progetti): firmware avvisa a 3,65 V e spegne a 3,50 V rilasciando HOLD → un latch a P-MOSFET stacca tutto (restano < ~5 µA). Il 5V dei contatti riaccende il latch (diodo) e dà un impulso di reset al nRF52840 (100 nF + 2N7002 su P0.18): "reset mettendolo in carica". Watchdog sempre attivo. PCM della cella come ultima protezione.
- Pin nRF52840: QSPI SCK P0.19, CS P0.17, IO0–3 P0.20–P0.23 · PDM CLK P0.26, DATA P0.27 · AIN0 P0.02 batteria · tocco A/B P0.06/P0.08 · CHRG P0.07 · 5V presente P0.12 · HOLD P0.11 · LED1 P0.13/14/15, LED2 P0.24/P0.25/P1.00, LED3 P1.01/P1.02/P1.04 · motorino P0.16 · RESET P0.18. Da confermare sul pinout reale dell'E73.
- Stime: ~4,6 mA medi → ~11,5 h con 60 mAh; audio LC3 2×24 kbit/s → 216 MB per 10 h.

## Problema aperto principale
Le zone A+B sono molto dense (~280 mm² disponibili). Se non ci sta: 2N7002 doppio SOT-363, BAT54C, reti resistive 4×0402 per i LED. Evitare il montaggio su due lati (Standard PCBA, +~70 $ di spese fisse) e i LED indirizzabili WS2812 (forzano lo Standard e consumano a riposo).

## Prossimo passo (richiesto dall'utente: fare TUTTO senza che lui disegni)
1. Installare su questo PC Windows: KiCad (ultima stabile), `pip install easyeda2kicad` per scaricare simboli/impronte/3D ufficiali LCSC dei codici sopra, Freerouting (Java) per lo sbroglio.
2. Verificare pinout E73 e porta dei microfoni sui datasheet; correggere `collegamenti.csv` se serve.
3. Creare il progetto KiCad `notapad_v0.1` (schema dalla netlist CSV, scheda dal DXF), posizionare per zone, sbrogliare, piani di massa, DRC pulito.
4. Esportare per JLCPCB: Gerber ZIP, BOM e CPL (posizionamento) nel formato JLC; controllare rotazioni CPL nell'anteprima JLC.
5. Ordine: Economic PCBA, 0,8 mm, HASL, 2 su 5 montate; usare coupon Black Friday JLC (fino al 2 dicembre) se in tempo.
Firmware (XIAO nRF52840, Zephyr) e app sono IN PAUSA per scelta dell'utente: si riparte dopo la scheda. Per l'app la proposta è Flutter, partendo da Android: nessuno dei due ha un Mac (c'è solo quello della sorella) e iOS si compila nel cloud.

## Metodo di lavoro e memoria
- Sei il coordinatore e l'unico interlocutore dell'utente. Deleghi ai sottoagenti (`.claude/agents/`) e riporti solo la sintesi. Niente lavoro sul software finché l'utente non lo chiede: è attento ai token e ai costi (ogni componente JLC Extended costa 3 $ a ordine).
- A inizio sessione leggi `docs/STATO.md` (e `docs/DOMANDE-APERTE.md` se serve). Decisioni in `docs/DECISIONI.md`, pinout in `docs/pinout_v0.1.md` (fonte unica per elettronica e firmware).
- Repository GitHub privato `PZero/notapad`, ramo `main`. Commit e README in italiano.
- Comandi: `/stato` dopo `/clear`; `/fine-sessione` per aggiornare i documenti e fare commit e push (poi l'utente digita `/clear`).
