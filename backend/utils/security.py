"""
Security utilities and decorators for the AI Video Generator platform.
Implements security-first approach with input validation, rate limiting, and secure practices.
"""

import re
import hashlib
import secrets
import functools
from typing import Dict, Any, Optional, List
from flask import request, jsonify, current_app
from werkzeug.exceptions import BadRequest
import logging

# Setup security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Security constants
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
MAX_STRING_LENGTH = 1000
MAX_JSON_KEYS = 50
ALLOWED_FILE_EXTENSIONS = {'txt', 'json', 'md', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Input validation patterns
PATTERNS = {
    'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    'username': re.compile(r'^[a-zA-Z0-9_-]{3,30}$'),
    'guru_type': re.compile(r'^[a-z]{3,20}$'),
    'safe_string': re.compile(r'^[a-zA-Z0-9\s\.\,\!\?\-\_\:\;]{1,1000}$'),
    'api_key_format': re.compile(r'^sk-[a-zA-Z0-9]{32,}$'),  # OpenAI API key pattern
}

class SecurityError(Exception):
    """Custom security exception"""
    pass

class InputValidator:
    """Input validation utilities with security-first approach"""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, max_length: int = MAX_STRING_LENGTH, 
                       pattern: Optional[str] = None, required: bool = True) -> str:
        """Validate string input with length and pattern checks"""
        if value is None:
            if required:
                raise SecurityError(f"{field_name} is required")
            return ""
        
        if not isinstance(value, str):
            raise SecurityError(f"{field_name} must be a string")
        
        # Check length
        if len(value) > max_length:
            raise SecurityError(f"{field_name} exceeds maximum length of {max_length}")
        
        # Check pattern if provided
        if pattern and pattern in PATTERNS:
            if not PATTERNS[pattern].match(value):
                raise SecurityError(f"{field_name} format is invalid")
        
        # Basic XSS prevention
        if InputValidator._contains_suspicious_content(value):
            security_logger.warning(f"Suspicious content detected in {field_name}: {value[:50]}...")
            raise SecurityError(f"{field_name} contains potentially malicious content")
        
        return value.strip()
    
    @staticmethod
    def validate_json_payload(data: Dict[str, Any], max_keys: int = MAX_JSON_KEYS) -> Dict[str, Any]:
        """Validate JSON payload size and structure"""
        if not isinstance(data, dict):
            raise SecurityError("Request payload must be a JSON object")
        
        if len(data) > max_keys:
            raise SecurityError(f"Request payload exceeds maximum {max_keys} keys")
        
        # Check for deeply nested objects (DoS prevention)
        if InputValidator._check_nested_depth(data) > 10:
            raise SecurityError("Request payload is too deeply nested")
        
        return data
    
    @staticmethod
    def validate_guru_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate spiritual guru API request"""
        validated = {}
        
        # Validate guru_type
        validated['guru_type'] = InputValidator.validate_string(
            data.get('guru_type'), 'guru_type', 20, 'guru_type', required=True
        )
        
        # Validate question
        validated['question'] = InputValidator.validate_string(
            data.get('question'), 'question', 2000, 'safe_string', required=True
        )
        
        # Validate optional user_context
        if 'user_context' in data:
            validated['user_context'] = InputValidator.validate_string(
                data.get('user_context'), 'user_context', 500, 'safe_string', required=False
            )
        
        return validated
    
    @staticmethod
    def validate_file_upload(file) -> bool:
        """Validate uploaded file for security"""
        if not file:
            raise SecurityError("No file provided")
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > MAX_FILE_SIZE:
            raise SecurityError(f"File size exceeds maximum {MAX_FILE_SIZE} bytes")
        
        # Check file extension
        filename = file.filename or ""
        if not filename or '.' not in filename:
            raise SecurityError("File must have a valid extension")
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_FILE_EXTENSIONS:
            raise SecurityError(f"File extension '{extension}' not allowed")
        
        # Check for suspicious filenames
        if InputValidator._contains_suspicious_filename(filename):
            raise SecurityError("Suspicious filename detected")
        
        return True
    
    @staticmethod
    def _contains_suspicious_content(content: str) -> bool:
        """Check for potentially malicious content"""
        suspicious_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'eval(', 'exec(', 'import os', 'subprocess', '__import__',
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET',
            '../', '..\\', '/etc/passwd', '/etc/shadow'
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in suspicious_patterns)
    
    @staticmethod
    def _contains_suspicious_filename(filename: str) -> bool:
        """Check for suspicious filenames"""
        suspicious_names = [
            '..', '.htaccess', '.env', 'config', 'passwd', 'shadow',
            'web.config', '.git', '.ssh', 'id_rsa'
        ]
        
        filename_lower = filename.lower()
        return any(name in filename_lower for name in suspicious_names)
    
    @staticmethod
    def _check_nested_depth(obj: Any, depth: int = 0) -> int:
        """Check nesting depth of JSON object"""
        if depth > 15:  # Prevent stack overflow
            return depth
        
        if isinstance(obj, dict):
            return max(InputValidator._check_nested_depth(v, depth + 1) for v in obj.values()) if obj else depth
        elif isinstance(obj, list):
            return max(InputValidator._check_nested_depth(item, depth + 1) for item in obj) if obj else depth
        else:
            return depth

def validate_request_size(f):
    """Decorator to validate request size"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_length and request.content_length > MAX_REQUEST_SIZE:
            security_logger.warning(f"Request size limit exceeded: {request.content_length} bytes from {request.remote_addr}")
            return jsonify({
                'success': False,
                'error': 'Request size exceeds maximum limit',
                'code': 'REQUEST_TOO_LARGE'
            }), 413
        return f(*args, **kwargs)
    return decorated_function

def validate_content_type(allowed_types: List[str]):
    """Decorator to validate content type"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_type not in allowed_types:
                security_logger.warning(f"Invalid content type: {request.content_type} from {request.remote_addr}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid content type',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events for monitoring"""
    log_data = {
        'event_type': event_type,
        'timestamp': request.timestamp if hasattr(request, 'timestamp') else None,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'endpoint': request.endpoint,
        'method': request.method,
        **details
    }
    
    security_logger.info(f"Security Event: {event_type}", extra=log_data)

def generate_secure_token() -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage"""
    salt = current_app.config.get('SECRET_KEY', 'default-salt')
    return hashlib.pbkdf2_hmac('sha256', api_key.encode(), salt.encode(), 100000).hex()

def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format (e.g., OpenAI)"""
    if not api_key:
        return False
    return bool(PATTERNS['api_key_format'].match(api_key))