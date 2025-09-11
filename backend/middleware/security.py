"""
Security headers middleware for the AI Video Generator platform.
Implements security-first approach with comprehensive security headers and CSRF protection.
"""

import secrets
import functools
from typing import Dict, Any, Optional
from flask import request, jsonify, session, current_app, g
from werkzeug.exceptions import BadRequest
import logging

from utils.security import log_security_event

# Setup security logger
security_logger = logging.getLogger('security_headers')
security_logger.setLevel(logging.INFO)

class SecurityHeadersMiddleware:
    """Security headers and CSRF protection middleware"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Configure security settings
        app.config.setdefault('SECURITY_HEADERS_ENABLED', True)
        app.config.setdefault('CSRF_PROTECTION_ENABLED', True)
        app.config.setdefault('CONTENT_SECURITY_POLICY_ENABLED', True)
        
        # CSRF exempt routes (for API endpoints that use token authentication)
        app.config.setdefault('CSRF_EXEMPT_ROUTES', [
            'health',
            'api.test_connection',
            '/api/auth/login',  # Login endpoint needs to be exempt
            '/api/auth/register'  # Register endpoint needs to be exempt
        ])
    
    def before_request(self):
        """Process request before handling"""
        # Skip security checks for health endpoints
        if request.endpoint in ['health', 'home']:
            return
        
        # Log request for security monitoring
        self.log_request()
        
        # Validate request origin and referrer
        if not self.validate_request_origin():
            log_security_event('invalid_origin', {
                'origin': request.headers.get('Origin'),
                'referrer': request.headers.get('Referer'),
                'endpoint': request.endpoint
            })
            return jsonify({
                'success': False,
                'error': 'Invalid request origin',
                'code': 'INVALID_ORIGIN'
            }), 403
        
        # CSRF protection for state-changing operations
        if current_app.config.get('CSRF_PROTECTION_ENABLED'):
            if not self.validate_csrf_token():
                return jsonify({
                    'success': False,
                    'error': 'CSRF token validation failed',
                    'code': 'CSRF_VALIDATION_FAILED'
                }), 403
    
    def after_request(self, response):
        """Add security headers to response"""
        if current_app.config.get('SECURITY_HEADERS_ENABLED'):
            response = self.add_security_headers(response)
        return response
    
    def add_security_headers(self, response):
        """Add comprehensive security headers"""
        headers = {
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Prevent caching of sensitive content
            'Cache-Control': 'no-cache, no-store, must-revalidate, private',
            'Pragma': 'no-cache',
            'Expires': '0',
            
            # Security policy headers
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
            
            # HSTS (HTTP Strict Transport Security) - only for HTTPS
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
        }
        
        # Content Security Policy
        if current_app.config.get('CONTENT_SECURITY_POLICY_ENABLED'):
            csp = self.get_content_security_policy()
            headers['Content-Security-Policy'] = csp
        
        # Add headers to response
        for header, value in headers.items():
            response.headers[header] = value
        
        # Add CSRF token to response for forms
        if request.endpoint and request.method in ['GET']:
            csrf_token = self.generate_csrf_token()
            response.headers['X-CSRF-Token'] = csrf_token
        
        return response
    
    def get_content_security_policy(self) -> str:
        """Generate Content Security Policy"""
        # Base CSP for API endpoints
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.openai.com wss:",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "upgrade-insecure-requests"
        ]
        
        # Add development-specific CSP for local development
        if current_app.config.get('DEBUG'):
            csp_directives.extend([
                "connect-src 'self' http://localhost:* https://api.openai.com wss:",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net"
            ])
        
        return "; ".join(csp_directives)
    
    def validate_request_origin(self) -> bool:
        """Validate request origin for CORS security"""
        # Skip origin validation for same-origin requests
        if not request.headers.get('Origin'):
            return True
        
        origin = request.headers.get('Origin')
        allowed_origins = current_app.config.get('CORS_ORIGINS', [])
        
        # Convert string to list if needed
        if isinstance(allowed_origins, str):
            allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
        
        # Add localhost for development
        if current_app.config.get('DEBUG'):
            allowed_origins.extend([
                'http://localhost:3000',
                'http://localhost:5000',
                'http://127.0.0.1:3000',
                'http://127.0.0.1:5000'
            ])
        
        return origin in allowed_origins
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session['csrf_token']
    
    def validate_csrf_token(self) -> bool:
        """Validate CSRF token for state-changing operations"""
        # Skip CSRF validation for certain routes
        if request.endpoint in current_app.config.get('CSRF_EXEMPT_ROUTES', []):
            return True
        
        # Skip CSRF for GET, HEAD, OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Skip CSRF for API requests with valid JWT token
        if self.has_valid_api_token():
            return True
        
        # Get CSRF token from header or form data
        csrf_token = (
            request.headers.get('X-CSRF-Token') or
            request.form.get('csrf_token') or
            request.json.get('csrf_token') if request.is_json else None
        )
        
        expected_token = session.get('csrf_token')
        
        if not csrf_token or not expected_token:
            log_security_event('csrf_token_missing', {
                'endpoint': request.endpoint,
                'method': request.method
            })
            return False
        
        if not secrets.compare_digest(csrf_token, expected_token):
            log_security_event('csrf_token_invalid', {
                'endpoint': request.endpoint,
                'method': request.method
            })
            return False
        
        return True
    
    def has_valid_api_token(self) -> bool:
        """Check if request has valid API token (JWT)"""
        auth_header = request.headers.get('Authorization')
        return auth_header and auth_header.startswith('Bearer ')
    
    def log_request(self):
        """Log request for security monitoring"""
        # Log potentially suspicious requests
        suspicious_indicators = [
            '../' in request.url,
            'script>' in request.url.lower(),
            'union select' in request.url.lower(),
            'drop table' in request.url.lower()
        ]
        
        if any(suspicious_indicators):
            log_security_event('suspicious_request', {
                'url': request.url,
                'method': request.method,
                'user_agent': request.headers.get('User-Agent', ''),
                'endpoint': request.endpoint
            })

# Decorator for endpoints that need CSRF protection
def csrf_protect(f):
    """Decorator to enforce CSRF protection on specific endpoints"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('CSRF_PROTECTION_ENABLED'):
            return f(*args, **kwargs)
        
        # Force CSRF validation regardless of other rules
        csrf_token = (
            request.headers.get('X-CSRF-Token') or
            request.form.get('csrf_token') or
            request.json.get('csrf_token') if request.is_json else None
        )
        
        expected_token = session.get('csrf_token')
        
        if not csrf_token or not expected_token or not secrets.compare_digest(csrf_token, expected_token):
            log_security_event('csrf_protection_failed', {
                'endpoint': request.endpoint,
                'method': request.method
            })
            return jsonify({
                'success': False,
                'error': 'CSRF protection failed',
                'code': 'CSRF_PROTECTION_FAILED'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Decorator to exempt endpoints from CSRF protection
def csrf_exempt(f):
    """Decorator to exempt endpoints from CSRF protection"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        g.csrf_exempt = True
        return f(*args, **kwargs)
    return decorated_function

# Utility functions
def get_csrf_token() -> str:
    """Get CSRF token for current session"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_secure_headers(response_headers: Dict[str, str]) -> bool:
    """Validate that response has required security headers"""
    required_headers = [
        'X-Frame-Options',
        'X-Content-Type-Options',
        'X-XSS-Protection',
        'Content-Security-Policy'
    ]
    
    return all(header in response_headers for header in required_headers)