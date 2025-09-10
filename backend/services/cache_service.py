"""
Redis-based caching service for API response optimization
"""

import json
import pickle
from functools import wraps
from typing import Any, Optional, Union
from datetime import timedelta

try:
    import redis
    from flask import current_app
except ImportError:
    redis = None


class CacheService:
    """Redis-based caching service with fallback to memory cache"""
    
    def __init__(self, app=None):
        self.redis_client = None
        self._memory_cache = {}
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize cache service with Flask app"""
        try:
            if redis and app.config.get('REDIS_URL'):
                self.redis_client = redis.from_url(
                    app.config['REDIS_URL'],
                    decode_responses=False
                )
                # Test connection
                self.redis_client.ping()
                app.logger.info("Redis cache initialized successfully")
            else:
                app.logger.warning("Redis not available, using memory cache")
        except Exception as e:
            app.logger.warning(f"Redis connection failed: {e}, using memory cache")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            else:
                return self._memory_cache.get(key)
        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache with optional timeout"""
        try:
            if self.redis_client:
                serialized_value = pickle.dumps(value)
                if timeout:
                    return self.redis_client.setex(key, timeout, serialized_value)
                else:
                    return self.redis_client.set(key, serialized_value)
            else:
                self._memory_cache[key] = value
                return True
        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                return bool(self._memory_cache.pop(key, None))
        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                return self.redis_client.flushdb()
            else:
                self._memory_cache.clear()
                return True
        except Exception as e:
            current_app.logger.error(f"Cache clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self._memory_cache
        except Exception as e:
            current_app.logger.error(f"Cache exists error: {e}")
            return False


# Global cache instance
cache = CacheService()


def cached(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator for caching function results
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def cache_response(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator for caching API responses
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Generate cache key from request
            cache_key = f"{key_prefix}:api:{request.endpoint}:{hash(request.full_path)}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                response = jsonify(cached_response)
                response.headers['X-Cache'] = 'HIT'
                return response
            
            # Execute function and cache response
            result = f(*args, **kwargs)
            
            # Cache successful responses only
            if hasattr(result, 'status_code') and result.status_code == 200:
                cache.set(cache_key, result.get_json(), timeout)
                result.headers['X-Cache'] = 'MISS'
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """Invalidate cache keys matching pattern"""
    try:
        if cache.redis_client:
            keys = cache.redis_client.keys(pattern)
            if keys:
                cache.redis_client.delete(*keys)
                return len(keys)
    except Exception as e:
        current_app.logger.error(f"Cache invalidation error: {e}")
    return 0