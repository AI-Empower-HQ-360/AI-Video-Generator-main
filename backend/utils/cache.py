"""
Performance-optimized caching utilities for AI Video Generator backend
Implements Redis caching with fallback to in-memory cache for better performance
"""
import json
import hashlib
import time
from typing import Any, Optional, Union
from functools import wraps
import logging

# Try to import Redis, fallback to in-memory cache if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class PerformanceCache:
    """
    High-performance caching layer with Redis primary and in-memory fallback
    Optimized for AI API responses, database queries, and expensive computations
    """
    
    def __init__(self, redis_url: Optional[str] = None, max_memory_items: int = 1000):
        self.redis_client = None
        self.memory_cache = {}
        self.memory_access_times = {}
        self.max_memory_items = max_memory_items
        
        # Initialize Redis if available
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
                self.redis_client = None
        else:
            logger.info("Using in-memory cache (Redis not available)")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key from arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cleanup_memory_cache(self):
        """Remove oldest items from memory cache when it's full"""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove 20% of oldest items
            items_to_remove = int(self.max_memory_items * 0.2)
            oldest_keys = sorted(self.memory_access_times.keys(), 
                               key=lambda k: self.memory_access_times[k])[:items_to_remove]
            
            for key in oldest_keys:
                self.memory_cache.pop(key, None)
                self.memory_access_times.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (Redis first, then memory)"""
        try:
            # Try Redis first
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to memory cache
            if key in self.memory_cache:
                self.memory_access_times[key] = time.time()
                return self.memory_cache[key]
            
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Try Redis first
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized_value)
                return True
            
            # Fallback to memory cache
            self._cleanup_memory_cache()
            self.memory_cache[key] = value
            self.memory_access_times[key] = time.time()
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            deleted = False
            
            if self.redis_client:
                deleted = self.redis_client.delete(key) > 0
            
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.memory_access_times.pop(key, None)
                deleted = True
            
            return deleted
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self):
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            
            self.memory_cache.clear()
            self.memory_access_times.clear()
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")

# Global cache instance
cache = PerformanceCache()

def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        return wrapper
    return decorator

def cache_ai_response(ttl: int = 1800):
    """Specific decorator for AI API responses with shorter TTL"""
    return cached("ai_response", ttl)

def cache_db_query(ttl: int = 3600):
    """Specific decorator for database queries"""
    return cached("db_query", ttl)

def cache_expensive_computation(ttl: int = 7200):
    """Specific decorator for expensive computations"""
    return cached("computation", ttl)