import os
from datetime import timedelta

class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spiritual-wisdom-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///spiritual_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # CORS Configuration - Restrictive by default
    CORS_ORIGINS = [
        'https://empowerhub360.org', 
        'https://ai-empower-hq-360.github.io',
        'https://www.empowerhub360.org'
    ]
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Security Configuration
    SECURITY_HEADERS_ENABLED = True
    CSRF_PROTECTION_ENABLED = True
    CONTENT_SECURITY_POLICY_ENABLED = True
    
    # Rate Limits (requests per time period)
    API_RATE_LIMITS = {
        'default': '100 per hour',
        'auth': '10 per minute',
        'guru_ask': '50 per hour',
        'file_upload': '20 per hour',
        'password_reset': '5 per hour'
    }
    
    # File Upload Security
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max request size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    ALLOWED_EXTENSIONS = {'txt', 'json', 'md', 'pdf', 'doc', 'docx'}
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # API Security Settings
    API_KEY_VALIDATION_ENABLED = True
    REQUEST_LOGGING_ENABLED = True
    SUSPICIOUS_ACTIVITY_MONITORING = True
    
    # CSRF Exempt Routes (for API endpoints using JWT)
    CSRF_EXEMPT_ROUTES = [
        'health',
        'home',
        'api.test_connection'
    ]

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    
    # Relaxed settings for development
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    CORS_ORIGINS = Config.CORS_ORIGINS + [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5000'
    ]
    
    # More lenient rate limits for development
    API_RATE_LIMITS = {
        'default': '200 per hour',
        'auth': '20 per minute',
        'guru_ask': '100 per hour',
        'file_upload': '40 per hour',
        'password_reset': '10 per hour'
    }

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    
    # Strict production settings
    SESSION_COOKIE_SECURE = True
    CSRF_PROTECTION_ENABLED = True
    
    # Stricter rate limits for production
    API_RATE_LIMITS = {
        'default': '60 per hour',
        'auth': '5 per minute',
        'guru_ask': '30 per hour',
        'file_upload': '10 per hour',
        'password_reset': '3 per hour'
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    
    # Disable security features that interfere with testing
    SECURITY_HEADERS_ENABLED = False
    CSRF_PROTECTION_ENABLED = False
    RATELIMIT_STORAGE_URL = 'memory://'
    SESSION_COOKIE_SECURE = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
