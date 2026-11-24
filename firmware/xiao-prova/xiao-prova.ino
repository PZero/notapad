// notªpad – firmware di prova per la XIAO nRF52840 Sense: registra dal microfono PDM,
// comprime in IMA ADPCM 16 kHz, salva in un anello di settori sulla flash QSPI da 2 MB e scarica via BLE
// verso l'app (app/). Quando la memoria arriva all'80% lo segnala (stato + LED blu) e l'app collegata scarica da sola.
// Core Seeeduino:nrf52 1.1.13 (Bluefruit), FQBN Seeeduino:nrf52:xiaonRF52840Sense. Istruzioni in LEGGIMI.md.
#include <Arduino.h>
#include <stdarg.h>
#include <bluefruit.h>
#include <PDM.h>
#include <Wire.h>
#include "flash_qspi.h"
#include "adpcm.h"
#include "protocollo.h"

#define FW_MAJ 0
#define FW_MIN 2
#define FW_PAT 0

#define FREQ_HZ 16000
#define SOGLIA_SYNC_PCT 80          // da qui il dispositivo chiede lo scarico
#define RIPARTI_SOTTO_PCT 95        // se si era fermato per memoria piena, riparte quando scende sotto
#define FINESTRA 4                  // settori inviati e non ancora confermati
#define ATTESA_ACK_MS 4000
#define BATT_AVVISO_MV 3650
#define BATT_SPEGNI_MV 3500
#define WDT_SECONDI 8
#define N_BUF 3                     // settori in RAM in attesa di scrittura (12 KB)
#define PDM_BUF_BYTE 8192           // per metà del doppio buffer della libreria: 256 ms a 16 kHz

static FlashQspi flash;
static bool flashOk = false;

// ---------- stato dell'anello ----------
static uint8_t valido[NP_SETT_N / 8];   // settore con dati non ancora scaricati
static uint8_t daCanc[NP_SETT_N / 8];   // settore confermato dall'app, da cancellare
static uint16_t usati = 0;
static uint16_t idxScrittura = 0;       // prossimo settore da scrivere (= il più vecchio quando l'anello è pieno)
static uint32_t prossimoSeq = 1;
static uint32_t idAvvio = 0;
static inline bool haBit(const uint8_t *m, uint16_t i) { return m[i >> 3] & (1 << (i & 7)); }
static inline void metti(uint8_t *m, uint16_t i, bool v) { if (v) m[i >> 3] |= (1 << (i & 7)); else m[i >> 3] &= ~(1 << (i & 7)); }

// ---------- registrazione ----------
static bool registra = true;            // all'accensione registra
static uint32_t lampiFinoMs = 0;        // conferma dei tocchi (vedi servizioTap)
static uint8_t lampiColore = 0;         // 1 verde, 2 rosso, 3 giallo
// modalità comando (tocco singolo): i settori della finestra si scaricano subito
static uint32_t cmdFineMs = 0, cmdSeqDa = 0, cmdSeqA = 0;
static bool cmdAttesa = false, cmdRecPrima = true;
static uint16_t cmdSlotDa = 0, cmdN = 0;  // cmdN > 0: lo scarico manda solo questi settori
static bool cmdRiprendi = false;         // finito il comando, lo scarico completo riprende
static bool fermaPerPiena = false;
static bool pdmAttivo = false;
static int pdmGuadagno = 0x30;          // +4 dB
static uint32_t ultimoPdmMs = 0, ripartenzePdm = 0, campioniPersi = 0;
static int64_t epocaOffset = 0;         // ora UTC - millis(), valida se oraNota
static bool oraNota = false;
static int32_t hpX = 0, hpY = 0;        // filtro passa-alto (toglie la componente continua del PDM)

// ---------- ascolto: si scrive in memoria solo quando c'è suono (23/11) ----------
// Il microfono resta acceso; ogni 20 ms si misura il livello (media del valore assoluto). Nel silenzio i campioni
// vanno solo in un anello di pre-ascolto in RAM (0,5 s): al primo suono si apre un settore datato 0,5 s prima e
// si scrive anche il pre-ascolto, così l'inizio della prima parola non si perde. Dopo VAD_CODA_MS senza suono il
// settore si chiude e si torna ad ascoltare. Durante la finestra di un comando si scrive sempre.
// Suono = livello sopra max(vadMin, fondo × vadFattore), per 2 blocchi di fila (40 ms: non bastano i clic).
#define VAD_BLOCCO 320                  // 20 ms
#define VAD_PRE 8000                    // 0,5 s di pre-ascolto (16 KB di RAM)
#define VAD_CODA_MS 3000
static bool vadOn = true;               // comando VAD 0/1
static uint16_t vadMin = 120;           // comando VAD <n>: livello minimo considerato suono
static const uint8_t vadFattore = 3;
static bool vadAttivo = false;          // suono sentito negli ultimi VAD_CODA_MS: si scrive
static uint32_t vadUltimoMs = 0;
static int16_t pre[VAD_PRE];
static uint16_t preTesta = 0, preN = 0;
static uint32_t bloccoSomma = 0, fondo16 = 0;   // fondo in sedicesimi
static uint16_t bloccoN = 0, livello = 0;
static uint8_t sopra = 0;
static uint32_t campAscoltati = 0, campScritti = 0;

