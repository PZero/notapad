// notªpad – app di prova (PWA locale): collega il dispositivo via Web Bluetooth, scarica i settori audio,
// li salva in IndexedDB e li fa ascoltare/scaricare in WAV. Protocollo in firmware/xiao-prova/protocollo.h.
import { SETT_BYTE, FREQ, verificaSettore, decodifica, wav, sessioni } from './adpcm.js';
import { soloParlato, tempoVero } from './vad.js';
import { trovaComandi, leggiStanze, chiamaHA, provaHA, statoHA } from './comandi.js';
import { assegna, turni, etichetta, media, aggiungiCampioni } from './voci.js';

const U = x => `a7d1000${x}-6e70-4b8f-9c4a-5f3e2b1d0c01`;
const $ = id => document.getElementById(id);
const enc = new TextEncoder(), dec = new TextDecoder();

// ---------- registro ----------
function log(t) {
  const r = `${new Date().toLocaleTimeString('it-IT')}  ${t}\n`;
  const el = $('log');
  el.textContent = (r + el.textContent).slice(0, 20000);
}

// ---------- IndexedDB ----------
// v1: settori (chiave seq) · v2: trascrizioni (chiave da = primo settore del pezzo trascritto, fino ad a)
let db;
const dbPronto = dbApri();       // aperto subito: se dopo qualcosa si rompe, i settori si salvano lo stesso
function dbApri() {
  return new Promise((ok, ko) => {
    const r = indexedDB.open('notapad', 2);
    r.onupgradeneeded = () => {
      const d = r.result;
      if (!d.objectStoreNames.contains('settori')) d.createObjectStore('settori', { keyPath: 'seq' });
      if (!d.objectStoreNames.contains('trascrizioni')) d.createObjectStore('trascrizioni', { keyPath: 'da' });
    };
    r.onsuccess = () => ok(db = r.result);
    r.onerror = () => ko(r.error);
  });
}
const tx = (modo, f, archivio = 'settori') => dbPronto.then(() => new Promise((ok, ko) => {
  const t = db.transaction(archivio, modo);
  const ris = f(t.objectStore(archivio));
  t.oncomplete = () => ok(ris && ris.result);
  t.onerror = () => ko(t.error);
}));
const dbMetti = rec => tx('readwrite', s => s.put(rec));
const dbPrendi = seq => tx('readonly', s => s.get(seq));
const dbCancella = seqs => tx('readwrite', s => seqs.forEach(q => s.delete(q)));
const dbTrascrizioni = () => tx('readonly', s => s.getAll(), 'trascrizioni');
const dbMettiTr = rec => tx('readwrite', s => s.put(rec), 'trascrizioni');
const dbCancellaTr = das => tx('readwrite', s => das.forEach(d => s.delete(d)), 'trascrizioni');
async function dbMeta() {
  await dbPronto;
  return new Promise((ok, ko) => {
    const out = [];
    const r = db.transaction('settori').objectStore('settori').openCursor();
    r.onsuccess = () => {
      const c = r.result;
      if (!c) return ok(out);
      const { dati, ...m } = c.value;
      out.push(m);
      c.continue();
    };
    r.onerror = () => ko(r.error);
  });
}

// ---------- Bluetooth ----------
let dev = null, ch = {}, collegato = false, voglioCollegato = false, stato = null;
let codaScritture = Promise.resolve();
const inArrivo = new Map();          // settore -> { buf, ricevuti }
let scaricoLocale = false, byteScaricati = 0, settoriOk = 0, t0Scarico = 0, ultimaRichiestaSync = 0;

function invia(t) {
  codaScritture = codaScritture
    .then(() => collegato && ch.cmd.writeValueWithResponse(enc.encode(t)))
    .catch(e => log('X scrittura: ' + e.message));
  return codaScritture;
}

async function collega(scegli) {
  if (!navigator.bluetooth) { avviso('Questo browser non ha Web Bluetooth: usa Edge o Chrome su Windows.'); return; }
  try {
    if (scegli || !dev) {
      dev = await navigator.bluetooth.requestDevice({ filters: [{ services: [U(0)] }], optionalServices: [U(0)] });
      dev.addEventListener('gattserverdisconnected', perso);
    }
    voglioCollegato = true;
    mostraStato('collego…');
    const srv = await (await dev.gatt.connect()).getPrimaryService(U(0));
    ch.cmd = await srv.getCharacteristic(U(1));
    ch.stato = await srv.getCharacteristic(U(2));
    ch.dati = await srv.getCharacteristic(U(3));
    ch.risp = await srv.getCharacteristic(U(4));
    // assegnazione (non addEventListener): al ricollegamento Chrome può ridare gli stessi oggetti
    ch.stato.oncharacteristicvaluechanged = e => suStato(e.target.value);
    ch.dati.oncharacteristicvaluechanged = e => suDati(e.target.value);
    ch.risp.oncharacteristicvaluechanged = e => suRisposta(dec.decode(e.target.value));
    await ch.risp.startNotifications();
    await ch.stato.startNotifications();
    await ch.dati.startNotifications();
    collegato = true;
    log(`collegato a ${dev.name}`);
    invia('TIME ' + Date.now());
    suStato(await ch.stato.readValue());
    aggiornaPulsanti();
  } catch (e) {
    log('X collegamento: ' + e.message);
    collegato = false;
    aggiornaPulsanti();
    if (voglioCollegato && dev) setTimeout(() => !collegato && voglioCollegato && collega(false), 3000);
  }
}

