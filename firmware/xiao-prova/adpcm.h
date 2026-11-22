// notªpad – codifica IMA ADPCM a 4 bit (standard, uguale al decodificatore di app/adpcm.js) e CRC32.
#pragma once
#include <stdint.h>

static const int16_t ADPCM_PASSI[89] = {
  7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107,
  118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
  1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894,
  6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794,
  32767};
static const int8_t ADPCM_INDICI[16] = {-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8};

struct AdpcmStato {
  int32_t pred = 0;
  int32_t indice = 0;
};

static inline uint8_t adpcmCodifica(AdpcmStato &s, int16_t x) {
  int32_t passo = ADPCM_PASSI[s.indice];
  int32_t diff = (int32_t)x - s.pred;
  uint8_t cod = 0;
  if (diff < 0) { cod = 8; diff = -diff; }
  int32_t delta = passo >> 3;
  if (diff >= passo) { cod |= 4; diff -= passo; delta += passo; }
  passo >>= 1;
  if (diff >= passo) { cod |= 2; diff -= passo; delta += passo; }
  passo >>= 1;
  if (diff >= passo) { cod |= 1; delta += passo; }
  s.pred += (cod & 8) ? -delta : delta;
  if (s.pred > 32767) s.pred = 32767;
  if (s.pred < -32768) s.pred = -32768;
  s.indice += ADPCM_INDICI[cod];
  if (s.indice < 0) s.indice = 0;
  if (s.indice > 88) s.indice = 88;
  return cod;
}

static inline uint32_t crc32Calcola(const uint8_t *p, uint32_t n) {
  uint32_t c = 0xFFFFFFFFUL;
  while (n--) {
    c ^= *p++;
    for (int k = 0; k < 8; k++) c = (c >> 1) ^ (0xEDB88320UL & (0UL - (c & 1)));
  }
  return ~c;
}
