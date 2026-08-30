// Bumped only when the caching strategy itself changes. The app's own files no
// longer need it: the shell is fetched from the network first, so an update
// reaches an installed copy on its next online launch.
const CACHE = "minesweeper-v3";

// How long to wait for the network before falling back to the cache. Short
// enough that a bad connection does not leave the player staring at nothing.
const NETWORK_TIMEOUT = 3000;

const ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./game.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-192.png",
  "./icons/maskable-512.png",
  "./icons/apple-touch-icon.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Rejects if the fetch has not answered in time. The fetch itself is left to
// finish in the background; aborting a navigation request is not portable.
function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("network timeout")), ms);
    promise.then(
      value => { clearTimeout(timer); resolve(value); },
      error => { clearTimeout(timer); reject(error); }
    );
  });
}

function store(request, response) {
  if (response && response.ok) {
    const copy = response.clone();
    caches.open(CACHE).then(cache => cache.put(request, copy));
  }
  return response;
}

// The markup, styles and script change whenever the game does, so ask the
// network first and keep the cache as the offline answer.
async function networkFirst(request) {
  try {
    return store(request, await withTimeout(fetch(request), NETWORK_TIMEOUT));
  } catch (error) {
    const hit = await caches.match(request);
    if (hit) return hit;
    if (request.mode === "navigate") {
      const shell = await caches.match("./index.html");
      if (shell) return shell;
    }
    return Response.error();
  }
}

// Icons are large and effectively fixed, so serve them straight from the cache.
async function cacheFirst(request) {
  const hit = await caches.match(request);
  if (hit) return hit;
  try {
    return store(request, await fetch(request));
  } catch (error) {
    return Response.error();
  }
}

const SHELL = /\.(?:html|css|js|json)$/;

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const isShell = request.mode === "navigate" ||
                  url.pathname.endsWith("/") ||
                  SHELL.test(url.pathname);

  event.respondWith(isShell ? networkFirst(request) : cacheFirst(request));
});