function perso() {
  collegato = false;
  scaricoLocale = false;
  inArrivo.clear();
  log('collegamento perso');
  aggiornaPulsanti();
  if (voglioCollegato) { mostraStato('riprovo…'); setTimeout(() => !collegato && voglioCollegato && collega(false), 3000); }
}

function scollega() {
  voglioCollegato = false;
  if (dev && dev.gatt.connected) dev.gatt.disconnect();
}

// all'apertura prova a ricollegare un dispositivo già autorizzato (se il browser lo permette)
async function ricollegaNoto() {
  if (!navigator.bluetooth || !navigator.bluetooth.getDevices) return;
  try {
    const noti = await navigator.bluetooth.getDevices();
    if (!noti.length) return;
    dev = noti[0];
    dev.addEventListener('gattserverdisconnected', perso);
    log(`dispositivo noto: ${dev.name}, attendo che sia in giro`);
    if (dev.watchAdvertisements) {
      const ac = new AbortController();
      dev.addEventListener('advertisementreceived', () => { ac.abort(); collega(false); }, { once: true });
      await dev.watchAdvertisements({ signal: ac.signal });
    } else collega(false);
  } catch (e) { log('ricollegamento automatico non disponibile: ' + e.message); }
}

// ---------- stato del dispositivo ----------
function suStato(v) {
  if (v.byteLength < 20) return;
  stato = {
    flag: v.getUint8(1), usati: v.getUint16(2, true), totali: v.getUint16(4, true), mv: v.getUint16(6, true),
    seq: v.getUint32(8, true), acceso: v.getUint32(12, true), pct: v.getUint8(16),
    fw: `${v.getUint8(17)}.${v.getUint8(18)}.${v.getUint8(19)}`,
  };
  const f = stato.flag;
  $('barra').style.width = stato.pct + '%';
  $('barra').style.background = f & 2 ? 'var(--err)' : stato.pct >= 80 ? 'var(--warn)' : 'var(--acc)';
  $('kMem').textContent = `${stato.pct}%`;
  $('kMin').textContent = durata(stato.usati * 8120 / FREQ);
  $('kBatt').textContent = stato.mv ? `${(stato.mv / 1000).toFixed(2)} V` : '—';
  $('kFw').textContent = `${stato.fw} · ${durata(stato.acceso)}`;
  const c = [];
  if (f & 1) c.push('<span class="chip e">registra</span>');
  if (f & 2) c.push('<span class="chip e">memoria piena</span>');
  if (f & 4) c.push('<span class="chip w">da sincronizzare</span>');
  if (f & 8) c.push('<span class="chip">USB</span>');
  if (f & 16) c.push('<span class="chip a">scarico</span>');
  if (f & 64) c.push('<span class="chip e">batteria bassa</span>');
  $('chips').innerHTML = c.join(' ');
  $('bRec').textContent = f & 1 ? 'Ferma registrazione' : 'Avvia registrazione';
  $('pall').className = 'pall ' + (f & 1 ? 'rec' : 'on');
  mostraStato(f & 1 ? 'collegato · registra' : 'collegato');
  if (!(f & 16) && scaricoLocale && inArrivo.size === 0 && Date.now() - ultimaRichiestaSync > 3000) fineScarico();
  // sincronizzazione automatica all'80%
  if ($('cAuto').checked && (f & 4) && !(f & 16) && !scaricoLocale && Date.now() - ultimaRichiestaSync > 10000) {
    log(`memoria al ${stato.pct}%: sincronizzo`);
    sincronizza();
  }
}

// tocco singolo sul notªpad: «K cmd <primo> <ultimo>» = settori di un comando, scaricati subito
let cmdSeq = new Set();
const cmdAttesi = new Set();          // settori del comando non ancora arrivati
function suRisposta(t) {
  log(t);
  const m = t.match(/^K cmd (\d+) (\d+)$/);
  if (m) { for (let q = +m[1]; q <= +m[2]; q++) { cmdSeq.add(q); cmdAttesi.add(q); } if (!scaricoLocale) { scaricoLocale = true; ultimaRichiestaSync = Date.now(); byteScaricati = 0; settoriOk = 0; t0Scarico = performance.now(); } }
  if (t.startsWith('K sync fine') && scaricoLocale) fineScarico();
}

