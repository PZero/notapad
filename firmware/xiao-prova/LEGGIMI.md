# Firmware di prova notªpad su XIAO nRF52840 Sense

Usa una Seeed XIAO nRF52840 Sense con batteria (microfono PDM, flash QSPI da 2 MB) per provare la catena completa prima che arrivino le schede v0.1: **registrazione → memoria → scarico via Bluetooth → app sul PC**.

**Attenzione:** il firmware usa tutta la flash QSPI della scheda: quello che c'era prima viene sovrascritto.

## Cosa fa (0.1.0)
- All'accensione **registra sempre**: microfono a 16 kHz mono, filtro passa-alto, compressione IMA ADPCM 4 bit (8 KB/s).
- Salva in un **anello di 512 settori da 4 KB** (2 MB ≈ **4 min 20 s** di audio). Ogni settore ha una testata (numero progressivo, ora, stato ADPCM, CRC32) e si decodifica da solo.
- **All'80% della memoria** (~3 min 30 s di audio) alza il flag "da sincronizzare" nello stato e lampeggia di **blu**: se l'app è collegata, scarica da sola. A memoria piena si ferma (LED **rosso**) e riparte da sola quando scende sotto il 95%.
- Un settore viene cancellato **solo dopo che l'app lo ha ricevuto, verificato col CRC e salvato** (ACK). Se un settore arriva male l'app chiede di rimandarlo.
- Batteria: avviso a 3,65 V (LED rosso), spegnimento a 3,50 V (System OFF, si riaccende collegando l'USB o col reset). Watchdog sempre attivo (8 s).
- LED (un lampo da 30 ms ogni 2 s, per consumare poco): blu = da sincronizzare, rosso = piena o batteria bassa, verde = registra con l'USB collegato. Durante lo scarico il blu lampeggia veloce.

Protocollo BLE e formato dei settori: `protocollo.h` (fonte unica, l'app usa gli stessi valori).

## Compilare e caricare
Core `Seeeduino:nrf52` 1.1.13 (già installato), FQBN `Seeeduino:nrf52:xiaonRF52840Sense`. Il compilatore ARM non accetta percorsi con spazi: si compila una copia in `C:\Temp\np`.

```powershell
New-Item -ItemType Directory -Force C:\Temp\np\xiao-prova | Out-Null; Copy-Item firmware\xiao-prova\*.ino, firmware\xiao-prova\*.h C:\Temp\np\xiao-prova\
```
```powershell
arduino-cli compile --fqbn Seeeduino:nrf52:xiaonRF52840Sense --build-property "compiler.cpp.extra_flags=-DCFG_BLE_TASK_STACKSIZE=(256*10)" --build-path C:\Temp\np\build C:\Temp\np\xiao-prova
```
```powershell
arduino-cli upload -p COM15 --fqbn Seeeduino:nrf52:xiaonRF52840Sense --input-dir C:\Temp\np\build
```
La porta (`COM15` è un esempio) si vede con `arduino-cli board list`. Se il caricamento non parte: doppio tocco sul pulsante di reset (LED che pulsa) e si riprova con la nuova porta.

Compilazione del 22/11/2026: sketch 137 808 byte (16 %), RAM globale 31 300 byte (13 %) più 16 KB di buffer PDM allocati all'avvio.

## Diagnostica
- Monitor seriale a 115200: le stesse righe `K ...` / `X ...` che arrivano all'app.
- Comando `INFO` (pulsante "Diagnostica" nell'app): versione, settori usati, campioni persi, ripartenze del PDM, batteria.
- `GAIN n` cambia il guadagno del microfono (0x28 = 0 dB, passi da 0,5 dB; predefinito 0x30 = +4 dB) finché non si riavvia.

## Limiti noti
- Non ancora provato sull'hardware: compilato senza errori, formato e decodifica provati con `node app/test/adpcm.test.mjs`.
- Ora dei settori: il dispositivo non ha un orologio; l'app manda l'ora a ogni collegamento. Le registrazioni fatte prima del primo collegamento hanno solo l'ora relativa all'accensione.
- 2 MB sono pochi (4 minuti): sulla scheda v0.1 la NAND da 256 MB e l'LC3 porteranno a ~10 ore.

## Doppio tocco (22/11/2026)
Doppio tocco sul dispositivo = avvia/ferma la registrazione (IMU LSM6DS3TR-C, rilevamento hardware, interruzione su INT1). Conferma: 3 lampi verdi (avvia) o rossi (ferma); nel registro dell'app compare `K tap rec 1/0`, oppure `X IMU ...` se l'IMU non risponde. Compilato e caricato, non ancora provato a mano.

## Registra solo quando c'è suono (0.2.0, 23/11/2026)
- Il microfono resta acceso, ma nel silenzio non si scrive niente in memoria. Ogni 20 ms il firmware misura il livello, cioè la media del valore assoluto dei campioni. È suono se supera sia 3 volte il rumore di fondo (che si adatta da solo) sia un minimo fisso (120), per almeno 40 ms di fila.
- **Pre-ascolto:** l'ultimo mezzo secondo resta sempre in RAM. Al primo suono il settore nuovo parte da 0,5 s prima, così l'inizio della prima parola c'è.
- Dopo 3 s senza suono il settore si chiude e si torna ad ascoltare. Durante la finestra di un comando (tocco singolo) si scrive sempre.
- Nello stato il bit 7 vale «in ascolto»: nell'app compare il chip «in ascolto» al posto di «registra».
- Comandi: `VAD 0` registra sempre (come la 0.1), `VAD 1` solo col suono (predefinito), `VAD <n>` cambia il minimo (2–5000). `INFO` aggiunge una riga con il livello attuale, il fondo e la percentuale di audio scritta.
- L'app rimette i silenzi, al massimo 60 s per buco, quando ricompone una registrazione. Così ascolto, ore e trascrizione restano allineati col tempo vero, e una pausa resta dentro la stessa registrazione.
- Compilato (142 204 byte, RAM globale 47 772 byte) e caricato il 23/11. Da provare a mano: la soglia 120 è una stima e va tarata con `INFO`.

## Tocco singolo = comando (22/11/2026)
Tocco singolo (se entro 600 ms non arriva il secondo): 5 lampi gialli, taglio dell'audio, i 6 s seguenti diventano un pezzo a sé, poi secondo taglio e la registrazione continua (se era ferma, si ferma di nuovo). Appena i settori sono in flash il firmware manda `K cmd <primo seq> <ultimo seq>` e, se collegato, scarica **solo** quei settori; l'app li trascrive per primi ed esegue il comando senza bisogno della parola «Comando». Compilato e caricato, non provato a mano.
