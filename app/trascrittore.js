// notªpad – trascrizione con Whisper nel browser (transformers.js + ONNX Runtime Web), in un Web Worker
// così Bluetooth e interfaccia non si bloccano. Funziona su Edge/Chrome per Windows e su Chrome per Android.
// Motore: WebGPU se c'è, altrimenti WASM (multithread se la pagina è cross-origin isolated, vedi sw.js).
// Il modello si scarica una volta da Hugging Face e resta nella cache del browser ("transformers-cache").
// Voci: per ogni frase calcola anche un'"impronta vocale" (embedding da 256 numeri) con WeSpeaker ResNet34
// (lo stesso modello della pipeline pyannote 3.1, 26 MB). Chi parla lo decide app.js confrontando le impronte.
import { pipeline, env, AutoModel, AutoFeatureExtractor } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2';
import { finestre, allucinazione, senzaRipetizioni } from './vad.js';

const VERSIONE = '0.10.0';              // la stessa di app.js: l'app la mostra quando il modello è pronto

// Dove cerca i modelli, in ordine: cache del browser → cartella app/modelli/ sul nostro server (copia fatta
// con «Salva i modelli in una cartella», per lavorare senza rete) → Hugging Face.
// Il percorso deve essere relativo al sito, non un URL completo (transformers.js salta i percorsi http://).
env.allowLocalModels = true;
env.localModelPath = new URL('modelli/', self.location.href).pathname;
env.useBrowserCache = true;
if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.numThreads = self.crossOriginIsolated ? Math.min(4, navigator.hardwareConcurrency || 2) : 1;
}

// file per motore (encoder + decoder):
//   wasm   q8:          tiny 41 MB · base 77 MB · small 249 MB
//   webgpu fp16 (fp32):  small 485 MB (970 MB) · turbo 1,6 GB (solo fp16)
// 23/11: niente più decoder a 4 bit su WebGPU: in italiano sbagliava molte parole ed era la causa principale
// delle trascrizioni scadenti rispetto a Whisper a precisione piena. Il download è più grande, una volta sola.
const MODELLI = {
  // varianti "_timestamped": danno l'ora di ogni parola (serve per dividere il testo tra chi parla)
  tiny:  'onnx-community/whisper-tiny_timestamped',
  base:  'onnx-community/whisper-base_timestamped',
  small: 'onnx-community/whisper-small_timestamped',
  turbo: 'onnx-community/whisper-large-v3-turbo_timestamped',
};

let asr = null, chiave = '', motore = '';

async function capacitaGpu() {
  if (!navigator.gpu) return null;
  try {
    const a = await navigator.gpu.requestAdapter();
    return a ? { f16: a.features.has('shader-f16') } : null;
  } catch { return null; }
}

function dtypePer(nome, dev, f16) {
  if (dev === 'wasm') return { encoder_model: 'q8', decoder_model_merged: 'q8' };
  const p = f16 ? 'fp16' : 'fp32';
  return { encoder_model: p, decoder_model_merged: p };
}

// avanzamento del download aggregato su tutti i file
function progresso() {
  const file = new Map();
  let ultimo = 0;
  return p => {
    if (p.status === 'progress' && p.total) file.set(p.file, [p.loaded, p.total]);
    else if (p.status === 'done' && file.has(p.file)) { const [, t] = file.get(p.file); file.set(p.file, [t, t]); }
    else return;
    const ora = Date.now();
    if (ora - ultimo < 250) return;
    ultimo = ora;
    let l = 0, t = 0; for (const [a, b] of file.values()) { l += a; t += b; }
    postMessage({ tipo: 'download', caricati: l, totali: t });
  };
}

