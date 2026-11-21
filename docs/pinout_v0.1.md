# notªpad v0.1 – pinout nRF52840 (modulo E73-2G4M08S1C)

Fonte unica del pinout per elettronica e firmware. Aggiornato il 21/11/2026 dopo la verifica dell'impronta E73.

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
| TOUCH_A (uscita TTP223 U5) | P0.08 | 16 | attivo alto |
| TOUCH_B (uscita TTP223 U6) | P0.31 | 9 | attivo alto |
| MOTOR_G | P0.30 | 10 | AO3400A, attivo alto |
| HOLD (latch alimentazione) | P0.29 | 8 | tenere ALTO subito al boot |
| VBAT_SENSE | P0.02 / AIN0 | 7 | partitore 1M/1M da VSYS (×2) |
| VBUS_SENSE | P0.28 | 4 | 5V presente = alto (partitore 100k/100k) |
| STAT (MCP73831) | P0.07 | 22 | pull-up interno; basso = in carica, alto = carica completa, alta impedenza = niente 5V/niente batteria (ex CHRG del TP4054) |
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
- Questo pinout può ancora cambiare durante lo sbroglio: nel firmware tenerlo in un unico overlay devicetree.