struct BufSett {
  alignas(4) uint8_t b[NP_SETT_BYTE];
  uint16_t campioni;
  bool pronto;                           // pieno, in coda per la flash
};
static BufSett bufs[N_BUF];
static int bufCorr = -1;                 // buffer in riempimento
static int codaTesta = 0, codaN = 0;     // coda circolare di buffer pronti (indici in bufs)
static int coda[N_BUF];
static AdpcmStato adpcm;

// ---------- scrittore della flash (una operazione per giro del loop) ----------
struct Scrittura { bool attiva; int buf; uint16_t sett; bool cancellato; uint8_t passo; };
static Scrittura scr = {};
static uint16_t cursoreCanc = 0;

// ---------- BLE ----------
static const uint8_t U_SERV[16] = NP_UUID(0x00), U_CMD[16] = NP_UUID(0x01), U_STATO[16] = NP_UUID(0x02),
                     U_DATI[16] = NP_UUID(0x03), U_RISP[16] = NP_UUID(0x04);
static BLEService servizio(U_SERV);
static BLECharacteristic chCmd(U_CMD), chStato(U_STATO), chDati(U_DATI), chRisp(U_RISP);
static uint16_t connHdl = BLE_CONN_HANDLE_INVALID;

// comandi ricevuti nella callback BLE, eseguiti nel loop
#define CMD_N 16
#define CMD_LEN 96
static char cmdCoda[CMD_N][CMD_LEN];
static volatile uint8_t cmdTesta = 0, cmdCoda_n = 0;

// scarico
static bool scarico = false;
static uint16_t cursoreInvio = 0;
struct InVolo { uint16_t sett; uint32_t t; };
static InVolo volo[FINESTRA];
static int nVolo = 0;
static bool inviando = false;
static uint16_t settInvio = 0, offInvio = 0;
static uint32_t settoriInviati = 0;

static uint16_t batteriaMv = 0;
static uint8_t battBasse = 0;
static uint32_t ultimoStatoMs = 0, ultimaBattMs = 0;

// ---------- utilità ----------
static void wdtServi() { NRF_WDT->RR[0] = 0x6E524635UL; }
static void wdtAvvia() {
  NRF_WDT->CONFIG = (WDT_CONFIG_SLEEP_Run << WDT_CONFIG_SLEEP_Pos) | (WDT_CONFIG_HALT_Pause << WDT_CONFIG_HALT_Pos);
  NRF_WDT->CRV = WDT_SECONDI * 32768UL - 1;
  NRF_WDT->RREN = WDT_RREN_RR0_Enabled << WDT_RREN_RR0_Pos;
  NRF_WDT->TASKS_START = 1;
}
static bool usb() { return NRF_POWER->USBREGSTATUS & POWER_USBREGSTATUS_VBUSDETECT_Msk; }
static uint8_t percento() { return (uint8_t)((uint32_t)usati * 100 / NP_SETT_N); }
static bool connesso() { return connHdl != BLE_CONN_HANDLE_INVALID; }

static void risp(const char *fmt, ...) {
  char out[100];
  va_list ap; va_start(ap, fmt); int n = vsnprintf(out, sizeof out, fmt, ap); va_end(ap);
  if (n < 0) return;
  if (n > (int)sizeof out - 1) n = sizeof out - 1;
  if (Serial) Serial.println(out);
  if (connesso() && chRisp.notifyEnabled(connHdl)) chRisp.notify(connHdl, out, n);
}

static void led(int pin, bool acceso) { digitalWrite(pin, acceso ? LOW : HIGH); }   // LED RGB attivi bassi

// Tensione della batteria: partitore 1 M / 510 k abilitato da VBAT_ENABLE basso (mai alto), riferimento 3,0 V
static uint16_t leggiBatteria() {
  analogReference(AR_INTERNAL_3_0);
  analogReadResolution(12);
  pinMode(VBAT_ENABLE, OUTPUT);
  digitalWrite(VBAT_ENABLE, LOW);
  delay(2);
  uint32_t s = 0;
  for (int i = 0; i < 8; i++) s += analogRead(PIN_VBAT);
  pinMode(VBAT_ENABLE, INPUT);
  return (uint16_t)((s / 8.0f) * 3000.0f / 4095.0f * 1510.0f / 510.0f);
}

