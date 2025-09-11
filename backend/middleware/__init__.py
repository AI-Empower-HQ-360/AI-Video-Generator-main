"""
Middleware package for the AI Video Generator platform.
Contains authentication and security middleware components.
"""

from .auth import AuthManager, require_auth, optional_auth, require_role, get_current_user
from .security import SecurityHeadersMiddleware, csrf_protect, csrf_exempt, get_csrf_token

__all__ = [
    'AuthManager',
    'require_auth', 
    'optional_auth',
    'require_role',
    'get_current_user',
    'SecurityHeadersMiddleware',
    'csrf_protect',
    'csrf_exempt',
    'get_csrf_token'
]