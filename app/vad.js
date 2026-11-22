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
  const fondo = ord[Math.floor(nf * 0.2)];                          // rumore di fondo = 20° percentile
  const soglia = Math.max(0.004, fondo * 3);
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
  if (tot > nf * 0.85) return { audio: x, mappa: [{ d0: 0, s0: 0, n: x.length / FREQ }], parlato: tot / nf };
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

// tempo nel compresso → tempo vero
export function tempoVero(t, mappa) {
  let m = mappa[0];
  for (const x of mappa) { if (x.d0 <= t + 1e-6) m = x; else break; }
  return m.s0 + Math.min(Math.max(0, t - m.d0), m.n);
}
