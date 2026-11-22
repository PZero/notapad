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