// ---------- anello: scansione all'avvio ----------
static void scandisciAnello() {
  memset(valido, 0, sizeof valido);
  memset(daCanc, 0, sizeof daCanc);
  usati = 0;
  uint32_t maxSeq = 0;
  int maxIdx = -1;
  for (uint16_t i = 0; i < NP_SETT_N; i++) {
    NpTesta t;
    if (flash.readBuffer((uint32_t)i * NP_SETT_BYTE, (uint8_t *)&t, sizeof t) != sizeof t) continue;
    if (t.magic != NP_MAGIC || t.seq == 0xFFFFFFFFUL) continue;
    metti(valido, i, true);
    usati++;
    if (t.seq >= maxSeq) { maxSeq = t.seq; maxIdx = i; }
    if ((i & 63) == 0) wdtServi();
  }
  idxScrittura = (maxIdx < 0) ? 0 : (uint16_t)((maxIdx + 1) % NP_SETT_N);
  prossimoSeq = maxSeq + 1;
  idAvvio = prossimoSeq;
}

// ---------- registrazione ----------
static void pdmAvvia() {
  if (pdmAttivo) return;
  PDM.setBufferSize(PDM_BUF_BYTE);
  if (!PDM.begin(1, FREQ_HZ)) { risp("X pdm non parte"); return; }
  PDM.setGain(pdmGuadagno);
  pdmAttivo = true;
  ultimoPdmMs = millis();
}
static void pdmFerma() {
  if (!pdmAttivo) return;
  PDM.end();
  pdmAttivo = false;
}

static int prendiBuffer() {
  for (int i = 0; i < N_BUF; i++) {
    bool inCoda = false;
    for (int k = 0; k < codaN; k++) if (coda[(codaTesta + k) % N_BUF] == i) inCoda = true;
    if (!inCoda && !(scr.attiva && scr.buf == i)) return i;
  }
  return -1;
}

// chiude il buffer in riempimento (anche se parziale) e lo mette in coda per la flash
static void chiudiBuffer() {
  if (bufCorr < 0) return;
  BufSett &B = bufs[bufCorr];
  NpTesta *t = (NpTesta *)B.b;
  if (B.campioni == 0) { bufCorr = -1; return; }
  t->campioni = B.campioni;
  t->crc = crc32Calcola(B.b + sizeof(NpTesta), NP_DATI_BYTE);
  coda[(codaTesta + codaN) % N_BUF] = bufCorr;
  codaN++;
  bufCorr = -1;
}

static void apriBuffer(uint32_t msInizio) {
  int i = prendiBuffer();
  if (i < 0) return;                                // niente posto: i campioni vanno persi finché la flash non libera
  BufSett &B = bufs[i];
  memset(B.b, 0xFF, sizeof B.b);
  NpTesta *t = (NpTesta *)B.b;
  t->magic = NP_MAGIC;
  t->seq = prossimoSeq++;
  t->avvio = idAvvio;
  t->ms = msInizio;
  t->epocaMs = oraNota ? (uint64_t)((int64_t)t->ms + epocaOffset) : 0;
  t->pred = (int16_t)adpcm.pred;
  t->indice = (uint8_t)adpcm.indice;
  t->codec = NP_CODEC_ADPCM16K;
  t->campioni = 0;
  t->riservato = cmdFineMs ? 1 : 0;              // dentro la finestra del comando
  t->crc = 0;
  B.campioni = 0;
  bufCorr = i;
}

// scrive un campione (già filtrato) nel settore corrente, aprendone uno nuovo se serve
static void scrivi(int16_t y, uint32_t msInizio) {
  if (bufCorr < 0) apriBuffer(msInizio);
  if (bufCorr < 0) { adpcmCodifica(adpcm, y); campioniPersi++; return; }
  BufSett &B = bufs[bufCorr];
  uint8_t c = adpcmCodifica(adpcm, y);
  uint8_t *d = B.b + sizeof(NpTesta) + (B.campioni >> 1);
  if ((B.campioni & 1) == 0) *d = (*d & 0xF0) | c;   // primo campione nel nibble basso
  else *d = (*d & 0x0F) | (c << 4);
  B.campioni++;
  campScritti++;
  if (B.campioni >= NP_DATI_BYTE * 2) chiudiBuffer();
}

static void vadAzzera() { vadAttivo = false; preN = 0; preTesta = 0; bloccoSomma = 0; bloccoN = 0; sopra = 0; }

// fine di un blocco da 20 ms: aggiorna fondo e livello, decide se c'è suono
static void vadBlocco() {
  livello = bloccoSomma / VAD_BLOCCO;
  bloccoSomma = 0; bloccoN = 0;
  uint32_t l16 = (uint32_t)livello * 16;
  if (!fondo16) fondo16 = l16 ? l16 : 16;
  else if (l16 < fondo16) fondo16 = (fondo16 * 7 + l16) / 8;           // scende in fretta
  else fondo16 += (l16 - fondo16) >> 9;                                 // sale piano (~10 s)
  uint32_t soglia = max<uint32_t>(vadMin, fondo16 * vadFattore / 16);
  sopra = livello > soglia ? (sopra < 255 ? sopra + 1 : 255) : 0;
  uint32_t ora = millis();
  if (sopra >= 2) {
    vadUltimoMs = ora;
    if (!vadAttivo) {
      // primo suono: settore datato all'inizio del pre-ascolto, poi il pre-ascolto stesso
      vadAttivo = true;
      chiudiBuffer();
      uint32_t ms0 = ora - (uint32_t)preN * 1000 / FREQ_HZ;
      uint16_t i = (preTesta + VAD_PRE - preN) % VAD_PRE;
      for (uint16_t k = 0; k < preN; k++) { scrivi(pre[i], ms0); i = (i + 1) % VAD_PRE; }
      preN = 0;
    }
  } else if (vadAttivo && !cmdFineMs && ora - vadUltimoMs > VAD_CODA_MS) {
    vadAttivo = false;                                                  // silenzio: si chiude il settore
    chiudiBuffer();
  }
}

