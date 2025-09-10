from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import os
from datetime import datetime

app = Flask(__name__)

# Load configuration
from config.config import config
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize database
from models.database import db
db.init_app(app)

# Initialize services
from services.cache_service import cache
from services.video_service import video_service
from services.performance_monitor import performance_monitor

cache.init_app(app)
video_service.init_app(app)
performance_monitor.init_app(app)

# Store services in app for access in routes
app.cache = cache
app.video_service = video_service
app.performance_monitor = performance_monitor

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",  # For development - we'll restrict this later
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Import API routes
from api.gurus import gurus_bp
from api.users import users_bp
from api.sessions import sessions_bp
from api.slokas import slokas_bp
from api.durable_endpoints import durable_bp
from api.whisper_endpoints import whisper_bp
from api.video_endpoints import video_bp
from api.performance_endpoints import performance_bp

# Configure CORS for Durable
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
app.register_blueprint(video_bp, url_prefix='/api/videos')  # New video endpoints
app.register_blueprint(performance_bp, url_prefix='/api/performance')  # Performance monitoring
app.register_blueprint(durable_bp)  # No url_prefix as it has its own

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Empower Heart Spiritual Platform API',
        'version': '2.0.0',  # Updated for performance optimizations
        'status': 'active',
        'features': {
            'gurus': ['karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'],
            'video_streaming': True,
            'adaptive_bitrate': True,
            'cdn_integration': True,
            'performance_monitoring': True,
            'caching': True
        },
        'endpoints': {
            'videos': '/api/videos',
            'performance': '/api/performance',
            'health': '/api/performance/health'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'spiritual-guidance-platform',
        'gurus_available': True,
        'database_connected': True,
        'cache_enabled': True,
        'video_processing': True
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
