// notªpad – rilevatore di parlato (VAD) a energia: Whisper riceve solo i tratti con voce, uniti con 0,3 s
// di pausa, e i tempi tornano poi quelli veri. In una giornata il parlato è una piccola parte dell'audio.
const FREQ = 16000, FR = 320;            // finestre da 20 ms

// ritorna { audio, mappa: [{ d0, s0, n }] (secondi: inizio nel compresso, inizio nel vero, durata), parlato }
export function soloParlato(x) {
  const nf = Math.floor(x.length / FR);
  if (nf < 50) return { audio: x, mappa: [{ d0: 0, s0: 0, n: x.length / FREQ }], parlato: 1 };
  const e = new Float32Array(nf);
  for (let f = 0; f < nf; f++) { let s = 0; for (let i = f * FR; i < (f + 1) * FR; i++) s += x[i] * x[i]; e[f] = Math.sqrt(s / FR); }
  const ord = Float32Array.from(e).sort();
  // rumore di fondo = 10° percentile; con una conversazione fitta anche quello è voce: la soglia non sale
  // oltre 0,015 (una voce lontana ha RMS ~0,01–0,02), altrimenti tutto il parlato sembrerebbe rumore
  const fondo = ord[Math.floor(nf * 0.1)];
  const soglia = Math.min(0.015, Math.max(0.004, fondo * 3));
  // voce = finestre sopra soglia, allargate di 0,3 s; buchi < 0,8 s chiusi; tratti < 0,25 s scartati
  const v = new Uint8Array(nf);
  for (let f = 0; f < nf; f++) if (e[f] > soglia) for (let k = Math.max(0, f - 15); k <= Math.min(nf - 1, f + 15); k++) v[k] = 1;
  const tratti = [];
  for (let f = 0; f < nf;) {
    if (!v[f]) { f++; continue; }
    let g = f; while (g < nf && v[g]) g++;
    const u = tratti[tratti.length - 1];
    if (u && f - u[1] < 40) u[1] = g; else tratti.push([f, g]);
    f = g;
  }
  const buoni = tratti.filter(([a, b]) => b - a >= 12);
  const tot = buoni.reduce((n, [a, b]) => n + b - a, 0);
  if (tot > nf * 0.85 || !tot) return { audio: x, mappa: [{ d0: 0, s0: 0, n: x.length / FREQ }], parlato: tot / nf };
  const PAUSA = Math.round(0.3 * FREQ);
  const out = new Float32Array(tot * FR + buoni.length * PAUSA);
  const mappa = [];
  let o = 0;
  for (const [a, b] of buoni) {
    out.set(x.subarray(a * FR, b * FR), o);
    mappa.push({ d0: o / FREQ, s0: a * FR / FREQ, n: (b - a) * FR / FREQ });
    o += (b - a) * FR + PAUSA;
  }
  return { audio: out, mappa, parlato: tot / nf };
}

// Finestre per Whisper: i tratti di parlato (mappa di soloParlato) si raggruppano in finestre di al massimo
// maxS secondi, tagliate solo tra un tratto e l'altro (mai a metà parola). Un tratto più lungo di maxS si
// taglia nel punto più silenzioso del suo ultimo terzo. Ogni finestra va a Whisper da sola (≤ 30 s: niente
// chunking con sovrapposizione, che in transformers.js perde e duplica parole). Ritorna [a, b] in campioni.
export function finestre(x, mappa, maxS = 25) {
  const max = Math.round(maxS * FREQ), out = [];
  let a = -1, b = -1;
  const chiudi = () => { if (a >= 0 && b > a) out.push([a, b]); a = -1; };
  for (const m of mappa) {
    let s0 = Math.round(m.d0 * FREQ);
    const s1 = Math.min(x.length, Math.round((m.d0 + m.n) * FREQ));
    if (a >= 0 && s1 - a > max) chiudi();
    while (s1 - s0 > max) {
      const t = taglio(x, s0 + Math.round(max * 2 / 3), s0 + max);
      out.push([s0, t]);
      s0 = t;
    }
    if (a < 0) a = s0;
    b = s1;
  }
  chiudi();
  return out;
}
// inizio della finestra da 20 ms con meno energia tra da e a
function taglio(x, da, a) {
  let best = a, eMin = Infinity;
  for (let f = da; f + FR <= a; f += FR) {
    let s = 0; for (let i = f; i < f + FR; i++) s += x[i] * x[i];
    if (s < eMin) { eMin = s; best = f + (FR >> 1); }
  }
  return best;
}

// frasi che Whisper "inventa" sul silenzio o sul rumore (soprattutto in italiano)
const ALLUCINAZIONI = [/sottotitoli (creati|a cura|e revisione)/i, /amara\.org/i, /grazie (a tutti )?per (la visione|l'ascolto|aver guardato)/i,
  /^(\W*|grazie\.?|\.\.\.|musica)$/i, /iscriviti al canale/i];
export const allucinazione = t => ALLUCINAZIONI.some(r => r.test(t.trim()));

// Whisper a volte si "incanta" e ripete la stessa parola o frase: oltre 2 ripetizioni di fila si tagliano
export function senzaRipetizioni(parole) {
  const n = w => w.testo.trim().toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
  const out = [];
  for (const w of parole) {
    out.push(w);
    for (let k = 1; k <= 6 && 3 * k <= out.length; k++) {
      const g = i => out.slice(out.length - i * k, out.length - (i - 1) * k).map(n).join(' ');
      if (g(1) && g(1) === g(2) && g(2) === g(3)) { out.splice(out.length - k, k); break; }
    }
  }
  return out;
}

// tempo nel compresso → tempo vero
export function tempoVero(t, mappa) {
  let m = mappa[0];
  for (const x of mappa) { if (x.d0 <= t + 1e-6) m = x; else break; }
  return m.s0 + Math.min(Math.max(0, t - m.d0), m.n);
}