static void campione(int16_t x) {
  // passa-alto a una via: y = x - x[-1] + 0,995 * y[-1]
  int32_t y = (int32_t)x - hpX + ((hpY * 32604) >> 15);
  hpX = x;
  hpY = y;
  if (y > 32767) y = 32767;
  if (y < -32768) y = -32768;
  campAscoltati++;
  bool scrive = !vadOn || vadAttivo || cmdFineMs;
  if (scrive) scrivi((int16_t)y, millis());
  else {
    pre[preTesta] = (int16_t)y;
    preTesta = (preTesta + 1) % VAD_PRE;
    if (preN < VAD_PRE) preN++;
  }
  if (vadOn) {
    bloccoSomma += (uint32_t)(y < 0 ? -y : y);
    if (++bloccoN >= VAD_BLOCCO) vadBlocco();
  }
}

static void servizioPdm() {
  if (!pdmAttivo) return;
  static int16_t pcm[512];
  int disp;
  while ((disp = PDM.available()) >= 2) {
    int n = PDM.read(pcm, min(disp, (int)sizeof pcm));
    for (int i = 0; i < n / 2; i++) campione(pcm[i]);
    ultimoPdmMs = millis();
  }
  // la libreria si ferma se un buffer non viene letto in tempo: la si riavvia
  if (millis() - ultimoPdmMs > 1000) {
    pdmFerma();
    pdmAvvia();
    ripartenzePdm++;
    risp("X pdm ripartito (%lu)", ripartenzePdm);
  }
}

static void aggiornaRegistrazione() {
  bool vuole = registra && !fermaPerPiena && flashOk;
  if (vuole && !pdmAttivo) pdmAvvia();
  if (!vuole && pdmAttivo) { pdmFerma(); chiudiBuffer(); vadAzzera(); }
}

// ---------- scrittore della flash ----------
static void servizioFlash() {
  if (!flashOk || flash.occupata()) return;
  if (scr.attiva) {
    uint32_t base = (uint32_t)scr.sett * NP_SETT_BYTE;
    if (!scr.cancellato) { flash.eraseAvvia(base); scr.cancellato = true; return; }
    // pagine 1..15 poi la 0 (con la testata): un settore a metà resta senza magic e non conta
    uint8_t pag = (scr.passo + 1) & 15;
    flash.writeBuffer(base + pag * 256, bufs[scr.buf].b + pag * 256, 256);
    if (++scr.passo < 16) return;
    metti(valido, scr.sett, true);
    usati++;
    idxScrittura = (scr.sett + 1) % NP_SETT_N;
    if (((NpTesta *)bufs[scr.buf].b)->seq == cmdSeqDa) cmdSlotDa = scr.sett;   // primo settore del comando
    scr.attiva = false;
    codaTesta = (codaTesta + 1) % N_BUF;
    codaN--;
    return;
  }
  if (codaN > 0) {
    uint16_t s = idxScrittura;
    if (haBit(valido, s)) {                            // il più vecchio non è ancora stato scaricato: memoria piena
      if (!fermaPerPiena) { fermaPerPiena = true; risp("X memoria piena, registrazione ferma"); }
      return;
    }
    metti(daCanc, s, false);                         // lo cancella comunque lo scrittore
    scr = {true, coda[codaTesta], s, false, 0};
    return;
  }
  // a riposo: cancella un settore già confermato dall'app
  for (uint16_t k = 0; k < NP_SETT_N; k++) {
    uint16_t i = (cursoreCanc + k) % NP_SETT_N;
    if (haBit(daCanc, i)) {
      metti(daCanc, i, false);
      flash.eraseAvvia((uint32_t)i * NP_SETT_BYTE);
      cursoreCanc = (i + 1) % NP_SETT_N;
      return;
    }
  }
}

