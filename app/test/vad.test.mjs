// prove di vad.js: node app/test/vad.test.mjs
import assert from 'node:assert';
import { soloParlato, finestre, senzaRipetizioni, allucinazione } from '../vad.js';
const F = 16000;
let seme = 7; const rnd = () => (seme = (seme * 16807) % 2147483647) / 2147483647 - 0.5;
// 80 s: parlato a tratti di 6 s con pause di 2 s, poi un monologo di 40 s senza pause
const x = new Float32Array(80 * F);
for (let i = 0; i < x.length; i++) x[i] = rnd() * 0.002;                       // fondo
const voce = (t0, t1) => { for (let i = t0 * F; i < t1 * F; i++) x[i] = 0.2 * Math.sin(i / 7) * (0.6 + rnd()); };
for (let t = 0; t < 38; t += 8) voce(t, t + 6);
voce(40, 80);
for (let i = 60 * F; i < 60.1 * F; i++) x[i] *= 0.05;                           // un respiro a 60 s
const v = soloParlato(x);
const fin = finestre(v.audio, v.mappa);
const N = v.audio.length;
assert.ok(fin.length >= 3, 'servono più finestre');
for (const [a, b] of fin) assert.ok(b - a <= 25 * F && b > a, `finestra troppo lunga: ${(b - a) / F} s`);
for (let k = 1; k < fin.length; k++) assert.ok(fin[k][0] >= fin[k - 1][1], 'finestre sovrapposte');
assert.ok(fin[fin.length - 1][1] <= N);
// ogni taglio cade in una pausa o nel respiro, mai in mezzo alla voce
const rmsA = t => { let s = 0; for (let i = t - 80; i < t + 80; i++) s += v.audio[i] * v.audio[i]; return Math.sqrt(s / 160); };
for (const [, b] of fin.slice(0, -1)) assert.ok(rmsA(b) < 0.02, `taglio nella voce a ${(b / F).toFixed(2)} s`);
console.log('finestre: ok', fin.map(([a, b]) => ((b - a) / F).toFixed(1) + ' s').join(' · '));
// senza mappa: un tratto solo di 70 s si taglia in pezzi ≤ 25 s nei punti più bassi
const f2 = finestre(x.subarray(10 * F), [{ d0: 0, s0: 0, n: 70 }]);
assert.ok(f2.every(([a, b]) => b - a <= 25 * F) && f2[0][0] === 0 && f2[f2.length - 1][1] === 70 * F);
console.log('tratto lungo: ok', f2.length, 'finestre');

const w = t => t.split(' ').map((p, i) => ({ t0: i, t1: i + 0.5, testo: ' ' + p }));
const testo = p => p.map(x => x.testo).join('').trim();
assert.strictEqual(testo(senzaRipetizioni(w('e poi e poi e poi e poi e poi siamo andati'))), 'e poi e poi siamo andati');
assert.strictEqual(testo(senzaRipetizioni(w('no no no no no'))), 'no no');
assert.strictEqual(testo(senzaRipetizioni(w('ciao come stai bene grazie'))), 'ciao come stai bene grazie');
assert.ok(allucinazione('Sottotitoli creati dalla comunità Amara.org') && !allucinazione('ci vediamo domani'));
console.log('ripetizioni e allucinazioni: ok');
