// notªpad – service worker: tiene in cache l'interfaccia, così l'app si apre anche senza server avviato da poco
const VERSIONE = 'np-0.1.0';
const FILE = ['./', 'index.html', 'app.js', 'adpcm.js', 'manifest.webmanifest', 'icone/icona-192.png', 'icone/icona-512.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(VERSIONE).then(c => c.addAll(FILE)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(k => Promise.all(k.filter(x => x !== VERSIONE).map(x => caches.delete(x)))).then(() => self.clients.claim())));
// prima la rete (così le modifiche si vedono subito), la cache solo se il server non risponde
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(r => {
    const copia = r.clone();
    caches.open(VERSIONE).then(c => c.put(e.request, copia));
    return r;
  }).catch(() => caches.match(e.request)));
});
