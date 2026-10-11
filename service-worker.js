const CACHE = "saudi-clubs-v1";

const FILES = [
  "./",
  "./index.html",
  "./data.json",
  "./names.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(FILES))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        const copy = response.clone();
        caches.open(CACHE).then(cache => {
          cache.put(event.request, copy);
        });
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
