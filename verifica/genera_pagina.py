"""Genera verifica/index.html (pagina autonoma, dati incorporati) da verifica/risultati.json.

Uso: python verifica/genera_pagina.py
La pagina disegna tutto in JavaScript dai dati incorporati: banco di prova (una casella per test),
diario degli esiti, azioni aperte, elenco filtrabile, pianta della scheda, impilamento e fonti.
"""
import json
import pathlib

QUI = pathlib.Path(__file__).parent
f = QUI / "risultati.json"
R = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {
    "concluso": False, "stato_lavoro": "Il revisore sta preparando il piano dei test", "test": []}
dati = json.dumps(R, ensure_ascii=False).replace("</", "<\\/")

PAGINA = r"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>notªpad – verifica scheda</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* VOICE  clinico, da banco di collaudo: ogni test è una misura
   IDEA   il banco di prova di un laboratorio: una piastra con una casella per ogni test che si accende quando passa
   PICTURE la piastra dei test, divisa per area, con il test in corso che pulsa
   COLOUR alluminio e nero, arancio segnale per ciò che è in corso; verde/ambra/rosso solo per gli esiti
   TYPE   Geist e Geist Mono; LAYOUT: fascia scura con il quadrante, poi piastra, diario e azioni, elenco */
:root{color-scheme:light dark;
--bg:light-dark(#e9eaec,#141517);--panel:light-dark(#ffffff,#1c1e21);--ink:light-dark(#121315,#e9eaec);--mut:light-dark(#5d636b,#9aa0a8);
--line:light-dark(#d3d6da,#2c2f34);--band:#0e0f11;--bandink:#e9eaec;--sig:#ff4f00;
--PASS:#1f9d55;--WARN:#e3a008;--FAIL:#e5322d;--NON_VERIFICABILE:#8a8f98}
:root[data-theme=light]{color-scheme:light}:root[data-theme=dark]{color-scheme:dark}
*{box-sizing:border-box;min-width:0}html{-webkit-text-size-adjust:100%;scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Geist,system-ui,-apple-system,Segoe UI,sans-serif;overflow-x:clip}
.mono{font-family:"Geist Mono",ui-monospace,Consolas,monospace}
.in{max-width:1240px;margin:0 auto;padding:0 max(4vw,16px)}
header{background:var(--band);color:var(--bandink);padding:28px 0 30px}
.top{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px;align-items:end}
h1{font-size:clamp(28px,4.4vw,46px);line-height:1.05;margin:6px 0 10px;font-weight:600;text-wrap:balance}
.meta{color:#9aa0a8;font-size:14px}
.live{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:#c9cdd2}
.dot{width:10px;height:10px;border-radius:50%;background:var(--sig);flex:none}
.on .dot{animation:pu 1.2s ease-in-out infinite}.off .dot{background:#5d636b}
@keyframes pu{0%,100%{box-shadow:0 0 0 0 rgba(255,79,0,.6)}50%{box-shadow:0 0 0 7px rgba(255,79,0,0)}}
.dial{display:flex;gap:18px;align-items:flex-end;justify-content:flex-end;flex-wrap:wrap}
.big{font-size:clamp(52px,8vw,88px);line-height:.9;font-weight:600;font-variant-numeric:tabular-nums}
.big small{font-size:.38em;color:#9aa0a8;font-weight:500}
.scale{margin-top:22px;height:14px;border-radius:7px;background:#26292d;display:flex;overflow:hidden}
.now{margin-top:12px;font-size:17px;color:#fff;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.now b{color:var(--sig);font-weight:600}
.verd{display:inline-block;margin-top:10px;padding:6px 12px;border-radius:8px;font-weight:600;font-size:15px}
main{padding:26px 0 60px}
h2{font-size:20px;margin:36px 0 12px;font-weight:600}
.sub{color:var(--mut);font-size:14px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}
.plate{display:grid;gap:10px}
.row{display:grid;grid-template-columns:200px minmax(0,1fr) 70px;gap:12px;align-items:center}
.row .lab{font-size:14px}.row .lab b{font-family:"Geist Mono",monospace;margin-right:6px}
.row .pc{font-size:13px;color:var(--mut);text-align:right;font-variant-numeric:tabular-nums}
.cells{display:flex;flex-wrap:wrap;gap:6px}
.cell{all:unset;cursor:pointer;width:46px;height:30px;border-radius:6px;border:1.5px solid var(--line);font:500 11px "Geist Mono",monospace;
 display:grid;place-items:center;color:var(--mut);transition:background .5s,border-color .5s,transform .2s}
.cell:hover,.cell:focus-visible{transform:translateY(-2px);outline:2px solid var(--ink);outline-offset:1px}
.cell.PASS{background:var(--PASS);border-color:var(--PASS);color:#fff}.cell.WARN{background:var(--WARN);border-color:var(--WARN);color:#111}
.cell.FAIL{background:var(--FAIL);border-color:var(--FAIL);color:#fff}.cell.NON_VERIFICABILE{background:var(--NON_VERIFICABILE);border-color:var(--NON_VERIFICABILE);color:#fff}
.cell.IN_CORSO{border-color:var(--sig);color:var(--sig);animation:run 1s ease-in-out infinite}
.cell.fresh{animation:pop .9s ease-out}
@keyframes run{50%{background:rgba(255,79,0,.18)}}
@keyframes pop{0%{transform:scale(1.35);box-shadow:0 0 0 6px rgba(255,79,0,.35)}100%{transform:none;box-shadow:none}}
.leg{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px;font-size:13px;color:var(--mut)}
.leg i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px;border:1.5px solid var(--line)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-top:14px}
.kpi{all:unset;cursor:pointer;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px;min-height:44px}
.kpi b{display:block;font-size:30px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.1}
.kpi span{font-size:13px;color:var(--mut)}.kpi i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.kpi.sel{outline:2px solid var(--ink)}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
.feed{list-style:none;margin:0;padding:0;max-height:440px;overflow:auto}
.feed li{display:grid;grid-template-columns:70px 44px minmax(0,1fr);gap:10px;padding:9px 4px;border-bottom:1px solid var(--line);align-items:baseline;cursor:pointer}
.feed li:last-child{border:0}.feed .t{font-size:13px;color:var(--mut);font-variant-numeric:tabular-nums}
.feed .chg{font-size:12px;color:var(--mut)}
.pill{font:600 11px "Geist Mono",monospace;padding:2px 7px;border-radius:999px;color:#fff;white-space:nowrap}
.pill.WARN{color:#111}.pill.IN_ATTESA{color:var(--mut);border:1px solid var(--line);background:transparent!important}
.act{border-left:4px solid;padding:8px 12px;margin:0 0 10px;background:var(--bg);border-radius:0 8px 8px 0;cursor:pointer}
.act b{font-family:"Geist Mono",monospace;margin-right:6px}.act p{margin:4px 0 0;font-size:14px}
.empty{color:var(--mut);font-size:14px;padding:8px 0}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;position:sticky;top:0;z-index:3;background:var(--bg);padding:8px 0}
.tools input{flex:1 1 240px;font:16px Geist,sans-serif;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--ink);min-height:44px}
.tools button{font:500 14px Geist,sans-serif;padding:0 14px;min-height:44px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--ink);cursor:pointer}
details.t{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:6px 0;scroll-margin-top:80px}
details.t.flash{animation:fl 1.6s ease-out}@keyframes fl{0%{box-shadow:0 0 0 3px var(--sig)}100%{box-shadow:none}}
details.t summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:52px 128px minmax(0,1fr) 64px;gap:10px;align-items:center;padding:11px 14px;min-height:44px}
details.t summary::-webkit-details-marker{display:none}details.t[open] summary{border-bottom:1px solid var(--line)}
details.t[data-e=IN_ATTESA]{opacity:.6}
.gr{font-size:12px;color:var(--mut);text-align:right}.gr.alta{color:var(--FAIL);font-weight:600}
.kv{display:grid;grid-template-columns:96px minmax(0,1fr);gap:6px 14px;padding:12px 14px 14px;font-size:15px;margin:0}
.kv dt{color:var(--mut);font-size:13px}.kv dd{margin:0;white-space:pre-line;overflow-wrap:anywhere}.kv dd.a{font-weight:600}
.src{display:inline-block;font:12px "Geist Mono",monospace;padding:2px 8px;margin:0 4px 4px 0;border:1px solid var(--line);border-radius:6px;color:inherit;text-decoration:none}
.mech{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:18px;align-items:start}
.fig svg{width:100%;height:auto;display:block;color:var(--ink)}
.o{cursor:pointer}.o.sel rect{stroke-width:3;fill-opacity:.5}
#info{margin-top:10px;font-size:14px;min-height:44px}
.chk{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:14px}.chk label{display:inline-flex;gap:6px;align-items:center;min-height:32px}
.chk i{width:12px;height:12px;border-radius:3px;display:inline-block}
.stack-row{display:grid;grid-template-columns:minmax(0,1fr) 110px;gap:10px;align-items:center;font-size:14px;margin:3px 0}
.stack-bar{height:26px;border-radius:5px;display:flex;align-items:center;padding:0 8px;color:#111;font-size:13px;white-space:nowrap;overflow:visible}
.stack-row .mm{text-align:right;color:var(--mut);font-variant-numeric:tabular-nums}
ul.f{padding-left:18px;font-size:14px}ul.f li{margin:6px 0;overflow-wrap:anywhere}
footer{color:var(--mut);font-size:13px;margin-top:40px}
@media(max-width:860px){.top,.two,.mech{grid-template-columns:minmax(0,1fr)}.dial{justify-content:flex-start}
 .row{grid-template-columns:minmax(0,1fr) 56px}.row .cells{grid-column:1/-1;grid-row:2}}
@media(max-width:600px){header{padding:20px 0 22px}.cell{width:40px;height:30px}
 details.t summary{grid-template-columns:auto minmax(0,1fr);gap:6px 10px}details.t summary .ti{grid-column:1/-1;font-weight:500}.gr{display:none}
 .kv{grid-template-columns:minmax(0,1fr);gap:2px}.kv dt{margin-top:8px;font-size:12px}
 .feed li{grid-template-columns:62px auto minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>
<header><div class="in">
 <div class="top">
  <div><div class="meta mono">notªpad v0.1 · 4 strati 1,0 mm · 16,5 × 38 mm · JLCPCB</div>
   <h1 id="titolo">Verifica pre-ordine della scheda</h1>
   <div id="live" class="live"><span class="dot"></span><span id="livetxt"></span></div></div>
  <div class="dial"><div><div class="big" id="cnt"></div><div class="meta" id="perc"></div></div></div>
 </div>
 <div class="scale" id="scale"></div>
 <div class="now" id="now"></div>
 <div id="verd"></div>
</div></header>
<main class="in">
 <div class="kpis" id="kpis"></div>
 <h2>Banco di prova</h2>
 <div class="panel"><div class="plate" id="plate"></div><div class="leg" id="leg"></div></div>
 <div class="two">
  <div><h2>Diario degli esiti</h2><div class="panel"><ul class="feed" id="feed"></ul></div></div>
  <div><h2>Da sistemare prima dell'ordine</h2><div class="panel" id="acts"></div></div>
 </div>
 <h2 id="sint-h">Sintesi</h2><div class="panel" id="sint" style="white-space:pre-line"></div>
 <h2>Tutti i test</h2>
 <div class="tools"><input id="q" placeholder="Cerca: U1, VBAT, LED, Gerber…" aria-label="Cerca"><button id="apri">Apri tutti</button><button id="chiudi">Chiudi</button><button id="reset">Togli filtri</button></div>
 <div id="lista"></div>
 <h2>Pianta della scheda</h2>
 <div class="mech"><div class="panel fig" id="pianta"></div>
  <div><div class="chk" id="chk"></div><p class="sub">Millimetri dall'angolo in alto a sinistra, anello in alto. Il tratteggio indica lo strato sotto la scheda o un keepout. Tocca un rettangolo per nome e misure.</p><div class="panel mono" id="info">Nessun elemento selezionato</div></div></div>
 <h2>Impilamento nello spessore</h2><div class="panel" id="stack"></div>
 <h2>Fonti</h2><ul class="f" id="fonti"></ul>
 <footer>Pagina generata da verifica/genera_pagina.py partendo da verifica/risultati.json. Gli script dei test sono in verifica/script/.</footer>
</main>
<script id="dati" type="application/json">__DATI__</script>
<script>
{
const R=JSON.parse(document.getElementById('dati').textContent);
const T=R.test||[];
const CAT={A:'Regole e integrità',B:'Pinout vs datasheet',C:'Simbolo ↔ impronta',D:'Analisi del circuito',E:'BOM e CPL JLC',F:'Meccanica e ingombri',G:'Fabbricazione',H:'Coerenza documenti'};
const ES=['FAIL','WARN','NON_VERIFICABILE','PASS','IN_CORSO','IN_ATTESA'];
const LAB={FAIL:'Errore',WARN:'Attenzione',NON_VERIFICABILE:'Non verificabile',PASS:'Superato',IN_CORSO:'In corso',IN_ATTESA:'In attesa'};
const COL={FAIL:'var(--FAIL)',WARN:'var(--WARN)',NON_VERIFICABILE:'var(--NON_VERIFICABILE)',PASS:'var(--PASS)',IN_CORSO:'var(--sig)',IN_ATTESA:'#3a3e44'};
const x=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $=id=>document.getElementById(id);
const n={};ES.forEach(k=>n[k]=T.filter(t=>t.esito===k).length);
const fatti=T.length-n.IN_CORSO-n.IN_ATTESA, conc=!!R.concluso&&!n.IN_CORSO&&!n.IN_ATTESA;
const cur=T.find(t=>t.esito==='IN_CORSO');
$('cnt').innerHTML=`${fatti}<small> / ${T.length}</small>`;
$('perc').textContent=T.length?`${Math.round(100*fatti/T.length)}% dei test conclusi`+(T.some(t=>t.giro==2)?' · secondo giro':''):'in preparazione';
$('scale').innerHTML=ES.filter(k=>n[k]).map(k=>`<span style="flex:${n[k]};background:${COL[k]}"></span>`).join('');
$('live').className='live '+(conc?'off':'on');
const agg=R.aggiornato?new Date(R.aggiornato):null;
function rel(){if(!agg||isNaN(agg)){$('livetxt').textContent=conc?'Verifica conclusa':'In attesa del primo esito';return}
 const s=Math.max(0,Math.round((Date.now()-agg)/1000));const r=s<60?`${s} s fa`:s<3600?`${Math.floor(s/60)} min fa`:`${Math.floor(s/3600)} h fa`;
 $('livetxt').textContent=(conc?'Verifica conclusa · ':'In diretta · ')+'ultimo aggiornamento '+r+' ('+agg.toLocaleTimeString('it-IT',{hour:'2-digit',minute:'2-digit'})+')'}
rel();setInterval(rel,1000);
$('now').innerHTML=conc?'':cur?`<span>Ora sul banco</span><b class="mono">${x(cur.id)}</b><span>${x(R.stato_lavoro||cur.titolo)}</span>`:`<span>${x(R.stato_lavoro||'')}</span>`;
let vt,vc;
if(!conc){vt=n.FAIL?`In corso · ${n.FAIL} ${n.FAIL==1?'errore':'errori'} finora`:'In corso · nessun errore finora';vc=n.FAIL?'var(--FAIL)':'var(--sig)'}
else if(n.FAIL){vt='Non ordinare ancora';vc='var(--FAIL)'}else if(n.WARN||n.NON_VERIFICABILE){vt='Ordinabile con riserve';vc='var(--WARN)'}else{vt='Ordinabile';vc='var(--PASS)'}
$('verd').innerHTML=`<span class="verd" style="background:${vc};color:${vc==='var(--WARN)'?'#111':'#fff'}">${x(vt)}</span>`;
$('titolo').textContent=conc?(n.FAIL?`${n.FAIL} ${n.FAIL==1?'errore blocca':'errori bloccano'} l'ordine della scheda`:'La scheda supera la verifica pre-ordine'):'Verifica pre-ordine della scheda, in diretta';
const st={e:null,q:''};
$('kpis').innerHTML=ES.filter(k=>(k!=='IN_ATTESA'&&k!=='IN_CORSO')||n[k]).map(k=>`<button class="kpi" data-e="${k}"><b>${n[k]}</b><span><i style="background:${COL[k]}"></i>${LAB[k]}</span></button>`).join('');
const cats=[...new Set(T.map(t=>t.categoria))].sort();
$('plate').innerHTML=cats.map(c=>{const tt=T.filter(t=>t.categoria===c),d=tt.filter(t=>!['IN_ATTESA','IN_CORSO'].includes(t.esito)).length;
 return `<div class="row"><div class="lab"><b>${x(c)}</b>${x(CAT[c]||'')}</div><div class="cells">${tt.map(t=>`<button class="cell ${t.esito}" data-id="${x(t.id)}" title="${x(t.id+' · '+t.titolo+' · '+LAB[t.esito])}">${x(t.id)}</button>`).join('')}</div><div class="pc">${d}/${tt.length}</div></div>`}).join('')||'<div class="empty">Il piano dei test non è ancora arrivato.</div>';
$('leg').innerHTML=ES.map(k=>`<span><i style="background:${k==='IN_ATTESA'?'transparent':COL[k]};${k==='IN_ATTESA'?'':'border-color:'+COL[k]}"></i>${LAB[k]}</span>`).join('');
try{const prev=JSON.parse(localStorage.getItem('np-esiti')||'{}');document.querySelectorAll('.cell').forEach(b=>{const t=T.find(t=>t.id===b.dataset.id);if(prev[t.id]&&prev[t.id]!==t.esito&&t.esito!=='IN_CORSO')b.classList.add('fresh')});
 localStorage.setItem('np-esiti',JSON.stringify(Object.fromEntries(T.map(t=>[t.id,t.esito]))))}catch(e){}
const done=T.filter(t=>!['IN_ATTESA','IN_CORSO'].includes(t.esito));
const feed=[...done].sort((a,b)=>String(b.ora||'').localeCompare(String(a.ora||''))||String(b.id).localeCompare(String(a.id)));
$('feed').innerHTML=(cur?`<li data-id="${x(cur.id)}"><span class="t">adesso</span><span class="pill" style="background:var(--sig)">${x(cur.id)}</span><span class="ti">${x(cur.titolo)}</span></li>`:'')+
 feed.map(t=>`<li data-id="${x(t.id)}"><span class="t">${x(t.ora||'—')}</span><span class="pill ${t.esito}" style="background:${COL[t.esito]}">${x(t.id)}</span><span class="ti">${x(t.titolo)}${t.esito_prec&&t.esito_prec!==t.esito?` <span class="chg">· era ${x(LAB[t.esito_prec]||t.esito_prec)}, ora ${x(LAB[t.esito])}</span>`:''}</span></li>`).join('')||(cur?'':'<li class="empty">Nessun esito ancora.</li>');
const ac=T.filter(t=>t.esito==='FAIL'||(t.esito==='WARN'&&t.gravita==='alta')).sort((a,b)=>ES.indexOf(a.esito)-ES.indexOf(b.esito));
$('acts').innerHTML=ac.map(t=>`<div class="act" data-id="${x(t.id)}" style="border-color:${COL[t.esito]}"><b>${x(t.id)}</b>${x(t.titolo)}<p>${x(t.azione||t.trovato)}</p></div>`).join('')||`<div class="empty">${conc?'Nessun errore e nessuna attenzione grave.':'Nessun errore finora.'}</div>`;
if(R.sintesi)$('sint').textContent=R.sintesi;else{$('sint').remove();$('sint-h').remove()}
const F={};(R.fonti||[]).forEach(f=>F[f.id]=f);
const src=id=>{const f=F[id];if(!f)return`<span class="src">${x(id)}</span>`;const u=String(f.url_o_percorso||'');
 return u.startsWith('http')?`<a class="src" href="${x(u)}" target="_blank" rel="noopener" title="${x(f.descrizione)}">${x(id)}</a>`:`<span class="src" title="${x(f.descrizione+' — '+u)}">${x(id)}</span>`};
const ord=k=>k==='IN_CORSO'?-1:ES.indexOf(k);
$('lista').innerHTML=[...T].sort((a,b)=>ord(a.esito)-ord(b.esito)||String(a.id).localeCompare(String(b.id))).map(t=>`
<details class="t" id="t-${x(t.id)}" data-e="${t.esito}"><summary><span class="mono">${x(t.id)}</span><span class="pill ${t.esito}" style="background:${COL[t.esito]};justify-self:start">${LAB[t.esito]}</span><span class="ti">${x(t.titolo)}</span><span class="gr ${x(t.gravita)}">${x(t.gravita||'')}</span></summary>
<dl class="kv"><dt>Metodo</dt><dd>${x(t.metodo)}</dd><dt>Atteso</dt><dd>${x(t.atteso)}</dd><dt>Trovato</dt><dd>${x(t.trovato)}</dd>
${t.azione?`<dt>Azione</dt><dd class="a">${x(t.azione)}</dd>`:''}${t.esito_prec?`<dt>Primo giro</dt><dd>${x(LAB[t.esito_prec]||t.esito_prec)}</dd>`:''}${t.ora?`<dt>Esito alle</dt><dd class="mono">${x(t.ora)}</dd>`:''}
<dt>Fonti</dt><dd>${(t.fonti||[]).map(src).join(' ')}</dd>${t.script?`<dt>Script</dt><dd class="mono">${x(t.script)}</dd>`:''}</dl></details>`).join('');
function apply(){document.querySelectorAll('details.t').forEach(d=>{d.style.display=(!st.e||d.dataset.e===st.e)&&(!st.q||d.textContent.toLowerCase().includes(st.q))?'':'none'});
 document.querySelectorAll('.kpi').forEach(b=>b.classList.toggle('sel',b.dataset.e===st.e))}
function go(id){st.e=null;st.q='';$('q').value='';apply();const d=$('t-'+id);if(!d)return;d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});d.classList.remove('flash');void d.offsetWidth;d.classList.add('flash')}
document.querySelectorAll('.kpi').forEach(b=>b.onclick=()=>{st.e=st.e===b.dataset.e?null:b.dataset.e;apply();$('lista').scrollIntoView({behavior:'smooth'})});
document.querySelectorAll('.cell,.feed li[data-id],.act').forEach(b=>b.onclick=()=>go(b.dataset.id));
$('q').oninput=e=>{st.q=e.target.value.toLowerCase();apply()};
$('apri').onclick=()=>document.querySelectorAll('details.t').forEach(d=>d.open=true);
$('chiudi').onclick=()=>document.querySelectorAll('details.t').forEach(d=>d.open=false);
$('reset').onclick=()=>{st.e=null;st.q='';$('q').value='';apply()};
const P=R.pianta||{},[W,H]=(P.scheda||[16.5,38]),S=14,M=26;
const TC={top:'#3b82f6',bottom:'#e3a008',keepout:'#e5322d',foro:'#8a8f98',fessura:'#1f9d55',porta:'#a855f7'};
let g='';for(let i=0;i<=H;i+=5)g+=`<line x1="${M-6}" x2="${M}" y1="${M+i*S}" y2="${M+i*S}" stroke="currentColor" opacity=".4"/><text x="${M-9}" y="${M+i*S+3}" text-anchor="end" font-size="10" fill="currentColor" opacity=".6">${i}</text>`;
(P.oggetti||[]).forEach(o=>{const c=TC[o.tipo]||'#64748b',d=['bottom','keepout'].includes(o.tipo);
 g+=`<g class="o" data-t="${x(o.tipo)}" data-i="${x(o.nome+' · '+o.tipo+' · x '+o.x+', y '+o.y+' · '+o.w+' × '+o.h+' mm')}"><rect x="${M+o.x*S}" y="${M+o.y*S}" width="${Math.max(o.w*S,2)}" height="${Math.max(o.h*S,2)}" fill="${c}" fill-opacity="${d?.1:.25}" stroke="${c}" stroke-width="1.2" ${d?'stroke-dasharray="4 3"':''}/><title>${x(o.nome)}</title></g>`});
$('pianta').innerHTML=`<svg viewBox="0 0 ${W*S+2*M} ${H*S+2*M}"><rect x="${M}" y="${M}" width="${W*S}" height="${H*S}" rx="${S}" fill="none" stroke="currentColor" stroke-width="1.5"/>${g}</svg>`;
$('chk').innerHTML=Object.entries(TC).map(([k,c])=>`<label><input type="checkbox" checked data-t="${k}"><i style="background:${c}"></i>${k}</label>`).join('');
document.querySelectorAll('#chk input').forEach(c=>c.onchange=()=>document.querySelectorAll(`.o[data-t="${c.dataset.t}"]`).forEach(o=>o.style.display=c.checked?'':'none'));
document.querySelectorAll('.o').forEach(o=>o.onclick=()=>{document.querySelectorAll('.o.sel').forEach(s=>s.classList.remove('sel'));o.classList.add('sel');$('info').textContent=o.dataset.i});
const K=R.stack||{},sp=+K.spessore_mm||8,pal=['#cbd5e1','#93c5fd','#86efac','#fcd34d','#d8b4fe','#fca5a5','#5eead4','#e2e8f0'];
$('stack').innerHTML=`<div class="sub" style="margin-bottom:8px">Spessore di riferimento ${sp} mm, dalla faccia anteriore (in alto) al retro. Ogni barra è lunga quanto lo spessore dello strato.</div>`+
 [...(K.strati||[])].sort((a,b)=>b.a_mm-a.a_mm).map((s,i)=>{const w=Math.max(4,100*(s.a_mm-s.da_mm)/sp);
 return `<div class="stack-row"><div><div class="stack-bar" style="width:${w}%;margin-left:${Math.max(0,100*(sp-s.a_mm)/sp)}%;background:${pal[i%pal.length]}">${x(s.nome)}</div></div><div class="mm mono">${(+s.da_mm).toFixed(1)}–${(+s.a_mm).toFixed(1)} mm</div></div>`}).join('')||'<div class="empty">Non ancora disponibile.</div>';
$('fonti').innerHTML=(R.fonti||[]).map(f=>{const u=String(f.url_o_percorso||'');return `<li><span class="mono">${x(f.id)}</span> — ${x(f.descrizione)}<br><small class="mono">${u.startsWith('http')?`<a href="${x(u)}" target="_blank" rel="noopener">${x(u)}</a>`:x(u)}</small></li>`}).join('');
}
</script></body></html>"""

(QUI / "index.html").write_text(PAGINA.replace("__DATI__", dati), encoding="utf-8")
t = R.get("test", [])
print(f"verifica/index.html: {len(t)} test, concluso={R.get('concluso')}")