function sincronizza() {
  ultimaRichiestaSync = Date.now();
  scaricoLocale = true;
  byteScaricati = 0; settoriOk = 0; t0Scarico = performance.now();
  invia('SYNC');
  aggiornaPulsanti();
}
function fineScarico() {
  scaricoLocale = false;
  const s = (performance.now() - t0Scarico) / 1000;
  if (settoriOk) log(`scarico finito: ${settoriOk} settori, ${(byteScaricati / 1024).toFixed(0)} KB in ${s.toFixed(1)} s`);
  aggiornaPulsanti();
  cmdAttesi.clear();
  aggiornaLista().then(async () => { await trascriviComando(); trascriviNuove(); });
}
// il pezzo del comando va in testa alla coda delle trascrizioni
async function trascriviComando() {
  const qs = [...cmdSeq].sort((a, b) => a - b); cmdSeq = new Set();
  const presenti = [];
  for (const q of qs) if (await dbPrendi(q)) presenti.push(q);
  if (!presenti.length) return;
  presenti.forEach(q => { comandoSeq.add(q); inCodaSeq.add(q); });
  log(`comando arrivato (${presenti.length} settori): lo trascrivo subito`);
  await aggiornaLista();
  // secondo trascrittore, solo per i comandi: whisper-base su CPU, in parallelo a quello lungo (che resta sulla GPU)
  try {
    const primo = await dbPrendi(presenti[0]);
    const pcm = await pcmDi(presenti);
    const audio = Float32Array.from(pcm, x => x / 32768);
    const t0 = performance.now();
    const r = await chiediComando({ tipo: 'trascrivi', audio, lingua: $('sLingua').value, voci: false }, [audio.buffer]);
    const base = { da: presenti[0], a: presenti[presenti.length - 1], ms: primo.ms, avvio: primo.avvio, durata: pcm.length / FREQ, data: Date.now(), lingua: $('sLingua').value };
    await dbMettiTr({ ...base, testo: r.testo, segmenti: [], parole: r.parole, finestre: [], voci: true, comando: true, modello: r.modello, motore: r.motore, secondi: r.secondi });
    log(`comando trascritto in ${((performance.now() - t0) / 1000).toFixed(1)} s: «${r.testo}»`);
    await eseguiComandi(base, r.parole, [], true);
  } catch (e) { log('X comando: ' + e.message); }
  finally { presenti.forEach(q => inCodaSeq.delete(q)); aggiornaTesti(); }
}
let workerCmd = null; const atteseCmd = new Map();
function chiediComando(msg, trasferibili = []) {
  if (!workerCmd) {
    workerCmd = new Worker('trascrittore.js', { type: 'module' });
    workerCmd.onmessage = e => {
      const m = e.data, p = atteseCmd.get(m.id);
      if (m.tipo === 'pronto') log(`comandi: pronto ${m.modello} (${m.motore})`);
      if (!p || !['risultato', 'fatto', 'errore'].includes(m.tipo)) return;
      atteseCmd.delete(m.id);
      m.tipo === 'errore' ? p.ko(new Error(m.testo)) : p.ok(m);
    };
  }
  return new Promise((ok, ko) => {
    const id = ++nId;
    atteseCmd.set(id, { ok, ko });
    workerCmd.postMessage({ ...msg, id, modello: 'base', motore: 'wasm' }, trasferibili);
  });
}
const comandoSeq = new Set();

// ---------- dati ----------
function suDati(v) {
  const sett = v.getUint16(0, true), off = v.getUint16(2, true);
  const pezzo = new Uint8Array(v.buffer, v.byteOffset + 4, v.byteLength - 4);
  let a = inArrivo.get(sett);
  if (off === 0 || !a) { a = { buf: new Uint8Array(SETT_BYTE), ricevuti: 0 }; inArrivo.set(sett, a); }
  if (off + pezzo.length > SETT_BYTE) return;
  a.buf.set(pezzo, off);
  a.ricevuti += pezzo.length;
  byteScaricati += pezzo.length;
  const s = (performance.now() - t0Scarico) / 1000;
  $('kSync').textContent = `${settoriOk} sett · ${(byteScaricati / 1024 / Math.max(s, 0.1)).toFixed(1)} KB/s`;
  if (off + pezzo.length < SETT_BYTE) return;
  inArrivo.delete(sett);
  if (a.ricevuti !== SETT_BYTE) { log(`X settore ${sett}: pezzi mancanti`); invia('NAK ' + sett); return; }
  const r = verificaSettore(a.buf);
  if (!r.ok) {
    // un settore senza magic non è audio (non dovrebbe succedere): lo si conferma per liberarlo
    log(`X settore ${sett}: ${r.motivo}`);
    invia(r.motivo === 'crc' ? 'NAK ' + sett : 'ACK ' + sett);
    return;
  }
  const t = r.testa;
  dbMetti({ ...t, dati: a.buf.slice(36).buffer, scaricato: Date.now() })
    .then(() => {
      settoriOk++; invia('ACK ' + sett);
      // il comando è arrivato tutto (anche a metà di uno scarico lungo): si trascrive subito, prima del resto
      if (cmdAttesi.delete(t.seq) && !cmdAttesi.size) trascriviComando();
    })
    .catch(e => log('X salvataggio: ' + e.message));
}

// ---------- registrazioni salvate ----------
let urlAudio = [], gruppi = [], pezzi = [];
const nomeFile = (s, est) => {
  const d = s.inizio ? new Date(s.inizio) : new Date();
  return `notapad_${d.toISOString().slice(0, 19).replace(/[-:T]/g, '')}.${est}`;
};
function scarica(blob, nome) {
  const u = URL.createObjectURL(blob); urlAudio.push(u);
  const a = document.createElement('a'); a.href = u; a.download = nome; a.click();
}
async function aggiornaLista() {
  const meta = await dbMeta();
  const g = gruppi = sessioni(meta).reverse();
  urlAudio.forEach(u => URL.revokeObjectURL(u)); urlAudio = [];
  $('vuota').style.display = g.length ? 'none' : 'block';
  $('lista').innerHTML = g.map((s, i) => `<tr>
    <td>${s.inizio ? new Date(s.inizio).toLocaleString('it-IT') : `avvio ${s.avvio}, +${durata(s.msInizio / 1000)}`}</td>
    <td class="n">${durata(s.campioni / FREQ)}</td><td>${s.seqs.length}</td>
    <td><button data-a="ascolta" data-i="${i}">Ascolta</button> <span id="pl${i}"></span></td>
    <td><button data-a="wav" data-i="${i}">WAV</button> <button data-a="del" data-i="${i}">Elimina</button></td></tr>
    <tr class="tr"><td colspan="5" id="tx${i}"></td></tr>`).join('');
  $('lista').onclick = async e => {
    const b = e.target.closest('button'); if (!b) return;
    const i = +b.dataset.i, s = g[i];
    if (b.dataset.a === 'del') {
      if (!confirm('Eliminare questa registrazione (audio e testo) dal PC?')) return;
      await dbCancella(s.seqs); await dbCancellaTr(pezziDi(s).map(p => p.da)); aggiornaLista(); return;
    }
    if (b.dataset.a === 'trascrivi') { await ritrascrivi(s); return; }
    if (b.dataset.a === 'io') { sonoIo(s, +b.dataset.n); return; }
    if (b.dataset.a === 'txt') { scarica(new Blob([testoDi(s, true)], { type: 'text/plain;charset=utf-8' }), nomeFile(s, 'txt')); return; }
    if (b.dataset.a === 'tutto') { $('tx' + i).querySelector('.testo').classList.toggle('aperto'); return; }
    const blob = wav(await pcmDi(s.seqs));
    if (b.dataset.a === 'ascolta') {
      const u = URL.createObjectURL(blob); urlAudio.push(u);
      $('pl' + i).innerHTML = `<audio controls autoplay src="${u}"></audio>`;
    } else scarica(blob, nomeFile(s, 'wav'));
  };
  await aggiornaTesti();
}
async function pcmDi(seqs) {
  const parti = [];
  let n = 0;
  for (const q of seqs) {
    const r = await dbPrendi(q);
    const pcm = decodifica(new Uint8Array(r.dati), r.campioni, r.pred, r.indice);
    parti.push(pcm); n += pcm.length;
  }
  const tutto = new Int16Array(n);
  let o = 0; for (const p of parti) { tutto.set(p, o); o += p.length; }
  return tutto;
}

