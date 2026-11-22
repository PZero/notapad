// notªpad – trascrizione con Whisper nel browser (transformers.js + ONNX Runtime Web), in un Web Worker
// così Bluetooth e interfaccia non si bloccano. Funziona su Edge/Chrome per Windows e su Chrome per Android.
// Motore: WebGPU se c'è, altrimenti WASM (multithread se la pagina è cross-origin isolated, vedi sw.js).
// Il modello si scarica una volta da Hugging Face e resta nella cache del browser ("transformers-cache").
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.2';

env.allowLocalModels = false;           // niente richieste a /models/ sul nostro server
env.useBrowserCache = true;
if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.numThreads = self.crossOriginIsolated ? Math.min(4, navigator.hardwareConcurrency || 2) : 1;
}

// file per motore (dimensioni del 22/11/2026, encoder + decoder):
//   wasm   q8:            tiny 41 MB · base 77 MB · small 249 MB
//   webgpu fp32/fp16 + q4: tiny 42/26 MB · base 106/65 MB · small 586/410 MB · turbo (q4f16) 564 MB
const MODELLI = {
  tiny:  'onnx-community/whisper-tiny',
  base:  'onnx-community/whisper-base',
  small: 'onnx-community/whisper-small',
  turbo: 'onnx-community/whisper-large-v3-turbo',
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
  if (nome === 'turbo') return { encoder_model: 'q4f16', decoder_model_merged: 'q4f16' };
  return { encoder_model: f16 ? 'fp16' : 'fp32', decoder_model_merged: 'q4' };
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
  postMessage({ tipo: 'pronto', modello: `whisper-${nome}`, motore });
}

async function trascrivi({ id, audio, lingua }) {
  const t0 = performance.now();
  const out = await asr(audio, {
    language: lingua || null,          // null = rilevamento automatico
    task: 'transcribe',
    chunk_length_s: 30,
    stride_length_s: 5,
    return_timestamps: true,
  });
  const segmenti = (out.chunks || []).map(c => ({ t0: c.timestamp[0] ?? 0, t1: c.timestamp[1] ?? null, testo: c.text.trim() }))
    .filter(s => s.testo);
  postMessage({
    tipo: 'risultato', id, testo: (out.text || '').trim(), segmenti,
    secondi: (performance.now() - t0) / 1000, modello: chiave.split('|')[0], motore,
  });
}

// le richieste si eseguono una alla volta, nell'ordine di arrivo
let coda = Promise.resolve();
onmessage = e => {
  const m = e.data;
  coda = coda.then(async () => {
    try {
      await carica(m.modello, m.motore);
      if (m.tipo === 'trascrivi') await trascrivi(m);
      else postMessage({ tipo: 'fatto', id: m.id });
    } catch (err) {
      postMessage({ tipo: 'errore', id: m.id, testo: err && err.message ? err.message : String(err) });
    }
  });
};
