# Environment Configuration Guide

## Overview

This guide provides comprehensive information about configuring environment variables and settings for the AI Empower Heart Platform across different deployment environments.

## Environment Files

### Backend Environment Configuration

The backend uses a `.env` file located in the `backend/` directory to manage configuration.

#### Template File
Use `backend/.env.example` as a template:

```bash
cp backend/.env.example backend/.env
```

#### Required Variables

**Flask Core Configuration**
```bash
# Flask secret key for session management and security
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-here-make-it-long-and-random

# Flask environment mode
FLASK_ENV=development  # development, production, testing

# Enable/disable debug mode
DEBUG=True  # True for development, False for production
```

**AI Service Configuration**
```bash
# OpenAI API key (Required)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# Alternative AI provider (Optional)
CLAUDE_API_KEY=your-claude-api-key-here
```

**Database Configuration**
```bash
# Database connection string
# Development (SQLite)
DATABASE_URL=sqlite:///spiritual_platform.db

# Production (PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/spiritual_platform

# Test database
# TEST_DATABASE_URL=sqlite:///test_spiritual_platform.db
```

**Cache and Session Storage**
```bash
# Redis URL for caching and session storage
REDIS_URL=redis://localhost:6379

# Session configuration
SESSION_TYPE=redis
SESSION_REDIS_URL=redis://localhost:6379
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
SESSION_KEY_PREFIX=spiritual_platform:
```

**Security and CORS**
```bash
# Allowed CORS origins (comma-separated)
# Development: Allow all origins
CORS_ORIGINS=*

# Production: Restrict to specific domains
# CORS_ORIGINS=https://empowerhub360.org,https://www.empowerhub360.org

# JWT settings (if using JWT authentication)
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour in seconds
```

**Email Configuration (Optional)**
```bash
# SMTP configuration for notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
EMAIL_USER=noreply@empowerhub360.org
EMAIL_PASSWORD=your-app-specific-password

# Email settings
EMAIL_SENDER=AI Empower Heart <noreply@empowerhub360.org>
EMAIL_REPLY_TO=support@empowerhub360.org
```

**Rate Limiting**
```bash
# Rate limiting configuration
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_STORAGE_URL=redis://localhost:6379

# AI API rate limiting
OPENAI_RATE_LIMIT_RPM=500  # Requests per minute
OPENAI_RATE_LIMIT_TPM=150000  # Tokens per minute
```

**Logging Configuration**
```bash
# Logging level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file location
LOG_FILE=logs/spiritual_platform.log

# Enable structured logging
STRUCTURED_LOGGING=True

# External logging service (Optional)
# SENTRY_DSN=your-sentry-dsn-here
```

**Analytics and Monitoring**
```bash
# Google Analytics
GOOGLE_ANALYTICS_ID=your-ga-id

# Application monitoring
NEW_RELIC_LICENSE_KEY=your-new-relic-key
NEW_RELIC_APP_NAME=AI Empower Heart Platform

# Health check settings
HEALTH_CHECK_ENABLED=True
HEALTH_CHECK_SECRET=your-health-check-secret
```

**Feature Flags**
```bash
# Enable/disable specific features
ENABLE_STREAMING_RESPONSES=True
ENABLE_VOICE_INPUT=True
ENABLE_USER_ACCOUNTS=True
ENABLE_CONVERSATION_HISTORY=True
ENABLE_ANALYTICS=True
ENABLE_CACHING=True

# AI model preferences
DEFAULT_AI_MODEL=gpt-4
FALLBACK_AI_MODEL=gpt-3.5-turbo
ENABLE_MODEL_FALLBACK=True
```

### Frontend Environment Configuration

The frontend uses environment variables for configuration, typically in `.env.local` for development.

#### Development Environment
```bash
# API configuration
VITE_API_BASE_URL=http://localhost:5000
VITE_API_TIMEOUT=30000

# Feature flags
VITE_ENABLE_STREAMING=true
VITE_ENABLE_VOICE_INPUT=true
VITE_ENABLE_ANALYTICS=true

# Debug settings
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug

# Analytics
VITE_GOOGLE_ANALYTICS_ID=your-ga-id
```

#### Production Environment
```bash
# API configuration
VITE_API_BASE_URL=/api
VITE_API_TIMEOUT=30000

# Feature flags
VITE_ENABLE_STREAMING=true
VITE_ENABLE_VOICE_INPUT=true
VITE_ENABLE_ANALYTICS=true

# Production settings
VITE_DEBUG_MODE=false
VITE_LOG_LEVEL=error

# Analytics
VITE_GOOGLE_ANALYTICS_ID=your-production-ga-id
```

