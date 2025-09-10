import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spiritual-wisdom-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///spiritual_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database Performance Optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 10
    }
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CORS Configuration
    CORS_ORIGINS = ['https://empowerhub360.org', 'https://ai-empower-hq-360.github.io']
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Redis Configuration for Caching
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout
    
    # CDN Configuration
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN', 'https://cdn.empowerhub360.org')
    VIDEO_CDN_DOMAIN = os.environ.get('VIDEO_CDN_DOMAIN', 'https://video-cdn.empowerhub360.org')
    
    # Video Streaming Configuration
    VIDEO_STORAGE_PATH = os.environ.get('VIDEO_STORAGE_PATH', 'uploads/videos')
    HLS_SEGMENT_DURATION = 10  # seconds
    HLS_PLAYLIST_SIZE = 5
    
    # Performance Monitoring
    APM_SERVICE_NAME = 'ai-heart-platform'
    APM_SERVER_URL = os.environ.get('APM_SERVER_URL')
    APM_SECRET_TOKEN = os.environ.get('APM_SECRET_TOKEN')

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
