// notªpad – comandi vocali: «Comando, accendi la luce [della cucina]» → Home Assistant.
// Riconoscimento senza AI (espressione regolare sul testo di Whisper), quindi gratis e senza internet.

// stanze: testo "cucina=light.cucina" una per riga; la prima riga è la luce predefinita
export function leggiStanze(testo) {
  return (testo || '').split('\n').map(r => r.split('=').map(x => x.trim())).filter(([n, e]) => n && e && /^\w+\.\w+$/.test(e));
}
const norm = t => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

// trova i comandi in un testo: [{ azione: 'turn_on' | 'turn_off', entita, frase }]
// Tollerante agli errori di Whisper: «spenni», «spengi», «accedi», «luci», «bagnio»… Si cerca «comando»,
// poi entro 2 parole il verbo (acc… = accendi, sp… = spegni), poi entro 5 parole il dispositivo:
// un nome della lista (anche con una lettera sbagliata) o «luce» + stanza, o «luce» da sola (riga «luce»).
const VUOTE = new Set(['la', 'le', 'il', 'i', 'lo', 'l', 'del', 'della', 'dello', 'dei', 'delle', 'di', 'in', 'nel', 'nella', 'e', 'anche', 'per', 'favore']);
function distanza(a, b) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}
const simile = (w, nome) => w === nome || (nome.length >= 4 && (distanza(w, nome) <= (nome.length >= 7 ? 2 : 1) || (w.length >= 4 && nome.startsWith(w))));
const verbo = w => /^ac+[ec]/.test(w) || /^ac+en/.test(w) ? 'turn_on' : /^sp[ei]/.test(w) ? 'turn_off' : null;
export function trovaComandi(testo, stanze) {
  const out = [];
  const nomi = stanze.map(([n, e]) => [norm(n), e]);
  const parole = norm(testo).split(/[^a-z]+/).filter(Boolean);
  for (let i = 0; i < parole.length; i++) {
    if (!/^com+an/.test(parole[i])) continue;                     // «comando», «commando», «comandi»…
    let j = i + 1, az = null;
    for (; j < parole.length && j <= i + 2; j++) if ((az = verbo(parole[j]))) break;
    if (!az) continue;
    let entita = null, luce = false, ignota = false, prep = false, k = j + 1;
    for (; k < parole.length && k <= j + 5; k++) {
      const w = parole[k];
      if (VUOTE.has(w)) { if (luce && /^(del|dell|della|dello|dei|delle|di|in|nel|nella)$/.test(w)) prep = true; continue; }
      if (/^com+an/.test(w)) break;                                 // inizia un altro comando
      const n = nomi.find(([x]) => !x.startsWith('luc') && simile(w, x));
      if (n) { entita = n[1]; break; }
      if (/^lu[cs]/.test(w)) { luce = true; continue; }
      if (luce) { ignota = prep; break; }                          // «luce della <stanza sconosciuta>»: niente
    }
    if (!entita && luce && !ignota) { const l = nomi.find(([x]) => x.startsWith('luc')) || nomi[0]; entita = l && l[1]; }
    if (entita) out.push({ azione: az, entita, frase: parole.slice(i, Math.min(k + 1, parole.length)).join(' ') });
  }
  return out;
}

// chiamata al servizio di Home Assistant (REST API, token "a lunga durata")
export async function chiamaHA({ url, token }, { azione, entita }) {
  const dominio = entita.split('.')[0];
  const r = await fetch(`${url.replace(/\/$/, '')}/api/services/${dominio}/${azione}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ entity_id: entita }),
  });
  if (!r.ok) throw new Error(`Home Assistant ha risposto ${r.status}`);
}
export async function provaHA({ url, token }) {
  const r = await fetch(`${url.replace(/\/$/, '')}/api/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`risposta ${r.status}`);
  return (await r.json()).message;
}
export async function statoHA({ url, token }, entita) {
  const r = await fetch(`${url.replace(/\/$/, '')}/api/states/${entita}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`risposta ${r.status}`);
  return (await r.json()).state;
}