// ---------- scarico via BLE ----------
static bool inVolo(uint16_t s) {
  for (int i = 0; i < nVolo; i++) if (volo[i].sett == s) return true;
  return false;
}
static void togliVolo(uint16_t s) {
  for (int i = 0; i < nVolo; i++)
    if (volo[i].sett == s) { volo[i] = volo[--nVolo]; return; }
}
static uint16_t piuVecchio() {
  for (uint16_t k = 0; k < NP_SETT_N; k++) {
    uint16_t i = (idxScrittura + k) % NP_SETT_N;
    if (haBit(valido, i)) return i;
  }
  return idxScrittura;
}
static void avviaScarico() {
  scarico = true;
  nVolo = 0;
  inviando = false;
  cursoreInvio = piuVecchio();
  risp("K sync %u settori", usati);
}
static void fermaScarico(const char *motivo) {
  if (!scarico) return;
  scarico = false;
  cmdN = 0; cmdRiprendi = false;
  inviando = false;
  nVolo = 0;
  risp("K sync fine %s, inviati %lu", motivo, settoriInviati);
}

static void servizioScarico() {
  if (!scarico) return;
  if (!connesso() || !chDati.notifyEnabled(connHdl)) { fermaScarico("scollegato"); return; }
  // conferme in ritardo: si riparte dal più vecchio non confermato
  for (int i = 0; i < nVolo; i++)
    if (millis() - volo[i].t > ATTESA_ACK_MS) {
      cursoreInvio = volo[i].sett;
      nVolo = 0;
      inviando = false;
      risp("X sync ritardo, rimando da %u", cursoreInvio);
      break;
    }
  BLEConnection *c = Bluefruit.Connection(connHdl);
  if (!c) return;
  uint16_t utile = c->getMtu() - 3 - 4;
  utile = min<uint16_t>(utile, 240) & ~3;
  if (utile < 16) return;
  for (int giro = 0; giro < 6; giro++) {
    if (!inviando) {
      if (nVolo >= FINESTRA) return;
      bool trovato = false;
      for (uint16_t k = 0; k < NP_SETT_N; k++) {
        uint16_t i = (cursoreInvio + k) % NP_SETT_N;
        if (cmdN && (uint16_t)((i + NP_SETT_N - cmdSlotDa) % NP_SETT_N) >= cmdN) continue;
        if (haBit(valido, i) && !inVolo(i) && !(scr.attiva && scr.sett == i)) { settInvio = i; trovato = true; break; }
      }
      if (!trovato && cmdN && cmdRiprendi) {           // comando inviato: si riprende lo scarico completo
        cmdN = 0; cmdRiprendi = false;
        cursoreInvio = piuVecchio();
        risp("K cmd inviato, riprendo");
        continue;
      }
      if (!trovato) { if (nVolo == 0) fermaScarico("ok"); return; }
      inviando = true;
      offInvio = 0;
    }
    if (flash.occupata()) return;
    uint8_t pkt[4 + 240];
    uint16_t n = min<uint16_t>(utile, NP_SETT_BYTE - offInvio);
    pkt[0] = settInvio & 0xFF; pkt[1] = settInvio >> 8; pkt[2] = offInvio & 0xFF; pkt[3] = offInvio >> 8;
    if (flash.readBuffer((uint32_t)settInvio * NP_SETT_BYTE + offInvio, pkt + 4, n) != n) return;
    if (!chDati.notify(connHdl, pkt, 4 + n)) return;   // coda radio piena: si riprova al prossimo giro
    offInvio += n;
    if (offInvio >= NP_SETT_BYTE) {
      volo[nVolo++] = {settInvio, millis()};
      cursoreInvio = (settInvio + 1) % NP_SETT_N;
      inviando = false;
      settoriInviati++;
    }
    servizioPdm();
  }
}

static void conferma(uint16_t s) {
  togliVolo(s);
  if (s >= NP_SETT_N || !haBit(valido, s)) return;
  metti(valido, s, false);
  metti(daCanc, s, true);
  usati--;
  if (fermaPerPiena && percento() < RIPARTI_SOTTO_PCT) { fermaPerPiena = false; risp("K memoria liberata, riparto"); }
}

// ---------- stato ----------
static void inviaStato() {
  NpStato s = {};
  s.proto = NP_PROTO;
  s.flag = (pdmAttivo ? NP_FLAG_REC : 0) | (fermaPerPiena ? NP_FLAG_PIENA : 0) |
           (percento() >= SOGLIA_SYNC_PCT ? NP_FLAG_SYNC_NEC : 0) | (usb() ? NP_FLAG_USB : 0) |
           (scarico ? NP_FLAG_SCARICO : 0) | (oraNota ? NP_FLAG_ORA : 0) |
           (batteriaMv && batteriaMv < BATT_AVVISO_MV && !usb() ? NP_FLAG_BATT_BASSA : 0) |
           (pdmAttivo && vadOn && !vadAttivo && !cmdFineMs ? NP_FLAG_ASCOLTO : 0);
  s.usati = usati;
  s.totali = NP_SETT_N;
  s.batteriaMv = batteriaMv;
  s.prossimoSeq = prossimoSeq;
  s.accesoS = millis() / 1000;
  s.percento = percento();
  s.fw[0] = FW_MAJ; s.fw[1] = FW_MIN; s.fw[2] = FW_PAT;
  chStato.write(&s, sizeof s);
  if (connesso() && chStato.notifyEnabled(connHdl)) chStato.notify(connHdl, &s, sizeof s);
}