## Environment-Specific Configurations

### Development Environment

**Characteristics:**
- Debug mode enabled
- Detailed error messages
- Hot reloading
- CORS allows all origins
- Local database (SQLite)
- Console logging

**Configuration:**
```bash
# backend/.env
SECRET_KEY=dev-secret-key-not-for-production
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///spiritual_platform.db
CORS_ORIGINS=*
LOG_LEVEL=DEBUG
OPENAI_API_KEY=sk-your-openai-key
```

### Testing Environment

**Characteristics:**
- Isolated test database
- Mock external services
- Predictable behavior
- Fast execution

**Configuration:**
```bash
# backend/.env.test
SECRET_KEY=test-secret-key
FLASK_ENV=testing
DEBUG=False
DATABASE_URL=sqlite:///test_spiritual_platform.db
REDIS_URL=redis://localhost:6379/1  # Different Redis DB
OPENAI_API_KEY=mock-api-key  # Or use real key for integration tests
ENABLE_ANALYTICS=False
EMAIL_BACKEND=console  # Don't send real emails in tests
```

### Staging Environment

**Characteristics:**
- Production-like configuration
- Real external services
- Performance testing
- Security testing

**Configuration:**
```bash
# backend/.env.staging
SECRET_KEY=staging-secret-key-long-and-secure
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/spiritual_platform
REDIS_URL=redis://staging-redis:6379
CORS_ORIGINS=https://staging.empowerhub360.org
LOG_LEVEL=INFO
OPENAI_API_KEY=sk-your-staging-openai-key
RATE_LIMIT_PER_HOUR=50  # Lower limits for staging
```

### Production Environment

**Characteristics:**
- High security
- Performance optimized
- Monitoring enabled
- Error tracking
- SSL/HTTPS required

**Configuration:**
```bash
# backend/.env.production
SECRET_KEY=production-secret-key-extremely-long-and-secure
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/spiritual_platform
REDIS_URL=redis://prod-redis:6379
CORS_ORIGINS=https://empowerhub360.org,https://www.empowerhub360.org
LOG_LEVEL=WARNING
OPENAI_API_KEY=sk-your-production-openai-key
RATE_LIMIT_PER_HOUR=100
SENTRY_DSN=your-production-sentry-dsn
ENABLE_ANALYTICS=True
```

## Google Cloud Services Configuration

### Service Account Setup

1. **Create Service Account Key:**
   ```bash
   cp key.example.json key.json
   ```

2. **Configure Service Account:**
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "your-private-key-id",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "service-account@your-project.iam.gserviceaccount.com",
     "client_id": "your-client-id",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project.iam.gserviceaccount.com"
   }
   ```

3. **Environment Variables:**
   ```bash
   # Google Cloud configuration
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   
   # Google Cloud Storage (for file uploads)
   GCS_BUCKET_NAME=your-bucket-name
   
   # Google Cloud Speech-to-Text
   GOOGLE_SPEECH_TO_TEXT_ENABLED=True
   
   # Google Cloud Translation
   GOOGLE_TRANSLATE_ENABLED=True
   ```

## Docker Environment Configuration

### Docker Compose Environment

**Development:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - FLASK_ENV=development
      - DEBUG=True
      - DATABASE_URL=sqlite:///spiritual_platform.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - backend/.env
```

**Production:**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: empowerheart/backend:latest
    environment:
      - FLASK_ENV=production
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/spiritual_platform
    env_file:
      - backend/.env.production
    secrets:
      - openai_api_key
      - secret_key

secrets:
  openai_api_key:
    external: true
  secret_key:
    external: true
```

## Security Best Practices

### Secret Management

1. **Use Strong Secrets:**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate random password
   openssl rand -base64 32
   ```

2. **Environment Variable Validation:**
   ```python
   # In your application
   import os
   
   def validate_environment():
       required_vars = [
           'SECRET_KEY',
           'OPENAI_API_KEY',
           'DATABASE_URL'
       ]
       
       missing_vars = [var for var in required_vars if not os.getenv(var)]
       
       if missing_vars:
           raise ValueError(f"Missing required environment variables: {missing_vars}")
   ```

3. **Secret Rotation:**
   ```bash
   # Rotate API keys regularly
   # Update SECRET_KEY periodically
   # Use different keys for different environments
   ```

### Access Control

```bash
# File permissions for sensitive files
chmod 600 backend/.env
chmod 600 key.json

# Ownership
chown app:app backend/.env
chown app:app key.json
```

## Environment Validation

### Validation Script

Create `scripts/validate_env.py`:

