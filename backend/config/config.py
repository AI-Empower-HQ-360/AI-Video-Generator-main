import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spiritual-wisdom-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///spiritual_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Cost Management Configuration
    COST_DAILY_LIMIT = float(os.environ.get('COST_DAILY_LIMIT', 10.0))
    COST_MONTHLY_LIMIT = float(os.environ.get('COST_MONTHLY_LIMIT', 100.0))
    TOKEN_DAILY_LIMIT = int(os.environ.get('TOKEN_DAILY_LIMIT', 10000))
    TOKEN_MONTHLY_LIMIT = int(os.environ.get('TOKEN_MONTHLY_LIMIT', 100000))
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 3600))  # Cache time-to-live in seconds
    MAX_CACHE_SIZE = int(os.environ.get('MAX_CACHE_SIZE', 1000))  # Maximum cache entries
    
    # Alert Thresholds
    ALERT_DAILY_COST_THRESHOLD = float(os.environ.get('ALERT_DAILY_COST_THRESHOLD', 10.0))
    ALERT_MONTHLY_COST_THRESHOLD = float(os.environ.get('ALERT_MONTHLY_COST_THRESHOLD', 100.0))
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CORS Configuration
    CORS_ORIGINS = ['https://empowerhub360.org', 'https://ai-empower-hq-360.github.io']
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')

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
