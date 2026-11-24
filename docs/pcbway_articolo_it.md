# notªpad: un registratore vocale AI indossabile, aperto e di proprietà dell'utente

*Bozza in italiano dell'articolo tecnico per il programma di sponsorizzazione PCBWay (https://www.pcbway.com/project/sponsorpublish). Da tradurre in inglese prima dell'invio. Niente nomi di altri produttori: l'articolo sarà pubblico.*

---

## 1. Contesto

I registratori vocali AI indossabili sono una categoria nuova: registrano la giornata e restituiscono trascrizioni, riassunti e note. Quasi tutti però legano l'utente a un servizio cloud, a un abbonamento e a un'unica AI scelta dal produttore.

notªpad nasce come alternativa aperta e non commerciale. È un piccolo monolite in resina da portare al collo, che:
- registra l'audio tutto il giorno con due microfoni;
- si sincronizza con il telefono via Bluetooth Low Energy;
- lascia la trascrizione e l'organizzazione delle note a un'AI **scelta dall'utente**, tramite un server **MCP (Model Context Protocol)** aperto;
- tiene i dati sotto il controllo dell'utente: la trascrizione può avvenire interamente sul dispositivo dell'utente, senza cloud.

Il progetto è sviluppato da un piccolo gruppo di amici nel tempo libero. È interamente pubblico: hardware sotto licenza **CERN-OHL-S-2.0**, software e documentazione sotto licenza **MIT**.

- Repository: https://github.com/PZero/notapad
- Pagina del progetto: https://pzero.github.io/notapad/

## 2. L'oggetto

- Monolite in resina di circa **41 × 17,5 × 9 mm**, con un anello in acciaio annegato in alto per il laccio.
- **Gesto "stretta"**: due elettrodi capacitivi, uno per fianco. Il comando vale solo se si toccano entrambi, così il contatto con il petto non attiva nulla per errore.
- **3 LED RGB** dietro una fessura frontale da 10 mm e un **motorino di vibrazione** per le notifiche.
- **2 microfoni PDM**: uno frontale e uno superiore (con un canalino verso la faccia superiore), per una registrazione stereo e, in prospettiva, per separare chi parla.
- **4 contatti dorati a vista sul retro**: 5 V e GND per la ricarica, SWDIO e SWCLK per il firmware. Le molle pogo stanno nella basetta, non nel monolite. Più avanti il firmware si aggiornerà anche via Bluetooth (OTA).
- Involucro: per la v0.1 due mezzi gusci stampati in SLA e riempiti di resina epossidica a bassa esotermia. Per la versione finale: master SLA → stampo in silicone → colata piena pigmentata.

## 3. Progetto elettronico (v0.1)

