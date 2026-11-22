// notªpad – chi parla: assegna ogni frase al proprietario ("Io") o a un interlocutore (1, 2, 3…)
// confrontando le impronte vocali (WeSpeaker, vettori di lunghezza 1) calcolate da trascrittore.js.
// Funzioni pure, senza DOM: girano uguali nel browser, in un'app Capacitor e in node (test/voci.test.mjs).

// Soglie sul coseno tra impronte (1 = stessa voce, ~0 = voci diverse). Da tarare con registrazioni vere.
export const SOGLIA_IO = 0.40;       // frase contro il profilo del proprietario
export const SOGLIA_STESSO = 0.35;   // frase contro la media di un interlocutore già trovato
export const MIN_S_NUOVO = 1.2;      // una frase più corta non apre un interlocutore nuovo
export const MAX_CAMPIONI = 200;     // impronte tenute nel profilo del proprietario

export function coseno(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}
// media normalizzata di più impronte
export function media(vettori) {
  if (!vettori.length) return null;
  const m = new Float64Array(vettori[0].length);
  for (const v of vettori) for (let i = 0; i < m.length; i++) m[i] += v[i];
  let n = 0; for (const x of m) n += x * x;
  n = Math.sqrt(n) || 1;
  return Array.from(m, x => x / n);
}

// righe: [{ voce: impronta | null, durata: secondi }], profilo: media delle impronte del proprietario o null.
// Ritorna per ogni riga { chi: 'io' | 1, 2, … | null, sim } (sim = somiglianza con chi è stato scelto).
// Due passate: la prima raccoglie gli interlocutori in ordine di tempo, la seconda riassegna ogni frase
// al più vicino (così le prime frasi non dipendono da medie fatte con poche frasi).
export function assegna(righe, profilo, { delta = 0, minimo = 1 } = {}) {
  const SI = SOGLIA_IO + delta, SS = SOGLIA_STESSO + delta;
  let gruppi = [];                   // { voci: [], c: media }
  const scegli = (v, durata, crea) => {
    const sIo = profilo ? coseno(v, profilo) : -1;
    let best = -1, bi = -1;
    gruppi.forEach((g, i) => { const s = coseno(v, g.c); if (s > best) { best = s; bi = i; } });
    if (sIo >= SI && sIo >= best) return { chi: 'io', sim: sIo };
    if (best >= SS) return { chi: bi, sim: best };
    if (crea && durata >= MIN_S_NUOVO) { gruppi.push({ voci: [], c: v }); return { chi: gruppi.length - 1, sim: 1 }; }
    return null;
  };
  // 1ª passata
  for (const r of righe) {
    if (!r.voce) continue;
    const x = scegli(r.voce, r.durata, true);
    if (x && x.chi !== 'io') { const g = gruppi[x.chi]; g.voci.push(r.voce); g.c = media(g.voci); }
  }
  // voci con troppo poche frasi/finestre (rumore, colpi di tosse): via, le loro frasi vanno al più vicino
  gruppi = gruppi.filter(g => g.voci.length >= minimo);
  // 2ª passata con le medie finali
  let prec = null;
  const out = righe.map(r => {
    const x = r.voce ? scegli(r.voce, r.durata, false) : null;
    const res = x || { chi: prec ? prec.chi : null, sim: null, dedotto: true };   // corta o incerta: come la precedente
    prec = res;
    return res;
  });
  // numeri in ordine di prima comparsa, senza buchi
  const num = new Map();
  for (const x of out) if (x.chi !== null && x.chi !== 'io' && !num.has(x.chi)) num.set(x.chi, num.size + 1);
  for (const x of out) if (x.chi !== null && x.chi !== 'io') x.chi = num.get(x.chi);
  return out;
}

export const etichetta = chi => chi === 'io' ? 'Io' : chi ? `Interlocutore ${chi}` : '?';

// profilo del proprietario: { campioni: [impronte], data }
export function aggiungiCampioni(profilo, nuovi) {
  const campioni = [...(profilo ? profilo.campioni : []), ...nuovi].slice(-MAX_CAMPIONI);
  return { campioni, data: Date.now() };
}

// Turni di parola da parole con l'ora (Whisper "word") e finestre con impronta (Int8 ×127 o numeri).
// Ogni finestra prende una voce, poi si liscia (maggioranza su 3 finestre vicine), ogni parola prende la
// voce della finestra più vicina al suo centro e le parole consecutive della stessa voce fanno un turno.
export function turni(parole, finestre, profilo, { delta = 0 } = {}) {
  if (!parole.length) return [];
  let voci = [];
  if (finestre && finestre.length) {
    const righe = finestre.map(f => ({ voce: Array.from(f.voce, x => f.voce instanceof Int8Array ? x / 127 : x), durata: f.t1 - f.t0 }));
    const a = assegna(righe, profilo, { delta, minimo: 3 });
    voci = a.map((x, i) => {                         // lisciatura
      const vic = [a[i - 1], x, a[i + 1]].filter(Boolean).map(y => y.chi);
      const conta = new Map(); vic.forEach(c => conta.set(c, (conta.get(c) || 0) + 1));
      const [top, n] = [...conta].sort((p, q) => q[1] - p[1])[0];
      return n >= 2 ? { ...x, chi: top } : x;
    });
  }
  const centro = f => (f.t0 + f.t1) / 2;
  const out = [];
  let j = 0;
  for (const w of parole) {
    const m = (w.t0 + w.t1) / 2;
    while (j + 1 < finestre?.length && Math.abs(centro(finestre[j + 1]) - m) <= Math.abs(centro(finestre[j]) - m)) j++;
    const v = voci.length && finestre[j] && Math.abs(centro(finestre[j]) - m) < 1.5 ? voci[j] : { chi: null, sim: null };
    const u = out[out.length - 1];
    const pausa = u ? w.t0 - u.t1 : 0;
    const lungo = u && u.t1 - u.t0 > 25 && /[.?!]$/.test(u.testo.trim());
    if (u && (u.chi === v.chi || v.chi === null) && pausa < 2 && !lungo) { u.testo += w.testo; u.t1 = w.t1; }
    else out.push({ t0: w.t0, t1: w.t1, testo: w.testo, chi: v.chi ?? (u ? u.chi : null), sim: v.sim });
  }
  out.forEach(t => t.testo = t.testo.trim());
  // numeri in ordine di comparsa nel testo
  const num = new Map();
  for (const t of out) if (t.chi && t.chi !== 'io' && !num.has(t.chi)) num.set(t.chi, num.size + 1);
  for (const t of out) if (t.chi && t.chi !== 'io') t.chi = num.get(t.chi);
  return out;
}
