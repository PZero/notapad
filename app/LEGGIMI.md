# App di prova notªpad (PWA per Windows, solo locale)

Pagina web installabile che si collega al dispositivo via **Web Bluetooth**, scarica le registrazioni, le salva **nel browser** (IndexedDB, niente cloud) e le fa ascoltare o scaricare in WAV.

## Avvio
1. Serve Python (già sul PC) e **Microsoft Edge o Google Chrome** su Windows 10/11 con il Bluetooth acceso. Firefox non ha Web Bluetooth.
2. Doppio clic su `avvia.cmd`: avvia un piccolo server su `http://localhost:8787` (solo da questo PC) e apre Edge. Web Bluetooth funziona solo da `localhost` o da `https`.
3. **Collega il dispositivo** → scegli `notapad-XXXX` nella finestra del browser.
4. Per installarla come app: menu di Edge → *App* → *Installa questo sito come app*. Per aprirla serve comunque `avvia.cmd` acceso (il server locale).

## Cosa fa
- Mostra memoria usata (con la soglia dell'80%), minuti di audio da scaricare, batteria, firmware.
- **Sincronizza da sola all'80%** (casella attiva per impostazione predefinita) mentre è collegata; c'è anche "Sincronizza ora".
- Se il collegamento cade, ritenta ogni 3 s finché la pagina è aperta. All'apertura prova a ricollegare il dispositivo già autorizzato, se il browser lo permette (`getDevices`).
- Ogni settore viene verificato (testata e CRC32) prima di essere salvato e confermato al dispositivo, che solo allora lo cancella.
- **Registrazioni sul PC:** settori consecutivi raggruppati in registrazioni, con Ascolta, WAV ed Elimina.
- Registro dei messaggi del dispositivo, Diagnostica, Avvia/Ferma registrazione, Svuota memoria (con conferma).

## Trascrizione (Whisper nel browser)
- Dopo ogni sincronizzazione i settori nuovi si trascrivono da soli (casella "Trascrivi da sola"); c'è anche **Trascrivi / Ritrascrivi** su ogni registrazione e l'export **TXT** con l'ora di ogni frase.
- Libreria: **transformers.js 4.3.2** (da cdn.jsdelivr.net, versione fissa) con i modelli `onnx-community/whisper-*`, in un Web Worker (`trascrittore.js`): l'audio non esce dal dispositivo.
- Motore: **WebGPU** se c'è (encoder fp16/fp32 + decoder q4), altrimenti **WASM** con modelli q8. Il service worker aggiunge COOP/COEP, così WASM usa più thread (importante su Android, dove WebGPU spesso manca).
- Modello "automatico": **small** sul PC (~250 MB, buono in italiano), **base** sul telefono (~80 MB). Ci sono anche tiny e large-v3-turbo (solo WebGPU, ~560 MB). Si scarica una volta e resta nella cache del browser (`navigator.storage.persist()`).
- Lingua predefinita: italiano. I pezzi di solo silenzio non vanno a Whisper e le frasi tipiche inventate ("Sottotitoli a cura di…") vengono scartate.
- Un pezzo copre al massimo 600 settori (~5 min). Una frase a cavallo tra due sincronizzazioni può restare spezzata in due.
- Dati: archivio `trascrizioni` in IndexedDB (versione 2 del database), chiave = primo settore del pezzo.
- Android: Chrome ha Web Bluetooth e WebGPU/WASM, ma la pagina va aperta da **https** (localhost vale solo sul PC): serve pubblicare `app/` (per esempio su GitHub Pages).
- Provato (22/11/2026): 17 s di parlato italiano trascritti in 4,8 s con whisper-base su WebGPU, testo corretto quasi parola per parola. Non provati: modello small, WASM, service worker in Edge, telefono Android.

## Chi parla (22/11/2026)
- Whisper non distingue le voci: per ogni frase `trascrittore.js` calcola un'impronta vocale con **WeSpeaker ResNet34** (`onnx-community/wespeaker-voxceleb-resnet34-LM`, 26 MB, sempre WASM fp32: stesso risultato su PC, Android, iPhone).
- `voci.js` confronta le impronte: le frasi simili al profilo del proprietario diventano **Io**, le altre **Interlocutore 1, 2, 3…** (numerati per registrazione). Frasi < 0,5 s: come la precedente. Soglie in testa al file (0,40 / 0,35), da tarare con registrazioni vere.
- Profilo del proprietario (localStorage `np-voce-io`): sezione "La mia voce" (30 s dal microfono) oppure, meglio, toccare l'interlocutore giusto in una trascrizione → «sono io».
- Le trascrizioni già fatte ricevono le impronte da sole all'apertura (senza rifare Whisper). Il TXT esce come `[ora] Io: testo`.
- Dal 22/11 sera: Whisper `_timestamped` con l'ora di ogni parola; impronte su finestre di 1,5 s ogni 0,75 s (Int8), così un cambio di voce a metà frase divide il turno. Cursore "Separazione delle voci" per tarare le soglie. Sul PC con WebGPU fp16 il modello automatico è large-v3-turbo (~560 MB). Le trascrizioni vecchie vanno ritrascritte per avere i turni.
- Provato: `node app/test/voci.test.mjs`. Non provato: il modello vero nel browser e la qualità con voci reali.

## File
- `index.html`, `app.js`: interfaccia, Bluetooth, IndexedDB.
- `trascrittore.js`: worker di Whisper (caricamento del modello, scelta del motore, trascrizione).
- `adpcm.js`: formato dei settori, decodifica ADPCM, CRC32, WAV, raggruppamento. È lo specchio di `firmware/xiao-prova/protocollo.h` e `adpcm.h`.
- `sw.js`, `manifest.webmanifest`, `icone/`: installazione come app.
- `test/adpcm.test.mjs`: prove del formato (`node app/test/adpcm.test.mjs`).

## Provato / non provato (22/11/2026)
- Provato: `node app/test/adpcm.test.mjs` (CRC32, ADPCM andata e ritorno 31,7 dB, settori pieni e parziali, CRC che scopre un bit sbagliato, raggruppamento, WAV). La pagina si apre senza errori nel browser di prova, la lista e la riproduzione funzionano con settori finti in IndexedDB.
- Non provato: il collegamento Bluetooth vero con il dispositivo e l'installazione come app. Il service worker non si registrava nel browser integrato usato per la prova: va verificato in Edge.

## Comandi vocali → Home Assistant (22/11/2026)
- `comandi.js`: «Comando, accendi/spegni la luce [della cucina]» riconosciuto con un'espressione regolare (niente AI, niente costi), poi `POST /api/services/light/turn_on|turn_off` all'Home Assistant di casa con un token a lunga durata (salvato solo nel browser).
- Solo comandi detti negli ultimi 10 minuti, una volta sola, e con la voce del proprietario se il profilo esiste.
- Home Assistant deve accettare la pagina: in `configuration.yaml` → `http: cors_allowed_origins: [http://localhost:8787]`, poi riavvio.
- Limite: il comando arriva solo dopo una sincronizzazione (oggi all'80% o con "Sincronizza ora"). Per la luce "subito" servirà una modalità comando in tempo reale nel firmware.
- Non provato con un Home Assistant vero.

## Velocità e ordine (22/11/2026 sera)
- `vad.js`: prima di Whisper si tengono solo i tratti con voce (energia sopra 3× il rumore di fondo, margini 0,3 s, buchi < 0,8 s chiusi), uniti con 0,3 s di pausa; i tempi di parole e finestre tornano quelli veri. Prova sintetica: 60 s con 7 s di voce → 8,8 s a Whisper. Se il parlato supera l'85% si manda tutto.
- Comando a metà di uno scarico lungo: il firmware passa avanti i settori del comando e poi riprende; l'app lo trascrive appena è arrivato tutto (`K cmd …`), prima del resto.
- Il testo di una registrazione è sempre in ordine di tempo (parole e finestre ordinate), qualunque sia stato l'ordine di scarico o di trascrizione.