// ---------- comandi ----------
static void esegui(char *c) {
  if (!strcmp(c, "STATO")) { inviaStato(); return; }
  if (!strncmp(c, "REC ", 4)) {
    registra = c[4] == '1';
    if (!registra) fermaPerPiena = false;
    aggiornaRegistrazione();
    risp("K rec %d", registra);
    inviaStato();
    return;
  }
  if (!strcmp(c, "SYNC")) { avviaScarico(); return; }
  if (!strcmp(c, "STOP")) { fermaScarico("chiesto"); return; }
  if (!strncmp(c, "ACK ", 4)) {
    char *p = c + 4;
    while (*p) {
      char *fine;
      long v = strtol(p, &fine, 10);
      if (fine == p) break;
      conferma((uint16_t)v);
      p = fine;
    }
    return;
  }
  if (!strncmp(c, "NAK ", 4)) {
    uint16_t s = (uint16_t)atoi(c + 4);
    togliVolo(s);
    cursoreInvio = s;
    risp("X sync rimando %u", s);
    return;
  }
  if (!strncmp(c, "TIME ", 5)) {
    uint64_t ms = strtoull(c + 5, NULL, 10);
    epocaOffset = (int64_t)ms - (int64_t)millis();
    oraNota = true;
    risp("K ora");
    return;
  }
  if (!strncmp(c, "GAIN ", 5)) {
    int g = atoi(c + 5);
    if (g < 0 || g > 80) { risp("X gain 0..80"); return; }
    pdmGuadagno = g;
    if (pdmAttivo) PDM.setGain(g);
    risp("K gain %d", g);
    return;
  }
  if (!strncmp(c, "VAD ", 4)) {                    // VAD 0 / VAD 1 / VAD <livello minimo>
    int v = atoi(c + 4);
    if (v == 0 || v == 1) {
      vadOn = v == 1;
      if (!vadOn) { vadAttivo = false; preN = 0; }
      else { chiudiBuffer(); vadAzzera(); }
    } else if (v >= 2 && v <= 5000) vadMin = (uint16_t)v;
    else { risp("X vad 0|1|2..5000"); return; }
    risp("K vad %d min %u", vadOn, vadMin);
    return;
  }
  if (!strcmp(c, "WIPE")) {
    fermaScarico("wipe");
    for (uint16_t i = 0; i < NP_SETT_N; i++)
      if (haBit(valido, i)) { metti(valido, i, false); metti(daCanc, i, true); }
    usati = 0;
    fermaPerPiena = false;
    risp("K wipe");
    inviaStato();
    return;
  }
  if (!strcmp(c, "INFO")) {
    risp("K fw %d.%d.%d flash %d usati %u scr %u seq %lu persi %lu pdm-rip %lu batt %u",
         FW_MAJ, FW_MIN, FW_PAT, flashOk, usati, idxScrittura, prossimoSeq, campioniPersi, ripartenzePdm, batteriaMv);
    risp("K vad %d min %u livello %u fondo %lu scritto %lu%%", vadOn, vadMin, livello, fondo16 / 16,
         campAscoltati ? (unsigned long)((uint64_t)campScritti * 100 / campAscoltati) : 0UL);
    return;
  }
  risp("X comando sconosciuto: %s", c);
}

static void suComando(uint16_t, BLECharacteristic *, uint8_t *data, uint16_t len) {
  taskENTER_CRITICAL();                               // la callback gira nel task BLE, il loop in un altro
  if (cmdCoda_n < CMD_N) {
    uint8_t i = (cmdTesta + cmdCoda_n) % CMD_N;
    uint16_t n = min<uint16_t>(len, CMD_LEN - 1);
    memcpy(cmdCoda[i], data, n);
    cmdCoda[i][n] = 0;
    cmdCoda_n++;
  }
  taskEXIT_CRITICAL();
}

static void suConnessione(uint16_t h) {
  connHdl = h;
  BLEConnection *c = Bluefruit.Connection(h);
  c->requestPHY(BLE_GAP_PHY_2MBPS);
  c->requestDataLengthUpdate();
  c->requestMtuExchange(247);
}
static void suDisconnessione(uint16_t, uint8_t) {
  connHdl = BLE_CONN_HANDLE_INVALID;
}

