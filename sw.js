const CACHE = 'masrofati-v35';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // app shell: cache first, refresh in background
  if (url.origin === location.origin) {
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(hit => {
      const net = fetch(req).then(r => { if (r.ok) caches.open(CACHE).then(c => c.put(req, r.clone())); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  // fonts and pdf.js from CDNs: cache as they are used
  if (/fonts\.(googleapis|gstatic)\.com|cdnjs\.cloudflare\.com/.test(url.host)) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok || r.type === 'opaque') caches.open(CACHE).then(c => c.put(req, r.clone())); return r; })));
  }
});
