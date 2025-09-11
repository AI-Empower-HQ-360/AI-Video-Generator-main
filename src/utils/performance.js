/**
 * Performance monitoring and optimization utilities
 * Implements client-side performance tracking and optimization
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            apiCallCount: 0,
            totalApiTime: 0,
            cacheHits: 0,
            cacheMisses: 0,
            memoryUsage: 0
        };
        
        this.init();
    }
    
    init() {
        // Monitor page load performance
        if (typeof window !== 'undefined') {
            window.addEventListener('load', () => {
                this.measurePageLoad();
            });
            
            // Register service worker for caching
            this.registerServiceWorker();
            
            // Set up performance observer
            this.setupPerformanceObserver();
            
            // Monitor memory usage periodically
            setInterval(() => this.checkMemoryUsage(), 30000); // Every 30 seconds
        }
    }
    
    measurePageLoad() {
        if (performance && performance.timing) {
            const timing = performance.timing;
            this.metrics.pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            
            console.log(`Page loaded in ${this.metrics.pageLoadTime}ms`);
            
            // Report if slow
            if (this.metrics.pageLoadTime > 3000) {
                console.warn('Slow page load detected:', this.metrics.pageLoadTime);
            }
        }
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/sw.js');
                console.log('Service Worker registered successfully');
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    console.log('Service Worker update found');
                });
            } catch (error) {
                console.warn('Service Worker registration failed:', error);
            }
        }
    }
    
    setupPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            // Observe navigation timing
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.entryType === 'navigation') {
                            this.analyzeNavigationTiming(entry);
                        } else if (entry.entryType === 'resource') {
                            this.analyzeResourceTiming(entry);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['navigation', 'resource'] });
            } catch (error) {
                console.warn('Performance Observer setup failed:', error);
            }
        }
    }
    
    analyzeNavigationTiming(entry) {
        const metrics = {
            dnsLookup: entry.domainLookupEnd - entry.domainLookupStart,
            tcpConnection: entry.connectEnd - entry.connectStart,
            serverResponse: entry.responseEnd - entry.requestStart,
            domProcessing: entry.domContentLoadedEventEnd - entry.responseEnd,
            pageLoad: entry.loadEventEnd - entry.loadEventStart
        };
        
        // Log slow operations
        Object.entries(metrics).forEach(([key, value]) => {
            if (value > 1000) { // More than 1 second
                console.warn(`Slow ${key}: ${value}ms`);
            }
        });
    }
    
    analyzeResourceTiming(entry) {
        // Check for slow API calls
        if (entry.name.includes('/api/')) {
            const duration = entry.responseEnd - entry.requestStart;
            this.metrics.apiCallCount++;
            this.metrics.totalApiTime += duration;
            
            if (duration > 2000) { // More than 2 seconds
                console.warn(`Slow API call: ${entry.name} took ${duration}ms`);
            }
        }
    }
    
    checkMemoryUsage() {
        if ('memory' in performance) {
            const memory = performance.memory;
            this.metrics.memoryUsage = memory.usedJSHeapSize;
            
            // Warn if memory usage is high
            if (memory.usedJSHeapSize > 50 * 1024 * 1024) { // 50MB
                console.warn('High memory usage detected:', memory.usedJSHeapSize / (1024 * 1024), 'MB');
            }
        }
    }
    
    // Measure API call performance
    async measureApiCall(url, options = {}) {
        const startTime = performance.now();
        
        try {
            const response = await fetch(url, options);
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            this.metrics.apiCallCount++;
            this.metrics.totalApiTime += duration;
            
            // Check if response was cached
            const cached = response.headers.get('cache-control') || 
                          response.headers.get('x-cache') === 'HIT';
            
            if (cached) {
                this.metrics.cacheHits++;
            } else {
                this.metrics.cacheMisses++;
            }
            
            console.log(`API call to ${url} took ${duration.toFixed(2)}ms`, cached ? '(cached)' : '');
            
            return response;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
    
    // Get current performance metrics
    getMetrics() {
        const avgApiTime = this.metrics.apiCallCount > 0 ? 
            this.metrics.totalApiTime / this.metrics.apiCallCount : 0;
        
        const cacheHitRate = (this.metrics.cacheHits + this.metrics.cacheMisses) > 0 ?
            this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses) : 0;
        
        return {
            ...this.metrics,
            avgApiTime: avgApiTime.toFixed(2),
            cacheHitRate: (cacheHitRate * 100).toFixed(1) + '%'
        };
    }
    
    // Report performance summary
    generateReport() {
        const metrics = this.getMetrics();
        
        console.group('Performance Report');
        console.log('Page Load Time:', metrics.pageLoadTime + 'ms');
        console.log('API Calls Made:', metrics.apiCallCount);
        console.log('Average API Time:', metrics.avgApiTime + 'ms');
        console.log('Cache Hit Rate:', metrics.cacheHitRate);
        console.log('Memory Usage:', (metrics.memoryUsage / (1024 * 1024)).toFixed(2) + 'MB');
        console.groupEnd();
        
        return metrics;
    }
}

// Lazy loading utility for images and components
class LazyLoader {
    constructor() {
        this.imageObserver = null;
        this.setupImageObserver();
    }
    
    setupImageObserver() {
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            this.imageObserver.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px 0px' // Start loading 50px before element is visible
            });
        }
    }
    
    // Add image to lazy loading
    observeImage(img) {
        if (this.imageObserver && img.dataset.src) {
            this.imageObserver.observe(img);
        }
    }
    
    // Lazy load all images with data-src attribute
    observeAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.observeImage(img));
    }
}

// Memory management utilities
class MemoryManager {
    constructor() {
        this.cache = new Map();
        this.maxCacheSize = 100; // Maximum number of cached items
    }
    
    // Add item to memory cache with LRU eviction
    set(key, value) {
        if (this.cache.size >= this.maxCacheSize) {
            // Remove oldest item
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, value);
    }
    
    get(key) {
        const value = this.cache.get(key);
        if (value !== undefined) {
            // Move to end (mark as recently used)
            this.cache.delete(key);
            this.cache.set(key, value);
        }
        return value;
    }
    
    clear() {
        this.cache.clear();
    }
    
    // Clean up unused objects
    cleanup() {
        // Force garbage collection if available (only in development)
        if (window.gc && typeof window.gc === 'function') {
            window.gc();
        }
    }
}

// Initialize performance monitoring
const performanceMonitor = new PerformanceMonitor();
const lazyLoader = new LazyLoader();
const memoryManager = new MemoryManager();

// Enhanced fetch with performance tracking
window.performanceFetch = async (url, options = {}) => {
    return performanceMonitor.measureApiCall(url, options);
};

// Export for use in other modules
export { PerformanceMonitor, LazyLoader, MemoryManager, performanceMonitor, lazyLoader, memoryManager };