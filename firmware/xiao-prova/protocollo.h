// notªpad – protocollo BLE e formato dei settori del firmware di prova (XIAO nRF52840 Sense).
// Fonte unica: l'app (app/app.js) usa gli stessi valori. Tutti i numeri sono little endian.
#pragma once
#include <stdint.h>

#define NP_PROTO 1

// UUID 128 bit: a7d1000X-6e70-4b8f-9c4a-5f3e2b1d0c01 (X: 0 servizio, 1 comandi, 2 stato, 3 dati, 4 risposte).
// Bluefruit vuole i 16 byte al contrario (dal meno significativo).
#define NP_UUID(x) { 0x01, 0x0c, 0x1d, 0x2b, 0x3e, 0x5f, 0x4a, 0x9c, 0x8f, 0x4b, 0x70, 0x6e, (x), 0x00, 0xd1, 0xa7 }

// Comandi (testo, caratteristica 1, scrittura): risposte "K ..." / "X ..." sulla caratteristica 4.
//   STATO              invia subito lo stato
//   REC 1 | REC 0      avvia / ferma la registrazione
//   SYNC | STOP        avvia / ferma lo scarico dei settori
//   ACK i [i ...]      settori ricevuti e verificati: il dispositivo li cancella
//   NAK i              settore arrivato male: lo rimanda
//   TIME <ms>          ora UTC in millisecondi (Date.now()), per datare i settori
//   GAIN <0..80>       guadagno PDM (0x28 = 0 dB, passi da 0,5 dB)
//   WIPE               cancella tutta la memoria
//   INFO               riga di diagnostica
//   VAD 0 | VAD 1      registra sempre / solo quando c'è suono (predefinito, con 0,5 s di pre-ascolto)
//   VAD <2..5000>      livello minimo considerato suono (media del valore assoluto su 20 ms, predefinito 120)

// Stato (caratteristica 2, lettura + notifica, 20 byte)
struct __attribute__((packed)) NpStato {
  uint8_t proto;        // NP_PROTO
  uint8_t flag;         // bit0 registra, bit1 piena, bit2 da sincronizzare (>= 80%), bit3 USB, bit4 scarico attivo,
                        // bit5 ora nota, bit6 batteria bassa, bit7 in ascolto (silenzio: microfono acceso, niente scritto)
  uint16_t usati;       // settori con dati non ancora scaricati
  uint16_t totali;      // settori dell'anello
  uint16_t batteriaMv;
  uint32_t prossimoSeq; // numero del prossimo settore che verrà scritto
  uint32_t accesoS;     // secondi dall'accensione
  uint8_t percento;     // usati * 100 / totali
  uint8_t fw[3];        // versione firmware
};
#define NP_FLAG_REC 0x01
#define NP_FLAG_PIENA 0x02
#define NP_FLAG_SYNC_NEC 0x04
#define NP_FLAG_USB 0x08
#define NP_FLAG_SCARICO 0x10
#define NP_FLAG_ORA 0x20
#define NP_FLAG_BATT_BASSA 0x40
#define NP_FLAG_ASCOLTO 0x80

// Dati (caratteristica 3, notifica): uint16 settore + uint16 offset + al massimo 240 byte del settore.
// Un settore (4096 byte) arriva in 18 pezzi; l'app lo ricompone, controlla magic e CRC, poi manda ACK.

// Settore in flash: 4096 byte = testata da 36 byte + 4060 byte di ADPCM (8120 campioni, 0,51 s a 16 kHz)
#define NP_SETT_BYTE 4096
#define NP_SETT_N 512                 // 2 MB della flash QSPI
#define NP_MAGIC 0x3141504EUL          // "NPA1"
#define NP_CODEC_ADPCM16K 1            // IMA ADPCM 4 bit, mono, 16 kHz, primo campione nel nibble basso
struct __attribute__((packed)) NpTesta {
  uint32_t magic;
  uint32_t seq;         // crescente, mai riusato
  uint32_t avvio;       // identificativo dell'accensione (= primo seq dopo il boot)
  uint32_t ms;          // millis() del primo campione
  uint64_t epocaMs;     // ora UTC del primo campione in ms, 0 se sconosciuta
  int16_t pred;         // stato ADPCM all'inizio del settore
  uint8_t indice;
  uint8_t codec;
  uint16_t campioni;    // campioni validi (8120 se il settore è pieno)
  uint16_t riservato;   // bit 0: settore di un comando vocale (tocco singolo), il resto a 0
  uint32_t crc;         // CRC32 (polinomio 0xEDB88320) dei 4060 byte di dati
};
#define NP_DATI_BYTE (NP_SETT_BYTE - sizeof(NpTesta))
static_assert(sizeof(NpTesta) == 36, "testata da 36 byte");
static_assert(sizeof(NpStato) == 20, "stato da 20 byte");