static void avviaBle() {
  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);
  Bluefruit.begin();
  Bluefruit.setTxPower(4);
  char nome[20];
  snprintf(nome, sizeof nome, "notapad-%04X", (unsigned)(NRF_FICR->DEVICEADDR[0] & 0xFFFF));
  Bluefruit.setName(nome);
  Bluefruit.Periph.setConnInterval(6, 12);          // 7,5-15 ms
  Bluefruit.Periph.setConnectCallback(suConnessione);
  Bluefruit.Periph.setDisconnectCallback(suDisconnessione);

  servizio.begin();
  chCmd.setProperties(CHR_PROPS_WRITE | CHR_PROPS_WRITE_WO_RESP);
  chCmd.setPermission(SECMODE_OPEN, SECMODE_OPEN);
  chCmd.setMaxLen(CMD_LEN - 1);
  chCmd.setWriteCallback(suComando);
  chCmd.begin();
  chStato.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  chStato.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  chStato.setFixedLen(sizeof(NpStato));
  chStato.begin();
  chDati.setProperties(CHR_PROPS_NOTIFY);
  chDati.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  chDati.setMaxLen(244);
  chDati.begin();
  chRisp.setProperties(CHR_PROPS_NOTIFY);
  chRisp.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  chRisp.setMaxLen(100);
  chRisp.begin();

  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addService(servizio);
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(160, 800);      // 100 ms per 30 s, poi 500 ms
  Bluefruit.Advertising.setFastTimeout(30);
  Bluefruit.Advertising.start(0);
}

// ---------- batteria e LED ----------
static void spegni() {
  risp("X batteria scarica, spengo");
  pdmFerma();
  chiudiBuffer();
  uint32_t t0 = millis();
  while ((codaN > 0 || scr.attiva) && millis() - t0 < 3000) { servizioFlash(); wdtServi(); delay(1); }
  led(LED_RED, false); led(LED_GREEN, false); led(LED_BLUE, false);
  NRF_POWER->EVENTS_USBDETECTED = 0;
  sd_power_system_off();                             // si riaccende col reset o collegando l'USB
}

static void servizioBatteriaLed() {
  uint32_t ora = millis();
  if (ora - ultimaBattMs > 30000 || !batteriaMv) {
    ultimaBattMs = ora;
    batteriaMv = leggiBatteria();
    if (!usb() && batteriaMv < BATT_SPEGNI_MV) { if (++battBasse >= 3) spegni(); }
    else battBasse = 0;
  }
  // lampeggio da 30 ms ogni 2 s: blu = da sincronizzare, rosso = piena o batteria bassa, verde = registra con USB
  bool fase = (ora % 2000) < 30;
  bool rosso = fermaPerPiena || (batteriaMv && batteriaMv < BATT_AVVISO_MV && !usb());
  bool blu = !rosso && percento() >= SOGLIA_SYNC_PCT;
  bool verde = !rosso && !blu && pdmAttivo && usb();
  if (cmdFineMs && ora >= lampiFinoMs) {          // finestra del comando aperta: giallo fisso
    led(LED_RED, true); led(LED_GREEN, true); led(LED_BLUE, false);
    return;
  }
  if (ora < lampiFinoMs) {                       // conferma del doppio tocco: 3 lampi
    bool on = (ora % 300) < 150;
    led(LED_RED, on && lampiColore >= 2); led(LED_GREEN, on && (lampiColore & 1)); led(LED_BLUE, false);
    return;
  }
  led(LED_RED, fase && rosso);
  led(LED_BLUE, (fase && blu) || (scarico && (ora % 200) < 20));
  led(LED_GREEN, fase && verde);
}

