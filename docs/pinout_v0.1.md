# notªpad v0.1 – pinout nRF52840 (modulo E73-2G4M08S1C)

Fonte unica del pinout per elettronica e firmware. Aggiornato il 21/11/2026 dopo la verifica dell'impronta E73; il 24/11/2026 aggiunti microfono con risveglio (VM3011), accelerometro (LIS2DH12) e cicalino.

## Perché è cambiato
Il modulo E73-2G4M08S1C NON porta fuori P0.11, P0.14, P0.16, P0.19, P0.21, P0.23, P0.25, P0.27, P1.01.
Il pinout originale del CLAUDE.md usava proprio quei pin, quindi è stato rifatto.

## Assegnazione (pad E73 → GPIO → segnale)
| Segnale | GPIO | Pad E73 | Note |
|---|---|---|---|
| QSPI_IO0 | P0.00 (XL1) | 11 | niente quarzo 32 kHz: firmware usa LFRC |
| QSPI_SCK | P0.01 (XL2) | 13 | QSPI su pin non dedicati → clock ≤ 8–16 MHz |
| QSPI_IO3 | P0.05 | 15 | |
| QSPI_IO1 | P0.04 | 18 | |
| QSPI_IO2 | P1.09 | 17 | |
| QSPI_CS | P0.12 | 20 | |
| PDM_CLK | P0.26 | 12 | |
| PDM_DATA | P0.06 | 14 | MK1 L/R=GND, MK2 L/R=3V3 (stereo su un filo) |
| MIC_WAKE (DOUT del VM3011, MK2) | P0.03 | 3 | alto = suono sopra soglia in ZPL; si riarma con un breve clock PDM o con DOUT_CLEAR via I2C |
| I2C_SDA | P0.07 | 22 | pull-up interno del nRF (~13 kΩ), 100 kHz; LIS2DH12 0x18, VM3011 0x61. Niente I2C mentre il PDM registra (click nell'audio) |
| I2C_SCL | P0.28 | 4 | come sopra |
| BUZ_G (cicalino, FET 2 di Q4 DMN2004DWK) | P1.13 | 6 | attivo alto, PWM ~4 kHz; cicalino magnetico 4×4 mm sul retro tra BZ+ (VSYS) e BZ− |
| VBUS (5V dei contatti) | – (pin VBUS del nRF) | 27 | rilevamento interno (evento USBDETECTED, sveglia anche da System OFF); sostituisce VBUS_SENSE |
| TOUCH_A (uscita TTP223 U5) | P0.08 | 16 | attivo alto |
| TOUCH_B (uscita TTP223 U6) | P0.31 | 9 | attivo alto |
| MOTOR_G | P0.30 | 10 | FET 1 di Q4 DMN2004DWK (prima AO3400A), attivo alto |
| HOLD (latch alimentazione) | P0.29 | 8 | tenere ALTO subito al boot |
| VBAT_SENSE | P0.02 / AIN0 | 7 | partitore 1M/1M da VSYS (×2) |
| ~~VBUS_SENSE~~ / ~~STAT~~ | – | – | tolti il 24/11 per liberare P0.28 e P0.07 (I2C). Il 5V si legge dal pin VBUS; "in carica" = 5V presente e batteria < ~4,15 V, "carica finita" = 5V presente e tensione ferma a ~4,2 V. STAT dell'MCP73832 resta non collegato |
| NRESET | P0.18 | 26 | abilitare pin reset (CONFIG_GPIO_AS_PINRESET) |
| SWDIO / SWCLK | – | 37 / 39 | contatti posteriori |
| LED1 R / G / B | P0.15 / P0.17 / P0.20 | 28 / 30 / 32 | catodi, attivi BASSI |
| LED2 R / G / B | P0.13 / P0.22 / P0.24 | 33 / 34 / 35 | catodi, attivi BASSI |
| LED3 R / G / B | P1.00 / P1.02 / P1.04 | 36 / 38 / 40 | catodi, attivi BASSI |

## Note per il firmware
- LED: una sola resistenza da 470 Ω sull'anodo comune di ogni LED (non più una per colore). Accendere UN colore alla volta per LED; i colori misti si fanno multiplexando in PWM.
- Nessun quarzo a 32,768 kHz: `CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y`.
- Batteria: avviso a 3,65 V, spegnimento a 3,50 V portando HOLD basso.
- Watchdog sempre attivo. Su LATCH_ON c'è 1 µF + 1 MΩ: il latch regge circa 0,5 s durante un reset, quindi HOLD va rimesso alto entro ~300 ms dal boot.
- Standby (24/11): PDM spento → il VM3011 entra in ZPL (~10 µA) e alza MIC_WAKE sul suono; il nRF dorme con il GPIO come sveglia, poi riaccende il clock PDM (audio valido dopo 0,2 ms). L'MSM261 (MK1) a clock fermo è spento.
- Find Hub / Find My: LIS2DH12 letto via I2C ogni 10 s in stato "separato" (rotazione > 10° = movimento), cicalino ≥ 60 phon a 25 cm per "Play sound".
- Pad E73 ancora liberi: 1 (P1.11), 2 (P1.10), 41 (P0.09/NFC1), 42 (P1.06), 43 (P0.10/NFC2) sono nel keepout dell'antenna; 25 (DCC), 29/31 (USB D−/D+) non sono GPIO.
- Questo pinout può ancora cambiare durante lo sbroglio: nel firmware tenerlo in un unico overlay devicetree.
