from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime
import logging

# Import security middleware
from middleware.security import SecurityHeadersMiddleware
from middleware.auth import AuthManager
from utils.security import log_security_event, validate_api_key_format

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    from config.config import ProductionConfig
    app.config.from_object(ProductionConfig)
elif config_name == 'testing':
    from config.config import TestingConfig
    app.config.from_object(TestingConfig)
else:
    from config.config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize security middleware
security_middleware = SecurityHeadersMiddleware(app)
auth_manager = AuthManager(app)

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
    strategy=app.config.get('RATELIMIT_STRATEGY', 'fixed-window'),
    headers_enabled=app.config.get('RATELIMIT_HEADERS_ENABLED', True)
)

# Configure CORS with security-first approach
CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get('CORS_ORIGINS', []),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"],
        "supports_credentials": True
    }
})

# Validate OpenAI API key on startup
openai_key = app.config.get('OPENAI_API_KEY')
if openai_key and not validate_api_key_format(openai_key):
    logging.warning("OpenAI API key format appears invalid")

# Import API routes
from api.gurus import gurus_bp
from api.users import users_bp
from api.sessions import sessions_bp
from api.slokas import slokas_bp
from api.durable_endpoints import durable_bp
from api.whisper_endpoints import whisper_bp
from api.video_endpoints import video_bp

# Register blueprints with rate limiting
app.register_blueprint(gurus_bp, url_prefix='/api/gurus')
app.register_blueprint(gurus_bp, url_prefix='/api')  # Also register at /api for direct spiritual guidance access
app.register_blueprint(users_bp, url_prefix='/api/users') 
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
app.register_blueprint(slokas_bp, url_prefix='/api/slokas')
app.register_blueprint(whisper_bp, url_prefix='/api/whisper')  # Whisper endpoints
app.register_blueprint(video_bp, url_prefix='/api/video')      # Video processing endpoints
app.register_blueprint(durable_bp)  # No url_prefix as it has its own

@app.route('/')
@limiter.limit(app.config['API_RATE_LIMITS']['default'])
def home():
    log_security_event('api_access', {
        'endpoint': 'home',
        'user_agent': request.headers.get('User-Agent', '')
    })
    
    return jsonify({
        'message': 'AI Empower Heart Spiritual Platform API',
        'version': '1.0.0',
        'status': 'active',
        'available_gurus': ['karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'],
        'timestamp': datetime.utcnow().isoformat(),
        'security': {
            'https_required': not app.config.get('DEBUG', False),
            'rate_limiting_enabled': True,
            'authentication_required': 'varies_by_endpoint'
        }
    })

@app.route('/health')
@limiter.exempt  # Health checks should not be rate limited
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'spiritual-guidance-platform',
        'gurus_available': True,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/ai-gurus/spiritual-guru')
@limiter.limit(app.config['API_RATE_LIMITS']['default'])
def spiritual_guru_video():
    """Render the spiritual guru video page"""
    return render_template('spiritual_guru_video.html')

@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin(origins=app.config.get('CORS_ORIGINS', []))
@limiter.limit(app.config['API_RATE_LIMITS']['default'])
def test_connection():
    """Test endpoint to verify API connectivity"""
    log_security_event('api_test', {
        'origin': request.headers.get('Origin', ''),
        'user_agent': request.headers.get('User-Agent', '')
    })
    
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'service': 'AI Empower Heart API',
        'timestamp': datetime.utcnow().isoformat()
    })

# Basic test route
@app.route('/test', methods=['GET'])
@limiter.limit(app.config['API_RATE_LIMITS']['default'])
def test():
    return jsonify({
        'status': 'success',
        'message': 'Backend is running!',
        'timestamp': datetime.utcnow().isoformat()
    })

# Security endpoints
@app.route('/api/security/csrf-token', methods=['GET'])
@limiter.limit("20 per minute")
def get_csrf_token():
    """Get CSRF token for forms"""
    from middleware.security import get_csrf_token
    
    return jsonify({
        'success': True,
        'csrf_token': get_csrf_token()
    })

# Global error handlers for security
@app.errorhandler(429)
def ratelimit_handler(e):
    log_security_event('rate_limit_exceeded', {
        'limit': str(e.description),
        'endpoint': request.endpoint
    })
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded',
        'code': 'RATE_LIMIT_EXCEEDED',
        'retry_after': getattr(e, 'retry_after', None)
    }), 429

@app.errorhandler(413)
def payload_too_large(e):
    log_security_event('payload_too_large', {
        'content_length': request.content_length,
        'endpoint': request.endpoint
    })
    return jsonify({
        'success': False,
        'error': 'Request payload too large',
        'code': 'PAYLOAD_TOO_LARGE'
    }), 413

@app.errorhandler(400)
def bad_request(e):
    log_security_event('bad_request', {
        'error': str(e),
        'endpoint': request.endpoint
    })
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'code': 'BAD_REQUEST'
    }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