async function carica(nome, preferito) {
  const gpu = preferito === 'wasm' ? null : await capacitaGpu();
  let dev = gpu ? 'webgpu' : 'wasm';
  if (nome === 'turbo' && !(gpu && gpu.f16)) nome = 'small';        // turbo solo con WebGPU fp16
  const k = `${nome}|${dev}`;
  if (asr && k === chiave) return;
  if (asr) { try { await asr.dispose(); } catch {} asr = null; }
  postMessage({ tipo: 'stato', testo: `carico whisper-${nome} (${dev})…` });
  try {
    asr = await pipeline('automatic-speech-recognition', MODELLI[nome],
      { device: dev, dtype: dtypePer(nome, dev, gpu && gpu.f16), progress_callback: progresso() });
  } catch (e) {
    if (dev !== 'webgpu') throw e;
    postMessage({ tipo: 'stato', testo: `WebGPU non va (${e.message}), passo a WASM` });
    dev = 'wasm';
    if (nome === 'turbo') nome = 'small';
    asr = await pipeline('automatic-speech-recognition', MODELLI[nome],
      { device: dev, dtype: dtypePer(nome, dev, false), progress_callback: progresso() });
  }
  chiave = `${nome}|${dev}`;
  motore = dev === 'webgpu' ? 'WebGPU' : `WASM ${self.crossOriginIsolated ? env.backends.onnx.wasm.numThreads + ' thread' : '1 thread'}`;
  postMessage({ tipo: 'pronto', modello: `whisper-${nome}`, motore, versione: VERSIONE });
}

// ---------- impronte vocali ----------
// Sempre su WASM fp32: il modello è piccolo, così il risultato è identico su PC, Android e iPhone
// (le impronte salvate restano confrontabili tra dispositivi e motori diversi).
const VOCE = 'onnx-community/wespeaker-voxceleb-resnet34-LM';
const FREQ = 16000, MIN_S = 0.5, MAX_S = 20;
let voce = null;
async function caricaVoce() {
  if (voce) return voce;
  postMessage({ tipo: 'stato', testo: 'carico il modello delle voci…' });
  const [fe, mod] = await Promise.all([
    AutoFeatureExtractor.from_pretrained(VOCE),
    AutoModel.from_pretrained(VOCE, { device: 'wasm', dtype: 'fp32', progress_callback: progresso() }),
  ]);
  return voce = { fe, mod };
}
// impronta normalizzata (lunghezza 1) di un pezzo di audio, o null se è troppo corto
async function impronta(audio) {
  if (audio.length < MIN_S * FREQ) return null;
  if (audio.length > MAX_S * FREQ) {                   // frase lunghissima: la parte centrale basta
    const m = (audio.length - MAX_S * FREQ) >> 1;
    audio = audio.subarray(m, m + MAX_S * FREQ);
  }
  const { fe, mod } = await caricaVoce();
  const out = await mod(await fe(audio));
  const v = Float32Array.from(Object.values(out)[0].data);
  let n = 0; for (const x of v) n += x * x;
  n = Math.sqrt(n) || 1;
  return Array.from(v, x => +(x / n).toFixed(5));
}
// un'impronta per ogni frase (t0, t1 in secondi dall'inizio dell'audio)
async function impronteDi(audio, segmenti) {
  const out = [];
  for (const s of segmenti) {
    const a = Math.max(0, Math.floor((s.t0 || 0) * FREQ));
    const b = Math.min(audio.length, Math.ceil((s.t1 ?? audio.length / FREQ) * FREQ));
    out.push(b > a ? await impronta(audio.subarray(a, b)) : null);
  }
  return out;
}

// finestre di 1,5 s ogni 0,75 s sulle parti con parlato: ognuna ha la sua impronta (Int8, ×127),
// così un cambio di voce a metà frase si vede. Chi parla lo decide app.js.
const FIN = 1.5, PASSO = 0.75;
async function finestreDi(audio, parole) {
  const out = [];
  for (let t = 0; t + FIN <= audio.length / FREQ + 0.01; t += PASSO) {
    if (!parole.some(w => w.t1 > t && w.t0 < t + FIN)) continue;      // nessuna parola: silenzio
    const v = await impronta(audio.subarray(Math.floor(t * FREQ), Math.floor((t + FIN) * FREQ)));
    if (v) out.push({ t0: +t.toFixed(2), t1: +(t + FIN).toFixed(2), voce: Int8Array.from(v, x => Math.round(x * 127)) });
  }
  return out;
}