// ---------- trascrizione (Whisper nel browser: trascrittore.js) ----------
// Ogni sincronizzazione porta settori nuovi: si trascrivono a pezzi (al massimo PEZZO_MAX settori, ~5 min)
// i settori di ogni registrazione non ancora coperti da un pezzo. Tutto resta sul dispositivo.
const PEZZO_MAX = 120;                 // ~1 min: pezzi corti, così niente resta in coda a lungo
const telefono = /Android|Mobi/i.test(navigator.userAgent);
// sul PC con WebGPU fp16 il modello automatico è large-v3-turbo: molto meglio in italiano con voci lontane
let gpuF16 = false;
if (navigator.gpu) navigator.gpu.requestAdapter().then(a => { gpuF16 = !!(a && a.features.has('shader-f16')); }).catch(() => {});
const esc = t => t.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
// frasi che Whisper "inventa" sul silenzio o sul rumore (soprattutto in italiano)
const ALLUCINAZIONI = [/sottotitoli (creati|a cura|e revisione)/i, /amara\.org/i, /grazie (a tutti )?per (la visione|l'ascolto|aver guardato)/i,
  /^(\W*|grazie\.?|\.\.\.|musica)$/i, /iscriviti al canale/i];
const allucinazione = t => ALLUCINAZIONI.some(r => r.test(t.trim()));

let worker = null, nId = 0, trInCorso = null;
const attese = new Map(), inCodaSeq = new Set();
let codaTr = Promise.resolve();

function trWorker() {
  if (worker) return worker;
  worker = new Worker('trascrittore.js', { type: 'module' });
  worker.onmessage = e => {
    const m = e.data;
    if (m.tipo === 'download') $('kTr').textContent = `modello ${(m.caricati / 1e6).toFixed(0)}/${(m.totali / 1e6).toFixed(0)} MB`;
    else if (m.tipo === 'stato') { log(m.testo); $('kTr').textContent = m.testo; }
    else if (m.tipo === 'pronto') { log(`pronto ${m.modello} (${m.motore})`); $('kMotore').textContent = `${m.modello} · ${m.motore}`; $('kTr').textContent = 'pronta'; }
    else {
      const p = attese.get(m.id); attese.delete(m.id);
      if (p) m.tipo === 'errore' ? p.ko(new Error(m.testo)) : p.ok(m);
    }
  };
  worker.onerror = e => {
    log('X trascrittore: ' + (e.message || 'il worker non parte'));
    attese.forEach(p => p.ko(new Error('worker fermo'))); attese.clear();
    worker = null;
  };
  return worker;
}
function modelloScelto() {
  const v = $('sModello').value;
  return v === 'auto' ? (telefono ? 'base' : 'small') : v;   // small: ~3× più veloce di turbo, turbo si sceglie a mano
}
function chiedi(msg, trasferibili = []) {
  if (navigator.storage && navigator.storage.persist) navigator.storage.persist();   // il modello non va buttato via
  return new Promise((ok, ko) => {
    const id = ++nId;
    attese.set(id, { ok, ko });
    trWorker().postMessage({ ...msg, id, modello: modelloScelto(), motore: $('sMotore').value }, trasferibili);
  });
}

async function trascriviNuove(forza = false) {
  if (!forza && !$('cTrascrivi').checked) return;
  pezzi = await dbTrascrizioni();
  const coperti = new Set();
  for (const p of pezzi) for (let q = p.da; q <= p.a; q++) coperti.add(q);
  for (const s of [...gruppi].reverse()) {             // dalla più vecchia
    let run = [];
    const chiudi = () => { if (run.length) accoda(run); run = []; };
    for (const q of s.seqs) {
      if (coperti.has(q) || inCodaSeq.has(q)) { chiudi(); continue; }
      run.push(q);
      if (run.length >= PEZZO_MAX) chiudi();
    }
    chiudi();
  }
}
async function ritrascrivi(s) {
  if (s.seqs.some(q => inCodaSeq.has(q))) return;
  await dbCancellaTr(pezziDi(s).map(p => p.da));
  pezzi = await dbTrascrizioni();
  for (let i = 0; i < s.seqs.length; i += PEZZO_MAX) accoda(s.seqs.slice(i, i + PEZZO_MAX));
}
function accoda(seqs) {
  seqs.forEach(q => inCodaSeq.add(q));
  aggiornaTesti();
  codaTr = codaTr
    .then(() => trascriviPezzo(seqs))
    .catch(e => { log('X trascrizione: ' + e.message); $('kTr').textContent = 'errore'; })
    .finally(() => { trInCorso = null; seqs.forEach(q => inCodaSeq.delete(q)); aggiornaTesti(); });
}
async function trascriviPezzo(seqs) {
  const primo = await dbPrendi(seqs[0]);
  if (!primo) return;                                  // registrazione eliminata nel frattempo
  const pcm = await pcmDi(seqs);
  const audio = new Float32Array(pcm.length);
  let e2 = 0;
  for (let i = 0; i < pcm.length; i++) { const v = pcm[i] / 32768; audio[i] = v; e2 += v * v; }
  const rms = Math.sqrt(e2 / Math.max(1, pcm.length));
  const lingua = $('sLingua').value;
  const base = { da: seqs[0], a: seqs[seqs.length - 1], ms: primo.ms, avvio: primo.avvio, durata: pcm.length / FREQ, data: Date.now(), lingua };
  if (rms < 0.0015) {                                  // solo silenzio: niente Whisper (inventerebbe frasi)
    await dbMettiTr({ ...base, testo: '', segmenti: [], silenzio: true });
    log(`${durata(base.durata)} di silenzio, niente da trascrivere`);
    return;
  }
  // solo i tratti con voce a Whisper (molto più veloce), poi i tempi tornano quelli veri
  const v = soloParlato(audio);
  trInCorso = { t0: Date.now(), durata: v.audio.length / FREQ };
  const r = await chiedi({ tipo: 'trascrivi', audio: v.audio, lingua }, [v.audio.buffer]);
  const vero = t => +tempoVero(t, v.mappa).toFixed(2);
  r.parole = (r.parole || []).map(w => ({ ...w, t0: vero(w.t0), t1: vero(w.t1) }));
  if (r.finestre) r.finestre = r.finestre.map(f => ({ ...f, t0: vero(f.t0), t1: vero(f.t0) + (f.t1 - f.t0) }));
  if (v.parlato < 0.85) log(`parlato ${Math.round(v.parlato * 100)}% del pezzo: a Whisper ${durata(v.audio.length / FREQ)} su ${durata(base.durata)}`);
  // formato 3: parole con l'ora + finestre con l'impronta; frasi e turni si ricavano quando si mostra
  const parole = allucinazione(r.testo) ? [] : r.parole;
  await dbMettiTr({ ...base, testo: r.testo, segmenti: [], parole, finestre: r.finestre || [], voci: true,
    modello: r.modello, motore: r.motore, secondi: r.secondi });
  log(`trascritti ${durata(base.durata)} di audio in ${r.secondi.toFixed(1)} s (whisper-${r.modello}, ${r.motore})` +
    (r.finestre ? `, voci in ${r.secondiVoci.toFixed(1)} s` : ''));
  eseguiComandi(base, parole, r.finestre || [], comandoSeq.has(seqs[0]) || !!primo.comando).catch(e => log('X comando: ' + e.message));
}

// pezzi trascritti prima del riconoscimento delle voci: si calcolano solo le impronte (senza Whisper)
async function vociMancanti() {
  for (const p of await dbTrascrizioni()) {
    if (p.voci || !(p.segmenti || []).length || vociInCoda.has(p.da)) continue;
    vociInCoda.add(p.da);
    codaTr = codaTr.then(async () => {
      const seqs = []; for (let q = p.da; q <= p.a; q++) seqs.push(q);
      const esistenti = [];
      for (const q of seqs) if (await dbPrendi(q)) esistenti.push(q);
      if (!esistenti.length) return;
      const pcm = await pcmDi(esistenti);
      const audio = Float32Array.from(pcm, v => v / 32768);
      $('kTr').textContent = 'riconosco le voci…';
      const r = await chiedi({ tipo: 'voci', audio, segmenti: p.segmenti.map(({ t0, t1 }) => ({ t0, t1 })) }, [audio.buffer]);
      await dbMettiTr({ ...p, voci: true, segmenti: p.segmenti.map((x, i) => ({ ...x, voce: r.impronte[i] })) });
      $('kTr').textContent = 'pronta';
      aggiornaTesti();
    }).catch(e => log('X voci: ' + e.message)).finally(() => vociInCoda.delete(p.da));
  }
}
const vociInCoda = new Set();

// ---------- comandi vocali → Home Assistant ----------
// Solo comandi detti da poco (COMANDO_MAX_MIN) e, se c'è il profilo, solo con la voce del proprietario.
// Ogni comando si esegue una volta sola (chiave = primo settore del pezzo + secondo), anche se si ritrascrive.
const COMANDO_MAX_MIN = 10;
const conf = () => ({ url: $('hUrl').value.trim(), token: $('hToken').value.trim(), stanze: leggiStanze($('hStanze').value) });
async function eseguiComandi(p, parole, finestre, daTocco = false) {
  const c = conf();
  if (!$('cComandi').checked || !c.url || !c.token) { if (daTocco) log('comando non eseguito: attiva «Esegui i comandi» e inserisci indirizzo e token'); return; }
  const s = gruppi.find(g => g.seqs.includes(p.da));
  if (!s || !s.inizio) { if (daTocco) log('comando non eseguito: registrazione senza ora'); return; }
  let fatti = []; try { fatti = JSON.parse(localStorage.getItem('np-comandi-fatti')) || []; } catch {}
  // dopo il tocco singolo basta «accendi la luce»: il tocco vale come la parola «Comando»
  const tt = daTocco ? [{ t0: 0, testo: 'comando ' + parole.map(w => w.testo).join(''), chi: 'io' }]
    : turni(parole, finestre, profiloMedia, { delta: delta() });
  if (daTocco && !trovaComandi(tt[0].testo, c.stanze).length) log(`nessun comando riconosciuto in «${tt[0].testo.slice(8)}»`);
  for (const t of tt) {
    if (profiloMedia && t.chi !== 'io') continue;
    const quando = s.inizio + ((p.ms - s.msInizio) / 1000 + t.t0) * 1000;
    for (const k of trovaComandi(t.testo, c.stanze)) {
      const id = `${p.da}:${Math.round(t.t0)}:${k.frase}`;
      if (fatti.includes(id)) continue;
      fatti = [...fatti, id].slice(-200);
      try { localStorage.setItem('np-comandi-fatti', JSON.stringify(fatti)); } catch {}
      if (Date.now() - quando > COMANDO_MAX_MIN * 60000) { log(`comando vecchio, non eseguito: «${k.frase}»`); continue; }
      await chiamaHA(c, k);
      log(`comando eseguito: «${k.frase}» → ${k.azione} ${k.entita}`);
    }
  }
}

// ---------- la voce del proprietario ----------
// Profilo = impronte della sua voce, nel browser (localStorage). Si costruisce registrando 30 s col
// microfono di questo dispositivo, oppure toccando "Interlocutore N" in una trascrizione → "sono io"
// (meglio: stesso microfono del notªpad).
let profilo = null, profiloMedia = null;
try { profilo = JSON.parse(localStorage.getItem('np-voce-io')); } catch {}
function salvaProfilo(p) {
  profilo = p;
  profiloMedia = p && p.campioni.length ? media(p.campioni) : null;
  try { p ? localStorage.setItem('np-voce-io', JSON.stringify(p)) : localStorage.removeItem('np-voce-io'); } catch {}
  if ($('kVoce')) $('kVoce').textContent = p && p.campioni.length ? `${p.campioni.length} campioni` : 'non registrata';
  if ($('bVoceVia')) $('bVoceVia').disabled = !p;
  aggiornaTesti();
}
async function registraVoce() {
  const b = $('bVoce');
  if (!navigator.mediaDevices || !window.MediaRecorder) { avviso('Questo browser non permette di registrare dal microfono.'); return; }
  let flusso;
  try { flusso = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: true } }); }
  catch (e) { log('X microfono: ' + e.message); return; }
  const rec = new MediaRecorder(flusso), parti = [];
  rec.ondataavailable = e => parti.push(e.data);
  const fine = new Promise(ok => rec.onstop = ok);
  rec.start();
  $('pVoce').style.display = 'block';
  b.disabled = true;
  let s = 30;
  const conta = setInterval(() => { s--; $('bVoceStop').textContent = `Ho finito (${s} s)`; if (s <= 0) rec.stop(); }, 1000);
  $('bVoceStop').textContent = `Ho finito (${s} s)`;
  $('bVoceStop').onclick = () => rec.state === 'recording' && rec.stop();
  await fine;
  clearInterval(conta);
  flusso.getTracks().forEach(t => t.stop());
  $('pVoce').style.display = 'none';
  try {
    const ctx = new AudioContext({ sampleRate: FREQ });
    const buf = await ctx.decodeAudioData(await new Blob(parti).arrayBuffer());
    ctx.close();
    const audio = buf.getChannelData(0).slice();
    $('kVoce').textContent = 'analizzo…';
    const r = await chiedi({ tipo: 'campione', audio }, [audio.buffer]);
    if (r.impronte.length < 3) { log(`voce: solo ${r.impronte.length} pezzi con parlato, riprova parlando di più`); salvaProfilo(profilo); }
    else { salvaProfilo(aggiungiCampioni(profilo, r.impronte)); log(`voce del proprietario: ${r.impronte.length} campioni aggiunti`); }
  } catch (e) { log('X voce: ' + e.message); salvaProfilo(profilo); }
  b.disabled = false;
}

