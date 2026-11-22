// prove di voci.js con impronte finte: node app/test/voci.test.mjs
import assert from 'node:assert';
import { assegna, media, etichetta } from '../voci.js';
let seme = 1; const rnd = () => (seme = (seme * 16807) % 2147483647) / 2147483647 - 0.5;
const norm = v => { const n = Math.hypot(...v); return v.map(x => x / n); };
const base = () => norm(Array.from({ length: 256 }, rnd));
const vicino = (b, r = 0.6) => norm(b.map(x => x + r * rnd() / 8));
const io = base(), a = base(), b = base();
const profilo = media([vicino(io), vicino(io), vicino(io)]);
const righe = [io, a, a, io, b, a, b, io].map(v => ({ voce: vicino(v), durata: 3 }));
righe.splice(3, 0, { voce: null, durata: 0.4 });           // frase corta senza impronta
const chi = assegna(righe, profilo).map(x => x.chi);
assert.deepStrictEqual(chi, ['io', 1, 1, 1, 'io', 2, 1, 2, 'io']);
assert.deepStrictEqual(assegna(righe, null).map(x => x.chi)[0], 1);   // senza profilo il proprietario è un interlocutore
assert.strictEqual(etichetta(2), 'Interlocutore 2');
console.log('voci: ok', chi.join(' '));
// turni: io parlo 0-6 s, A 6-12 s, io 12-15 s; finestre ogni 0,75 s
import { turni } from '../voci.js';
const q = v => Int8Array.from(v, x => Math.round(x * 127));
const fin = []; for (let t = 0; t + 1.5 <= 15; t += 0.75) { const c = t + 0.75; fin.push({ t0: t, t1: t + 1.5, voce: q(vicino(c < 6 || c >= 12 ? io : a)) }); }
const par = []; for (let t = 0; t < 15; t += 0.5) par.push({ t0: t, t1: t + 0.4, testo: ' p' + t });
const tu = turni(par, fin, profilo);
assert.deepStrictEqual(tu.map(t => t.chi), ['io', 1, 'io']);
console.log('turni: ok', tu.map(t => `${t.chi}@${t.t0}`).join(' '));
