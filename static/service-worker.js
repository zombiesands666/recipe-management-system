const CACHE_NAME = 'recipe-app-v2';
const STATIC_CACHE = 'static-cache-v2';
const DYNAMIC_CACHE = 'dynamic-cache-v2';
const RECIPE_CACHE = 'recipe-cache-v2';

const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/icon-192x192.png',
    '/static/icon-512x512.png'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, RECIPE_CACHE];
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return cacheNames.filter(
                    cacheName => !currentCaches.includes(cacheName)
                );
            })
            .then(cachesToDelete => {
                return Promise.all(
                    cachesToDelete.map(cacheToDelete => {
                        return caches.delete(cacheToDelete);
                    })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Background sync for offline recipe additions
self.addEventListener('sync', event => {
    if (event.tag === 'sync-new-recipe') {
        event.waitUntil(syncRecipes());
    }
});

// Helper function to determine response strategy based on request
function getResponseStrategy(request) {
    const url = new URL(request.url);
    
    // Static assets - Cache First
    if (STATIC_ASSETS.includes(url.pathname)) {
        return 'cache-first';
    }
    
    // API requests - Network First
    if (url.pathname.includes('/api/')) {
        return 'network-first';
    }
    
    // Recipe data - Cache with network update
    if (url.pathname.includes('/recipes')) {
        return 'stale-while-revalidate';
    }
    
    // Default to network first
    return 'network-first';
}

// Fetch event with different strategies
self.addEventListener('fetch', event => {
    const strategy = getResponseStrategy(event.request);
    
    switch (strategy) {
        case 'cache-first':
            event.respondWith(
                caches.match(event.request)
                    .then(response => response || fetchAndCache(event.request, STATIC_CACHE))
            );
            break;
            
        case 'network-first':
            event.respondWith(
                fetch(event.request)
                    .then(response => {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => cache.put(event.request, responseClone));
                        return response;
                    })
                    .catch(() => caches.match(event.request))
            );
            break;
            
        case 'stale-while-revalidate':
            event.respondWith(
                caches.match(event.request)
                    .then(cached => {
                        const fetchedResource = fetch(event.request)
                            .then(response => {
                                const responseClone = response.clone();
                                caches.open(RECIPE_CACHE)
                                    .then(cache => cache.put(event.request, responseClone));
                                return response;
                            });
                        return cached || fetchedResource;
                    })
            );
            break;
    }
});

// Helper function to fetch and cache
async function fetchAndCache(request, cacheName) {
    const response = await fetch(request);
    const cache = await caches.open(cacheName);
    cache.put(request, response.clone());
    return response;
}

// Helper function to sync recipes
async function syncRecipes() {
    const recipesToSync = await getRecipesToSync();
    return Promise.all(
        recipesToSync.map(recipe => {
            return fetch('/api/recipes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(recipe)
            });
        })
    );
}

// Helper function to get recipes to sync (would be implemented with IndexedDB)
async function getRecipesToSync() {
    // This would normally fetch from IndexedDB
    return [];
}

// Send message to clients when offline/online status changes
self.addEventListener('message', event => {
    if (event.data === 'CHECK_ONLINE_STATUS') {
        const online = self.navigator ? navigator.onLine : false;
        event.ports[0].postMessage({
            online: online,
            timestamp: new Date().getTime()
        });
    }
});