// ---------- tocchi (IMU LSM6DS3TR-C della XIAO Sense, Wire1 0x6A, INT1) ----------
// Doppio tocco = avvia/ferma la registrazione (3 lampi verdi o rossi).
// Tocco singolo = comando: 5 lampi gialli, l'audio si taglia, i prossimi CMD_S secondi diventano un pezzo a sé
// che si scarica subito (l'app lo trascrive ed esegue il comando), poi la registrazione continua.
// Rilevamento nell'IMU (registri da ST AN5130); un singolo diventa "singolo" se entro 600 ms non arriva il secondo.
static const uint8_t IMU = 0x6A;
static const uint32_t CMD_MS = 6000, ATTESA_DOPPIO_MS = 600;
static volatile bool tapArrivato = false;
static bool imuOk = false;
static uint32_t ultimoTapMs = 0, singoloMs = 0;
static void suTap() { tapArrivato = true; }
static bool imuScrivi(uint8_t r, uint8_t v) {
  Wire1.beginTransmission(IMU); Wire1.write(r); Wire1.write(v);
  return Wire1.endTransmission() == 0;
}
static int imuLeggi(uint8_t r) {
  Wire1.beginTransmission(IMU); Wire1.write(r);
  if (Wire1.endTransmission(false) != 0) return -1;
  Wire1.requestFrom(IMU, (uint8_t)1);
  return Wire1.available() ? Wire1.read() : -1;
}
static void avviaTap() {
  pinMode(PIN_LSM6DS3TR_C_POWER, OUTPUT);
  digitalWrite(PIN_LSM6DS3TR_C_POWER, HIGH);
  delay(20);
  Wire1.begin();
  if (imuLeggi(0x0F) != 0x6A) { risp("X IMU assente: niente tocchi"); return; }   // WHO_AM_I
  imuOk = imuScrivi(0x10, 0x60)      // CTRL1_XL: 416 Hz, ±2 g
       && imuScrivi(0x58, 0x8E)      // TAP_CFG: interruzioni attive, tocco su X, Y, Z
       && imuScrivi(0x59, 0x8C)      // TAP_THS_6D: soglia 12/32 del fondo scala (~0,75 g)
       && imuScrivi(0x5A, 0x7F)      // INT_DUR2: durata, quiete e shock massimi (doppio tocco entro ~0,5 s)
       && imuScrivi(0x5B, 0x80)      // WAKE_UP_THS: abilita singolo e doppio tocco
       && imuScrivi(0x5E, 0x48);     // MD1_CFG: singolo e doppio tocco su INT1
  if (!imuOk) { risp("X IMU non configurato"); return; }
  pinMode(PIN_LSM6DS3TR_C_INT1, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_LSM6DS3TR_C_INT1), suTap, RISING);
}
static void lampi(uint8_t colore, uint32_t ms) { lampiColore = colore; lampiFinoMs = millis() + ms; }
static void doppioTocco() {
  registra = !registra;
  if (!registra) fermaPerPiena = false;
  cmdFineMs = 0; cmdAttesa = false;
  aggiornaRegistrazione();
  lampi(registra ? 1 : 2, 900);
  risp("K tap rec %d", registra);
  inviaStato();
}
static void toccoSingolo() {
  if (cmdFineMs || cmdAttesa || !flashOk) return;                  // un comando alla volta
  cmdRecPrima = registra;
  if (!registra) { registra = true; aggiornaRegistrazione(); }
  chiudiBuffer();                                                  // taglio: il comando parte da un settore nuovo
  cmdSeqDa = prossimoSeq;
  cmdFineMs = millis() + CMD_MS;
  lampi(3, 1500);                                                  // 5 lampi gialli
  risp("K cmd ascolto %lu", cmdSeqDa);
}
static void servizioTap() {
  uint32_t ora = millis();
  if (tapArrivato) {
    tapArrivato = false;
    int src = imuLeggi(0x1C);                                      // TAP_SRC: bit4 doppio, bit5 singolo
    if (src >= 0 && (src & 0x10)) {
      singoloMs = 0;
      if (ora - ultimoTapMs > 1000) { ultimoTapMs = ora; doppioTocco(); }
    } else if (src >= 0 && (src & 0x20) && !singoloMs && ora - ultimoTapMs > 1000) singoloMs = ora;
  }
  if (singoloMs && ora - singoloMs > ATTESA_DOPPIO_MS) { singoloMs = 0; ultimoTapMs = ora; toccoSingolo(); }
  // fine della finestra del comando: secondo taglio, poi si aspetta che sia tutto in flash
  if (cmdFineMs && (int32_t)(ora - cmdFineMs) >= 0) {
    cmdFineMs = 0;
    chiudiBuffer();
    cmdSeqA = prossimoSeq - 1;
    cmdAttesa = cmdSeqA >= cmdSeqDa;
    if (!cmdRecPrima) { registra = false; aggiornaRegistrazione(); }
  }
  if (cmdAttesa && codaN == 0 && !scr.attiva) {
    cmdAttesa = false;
    uint16_t n = cmdSeqA - cmdSeqDa + 1;
    risp("K cmd %lu %lu", cmdSeqDa, cmdSeqA);
    if (connesso()) {
      cmdRiprendi = scarico;                                       // scarico già in corso: passa avanti il comando
      if (!scarico) avviaScarico();
      cmdN = n;
      cursoreInvio = cmdSlotDa;
      inviando = false;                                            // il settore a metà si rimanda dopo
    }
  }
}

// ---------- setup e loop ----------
void setup() {
  pinMode(LED_RED, OUTPUT); pinMode(LED_GREEN, OUTPUT); pinMode(LED_BLUE, OUTPUT);
  led(LED_RED, false); led(LED_GREEN, false); led(LED_BLUE, false);
  Serial.begin(115200);
  wdtAvvia();
  PDM.setPins(PIN_PDM_DIN, PIN_PDM_CLK, PIN_PDM_PWR);
  flash.ciclo = wdtServi;
  flashOk = flash.begin();
  if (flashOk) scandisciAnello();
  avviaBle();
  batteriaMv = leggiBatteria();
  aggiornaRegistrazione();
  avviaTap();
  inviaStato();
  risp("K avvio fw %d.%d.%d flash %d usati %u", FW_MAJ, FW_MIN, FW_PAT, flashOk, usati);
}

void loop() {
  wdtServi();
  servizioPdm();
  servizioFlash();
  servizioPdm();
  while (cmdCoda_n > 0) {
    char c[CMD_LEN];
    taskENTER_CRITICAL();
    strcpy(c, cmdCoda[cmdTesta]);
    cmdTesta = (cmdTesta + 1) % CMD_N;
    cmdCoda_n--;
    taskEXIT_CRITICAL();
    esegui(c);
  }
  servizioScarico();
  servizioTap();
  aggiornaRegistrazione();
  servizioBatteriaLed();
  if (millis() - ultimoStatoMs > 2000) { ultimoStatoMs = millis(); inviaStato(); }
  delay(1);
}