### Scheda
- **16,5 × 38 mm, 4 strati, spessore 1,0 mm**, componenti **solo sul lato superiore**.
- Stackup: F.Cu segnali · In1 piano di massa continuo · In2 segnali e alimentazioni · B.Cu segnali e massa. Keepout dell'antenna su tutti gli strati.
- Regole: pista e spazio 0,10 / 0,10 mm, via 0,25 / 0,45 mm, distanza rame-bordo 0,25 mm.
- Tre zone: **A** (contatti, microfono superiore, caricatore, latch di alimentazione) · **B** (LED, memoria NAND, microfono frontale, regolatore, sensori di tocco) · **C** (modulo radio con l'antenna a filo del bordo, senza rame né batteria sotto).
- Sotto la scheda: motorino Ø 8 × 2 mm e batteria LiPo **381620** con circuito di protezione (circa 110 mAh).

### Componenti principali
| Funzione | Componente |
|---|---|
| MCU + Bluetooth LE | Ebyte E73-2G4M08S1C (nRF52840) |
| Memoria audio | W25N02KV, SPI NAND 256 MB (impronta compatibile con la versione da 512 MB) |
| Microfoni | 2 × MSM261DGT003, PDM, top-port |
| Ricarica | MCP73832 (STAT open-drain), 50 mA |
| Regolatore | XC6206 3,3 V |
| Tocco | 2 × TTP223 |
| LED | 3 × RGB ad anodo comune |
| Latch e reset | AO3401A, 2N7002DW, 1N4148WS |

### Gestione dell'alimentazione
- Il firmware avvisa a 3,65 V e spegne a 3,50 V rilasciando un segnale HOLD: un **latch a P-MOSFET** stacca tutto e il consumo residuo scende sotto i ~5 µA, per proteggere la cella.
- Quando si appoggia il monolite sulla basetta, il 5 V dei contatti riaccende il latch tramite un diodo e manda un impulso di reset al nRF52840: "reset mettendolo in carica", senza pulsanti.
- Watchdog sempre attivo. Il circuito di protezione della cella resta come ultima difesa.

### Metodo di progetto
L'intero progetto KiCad 10 è **generato da script** a partire da un'unica definizione di componenti, reti e piazzamento: schema, scheda, regole, sbroglio automatico, file di produzione (Gerber, distinta base, posizionamento). Un insieme di 69 controlli automatici verifica regole, pinout rispetto ai datasheet, simboli rispetto alle impronte, calcoli dei circuiti, meccanica e coerenza tra i documenti.

Stato della scheda: ERC 0, DRC 0 violazioni, 0 collegamenti aperti, schema e scheda allineati.

### Stime (da confermare con l'hardware reale)
- Consumo medio ~4,6 mA in registrazione (somma dai datasheet) → circa **20 ore** di batteria con la cella da 110 mAh, con poco margine finché il convertitore DC-DC non è confermato.
- Audio LC3 stereo 2 × 24 kbit/s → circa 216 MB per 10 ore: la NAND da 256 MB contiene **11–12 ore di registrazione continua**. Il limite è quindi la memoria, non la batteria; la registrazione solo in presenza di suono e la sincronizzazione automatica durante il giorno lo allungano.

## 4. Stato di avanzamento

### Fatto
- Concept, render e scelta delle finiture del monolite.
- Scheda v0.1 completa, verificata e con i file di produzione esportati.
- **Banco di prova software**: in attesa della scheda definitiva, abbiamo portato l'intera catena su una scheda di sviluppo **Seeed XIAO nRF52840 Sense** con batteria (stesso chip nRF52840, microfono PDM, memoria flash).
  - **Firmware di prova**: registra a 16 kHz, comprime in ADPCM, scrive in un buffer circolare in memoria e scarica i dati via BLE con conferma e controllo CRC. Si sincronizza da solo all'80% della memoria. Gesti di tocco per avviare e fermare. **Registra solo quando c'è suono**: soglia adattiva sul rumore di fondo e mezzo secondo di pre-ascolto in RAM.
  - **App di prova** (web app progressiva, Web Bluetooth): scarico, archivio locale e **trascrizione Whisper interamente sul dispositivo dell'utente** (WebGPU/WASM, nessun cloud), separazione di chi parla e comandi vocali.
  - La catena scheda → app è stata provata sull'hardware reale.

### In corso
- Collaudo sul campo di firmware e app: qualità della trascrizione, soglia del suono, consumi.
- Revisione della scheda in base a quanto emerso dai test (vedi §5).

### Prossimi passi
1. **App Android** nativa (oggi l'app è una web app locale).
2. **Architettura del server MCP**: trascrizione, riconoscimento di chi parla e comandi spostati in un servizio aperto, a cui l'utente collega l'AI che preferisce.
3. Firmware definitivo per la scheda (Zephyr / nRF Connect SDK, codec LC3, aggiornamento OTA).
4. Mezzi gusci SLA da 9 mm e primo assemblaggio completo.

## 5. Miglioramenti emersi dai test

Le prove sul banco hanno già cambiato alcune scelte e ci aspettiamo che ne emergano altre nelle prossime settimane. Per questo preferiamo **congelare la scheda solo dopo questa fase**.

- **Standby con risveglio acustico.** Registrare solo quando c'è suono funziona, ma con i microfoni PDM attuali il nRF52840 deve tenerli sempre accesi per "ascoltare", e questo costa qualche mA. Stiamo valutando un microfono con **rilevamento dell'attività acustica integrato**, che risveglia il processore con un interrupt e consuma poche decine di µA (per esempio TDK T5838). L'alternativa è un microfono analogico collegato al comparatore a basso consumo interno al nRF52840. L'obiettivo è allungare molto l'autonomia senza perdere l'inizio delle frasi.
- **Ritrovamento del dispositivo.** Stiamo valutando la compatibilità con le reti di localizzazione degli smartphone. Il nRF52840 e lo stack Nordic supportano già **Google Find Hub**, che è il nostro obiettivo. Per **Apple Find My** serve il programma di certificazione Apple: è da valutare. Qualsiasi soluzione rispetterà le protezioni contro il tracciamento indesiderato (specifica DULT), perché un dispositivo che registra deve essere più che mai rispettoso della privacy.

## 6. Esigenze di produzione

- **Primo lotto: 5 schede montate.**
  - PCB a 4 strati, 1,0 mm, 16,5 × 38 mm, montaggio solo sul lato superiore.
  - Componenti fini: passo minimo del modulo radio, passivi 0402, microfoni PDM, LED 1010.
  - Le 5 unità servono a: 2 prototipi per lo sviluppo del firmware, 1 per i test di consumo e autonomia, 2 per i test di colata e involucro.
- **Eventuale supporto per l'involucro**: mezzi gusci in stampa SLA (resina) per la v0.1 e il master per lo stampo in silicone.
- **Tempi**: i file definitivi (Gerber, distinta base, posizionamento) saranno pronti tra qualche settimana, dopo la revisione del §5. Prima di congelarli adatteremo la distinta base ai componenti disponibili presso lo sponsor, per una compatibilità al 100%.

## 7. Cosa offriamo allo sponsor

- Logo e dicitura "Sponsored by" sul README, sulla pagina del progetto e **sulla serigrafia della scheda**.
- Pubblicazione del progetto sulla piattaforma dello sponsor, con il diario di costruzione, le foto delle schede montate e i file di produzione.
- Citazione in ogni post e video dedicato al progetto.
- Un unico sponsor per la produzione: nessun altro produttore citato come fornitore.
- Apertura a richieste particolari dello sponsor (contenuti, formati, visibilità, dettagli del progetto): le valuteremo insieme e, se fattibili, saremo ben contenti di implementarle.
