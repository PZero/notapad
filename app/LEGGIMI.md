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

## File
- `index.html`, `app.js`: interfaccia, Bluetooth, IndexedDB.
- `adpcm.js`: formato dei settori, decodifica ADPCM, CRC32, WAV, raggruppamento. È lo specchio di `firmware/xiao-prova/protocollo.h` e `adpcm.h`.
- `sw.js`, `manifest.webmanifest`, `icone/`: installazione come app.
- `test/adpcm.test.mjs`: prove del formato (`node app/test/adpcm.test.mjs`).

## Provato / non provato (22/11/2026)
- Provato: `node app/test/adpcm.test.mjs` (CRC32, ADPCM andata e ritorno 31,7 dB, settori pieni e parziali, CRC che scopre un bit sbagliato, raggruppamento, WAV). La pagina si apre senza errori nel browser di prova, la lista e la riproduzione funzionano con settori finti in IndexedDB.
- Non provato: il collegamento Bluetooth vero con il dispositivo e l'installazione come app. Il service worker non si registrava nel browser integrato usato per la prova: va verificato in Edge.
