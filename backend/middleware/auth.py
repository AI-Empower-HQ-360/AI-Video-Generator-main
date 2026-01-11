"""
Authentication middleware for the AI Video Generator platform.
Implements JWT-based authentication with security-first approach.
"""

import jwt
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import request, jsonify, current_app, g
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
import logging

from utils.security import log_security_event, SecurityError

# Setup auth logger
auth_logger = logging.getLogger('auth')
auth_logger.setLevel(logging.INFO)

# JWT Configuration
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_DAYS = 30

class AuthenticationError(Exception):
    """Authentication related errors"""
    pass

class AuthManager:
    """JWT Authentication manager with security features"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize JWT with Flask app"""
        # JWT Configuration
        app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'jwt-secret-change-in-production')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=JWT_EXPIRATION_HOURS)
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=JWT_REFRESH_EXPIRATION_DAYS)
        app.config['JWT_ALGORITHM'] = 'HS256'
        
        # Initialize JWT manager
        self.jwt = JWTManager(app)
        
        # JWT error handlers
        @self.jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            log_security_event('jwt_expired', {
                'user_id': jwt_payload.get('sub'),
                'exp': jwt_payload.get('exp')
            })
            return jsonify({
                'success': False,
                'error': 'Token has expired',
                'code': 'TOKEN_EXPIRED'
            }), 401
        
        @self.jwt.invalid_token_loader
        def invalid_token_callback(error):
            log_security_event('jwt_invalid', {'error': str(error)})
            return jsonify({
                'success': False,
                'error': 'Invalid token',
                'code': 'INVALID_TOKEN'
            }), 401
        
        @self.jwt.unauthorized_loader
        def missing_token_callback(error):
            log_security_event('jwt_missing', {'error': str(error)})
            return jsonify({
                'success': False,
                'error': 'Authorization token required',
                'code': 'TOKEN_REQUIRED'
            }), 401
    
    @staticmethod
    def generate_tokens(user_id: str, additional_claims: Optional[Dict] = None) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        identity = user_id
        additional_claims = additional_claims or {}
        
        # Add security claims
        additional_claims.update({
            'iat': datetime.utcnow().timestamp(),
            'type': 'access'
        })
        
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
        
        # Generate refresh token with longer expiration
        refresh_claims = additional_claims.copy()
        refresh_claims['type'] = 'refresh'
        
        refresh_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
            additional_claims=refresh_claims
        )
        
        log_security_event('token_generated', {
            'user_id': user_id,
            'token_type': 'access_and_refresh'
        })
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        }
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # Verify token type
            if payload.get('type') != 'access':
                raise AuthenticationError("Invalid token type")
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                raise AuthenticationError("Token has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def extract_token_from_request() -> Optional[str]:
        """Extract JWT token from request headers"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None

# Authentication decorators
def require_auth(f):
    """Decorator to require authentication"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = AuthManager.extract_token_from_request()
            if not token:
                log_security_event('auth_missing_token', {
                    'endpoint': request.endpoint
                })
                return jsonify({
                    'success': False,
                    'error': 'Authorization token required',
                    'code': 'TOKEN_REQUIRED'
                }), 401
            
            payload = AuthManager.verify_token(token)
            g.current_user_id = payload.get('sub')
            g.current_user_claims = payload
            
            log_security_event('auth_success', {
                'user_id': g.current_user_id,
                'endpoint': request.endpoint
            })
            
        except AuthenticationError as e:
            log_security_event('auth_failed', {
                'error': str(e),
                'endpoint': request.endpoint
            })
            return jsonify({
                'success': False,
                'error': str(e),
                'code': 'AUTH_FAILED'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (useful for public endpoints with enhanced features for authenticated users)"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_user_id = None
        g.current_user_claims = None
        
        token = AuthManager.extract_token_from_request()
        if token:
            try:
                payload = AuthManager.verify_token(token)
                g.current_user_id = payload.get('sub')
                g.current_user_claims = payload
                
                log_security_event('optional_auth_success', {
                    'user_id': g.current_user_id,
                    'endpoint': request.endpoint
                })
            except AuthenticationError:
                # For optional auth, we don't fail on invalid tokens
                # but we log the attempt
                log_security_event('optional_auth_failed', {
                    'endpoint': request.endpoint
                })
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user_claims') or not g.current_user_claims:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            user_roles = g.current_user_claims.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                log_security_event('insufficient_privileges', {
                    'user_id': g.current_user_id,
                    'required_roles': required_roles,
                    'user_roles': user_roles,
                    'endpoint': request.endpoint
                })
                return jsonify({
                    'success': False,
                    'error': 'Insufficient privileges',
                    'code': 'INSUFFICIENT_PRIVILEGES'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_user_session(user_id: str, user_data: Dict[str, Any]) -> Dict[str, str]:
    """Create authenticated user session"""
    additional_claims = {
        'email': user_data.get('email'),
        'roles': user_data.get('roles', ['user']),
        'preferences': user_data.get('preferences', {})
    }
    
    tokens = AuthManager.generate_tokens(user_id, additional_claims)
    
    log_security_event('session_created', {
        'user_id': user_id,
        'email': user_data.get('email')
    })
    
    return tokens

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user information"""
    if hasattr(g, 'current_user_id') and g.current_user_id:
        return {
            'user_id': g.current_user_id,
            'claims': g.current_user_claims
        }
    return None