// volume di una finestra: parlato a un livello costante (RMS ~0,08), senza mai saturare; mai abbassato
function livella(x) {
  let e2 = 0, picco = 0;
  for (const v of x) { e2 += v * v; const a = Math.abs(v); if (a > picco) picco = a; }
  const rms = Math.sqrt(e2 / Math.max(1, x.length));
  const k = Math.min(0.08 / Math.max(rms, 1e-6), 0.95 / Math.max(picco, 1e-6), 30);
  if (k > 1) for (let i = 0; i < x.length; i++) x[i] *= k;
  return x;
}

// mappa: tratti di parlato (vad.js) nell'audio ricevuto; senza mappa l'audio è un tratto solo.
// Ogni finestra (≤ 25 s, tagliata nelle pause) va a Whisper da sola: niente tagli a metà parola.
async function trascrivi({ id, audio, mappa, lingua, voci = true }) {
  const t0 = performance.now();
  const FIN_W = finestre(audio, mappa || [{ d0: 0, s0: 0, n: audio.length / FREQ }]);
  let parole = [];
  const testi = [];
  for (const [a, b] of FIN_W) {
    if (b - a < 0.3 * FREQ) continue;
    const out = await asr(livella(audio.slice(a, b)), {
      language: lingua || null,        // null = rilevamento automatico
      task: 'transcribe',
      return_timestamps: 'word',
    });
    const testo = (out.text || '').trim();
    if (!testo || allucinazione(testo)) continue;
    const off = a / FREQ;
    const pw = (out.chunks || []).map(c => ({ t0: off + (c.timestamp[0] ?? 0), t1: off + (c.timestamp[1] ?? c.timestamp[0] ?? 0), testo: c.text }))
      .filter(w => w.testo.trim());
    const pulite = senzaRipetizioni(pw);
    parole = parole.concat(pulite);
    testi.push(pulite.length < pw.length ? pulite.map(w => w.testo).join('').trim() : testo);
  }
  const secondi = (performance.now() - t0) / 1000;
  let impronte = null;
  try { if (voci) impronte = await finestreDi(audio, parole); }
  catch (e) { postMessage({ tipo: 'stato', testo: `voci non riconosciute (${e.message})` }); }
  postMessage({
    tipo: 'risultato', id, testo: testi.join(' '), parole, finestre: impronte,
    secondi, secondiVoci: (performance.now() - t0) / 1000 - secondi, modello: chiave.split('|')[0], motore,
  });
}

// le richieste si eseguono una alla volta, nell'ordine di arrivo
let coda = Promise.resolve();
onmessage = e => {
  const m = e.data;
  coda = coda.then(async () => {
    try {
      if (m.tipo === 'voci') {                          // impronte per frasi già trascritte (senza Whisper)
        postMessage({ tipo: 'risultato', id: m.id, impronte: await impronteDi(m.audio, m.segmenti) });
        return;
      }
      if (m.tipo === 'campione') {                      // voce del proprietario: un'impronta ogni 3 s di parlato
        const imp = [];
        for (let i = 0; i + 1.5 * FREQ <= m.audio.length; i += 3 * FREQ) {
          const pezzo = m.audio.subarray(i, i + 3 * FREQ);
          let e2 = 0; for (const x of pezzo) e2 += x * x;
          if (Math.sqrt(e2 / pezzo.length) < 0.003) continue;      // silenzio
          const v = await impronta(pezzo); if (v) imp.push(v);
        }
        postMessage({ tipo: 'risultato', id: m.id, impronte: imp });
        return;
      }
      await carica(m.modello, m.motore);
      if (m.tipo === 'trascrivi') await trascrivi(m);
      else postMessage({ tipo: 'fatto', id: m.id });
    } catch (err) {
      postMessage({ tipo: 'errore', id: m.id, testo: err && err.message ? err.message : String(err) });
    }
  });
};
