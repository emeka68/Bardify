const CACHE_NAME = 'shakespeare-translator-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
  '/static/css/main.css',
  '/static/js/main.js',
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('📦 Caching app shell');
      // Don't fail if some files aren't available yet
      return cache.addAll(urlsToCache).catch(() => {
        console.log('⚠️  Some files not cached during install');
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️  Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip API calls (let them go directly to network)
  if (request.url.includes('/api/') || request.url.includes('/transform')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful API responses
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return offline message for failed API calls
          return new Response(
            JSON.stringify({
              error: 'Offline - API temporarily unavailable',
              offline: true,
            }),
            {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'application/json',
              }),
            }
          );
        })
    );
    return;
  }

  // For everything else, use cache-first strategy
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        // Return from cache
        return response;
      }

      // Not in cache, fetch from network
      return fetch(request)
        .then((response) => {
          // Don't cache if not successful
          if (!response || response.status !== 200) {
            return response;
          }

          // Clone and cache the response
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });

          return response;
        })
        .catch(() => {
          // Offline fallback
          return new Response('Offline - Page not available', {
            status: 503,
            statusText: 'Service Unavailable',
          });
        });
    })
  );
});

// Handle messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('✅ Service Worker loaded');
