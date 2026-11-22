// Prove del formato: node app/test/adpcm.test.mjs
import { codifica, decodifica, crc32, leggiTesta, verificaSettore, sessioni, wav, SETT_BYTE, TESTA_BYTE, DATI_BYTE, MAGIC } from '../adpcm.js';

let falliti = 0;
const prova = (nome, ok, extra = '') => { console.log(`${ok ? 'OK ' : 'NO '} ${nome}${extra ? ' — ' + extra : ''}`); if (!ok) falliti++; };

// 1. CRC32 standard
prova('crc32("123456789") = cbf43926', crc32(new TextEncoder().encode('123456789')) === 0xcbf43926);

// 2. ADPCM: voce sintetica (somma di toni + rumore) codificata e decodificata
const N = 16000;
const pcm = new Int16Array(N);
for (let i = 0; i < N; i++) {
  const t = i / 16000;
  pcm[i] = Math.round(6000 * Math.sin(2 * Math.PI * 220 * t) + 3000 * Math.sin(2 * Math.PI * 1300 * t) + 800 * (Math.random() - 0.5));
}
const stato = { pred: 0, indice: 0 };
const cod = codifica(pcm, stato);
const dec = decodifica(cod, N, 0, 0);
let se = 0, ss = 0;
for (let i = 100; i < N; i++) { se += (pcm[i] - dec[i]) ** 2; ss += pcm[i] ** 2; }
const snr = 10 * Math.log10(ss / se);
prova('ADPCM andata e ritorno, SNR > 20 dB', snr > 20, snr.toFixed(1) + ' dB');

// 3. Settore completo come lo scrive il firmware, poi verificato come fa l'app
function settore(seq, avvio, ms, pcmS, st) {
  const u8 = new Uint8Array(SETT_BYTE).fill(0xff);
  const pred0 = st.pred, ind0 = st.indice;
  const d = codifica(pcmS, st);
  u8.set(d, TESTA_BYTE);
  const v = new DataView(u8.buffer);
  v.setUint32(0, MAGIC, true); v.setUint32(4, seq, true); v.setUint32(8, avvio, true); v.setUint32(12, ms, true);
  v.setBigUint64(16, 1763800000000n, true); v.setInt16(24, pred0, true); v.setUint8(26, ind0); v.setUint8(27, 1);
  v.setUint16(28, pcmS.length, true); v.setUint16(30, 0, true);
  v.setUint32(32, crc32(u8.subarray(TESTA_BYTE)), true);
  return u8;
}
const st2 = { pred: 0, indice: 0 };
const s1 = settore(7, 5, 1000, pcm.subarray(0, DATI_BYTE * 2), st2);
const s2 = settore(8, 5, 1000 + 508, pcm.subarray(DATI_BYTE * 2, N), st2);   // secondo settore parziale
const v1 = verificaSettore(s1), v2 = verificaSettore(s2);
prova('settore pieno valido', v1.ok, v1.motivo);
prova('settore parziale valido', v2.ok && v2.testa.campioni === N - DATI_BYTE * 2, v2.motivo);
const t = leggiTesta(s1);
prova('testata letta', t.seq === 7 && t.avvio === 5 && t.campioni === 8120 && t.epocaMs === 1763800000000);
// la decodifica di due settori consecutivi dalle loro testate ridà la stessa forma d'onda
const d1 = decodifica(s1.subarray(TESTA_BYTE), t.campioni, t.pred, t.indice);
const t2 = leggiTesta(s2);
const d2 = decodifica(s2.subarray(TESTA_BYTE), t2.campioni, t2.pred, t2.indice);
let uguali = true;
for (let i = 0; i < d1.length; i++) if (d1[i] !== dec[i]) uguali = false;
for (let i = 0; i < d2.length; i++) if (d2[i] !== dec[d1.length + i]) uguali = false;
prova('settori indipendenti = flusso continuo', uguali);
const rotto = s1.slice(); rotto[1000] ^= 1;
prova('CRC scopre un bit sbagliato', verificaSettore(rotto).motivo === 'crc');

// 4. Raggruppamento in registrazioni
const meta = (seq, avvio, ms) => ({ seq, avvio, ms, campioni: 8120, epocaMs: 0 });
const g = sessioni([meta(3, 1, 0), meta(1, 1, 0 - 1015), meta(2, 1, -508), meta(10, 1, 60000), meta(11, 11, 0)]);
prova('3 registrazioni distinte', g.length === 3 && g[0].seqs.join() === '1,2,3', JSON.stringify(g.map(x => x.seqs)));

// 5. WAV
const w = wav(dec);
prova('WAV di 16000 campioni = 32044 byte', w.size === 44 + N * 2);

console.log(falliti ? `\n${falliti} prove fallite` : '\nTutte le prove superate');
process.exit(falliti ? 1 : 0);
