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
let db;
function dbApri() {
  return new Promise((ok, ko) => {
    const r = indexedDB.open('notapad', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('settori', { keyPath: 'seq' });
    r.onsuccess = () => ok(db = r.result);
    r.onerror = () => ko(r.error);
  });
}
const tx = (modo, f) => new Promise((ok, ko) => {
  const t = db.transaction('settori', modo);
  const ris = f(t.objectStore('settori'));
  t.oncomplete = () => ok(ris && ris.result);
  t.onerror = () => ko(t.error);
});
const dbMetti = rec => tx('readwrite', s => s.put(rec));
const dbPrendi = seq => tx('readonly', s => s.get(seq));
const dbCancella = seqs => tx('readwrite', s => seqs.forEach(q => s.delete(q)));
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
  aggiornaLista();
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
let urlAudio = [];
async function aggiornaLista() {
  const meta = await dbMeta();
  const g = sessioni(meta).reverse();
  urlAudio.forEach(u => URL.revokeObjectURL(u)); urlAudio = [];
  $('vuota').style.display = g.length ? 'none' : 'block';
  $('lista').innerHTML = g.map((s, i) => `<tr>
    <td>${s.inizio ? new Date(s.inizio).toLocaleString('it-IT') : `avvio ${s.avvio}, +${durata(s.msInizio / 1000)}`}</td>
    <td class="n">${durata(s.campioni / FREQ)}</td><td>${s.seqs.length}</td>
    <td><button data-a="ascolta" data-i="${i}">Ascolta</button> <span id="pl${i}"></span></td>
    <td><button data-a="wav" data-i="${i}">WAV</button> <button data-a="del" data-i="${i}">Elimina</button></td></tr>`).join('');
  $('lista').onclick = async e => {
    const b = e.target.closest('button'); if (!b) return;
    const s = g[+b.dataset.i];
    if (b.dataset.a === 'del') {
      if (!confirm('Eliminare questa registrazione dal PC?')) return;
      await dbCancella(s.seqs); aggiornaLista(); return;
    }
    const blob = await audioDi(s);
    const u = URL.createObjectURL(blob); urlAudio.push(u);
    if (b.dataset.a === 'ascolta') $('pl' + b.dataset.i).innerHTML = `<audio controls autoplay src="${u}"></audio>`;
    else {
      const d = s.inizio ? new Date(s.inizio) : new Date();
      const nome = `notapad_${d.toISOString().slice(0, 19).replace(/[-:T]/g, '')}.wav`;
      const a = document.createElement('a'); a.href = u; a.download = nome; a.click();
    }
  };
}
async function audioDi(s) {
  const parti = [];
  let n = 0;
  for (const q of s.seqs) {
    const r = await dbPrendi(q);
    const pcm = decodifica(new Uint8Array(r.dati), r.campioni, r.pred, r.indice);
    parti.push(pcm); n += pcm.length;
  }
  const tutto = new Int16Array(n);
  let o = 0; for (const p of parti) { tutto.set(p, o); o += p.length; }
  return wav(tutto);
}

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

if (!window.isSecureContext) avviso('Apri la pagina da http://localhost (avvia.cmd): Web Bluetooth funziona solo in un contesto sicuro.');
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
await dbApri();
aggiornaLista();
aggiornaPulsanti();
ricollegaNoto();