const pezziDi = s => { const q = new Set(s.seqs); return pezzi.filter(p => q.has(p.da)).sort((a, b) => a.da - b.da); };
// segmenti con l'ora: assoluta se la registrazione ha l'ora vera, altrimenti relativa all'inizio
const delta = () => +($('rSep') ? $('rSep').value : 0);
function righeDi(s) {
  const oraDi = t => s.inizio ? new Date(s.inizio + t * 1000).toLocaleTimeString('it-IT')
    : `+${String(Math.floor(t / 60)).padStart(2, '0')}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
  const vecchie = [], parole = [], finestre = [];
  for (const p of pezziDi(s)) {
    const off = (p.ms - s.msInizio) / 1000;
    for (const x of p.segmenti || [])
      vecchie.push({ t: off + (x.t0 || 0), testo: x.testo, voce: x.voce || null, durata: x.t1 != null ? x.t1 - (x.t0 || 0) : 0 });
    for (const w of p.parole || []) parole.push({ ...w, t0: w.t0 + off, t1: w.t1 + off });
    for (const f of p.finestre || []) finestre.push({ ...f, t0: f.t0 + off, t1: f.t1 + off });
  }
  // ordine cronologico vero, qualunque sia stato l'ordine di scarico e di trascrizione
  parole.sort((a, b) => a.t0 - b.t0); finestre.sort((a, b) => a.t0 - b.t0); vecchie.sort((a, b) => a.t - b.t);
  if (vecchie.length && parole.length)                 // registrazione mista: le frasi vecchie diventano "parole"
    for (const v of vecchie.splice(0)) parole.push({ t0: v.t, t1: v.t + v.durata, testo: ' ' + v.testo });
  parole.sort((a, b) => a.t0 - b.t0);
  if (vecchie.length) {                                // trascrizioni fatte prima del 22/11 sera: una voce per frase
    const chi = assegna(vecchie, profiloMedia, { delta: delta() });
    return vecchie.map((r, i) => ({ ...r, ...chi[i], ora: oraDi(r.t), campioni: r.voce ? [r.voce] : [] }));
  }
  // chi parla, a turni: numeri degli interlocutori propri di ogni registrazione
  return turni(parole, finestre, profiloMedia, { delta: delta() }).filter(t => !allucinazione(t.testo)).map(t => ({
    ...t, ora: oraDi(t.t0),
    campioni: finestre.filter(f => f.t0 >= t.t0 - 0.2 && f.t1 <= t.t1 + 0.2).map(f => Array.from(f.voce, x => x / 127)),
  }));
}
const conVoci = righe => righe.some(r => r.chi);
const testoDi = (s, conOra) => {
  const righe = righeDi(s), v = conVoci(righe);
  return righe.map(r => (conOra ? `[${r.ora}] ` : '') + (v ? etichetta(r.chi) + ': ' : '') + r.testo).join('\n');
};
// "Interlocutore N sono io": le sue impronte in questa registrazione vanno nel profilo del proprietario
function sonoIo(s, n) {
  const imp = righeDi(s).filter(r => r.chi === n && !r.dedotto).flatMap(r => r.campioni).slice(-100);
  if (!imp.length) return;
  if (!confirm(`${etichetta(n)} sei tu? Le sue ${imp.length} frasi diventano campioni della tua voce.`)) return;
  salvaProfilo(aggiungiCampioni(profilo, imp));
  log(`voce del proprietario: ${imp.length} campioni presi da una registrazione`);
}

const chip = (r, i) => {
  const t = r.sim != null ? ` title="somiglianza ${r.sim.toFixed(2)}"` : ' title="frase corta: come la precedente"';
  if (r.chi === 'io') return `<b class="chi io"${t}>Io</b>`;
  if (!r.chi) return `<b class="chi"${t}>?</b>`;
  return `<button class="chi c${(r.chi - 1) % 6}" data-a="io" data-i="${i}" data-n="${r.chi}"${t}>${etichetta(r.chi)}</button>`;
};
async function aggiornaTesti() {
  pezzi = await dbTrascrizioni();
  gruppi.forEach((s, i) => {
    const cella = $('tx' + i); if (!cella) return;
    const inCoda = s.seqs.some(q => inCodaSeq.has(q));
    const pz = pezziDi(s), righe = righeDi(s);
    const coperti = pz.reduce((n, p) => n + p.a - p.da + 1, 0);
    let stato = '';
    if (inCoda) stato = '<span class="chip a">trascrivo…</span>';
    else if (!pz.length) stato = '<span class="chip">non trascritta</span>';
    else if (coperti < s.seqs.length) stato = '<span class="chip w">trascritta in parte</span>';
    else if (!righe.length) stato = '<span class="chip">nessun parlato</span>';
    const info = pz.find(p => p.modello);
    cella.innerHTML = `<div class="riga">${stato}
      ${righe.length ? `<div class="testo">${righe.map(r => `<p><time>${r.ora}</time> ${conVoci(righe) ? chip(r, i) : ''}${esc(r.testo)}</p>`).join('')}</div>` : ''}
      <span class="az">${righe.length > 3 ? `<button data-a="tutto" data-i="${i}">Tutto</button> ` : ''}
      ${righe.length ? `<button data-a="txt" data-i="${i}">TXT</button> ` : ''}
      <button data-a="trascrivi" data-i="${i}" ${inCoda ? 'disabled' : ''}>${pz.length ? 'Ritrascrivi' : 'Trascrivi'}</button>
      ${info ? `<small>whisper-${info.modello} · ${info.motore}</small>` : ''}</span></div>`;
  });
  const n = new Set([...inCodaSeq]).size;
  if (!trInCorso && !n && $('kTr').textContent.startsWith('trascrivo')) $('kTr').textContent = 'pronta';
}
setInterval(() => {
  if (!trInCorso) return;
  const s = (Date.now() - trInCorso.t0) / 1000;
  $('kTr').textContent = `trascrivo ${durata(trInCorso.durata)} · ${durata(s)}${inCodaSeq.size > trInCorso.durata * 2 ? ' (altro in coda)' : ''}`;
}, 1000);

// ---------- interfaccia ----------
function durata(s) {
  s = Math.round(s);
  if (s < 60) return `${s} s`;
  if (s < 3600) return `${Math.floor(s / 60)} min ${s % 60} s`;
  return `${Math.floor(s / 3600)} h ${Math.floor(s % 3600 / 60)} min`;
}
function mostraStato(t) { $('statoTxt').textContent = t; if (!collegato) $('pall').className = 'pall'; }
function avviso(t) { $('avviso').style.display = 'block'; $('avviso').textContent = t; }
function aggiornaPulsanti() {
  $('bCollega').disabled = collegato;
  $('bScollega').disabled = !collegato && !voglioCollegato;
  for (const id of ['bRec', 'bInfo', 'bWipe']) $(id).disabled = !collegato;
  $('bSync').disabled = !collegato || scaricoLocale;
  if (!collegato) mostraStato(voglioCollegato ? 'riprovo…' : 'non collegato');
}

$('bCollega').onclick = () => collega(true);      // sempre la finestra di scelta (il ricollegamento automatico resta)
$('bScollega').onclick = scollega;
$('bRec').onclick = () => invia(stato && stato.flag & 1 ? 'REC 0' : 'REC 1');
$('bSync').onclick = sincronizza;
$('bInfo').onclick = () => invia('INFO');
$('bWipe').onclick = () => confirm('Cancellare tutta la memoria del dispositivo? I dati non scaricati andranno persi.') && invia('WIPE');
$('cAuto').checked = localStorage.getItem('np-auto') !== '0';
$('cAuto').onchange = e => localStorage.setItem('np-auto', e.target.checked ? '1' : '0');
// impostazioni della trascrizione, ricordate nel browser
for (const [id, k, pred] of [['cTrascrivi', 'np-tr', '1'], ['sModello', 'np-modello', 'auto'], ['sLingua', 'np-lingua', 'italian'], ['sMotore', 'np-motore', 'auto']]) {
  const el = $(id), v = localStorage.getItem(k) ?? pred;
  if (el.type === 'checkbox') el.checked = v === '1'; else el.value = v;
  el.onchange = () => localStorage.setItem(k, el.type === 'checkbox' ? (el.checked ? '1' : '0') : el.value);
}
$('cTrascrivi').addEventListener('change', e => e.target.checked && trascriviNuove());
$('bModello').onclick = async () => {
  $('bModello').disabled = true;
  try { await chiedi({ tipo: 'carica' }); } catch (e) { log('X modello: ' + e.message); $('kTr').textContent = 'errore'; }
  $('bModello').disabled = false;
};
$('kMotore').textContent = `${navigator.gpu ? 'WebGPU' : 'WASM'}${navigator.gpu ? '' : crossOriginIsolated ? ' multithread' : ' 1 thread'} · ${modelloScelto()}`;

if (!window.isSecureContext) avviso('Apri la pagina da http://localhost (avvia.cmd) o da https: Web Bluetooth funziona solo in un contesto sicuro.');
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
  // il service worker aggiunge le intestazioni COOP/COEP: alla prima apertura serve un ricaricamento
  // per avere WASM multithread (conta soprattutto su Android, dove spesso manca WebGPU)
  if (!crossOriginIsolated && !sessionStorage.getItem('np-ricaricata'))
    navigator.serviceWorker.addEventListener('controllerchange', () => { sessionStorage.setItem('np-ricaricata', '1'); location.reload(); }, { once: true });
}
for (const [id, k] of [['hUrl', 'np-ha-url'], ['hToken', 'np-ha-token'], ['hStanze', 'np-ha-stanze'], ['cComandi', 'np-comandi']]) {
  const el = $(id); let v = null; try { v = localStorage.getItem(k); } catch {}
  if (v !== null) { if (el.type === 'checkbox') el.checked = v === '1'; else el.value = v; }
  el.onchange = () => { try { localStorage.setItem(k, el.type === 'checkbox' ? (el.checked ? '1' : '0') : el.value); } catch {} };
}
// pulsanti di prova: un pulsante per ogni riga della lista (luce, ventilatore…), mostrano lo stato
async function pulsantiHA() {
  const c = conf(), box = $('hPuls');
  box.innerHTML = c.stanze.map(([n, e]) => `<button data-e="${esc(e)}">${esc(n)}: <b>…</b></button>`).join(' ');
  if (!c.url || !c.token) return;
  for (const b of box.querySelectorAll('button')) {
    const agg = async () => { try { b.querySelector('b').textContent = (await statoHA(conf(), b.dataset.e)) === 'on' ? 'accesa' : 'spenta'; } catch { b.querySelector('b').textContent = '?'; } };
    b.onclick = async () => {
      try { await chiamaHA(conf(), { azione: 'toggle', entita: b.dataset.e }); log(`${b.textContent.split(':')[0]}: toggle ${b.dataset.e}`); }
      catch (e) { log('X Home Assistant: ' + e.message); }
      setTimeout(agg, 400);
    };
    agg();
  }
}
for (const id of ['hUrl', 'hToken', 'hStanze']) $(id).addEventListener('change', pulsantiHA);
pulsantiHA();
// con i comandi attivi il trascrittore dei comandi si prepara subito (il primo comando non aspetta il download)
const preparaComandi = () => $('cComandi').checked && chiediComando({ tipo: 'carica' }).catch(e => log('X comandi: ' + e.message));
$('cComandi').addEventListener('change', preparaComandi);
preparaComandi();
$('bHa').onclick = async () => {
  try { log('Home Assistant: ' + await provaHA(conf())); pulsantiHA(); }
  catch (e) { log('X Home Assistant: ' + e.message + ' (indirizzo, token o cors_allowed_origins?)'); }
};
if ($('bVoce')) $('bVoce').onclick = registraVoce;
if ($('rSep')) { try { $('rSep').value = localStorage.getItem('np-sep') ?? 0; } catch {}
  $('rSep').oninput = () => { try { localStorage.setItem('np-sep', $('rSep').value); } catch {} aggiornaTesti(); }; }
if ($('bVoceVia')) $('bVoceVia').onclick = () => confirm('Cancellare il profilo della tua voce da questo dispositivo?') && salvaProfilo(null);
salvaProfilo(profilo);
aggiornaLista().then(() => { trascriviNuove(); vociMancanti(); });
aggiornaPulsanti();
ricollegaNoto();