```python
#!/usr/bin/env python3
"""
Environment validation script for AI Empower Heart Platform
"""

import os
import sys
from urllib.parse import urlparse

def validate_environment():
    """Validate all required environment variables."""
    
    errors = []
    warnings = []
    
    # Required variables
    required_vars = {
        'SECRET_KEY': 'Flask secret key',
        'OPENAI_API_KEY': 'OpenAI API key',
        'DATABASE_URL': 'Database connection string'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"Missing {var} ({description})")
        elif var == 'SECRET_KEY' and len(value) < 32:
            warnings.append(f"{var} should be at least 32 characters long")
        elif var == 'OPENAI_API_KEY' and not value.startswith('sk-'):
            errors.append(f"{var} appears to be invalid (should start with 'sk-')")
    
    # Optional but recommended variables
    recommended_vars = {
        'REDIS_URL': 'Redis caching',
        'CORS_ORIGINS': 'CORS configuration',
        'LOG_LEVEL': 'Logging configuration'
    }
    
    for var, description in recommended_vars.items():
        if not os.getenv(var):
            warnings.append(f"Consider setting {var} for {description}")
    
    # Environment-specific validations
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        if os.getenv('DEBUG', '').lower() == 'true':
            errors.append("DEBUG should be False in production")
        
        if os.getenv('CORS_ORIGINS') == '*':
            warnings.append("CORS_ORIGINS should be restricted in production")
        
        if not os.getenv('SENTRY_DSN'):
            warnings.append("Consider setting SENTRY_DSN for error tracking in production")
    
    # Database URL validation
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        parsed = urlparse(db_url)
        if parsed.scheme not in ['sqlite', 'postgresql', 'mysql']:
            warnings.append(f"Unusual database scheme: {parsed.scheme}")
    
    # Print results
    if errors:
        print("❌ Environment validation failed:")
        for error in errors:
            print(f"  • {error}")
        print()
    
    if warnings:
        print("⚠️  Environment warnings:")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ Environment validation passed!")
    
    return len(errors) == 0

if __name__ == '__main__':
    if not validate_environment():
        sys.exit(1)
```

Run validation:
```bash
python scripts/validate_env.py
```

## Environment Loading

### Python Environment Loading

```python
# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///spiritual_platform.db'
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @classmethod
    def validate(cls):
        super().validate()
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig,  # Use development config for testing
    'default': DevelopmentConfig
}
```

### JavaScript Environment Loading

```javascript
// src/config/environment.js
const config = {
  development: {
    apiBaseUrl: 'http://localhost:5000',
    enableDebug: true,
    enableAnalytics: false,
    logLevel: 'debug'
  },
  
  production: {
    apiBaseUrl: '/api',
    enableDebug: false,
    enableAnalytics: true,
    logLevel: 'error'
  },
  
  testing: {
    apiBaseUrl: 'http://localhost:5000',
    enableDebug: true,
    enableAnalytics: false,
    logLevel: 'warn'
  }
};

const environment = process.env.NODE_ENV || 'development';
export default config[environment];
```

## Troubleshooting Environment Issues

### Common Problems

1. **Environment Variables Not Loading:**
   ```bash
   # Check if .env file exists
   ls -la backend/.env
   
   # Check file permissions
   ls -la backend/.env
   
   # Test loading manually
   python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv('backend/.env')
   print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY')[:10] + '...' if os.getenv('OPENAI_API_KEY') else 'Not found')
   "
   ```

2. **Wrong Environment File:**
   ```bash
   # Check which .env file is being loaded
   echo "Environment: $FLASK_ENV"
   
   # Specify environment file explicitly
   export FLASK_ENV=production
   export ENV_FILE=backend/.env.production
   ```

3. **Docker Environment Issues:**
   ```bash
   # Check environment variables in container
   docker exec container-name env | grep -E "(FLASK|OPENAI|DATABASE)"
   
   # Test environment loading in container
   docker exec container-name python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

For more troubleshooting help, see [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Best Practices Summary

1. **Security:**
   - Use strong, unique secret keys for each environment
   - Never commit sensitive environment files to version control
   - Rotate API keys and secrets regularly
   - Use different credentials for each environment

2. **Organization:**
   - Use descriptive variable names
   - Group related variables together
   - Document all variables with comments
   - Use environment-specific files (.env.development, .env.production)

3. **Validation:**
   - Validate required variables at application startup
   - Use type checking for configuration values
   - Provide clear error messages for missing configuration
   - Include validation in CI/CD pipeline

4. **Maintenance:**
   - Keep environment configurations up to date
   - Document any changes to environment variables
   - Test configuration changes in staging first
   - Monitor for configuration-related errors in production