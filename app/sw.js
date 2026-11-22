// notªpad – service worker:
// 1. tiene in cache l'interfaccia, così l'app si apre anche senza rete;
// 2. aggiunge COOP/COEP alle pagine dell'app (cross-origin isolation), che servono a WASM multithread per
//    Whisper; né il server di Python né GitHub Pages permettono di impostare queste intestazioni;
// 3. tiene in cache la libreria transformers.js e i file di ONNX Runtime (cdn.jsdelivr.net, versione fissa).
// I modelli Whisper (Hugging Face) non passano di qui: transformers.js li tiene nella sua cache.
const VERSIONE = 'np-0.2.0', LIB = 'np-lib-4.3.2';
const FILE = ['./', 'index.html', 'app.js', 'adpcm.js', 'trascrittore.js', 'manifest.webmanifest', 'icone/icona-192.png', 'icone/icona-512.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(VERSIONE).then(c => c.addAll(FILE)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(k => Promise.all(k.filter(x => x !== VERSIONE && x !== LIB).map(x => caches.delete(x)))).then(() => self.clients.claim())));

function isola(r) {
  if (r.type === 'opaque' || r.status === 0) return r;
  const h = new Headers(r.headers);
  h.set('Cross-Origin-Opener-Policy', 'same-origin');
  h.set('Cross-Origin-Embedder-Policy', 'credentialless');
  return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin === self.location.origin) {
    // prima la rete (così le modifiche si vedono subito), la cache solo se il server non risponde
    e.respondWith(fetch(e.request).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(VERSIONE).then(c => c.put(e.request, copia)); }
      return isola(r);
    }).catch(() => caches.match(e.request).then(r => r ? isola(r) : Response.error())));
  } else if (u.hostname === 'cdn.jsdelivr.net') {
    // versione fissa nell'URL: prima la cache
    e.respondWith(caches.open(LIB).then(async c => {
      const hit = await c.match(e.request);
      if (hit) return hit;
      const r = await fetch(e.request);
      if (r.ok) c.put(e.request, r.clone());
      return r;
    }));
  }
});
