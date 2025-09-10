"""
Rate limiting middleware for API key management
"""
from flask import request, jsonify, g
from functools import wraps
import time
import hashlib
from datetime import datetime, timedelta

class RateLimiter:
    """In-memory rate limiter (use Redis in production)"""
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def is_allowed(self, key, limit, window=3600):
        """Check if request is allowed within rate limit"""
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup(now - window)
            self.last_cleanup = now
        
        # Get or create entry for this key
        if key not in self.requests:
            self.requests[key] = []
        
        entries = self.requests[key]
        
        # Remove old entries outside the window
        entries[:] = [entry for entry in entries if entry[0] > now - window]
        
        # Count requests in current window
        current_count = sum(entry[1] for entry in entries)
        
        if current_count >= limit:
            return False, current_count, limit
        
        # Add this request
        entries.append((now, 1))
        
        return True, current_count + 1, limit
    
    def _cleanup(self, cutoff_time):
        """Remove old entries"""
        for key in list(self.requests.keys()):
            self.requests[key] = [
                entry for entry in self.requests[key] 
                if entry[0] > cutoff_time
            ]
            if not self.requests[key]:
                del self.requests[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit_by_api_key():
    """Rate limiting decorator for API key requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract API key
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Validate API key and get rate limit
            try:
                from models.enterprise import ApiKey, User, Tenant
                from werkzeug.security import check_password_hash
                
                # Hash the provided key to compare
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                
                # Find matching API key
                api_key_record = None
                for key_record in ApiKey.query.filter_by(is_active=True).all():
                    if check_password_hash(key_record.key_hash, api_key):
                        api_key_record = key_record
                        break
                
                if not api_key_record:
                    return jsonify({'error': 'Invalid API key'}), 401
                
                # Check if API key is expired
                if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
                    return jsonify({'error': 'API key expired'}), 401
                
                # Get rate limit for this key
                rate_limit = api_key_record.rate_limit
                
                # Check rate limit
                limiter_key = f"api_key:{api_key_record.id}"
                allowed, current_count, limit = rate_limiter.is_allowed(limiter_key, rate_limit)
                
                if not allowed:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'limit': limit,
                        'current': current_count,
                        'reset_in': 3600  # 1 hour window
                    }), 429
                
                # Update usage tracking
                api_key_record.usage_count += 1
                api_key_record.last_used = datetime.utcnow()
                
                # Update user's API usage
                user = User.query.filter_by(id=api_key_record.user_id).first()
                if user:
                    user.api_usage_count += 1
                    user.last_api_call = datetime.utcnow()
                
                from models.enterprise import db
                db.session.commit()
                
                # Set context for the request
                g.api_key_id = api_key_record.id
                g.user_id = api_key_record.user_id
                g.tenant_id = api_key_record.tenant_id
                g.api_scopes = api_key_record.scopes
                
                # Log API call
                from api.enterprise import log_audit_event
                log_audit_event('api_call', api_key_record.tenant_id, {
                    'api_key_id': api_key_record.id,
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'usage_count': current_count
                }, user_id=api_key_record.user_id)
                
                # Add rate limit headers to response
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(limit)
                    response.headers['X-RateLimit-Remaining'] = str(limit - current_count)
                    response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 3600)
                
                return response
                
            except Exception as e:
                return jsonify({'error': f'Rate limiting error: {str(e)}'}), 500
                
        return decorated_function
    return decorator

def check_api_scope(required_scope):
    """Check if API key has required scope"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            scopes = getattr(g, 'api_scopes', [])
            
            if 'admin' in scopes:  # Admin scope grants all access
                return f(*args, **kwargs)
            
            if required_scope not in scopes:
                return jsonify({
                    'error': f'Insufficient permissions. Required scope: {required_scope}',
                    'available_scopes': scopes
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator