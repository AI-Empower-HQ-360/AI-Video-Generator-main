from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import os
from datetime import datetime
import atexit

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",  # For development - we'll restrict this later
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'spiritual-wisdom-key')
app.config['DEBUG'] = True

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///spiritual_platform.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models.database import db
db.init_app(app)

# Import API routes
from api.gurus import gurus_bp
from api.users import users_bp
from api.sessions import sessions_bp
from api.slokas import slokas_bp
from api.durable_endpoints import durable_bp
from api.whisper_endpoints import whisper_bp
from api.workflow_endpoints import workflow_bp

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
app.register_blueprint(workflow_bp)  # Workflow endpoints
app.register_blueprint(durable_bp)  # No url_prefix as it has its own

# Initialize workflow scheduler
from services.workflow_scheduler import start_scheduler, stop_scheduler

def init_scheduler():
    """Initialize the workflow scheduler"""
    try:
        start_scheduler()
        print("🔄 Workflow scheduler initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize workflow scheduler: {e}")

def cleanup_scheduler():
    """Cleanup function to stop scheduler on app shutdown"""
    try:
        stop_scheduler()
        print("🔄 Workflow scheduler stopped")
    except Exception as e:
        print(f"❌ Error stopping scheduler: {e}")

# Register cleanup function
atexit.register(cleanup_scheduler)

@app.route('/')
def home():
    return jsonify({
        'message': 'AI Empower Heart Spiritual Platform API',
        'version': '1.0.0',
        'status': 'active',
        'available_gurus': ['karma', 'bhakti', 'meditation', 'yoga', 'spiritual', 'sloka'],
        'features': [
            'spiritual_guidance',
            'workflow_automation',
            'multilingual_support',
            'content_scheduling',
            'approval_chains',
            'template_marketplace'
        ],
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
    with app.app_context():
        # Create database tables
        db.create_all()
        print("📊 Database tables created")
        
        # Initialize scheduler
        init_scheduler()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
