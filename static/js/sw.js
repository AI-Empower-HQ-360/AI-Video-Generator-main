// Service Worker for caching and performance optimization
// Implements efficient caching strategies for the AI Video Generator

const CACHE_NAME = 'ai-video-generator-v1';
const STATIC_CACHE_NAME = 'static-v1';
const API_CACHE_NAME = 'api-v1';

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/css/style.css',
  '/static/js/main.js'
];

// API endpoints that can be cached
const CACHEABLE_API_PATTERNS = [
  /\/api\/slokas\/daily/,
  /\/api\/health/,
  /\/api\/test/
];

// Cache strategies based on content type
const CACHE_STRATEGIES = {
  static: { maxAge: 31536000, maxEntries: 100 }, // 1 year for static assets
  api: { maxAge: 300, maxEntries: 50 },          // 5 minutes for API responses
  dynamic: { maxAge: 60, maxEntries: 30 }        // 1 minute for dynamic content
};

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then(cache => {
        return cache.addAll(STATIC_ASSETS);
      }),
      caches.open(API_CACHE_NAME),
      caches.open(CACHE_NAME)
    ]).then(() => {
      console.log('Service Worker installed successfully');
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (![CACHE_NAME, STATIC_CACHE_NAME, API_CACHE_NAME].includes(cacheName)) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleAPIRequest(request));
  } else if (url.pathname.startsWith('/static/')) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleDynamicRequest(request));
  }
});

// Handle API requests with caching
async function handleAPIRequest(request) {
  const url = new URL(request.url);
  const cache = await caches.open(API_CACHE_NAME);
  
  // Check if this API endpoint should be cached
  const shouldCache = CACHEABLE_API_PATTERNS.some(pattern => pattern.test(url.pathname));
  
  if (shouldCache) {
    // Try cache first, then network
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      console.log('API cache hit:', url.pathname);
      
      // Update cache in background
      fetch(request).then(response => {
        if (response.ok) {
          cache.put(request, response.clone());
        }
      }).catch(() => {}); // Ignore background update errors
      
      return cachedResponse;
    }
  }
  
  // Network first for non-cached or cache miss
  try {
    const response = await fetch(request);
    
    if (response.ok && shouldCache) {
      console.log('Caching API response:', url.pathname);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    
    // Return cached version if available
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline message
    return new Response(JSON.stringify({
      error: 'Network unavailable',
      cached: false
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle static assets with aggressive caching
async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  // Cache first, then network
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('Static asset request failed:', error);
    throw error;
  }
}

// Handle dynamic content with short-term caching
async function handleDynamicRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      // Cache for short duration
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    // Try cache as fallback
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Performance monitoring
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_STATS') {
    getCacheStats().then(stats => {
      event.ports[0].postMessage(stats);
    });
  }
});

async function getCacheStats() {
  const cacheNames = await caches.keys();
  const stats = {};
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    stats[cacheName] = keys.length;
  }
  
  return stats;
}