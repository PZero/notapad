// notªpad – formato dei settori, decodifica IMA ADPCM, CRC32 e WAV.
// Speculare a firmware/xiao-prova/protocollo.h e adpcm.h: se cambia uno, cambia l'altro.

export const SETT_BYTE = 4096;
export const TESTA_BYTE = 36;
export const DATI_BYTE = SETT_BYTE - TESTA_BYTE;
export const MAGIC = 0x3141504e; // "NPA1"
export const FREQ = 16000;

const PASSI = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88,
  97, 107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876,
  963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894,
  6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767];
const INDICI = [-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8];

// Codifica (usata solo dai test: è la stessa del firmware)
export function codifica(pcm, stato = { pred: 0, indice: 0 }) {
  const out = new Uint8Array(Math.ceil(pcm.length / 2));
  for (let i = 0; i < pcm.length; i++) {
    let passo = PASSI[stato.indice];
    let diff = pcm[i] - stato.pred;
    let c = 0;
    if (diff < 0) { c = 8; diff = -diff; }
    let delta = passo >> 3;
    if (diff >= passo) { c |= 4; diff -= passo; delta += passo; }
    passo >>= 1;
    if (diff >= passo) { c |= 2; diff -= passo; delta += passo; }
    passo >>= 1;
    if (diff >= passo) { c |= 1; delta += passo; }
    stato.pred += (c & 8) ? -delta : delta;
    stato.pred = Math.max(-32768, Math.min(32767, stato.pred));
    stato.indice = Math.max(0, Math.min(88, stato.indice + INDICI[c]));
    if (i & 1) out[i >> 1] |= c << 4; else out[i >> 1] = c;
  }
  return out;
}

export function decodifica(dati, campioni, pred, indice) {
  const out = new Int16Array(campioni);
  for (let i = 0; i < campioni; i++) {
    const b = dati[i >> 1];
    const c = (i & 1) ? (b >> 4) : (b & 15);
    const passo = PASSI[indice];
    let delta = passo >> 3;
    if (c & 4) delta += passo;
    if (c & 2) delta += passo >> 1;
    if (c & 1) delta += passo >> 2;
    pred += (c & 8) ? -delta : delta;
    if (pred > 32767) pred = 32767; else if (pred < -32768) pred = -32768;
    indice += INDICI[c];
    if (indice < 0) indice = 0; else if (indice > 88) indice = 88;
    out[i] = pred;
  }
  return out;
}

let TAB = null;
export function crc32(u8) {
  if (!TAB) {
    TAB = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      TAB[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (let i = 0; i < u8.length; i++) c = TAB[(c ^ u8[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

export function leggiTesta(u8) {
  const v = new DataView(u8.buffer, u8.byteOffset, TESTA_BYTE);
  return {
    magic: v.getUint32(0, true),
    seq: v.getUint32(4, true),
    avvio: v.getUint32(8, true),
    ms: v.getUint32(12, true),
    epocaMs: Number(v.getBigUint64(16, true)),
    pred: v.getInt16(24, true),
    indice: v.getUint8(26),
    codec: v.getUint8(27),
    campioni: v.getUint16(28, true),
    comando: !!(v.getUint16(30, true) & 1),     // riservato bit 0: settore di un comando (tocco singolo)
    crc: v.getUint32(32, true),
  };
}

// Controlla un settore ricevuto: ritorna { ok, testa, motivo }
export function verificaSettore(u8) {
  if (u8.length !== SETT_BYTE) return { ok: false, motivo: 'lunghezza' };
  const t = leggiTesta(u8);
  if (t.magic !== MAGIC) return { ok: false, testa: t, motivo: 'magic' };
  if (t.codec !== 1) return { ok: false, testa: t, motivo: 'codec ' + t.codec };
  if (t.campioni > DATI_BYTE * 2) return { ok: false, testa: t, motivo: 'campioni' };
  if (crc32(u8.subarray(TESTA_BYTE)) !== t.crc) return { ok: false, testa: t, motivo: 'crc' };
  return { ok: true, testa: t };
}

export function wav(pcm, freq = FREQ) {
  const b = new ArrayBuffer(44 + pcm.length * 2);
  const v = new DataView(b);
  const s = (o, t) => { for (let i = 0; i < t.length; i++) v.setUint8(o + i, t.charCodeAt(i)); };
  s(0, 'RIFF'); v.setUint32(4, 36 + pcm.length * 2, true); s(8, 'WAVE');
  s(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, freq, true); v.setUint32(28, freq * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  s(36, 'data'); v.setUint32(40, pcm.length * 2, true);
  new Int16Array(b, 44).set(pcm);
  return new Blob([b], { type: 'audio/wav' });
}

// Raggruppa i settori (ordinati per seq) in registrazioni continue
export function sessioni(settori) {
  const ord = [...settori].sort((a, b) => a.seq - b.seq);
  const out = [];
  let cur = null;
  for (const s of ord) {
    const fineAtt = cur ? cur.ultimo.ms + Math.round(cur.ultimo.campioni * 1000 / FREQ) : 0;
    const continuo = cur && s.avvio === cur.avvio && s.seq === cur.ultimo.seq + 1 && Math.abs(s.ms - fineAtt) < 1500;
    if (!continuo) {
      cur = { seqs: [], campioni: 0, inizio: s.epocaMs || null, avvio: s.avvio, msInizio: s.ms, ultimo: s };
      out.push(cur);
    }
    cur.seqs.push(s.seq);
    cur.campioni += s.campioni;
    cur.ultimo = s;
  }
  return out;
}
