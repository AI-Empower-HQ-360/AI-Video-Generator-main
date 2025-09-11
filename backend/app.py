from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from flask_compress import Compress
import os
import time
from datetime import datetime
import logging

# Configure logging for better performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable response compression for better performance
compress = Compress()
compress.init_app(app)

# Performance-optimized CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",  # For development - we'll restrict this later
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 86400  # Cache preflight requests for 24 hours
    }
})

# Performance-optimized configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'spiritual-wisdom-key')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

# JSON configuration for better performance
app.config['JSON_SORT_KEYS'] = False  # Don't sort JSON keys for better performance
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing in production

# Session configuration for better performance
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime

# Initialize cache with Redis if available
try:
    from utils.cache import cache
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        cache.__init__(redis_url=redis_url)
        logger.info("Redis cache initialized")
except Exception as e:
    logger.warning(f"Cache initialization failed: {e}")

# Import API routes
from api.gurus import gurus_bp
from api.users import users_bp
from api.sessions import sessions_bp
from api.slokas import slokas_bp
from api.durable_endpoints import durable_bp
from api.whisper_endpoints import whisper_bp

# Configure CORS for Durable with performance optimizations
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://empowerhub360.org",
            "https://www.empowerhub360.org"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Register blueprints
app.register_blueprint(gurus_bp, url_prefix='/api/gurus')
app.register_blueprint(gurus_bp, url_prefix='/api')  # Also register at /api for direct spiritual guidance access
app.register_blueprint(users_bp, url_prefix='/api/users') 
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
app.register_blueprint(slokas_bp, url_prefix='/api/slokas')
app.register_blueprint(whisper_bp, url_prefix='/api/whisper')  # New Whisper endpoints
app.register_blueprint(durable_bp)  # No url_prefix as it has its own

# Performance middleware for caching and optimization
@app.after_request
def add_performance_headers(response):
    """Add performance-optimized headers to all responses"""
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add caching headers for static resources
    if request.endpoint and 'static' in request.endpoint:
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    elif request.endpoint and request.endpoint in ['health_check', 'test_connection']:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    else:
        # API responses - short cache for performance
        response.headers['Cache-Control'] = 'public, max-age=60'  # 1 minute
    
    # Add ETag for better caching
    if response.status_code == 200 and response.get_json():
        import hashlib
        content_hash = hashlib.md5(response.get_data()).hexdigest()
        response.headers['ETag'] = f'"{content_hash}"'
    
    # Compression hint
    response.headers['Vary'] = 'Accept-Encoding'
    
    return response

@app.before_request  
def performance_logging():
    """Log performance metrics for monitoring"""
    request.start_time = time.time()

@app.after_request
def log_performance(response):
    """Log request performance"""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}s")
        elif duration > 0.5:
            logger.info(f"Request: {request.method} {request.path} took {duration:.2f}s")
    return response

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Empower Heart Spiritual Platform API',
        'version': '1.0.0',
        'status': 'active',
        'available_gurus': ['karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'spiritual-guidance-platform',
        'gurus_available': True
    })

@app.route('/ai-gurus/spiritual-guru')
def spiritual_guru_video():
    """Render the spiritual guru video page"""
    return render_template('spiritual_guru_video.html')

@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['https://empowerhub360.org', 'https://www.empowerhub360.org'])
def test_connection():
    """Test endpoint to verify API connectivity"""
    return jsonify({
        'status': 'success',
        'message': 'API connection successful',
        'service': 'AI Empower Heart API'
    })

# Basic test route
@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': 'Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
