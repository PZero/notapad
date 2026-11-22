// notªpad – app di prova (PWA locale): collega il dispositivo via Web Bluetooth, scarica i settori audio,
// li salva in IndexedDB e li fa ascoltare/scaricare in WAV. Protocollo in firmware/xiao-prova/protocollo.h.
import { SETT_BYTE, FREQ, verificaSettore, decodifica, wav, sessioni } from './adpcm.js';

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
const tx = (modo, f, archivio = 'settori') => new Promise((ok, ko) => {
  const t = db.transaction(archivio, modo);
  const ris = f(t.objectStore(archivio));
  t.oncomplete = () => ok(ris && ris.result);
  t.onerror = () => ko(t.error);
});
const dbMetti = rec => tx('readwrite', s => s.put(rec));
const dbPrendi = seq => tx('readonly', s => s.get(seq));
const dbCancella = seqs => tx('readwrite', s => seqs.forEach(q => s.delete(q)));
const dbTrascrizioni = () => tx('readonly', s => s.getAll(), 'trascrizioni');
const dbMettiTr = rec => tx('readwrite', s => s.put(rec), 'trascrizioni');
const dbCancellaTr = das => tx('readwrite', s => das.forEach(d => s.delete(d)), 'trascrizioni');
function dbMeta() {
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

function suRisposta(t) {
  log(t);
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
  aggiornaLista().then(trascriviNuove);
}

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
    .then(() => { settoriOk++; invia('ACK ' + sett); })
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
const PEZZO_MAX = 600;
const telefono = /Android|Mobi/i.test(navigator.userAgent);
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
  return v === 'auto' ? (telefono ? 'base' : 'small') : v;
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
  trInCorso = { t0: Date.now(), durata: base.durata };
  const r = await chiedi({ tipo: 'trascrivi', audio, lingua }, [audio.buffer]);
  const segmenti = r.segmenti.filter(x => !allucinazione(x.testo));
  await dbMettiTr({ ...base, testo: segmenti.map(x => x.testo).join(' '), segmenti, modello: r.modello, motore: r.motore, secondi: r.secondi });
  log(`trascritti ${durata(base.durata)} di audio in ${r.secondi.toFixed(1)} s (whisper-${r.modello}, ${r.motore})`);
}

const pezziDi = s => { const q = new Set(s.seqs); return pezzi.filter(p => q.has(p.da)).sort((a, b) => a.da - b.da); };
// segmenti con l'ora: assoluta se la registrazione ha l'ora vera, altrimenti relativa all'inizio
function righeDi(s) {
  const out = [];
  for (const p of pezziDi(s)) {
    const off = (p.ms - s.msInizio) / 1000;
    for (const x of p.segmenti) {
      const t = off + (x.t0 || 0);
      const ora = s.inizio ? new Date(s.inizio + t * 1000).toLocaleTimeString('it-IT')
        : `+${String(Math.floor(t / 60)).padStart(2, '0')}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
      out.push({ ora, testo: x.testo });
    }
  }
  return out;
}
const testoDi = (s, conOra) => righeDi(s).map(r => conOra ? `[${r.ora}] ${r.testo}` : r.testo).join('\n');

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
      ${righe.length ? `<div class="testo">${righe.map(r => `<p><time>${r.ora}</time> ${esc(r.testo)}</p>`).join('')}</div>` : ''}
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

$('bCollega').onclick = () => collega(!dev);
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
await dbApri();
aggiornaLista().then(() => trascriviNuove());
aggiornaPulsanti();
ricollegaNoto();
